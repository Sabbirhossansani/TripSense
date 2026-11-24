"""
End-to-End Training, Ablation & Q1 Journal Benchmarking Script for TripSense Blueprint B.

Executes:
  1. Loads real CRUISEResearchGroup/Massive-STEPS-Sydney (29.9k POI check-ins) & osunlp/TravelPlanner.
  2. Encodes POIs & Swipe Deck with SOTA google/siglip-base-patch16-224 on RTX 3050 GPU.
  3. Trains:
       - TripSense-FairNet (Full: Cross-Attention + Fairness-Regularized BPR Loss)
       - FairNet-NoFairness (Ablation: BPR-only without fairness/misery/eco penalties)
       - LightGBM GBDT Ranker Baseline + SHAP TreeExplainer global feature attributions
  4. Evaluates 6 approaches across held-out test groups:
       Popularity | Average Heuristic | Least-Misery Heuristic | LightGBM | FairNet (Ablation) | TripSense-FairNet (Ours)
     with statistical significance via Wilcoxon signed-rank test.
  5. Benchmarks Active Bayesian Swipe vs. Random Swipe across 120 held-out users.
  6. Evaluates Neuro-Symbolic RAG + Verifier vs. Vanilla LLM on osunlp/TravelPlanner.
  7. Saves trained weights (fairnet_best.pt, lgbm_ranker.pkl) & q1_benchmark_results.json.
"""

import os
import sys
import json
import time
import pickle
from typing import Optional
import numpy as np
import torch
from scipy.stats import wilcoxon
from sklearn.metrics import ndcg_score
import lightgbm as lgb
import shap

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.ml.dataset_loader import (
    load_massive_steps_sydney,
    load_travelplanner_val,
    build_sydney_group_benchmark,
    CACHE_DIR,
)
from backend.ml.backbone import SigLIPBackbone, encode_and_save_tripsense_artifacts, ARTIFACTS_DIR
from backend.ml.fairnet import TripSenseFairNet, fairness_regularized_bpr_loss
from backend.ml.active_swipe import benchmark_active_vs_random_swipe
from backend.ml.eval_travelplanner import evaluate_travelplanner_rag


def compute_gini(values: list) -> float:
    arr = sorted(max(0.0, float(v)) for v in values)
    n = len(arr)
    if n <= 1 or sum(arr) <= 1e-8:
        return 0.0
    numer = sum((2 * (i + 1) - n - 1) * arr[i] for i in range(n))
    return float(numer / (n * sum(arr)))


def build_group_tensors(
    groups: list,
    venue_embs: np.ndarray,
    venue_features: np.ndarray,
    max_members: int = 4,
):
    emb_dim = venue_embs.shape[1]
    u_embs_list, u_feats_list, u_masks_list, pos_list = [], [], [], []
    valid_groups = []

    for g in groups:
        hist_vecs = []
        budgets = g["member_budgets"]
        for m_idx, m in enumerate(g["members"][:max_members]):
            seq = g["member_histories"][m]
            v = venue_embs[seq].mean(axis=0)
            v /= np.linalg.norm(v) + 1e-8
            hist_vecs.append(v)

        M = len(hist_vecs)
        if M == 0 or not g["pos_targets"]:
            continue

        u_e = np.zeros((max_members, emb_dim), dtype=np.float32)
        u_f = np.zeros((max_members, 3), dtype=np.float32)
        u_m = np.zeros((max_members,), dtype=bool)
        for i in range(M):
            u_e[i] = hist_vecs[i]
            b_val = budgets[i]
            n_hist = min(1.0, len(g["member_histories"][g["members"][i]]) / 10.0)
            u_f[i] = [b_val, n_hist, 0.65 if b_val > 0.3 else 0.45]
            u_m[i] = True

        u_embs_list.append(u_e)
        u_feats_list.append(u_f)
        u_masks_list.append(u_m)
        pos_list.append(g["pos_targets"])
        valid_groups.append(g)

    return (
        np.stack(u_embs_list),
        np.stack(u_feats_list),
        np.stack(u_masks_list),
        pos_list,
        valid_groups,
    )


def train_pytorch_fairnet(
    train_data: tuple,
    val_data: tuple,
    venue_embs: np.ndarray,
    venue_features: np.ndarray,
    device: torch.device,
    popularity: Optional[np.ndarray] = None,
    fairness_weight: float = 0.35,
    misery_weight: float = 0.30,
    eco_weight: float = 0.10,
    epochs: int = 28,
    batch_size: int = 64,
    seed: int = 42,
):
    torch.manual_seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)

    u_embs_tr, u_feats_tr, u_masks_tr, pos_tr, _ = train_data
    u_embs_va, u_feats_va, u_masks_va, pos_va, _ = val_data

    emb_dim = venue_embs.shape[1]
    n_venues = len(venue_embs)
    top_pop_ids = np.argsort(-popularity)[: min(250, n_venues)] if popularity is not None else None
    v_emb_t = torch.from_numpy(venue_embs).to(device)
    v_feat_t = torch.from_numpy(venue_features).to(device)

    model = TripSenseFairNet(
        emb_dim=emb_dim,
        poi_feat_dim=8,
        user_feat_dim=3,
        hidden_dim=128,
        num_heads=4,
        dropout=0.15,
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=8e-4, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    # Flatten (group_idx, pos_venue_idx) pairs for training
    train_pairs = [(gi, pid) for gi, plist in enumerate(pos_tr) for pid in plist]
    n_train = len(train_pairs)

    history_losses = []
    best_val_score = -1.0
    best_state = None

    for ep in range(1, epochs + 1):
        model.train()
        rng.shuffle(train_pairs)
        ep_loss = 0.0
        steps = 0

        for start in range(0, n_train, batch_size):
            batch = train_pairs[start : start + batch_size]
            g_ids = [b[0] for b in batch]
            p_ids = np.array([b[1] for b in batch], dtype=np.int64)
            # Mix 50% hard popularity negatives and 50% random negatives
            neg_ids = []
            for gi in g_ids:
                pset = set(pos_tr[gi])
                if top_pop_ids is not None and rng.random() < 0.5:
                    nid = int(rng.choice(top_pop_ids))
                    while nid in pset:
                        nid = int(rng.choice(top_pop_ids))
                else:
                    nid = int(rng.integers(0, n_venues))
                    while nid in pset:
                        nid = int(rng.integers(0, n_venues))
                neg_ids.append(nid)
            neg_ids = np.array(neg_ids, dtype=np.int64)

            ue = torch.from_numpy(u_embs_tr[g_ids]).to(device)
            uf = torch.from_numpy(u_feats_tr[g_ids]).to(device)
            um = torch.from_numpy(u_masks_tr[g_ids]).to(device)
            pe_pos = v_emb_t[p_ids]
            pf_pos = v_feat_t[p_ids]
            pe_neg = v_emb_t[neg_ids]
            pf_neg = v_feat_t[neg_ids]

            pos_g, pos_m, _ = model(ue, uf, um, pe_pos, pf_pos)
            neg_g, _, _ = model(ue, uf, um, pe_neg, pf_neg)

            loss, _ = fairness_regularized_bpr_loss(
                pos_g,
                pos_m,
                neg_g,
                um,
                pf_pos[:, 6],  # eco_score feature
                fairness_weight=fairness_weight,
                misery_weight=misery_weight,
                eco_weight=eco_weight,
            )

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 2.0)
            optimizer.step()

            ep_loss += float(loss.item())
            steps += 1

        scheduler.step()
        avg_loss = ep_loss / max(1, steps)
        history_losses.append(round(avg_loss, 4))

        # Validation Hit@10 check every 4 epochs (chunked to keep RTX 3050 fast)
        if ep % 4 == 0 or ep == epochs:
            model.eval()
            with torch.no_grad():
                hits = []
                for gi in range(len(pos_va)):
                    gt = set(pos_va[gi])
                    ue_base = torch.from_numpy(u_embs_va[gi : gi + 1]).to(device)
                    uf_base = torch.from_numpy(u_feats_va[gi : gi + 1]).to(device)
                    um_base = torch.from_numpy(u_masks_va[gi : gi + 1]).to(device)
                    chunk_scores = []
                    for v_start in range(0, n_venues, 512):
                        v_end = min(n_venues, v_start + 512)
                        cs = v_end - v_start
                        g_sc, _, _ = model(
                            ue_base.expand(cs, -1, -1),
                            uf_base.expand(cs, -1, -1),
                            um_base.expand(cs, -1),
                            v_emb_t[v_start:v_end],
                            v_feat_t[v_start:v_end],
                        )
                        chunk_scores.append(g_sc)
                    all_sc = torch.cat(chunk_scores, dim=0)
                    top10 = set(torch.topk(all_sc, k=min(10, n_venues)).indices.cpu().tolist())
                    hits.append(1.0 if (gt & top10) else 0.0)
                val_hit = float(np.mean(hits)) if hits else 0.0
                print(f"  [Epoch {ep:02d}/{epochs}] loss={avg_loss:.4f} val_hit@10={val_hit:.4f}", flush=True)
                if val_hit >= best_val_score:
                    best_val_score = val_hit
                    best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict({k: v.to(device) for k, v in best_state.items()})
    model.eval()
    return model, history_losses, round(best_val_score, 4)


def build_tabular_pair_features(u_embs, u_feats, u_masks, g_idx, v_ids, venue_embs, venue_features):
    """Creates 12 tabular engineered features for LightGBM + SHAP comparison."""
    ue = u_embs[g_idx]  # (M, D)
    uf = u_feats[g_idx]  # (M, 3)
    um = u_masks[g_idx]  # (M,)
    valid_ue = ue[um]  # (k, D)
    valid_uf = uf[um]  # (k, 3)

    v_emb = venue_embs[v_ids]  # (K, D)
    v_feat = venue_features[v_ids]  # (K, 8)
    sims = v_emb @ valid_ue.T  # (K, k)

    mean_sim = sims.mean(axis=1, keepdims=True)
    min_sim = sims.min(axis=1, keepdims=True)
    max_sim = sims.max(axis=1, keepdims=True)
    budget_gap = np.abs(v_feat[:, 1:2] - valid_uf[:, 0].mean())

    return np.hstack([mean_sim, min_sim, max_sim, budget_gap, v_feat]).astype(np.float32)


def evaluate_all_models(
    test_data: tuple,
    venue_embs: np.ndarray,
    venue_features: np.ndarray,
    popularity: np.ndarray,
    fairnet_full: TripSenseFairNet,
    fairnet_nofair: TripSenseFairNet,
    lgbm_model,
    device: torch.device,
):
    u_embs_te, u_feats_te, u_masks_te, pos_te, _ = test_data
    n_venues = len(venue_embs)
    v_emb_t = torch.from_numpy(venue_embs).to(device)
    v_feat_t = torch.from_numpy(venue_features).to(device)

    pop_norm = popularity / max(1.0, float(popularity.max()))

    model_names = [
        "Popularity",
        "Average Cosine",
        "Least-Misery",
        "LightGBM GBDT",
        "FairNet (w/o Fairness)",
        "TripSense-FairNet (Ours)",
    ]
    per_group_metrics = {
        m: {"ndcg5": [], "ndcg10": [], "hit10": [], "gini": [], "min_sat": [], "eco_cov": []}
        for m in model_names
    }

    for gi in range(len(pos_te)):
        gt_set = set(pos_te[gi])
        valid_m = u_masks_te[gi]
        valid_ue = u_embs_te[gi][valid_m]  # (k, D)

        # Grounded latent satisfaction of each member across all venues
        # (normalized cosine affinity + quality)
        member_true_utils = np.clip(0.55 + 0.45 * (venue_embs @ valid_ue.T), 0.05, 0.99)  # (V, k)

        # 1. Popularity
        sc_pop = pop_norm

        # 2. Average Cosine
        sc_avg = member_true_utils.mean(axis=1)

        # 3. Least-Misery
        sc_lm = member_true_utils.min(axis=1)

        # 4. LightGBM
        all_vids = np.arange(n_venues)
        x_lgb = build_tabular_pair_features(u_embs_te, u_feats_te, u_masks_te, gi, all_vids, venue_embs, venue_features)
        sc_lgb = lgbm_model.predict_proba(x_lgb)[:, 1]

        # 5 & 6. PyTorch FairNet variants (chunked to keep VRAM low and inference fast)
        with torch.no_grad():
            ue_b = torch.from_numpy(u_embs_te[gi : gi + 1]).to(device)
            uf_b = torch.from_numpy(u_feats_te[gi : gi + 1]).to(device)
            um_b = torch.from_numpy(u_masks_te[gi : gi + 1]).to(device)
            nf_parts, fl_parts = [], []
            for v_start in range(0, n_venues, 512):
                v_end = min(n_venues, v_start + 512)
                cs = v_end - v_start
                nf_parts.append(fairnet_nofair(ue_b.expand(cs, -1, -1), uf_b.expand(cs, -1, -1), um_b.expand(cs, -1), v_emb_t[v_start:v_end], v_feat_t[v_start:v_end])[0].cpu().numpy())
                fl_parts.append(fairnet_full(ue_b.expand(cs, -1, -1), uf_b.expand(cs, -1, -1), um_b.expand(cs, -1), v_emb_t[v_start:v_end], v_feat_t[v_start:v_end])[0].cpu().numpy())
            sc_nofair = np.concatenate(nf_parts, axis=0)
            sc_full = np.concatenate(fl_parts, axis=0)

        y_true = np.array([[1.0 if v in gt_set else 0.0 for v in range(n_venues)]])

        for name, scores in [
            ("Popularity", sc_pop),
            ("Average Cosine", sc_avg),
            ("Least-Misery", sc_lm),
            ("LightGBM GBDT", sc_lgb),
            ("FairNet (w/o Fairness)", sc_nofair),
            ("TripSense-FairNet (Ours)", sc_full),
        ]:
            ranked = np.argsort(-scores)
            top10 = ranked[:10]

            n5 = float(ndcg_score(y_true, [scores], k=5))
            n10 = float(ndcg_score(y_true, [scores], k=10))
            h10 = 1.0 if (set(top10.tolist()) & gt_set) else 0.0

            # Member average utility over top-10 recommended POIs
            top10_member_means = member_true_utils[top10].mean(axis=0).tolist()
            gini = compute_gini(top10_member_means)
            min_sat = float(min(top10_member_means)) * 100.0
            # Eco + Hidden Gem coverage among top-10
            eco_cov = float(venue_features[top10, 6].mean()) * 100.0

            per_group_metrics[name]["ndcg5"].append(n5)
            per_group_metrics[name]["ndcg10"].append(n10)
            per_group_metrics[name]["hit10"].append(h10)
            per_group_metrics[name]["gini"].append(gini)
            per_group_metrics[name]["min_sat"].append(min_sat)
            per_group_metrics[name]["eco_cov"].append(eco_cov)

    summary = {}
    ours_ndcg10 = per_group_metrics["TripSense-FairNet (Ours)"]["ndcg10"]
    ours_gini = per_group_metrics["TripSense-FairNet (Ours)"]["gini"]

    for name in model_names:
        d = per_group_metrics[name]
        row = {
            "ndcg5": round(float(np.mean(d["ndcg5"])), 4),
            "ndcg10": round(float(np.mean(d["ndcg10"])), 4),
            "hit10": round(float(np.mean(d["hit10"]) * 100), 2),
            "gini_index": round(float(np.mean(d["gini"])), 4),
            "min_member_sat": round(float(np.mean(d["min_sat"])), 2),
            "eco_coverage_pct": round(float(np.mean(d["eco_cov"])), 2),
        }
        if name != "TripSense-FairNet (Ours)":
            try:
                _, p_ndcg = wilcoxon(ours_ndcg10, d["ndcg10"])
                _, p_gini = wilcoxon(ours_gini, d["gini"])
                row["p_value_ndcg10"] = round(float(p_ndcg), 6)
                row["p_value_gini"] = round(float(p_gini), 6)
            except Exception:
                row["p_value_ndcg10"] = None
                row["p_value_gini"] = None
        summary[name] = row

    return summary


def main():
    t_start = time.perf_counter()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"=== TripSense Blueprint B Q1 Training Pipeline (device={device}) ===")

    # 1. Load Real Datasets from Hugging Face
    sydney_df = load_massive_steps_sydney()
    tp_df = load_travelplanner_val()
    bench = build_sydney_group_benchmark(sydney_df, seed=42, n_groups=850)

    # 2. Load Pretrained SigLIP Backbone & Encode POIs
    backbone = SigLIPBackbone(device=str(device))
    backbone_name, _, _ = encode_and_save_tripsense_artifacts(backbone)

    steps_emb_cache = os.path.join(CACHE_DIR, "steps_poi_emb.npy")
    if os.path.exists(steps_emb_cache):
        venue_embs = np.load(steps_emb_cache)
        if len(venue_embs) != len(bench["venue_texts"]) or venue_embs.shape[1] != backbone.emb_dim:
            venue_embs = backbone.encode_texts(bench["venue_texts"], batch_size=64)
            np.save(steps_emb_cache, venue_embs)
    else:
        venue_embs = backbone.encode_texts(bench["venue_texts"], batch_size=64)
        np.save(steps_emb_cache, venue_embs)

    print(f"[Pipeline] Massive-STEPS Venues={len(venue_embs)}, Train Groups={len(bench['train_groups'])}, Val={len(bench['val_groups'])}, Test={len(bench['test_groups'])}")

    train_data = build_group_tensors(bench["train_groups"], venue_embs, bench["venue_features"])
    val_data = build_group_tensors(bench["val_groups"], venue_embs, bench["venue_features"])
    test_data = build_group_tensors(bench["test_groups"], venue_embs, bench["venue_features"])

    # 3. Train TripSense-FairNet (Full) & Ablation (w/o Fairness Loss)
    print("[Pipeline] Training TripSense-FairNet (Full Multi-Objective Model)...", flush=True)
    fairnet_full, loss_curve_full, val_hit_full = train_pytorch_fairnet(
        train_data, val_data, venue_embs, bench["venue_features"], device,
        popularity=bench["popularity"],
        fairness_weight=0.35, misery_weight=0.30, eco_weight=0.10, epochs=20, seed=42
    )

    print("[Pipeline] Training FairNet Ablation (w/o Fairness Loss)...", flush=True)
    fairnet_nofair, _, val_hit_nofair = train_pytorch_fairnet(
        train_data, val_data, venue_embs, bench["venue_features"], device,
        popularity=bench["popularity"],
        fairness_weight=0.0, misery_weight=0.0, eco_weight=0.0, epochs=20, seed=42
    )

    # Save best FairNet checkpoint
    ckpt_path = os.path.join(ARTIFACTS_DIR, "fairnet_best.pt")
    torch.save({
        "model_state_dict": {k: v.cpu() for k, v in fairnet_full.state_dict().items()},
        "config": {
            "emb_dim": backbone.emb_dim,
            "poi_feat_dim": 8,
            "user_feat_dim": 3,
            "hidden_dim": 128,
            "num_heads": 4,
            "backbone": backbone_name,
        },
        "loss_curve": loss_curve_full,
    }, ckpt_path)
    print(f"[Pipeline] Saved FairNet weights -> {ckpt_path}")

    # 4. Train LightGBM Ranker + SHAP Explainability Feature Attribution
    print("[Pipeline] Training LightGBM GBDT Baseline & Computing SHAP values...")
    rng = np.random.default_rng(42)
    u_embs_tr, u_feats_tr, u_masks_tr, pos_tr, _ = train_data
    n_venues = len(venue_embs)
    X_rows, y_rows = [], []
    for gi, plist in enumerate(pos_tr):
        pset = set(plist)
        negs = [int(rng.integers(0, n_venues)) for _ in range(len(plist) * 2)]
        negs = [n for n in negs if n not in pset][:len(plist) * 2]
        v_ids = np.array(plist + negs, dtype=np.int64)
        feats = build_tabular_pair_features(u_embs_tr, u_feats_tr, u_masks_tr, gi, v_ids, venue_embs, bench["venue_features"])
        X_rows.append(feats)
        y_rows.extend([1] * len(plist) + [0] * len(negs))

    X_tr = np.vstack(X_rows)
    y_tr = np.array(y_rows, dtype=np.int32)
    lgbm_model = lgb.LGBMClassifier(n_estimators=140, learning_rate=0.06, max_depth=6, random_state=42, verbose=-1)
    lgbm_model.fit(X_tr, y_tr)

    lgb_path = os.path.join(ARTIFACTS_DIR, "lgbm_ranker.pkl")
    with open(lgb_path, "wb") as f:
        pickle.dump(lgbm_model, f)

    feat_names = [
        "Mean Taste Similarity",
        "Min Member Similarity",
        "Max Member Similarity",
        "Budget Gap",
        "Spatial Distance",
        "Ticket Cost",
        "Crowd Congestion",
        "Quality Rating",
        "Indoor Shelter",
        "Hidden Gem Flag",
        "Eco Sustainability",
        "Local SME Revenue",
    ]
    explainer = shap.TreeExplainer(lgbm_model)
    shap_sample = X_tr[:min(500, len(X_tr))]
    shap_vals = explainer.shap_values(shap_sample)
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1]
    mean_abs_shap = np.abs(shap_vals).mean(axis=0)
    shap_total = float(mean_abs_shap.sum()) or 1.0
    shap_importances = sorted(
        [
            {"feature": fn, "importance_pct": round(float(val / shap_total * 100), 2)}
            for fn, val in zip(feat_names, mean_abs_shap)
        ],
        key=lambda x: x["importance_pct"],
        reverse=True,
    )

    # 5. Evaluate All 6 Models on Held-Out Test Groups
    print("[Pipeline] Running Q1 Test Benchmark & Wilcoxon Significance Tests...")
    group_comparison = evaluate_all_models(
        test_data, venue_embs, bench["venue_features"], bench["popularity"],
        fairnet_full, fairnet_nofair, lgbm_model, device
    )

    # 6. Benchmark Active Bayesian Swipe vs Random Quiz
    print("[Pipeline] Running Active Bayesian Swipe Curve Benchmark...")
    active_swipe_curve = benchmark_active_vs_random_swipe(venue_embs, bench["user_to_venues"], seed=42, n_eval_users=120)

    # 7. Evaluate Neuro-Symbolic RAG vs Published LLM Baseline on osunlp/TravelPlanner
    print("[Pipeline] Running osunlp/TravelPlanner Hallucination & Feasibility Benchmark...")
    travelplanner_eval = evaluate_travelplanner_rag(tp_df, max_tasks=180)

    elapsed = round(time.perf_counter() - t_start, 2)
    results = {
        "model_name": "TripSense-FairNet",
        "backbone": backbone_name,
        "embedding_dim": backbone.emb_dim,
        "device_trained": str(device) + (f" ({torch.cuda.get_device_name(0)})" if torch.cuda.is_available() else ""),
        "training_time_sec": elapsed,
        "datasets": {
            "group_poi_benchmark": "CRUISEResearchGroup/Massive-STEPS-Sydney",
            "total_checkins_loaded": len(sydney_df),
            "unique_venues": len(venue_embs),
            "train_groups": len(train_data[3]),
            "val_groups": len(val_data[3]),
            "test_groups": len(test_data[3]),
            "rag_benchmark": "osunlp/TravelPlanner (validation)",
        },
        "fairnet_training": {
            "epochs": len(loss_curve_full),
            "initial_loss": loss_curve_full[0],
            "final_loss": loss_curve_full[-1],
            "loss_curve": loss_curve_full,
            "best_val_hit10": val_hit_full,
            "ablation_nofair_val_hit10": val_hit_nofair,
            "total_parameters": int(sum(p.numel() for p in fairnet_full.parameters())),
        },
        "group_consensus_comparison": group_comparison,
        "shap_feature_importance": shap_importances,
        "active_swipe_learning_curve": active_swipe_curve,
        "travelplanner_rag_evaluation": travelplanner_eval,
    }

    out_json = os.path.join(ARTIFACTS_DIR, "q1_benchmark_results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n=== COMPLETED IN {elapsed}s! Results saved to {out_json} ===")
    print(json.dumps(group_comparison, indent=2))
    print("Active Swipe Curve:", active_swipe_curve)
    print("TravelPlanner RAG Eval:", travelplanner_eval)


if __name__ == "__main__":
    main()
