"""
Active Bayesian Preference Elicitation (CLIP/SigLIP + Expected Information Gain)
for TripSense's 60-Second Swipe Deck.

Instead of asking static categorical checkboxes, this engine maintains a Gaussian
posterior N(mu_u, diag(sigma^2_u)) over the user's continuous SigLIP taste embedding
and selects the next card maximizing Expected Information Gain + diversity.
"""

import os
import numpy as np
from typing import List, Dict, Any, Tuple
from backend.ml.backbone import SWIPE_CARDS_CATALOG, ARTIFACTS_DIR

CATEGORIES = ["Historical", "Culture", "Nature", "Adventure", "Food", "Shopping", "Relaxation", "Beach"]


class ActiveSwipeEngine:
    def __init__(self, artifacts_dir: str = ARTIFACTS_DIR):
        self.cards = SWIPE_CARDS_CATALOG
        self.card_by_id = {c["id"]: c for c in self.cards}
        self.swipe_npz = os.path.join(artifacts_dir, "swipe_embeddings.npz")
        self.poi_npz = os.path.join(artifacts_dir, "poi_embeddings.npz")

        self.card_embs: Dict[str, np.ndarray] = {}
        self.emb_dim = 768
        self._load_embeddings()

    def _load_embeddings(self):
        if os.path.exists(self.swipe_npz):
            data = np.load(self.swipe_npz, allow_pickle=False)
            c_ids = [str(x) for x in data["card_ids"]]
            embs = data["embeddings"].astype(np.float32)
            self.emb_dim = int(embs.shape[1])
            for cid, vec in zip(c_ids, embs):
                self.card_embs[cid] = vec
        else:
            # Deterministic orthogonal fallback if artifacts have not been built yet
            rng = np.random.default_rng(42)
            self.emb_dim = 64
            for c in self.cards:
                v = rng.normal(size=self.emb_dim).astype(np.float32)
                v /= np.linalg.norm(v) + 1e-8
                self.card_embs[c["id"]] = v

    def infer_posterior(self, history: List[Dict[str, str]]) -> Tuple[np.ndarray, np.ndarray, Dict[str, float]]:
        """
        Bayesian Ridge / Kalman-style Gaussian belief update in SigLIP space.
        - 'super': +1.35 pull, strong precision
        - 'like':  +1.00 pull, standard precision
        - 'pass':  -0.65 push away, moderate precision
        Returns: (mu_normed, sigma_diag, category_scores)
        """
        mu = np.zeros(self.emb_dim, dtype=np.float32)
        precision = np.ones(self.emb_dim, dtype=np.float32) * 1.0  # Prior precision = 1.0

        cat_votes = {cat: 0.35 for cat in CATEGORIES}

        for item in history:
            cid = item.get("card_id", "")
            action = item.get("action", "like").lower()
            card = self.card_by_id.get(cid)
            if not card or cid not in self.card_embs:
                continue

            vec = self.card_embs[cid]
            cat = card["category"]

            if action == "super":
                weight, obs_prec = 1.35, 3.0
                cat_votes[cat] = min(1.0, cat_votes.get(cat, 0.35) + 0.55)
            elif action == "like":
                weight, obs_prec = 1.0, 2.0
                cat_votes[cat] = min(1.0, cat_votes.get(cat, 0.35) + 0.40)
            else:  # pass
                weight, obs_prec = -0.60, 1.5
                cat_votes[cat] = max(0.05, cat_votes.get(cat, 0.35) - 0.28)

            # Diagonal Bayesian update proportional to squared feature energy
            feat_energy = (vec ** 2) * obs_prec * self.emb_dim * 0.15
            new_prec = precision + feat_energy
            mu = (precision * mu + feat_energy * (weight * vec)) / np.maximum(new_prec, 1e-6)
            precision = new_prec

        sigma_diag = 1.0 / np.maximum(precision, 1e-6)
        norm = float(np.linalg.norm(mu))
        mu_normed = (mu / norm).astype(np.float32) if norm > 1e-6 else mu

        # Also boost categories semantically aligned in SigLIP space
        if norm > 1e-6:
            for c in self.cards:
                sim = float(np.dot(mu_normed, self.card_embs[c["id"]]))
                cat_votes[c["category"]] = float(np.clip(cat_votes[c["category"]] + 0.15 * sim, 0.05, 1.0))

        return mu_normed, sigma_diag, {k: round(v * 100, 1) for k, v in cat_votes.items()}

    def step(self, history: List[Dict[str, str]], max_cards: int = 6) -> Dict[str, Any]:
        """
        Computes current posterior & picks next most informative card via Expected Information Gain.
        """
        seen_ids = {h.get("card_id") for h in history}
        seen_cats = {self.card_by_id[cid]["category"] for cid in seen_ids if cid in self.card_by_id}

        mu_normed, sigma_diag, cat_scores = self.infer_posterior(history)
        step_idx = len(history)

        # Confidence grows rapidly as posterior variance contracts across orthogonal themes
        prior_var = float(self.emb_dim)
        current_var = float(sigma_diag.sum())
        reduction = max(0.0, 1.0 - (current_var / prior_var))
        confidence_pct = round(min(96.5, 22.0 + 74.5 * (1.0 - np.exp(-step_idx * 0.42)) + 15.0 * reduction), 1)

        inferred_interests = [
            cat for cat, sc in sorted(cat_scores.items(), key=lambda x: x[1], reverse=True)
            if sc >= 52.0
        ][:4]
        if not inferred_interests:
            inferred_interests = ["Nature", "Historical", "Food"]

        if step_idx >= max_cards or len(seen_ids) >= len(self.cards):
            return {
                "completed": True,
                "step": step_idx,
                "total_steps": max_cards,
                "confidence_pct": confidence_pct,
                "next_card": None,
                "inferred_interests": inferred_interests,
                "category_scores": cat_scores,
                "taste_embedding": mu_normed.tolist(),
                "information_gain": 0.0,
            }

        # Select next card maximizing Expected Information Gain + category exploration bonus
        best_card = None
        best_eig = -1e9
        for card in self.cards:
            cid = card["id"]
            if cid in seen_ids:
                continue
            vec = self.card_embs[cid]
            # Predictive variance along candidate direction: e_c^T Sigma e_c
            proj_var = float(np.dot(vec ** 2, sigma_diag))
            # Exploration bonus for unseen categories so we probe diverse tastes early
            cat_bonus = 0.35 if card["category"] not in seen_cats else 0.0
            # Uncertainty closeness: near 0 similarity = maximally informative decision boundary
            boundary_bonus = 0.15 * (1.0 - abs(float(np.dot(mu_normed, vec)))) if step_idx > 0 else 0.1
            eig = proj_var + cat_bonus + boundary_bonus

            if eig > best_eig:
                best_eig = eig
                best_card = card

        return {
            "completed": False,
            "step": step_idx,
            "total_steps": max_cards,
            "confidence_pct": confidence_pct,
            "next_card": best_card,
            "inferred_interests": inferred_interests,
            "category_scores": cat_scores,
            "taste_embedding": mu_normed.tolist(),
            "information_gain": round(float(best_eig), 4),
        }


def benchmark_active_vs_random_swipe(
    venue_embs: np.ndarray,
    user_to_venues: Dict[str, List[int]],
    seed: int = 42,
    n_eval_users: int = 120,
) -> Dict[str, Any]:
    """
    Evaluates Active Bayesian Swipe vs. Random Card Quiz on real Massive-STEPS-Sydney users.
    For each user, first 60% of check-ins define latent ground-truth taste vector;
    test set is final 40% check-ins. Measures NDCG@10 after 1, 3, 5, 7, 10 simulated swipes.
    """
    rng = np.random.default_rng(seed)
    eligible = [u for u, seq in user_to_venues.items() if len(seq) >= 6]
    if len(eligible) > n_eval_users:
        eligible = list(rng.choice(eligible, size=n_eval_users, replace=False))

    k_steps = [1, 3, 5, 7, 10]
    active_ndcg = {k: [] for k in k_steps}
    random_ndcg = {k: [] for k in k_steps}

    n_venues = len(venue_embs)
    emb_dim = venue_embs.shape[1]
    centered = venue_embs.astype(np.float32) - venue_embs.mean(axis=0, keepdims=True).astype(np.float32)
    centered /= np.linalg.norm(centered, axis=1, keepdims=True) + 1e-8

    def _ndcg_at_10(pred_order: np.ndarray, gt_set: set) -> float:
        dcg = 0.0
        for rank, vid in enumerate(pred_order[:10]):
            if int(vid) in gt_set:
                dcg += 1.0 / np.log2(rank + 2.0)
        ideal_hits = min(10, len(gt_set))
        idcg = sum(1.0 / np.log2(r + 2.0) for r in range(ideal_hits))
        return dcg / idcg if idcg > 0 else 0.0

    for u in eligible:
        seq = user_to_venues[u]
        split = max(3, int(len(seq) * 0.6))
        train_ids = seq[:split]
        gt_set = set(seq[split:])

        # Ground-truth user profile centroid in zero-centered CLIP space (for simulated swipe oracle only)
        gt_vec = centered[train_ids].mean(axis=0)
        gt_vec /= np.linalg.norm(gt_vec) + 1e-8

        visited_all = set(seq)
        unvisited = [i for i in range(n_venues) if i not in visited_all]
        probe_pool = rng.choice(unvisited, size=min(48, len(unvisited)), replace=False)
        probe_set = set(int(x) for x in probe_pool)
        neg_candidates = [i for i in unvisited if i not in probe_set]
        eval_neg = list(rng.choice(neg_candidates, size=min(90, len(neg_candidates)), replace=False))
        eval_pool = np.array(list(gt_set) + [int(x) for x in eval_neg], dtype=np.int64)
        med_sim = float(np.median(centered[probe_pool] @ gt_vec))

        for mode, out_dict in [("active", active_ndcg), ("random", random_ndcg)]:
            mu = np.zeros(emb_dim, dtype=np.float32)
            prec = np.ones(emb_dim, dtype=np.float32)
            swiped = set()

            for step in range(1, max(k_steps) + 1):
                avail = [int(p) for p in probe_pool if int(p) not in swiped]
                if not avail:
                    break
                if mode == "active":
                    sigma = 1.0 / prec
                    mu_norm_cur = mu / (np.linalg.norm(mu) + 1e-8)
                    # Pick candidate maximizing EIG along uncertain boundary
                    best_p = max(
                        avail,
                        key=lambda p: float(np.dot(centered[p] ** 2, sigma))
                        + 0.25 * (1.0 - abs(float(np.dot(mu_norm_cur, centered[p])))),
                    )
                else:
                    best_p = int(rng.choice(avail))

                swiped.add(best_p)
                sim_gt = float(np.dot(gt_vec, centered[best_p]))
                label = 1.0 if sim_gt >= med_sim else -0.65
                obs_prec = 2.5 if label > 0 else 1.5
                e = (centered[best_p] ** 2) * obs_prec * emb_dim * 0.15
                new_prec = prec + e
                mu = (prec * mu + e * (label * centered[best_p])) / np.maximum(new_prec, 1e-6)
                prec = new_prec

                if step in k_steps:
                    mu_norm = mu / (np.linalg.norm(mu) + 1e-8)
                    scores = centered[eval_pool] @ mu_norm
                    ranked = eval_pool[np.argsort(-scores)]
                    out_dict[step].append(_ndcg_at_10(ranked, gt_set))

    return {
        "eval_users": len(eligible),
        "swipes": k_steps,
        "active_bayesian_ndcg10": [round(float(np.mean(active_ndcg[k])), 4) for k in k_steps],
        "random_quiz_ndcg10": [round(float(np.mean(random_ndcg[k])), 4) for k in k_steps],
    }
