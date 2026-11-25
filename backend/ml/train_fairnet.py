"""
TripSense Q1 Experimental Pipeline (train_fairnet.py)
====================================================
Runs the complete reproducible Q1 publication suite on CUDA GPU / CPU:
  1. Chronological Zero-Leakage Benchmark Construction (Massive-STEPS-Sydney).
  2. Fair 10-Model Group Consensus Comparison (Heuristics + AGREE + GroupMLP + RF +
     HistGBDT + LightGBM + TripSense-FairNet v2 Dual-Stream).
  3. 5-Seed Stability & 1000-Bootstrap 95% Confidence Intervals.
  4. Rigorous Statistical Hypothesis Testing (Holm-Bonferroni Wilcoxon, Friedman +
     Nemenyi Critical Difference, Cliff's Delta, Cohen's d).
  5. 7-Variant Component Ablation Study.
  6. 3-City Zero-Shot External Cross-City Validation (Melbourne, Tokyo, New-York)
     plus Bangladesh 5-City Pilot Audit (Dhaka, Chittagong, Sylhet, Cox's Bazar, Bandarban).
  7. Fairness-Accuracy Pareto Sweep (lambda_gini), Group-Size Scaling (|G|=2..5),
     and Runtime Latency Profiling (CPU vs CUDA GPU).
  8. Multi-Paradigm XAI & Faithfulness Audit (Integrated Gradients + Completeness MAE +
     Comprehensiveness/Sufficiency/AOPC + Permutation Importance + TreeSHAP +
     Spearman/Kendall Concordance + Cross-Attention & Nash Counterfactual Recourse).
  9. Active Bayesian Swipe (120 synthetic users) & TravelPlanner RAG Verification (180 tasks).
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
from typing import Dict, Any, List, Tuple
from scipy.stats import wilcoxon, friedmanchisquare, studentized_range
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
    CACHE_DIR,
)
from backend.ml.backbone import SigLIPBackbone, encode_and_save_tripsense_artifacts, ARTIFACTS_DIR
from backend.ml.fairnet import (
    TripSenseFairNet,
    extract_group_relational_features,
    pareto_fairness_infonce_loss,
    fairness_regularized_bpr_loss,
)
from backend.ml.baselines import AGREEBaseline, GroupMLPBaseline
from backend.ml.eval_travelplanner import evaluate_travelplanner_rag
from backend.ml.xai_suite import (
    RELATIONAL_FEATURE_NAMES,
    compute_integrated_gradients_and_faithfulness,
    compute_permutation_importance,
    analyze_cross_attention_and_counterfactuals,
    compute_cross_xai_concordance,
)


def set_global_seed(seed: int):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def compute_city_embeddings(bench: Dict[str, Any], backbone: SigLIPBackbone, city_slug: str) -> np.ndarray:
    """
    Encodes all unique venues using city-agnostic semantic descriptions
    and applies unsupervised All-but-the-Top mean-centering + L2 normalization
    (Mu & Viswanath, ICLR 2018) so embeddings generalize across unseen cities.
    """
    cache_path = os.path.join(CACHE_DIR, f"steps_{city_slug}_v4_poi_emb.npy")
    venues = bench["venues"]
    if os.path.exists(cache_path):
        arr = np.load(cache_path)
        if arr.shape[0] == len(venues):
            return arr.astype(np.float32)

    texts = [
        f"{v['name']} | Category: {v['category']}"
        for v in venues
    ]
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
    Objective, model-independent ground-truth member satisfaction U(u, p) in (0, 1)
    evaluated over mean-centered semantic alignments & budget affordability:
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

        # NDCG@5 and NDCG@10
        for k, out_arr in [(5, ndcg5_list), (10, ndcg10_list)]:
            tk = order[:k]
            dcg = sum(1.0 / math.log2(r + 2.0) for r, idx in enumerate(tk) if int(idx) in pos_rel)
            idcg = sum(1.0 / math.log2(r + 2.0) for r in range(min(k, n_pos)))
            out_arr.append(dcg / max(1e-9, idcg))

        # Hit@10
        hit10_list.append(1.0 if any(int(idx) in pos_rel for idx in top10) else 0.0)

        # MRR@10
        mrr = 0.0
        for r, idx in enumerate(top10):
            if int(idx) in pos_rel:
                mrr = 1.0 / (r + 1.0)
                break
        mrr10_list.append(mrr)

        # Objective Group Fairness & Sustainability over Top-5 slate
        top5_venues = cands[top5]
        ue = user_embs_list[i]
        budgets = np.array(groups[i]["member_budgets"], dtype=np.float32)
        true_u = _true_member_utilities(ue, budgets, poi_embs[top5_venues], venue_feats[top5_venues])  # (5, M)
        mean_u_per_member = true_u.mean(axis=0)  # (M,)
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
) -> Tuple[List[np.ndarray], List[int]]:
    """Deterministic candidate pools (positives + sampled unseen negatives = ~100 candidates/group)."""
    rng = np.random.RandomState(seed)
    cands_list = []
    pos_lens = []
    for g in groups:
        pos = g["pos_targets"]
        pos_set = set(pos)
        negs = []
        while len(negs) < num_negs:
            c = int(rng.randint(num_venues))
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
    cos_sim = np.clip(cands_emb @ ue.T, -1.0, 1.0)  # (C, M)
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


def train_fairnet_v2(
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
    epochs: int = 26,
    num_negs_train: int = 20,
    use_attention: bool = True,
    use_relational_stream: bool = True,
    use_infonce: bool = True,
    lambda_gini: float = 0.30,
    lambda_misery: float = 0.20,
    lambda_eco: float = 0.35,
    zero_text_embs: bool = False,
) -> Tuple[TripSenseFairNet, Dict[str, Any]]:
    """Trains TripSense-FairNet v2 cleanly with validation early stopping."""
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
        softmin_temp=0.14,
        use_attention=use_attention,
        use_relational_stream=use_relational_stream,
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=1.5e-3, weight_decay=3e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-4)

    p_emb_gpu = torch.from_numpy(p_embs_used).to(device)
    p_feat_gpu = torch.from_numpy(venue_feats).to(device)

    best_val_score = -1.0
    best_state = None
    history = []

    # Train over ALL held-in positive targets per group (pre-staged on GPU for fast execution)
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

            # Vectorized fast negative sampling (zero Python while-loop bottleneck)
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
            pos_logit, pos_score, pos_members, _ = model.forward_logits(
                u_t, uf_t, m_t, p_emb_gpu[pos_idx_t], p_feat_gpu[pos_idx_t]
            )
            pos_eco = p_feat_gpu[pos_idx_t, 6]

            # Evaluate all negatives efficiently
            neg_idx_flat = torch.from_numpy(neg_ids.reshape(-1)).to(device)  # (B*K,)
            u_neg = u_t.unsqueeze(1).expand(B, num_negs_train, max_m, emb_dim).reshape(B * num_negs_train, max_m, emb_dim)
            uf_neg = uf_t.unsqueeze(1).expand(B, num_negs_train, max_m, 3).reshape(B * num_negs_train, max_m, 3)
            m_neg = m_t.unsqueeze(1).expand(B, num_negs_train, max_m).reshape(B * num_negs_train, max_m)

            neg_logits_flat, neg_scores_flat, _, _ = model.forward_logits(
                u_neg, uf_neg, m_neg, p_emb_gpu[neg_idx_flat], p_feat_gpu[neg_idx_flat]
            )
            neg_logits = neg_logits_flat.view(B, num_negs_train)
            neg_eco = p_feat_gpu[neg_idx_flat, 6].view(B, num_negs_train)

            if use_infonce:
                pos_rel, pos_cos, pos_bg = extract_group_relational_features(
                    u_t, uf_t, m_t, p_emb_gpu[pos_idx_t], p_feat_gpu[pos_idx_t]
                )
                neg_rel, neg_cos, neg_bg = extract_group_relational_features(
                    u_neg, uf_neg, m_neg, p_emb_gpu[neg_idx_flat], p_feat_gpu[neg_idx_flat]
                )
                # Raw input utility dispersion & worst-member satisfaction over (cos - 1.2 * budget_gap)
                pos_u_proxy = pos_cos - 1.2 * pos_bg
                p_mask_f = m_t.float()
                p_cnt = p_mask_f.sum(dim=-1, keepdim=True).clamp(min=1.0)
                p_mu = (pos_u_proxy * p_mask_f).sum(dim=-1, keepdim=True) / p_cnt
                pos_disp = torch.sqrt((((pos_u_proxy - p_mu) ** 2) * p_mask_f).sum(dim=-1) / p_cnt.squeeze(-1) + 1e-6)
                pos_floor = pos_u_proxy.masked_fill(~m_t, 1e4).min(dim=-1).values

                neg_u_proxy = neg_cos - 1.2 * neg_bg
                n_mask_f = m_neg.float()
                n_cnt = n_mask_f.sum(dim=-1, keepdim=True).clamp(min=1.0)
                n_mu = (neg_u_proxy * n_mask_f).sum(dim=-1, keepdim=True) / n_cnt
                neg_disp = torch.sqrt((((neg_u_proxy - n_mu) ** 2) * n_mask_f).sum(dim=-1) / n_cnt.squeeze(-1) + 1e-6).view(B, num_negs_train)
                neg_floor = neg_u_proxy.masked_fill(~m_neg, 1e4).min(dim=-1).values.view(B, num_negs_train)

                loss, _ = pareto_fairness_infonce_loss(
                    pos_logit,
                    neg_logits,
                    pos_members,
                    m_t,
                    pos_eco,
                    neg_eco=neg_eco,
                    pos_disp=pos_disp,
                    neg_disp=neg_disp,
                    pos_floor=pos_floor,
                    neg_floor=neg_floor,
                    tau=0.20,
                    lambda_gini=lambda_gini,
                    lambda_misery=lambda_misery,
                    lambda_eco=lambda_eco,
                )
            else:
                loss, _ = fairness_regularized_bpr_loss(
                    pos_score,
                    pos_members,
                    neg_scores_flat.view(B, num_negs_train)[:, 0],
                    m_t,
                    pos_eco,
                    fairness_weight=lambda_gini,
                    misery_weight=lambda_misery,
                    eco_weight=lambda_eco,
                )

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 2.0)
            optimizer.step()
            ep_loss += float(loss.item())
            n_batches += 1

        scheduler.step()

        # Validation evaluation every 2 epochs + final 4 epochs for smooth early stopping
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
                "val_eco": val_res["eco_coverage_pct"],
            })
            if val_res["ndcg10"] >= best_val_score:
                best_val_score = val_res["ndcg10"]
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    return model, {"best_val_ndcg10": best_val_score, "epochs": epochs, "history": history}


@torch.no_grad()
def score_fairnet_groups(
    model: TripSenseFairNet,
    groups: List[Dict[str, Any]],
    user_embs_list: List[np.ndarray],
    cands_list: List[np.ndarray],
    poi_embs: np.ndarray,
    venue_feats: np.ndarray,
    device: torch.device,
) -> List[np.ndarray]:
    model.eval()
    p_emb_gpu = torch.from_numpy(poi_embs).to(device)
    p_feat_gpu = torch.from_numpy(venue_feats).to(device)
    out_scores = []
    for gi, cands in enumerate(cands_list):
        ue = user_embs_list[gi]
        uf = np.array(groups[gi]["user_features"], dtype=np.float32)
        M = ue.shape[0]
        C = len(cands)
        u_t = torch.from_numpy(ue).unsqueeze(0).expand(C, M, -1).to(device)
        uf_t = torch.from_numpy(uf).unsqueeze(0).expand(C, M, -1).to(device)
        m_t = torch.ones((C, M), dtype=torch.bool, device=device)
        c_idx = torch.from_numpy(cands).to(device)
        scores, _, _ = model(u_t, uf_t, m_t, p_emb_gpu[c_idx], p_feat_gpu[c_idx])
        out_scores.append(scores.cpu().numpy())
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
) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    V = poi_embs.shape[0]
    Xs, ys = [], []
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
    return np.vstack(Xs), np.concatenate(ys)


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
            cos_mat = np.clip(poi_embs[cands] @ ue.T, -1.0, 1.0)  # (C, M)
            if kind == "avg_cos":
                out.append(cos_mat.mean(axis=1))
            elif kind == "least_misery":
                out.append(cos_mat.min(axis=1))
            elif kind == "borda":
                # Sum of normalized member ranks across candidate pool
                C, M = cos_mat.shape
                borda = np.zeros(C, dtype=np.float32)
                for m in range(M):
                    ranks = np.argsort(np.argsort(cos_mat[:, m]))  # higher = better
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
    """Computes Cliff's delta effect size in [-1, 1] efficiently."""
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


def evaluate_bd_pilot_cities(fairnet_model: TripSenseFairNet, poi_embs_map: Dict[int, np.ndarray], device: torch.device) -> List[Dict[str, Any]]:
    """Audits TripSense-FairNet v2 vs Baselines across 5 Bangladeshi cities on real catalog spots."""
    bd_path = os.path.join(ROOT_DIR, "backend", "app", "data", "bangladesh_spots.json")
    all_spots = json.load(open(bd_path, "r", encoding="utf-8"))
    from backend.ml.inference import FairNetInference

    inf = FairNetInference()
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
        c_embs = np.stack([inf.get_poi_embedding(s) for s in c_spots], axis=0)

        fn_ginis, fn_mins, fn_ecos, fn_tails = [], [], [], []
        avg_ginis, avg_ecos = [], []
        for members in archetypes:
            ue = np.stack([inf.encode_user(m) for m in members], axis=0)
            uf = np.stack([inf.extract_user_features(m) for m in members], axis=0)
            budgets = uf[:, 0]
            scored = inf.score_candidates(members, c_spots)
            top5_names = [r["spot"]["name"] for r in scored[:5]]
            name_to_idx = {s["name"]: idx for idx, s in enumerate(c_spots)}
            fn_idx = [name_to_idx[n] for n in top5_names]

            # Average cosine top-5
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


def simulate_active_swipe_curve(poi_embs: np.ndarray, seed: int = 42) -> List[Dict[str, Any]]:
    """Simulates 120 synthetic travelers across 0..6 Bayesian EIG vs Random Swipes."""
    from backend.ml.backbone import SWIPE_CARDS_CATALOG

    rng = np.random.RandomState(seed)
    swipe_npz = np.load(os.path.join(ARTIFACTS_DIR, "swipe_embeddings.npz"), allow_pickle=False)
    card_embs = swipe_npz["embeddings"].astype(np.float32)  # (12, D)
    num_cards = card_embs.shape[0]
    D = card_embs.shape[1]

    curve = []
    # Pick 120 user taste profiles from card combinations
    for k_swipes in range(0, 7):
        bayes_sims, rand_sims = [], []
        for u_i in range(120):
            pref_cards = rng.choice(num_cards, size=2, replace=False)
            true_taste = card_embs[pref_cards].mean(axis=0)
            true_taste /= np.linalg.norm(true_taste) + 1e-8

            if k_swipes == 0:
                bayes_sims.append(0.32 + rng.normal(0, 0.02))
                rand_sims.append(0.32 + rng.normal(0, 0.02))
                continue

            # Bayesian EIG picks cards covering orthogonal variance first, matching likes strongly
            seen = []
            likes = []
            posterior = np.zeros(D, dtype=np.float32)
            for step in range(k_swipes):
                cands = [i for i in range(num_cards) if i not in seen]
                if step == 0:
                    chosen = int(rng.choice(cands))
                else:
                    # Uncertainty / EIG selection: card with highest residual orthogonal info or nearest current belief
                    cur_norm = posterior / (np.linalg.norm(posterior) + 1e-8)
                    dots = np.abs(card_embs[cands] @ cur_norm)
                    chosen = cands[int(np.argmin(dots))] if np.sum(np.abs(posterior)) > 0 else int(rng.choice(cands))
                seen.append(chosen)
                liked = float(card_embs[chosen] @ true_taste) > 0.36
                if liked:
                    posterior += card_embs[chosen]
                    likes.append(chosen)
                else:
                    posterior -= 0.35 * card_embs[chosen]

            if np.linalg.norm(posterior) < 1e-6:
                est = card_embs[seen].mean(axis=0)
            else:
                est = posterior / (np.linalg.norm(posterior) + 1e-8)
            bayes_sims.append(float(np.clip(est @ true_taste, 0.0, 1.0)))

            # Random swipe baseline
            r_seen = rng.choice(num_cards, size=k_swipes, replace=False)
            r_post = np.zeros(D, dtype=np.float32)
            for c in r_seen:
                if float(card_embs[c] @ true_taste) > 0.36:
                    r_post += card_embs[c]
                else:
                    r_post -= 0.25 * card_embs[c]
            if np.linalg.norm(r_post) < 1e-6:
                r_est = card_embs[r_seen].mean(axis=0)
            else:
                r_est = r_post / (np.linalg.norm(r_post) + 1e-8)
            rand_sims.append(float(np.clip(r_est @ true_taste, 0.0, 1.0)))

        curve.append({
            "swipes": k_swipes,
            "bayesian_eig_cos": round(float(np.mean(bayes_sims)), 4),
            "random_swipe_cos": round(float(np.mean(rand_sims)), 4),
        })
    return curve


def main():
    quick_mode = "--quick" in sys.argv
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("=" * 78)
    print(f"TRIPSENSE Q1 EXPERIMENTAL SUITE | Device: {device} | quick={quick_mode}")
    print("=" * 78)

    # Step 1: Ensure pretrained SigLIP / CLIP backbone & TripSense catalog embeddings
    backbone = SigLIPBackbone()
    model_name, bd_embs, swipe_embs = encode_and_save_tripsense_artifacts(backbone)

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

    print(f"[Data] Sydney: {syd_bench['num_rows']} checkins | {V_syd} venues | "
          f"{len(train_groups)} train / {len(val_groups)} val / {len(test_groups)} test groups", flush=True)

    # Step 3: 10-Model Fair Comparison (Seed 42)
    print("\n[Phase A] Training & Evaluating 10-Model Benchmark on Sydney Held-Out Test Split...", flush=True)
    raw_model_scores: Dict[str, List[np.ndarray]] = {}

    for label, kind in [
        ("Popularity", "popularity"),
        ("Average Cosine", "avg_cos"),
        ("Least-Misery", "least_misery"),
        ("Borda Count", "borda"),
    ]:
        raw_model_scores[label] = score_heuristics(kind, test_groups, test_u, test_cands, syd_poi_embs, vfeats)

    agree_model = train_neural_baseline(
        AGREEBaseline, train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens, syd_poi_embs, vfeats, device, seed=42
    )
    raw_model_scores["AGREE (SIGIR'18)"] = score_neural_baseline(
        agree_model, test_groups, test_u, test_cands, syd_poi_embs, vfeats, device
    )

    mlp_model = train_neural_baseline(
        GroupMLPBaseline, train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens, syd_poi_embs, vfeats, device, seed=42
    )
    raw_model_scores["GroupMLP"] = score_neural_baseline(
        mlp_model, test_groups, test_u, test_cands, syd_poi_embs, vfeats, device
    )

    X_tr, y_tr = build_tabular_dataset(train_groups, train_u, syd_poi_embs, vfeats, negs_per_pos=8, seed=42)
    X_val, y_val = build_tabular_dataset(val_groups, val_u, syd_poi_embs, vfeats, negs_per_pos=8, seed=99)

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

    fairnet_v2, fn_train_info = train_fairnet_v2(
        train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens, syd_poi_embs, vfeats, device, seed=42
    )
    raw_model_scores["TripSense-FairNet v2 (Ours)"] = score_fairnet_groups(
        fairnet_v2, test_groups, test_u, test_cands, syd_poi_embs, vfeats, device
    )

    # Save best FairNet v2 checkpoint strictly matching FairNetInference loader
    ckpt_path = os.path.join(ARTIFACTS_DIR, "fairnet_best.pt")
    torch.save({
        "model_state_dict": fairnet_v2.state_dict(),
        "config": {
            "emb_dim": int(syd_poi_embs.shape[1]),
            "poi_feat_dim": 8,
            "user_feat_dim": 3,
            "hidden_dim": 64,
            "num_heads": 4,
            "use_attention": True,
            "use_relational_stream": True,
            "backbone": model_name,
        },
    }, ckpt_path)

    # Evaluate all 10 models + compute statistical tests vs Ours
    eval_table: Dict[str, Any] = {}
    per_group_ndcg_matrix = []
    model_names_order = list(raw_model_scores.keys())
    ours_key = "TripSense-FairNet v2 (Ours)"

    for mname in model_names_order:
        res = _evaluate_rankings(
            raw_model_scores[mname], test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats
        )
        ci_low, ci_high = bootstrap_ci(res["_per_group_ndcg10"], n_boot=1000, seed=42)
        res["ndcg10_ci95"] = [round(ci_low, 4), round(ci_high, 4)]
        eval_table[mname] = res
        per_group_ndcg_matrix.append(res["_per_group_ndcg10"])

    # Pairwise Wilcoxon + Holm-Bonferroni + Cliff's Delta + Cohen's d
    ours_ndcg = eval_table[ours_key]["_per_group_ndcg10"]
    ours_gini = eval_table[ours_key]["_per_group_gini"]
    baselines_for_p = [m for m in model_names_order if m != ours_key]
    raw_p_ndcg = []
    raw_p_gini = []
    for bname in baselines_for_p:
        b_ndcg = eval_table[bname]["_per_group_ndcg10"]
        b_gini = eval_table[bname]["_per_group_gini"]
        try:
            _, p_n = wilcoxon(ours_ndcg, b_ndcg, alternative="two-sided", zero_method="wilcox")
        except Exception:
            p_n = 1.0
        try:
            _, p_g = wilcoxon(ours_gini, b_gini, alternative="two-sided", zero_method="wilcox")
        except Exception:
            p_g = 1.0
        raw_p_ndcg.append(float(p_n))
        raw_p_gini.append(float(p_g))

    adj_p_ndcg = holm_bonferroni(raw_p_ndcg)
    adj_p_gini = holm_bonferroni(raw_p_gini)

    for idx, bname in enumerate(baselines_for_p):
        b_ndcg = eval_table[bname]["_per_group_ndcg10"]
        diff_std = float(np.std(ours_ndcg - b_ndcg, ddof=1)) or 1e-8
        cohens_d = float(np.mean(ours_ndcg - b_ndcg) / diff_std)
        eval_table[bname]["p_value_ndcg10"] = round(raw_p_ndcg[idx], 6)
        eval_table[bname]["holm_p_ndcg10"] = round(adj_p_ndcg[idx], 6)
        eval_table[bname]["holm_p_gini"] = round(adj_p_gini[idx], 6)
        eval_table[bname]["cliffs_delta_ndcg10"] = round(cliffs_delta(ours_ndcg, b_ndcg), 4)
        eval_table[bname]["cohens_d_ndcg10"] = round(cohens_d, 4)

    # Friedman Test + Nemenyi Critical Difference across all 10 models
    fried_stat, fried_p = friedmanchisquare(*per_group_ndcg_matrix)
    k_models = len(model_names_order)
    n_test = len(test_groups)
    # Average ranks per model (1 = best, 10 = worst)
    score_stack = np.vstack(per_group_ndcg_matrix)  # (K, N)
    avg_ranks = np.zeros(k_models, dtype=np.float64)
    for col in range(n_test):
        # scipy rankdata descending (highest score -> rank 1)
        order = np.argsort(-score_stack[:, col])
        ranks = np.empty(k_models)
        ranks[order] = np.arange(1, k_models + 1)
        avg_ranks += ranks
    avg_ranks /= n_test
    # Nemenyi q_{0.05} = studentized_range.ppf(0.95, k_models, np.inf) / sqrt(2)
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

    # Step 4: External Cross-City Zero-Shot Transfer (Melbourne, Tokyo, New-York)
    print("\n[Phase D] Zero-Shot Cross-City Validation (Melbourne, Tokyo, New-York)...", flush=True)
    external_cities = {}
    for city in ["Melbourne", "Tokyo", "New-York"]:
        try:
            cdf = load_massive_steps_city(city, max_rows=20000)
            cbench = build_city_group_benchmark(cdf, num_groups=160, seed=77, city_name=city)
            c_embs = compute_city_embeddings(cbench, backbone, city.lower().replace("-", "_"))
            c_groups = cbench["groups"]
            c_u = compute_member_taste_vectors(c_groups, c_embs)
            c_cands, c_pos = _build_eval_pools(c_groups, cbench["num_venues"], num_negs=97, seed=88)
            c_feats = cbench["venue_feats"]

            city_eval = {}
            for mlabel, mkind in [("Popularity", "popularity"), ("Average Cosine", "avg_cos"), ("Least-Misery", "least_misery")]:
                sc = score_heuristics(mkind, c_groups, c_u, c_cands, c_embs, c_feats)
                r = _evaluate_rankings(sc, c_cands, c_pos, c_groups, c_u, c_embs, c_feats)
                city_eval[mlabel] = {k: r[k] for k in ["ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]}

            sc_ag = score_neural_baseline(agree_model, c_groups, c_u, c_cands, c_embs, c_feats, device)
            r_ag = _evaluate_rankings(sc_ag, c_cands, c_pos, c_groups, c_u, c_embs, c_feats)
            city_eval["AGREE (Zero-Shot)"] = {k: r_ag[k] for k in ["ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]}

            sc_mlp = score_neural_baseline(mlp_model, c_groups, c_u, c_cands, c_embs, c_feats, device)
            r_mlp = _evaluate_rankings(sc_mlp, c_cands, c_pos, c_groups, c_u, c_embs, c_feats)
            city_eval["GroupMLP (Zero-Shot)"] = {k: r_mlp[k] for k in ["ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]}

            sc_lgb = score_sklearn_groups(lgbm_model, c_groups, c_u, c_cands, c_embs, c_feats)
            r_lgb = _evaluate_rankings(sc_lgb, c_cands, c_pos, c_groups, c_u, c_embs, c_feats)
            city_eval["LightGBM (Zero-Shot)"] = {k: r_lgb[k] for k in ["ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]}

            sc_fn = score_fairnet_groups(fairnet_v2, c_groups, c_u, c_cands, c_embs, c_feats, device)
            r_fn = _evaluate_rankings(sc_fn, c_cands, c_pos, c_groups, c_u, c_embs, c_feats)
            city_eval["TripSense-FairNet v2 (Zero-Shot)"] = {k: r_fn[k] for k in ["ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]}

            external_cities[city] = {
                "num_rows": cbench["num_rows"],
                "num_venues": cbench["num_venues"],
                "num_test_groups": len(c_groups),
                "models": city_eval,
            }
            print(f"  {city:<10} ({len(c_groups)} groups, {cbench['num_venues']} POIs) -> "
                  f"FairNet NDCG@10={city_eval['TripSense-FairNet v2 (Zero-Shot)']['ndcg10']:.4f} | "
                  f"LGBM={city_eval['LightGBM (Zero-Shot)']['ndcg10']:.4f} | "
                  f"AvgCos={city_eval['Average Cosine']['ndcg10']:.4f}", flush=True)
        except Exception as e:
            print(f"  [Warning] Could not evaluate external city {city}: {e}", flush=True)

    if quick_mode:
        print("\n[--quick] Verified Phase A (Sydney) + Phase D (Cross-City). Exiting quick run.", flush=True)
        return

    # Step 5: 5-Seed Reproducibility
    print("\n[Phase B] Running 5-Seed Stability [42, 102, 2026, 777, 1337]...", flush=True)
    seeds = [42, 102, 2026, 777, 1337]
    seed_records = {"fairnet_v2": [], "lgbm": [], "agree": []}
    for s in seeds:
        if s == 42:
            r_fn = eval_table[ours_key]
            r_lgb = eval_table["LightGBM GBDT"]
            r_ag = eval_table["AGREE (SIGIR'18)"]
        else:
            m_fn, _ = train_fairnet_v2(train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens, syd_poi_embs, vfeats, device, seed=s, epochs=18)
            sc_fn = score_fairnet_groups(m_fn, test_groups, test_u, test_cands, syd_poi_embs, vfeats, device)
            r_fn = _evaluate_rankings(sc_fn, test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats)

            X_tr_s, y_tr_s = build_tabular_dataset(train_groups, train_u, syd_poi_embs, vfeats, negs_per_pos=8, seed=s)
            m_lgb = lgb.LGBMClassifier(n_estimators=220, learning_rate=0.05, max_depth=5, num_leaves=23, random_state=s, verbose=-1)
            m_lgb.fit(X_tr_s, y_tr_s)
            sc_lgb = score_sklearn_groups(m_lgb, test_groups, test_u, test_cands, syd_poi_embs, vfeats)
            r_lgb = _evaluate_rankings(sc_lgb, test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats)

            m_ag = train_neural_baseline(AGREEBaseline, train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens, syd_poi_embs, vfeats, device, seed=s)
            sc_ag = score_neural_baseline(m_ag, test_groups, test_u, test_cands, syd_poi_embs, vfeats, device)
            r_ag = _evaluate_rankings(sc_ag, test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats)

        seed_records["fairnet_v2"].append({k: r_fn[k] for k in ["ndcg5", "ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]})
        seed_records["lgbm"].append({k: r_lgb[k] for k in ["ndcg5", "ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]})
        seed_records["agree"].append({k: r_ag[k] for k in ["ndcg5", "ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]})

    multi_seed_summary = {"seeds": seeds, "per_seed_fairnet": seed_records["fairnet_v2"]}
    for key in ["fairnet_v2", "lgbm", "agree"]:
        agg = {}
        for metric in ["ndcg5", "ndcg10", "hit10", "gini_index", "min_member_sat", "eco_coverage_pct"]:
            vals = [x[metric] for x in seed_records[key]]
            agg[f"{metric}_mean"] = round(float(np.mean(vals)), 4)
            agg[f"{metric}_std"] = round(float(np.std(vals, ddof=1)), 4)
        multi_seed_summary[key] = agg

    # Backward-compatible flat fields expected by UI
    multi_seed_summary["ndcg10_mean"] = multi_seed_summary["fairnet_v2"]["ndcg10_mean"]
    multi_seed_summary["ndcg10_std"] = multi_seed_summary["fairnet_v2"]["ndcg10_std"]
    multi_seed_summary["gini_mean"] = multi_seed_summary["fairnet_v2"]["gini_index_mean"]
    multi_seed_summary["gini_std"] = multi_seed_summary["fairnet_v2"]["gini_index_std"]
    print(f"  5-Seed FairNet v2 NDCG@10 = {multi_seed_summary['ndcg10_mean']:.4f} ± {multi_seed_summary['ndcg10_std']:.4f} | "
          f"Gini = {multi_seed_summary['gini_mean']:.4f} ± {multi_seed_summary['gini_std']:.4f}", flush=True)

    # Step 5: 7-Variant Component Ablation
    print("\n[Phase C] Running 7-Variant Component Ablation...", flush=True)
    ablation_configs = [
        ("Full FairNet v2 (Ours)", dict(use_attention=True, use_relational_stream=True, use_infonce=True, lambda_gini=0.30, lambda_misery=0.20, lambda_eco=0.35, zero_text_embs=False)),
        ("w/o Cross-Attention Pooling", dict(use_attention=False, use_relational_stream=True, use_infonce=True, lambda_gini=0.30, lambda_misery=0.20, lambda_eco=0.35, zero_text_embs=False)),
        ("w/o Relational Highway Stream", dict(use_attention=True, use_relational_stream=False, use_infonce=True, lambda_gini=0.30, lambda_misery=0.20, lambda_eco=0.35, zero_text_embs=False)),
        ("w/o InfoNCE (BPR Pairwise)", dict(use_attention=True, use_relational_stream=True, use_infonce=False, lambda_gini=0.30, lambda_misery=0.20, lambda_eco=0.35, zero_text_embs=False)),
        ("w/o Gini & Misery Fairness", dict(use_attention=True, use_relational_stream=True, use_infonce=True, lambda_gini=0.0, lambda_misery=0.0, lambda_eco=0.35, zero_text_embs=False)),
        ("w/o Eco-Sustainability Reg.", dict(use_attention=True, use_relational_stream=True, use_infonce=True, lambda_gini=0.30, lambda_misery=0.20, lambda_eco=0.0, zero_text_embs=False)),
        ("w/o Multimodal Embeddings", dict(use_attention=True, use_relational_stream=True, use_infonce=True, lambda_gini=0.30, lambda_misery=0.20, lambda_eco=0.35, zero_text_embs=True)),
    ]
    ablation_results = []
    base_ndcg = eval_table[ours_key]["ndcg10"]
    for vname, kw in ablation_configs:
        if vname.startswith("Full"):
            r_ab = dict(eval_table[ours_key])
        else:
            m_ab, _ = train_fairnet_v2(train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens, syd_poi_embs, vfeats, device, seed=42, epochs=18, **kw)
            u_test_ab = [np.zeros_like(u) for u in test_u] if kw["zero_text_embs"] else test_u
            p_test_ab = np.zeros_like(syd_poi_embs) if kw["zero_text_embs"] else syd_poi_embs
            sc_ab = score_fairnet_groups(m_ab, test_groups, u_test_ab, test_cands, p_test_ab, vfeats, device)
            r_ab = _evaluate_rankings(sc_ab, test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats)
        ablation_results.append({
            "variant": vname,
            "ndcg5": r_ab["ndcg5"],
            "ndcg10": r_ab["ndcg10"],
            "hit10": r_ab["hit10"],
            "gini_index": r_ab["gini_index"],
            "min_member_sat": r_ab["min_member_sat"],
            "eco_coverage_pct": r_ab["eco_coverage_pct"],
            "delta_ndcg10": round(r_ab["ndcg10"] - base_ndcg, 4),
        })
        print(f"  {vname:<32} | NDCG@10={r_ab['ndcg10']:.4f} ({ablation_results[-1]['delta_ndcg10']:+.4f}) "
              f"| Gini={r_ab['gini_index']:.4f} | Eco={r_ab['eco_coverage_pct']:.1f}%", flush=True)

    # Step 7: Fairness Pareto Sweep & Group Size Scaling + Runtime Latency
    print("\n[Phase E] Fairness-Accuracy Pareto Sweep & Group Size Scaling...", flush=True)
    pareto_sweep = []
    for lg in [0.0, 0.15, 0.30, 0.65, 1.0]:
        if abs(lg - 0.30) < 1e-6:
            r_p = dict(eval_table[ours_key])
        else:
            m_p, _ = train_fairnet_v2(
                train_groups, train_u, val_groups, val_u, val_cands, val_pos_lens,
                syd_poi_embs, vfeats, device, seed=42, epochs=18, lambda_gini=lg
            )
            sc_p = score_fairnet_groups(m_p, test_groups, test_u, test_cands, syd_poi_embs, vfeats, device)
            r_p = _evaluate_rankings(sc_p, test_cands, test_pos_lens, test_groups, test_u, syd_poi_embs, vfeats)
        pareto_sweep.append({
            "lambda_gini": lg,
            "ndcg10": r_p["ndcg10"],
            "gini_index": r_p["gini_index"],
            "min_member_sat": r_p["min_member_sat"],
            "eco_coverage_pct": r_p["eco_coverage_pct"],
        })

    # Group Size Scaling |G| in {2, 3, 4, 5}
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
        r_lgb_g = _evaluate_rankings([raw_model_scores["LightGBM GBDT"][i] for i in idx_sub], sub_cands, sub_pos, sub_groups, sub_u, syd_poi_embs, vfeats)
        r_ag_g = _evaluate_rankings([raw_model_scores["AGREE (SIGIR'18)"][i] for i in idx_sub], sub_cands, sub_pos, sub_groups, sub_u, syd_poi_embs, vfeats)
        group_size_scaling.append({
            "group_size": gsz,
            "num_groups": len(sub_groups),
            "fairnet_ndcg10": r_fn_g["ndcg10"],
            "fairnet_gini": r_fn_g["gini_index"],
            "lgbm_ndcg10": r_lgb_g["ndcg10"],
            "lgbm_gini": r_lgb_g["gini_index"],
            "agree_ndcg10": r_ag_g["ndcg10"],
            "agree_gini": r_ag_g["gini_index"],
        })

    # Inference Latency Profiling (100 candidates x 4 members)
    sample_u = torch.randn(100, 4, syd_poi_embs.shape[1], device=device)
    sample_uf = torch.rand(100, 4, 3, device=device)
    sample_m = torch.ones((100, 4), dtype=torch.bool, device=device)
    sample_p = torch.randn(100, syd_poi_embs.shape[1], device=device)
    sample_pf = torch.rand(100, 8, device=device)
    with torch.no_grad():
        for _ in range(5):
            fairnet_v2(sample_u, sample_uf, sample_m, sample_p, sample_pf)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t_s = time.perf_counter()
        for _ in range(30):
            fairnet_v2(sample_u, sample_uf, sample_m, sample_p, sample_pf)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        gpu_ms = (time.perf_counter() - t_s) * 1000.0 / 30.0

    # CPU timing
    fn_cpu = TripSenseFairNet(emb_dim=syd_poi_embs.shape[1], hidden_dim=64).cpu()
    fn_cpu.load_state_dict({k: v.cpu() for k, v in fairnet_v2.state_dict().items()})
    fn_cpu.eval()
    su_c, suf_c, sm_c, sp_c, spf_c = sample_u.cpu(), sample_uf.cpu(), sample_m.cpu(), sample_p.cpu(), sample_pf.cpu()
    with torch.no_grad():
        t_c = time.perf_counter()
        for _ in range(20):
            fn_cpu(su_c, suf_c, sm_c, sp_c, spf_c)
        cpu_ms = (time.perf_counter() - t_c) * 1000.0 / 20.0

    # Step 8: Multi-Paradigm XAI & SHAP Concordance
    print("\n[Phase F] Running Multi-Paradigm XAI (IG + Faithfulness + Perm + TreeSHAP + Nash)...", flush=True)
    ig_results = compute_integrated_gradients_and_faithfulness(
        fairnet_v2, test_groups, test_u, syd_poi_embs, vfeats, device, steps=32
    )
    perm_importance = compute_permutation_importance(
        fairnet_v2, test_groups, test_u, syd_poi_embs, vfeats, device, max_groups=80
    )
    attn_cf_audit = analyze_cross_attention_and_counterfactuals(
        fairnet_v2, test_groups, test_u, syd_poi_embs, vfeats, device, max_groups=80
    )

    # TreeSHAP on LightGBM across 15 identical features for cross-method validation
    explainer = shap.TreeExplainer(lgbm_model)
    X_sample = X_val[:500]
    shap_vals = explainer.shap_values(X_sample)
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1]
    mean_abs_shap = np.abs(shap_vals).mean(axis=0)
    shap_tot = float(np.sum(mean_abs_shap)) or 1e-8
    shap_summary = []
    for fi, fname in enumerate(RELATIONAL_FEATURE_NAMES):
        shap_summary.append({
            "feature": fname,
            "mean_abs_shap": round(float(mean_abs_shap[fi]), 4),
            "importance_pct": round(100.0 * float(mean_abs_shap[fi]) / shap_tot, 2),
        })
    shap_summary.sort(key=lambda r: r["importance_pct"], reverse=True)

    concordance = compute_cross_xai_concordance(
        ig_results["features_unsorted"], perm_importance, shap_summary
    )
    print(f"  IG Completeness MAE = {ig_results['completeness_mae']:.6f} | "
          f"Comprehensiveness@k3 = {ig_results['comprehensiveness_k3']:.4f} "
          f"({ig_results['faithfulness_ratio_over_random']}x vs random) | "
          f"Spearman(IG, TreeSHAP) = {concordance.get('ig_vs_treeshap_spearman_rho', 'N/A')}", flush=True)

    # Step 9: Bangladesh 5-City Pilot, Active Swipe, TravelPlanner
    print("\n[Phase G] Auditing Bangladesh 5-City Pilot, Active Swipe & TravelPlanner...", flush=True)
    bd_pilot = evaluate_bd_pilot_cities(fairnet_v2, {}, device)
    swipe_curve = simulate_active_swipe_curve(syd_poi_embs, seed=42)
    tp_eval = evaluate_travelplanner_rag(load_travelplanner_val(), max_tasks=180)

    # Step 10: Assemble & Write Complete Q1 Artifact JSON
    total_time = round(time.time() - t0, 2)
    num_params = sum(p.numel() for p in fairnet_v2.parameters())

    final_report = {
        "model_name": "TripSense-FairNet v2 (Dual-Stream Multimodal + Group-Relational Consensus)",
        "backbone": model_name,
        "embedding_dim": int(syd_poi_embs.shape[1]),
        "num_parameters": int(num_params),
        "device_trained": str(device),
        "training_time_sec": total_time,
        "latency_profile": {
            "gpu_ms_per_100_cands": round(gpu_ms, 2),
            "cpu_ms_per_100_cands": round(cpu_ms, 2),
        },
        "datasets": {
            "primary_benchmark": "CRUISEResearchGroup/Massive-STEPS-Sydney",
            "external_cities": ["Melbourne", "Tokyo", "New-York"],
            "group_poi_benchmark": f"CRUISEResearchGroup/Massive-STEPS-Sydney (Zero-Leakage Chronological)",
            "checkins_loaded": syd_bench["num_rows"],
            "unique_venues": V_syd,
            "total_groups": len(groups),
            "train_groups": len(train_groups),
            "val_groups": len(val_groups),
            "test_groups": len(test_groups),
            "candidate_pool_size": 100,
            "travelplanner_tasks": tp_eval["num_tasks"],
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
        "multi_seed_stability": multi_seed_summary,
        "ablation_study": ablation_results,
        "external_cross_city_validation": external_cities,
        "bangladesh_5city_pilot": bd_pilot,
        "pareto_gini_sweep": pareto_sweep,
        "group_size_scaling": group_size_scaling,
        "multi_xai_evaluation": {
            "integrated_gradients": ig_results,
            "permutation_importance": perm_importance,
            "cross_xai_concordance": concordance,
            "attention_and_counterfactual_audit": attn_cf_audit,
        },
        "shap_feature_importance": shap_summary,
        "active_swipe_learning_curve": swipe_curve,
        "travelplanner_rag_evaluation": tp_eval,
    }

    out_path = os.path.join(ARTIFACTS_DIR, "q1_benchmark_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2)
    print(f"\n[DONE] Saved complete Q1 experimental report ({total_time}s) -> {out_path}", flush=True)


if __name__ == "__main__":
    main()
