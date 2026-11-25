"""
Multi-Paradigm Explainable AI (XAI) & Faithfulness Verification Suite for TripSense-FairNet v2.

Produces Q1-grade explainability metrics across 4 complementary paradigms:
  1. Integrated Gradients (Sundararajan et al., ICML 2017) over the 15-dim semantic-relational
     manifold + exact Axiom 1 Completeness check + Perturbation Faithfulness (Comprehensiveness,
     Sufficiency, and AOPC across top-k feature masking, DeYoung et al., ACL 2020).
  2. Permutation Feature Importance directly measured by NDCG@10 drop on held-out test groups.
  3. Cross-XAI Method Concordance: Spearman rho and Kendall tau between Integrated Gradients,
     Permutation Importance, and TreeSHAP.
  4. Cross-Attention Member Influence & Nash Counterfactual Recourse Audit.
"""

import numpy as np
import torch
from typing import Dict, Any, List
from scipy.stats import spearmanr, kendalltau
from backend.ml.fairnet import TripSenseFairNet, extract_group_relational_features

RELATIONAL_FEATURE_NAMES: List[str] = [
    "Mean Semantic Alignment",
    "Min Member Alignment",
    "Max Member Alignment",
    "Preference Dispersion (Std)",
    "Mean Budget Gap",
    "Worst Budget Hardship",
    "Normalized Group Size",
    "Distance Centrality",
    "Venue Price Tier",
    "Venue Popularity",
    "Community Rating",
    "Indoor Shelter Flag",
    "Hidden Gem Flag",
    "Eco-Sustainability Score",
    "Local SME Revenue Share",
]


def _gini(arr: np.ndarray) -> float:
    x = np.sort(np.maximum(0.0, arr.astype(np.float64)))
    n = len(x)
    if n <= 1 or np.sum(x) <= 1e-9:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2.0 * np.sum(idx * x) / (n * np.sum(x))) - (n + 1.0) / n)


def _ndcg_at_k(scores: np.ndarray, pos_set: set, k: int = 10) -> float:
    order = np.argsort(-scores)[:k]
    dcg = 0.0
    for r, idx in enumerate(order):
        if int(idx) in pos_set:
            dcg += 1.0 / np.log2(r + 2.0)
    idcg = sum(1.0 / np.log2(r + 2.0) for r in range(min(k, len(pos_set))))
    return dcg / max(1e-9, idcg)


@torch.no_grad()
def _build_test_relational_samples(
    model: TripSenseFairNet,
    test_groups: List[Dict[str, Any]],
    user_embs_list: List[np.ndarray],
    poi_embs: np.ndarray,
    venue_feats: np.ndarray,
    device: torch.device,
    max_groups: int = 120,
    seed: int = 42,
):
    rng = np.random.RandomState(seed)
    all_vecs = []
    all_raw = []
    all_groups_data = []

    sample_groups = test_groups[:max_groups]
    for g_idx, g in enumerate(sample_groups):
        ue = user_embs_list[g_idx]  # (M, D)
        uf = np.array(g["user_features"], dtype=np.float32)  # (M, 3)
        M = ue.shape[0]
        pos = g["pos_targets"][0]
        negs = []
        pos_set = set(g["pos_targets"])
        while len(negs) < 3:
            c = int(rng.randint(poi_embs.shape[0]))
            if c not in pos_set:
                negs.append(c)

        cand_ids = [pos] + negs
        C = len(cand_ids)
        u_t = torch.from_numpy(ue).unsqueeze(0).expand(C, M, -1).to(device)
        uf_t = torch.from_numpy(uf).unsqueeze(0).expand(C, M, -1).to(device)
        m_t = torch.ones((C, M), dtype=torch.bool, device=device)
        p_t = torch.from_numpy(poi_embs[cand_ids]).to(device)
        pf_t = torch.from_numpy(venue_feats[cand_ids]).to(device)

        rel_vec, _, _ = extract_group_relational_features(u_t, uf_t, m_t, p_t, pf_t)
        all_vecs.append(rel_vec[0].cpu().numpy())  # positive item
        all_vecs.append(rel_vec[1].cpu().numpy())  # negative item

        all_raw.append((u_t[0], uf_t[0], m_t[0], p_t[0], pf_t[0]))
        all_groups_data.append((g, ue, uf))

    return np.stack(all_vecs, axis=0), all_groups_data


def compute_integrated_gradients_and_faithfulness(
    model: TripSenseFairNet,
    test_groups: List[Dict[str, Any]],
    user_embs_list: List[np.ndarray],
    poi_embs: np.ndarray,
    venue_feats: np.ndarray,
    device: torch.device,
    steps: int = 32,
) -> Dict[str, Any]:
    """
    Computes 32-step Integrated Gradients on FairNet v2's relational decision head,
    verifies Axiom 1 Completeness, and evaluates Perturbation Faithfulness
    (Comprehensiveness, Sufficiency, and AOPC).
    """
    model.eval()
    rel_np, _ = _build_test_relational_samples(
        model, test_groups, user_embs_list, poi_embs, venue_feats, device, max_groups=120
    )
    x = torch.from_numpy(rel_np).float().to(device)  # (N, 15)
    # Neutral baseline x0 = feature-wise sample mean across candidate pool (standard baseline IG)
    x0 = x.mean(dim=0, keepdim=True).expand_as(x).clone()

    # Smooth Riemann approximation from x0 -> x
    alphas = torch.linspace(0.0, 1.0, steps + 1, device=device)
    total_grads = torch.zeros_like(x)
    delta = x - x0

    for a in alphas[:-1]:
        x_step = (x0 + (a + 0.5 / steps) * delta).detach().requires_grad_(True)
        out = model.score_relational_head(x_step).sum()
        model.zero_grad(set_to_none=True)
        out.backward()
        total_grads += x_step.grad.detach()

    avg_grads = total_grads / float(steps)
    ig = (delta * avg_grads).detach()  # (N, 15)

    with torch.no_grad():
        fx = torch.sigmoid(model.score_relational_head(x))
        fx_logit = model.score_relational_head(x)
        fx0_logit = model.score_relational_head(x0)
        completeness_err = torch.abs(ig.sum(dim=-1) - (fx_logit - fx0_logit))

        # Mean absolute IG normalized to percentage
        abs_ig = ig.abs().mean(dim=0).cpu().numpy()
        signed_ig = ig.mean(dim=0).cpu().numpy()
        # Positive-sample directional effect (pos items are even indices)
        pos_signed = ig[0::2].mean(dim=0).cpu().numpy()
        norm_pct = 100.0 * abs_ig / max(1e-8, float(np.sum(abs_ig)))

        # Faithfulness Perturbation Tests (positive items x_pos = x[0::2])
        x_pos = x[0::2]
        x0_pos = x0[0::2]
        ig_pos = ig[0::2].abs()
        fx_pos = torch.sigmoid(model.score_relational_head(x_pos))

        aopc_drops = []
        comp_by_k = {}
        suff_by_k = {}
        rank_order = torch.argsort(ig_pos, dim=-1, descending=True)

        for k in [1, 3, 5, 7]:
            top_idx = rank_order[:, :k]
            mask_top = torch.zeros_like(x_pos, dtype=torch.bool)
            mask_top.scatter_(1, top_idx, True)

            # Comprehensiveness: remove top-k important features -> predict drop
            x_comp = torch.where(mask_top, x0_pos, x_pos)
            prob_comp = torch.sigmoid(model.score_relational_head(x_comp))
            comp = float((fx_pos - prob_comp).mean().item())
            comp_by_k[f"k{k}"] = round(comp, 4)
            aopc_drops.append(comp)

            # Sufficiency: keep ONLY top-k features -> small change = high sufficiency
            x_suff = torch.where(mask_top, x_pos, x0_pos)
            prob_suff = torch.sigmoid(model.score_relational_head(x_suff))
            suff_gap = float(torch.abs(fx_pos - prob_suff).mean().item())
            suff_by_k[f"k{k}"] = round(suff_gap, 4)

        # Random baseline masking at k=3 for contrast
        rng_mask = torch.zeros_like(x_pos, dtype=torch.bool)
        for row_i in range(x_pos.size(0)):
            perm = torch.randperm(x_pos.size(1), device=device)[:3]
            rng_mask[row_i, perm] = True
        prob_rand = torch.sigmoid(model.score_relational_head(torch.where(rng_mask, x0_pos, x_pos)))
        rand_comp_k3 = float((fx_pos - prob_rand).mean().item())

    features_ranked = []
    for i, name in enumerate(RELATIONAL_FEATURE_NAMES):
        features_ranked.append({
            "feature": name,
            "mean_abs_ig": round(float(abs_ig[i]), 5),
            "importance_pct": round(float(norm_pct[i]), 2),
            "mean_signed_ig": round(float(pos_signed[i]), 5),
            "direction": "Positive (+)" if pos_signed[i] >= 0 else "Penalty (-)",
        })
    features_ranked_sorted = sorted(features_ranked, key=lambda r: r["mean_abs_ig"], reverse=True)

    return {
        "steps": steps,
        "num_explained_instances": int(x.size(0)),
        "completeness_mae": round(float(completeness_err.mean().item()), 6),
        "completeness_max": round(float(completeness_err.max().item()), 6),
        "comprehensiveness_k3": comp_by_k["k3"],
        "sufficiency_gap_k3": suff_by_k["k3"],
        "random_baseline_comp_k3": round(rand_comp_k3, 4),
        "faithfulness_ratio_over_random": round(comp_by_k["k3"] / max(1e-4, abs(rand_comp_k3)), 2),
        "aopc_score": round(float(np.mean(aopc_drops)), 4),
        "comprehensiveness_curve": comp_by_k,
        "sufficiency_curve": suff_by_k,
        "features_unsorted": features_ranked,
        "features_ranked": features_ranked_sorted,
    }


@torch.no_grad()
def compute_permutation_importance(
    model: TripSenseFairNet,
    test_groups: List[Dict[str, Any]],
    user_embs_list: List[np.ndarray],
    poi_embs: np.ndarray,
    venue_feats: np.ndarray,
    device: torch.device,
    max_groups: int = 80,
    num_negs: int = 49,
    seed: int = 123,
) -> List[Dict[str, Any]]:
    """
    Model-agnostic permutation importance measuring real NDCG@10 degradation
    when each relational/semantic feature is shuffled across candidates.
    """
    model.eval()
    rng = np.random.RandomState(seed)
    V = poi_embs.shape[0]
    subset = test_groups[:max_groups]

    # Precompute candidate pools and baseline relational vectors
    cand_rel_vecs = []
    cand_pos_sets = []
    base_ndcgs = []

    for g_idx, g in enumerate(subset):
        ue = user_embs_list[g_idx]
        uf = np.array(g["user_features"], dtype=np.float32)
        M = ue.shape[0]
        pos_list = g["pos_targets"]
        pos_set = set(pos_list)
        negs = []
        while len(negs) < num_negs:
            c = int(rng.randint(V))
            if c not in pos_set:
                negs.append(c)
        cands = list(pos_list) + negs
        rel_pos_set = set(range(len(pos_list)))
        C = len(cands)

        u_t = torch.from_numpy(ue).unsqueeze(0).expand(C, M, -1).to(device)
        uf_t = torch.from_numpy(uf).unsqueeze(0).expand(C, M, -1).to(device)
        m_t = torch.ones((C, M), dtype=torch.bool, device=device)
        p_t = torch.from_numpy(poi_embs[cands]).to(device)
        pf_t = torch.from_numpy(venue_feats[cands]).to(device)

        rv, _, _ = extract_group_relational_features(u_t, uf_t, m_t, p_t, pf_t)
        scores = model.score_relational_head(rv).cpu().numpy()
        base_ndcgs.append(_ndcg_at_k(scores, rel_pos_set, k=10))
        cand_rel_vecs.append(rv)
        cand_pos_sets.append(rel_pos_set)

    base_mean = float(np.mean(base_ndcgs))
    perm_results = []
    for f_idx, fname in enumerate(RELATIONAL_FEATURE_NAMES):
        drops = []
        for g_i, rv in enumerate(cand_rel_vecs):
            rv_perm = rv.clone()
            perm_order = torch.randperm(rv_perm.size(0), device=device)
            rv_perm[:, f_idx] = rv_perm[perm_order, f_idx]
            scores_p = model.score_relational_head(rv_perm).cpu().numpy()
            nd = _ndcg_at_k(scores_p, cand_pos_sets[g_i], k=10)
            drops.append(max(0.0, base_mean - nd))
        perm_results.append({
            "feature": fname,
            "ndcg10_drop": round(float(np.mean(drops)), 5),
        })

    total_drop = sum(r["ndcg10_drop"] for r in perm_results) or 1e-8
    for r in perm_results:
        r["importance_pct"] = round(100.0 * r["ndcg10_drop"] / total_drop, 2)
    return sorted(perm_results, key=lambda x: x["ndcg10_drop"], reverse=True)


@torch.no_grad()
def analyze_cross_attention_and_counterfactuals(
    model: TripSenseFairNet,
    test_groups: List[Dict[str, Any]],
    user_embs_list: List[np.ndarray],
    poi_embs: np.ndarray,
    venue_feats: np.ndarray,
    device: torch.device,
    max_groups: int = 80,
    seed: int = 99,
) -> Dict[str, Any]:
    """
    Analyzes Cross-Attention weight allocation across heterogeneous member budgets
    and evaluates Counterfactual Nash Veto substitutions across test groups.
    """
    model.eval()
    rng = np.random.RandomState(seed)
    V = poi_embs.shape[0]
    low_budget_attns = []
    high_budget_attns = []
    min_sat_before = []
    min_sat_after = []
    gini_before = []
    gini_after = []
    nash_gains = []

    for g_idx, g in enumerate(test_groups[:max_groups]):
        ue = user_embs_list[g_idx]
        uf = np.array(g["user_features"], dtype=np.float32)
        M = ue.shape[0]
        if M < 2:
            continue
        budgets = uf[:, 0]

        # Sample 30 candidate venues for counterfactual audit
        cands = rng.choice(V, size=min(30, V), replace=False)
        C = len(cands)
        u_t = torch.from_numpy(ue).unsqueeze(0).expand(C, M, -1).to(device)
        uf_t = torch.from_numpy(uf).unsqueeze(0).expand(C, M, -1).to(device)
        m_t = torch.ones((C, M), dtype=torch.bool, device=device)
        p_t = torch.from_numpy(poi_embs[cands]).to(device)
        pf_t = torch.from_numpy(venue_feats[cands]).to(device)

        g_scores, m_scores, attn_w = model(u_t, uf_t, m_t, p_t, pf_t)
        g_np = g_scores.cpu().numpy()
        m_np = m_scores.cpu().numpy()
        a_np = attn_w.cpu().numpy()

        top_idx = int(np.argmax(g_np))
        top_attn = a_np[top_idx]
        low_b_idx = int(np.argmin(budgets))
        high_b_idx = int(np.argmax(budgets))
        low_budget_attns.append(float(top_attn[low_b_idx]))
        high_budget_attns.append(float(top_attn[high_b_idx]))

        # Simulate veto by least-satisfied member on a mediocre rank-2/3 candidate -> best counterfactual
        order = np.argsort(-g_np)
        vetoed_i = int(order[min(2, C - 1)])
        ms_vetoed = m_np[vetoed_i]
        gini_v = _gini(ms_vetoed)
        min_v = float(np.min(ms_vetoed))
        nash_v = float(np.prod(np.maximum(0.05, ms_vetoed)) ** (1.0 / M))

        # Best substitute increasing Nash product
        best_nash = nash_v
        best_j = vetoed_i
        for j in range(C):
            if j == vetoed_i:
                continue
            nj = float(np.prod(np.maximum(0.05, m_np[j])) ** (1.0 / M))
            if nj > best_nash:
                best_nash = nj
                best_j = j

        ms_sub = m_np[best_j]
        min_sat_before.append(min_v)
        min_sat_after.append(float(np.min(ms_sub)))
        gini_before.append(gini_v)
        gini_after.append(_gini(ms_sub))
        nash_gains.append(100.0 * (best_nash - nash_v) / max(1e-6, nash_v))

    return {
        "cross_attention_audit": {
            "groups_audited": len(low_budget_attns),
            "uniform_weight_expected": round(1.0 / 3.5, 4),
            "lowest_budget_member_mean_attn": round(float(np.mean(low_budget_attns)), 4),
            "highest_budget_member_mean_attn": round(float(np.mean(high_budget_attns)), 4),
        },
        "nash_counterfactual_recourse": {
            "groups_audited": len(min_sat_before),
            "mean_min_member_sat_before": round(float(np.mean(min_sat_before)), 4),
            "mean_min_member_sat_after": round(float(np.mean(min_sat_after)), 4),
            "mean_gini_before": round(float(np.mean(gini_before)), 4),
            "mean_gini_after": round(float(np.mean(gini_after)), 4),
            "mean_nash_welfare_gain_pct": round(float(np.mean(nash_gains)), 2),
        },
    }


def compute_cross_xai_concordance(
    ig_unsorted: List[Dict[str, Any]],
    perm_sorted: List[Dict[str, Any]],
    shap_summary: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Computes Spearman rho and Kendall tau correlations across XAI methods."""
    ig_map = {r["feature"]: r["mean_abs_ig"] for r in ig_unsorted}
    perm_map = {r["feature"]: r["ndcg10_drop"] for r in perm_sorted}
    names = RELATIONAL_FEATURE_NAMES

    v_ig = np.array([ig_map[n] for n in names])
    v_perm = np.array([perm_map[n] for n in names])
    rho_ip, p_ip = spearmanr(v_ig, v_perm)
    tau_ip, tp_ip = kendalltau(v_ig, v_perm)

    # Compare overlapping features with LightGBM TreeSHAP
    shap_map = {r["feature"]: r["importance_pct"] for r in shap_summary}
    common = [n for n in names if n in shap_map]
    res = {
        "ig_vs_permutation_spearman_rho": round(float(rho_ip), 4),
        "ig_vs_permutation_p_value": float(f"{p_ip:.3e}"),
        "ig_vs_permutation_kendall_tau": round(float(tau_ip), 4),
    }
    if len(common) >= 5:
        v1 = np.array([ig_map[n] for n in common])
        v2 = np.array([shap_map[n] for n in common])
        rho_is, p_is = spearmanr(v1, v2)
        tau_is, _ = kendalltau(v1, v2)
        res["ig_vs_treeshap_common_features"] = len(common)
        res["ig_vs_treeshap_spearman_rho"] = round(float(rho_is), 4)
        res["ig_vs_treeshap_p_value"] = float(f"{p_is:.3e}")
        res["ig_vs_treeshap_kendall_tau"] = round(float(tau_is), 4)
    return res
