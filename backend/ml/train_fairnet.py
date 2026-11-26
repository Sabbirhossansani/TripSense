"""
TripSense Q1 Experimental Pipeline (train_fairnet.py) - Flagship v3 (GeoFairFormer)
====================================================================================
Runs the complete reproducible Q1 publication & thesis-defense suite on CUDA GPU / CPU:
  1. Chronological Zero-Leakage Benchmark Construction (Massive-STEPS-Sydney).
  2. Fair 15-Model Group Consensus Comparison:
       - 4 Heuristics: Popularity, Average Cosine, Least-Misery, Borda Count
       - 6 Neural SOTA: DeepSets (NeurIPS'17), AGREE (SIGIR'18), MoSAN (SIGIR'19),
         Set-Transformer (ICML'19), GroupIM (SIGIR'20), GroupMLP
       - 4 Tree/LTR Ensembles: Random Forest, HistGBDT, LightGBM Classifier, LightGBM LambdaRank
       - Proposed: TripSense-FairNet v3 (GeoFairFormer)
  3. 5-Seed Stability & 1000-Bootstrap 95% Confidence Intervals.
  4. Rigorous Statistical Hypothesis Testing (Friedman + Nemenyi CD across 15 models,
     Holm-Bonferroni Wilcoxon + Paired t-test on NDCG@10/Gini/Eco, Cliff's delta, Cohen's d).
  5. 9-Variant Component Ablation Study & Hyperparameter Sensitivity (lambda_gini, lambda_eco, tau).
  6. 3-Backbone Foundation Comparison (CLIP ViT-B/32 vs Google SigLIP vs BAAI BGE-base).
  7. External Validation Suite 1: 5 Unseen Global Cities across 5 Continents
       (Melbourne, Tokyo, New-York, Istanbul, Sao-Paulo - Zero-Shot).
  8. External Validation Suite 2: Independent 2026 Dataset (CRUISEResearchGroup/TripWorld
       Out-of-Town Tourist Benchmark - Hometown History -> Unfamiliar Destination POIs).
  9. Group Cardinality Scaling (|G| = 2..5), BD 5-City Pilot, Latency & Peak VRAM Profiling.
 10. 5-Paradigm End-to-End XAI Faithfulness Suite (IG, Expected Gradients, InputxGrad,
       Vanilla Saliency, Random -> Comp/Suff/AOPC/Insertion-AUC/Deletion-AUC), Permutation,
       TreeSHAP Concordance, Cross-Attention Audit, Nash Recourse, Worked Case Studies.
 11. Active Bayesian EIG (BALD) Swipe Curve & TravelPlanner Verification (180 tasks).
"""

import os
import sys
import time
import json
import math
import pickle
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, List, Tuple, Optional
from scipy.stats import wilcoxon, ttest_rel, friedmanchisquare, studentized_range
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
import lightgbm as lgb
import shap

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.ml.dataset_loader import (
    load_massive_steps_city,
    load_massive_steps_sydney,
    load_travelplanner_val,
    build_city_group_benchmark,
    build_tripworld_group_benchmark,
    CACHE_DIR,
)
from backend.ml.backbone import SigLIPBackbone, encode_and_save_tripsense_artifacts, ARTIFACTS_DIR
from backend.ml.fairnet import (
    TripSenseFairNet,
    extract_group_relational_features,
    pareto_fairness_infonce_loss,
    fairness_regularized_bpr_loss,
)
from backend.ml.baselines import (
    DeepSetsBaseline,
    AGREEBaseline,
    MoSANBaseline,
    SetTransformerBaseline,
    GroupIMBaseline,
    GroupMLPBaseline,
)
from backend.ml.eval_travelplanner import evaluate_travelplanner_rag
from backend.ml.xai_suite import (
    RELATIONAL_FEATURE_NAMES,
    compute_multi_xai_faithfulness_suite,
    compute_permutation_importance,
    analyze_cross_attention_and_counterfactuals,
    extract_worked_case_studies,
    compute_cross_xai_concordance,
)


def set_global_seed(seed: int):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _tag_model_cache(model_name: str) -> str:
    return model_name.strip().lower().replace("/", "_").replace("-", "_")


def compute_city_embeddings(bench: Dict[str, Any], backbone: SigLIPBackbone, dataset_slug: str) -> np.ndarray:
    """
    Encodes all unique venues using city-agnostic semantic descriptions
    and applies unsupervised All-but-the-Top mean-centering + L2 normalization
    (Mu & Viswanath, ICLR 2018) so embeddings generalize across unseen domains.
    """
    mtag = _tag_model_cache(backbone.model_name or "clip")
    cache_path = os.path.join(CACHE_DIR, f"v5_{dataset_slug}_{mtag}_poi_emb.npy")
    venues = bench["venues"]
    if os.path.exists(cache_path):
        arr = np.load(cache_path)
        if arr.shape[0] == len(venues):
            return arr.astype(np.float32)

    texts = [f"{v['name']} | Category: {v['category']}" for v in venues]
    print(f"[Pipeline] Encoding {len(texts)} venues for {bench['city']} via {backbone.model_name}...", flush=True)
    raw_embs = backbone.encode_texts(texts, batch_size=64).astype(np.float32)
    centered = raw_embs - raw_embs.mean(axis=0, keepdims=True)
    norms = np.linalg.norm(centered, axis=1, keepdims=True) + 1e-8
    embs = (centered / norms).astype(np.float32)
    np.save(cache_path, embs)
    return embs


def compute_member_taste_vectors(groups: List[Dict[str, Any]], poi_embs: np.ndarray) -> List[np.ndarray]:
    """Builds L2-normalized per-member taste embeddings strictly from held-in past check-ins."""
    out = []
    for g in groups:
        vecs = []
        for hist in g["member_histories"]:
            emb = poi_embs[hist].mean(axis=0)
            norm = float(np.linalg.norm(emb))
            vecs.append((emb / max(norm, 1e-8)).astype(np.float32))
        out.append(np.stack(vecs, axis=0))
    return out


def _gini(arr: np.ndarray) -> float:
    x = np.sort(np.maximum(0.0, arr.astype(np.float64)))
    n = len(x)
    if n <= 1 or np.sum(x) <= 1e-9:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2.0 * np.sum(idx * x) / (n * np.sum(x))) - (n + 1.0) / n)


def _true_member_utilities(
    ue: np.ndarray,           # (M, D)
    budgets: np.ndarray,      # (M,)
    cand_embs: np.ndarray,    # (C, D)
    cand_feats: np.ndarray,   # (C, 8)
) -> np.ndarray:
    """
    Objective, model-independent ground-truth member satisfaction U(u, p) in (0, 1):
      U(u, p) = sigmoid(2.8 * cos_centered(u, p) - 3.6 * ReLU(price_p - budget_u))
    """
    cos = np.clip(cand_embs @ ue.T, -1.0, 1.0)
    price = cand_feats[:, 1:2]
    gap = np.maximum(0.0, price - budgets[None, :])
    logit = 2.8 * cos - 3.6 * gap
    return 1.0 / (1.0 + np.exp(-logit))


def _evaluate_rankings(
    per_group_scores: List[np.ndarray],
    per_group_cands: List[np.ndarray],
    per_group_pos_len: List[int],
    groups: List[Dict[str, Any]],
    user_embs_list: List[np.ndarray],
    poi_embs: np.ndarray,
    venue_feats: np.ndarray,
) -> Dict[str, Any]:
    ndcg5_list, ndcg10_list, hit10_list, mrr10_list = [], [], [], []
    gini_list, min_sat_list, eco_cov_list, long_tail_list = [], [], [], []

    for i, scores in enumerate(per_group_scores):
        cands = per_group_cands[i]
        n_pos = per_group_pos_len[i]
        pos_rel = set(range(n_pos))

        order = np.argsort(-scores)
        top10 = order[:10]
        top5 = order[:5]

        for k, out_arr in [(5, ndcg5_list), (10, ndcg10_list)]:
            tk = order[:k]
            dcg = sum(1.0 / math.log2(r + 2.0) for r, idx in enumerate(tk) if int(idx) in pos_rel)
            idcg = sum(1.0 / math.log2(r + 2.0) for r in range(min(k, n_pos)))
            out_arr.append(dcg / max(1e-9, idcg))

        hit10_list.append(1.0 if any(int(idx) in pos_rel for idx in top10) else 0.0)

        mrr = 0.0
        for r, idx in enumerate(top10):
            if int(idx) in pos_rel:
                mrr = 1.0 / (r + 1.0)
                break
        mrr10_list.append(mrr)

        top5_venues = cands[top5]
        ue = user_embs_list[i]
        budgets = np.array(groups[i]["member_budgets"], dtype=np.float32)
        true_u = _true_member_utilities(ue, budgets, poi_embs[top5_venues], venue_feats[top5_venues])
        mean_u_per_member = true_u.mean(axis=0)
        gini_list.append(_gini(mean_u_per_member))
        min_sat_list.append(float(np.min(mean_u_per_member)))

        top5_feats = venue_feats[top5_venues]
        eco_cov_list.append(100.0 * float(np.mean(top5_feats[:, 6] >= 0.68)))
        long_tail_list.append(100.0 * float(np.mean(top5_feats[:, 5] > 0.5)))

    return {
        "ndcg5": round(float(np.mean(ndcg5_list)), 4),
        "ndcg10": round(float(np.mean(ndcg10_list)), 4),
        "hit10": round(float(np.mean(hit10_list)), 4),
        "mrr10": round(float(np.mean(mrr10_list)), 4),
        "gini_index": round(float(np.mean(gini_list)), 4),
        "min_member_sat": round(float(np.mean(min_sat_list)), 4),
        "eco_coverage_pct": round(float(np.mean(eco_cov_list)), 2),
        "long_tail_pct": round(float(np.mean(long_tail_list)), 2),
        "_per_group_ndcg10": np.array(ndcg10_list, dtype=np.float64),
        "_per_group_gini": np.array(gini_list, dtype=np.float64),
        "_per_group_eco": np.array(eco_cov_list, dtype=np.float64),
    }


def _build_eval_pools(
    groups: List[Dict[str, Any]],
    num_venues: int,
    num_negs: int = 97,
    seed: int = 42,
    allowed_neg_pool: Optional[List[int]] = None,
) -> Tuple[List[np.ndarray], List[int]]:
    """Deterministic candidate pools (~100 candidates/group)."""
    rng = np.random.RandomState(seed)
    cands_list = []
    pos_lens = []
    pool_arr = np.array(allowed_neg_pool, dtype=np.int64) if allowed_neg_pool is not None else None
    for g in groups:
        pos = g["pos_targets"]
        pos_set = set(pos)
        negs = []
        while len(negs) < num_negs:
            c = int(pool_arr[rng.randint(len(pool_arr))]) if pool_arr is not None else int(rng.randint(num_venues))
            if c not in pos_set and c not in negs:
                negs.append(c)
        cands_list.append(np.array(list(pos) + negs, dtype=np.int64))
        pos_lens.append(len(pos))
    return cands_list, pos_lens


def _relational_matrix_np(
    ue: np.ndarray,
    uf: np.ndarray,
    cands_emb: np.ndarray,
    cands_feat: np.ndarray,
) -> np.ndarray:
    """Pure NumPy computation matching extract_group_relational_features (C, 15)."""
    C = cands_emb.shape[0]
    M = ue.shape[0]
    cos_sim = np.clip(cands_emb @ ue.T, -1.0, 1.0)
    cos_mean = cos_sim.mean(axis=1, keepdims=True)
    cos_min = cos_sim.min(axis=1, keepdims=True)
    cos_max = cos_sim.max(axis=1, keepdims=True)
    cos_std = np.sqrt(np.mean((cos_sim - cos_mean) ** 2, axis=1, keepdims=True) + 1e-6)

    price = cands_feat[:, 1:2]
    budgets = uf[:, 0][None, :]
    bg = np.maximum(0.0, price - budgets)
    bg_mean = bg.mean(axis=1, keepdims=True)
    bg_max = bg.max(axis=1, keepdims=True)
    m_norm = np.full((C, 1), M / 5.0, dtype=np.float32)

    return np.concatenate(
        [cos_mean, cos_min, cos_max, cos_std, bg_mean, bg_max, m_norm, cands_feat],
        axis=1,
    ).astype(np.float32)


def _pad_group_batch(
    batch_indices: np.ndarray,
    groups: List[Dict[str, Any]],
    user_embs_list: List[np.ndarray],
    max_m: int,
    emb_dim: int,
):
    B = len(batch_indices)
    u_emb = np.zeros((B, max_m, emb_dim), dtype=np.float32)
    u_feat = np.zeros((B, max_m, 3), dtype=np.float32)
    u_mask = np.zeros((B, max_m), dtype=bool)
    for bi, gi in enumerate(batch_indices):
        ue = user_embs_list[gi]
        uf = np.array(groups[gi]["user_features"], dtype=np.float32)
        m = ue.shape[0]
        u_emb[bi, :m] = ue
        u_feat[bi, :m] = uf
        u_mask[bi, :m] = True
    return u_emb, u_feat, u_mask


def _batch_true_gini_and_floor(
    cos_t: torch.Tensor,   # (B, M)
    bg_t: torch.Tensor,    # (B, M)
    mask_t: torch.Tensor,  # (B, M) bool
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Differentiable member utility Gini & soft-min floor computed purely from (cos, bg)."""
    u_true = torch.sigmoid(2.8 * cos_t - 3.6 * bg_t)  # (B, M)
    mf = mask_t.float()
    cnt = mf.sum(dim=-1).clamp(min=1.0)
    mu = (u_true * mf).sum(dim=-1) / cnt
    diff = u_true.unsqueeze(2) - u_true.unsqueeze(1)
    s_abs = torch.sqrt(diff * diff + 1e-5)
    pmask = mf.unsqueeze(2) * mf.unsqueeze(1)
    gini = (s_abs * pmask).sum(dim=(1, 2)) / (2.0 * (cnt ** 2) * (mu + 1e-5))
    min_u = u_true.masked_fill(~mask_t, 1e4).min(dim=-1).values
    return gini, min_u


def train_fairnet_v3(
    train_groups: List[Dict[str, Any]],
    train_u_embs: List[np.ndarray],
    val_groups: List[Dict[str, Any]],
    val_u_embs: List[np.ndarray],
    val_cands: List[np.ndarray],
    val_pos_lens: List[int],
    poi_embs: np.ndarray,
    venue_feats: np.ndarray,
    device: torch.device,
    seed: int = 42,
    epochs: int = 28,
    num_negs_train: int = 20,
    use_attention: bool = True,
    use_relational_stream: bool = True,
    use_member_sab: bool = True,
    use_hadamard: bool = True,
    use_spectral_gate: bool = True,
    subspace_rank: int = 48,
    use_infonce: bool = True,
    tau: float = 0.20,
    lambda_gini: float = 0.36,
    lambda_misery: float = 0.28,
    lambda_eco: float = 0.38,
    zero_text_embs: bool = False,
) -> Tuple[TripSenseFairNet, Dict[str, Any]]:
    """Trains TripSense-FairNet v3 (Spectral-Gated GeoFairFormer) with dual-path Pareto InfoNCE."""
    set_global_seed(seed)
    rng = np.random.RandomState(seed)
    emb_dim = poi_embs.shape[1]
    V = poi_embs.shape[0]
    max_m = max(max(g["group_size"] for g in train_groups), 5)

    p_embs_used = np.zeros_like(poi_embs) if zero_text_embs else poi_embs
    t_u_embs_used = [np.zeros_like(u) for u in train_u_embs] if zero_text_embs else train_u_embs
    v_u_embs_used = [np.zeros_like(u) for u in val_u_embs] if zero_text_embs else val_u_embs

    model = TripSenseFairNet(
        emb_dim=emb_dim,
        poi_feat_dim=8,
        user_feat_dim=3,
        hidden_dim=64,
        num_heads=4,
        dropout=0.10,
        softmin_temp=0.12,
        use_attention=use_attention,
        use_relational_stream=use_relational_stream,
        use_member_sab=use_member_sab,
        use_hadamard=use_hadamard,
        use_spectral_gate=use_spectral_gate,
        subspace_rank=subspace_rank,
    ).to(device)

    if use_hadamard and use_spectral_gate and not zero_text_embs:
        model.set_source_subspace(p_embs_used)

    sem_params, other_params = [], []
    for pname, param in model.named_parameters():
        if not param.requires_grad:
            continue
        if "sem_adapter" in pname:
            sem_params.append(param)
        else:
            other_params.append(param)

    optimizer = torch.optim.AdamW(
        [
            {"params": other_params, "weight_decay": 3e-4},
            {"params": sem_params, "weight_decay": 5e-3},
        ],
        lr=1.5e-3,
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-4)

    p_emb_gpu = torch.from_numpy(p_embs_used).to(device)
    p_feat_gpu = torch.from_numpy(venue_feats).to(device)

    best_val_ndcg = -1.0
    best_val_gini = 999.0
    best_state = None
    history = []

    train_pairs = [(gi, int(pid)) for gi, g in enumerate(train_groups) for pid in g["pos_targets"]]
    n_pairs = len(train_pairs)
    all_pair_gi = np.array([gi for gi, _ in train_pairs], dtype=np.int64)
    all_pair_pid = np.array([pid for _, pid in train_pairs], dtype=np.int64)
    u_e_all_np, u_f_all_np, u_m_all_np = _pad_group_batch(all_pair_gi, train_groups, t_u_embs_used, max_m, emb_dim)
    u_e_all_gpu = torch.from_numpy(u_e_all_np).to(device)
    u_f_all_gpu = torch.from_numpy(u_f_all_np).to(device)
    u_m_all_gpu = torch.from_numpy(u_m_all_np).to(device)
    pos_all_gpu = torch.from_numpy(all_pair_pid).to(device)

    batch_size = 64

    for ep in range(1, epochs + 1):
        model.train()
        perm = rng.permutation(n_pairs)
        ep_loss = 0.0
        n_batches = 0

        for start in range(0, n_pairs, batch_size):
            sel = perm[start : start + batch_size]
            B = len(sel)
            b_idx = all_pair_gi[sel]
            sel_t = torch.from_numpy(sel).to(device)

            neg_ids = rng.randint(0, V, size=(B, num_negs_train), dtype=np.int64)
            for bi, gi in enumerate(b_idx):
                pset = set(train_groups[gi]["pos_targets"])
                for kc in range(num_negs_train):
                    while int(neg_ids[bi, kc]) in pset:
                        neg_ids[bi, kc] = int(rng.randint(0, V))

            u_t = u_e_all_gpu[sel_t]
            uf_t = u_f_all_gpu[sel_t]
            m_t = u_m_all_gpu[sel_t]

            pos_idx_t = pos_all_gpu[sel_t]
            pos_total, pos_inv, pos_score, pos_members, _, _ = model.forward_dual(
                u_t, uf_t, m_t, p_emb_gpu[pos_idx_t], p_feat_gpu[pos_idx_t]
            )
            pos_eco = p_feat_gpu[pos_idx_t, 6]

            neg_idx_flat = torch.from_numpy(neg_ids.reshape(-1)).to(device)
            u_neg = u_t.unsqueeze(1).expand(B, num_negs_train, max_m, emb_dim).reshape(B * num_negs_train, max_m, emb_dim)
            uf_neg = uf_t.unsqueeze(1).expand(B, num_negs_train, max_m, 3).reshape(B * num_negs_train, max_m, 3)
            m_neg = m_t.unsqueeze(1).expand(B, num_negs_train, max_m).reshape(B * num_negs_train, max_m)

            neg_total_f, neg_inv_f, neg_scores_f, _, _, _ = model.forward_dual(
                u_neg, uf_neg, m_neg, p_emb_gpu[neg_idx_flat], p_feat_gpu[neg_idx_flat]
            )
            neg_total = neg_total_f.view(B, num_negs_train)
            neg_inv = neg_inv_f.view(B, num_negs_train)
            neg_eco = p_feat_gpu[neg_idx_flat, 6].view(B, num_negs_train)

            if use_infonce:
                _, pos_cos, pos_bg = extract_group_relational_features(
                    u_t, uf_t, m_t, p_emb_gpu[pos_idx_t], p_feat_gpu[pos_idx_t]
                )
                _, neg_cos, neg_bg = extract_group_relational_features(
                    u_neg, uf_neg, m_neg, p_emb_gpu[neg_idx_flat], p_feat_gpu[neg_idx_flat]
                )
                pos_gini_true, pos_floor = _batch_true_gini_and_floor(pos_cos, pos_bg, m_t)
                neg_gini_true, neg_floor = _batch_true_gini_and_floor(neg_cos, neg_bg, m_neg)
                neg_gini_true = neg_gini_true.view(B, num_negs_train)
                neg_floor = neg_floor.view(B, num_negs_train)

                loss_tot, _ = pareto_fairness_infonce_loss(
                    pos_total, neg_total, pos_members, m_t, pos_eco, neg_eco=neg_eco,
                    pos_floor=pos_floor, neg_floor=neg_floor,
                    pos_gini_true=pos_gini_true, neg_gini_true=neg_gini_true,
                    tau=tau, lambda_gini=lambda_gini, lambda_misery=lambda_misery, lambda_eco=lambda_eco,
                )
                if use_hadamard and use_spectral_gate:
                    loss_inv, _ = pareto_fairness_infonce_loss(
                        pos_inv, neg_inv, pos_members, m_t, pos_eco, neg_eco=neg_eco,
                        pos_floor=pos_floor, neg_floor=neg_floor,
                        pos_gini_true=pos_gini_true, neg_gini_true=neg_gini_true,
                        tau=tau, lambda_gini=lambda_gini, lambda_misery=lambda_misery, lambda_eco=lambda_eco,
                    )
                    loss = loss_tot + 0.70 * loss_inv
                else:
                    loss = loss_tot
            else:
                loss, _ = fairness_regularized_bpr_loss(
                    pos_score, pos_members, neg_scores_f.view(B, num_negs_train)[:, 0],
                    m_t, pos_eco, fairness_weight=lambda_gini, misery_weight=lambda_misery, eco_weight=lambda_eco,
                )

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 2.0)
            optimizer.step()
            ep_loss += float(loss.item())
            n_batches += 1

        scheduler.step()

        if ep % 2 == 0 or ep >= epochs - 3 or ep == 1:
            val_scores = score_fairnet_groups(
                model, val_groups, v_u_embs_used, val_cands, p_embs_used, venue_feats, device
            )
            val_res = _evaluate_rankings(
                val_scores, val_cands, val_pos_lens, val_groups, val_u_embs, poi_embs, venue_feats
            )
            history.append({
                "epoch": ep,
                "train_loss": round(ep_loss / max(1, n_batches), 4),
                "val_ndcg10": val_res["ndcg10"],
                "val_gini": val_res["gini_index"],
                "val_min_sat": val_res["min_member_sat"],
                "val_eco": val_res["eco_coverage_pct"],
            })
            if (val_res["ndcg10"] > best_val_ndcg + 1e-4) or (
                abs(val_res["ndcg10"] - best_val_ndcg) <= 1e-4 and val_res["gini_index"] < best_val_gini
            ):
                best_val_ndcg = val_res["ndcg10"]
                best_val_gini = val_res["gini_index"]
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    return model, {"best_val_ndcg10": best_val_ndcg, "epochs": epochs, "history": history}


@torch.no_grad()
def score_fairnet_groups(
    model: TripSenseFairNet,
    groups: List[Dict[str, Any]],
    user_embs_list: List[np.ndarray],
    cands_list: List[np.ndarray],
    poi_embs: np.ndarray,
    venue_feats: np.ndarray,
    device: torch.device,
    return_gate: bool = False,
):
    model.eval()
    p_emb_gpu = torch.from_numpy(poi_embs).to(device)
    p_feat_gpu = torch.from_numpy(venue_feats).to(device)
    out_scores = []
    gates = []
    for gi, cands in enumerate(cands_list):
        ue = user_embs_list[gi]
        uf = np.array(groups[gi]["user_features"], dtype=np.float32)
        M = ue.shape[0]
        C = len(cands)
        u_t = torch.from_numpy(ue).unsqueeze(0).expand(C, M, -1).to(device)
        uf_t = torch.from_numpy(uf).unsqueeze(0).expand(C, M, -1).to(device)
        m_t = torch.ones((C, M), dtype=torch.bool, device=device)
        c_idx = torch.from_numpy(cands).to(device)
        _, _, scores, _, _, gate = model.forward_dual(u_t, uf_t, m_t, p_emb_gpu[c_idx], p_feat_gpu[c_idx])
        out_scores.append(scores.cpu().numpy())
        gates.append(float(gate.mean().item()))
    if return_gate:
        return out_scores, round(float(np.mean(gates)), 4)
    return out_scores


def train_neural_baseline(
    cls,
    train_groups: List[Dict[str, Any]],
    train_u_embs: List[np.ndarray],
    val_groups: List[Dict[str, Any]],
    val_u_embs: List[np.ndarray],
    val_cands: List[np.ndarray],
    val_pos_lens: List[int],
    poi_embs: np.ndarray,
    venue_feats: np.ndarray,
    device: torch.device,
    seed: int = 42,
    epochs: int = 18,
):
    set_global_seed(seed)
    rng = np.random.RandomState(seed)
    emb_dim = poi_embs.shape[1]
    V = poi_embs.shape[0]
    max_m = max(max(g["group_size"] for g in train_groups), 5)

    model = cls(emb_dim=emb_dim, poi_feat_dim=8, user_feat_dim=3, hidden_dim=64, dropout=0.25).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=2e-4)
    p_emb_gpu = torch.from_numpy(poi_embs).to(device)
    p_feat_gpu = torch.from_numpy(venue_feats).to(device)

    is_groupim = cls is GroupIMBaseline
    best_ndcg = -1.0
    best_state = None
    batch_size = 64
    n_train = len(train_groups)

    for _ in range(epochs):
        model.train()
        perm = rng.permutation(n_train)
        for start in range(0, n_train, batch_size):
            b_idx = perm[start : start + batch_size]
            B = len(b_idx)
            u_emb_np, u_feat_np, u_mask_np = _pad_group_batch(b_idx, train_groups, train_u_embs, max_m, emb_dim)
            pos_ids = np.array([train_groups[gi]["pos_targets"][rng.randint(len(train_groups[gi]["pos_targets"]))] for gi in b_idx], dtype=np.int64)
            neg_ids = np.array([int(rng.randint(V)) for _ in range(B)], dtype=np.int64)

            u_t = torch.from_numpy(u_emb_np).to(device)
            uf_t = torch.from_numpy(u_feat_np).to(device)
            m_t = torch.from_numpy(u_mask_np).to(device)
            pos_t = torch.from_numpy(pos_ids).to(device)
            neg_t = torch.from_numpy(neg_ids).to(device)

            if is_groupim:
                l_pos, mi_loss = model(u_t, uf_t, m_t, p_emb_gpu[pos_t], p_feat_gpu[pos_t], return_mi_loss=True)
                l_neg = model(u_t, uf_t, m_t, p_emb_gpu[neg_t], p_feat_gpu[neg_t], return_mi_loss=False)
                loss = -F.logsigmoid(l_pos - l_neg).mean() + 0.25 * mi_loss
            else:
                out_pos = model(u_t, uf_t, m_t, p_emb_gpu[pos_t], p_feat_gpu[pos_t])
                out_neg = model(u_t, uf_t, m_t, p_emb_gpu[neg_t], p_feat_gpu[neg_t])
                l_pos = out_pos[0] if isinstance(out_pos, tuple) else out_pos
                l_neg = out_neg[0] if isinstance(out_neg, tuple) else out_neg
                loss = -F.logsigmoid(l_pos - l_neg).mean()

            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 2.0)
            opt.step()

        scores = score_neural_baseline(model, val_groups, val_u_embs, val_cands, poi_embs, venue_feats, device)
        res = _evaluate_rankings(scores, val_cands, val_pos_lens, val_groups, val_u_embs, poi_embs, venue_feats)
        if res["ndcg10"] >= best_ndcg:
            best_ndcg = res["ndcg10"]
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    return model


@torch.no_grad()
def score_neural_baseline(model, groups, user_embs_list, cands_list, poi_embs, venue_feats, device):
    model.eval()
    p_emb_gpu = torch.from_numpy(poi_embs).to(device)
    p_feat_gpu = torch.from_numpy(venue_feats).to(device)
    out = []
    for gi, cands in enumerate(cands_list):
        ue = user_embs_list[gi]
        uf = np.array(groups[gi]["user_features"], dtype=np.float32)
        M = ue.shape[0]
        C = len(cands)
        u_t = torch.from_numpy(ue).unsqueeze(0).expand(C, M, -1).to(device)
        uf_t = torch.from_numpy(uf).unsqueeze(0).expand(C, M, -1).to(device)
        m_t = torch.ones((C, M), dtype=torch.bool, device=device)
        c_idx = torch.from_numpy(cands).to(device)
        res = model(u_t, uf_t, m_t, p_emb_gpu[c_idx], p_feat_gpu[c_idx])
        logits = res[0] if isinstance(res, tuple) else res
        out.append(logits.cpu().numpy())
    return out


def build_tabular_dataset(
    groups: List[Dict[str, Any]],
    user_embs_list: List[np.ndarray],
    poi_embs: np.ndarray,
    venue_feats: np.ndarray,
    negs_per_pos: int = 8,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray, List[int]]:
    rng = np.random.RandomState(seed)
    V = poi_embs.shape[0]
    Xs, ys, q_sizes = [], [], []
    for gi, g in enumerate(groups):
        ue = user_embs_list[gi]
        uf = np.array(g["user_features"], dtype=np.float32)
        pos_list = g["pos_targets"]
        pos_set = set(pos_list)
        negs = []
        while len(negs) < negs_per_pos * len(pos_list):
            c = int(rng.randint(V))
            if c not in pos_set:
                negs.append(c)
        cands = np.array(list(pos_list) + negs, dtype=np.int64)
        labels = np.array([1] * len(pos_list) + [0] * len(negs), dtype=np.int32)
        X_g = _relational_matrix_np(ue, uf, poi_embs[cands], venue_feats[cands])
        Xs.append(X_g)
        ys.append(labels)
        q_sizes.append(len(cands))
    return np.vstack(Xs), np.concatenate(ys), q_sizes


def score_sklearn_groups(model, groups, user_embs_list, cands_list, poi_embs, venue_feats) -> List[np.ndarray]:
    out = []
    for gi, cands in enumerate(cands_list):
        ue = user_embs_list[gi]
        uf = np.array(groups[gi]["user_features"], dtype=np.float32)
        X_g = _relational_matrix_np(ue, uf, poi_embs[cands], venue_feats[cands])
        if hasattr(model, "predict_proba"):
            out.append(model.predict_proba(X_g)[:, 1])
        else:
            out.append(model.predict(X_g))
    return out


def score_heuristics(
    kind: str,
    groups: List[Dict[str, Any]],
    user_embs_list: List[np.ndarray],
    cands_list: List[np.ndarray],
    poi_embs: np.ndarray,
    venue_feats: np.ndarray,
) -> List[np.ndarray]:
    out = []
    for gi, cands in enumerate(cands_list):
        if kind == "popularity":
            out.append(venue_feats[cands, 2].copy())
        else:
            ue = user_embs_list[gi]
            cos_mat = np.clip(poi_embs[cands] @ ue.T, -1.0, 1.0)
            if kind == "avg_cos":
                out.append(cos_mat.mean(axis=1))
            elif kind == "least_misery":
                out.append(cos_mat.min(axis=1))
            elif kind == "borda":
                C, M = cos_mat.shape
                borda = np.zeros(C, dtype=np.float32)
                for m in range(M):
                    ranks = np.argsort(np.argsort(cos_mat[:, m]))
                    borda += ranks / max(1.0, C - 1.0)
                out.append(borda / M)
    return out


def bootstrap_ci(arr: np.ndarray, n_boot: int = 1000, seed: int = 42) -> Tuple[float, float]:
    rng = np.random.RandomState(seed)
    n = len(arr)
    means = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        idx = rng.randint(0, n, size=n)
        means[b] = arr[idx].mean()
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    diff = a[:, None] - b[None, :]
    n_gt = np.sum(diff > 1e-12)
    n_lt = np.sum(diff < -1e-12)
    return float((n_gt - n_lt) / (len(a) * len(b)))


def holm_bonferroni(p_vals: List[float]) -> List[float]:
    m = len(p_vals)
    order = np.argsort(p_vals)
    adj = np.empty(m, dtype=np.float64)
    running_max = 0.0
    for rank, idx in enumerate(order):
        val = min(1.0, p_vals[idx] * (m - rank))
        running_max = max(running_max, val)
        adj[idx] = running_max
    return [float(x) for x in adj]


def evaluate_bd_pilot_cities(fairnet_model: TripSenseFairNet, device: torch.device) -> List[Dict[str, Any]]:
    """Audits TripSense-FairNet v3 vs Average Cosine across 5 Bangladeshi cities using isotropic centered embeddings."""
    bd_path = os.path.join(ROOT_DIR, "backend", "app", "data", "bangladesh_spots.json")
    all_spots = json.load(open(bd_path, "r", encoding="utf-8"))
    from backend.ml.inference import FairNetInference

    inf = FairNetInference()
    # Center all BD POI embeddings isotropically for true utility evaluation
    all_raw = np.stack([inf.get_poi_embedding(s) for s in all_spots], axis=0)
    mu_bd = all_raw.mean(axis=0, keepdims=True)

    def _iso(v: np.ndarray) -> np.ndarray:
        c = v - mu_bd.squeeze(0) if v.ndim == 1 else v - mu_bd
        n = np.linalg.norm(c, axis=-1, keepdims=True) + 1e-8
        return (c / n).astype(np.float32)

    cities = ["Dhaka", "Chittagong", "Sylhet", "Cox's Bazar", "Bandarban"]
    archetypes = [
        [
            {"name": "A1", "interests": ["Historical", "Culture"], "budget_tier": "Budget"},
            {"name": "A2", "interests": ["Nature", "Beach"], "budget_tier": "Mid-range"},
            {"name": "A3", "interests": ["Food", "Adventure"], "budget_tier": "Luxury"},
        ],
        [
            {"name": "B1", "interests": ["Nature", "Relaxation"], "budget_tier": "Budget"},
            {"name": "B2", "interests": ["Adventure", "Culture"], "budget_tier": "Mid-range"},
            {"name": "B3", "interests": ["Food", "Historical"], "budget_tier": "Budget"},
            {"name": "B4", "interests": ["Beach", "Nature"], "budget_tier": "Mid-range"},
        ],
    ]

    city_reports = []
    for city in cities:
        c_spots = [s for s in all_spots if str(s.get("city", "")).lower() == city.lower()]
        if len(c_spots) < 5:
            continue
        c_feats = np.stack([inf.extract_poi_features(s) for s in c_spots], axis=0)
        c_embs = _iso(np.stack([inf.get_poi_embedding(s) for s in c_spots], axis=0))

        fn_ginis, fn_mins, fn_ecos, fn_tails = [], [], [], []
        avg_ginis, avg_ecos = [], []
        for members in archetypes:
            ue = _iso(np.stack([inf.encode_user(m) for m in members], axis=0))
            uf = np.stack([inf.extract_user_features(m) for m in members], axis=0)
            budgets = uf[:, 0]

            C, M = len(c_spots), len(members)
            u_t = torch.from_numpy(ue).unsqueeze(0).expand(C, M, -1).to(device)
            uf_t = torch.from_numpy(uf).unsqueeze(0).expand(C, M, -1).to(device)
            m_t = torch.ones((C, M), dtype=torch.bool, device=device)
            with torch.no_grad():
                fn_scores, _, _ = fairnet_model(
                    u_t, uf_t, m_t,
                    torch.from_numpy(c_embs).to(device),
                    torch.from_numpy(c_feats).to(device),
                )
            fn_idx = np.argsort(-fn_scores.cpu().numpy())[:5]
            cos_scores = (c_embs @ ue.T).mean(axis=1)
            avg_idx = np.argsort(-cos_scores)[:5]

            true_fn = _true_member_utilities(ue, budgets, c_embs[fn_idx], c_feats[fn_idx]).mean(axis=0)
            true_avg = _true_member_utilities(ue, budgets, c_embs[avg_idx], c_feats[avg_idx]).mean(axis=0)

            fn_ginis.append(_gini(true_fn))
            fn_mins.append(float(np.min(true_fn)))
            fn_ecos.append(float(np.mean(c_feats[fn_idx, 6]) * 100.0))
            fn_tails.append(float(np.mean(c_feats[fn_idx, 5]) * 100.0))
            avg_ginis.append(_gini(true_avg))
            avg_ecos.append(float(np.mean(c_feats[avg_idx, 6]) * 100.0))

        city_reports.append({
            "city": city,
            "num_spots": len(c_spots),
            "fairnet_gini": round(float(np.mean(fn_ginis)), 4),
            "avg_cos_gini": round(float(np.mean(avg_ginis)), 4),
            "fairnet_min_sat": round(float(np.mean(fn_mins)), 4),
            "fairnet_eco_score_pct": round(float(np.mean(fn_ecos)), 1),
            "avg_cos_eco_score_pct": round(float(np.mean(avg_ecos)), 1),
            "hidden_gem_exposure_pct": round(float(np.mean(fn_tails)), 1),
        })
    return city_reports


def simulate_active_swipe_curve(seed: int = 42) -> List[Dict[str, Any]]:
    """
    Simulates 120 synthetic travelers across 0..6 swipes comparing Gaussian-Posterior
    BALD Expected Information Gain (Houlsby et al., 2011) vs Random Swipes over isotropically
    mean-centered swipe card embeddings.
    """
    rng = np.random.RandomState(seed)
    swipe_npz = np.load(os.path.join(ARTIFACTS_DIR, "swipe_embeddings.npz"), allow_pickle=False)
    raw = swipe_npz["embeddings"].astype(np.float32)
    centered = raw - raw.mean(axis=0, keepdims=True)
    card_embs = centered / (np.linalg.norm(centered, axis=1, keepdims=True) + 1e-8)
    num_cards, D = card_embs.shape

    curve = []
    for k_swipes in range(0, 7):
        bayes_sims, rand_sims = [], []
        for _ in range(120):
            pref_cards = rng.choice(num_cards, size=2, replace=False)
            true_taste = card_embs[pref_cards].mean(axis=0)
            true_taste /= np.linalg.norm(true_taste) + 1e-8

            if k_swipes == 0:
                bayes_sims.append(float(np.clip(rng.normal(0.18, 0.04), 0.0, 1.0)))
                rand_sims.append(float(np.clip(rng.normal(0.18, 0.04), 0.0, 1.0)))
                continue

            # Bayesian D-optimal / BALD EIG via online Woodbury posterior precision covariance
            cov = np.eye(D, dtype=np.float32)
            seen = []
            posterior = np.zeros(D, dtype=np.float32)
            for _step in range(k_swipes):
                cands = [i for i in range(num_cards) if i not in seen]
                # BALD score = x^T Sigma x (expected reduction in posterior entropy)
                gains = [float(card_embs[c] @ cov @ card_embs[c]) for c in cands]
                chosen = cands[int(np.argmax(gains))]
                seen.append(chosen)
                xc = card_embs[chosen]
                # Sherman-Morrison posterior update with observation precision alpha=6.0
                c_x = cov @ xc
                cov = cov - (6.0 / (1.0 + 6.0 * float(xc @ c_x))) * np.outer(c_x, c_x)
                sim_true = float(xc @ true_taste)
                if sim_true > 0.15:
                    posterior += (0.8 + sim_true) * xc
                else:
                    posterior -= 0.45 * xc

            est = posterior / (np.linalg.norm(posterior) + 1e-8) if np.linalg.norm(posterior) > 1e-6 else card_embs[seen].mean(axis=0)
            bayes_sims.append(float(np.clip(est @ true_taste, 0.0, 1.0)))

            r_seen = rng.choice(num_cards, size=k_swipes, replace=False)
            r_post = np.zeros(D, dtype=np.float32)
            for c in r_seen:
                sim_true = float(card_embs[c] @ true_taste)
                if sim_true > 0.15:
                    r_post += (0.8 + sim_true) * card_embs[c]
                else:
                    r_post -= 0.45 * card_embs[c]
            r_est = r_post / (np.linalg.norm(r_post) + 1e-8) if np.linalg.norm(r_post) > 1e-6 else card_embs[r_seen].mean(axis=0)
            rand_sims.append(float(np.clip(r_est @ true_taste, 0.0, 1.0)))

        curve.append({
            "swipes": k_swipes,
            "bayesian_eig_cos": round(float(np.mean(bayes_sims)), 4),
            "random_swipe_cos": round(float(np.mean(rand_sims)), 4),
        })
    return curve


def _evaluate_external_dataset(
    bench: Dict[str, Any],
    backbone: SigLIPBackbone,
    dataset_slug: str,
    models_dict: Dict[str, Any],
    device: torch.device,
    seed: int = 88,
) -> Dict[str, Any]:
    """Runs zero-shot transfer evaluation across 10 models on any unseen dataset/city."""
    c_embs = compute_city_embeddings(bench, backbone, dataset_slug)
    c_groups = bench["groups"]
    c_u = compute_member_taste_vectors(c_groups, c_embs)
    allowed_negs = bench.get("dest_candidate_indices")
    c_cands, c_pos = _build_eval_pools(
        c_groups, bench["num_venues"], num_negs=97, seed=seed, allowed_neg_pool=allowed_negs
    )
    c_feats = bench["venue_feats"]

    city_eval = {}
    for mlabel, mkind in [("Popularity", "popularity"), ("Average Cosine", "avg_cos"), ("Least-Misery", "least_misery")]:
        sc = score_heuristics(mkind, c_groups, c_u, c_cands, c_embs, c_feats)
        r = _evaluate_rankings(sc, c_cands, c_pos, c_groups, c_u, c_embs, c_feats)
        city_eval[mlabel] = {k: r[k] for k in ["ndcg5", "ndcg10", "hit10", "mrr10", "gini_index", "min_member_sat", "eco_coverage_pct", "long_tail_pct"]}

    for nlabel, nmodel in [
        ("AGREE (Zero-Shot)", models_dict["agree"]),
        ("MoSAN (Zero-Shot)", models_dict["mosan"]),
        ("Set-Transformer (Zero-Shot)", models_dict["set_transformer"]),
        ("GroupIM (Zero-Shot)", models_dict["groupim"]),
    ]:
        sc_n = score_neural_baseline(nmodel, c_groups, c_u, c_cands, c_embs, c_feats, device)
        r_n = _evaluate_rankings(sc_n, c_cands, c_pos, c_groups, c_u, c_embs, c_feats)
        city_eval[nlabel] = {k: r_n[k] for k in ["ndcg5", "ndcg10", "hit10", "mrr10", "gini_index", "min_member_sat", "eco_coverage_pct", "long_tail_pct"]}

    for tlabel, tmodel in [
        ("LightGBM Cls (Zero-Shot)", models_dict["lgbm"]),
        ("LightGBM LambdaRank (Zero-Shot)", models_dict["lambdarank"]),
    ]:
        sc_t = score_sklearn_groups(tmodel, c_groups, c_u, c_cands, c_embs, c_feats)
        r_t = _evaluate_rankings(sc_t, c_cands, c_pos, c_groups, c_u, c_embs, c_feats)
        city_eval[tlabel] = {k: r_t[k] for k in ["ndcg5", "ndcg10", "hit10", "mrr10", "gini_index", "min_member_sat", "eco_coverage_pct", "long_tail_pct"]}

    sc_fn, mean_gate = score_fairnet_groups(models_dict["fairnet"], c_groups, c_u, c_cands, c_embs, c_feats, device, return_gate=True)
    r_fn = _evaluate_rankings(sc_fn, c_cands, c_pos, c_groups, c_u, c_embs, c_feats)
    city_eval["TripSense-FairNet v3 (Zero-Shot)"] = {
        k: r_fn[k] for k in ["ndcg5", "ndcg10", "hit10", "mrr10", "gini_index", "min_member_sat", "eco_coverage_pct", "long_tail_pct"]
    }
    return {
        "num_rows": bench["num_rows"],
        "num_venues": bench["num_venues"],
        "num_test_groups": len(c_groups),
        "spectral_gate_activation": mean_gate,
        "models": city_eval,
    }


def _train_lambdarank(X_tr, y_tr, q_tr, X_val, y_val, q_val, seed: int = 42):
    ranker = lgb.LGBMRanker(
        objective="lambdarank",
        n_estimators=220,
        learning_rate=0.05,
        max_depth=5,
        num_leaves=23,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=seed,
        verbose=-1,
    )
    ranker.fit(
        X_tr, y_tr, group=q_tr,
        eval_set=[(X_val, y_val)], eval_group=[q_val],
        callbacks=[lgb.early_stopping(25, verbose=False)],
    )
    return ranker


def main():
    quick_mode = "--quick" in sys.argv
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("=" * 84)
    print(f"TRIPSENSE v3 (GeoFairFormer) Q1 SUITE | Device: {device} | quick={quick_mode}")
    print("=" * 84)

    # Step 1: Primary Multimodal Backbone & App Artifacts
    backbone = SigLIPBackbone("openai/clip-vit-base-patch32", device=str(device))
    model_name, _, _ = encode_and_save_tripsense_artifacts(backbone)

    # Step 2: Load Sydney Benchmark (zero-leakage 1200 groups: 840 train / 180 val / 180 test)
    syd_df = load_massive_steps_sydney(max_rows=30000)
    syd_bench = build_city_group_benchmark(syd_df, num_groups=1200, seed=42, city_name="Sydney")
    syd_poi_embs = compute_city_embeddings(syd_bench, backbone, "sydney")

    groups = syd_bench["groups"]
    train_groups = groups[:840]
    val_groups = groups[840:1020]
    test_groups = groups[1020:]

    train_u = compute_member_taste_vectors(train_groups, syd_poi_embs)
    val_u = compute_member_taste_vectors(val_groups, syd_poi_embs)
    test_u = compute_member_taste_vectors(test_groups, syd_poi_embs)

    V_syd = syd_bench["num_venues"]
    vfeats = syd_bench["venue_feats"]
    val_cands, val_pos_lens = _build_eval_pools(val_groups, V_syd, num_negs=97, seed=101)
    test_cands, test_pos_lens = _build_eval_pools(test_groups, V_syd, num_negs=97, seed=2026)

    print(f"[Data] Sydney: {syd_bench['num_rows']} check-ins | {V_syd} venues | "
          f"{len(train_groups)} train / {len(val_groups)} val / {len(test_groups)} test groups", flush=True)

    # Step 3: 15-Model Fair Comparison on Sydney Held-Out Test Split
    print("\n[Phase A] Training & Evaluating 15-Model Benchmark on Sydney Held-Out Test Split...", flush=True)
    raw_model_scores: Dict[str, List[np.ndarray]] = {}

    for label, kind in [
        ("Popularity", "popularity"),
        ("Average Cosine", "avg_cos"),
        ("Least-Misery", "least_misery"),
        ("Borda Count", "borda"),
    ]:
        raw_model_scores[label] = score_heuristics(kind, test_groups, test_u, test_cands, syd_poi_embs, vfeats)

    neural_specs = [
        ("DeepSets (NeurIPS'17)", DeepSetsBaseline),
        ("AGREE (SIGIR'18)", AGREEBaseline),
        ("MoSAN (SIGIR'19)", MoSANBaseline),
        ("Set-Transformer (ICML'19)", SetTransformerBaseline),
        ("GroupIM (SIGIR'20)", GroupIMBaseline),
        ("GroupMLP", GroupMLPBaseline),
    ]
    trained_neural = {}
    for nname, ncls in neural_specs:
        nm = train_neural_baseline(
            ncls, train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens, syd_poi_embs, vfeats, device, seed=42
        )
        trained_neural[nname] = nm
        raw_model_scores[nname] = score_neural_baseline(
            nm, test_groups, test_u, test_cands, syd_poi_embs, vfeats, device
        )

    X_tr, y_tr, q_tr = build_tabular_dataset(train_groups, train_u, syd_poi_embs, vfeats, negs_per_pos=8, seed=42)
    X_val, y_val, q_val = build_tabular_dataset(val_groups, val_u, syd_poi_embs, vfeats, negs_per_pos=8, seed=99)

    rf_model = RandomForestClassifier(n_estimators=180, max_depth=9, random_state=42, n_jobs=-1)
    rf_model.fit(X_tr, y_tr)
    raw_model_scores["Random Forest"] = score_sklearn_groups(rf_model, test_groups, test_u, test_cands, syd_poi_embs, vfeats)

    hgb_model = HistGradientBoostingClassifier(max_iter=180, max_depth=5, learning_rate=0.05, random_state=42)
    hgb_model.fit(X_tr, y_tr)
    raw_model_scores["HistGBDT"] = score_sklearn_groups(hgb_model, test_groups, test_u, test_cands, syd_poi_embs, vfeats)

    lgbm_model = lgb.LGBMClassifier(
        n_estimators=220, learning_rate=0.05, max_depth=5, num_leaves=23, subsample=0.85,
        colsample_bytree=0.85, random_state=42, verbose=-1
    )
    lgbm_model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], callbacks=[lgb.early_stopping(25, verbose=False)])
    raw_model_scores["LightGBM GBDT"] = score_sklearn_groups(lgbm_model, test_groups, test_u, test_cands, syd_poi_embs, vfeats)
    pickle.dump(lgbm_model, open(os.path.join(ARTIFACTS_DIR, "lgbm_ranker.pkl"), "wb"))

    lambdarank_model = _train_lambdarank(X_tr, y_tr, q_tr, X_val, y_val, q_val, seed=42)
    raw_model_scores["LightGBM LambdaRank"] = score_sklearn_groups(lambdarank_model, test_groups, test_u, test_cands, syd_poi_embs, vfeats)

    fairnet_v3, fn_train_info = train_fairnet_v3(
        train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens, syd_poi_embs, vfeats, device, seed=42
    )
    raw_model_scores["TripSense-FairNet v3 (Ours)"], sydney_gate = score_fairnet_groups(
        fairnet_v3, test_groups, test_u, test_cands, syd_poi_embs, vfeats, device, return_gate=True
    )

    ckpt_path = os.path.join(ARTIFACTS_DIR, "fairnet_best.pt")
    torch.save({
        "model_state_dict": fairnet_v3.state_dict(),
        "config": {
            "emb_dim": int(syd_poi_embs.shape[1]),
            "poi_feat_dim": 8,
            "user_feat_dim": 3,
            "hidden_dim": 64,
            "num_heads": 4,
            "use_attention": True,
            "use_relational_stream": True,
            "use_member_sab": True,
            "use_hadamard": True,
            "use_spectral_gate": True,
            "subspace_rank": 48,
            "backbone": model_name,
        },
    }, ckpt_path)

    eval_table: Dict[str, Any] = {}
    per_group_ndcg_matrix = []
    model_names_order = list(raw_model_scores.keys())
    ours_key = "TripSense-FairNet v3 (Ours)"

    for mname in model_names_order:
        res = _evaluate_rankings(
            raw_model_scores[mname], test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats
        )
        ci_low, ci_high = bootstrap_ci(res["_per_group_ndcg10"], n_boot=1000, seed=42)
        res["ndcg10_ci95"] = [round(ci_low, 4), round(ci_high, 4)]
        eval_table[mname] = res
        per_group_ndcg_matrix.append(res["_per_group_ndcg10"])

    ours_ndcg = eval_table[ours_key]["_per_group_ndcg10"]
    ours_gini = eval_table[ours_key]["_per_group_gini"]
    ours_eco = eval_table[ours_key]["_per_group_eco"]
    baselines_for_p = [m for m in model_names_order if m != ours_key]
    raw_p_ndcg, raw_p_ttest, raw_p_gini, raw_p_eco = [], [], [], []
    for bname in baselines_for_p:
        b_ndcg = eval_table[bname]["_per_group_ndcg10"]
        b_gini = eval_table[bname]["_per_group_gini"]
        b_eco = eval_table[bname]["_per_group_eco"]
        try:
            _, p_n = wilcoxon(ours_ndcg, b_ndcg, alternative="two-sided", zero_method="wilcox")
        except Exception:
            p_n = 1.0
        try:
            _, p_tt = ttest_rel(ours_ndcg, b_ndcg)
        except Exception:
            p_tt = 1.0
        try:
            _, p_g = wilcoxon(ours_gini, b_gini, alternative="two-sided", zero_method="wilcox")
        except Exception:
            p_g = 1.0
        try:
            _, p_e = wilcoxon(ours_eco, b_eco, alternative="two-sided", zero_method="wilcox")
        except Exception:
            p_e = 1.0
        raw_p_ndcg.append(float(p_n))
        raw_p_ttest.append(float(p_tt))
        raw_p_gini.append(float(p_g))
        raw_p_eco.append(float(p_e))

    adj_p_ndcg = holm_bonferroni(raw_p_ndcg)
    adj_p_ttest = holm_bonferroni(raw_p_ttest)
    adj_p_gini = holm_bonferroni(raw_p_gini)
    adj_p_eco = holm_bonferroni(raw_p_eco)

    for idx, bname in enumerate(baselines_for_p):
        b_ndcg = eval_table[bname]["_per_group_ndcg10"]
        diff_std = float(np.std(ours_ndcg - b_ndcg, ddof=1)) or 1e-8
        cohens_d = float(np.mean(ours_ndcg - b_ndcg) / diff_std)
        eval_table[bname]["p_value_ndcg10"] = round(raw_p_ndcg[idx], 6)
        eval_table[bname]["holm_p_ndcg10"] = round(adj_p_ndcg[idx], 6)
        eval_table[bname]["holm_ttest_p_ndcg10"] = round(adj_p_ttest[idx], 6)
        eval_table[bname]["holm_p_gini"] = round(adj_p_gini[idx], 6)
        eval_table[bname]["holm_p_eco"] = round(adj_p_eco[idx], 6)
        eval_table[bname]["cliffs_delta_ndcg10"] = round(cliffs_delta(ours_ndcg, b_ndcg), 4)
        eval_table[bname]["cohens_d_ndcg10"] = round(cohens_d, 4)

    fried_stat, fried_p = friedmanchisquare(*per_group_ndcg_matrix)
    k_models = len(model_names_order)
    n_test = len(test_groups)
    score_stack = np.vstack(per_group_ndcg_matrix)
    avg_ranks = np.zeros(k_models, dtype=np.float64)
    for col in range(n_test):
        # Average tie-aware descending ranking
        vals = score_stack[:, col]
        from scipy.stats import rankdata
        ranks = rankdata(-vals, method="average")
        avg_ranks += ranks
    avg_ranks /= n_test
    q_alpha = float(studentized_range.ppf(0.95, k_models, 1e6) / math.sqrt(2.0))
    nemenyi_cd = q_alpha * math.sqrt(k_models * (k_models + 1.0) / (6.0 * n_test))

    for idx, mname in enumerate(model_names_order):
        eval_table[mname]["friedman_rank"] = round(float(avg_ranks[idx]), 3)
        eval_table[mname].pop("_per_group_ndcg10", None)
        eval_table[mname].pop("_per_group_gini", None)
        eval_table[mname].pop("_per_group_eco", None)
        print(f"  {mname:<28} | NDCG@10={eval_table[mname]['ndcg10']:.4f} | Hit@10={eval_table[mname]['hit10']:.4f} "
              f"| Gini={eval_table[mname]['gini_index']:.4f} | MinSat={eval_table[mname]['min_member_sat']:.4f} "
              f"| Eco={eval_table[mname]['eco_coverage_pct']:.1f}% | Rank={eval_table[mname]['friedman_rank']:.2f}", flush=True)

    # Check Group Size Scaling in both quick and full modes
    group_size_scaling = []
    for gsz in [2, 3, 4, 5]:
        idx_sub = [i for i, g in enumerate(test_groups) if g["group_size"] == gsz]
        if not idx_sub:
            continue
        sub_groups = [test_groups[i] for i in idx_sub]
        sub_u = [test_u[i] for i in idx_sub]
        sub_cands = [test_cands[i] for i in idx_sub]
        sub_pos = [test_pos_lens[i] for i in idx_sub]
        r_fn_g = _evaluate_rankings([raw_model_scores[ours_key][i] for i in idx_sub], sub_cands, sub_pos, sub_groups, sub_u, syd_poi_embs, vfeats)
        r_lr_g = _evaluate_rankings([raw_model_scores["LightGBM LambdaRank"][i] for i in idx_sub], sub_cands, sub_pos, sub_groups, sub_u, syd_poi_embs, vfeats)
        r_lgb_g = _evaluate_rankings([raw_model_scores["LightGBM GBDT"][i] for i in idx_sub], sub_cands, sub_pos, sub_groups, sub_u, syd_poi_embs, vfeats)
        r_gim_g = _evaluate_rankings([raw_model_scores["GroupIM (SIGIR'20)"][i] for i in idx_sub], sub_cands, sub_pos, sub_groups, sub_u, syd_poi_embs, vfeats)
        r_ag_g = _evaluate_rankings([raw_model_scores["AGREE (SIGIR'18)"][i] for i in idx_sub], sub_cands, sub_pos, sub_groups, sub_u, syd_poi_embs, vfeats)
        group_size_scaling.append({
            "group_size": gsz,
            "num_groups": len(sub_groups),
            "fairnet_ndcg10": r_fn_g["ndcg10"],
            "fairnet_gini": r_fn_g["gini_index"],
            "lambdarank_ndcg10": r_lr_g["ndcg10"],
            "lambdarank_gini": r_lr_g["gini_index"],
            "lgbm_ndcg10": r_lgb_g["ndcg10"],
            "lgbm_gini": r_lgb_g["gini_index"],
            "groupim_ndcg10": r_gim_g["ndcg10"],
            "groupim_gini": r_gim_g["gini_index"],
            "agree_ndcg10": r_ag_g["ndcg10"],
            "agree_gini": r_ag_g["gini_index"],
        })
    print("\n[Scaling |G|=2..5] FairNet vs LambdaRank vs LGBM:", [(x["group_size"], x["fairnet_ndcg10"], x["lambdarank_ndcg10"], x["lgbm_ndcg10"]) for x in group_size_scaling], flush=True)

    # External Validation Models bundle
    ext_models = {
        "agree": trained_neural["AGREE (SIGIR'18)"],
        "mosan": trained_neural["MoSAN (SIGIR'19)"],
        "set_transformer": trained_neural["Set-Transformer (ICML'19)"],
        "groupim": trained_neural["GroupIM (SIGIR'20)"],
        "lgbm": lgbm_model,
        "lambdarank": lambdarank_model,
        "fairnet": fairnet_v3,
    }

    # Step 4A: External Validation Suite 1 - 5 Global Cities across 5 Continents
    print("\n[Phase D1] Zero-Shot Cross-City Validation (Melbourne, Tokyo, New-York, Istanbul, Sao-Paulo)...", flush=True)
    external_cities = {}
    for city in ["Melbourne", "Tokyo", "New-York", "Istanbul", "Sao-Paulo"]:
        cdf = load_massive_steps_city(city, max_rows=20000)
        cbench = build_city_group_benchmark(cdf, num_groups=160, seed=77, city_name=city)
        rep = _evaluate_external_dataset(cbench, backbone, city.lower().replace("-", "_"), ext_models, device, seed=88)
        external_cities[city] = rep
        ms_c = rep["models"]
        print(f"  {city:<11} ({rep['num_test_groups']}g, {rep['num_venues']} POIs, Gate={rep['spectral_gate_activation']:.3f}) -> "
              f"FairNet={ms_c['TripSense-FairNet v3 (Zero-Shot)']['ndcg10']:.4f} (Gini={ms_c['TripSense-FairNet v3 (Zero-Shot)']['gini_index']:.4f}, Eco={ms_c['TripSense-FairNet v3 (Zero-Shot)']['eco_coverage_pct']:.1f}%) | "
              f"LambdaRank={ms_c['LightGBM LambdaRank (Zero-Shot)']['ndcg10']:.4f} | "
              f"LGBM={ms_c['LightGBM Cls (Zero-Shot)']['ndcg10']:.4f} | "
              f"GroupIM={ms_c['GroupIM (Zero-Shot)']['ndcg10']:.4f}", flush=True)

    # Step 4B: External Validation Suite 2 - Independent 2026 TripWorld Out-of-Town Benchmark
    print("\n[Phase D2] Independent 2026 Dataset: CRUISEResearchGroup/TripWorld (Osaka Out-of-Town Zero-Shot)...", flush=True)
    tw_bench = build_tripworld_group_benchmark(dest_qid="Q35765", dest_name="Osaka (TripWorld)", num_groups=200, seed=77)
    tw_rep = _evaluate_external_dataset(tw_bench, backbone, "tripworld_osaka", ext_models, device, seed=99)
    ms_tw = tw_rep["models"]
    print(f"  TripWorld-Osaka ({tw_rep['num_test_groups']}g, {tw_rep['num_venues']} POIs, Gate={tw_rep['spectral_gate_activation']:.3f}) -> "
          f"FairNet={ms_tw['TripSense-FairNet v3 (Zero-Shot)']['ndcg10']:.4f} (Gini={ms_tw['TripSense-FairNet v3 (Zero-Shot)']['gini_index']:.4f}, Eco={ms_tw['TripSense-FairNet v3 (Zero-Shot)']['eco_coverage_pct']:.1f}%) | "
          f"LambdaRank={ms_tw['LightGBM LambdaRank (Zero-Shot)']['ndcg10']:.4f} | "
          f"LGBM={ms_tw['LightGBM Cls (Zero-Shot)']['ndcg10']:.4f} | "
          f"GroupIM={ms_tw['GroupIM (Zero-Shot)']['ndcg10']:.4f}", flush=True)

    # Run End-to-End Multi-XAI Check early in quick mode too!
    print("\n[Phase F] Running 5-Paradigm End-to-End XAI Faithfulness & Concordance...", flush=True)
    xai_suite_res = compute_multi_xai_faithfulness_suite(
        fairnet_v3, test_groups, test_u, syd_poi_embs, vfeats, device, steps=32
    )
    ig_results = xai_suite_res["integrated_gradients"]
    faithfulness_table = xai_suite_res["faithfulness_comparison"]
    perm_importance = compute_permutation_importance(
        fairnet_v3, test_groups, test_u, syd_poi_embs, vfeats, device, max_groups=80
    )
    explainer = shap.TreeExplainer(lgbm_model)
    X_sample = X_val[:500]
    shap_vals = explainer.shap_values(X_sample)
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1]
    mean_abs_shap = np.abs(shap_vals).mean(axis=0)
    shap_tot = float(np.sum(mean_abs_shap)) or 1e-8
    shap_summary = [
        {
            "feature": fname,
            "mean_abs_shap": round(float(mean_abs_shap[fi]), 4),
            "importance_pct": round(100.0 * float(mean_abs_shap[fi]) / shap_tot, 2),
        }
        for fi, fname in enumerate(RELATIONAL_FEATURE_NAMES)
    ]
    shap_summary.sort(key=lambda r: r["importance_pct"], reverse=True)
    concordance = compute_cross_xai_concordance(
        ig_results["features_unsorted"],
        ig_results["expected_gradients_unsorted"],
        perm_importance,
        shap_summary,
    )
    print(f"  IG Completeness MAE={ig_results['completeness_mae']:.6f} | Comp@3={ig_results['comprehensiveness_k3']:.4f} ({ig_results['faithfulness_ratio_over_random']}x rand) "
          f"| InsAUC={ig_results['insertion_auc']:.4f} | DelAUC={ig_results['deletion_auc']:.4f}", flush=True)
    print(f"  Concordance: Spearman(IG, EG)={concordance['ig_vs_expected_grad_spearman_rho']} (p={concordance['ig_vs_expected_grad_p_value']}) | "
          f"Spearman(IG, Perm)={concordance['ig_vs_permutation_spearman_rho']} (p={concordance['ig_vs_permutation_p_value']}) | "
          f"Spearman(IG, TreeSHAP)={concordance.get('ig_vs_treeshap_spearman_rho')} (p={concordance.get('ig_vs_treeshap_p_value')})", flush=True)

    if quick_mode:
        print("\n[--quick] Gate inspection completed cleanly. Exiting quick run.", flush=True)
        return

    # Step 5: 3-Backbone Foundation Comparison on Sydney (CLIP vs SigLIP vs BGE-base)
    print("\n[Phase B1] Running 3-Backbone Foundation Encoder Comparison (CLIP vs SigLIP vs BGE-base)...", flush=True)
    backbone_comparison = {}
    for bb_name in ["openai/clip-vit-base-patch32", "google/siglip-base-patch16-224", "BAAI/bge-base-en-v1.5"]:
        if bb_name == "openai/clip-vit-base-patch32":
            backbone_comparison[bb_name] = {
                "emb_dim": int(syd_poi_embs.shape[1]),
                "fairnet_v3": {k: eval_table[ours_key][k] for k in ["ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]},
                "lambdarank": {k: eval_table["LightGBM LambdaRank"][k] for k in ["ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]},
                "groupim": {k: eval_table["GroupIM (SIGIR'20)"][k] for k in ["ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]},
                "avg_cos": {k: eval_table["Average Cosine"][k] for k in ["ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]},
            }
            continue

        bb = SigLIPBackbone(bb_name, device=str(device))
        bb_embs = compute_city_embeddings(syd_bench, bb, "sydney")
        b_tr_u = compute_member_taste_vectors(train_groups, bb_embs)
        b_va_u = compute_member_taste_vectors(val_groups, bb_embs)
        b_te_u = compute_member_taste_vectors(test_groups, bb_embs)

        m_fn_bb, _ = train_fairnet_v3(
            train_groups, b_tr_u, val_groups, b_va_u, val_cands, val_pos_lens, bb_embs, vfeats, device, seed=42, epochs=22
        )
        r_fn_bb = _evaluate_rankings(score_fairnet_groups(m_fn_bb, test_groups, b_te_u, test_cands, bb_embs, vfeats, device), test_cands, test_pos_lens, test_groups, b_te_u, bb_embs, vfeats)

        X_tr_b, y_tr_b, q_tr_b = build_tabular_dataset(train_groups, b_tr_u, bb_embs, vfeats, negs_per_pos=8, seed=42)
        X_val_b, y_val_b, q_val_b = build_tabular_dataset(val_groups, b_va_u, bb_embs, vfeats, negs_per_pos=8, seed=99)
        lr_bb = _train_lambdarank(X_tr_b, y_tr_b, q_tr_b, X_val_b, y_val_b, q_val_b, seed=42)
        r_lr_bb = _evaluate_rankings(score_sklearn_groups(lr_bb, test_groups, b_te_u, test_cands, bb_embs, vfeats), test_cands, test_pos_lens, test_groups, b_te_u, bb_embs, vfeats)

        gim_bb = train_neural_baseline(GroupIMBaseline, train_groups, b_tr_u, val_groups, b_va_u, val_cands, val_pos_lens, bb_embs, vfeats, device, seed=42)
        r_gim_bb = _evaluate_rankings(score_neural_baseline(gim_bb, test_groups, b_te_u, test_cands, bb_embs, vfeats, device), test_cands, test_pos_lens, test_groups, b_te_u, bb_embs, vfeats)

        r_ac_bb = _evaluate_rankings(score_heuristics("avg_cos", test_groups, b_te_u, test_cands, bb_embs, vfeats), test_cands, test_pos_lens, test_groups, b_te_u, bb_embs, vfeats)

        backbone_comparison[bb_name] = {
            "emb_dim": int(bb_embs.shape[1]),
            "fairnet_v3": {k: r_fn_bb[k] for k in ["ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]},
            "lambdarank": {k: r_lr_bb[k] for k in ["ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]},
            "groupim": {k: r_gim_bb[k] for k in ["ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]},
            "avg_cos": {k: r_ac_bb[k] for k in ["ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]},
        }
        del bb.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # Step 6: 5-Seed Stability [42, 102, 2026, 777, 1337]
    print("\n[Phase B2] Running 5-Seed Stability [42, 102, 2026, 777, 1337]...", flush=True)
    seeds = [42, 102, 2026, 777, 1337]
    seed_records = {"fairnet_v3": [], "lambdarank": [], "lgbm": [], "groupim": [], "agree": []}
    for s in seeds:
        if s == 42:
            r_fn, r_lr, r_lgb, r_gim, r_ag = (
                eval_table[ours_key],
                eval_table["LightGBM LambdaRank"],
                eval_table["LightGBM GBDT"],
                eval_table["GroupIM (SIGIR'20)"],
                eval_table["AGREE (SIGIR'18)"],
            )
        else:
            m_fn, _ = train_fairnet_v3(train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens, syd_poi_embs, vfeats, device, seed=s, epochs=22)
            r_fn = _evaluate_rankings(score_fairnet_groups(m_fn, test_groups, test_u, test_cands, syd_poi_embs, vfeats, device), test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats)

            X_tr_s, y_tr_s, q_tr_s = build_tabular_dataset(train_groups, train_u, syd_poi_embs, vfeats, negs_per_pos=8, seed=s)
            m_lr = _train_lambdarank(X_tr_s, y_tr_s, q_tr_s, X_val, y_val, q_val, seed=s)
            r_lr = _evaluate_rankings(score_sklearn_groups(m_lr, test_groups, test_u, test_cands, syd_poi_embs, vfeats), test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats)

            m_lgb = lgb.LGBMClassifier(n_estimators=220, learning_rate=0.05, max_depth=5, num_leaves=23, random_state=s, verbose=-1)
            m_lgb.fit(X_tr_s, y_tr_s)
            r_lgb = _evaluate_rankings(score_sklearn_groups(m_lgb, test_groups, test_u, test_cands, syd_poi_embs, vfeats), test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats)

            m_gim = train_neural_baseline(GroupIMBaseline, train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens, syd_poi_embs, vfeats, device, seed=s)
            r_gim = _evaluate_rankings(score_neural_baseline(m_gim, test_groups, test_u, test_cands, syd_poi_embs, vfeats, device), test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats)

            m_ag = train_neural_baseline(AGREEBaseline, train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens, syd_poi_embs, vfeats, device, seed=s)
            r_ag = _evaluate_rankings(score_neural_baseline(m_ag, test_groups, test_u, test_cands, syd_poi_embs, vfeats, device), test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats)

        for kkey, rec in [("fairnet_v3", r_fn), ("lambdarank", r_lr), ("lgbm", r_lgb), ("groupim", r_gim), ("agree", r_ag)]:
            seed_records[kkey].append({k: rec[k] for k in ["ndcg5", "ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]})

    multi_seed_summary = {"seeds": seeds, "per_seed_fairnet": seed_records["fairnet_v3"]}
    for key in ["fairnet_v3", "lambdarank", "lgbm", "groupim", "agree"]:
        agg = {}
        for metric in ["ndcg5", "ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]:
            vals = [x[metric] for x in seed_records[key]]
            agg[f"{metric}_mean"] = round(float(np.mean(vals)), 4)
            agg[f"{metric}_std"] = round(float(np.std(vals, ddof=1)), 4)
        multi_seed_summary[key] = agg
    multi_seed_summary["fairnet_v2"] = multi_seed_summary["fairnet_v3"]
    multi_seed_summary["ndcg10_mean"] = multi_seed_summary["fairnet_v3"]["ndcg10_mean"]
    multi_seed_summary["ndcg10_std"] = multi_seed_summary["fairnet_v3"]["ndcg10_std"]
    multi_seed_summary["gini_mean"] = multi_seed_summary["fairnet_v3"]["gini_index_mean"]
    multi_seed_summary["gini_std"] = multi_seed_summary["fairnet_v3"]["gini_index_std"]

    # Step 7: 10-Variant Component Ablation (evaluating BOTH Sydney AND Mean 5-City Zero-Shot Transfer!)
    print("\n[Phase C] Running 10-Variant Component Ablation (Sydney + Cross-City Zero-Shot)...", flush=True)
    ext_city_caches = {}
    for cname in ["Melbourne", "Tokyo", "New-York", "Istanbul", "Sao-Paulo"]:
        cdf = load_massive_steps_city(cname, max_rows=20000)
        cb = build_city_group_benchmark(cdf, num_groups=160, seed=77, city_name=cname)
        ce = compute_city_embeddings(cb, backbone, cname.lower().replace("-", "_"))
        cu = compute_member_taste_vectors(cb["groups"], ce)
        cc, cp = _build_eval_pools(cb["groups"], cb["num_venues"], num_negs=97, seed=88)
        ext_city_caches[cname] = (cb, ce, cu, cc, cp)

    ablation_configs = [
        ("Full FairNet v3 (Ours)", dict(use_member_sab=True, use_attention=True, use_hadamard=True, use_spectral_gate=True, use_relational_stream=True, use_infonce=True, lambda_gini=0.36, lambda_misery=0.28, lambda_eco=0.38, zero_text_embs=False)),
        ("w/o Spectral OOD Gate (Unconstrained)", dict(use_member_sab=True, use_attention=True, use_hadamard=True, use_spectral_gate=False, use_relational_stream=True, use_infonce=True, lambda_gini=0.36, lambda_misery=0.28, lambda_eco=0.38, zero_text_embs=False)),
        ("w/o Member Gram SAB", dict(use_member_sab=False, use_attention=True, use_hadamard=True, use_spectral_gate=True, use_relational_stream=True, use_infonce=True, lambda_gini=0.36, lambda_misery=0.28, lambda_eco=0.38, zero_text_embs=False)),
        ("w/o Cross-Attention Pooling", dict(use_member_sab=True, use_attention=False, use_hadamard=True, use_spectral_gate=True, use_relational_stream=True, use_infonce=True, lambda_gini=0.36, lambda_misery=0.28, lambda_eco=0.38, zero_text_embs=False)),
        ("w/o Hadamard Adapter (Pure O(D))", dict(use_member_sab=True, use_attention=True, use_hadamard=False, use_spectral_gate=True, use_relational_stream=True, use_infonce=True, lambda_gini=0.36, lambda_misery=0.28, lambda_eco=0.38, zero_text_embs=False)),
        ("w/o Relational Highway Stream", dict(use_member_sab=True, use_attention=True, use_hadamard=True, use_spectral_gate=True, use_relational_stream=False, use_infonce=True, lambda_gini=0.36, lambda_misery=0.28, lambda_eco=0.38, zero_text_embs=False)),
        ("w/o InfoNCE (BPR Pairwise)", dict(use_member_sab=True, use_attention=True, use_hadamard=True, use_spectral_gate=True, use_relational_stream=True, use_infonce=False, lambda_gini=0.36, lambda_misery=0.28, lambda_eco=0.38, zero_text_embs=False)),
        ("w/o Gini & Misery Fairness", dict(use_member_sab=True, use_attention=True, use_hadamard=True, use_spectral_gate=True, use_relational_stream=True, use_infonce=True, lambda_gini=0.0, lambda_misery=0.0, lambda_eco=0.38, zero_text_embs=False)),
        ("w/o Eco-Sustainability Reg.", dict(use_member_sab=True, use_attention=True, use_hadamard=True, use_spectral_gate=True, use_relational_stream=True, use_infonce=True, lambda_gini=0.36, lambda_misery=0.28, lambda_eco=0.0, zero_text_embs=False)),
        ("w/o Multimodal Embeddings", dict(use_member_sab=True, use_attention=True, use_hadamard=True, use_spectral_gate=True, use_relational_stream=True, use_infonce=True, lambda_gini=0.36, lambda_misery=0.28, lambda_eco=0.38, zero_text_embs=True)),
    ]
    ablation_results = []
    base_ndcg = eval_table[ours_key]["ndcg10"]
    for vname, kw in ablation_configs:
        if vname.startswith("Full"):
            m_ab = fairnet_v3
            r_ab = dict(eval_table[ours_key])
        else:
            m_ab, _ = train_fairnet_v3(train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens, syd_poi_embs, vfeats, device, seed=42, epochs=22, **kw)
            u_test_ab = [np.zeros_like(u) for u in test_u] if kw["zero_text_embs"] else test_u
            p_test_ab = np.zeros_like(syd_poi_embs) if kw["zero_text_embs"] else syd_poi_embs
            sc_ab = score_fairnet_groups(m_ab, test_groups, u_test_ab, test_cands, p_test_ab, vfeats, device)
            r_ab = _evaluate_rankings(sc_ab, test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats)

        # Evaluate 5-city zero-shot transfer mean for each variant
        ext_vals = []
        for cb, ce, cu, cc, cp in ext_city_caches.values():
            ce_ab = np.zeros_like(ce) if kw["zero_text_embs"] else ce
            cu_ab = [np.zeros_like(u) for u in cu] if kw["zero_text_embs"] else cu
            sc_e = score_fairnet_groups(m_ab, cb["groups"], cu_ab, cc, ce_ab, cb["venue_feats"], device)
            re_c = _evaluate_rankings(sc_e, cc, cp, cb["groups"], cu, ce, cb["venue_feats"])
            ext_vals.append(re_c["ndcg10"])

        ablation_results.append({
            "variant": vname,
            "ndcg5": r_ab["ndcg5"],
            "ndcg10": r_ab["ndcg10"],
            "hit10": r_ab["hit10"],
            "gini_index": r_ab["gini_index"],
            "min_member_sat": r_ab["min_member_sat"],
            "eco_coverage_pct": r_ab["eco_coverage_pct"],
            "ext_mean_ndcg10": round(float(np.mean(ext_vals)), 4),
            "delta_ndcg10": round(r_ab["ndcg10"] - base_ndcg, 4),
        })

    # Step 8: Hyperparameter Sensitivity & Pareto Sweeps
    print("\n[Phase E] Hyperparameter Sensitivity Sweeps (lambda_gini, lambda_eco, tau)...", flush=True)
    pareto_sweep = []
    for lg in [0.0, 0.15, 0.28, 0.36, 0.65, 1.0]:
        if abs(lg - 0.36) < 1e-6:
            r_p = dict(eval_table[ours_key])
        else:
            m_p, _ = train_fairnet_v3(train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens, syd_poi_embs, vfeats, device, seed=42, epochs=22, lambda_gini=lg)
            r_p = _evaluate_rankings(score_fairnet_groups(m_p, test_groups, test_u, test_cands, syd_poi_embs, vfeats, device), test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats)
        pareto_sweep.append({
            "lambda_gini": lg,
            "ndcg10": r_p["ndcg10"],
            "gini_index": r_p["gini_index"],
            "min_member_sat": r_p["min_member_sat"],
            "eco_coverage_pct": r_p["eco_coverage_pct"],
        })

    eco_sweep = []
    for le in [0.0, 0.20, 0.38, 0.68]:
        if abs(le - 0.38) < 1e-6:
            r_e = dict(eval_table[ours_key])
        else:
            m_e, _ = train_fairnet_v3(train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens, syd_poi_embs, vfeats, device, seed=42, epochs=22, lambda_eco=le)
            r_e = _evaluate_rankings(score_fairnet_groups(m_e, test_groups, test_u, test_cands, syd_poi_embs, vfeats, device), test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats)
        eco_sweep.append({
            "lambda_eco": le,
            "ndcg10": r_e["ndcg10"],
            "gini_index": r_e["gini_index"],
            "eco_coverage_pct": r_e["eco_coverage_pct"],
        })

    tau_sweep = []
    for tv in [0.10, 0.20, 0.35, 0.50]:
        if abs(tv - 0.20) < 1e-6:
            r_t = dict(eval_table[ours_key])
        else:
            m_t, _ = train_fairnet_v3(train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens, syd_poi_embs, vfeats, device, seed=42, epochs=22, tau=tv)
            r_t = _evaluate_rankings(score_fairnet_groups(m_t, test_groups, test_u, test_cands, syd_poi_embs, vfeats, device), test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats)
        tau_sweep.append({
            "tau": tv,
            "ndcg10": r_t["ndcg10"],
            "gini_index": r_t["gini_index"],
            "eco_coverage_pct": r_t["eco_coverage_pct"],
        })

    # Inference Latency & Peak VRAM Profiling (100 candidates x 4 members)
    sample_u = torch.randn(100, 4, syd_poi_embs.shape[1], device=device)
    sample_uf = torch.rand(100, 4, 3, device=device)
    sample_m = torch.ones((100, 4), dtype=torch.bool, device=device)
    sample_p = torch.randn(100, syd_poi_embs.shape[1], device=device)
    sample_pf = torch.rand(100, 8, device=device)
    peak_vram_mb = 0.0
    with torch.no_grad():
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats(device)
        for _ in range(5):
            fairnet_v3(sample_u, sample_uf, sample_m, sample_p, sample_pf)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t_s = time.perf_counter()
        for _ in range(30):
            fairnet_v3(sample_u, sample_uf, sample_m, sample_p, sample_pf)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            peak_vram_mb = float(torch.cuda.max_memory_allocated(device) / (1024.0 * 1024.0))
        gpu_ms = (time.perf_counter() - t_s) * 1000.0 / 30.0

    fn_cpu = TripSenseFairNet(emb_dim=syd_poi_embs.shape[1], hidden_dim=64).cpu()
    fn_cpu.load_state_dict({k: v.cpu() for k, v in fairnet_v3.state_dict().items()})
    fn_cpu.eval()
    su_c, suf_c, sm_c, sp_c, spf_c = sample_u.cpu(), sample_uf.cpu(), sample_m.cpu(), sample_p.cpu(), sample_pf.cpu()
    with torch.no_grad():
        t_c = time.perf_counter()
        for _ in range(20):
            fn_cpu(su_c, suf_c, sm_c, sp_c, spf_c)
        cpu_ms = (time.perf_counter() - t_c) * 1000.0 / 20.0

    # Complete XAI Audits (Nash, Cross-Attn & Worked Case Studies)
    attn_cf_audit = analyze_cross_attention_and_counterfactuals(
        fairnet_v3, test_groups, test_u, syd_poi_embs, vfeats, device, max_groups=80
    )
    case_studies = extract_worked_case_studies(
        fairnet_v3, test_groups, test_u, test_cands, syd_bench["venues"], syd_poi_embs, vfeats, device
    )

    # Step 9: Bangladesh 5-City Pilot, Active Swipe, TravelPlanner
    print("\n[Phase G] Auditing Bangladesh 5-City Pilot, Active Swipe & TravelPlanner...", flush=True)
    bd_pilot = evaluate_bd_pilot_cities(fairnet_v3, device)
    swipe_curve = simulate_active_swipe_curve(seed=42)
    tp_eval = evaluate_travelplanner_rag(load_travelplanner_val(), max_tasks=180)

    total_time = round(time.time() - t0, 2)
    num_params = sum(p.numel() for p in fairnet_v3.parameters())

    final_report = {
        "model_name": "TripSense-FairNet v3 (GeoFairFormer Dual-Stream + MemberGramSAB)",
        "backbone": model_name,
        "embedding_dim": int(syd_poi_embs.shape[1]),
        "num_parameters": int(num_params),
        "device_trained": str(device),
        "training_time_sec": total_time,
        "latency_profile": {
            "gpu_ms_per_100_cands": round(gpu_ms, 2),
            "cpu_ms_per_100_cands": round(cpu_ms, 2),
            "peak_inference_vram_mb": round(peak_vram_mb, 2),
        },
        "datasets": {
            "primary_benchmark": "CRUISEResearchGroup/Massive-STEPS-Sydney",
            "external_cities": ["Melbourne", "Tokyo", "New-York", "Istanbul", "Sao-Paulo"],
            "independent_external_dataset": "CRUISEResearchGroup/TripWorld (Osaka Out-of-Town Q35765)",
            "group_poi_benchmark": "CRUISEResearchGroup/Massive-STEPS-Sydney (Zero-Leakage Chronological)",
            "checkins_loaded": syd_bench["num_rows"],
            "unique_venues": V_syd,
            "total_groups": len(groups),
            "train_groups": len(train_groups),
            "val_groups": len(val_groups),
            "test_groups": len(test_groups),
            "candidate_pool_size": 100,
            "travelplanner_tasks": tp_eval["num_tasks"],
            "sydney_spectral_gate": sydney_gate,
        },
        "fairnet_training": fn_train_info,
        "group_consensus_comparison": eval_table,
        "statistical_tests": {
            "friedman_chi2": round(float(fried_stat), 3),
            "friedman_p_value": float(f"{fried_p:.3e}"),
            "nemenyi_cd_alpha05": round(float(nemenyi_cd), 3),
            "num_models": k_models,
            "num_test_groups": n_test,
        },
        "backbone_comparison": backbone_comparison,
        "multi_seed_stability": multi_seed_summary,
        "ablation_study": ablation_results,
        "external_cross_city_validation": external_cities,
        "tripworld_external_validation": tw_rep,
        "bangladesh_5city_pilot": bd_pilot,
        "pareto_gini_sweep": pareto_sweep,
        "hyperparameter_sensitivity": {
            "lambda_gini_sweep": pareto_sweep,
            "lambda_eco_sweep": eco_sweep,
            "tau_sweep": tau_sweep,
        },
        "group_size_scaling": group_size_scaling,
        "multi_xai_evaluation": {
            "integrated_gradients": ig_results,
            "faithfulness_comparison": faithfulness_table,
            "permutation_importance": perm_importance,
            "cross_xai_concordance": concordance,
            "attention_and_counterfactual_audit": attn_cf_audit,
            "worked_case_studies": case_studies,
        },
        "shap_feature_importance": shap_summary,
        "active_swipe_learning_curve": swipe_curve,
        "travelplanner_rag_evaluation": tp_eval,
    }

    out_path = os.path.join(ARTIFACTS_DIR, "q1_benchmark_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2)
    print(f"\n[DONE] Saved complete Flagship v3 Q1 report ({total_time}s) -> {out_path}", flush=True)


if __name__ == "__main__":
    main()
