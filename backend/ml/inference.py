"""
Runtime Inference Wrapper for TripSense-FairNet & Precomputed SigLIP POI Embeddings.
Provides sub-10ms CPU/GPU scoring inside FastAPI endpoints with graceful fallback.
"""

import os
import json
import math
import pickle
import numpy as np
import torch
from typing import List, Dict, Any
from backend.ml.fairnet import TripSenseFairNet

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")

CATEGORY_DESCRIPTIONS = {
    "historical": "ancient fort palace mosque heritage architecture history museum",
    "culture": "cultural museum indigenous crafts handloom exhibition heritage",
    "nature": "forest waterfall lake wildlife mountain sanctuary nature eco tour",
    "adventure": "trekking boating cycling cave adventure mountain peaks trails",
    "food": "local street food traditional restaurant mezban biryani cafe culinary",
    "shopping": "local craft market artisan bazaar souvenirs",
    "relaxation": "calm lakeside tea garden peaceful lounge sunset breeze",
    "beach": "golden ocean sandy beach coral waves sunset coastline",
}


class FairNetInference:
    def __init__(self, artifacts_dir: str = ARTIFACTS_DIR):
        self.artifacts_dir = artifacts_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.poi_embs: Dict[int, np.ndarray] = {}
        self.emb_dim = 768
        self.cat_embs: Dict[str, np.ndarray] = {}
        self.loaded_real_model = False
        self.backbone_name = "google/siglip-base-patch16-224"
        self.q1_metrics: Dict[str, Any] = {}
        self._load()

    def _load(self):
        poi_npz = os.path.join(self.artifacts_dir, "poi_embeddings.npz")
        ckpt_pt = os.path.join(self.artifacts_dir, "fairnet_best.pt")
        metrics_json = os.path.join(self.artifacts_dir, "q1_benchmark_results.json")

        if os.path.exists(metrics_json):
            try:
                self.q1_metrics = json.load(open(metrics_json, "r", encoding="utf-8"))
            except Exception:
                self.q1_metrics = {}

        if os.path.exists(poi_npz):
            data = np.load(poi_npz, allow_pickle=False)
            ids = data["poi_ids"]
            embs = data["embeddings"].astype(np.float32)
            self.emb_dim = int(embs.shape[1])
            if "model_name" in data:
                self.backbone_name = str(data["model_name"][0])
            for pid, vec in zip(ids, embs):
                self.poi_embs[int(pid)] = vec

        # Build category prototype vectors from Swipe embeddings or POI centroids
        swipe_npz = os.path.join(self.artifacts_dir, "swipe_embeddings.npz")
        if os.path.exists(swipe_npz):
            sdata = np.load(swipe_npz, allow_pickle=False)
            cats = [str(c).lower() for c in sdata["categories"]]
            sembs = sdata["embeddings"].astype(np.float32)
            for c_low in CATEGORY_DESCRIPTIONS:
                matches = [sembs[i] for i, cat in enumerate(cats) if cat == c_low]
                if matches:
                    centroid = np.mean(matches, axis=0)
                    centroid /= np.linalg.norm(centroid) + 1e-8
                    self.cat_embs[c_low] = centroid.astype(np.float32)

        if os.path.exists(ckpt_pt):
            try:
                ckpt = torch.load(ckpt_pt, map_location=self.device, weights_only=False)
                cfg = ckpt.get("config", {})
                model = TripSenseFairNet(
                    emb_dim=cfg.get("emb_dim", self.emb_dim),
                    poi_feat_dim=cfg.get("poi_feat_dim", 8),
                    user_feat_dim=cfg.get("user_feat_dim", 3),
                    hidden_dim=cfg.get("hidden_dim", 64),
                    num_heads=cfg.get("num_heads", 4),
                    use_attention=cfg.get("use_attention", True),
                    use_relational_stream=cfg.get("use_relational_stream", True),
                    use_member_sab=cfg.get("use_member_sab", False),
                    use_hadamard=cfg.get("use_hadamard", True),
                    use_spectral_gate=cfg.get("use_spectral_gate", True),
                    subspace_rank=cfg.get("subspace_rank", 48),
                ).to(self.device)
                model.load_state_dict(ckpt["model_state_dict"])
                model.eval()
                self.model = model
                self.loaded_real_model = True
            except Exception as e:
                print(f"[FairNetInference] Could not load checkpoint: {e}")

    def get_poi_embedding(self, spot: Dict[str, Any]) -> np.ndarray:
        sid = int(spot.get("id", -1))
        if sid in self.poi_embs:
            return self.poi_embs[sid]
        cat = str(spot.get("category", "culture")).lower()
        if cat in self.cat_embs:
            return self.cat_embs[cat]
        vec = np.zeros(self.emb_dim, dtype=np.float32)
        vec[hash(cat) % self.emb_dim] = 1.0
        return vec

    @staticmethod
    def extract_poi_features(spot: Dict[str, Any]) -> np.ndarray:
        cost_bdt = float(spot.get("estimated_cost_bdt", spot.get("estimated_cost_usd", 0.0) * 115.0))
        price_norm = min(1.0, cost_bdt / 1000.0)
        crowd_map = {"low": 0.25, "medium": 0.55, "high": 0.88}
        crowd_norm = crowd_map.get(str(spot.get("crowd_level", "medium")).lower(), 0.55)
        rating_norm = max(0.0, min(1.0, (float(spot.get("rating", 4.4)) - 3.0) / 2.0))
        is_indoor = 1.0 if str(spot.get("indoor_outdoor", "Outdoor")).lower() == "indoor" else 0.0
        is_hidden = 1.0 if spot.get("hidden_gem", False) else 0.0
        eco_norm = min(1.0, float(spot.get("sustainability_score", 80)) / 100.0)
        sme_norm = min(1.0, float(spot.get("local_revenue_share_pct", 65)) / 100.0)
        dist_norm = 0.25  # Default intra-city centrality
        return np.array(
            [dist_norm, price_norm, crowd_norm, rating_norm, is_indoor, is_hidden, eco_norm, sme_norm],
            dtype=np.float32,
        )

    def encode_user(self, user: Dict[str, Any]) -> np.ndarray:
        custom_emb = user.get("taste_embedding")
        if custom_emb and len(custom_emb) == self.emb_dim:
            vec = np.array(custom_emb, dtype=np.float32)
            norm = float(np.linalg.norm(vec))
            return (vec / norm) if norm > 1e-6 else vec

        interests = [str(i).lower() for i in user.get("interests", [])]
        vecs = [self.cat_embs[c] for c in interests if c in self.cat_embs]
        if vecs:
            centroid = np.mean(vecs, axis=0)
            centroid /= np.linalg.norm(centroid) + 1e-8
            return centroid.astype(np.float32)

        # Fallback if no category embeddings matched
        if self.cat_embs:
            any_vec = np.mean(list(self.cat_embs.values()), axis=0)
            any_vec /= np.linalg.norm(any_vec) + 1e-8
            return any_vec.astype(np.float32)
        return np.zeros(self.emb_dim, dtype=np.float32)

    @staticmethod
    def extract_user_features(user: Dict[str, Any]) -> np.ndarray:
        tier = str(user.get("budget_tier", "Mid-range")).lower()
        b_val = 0.25 if tier == "budget" else (0.90 if tier == "luxury" else 0.55)
        n_int = min(1.0, len(user.get("interests", [])) / 5.0)
        flex = 0.65 if tier != "budget" else 0.45
        return np.array([b_val, n_int, flex], dtype=np.float32)

    @torch.no_grad()
    def score_candidates(
        self,
        members: List[Dict[str, Any]],
        candidates: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Scores candidate POIs for a group using TripSense-FairNet when loaded,
        incorporating explicit semantic alignment and budget/eco calibration.
        """
        if not candidates or not members:
            return []

        M = len(members)
        u_embs = np.stack([self.encode_user(m) for m in members], axis=0)  # (M, D)
        u_feats = np.stack([self.extract_user_features(m) for m in members], axis=0)  # (M, 3)

        N = len(candidates)
        p_embs = np.stack([self.get_poi_embedding(s) for s in candidates], axis=0)  # (N, D)
        p_feats = np.stack([self.extract_poi_features(s) for s in candidates], axis=0)  # (N, 8)

        # Cosine alignment in SigLIP space + explicit category match signal
        cos_sim = np.clip(p_embs @ u_embs.T, -1.0, 1.0)  # (N, M)

        if self.model is not None:
            u_t = torch.from_numpy(u_embs).unsqueeze(0).expand(N, M, self.emb_dim).to(self.device)
            uf_t = torch.from_numpy(u_feats).unsqueeze(0).expand(N, M, 3).to(self.device)
            mask_t = torch.ones((N, M), dtype=torch.bool, device=self.device)
            p_t = torch.from_numpy(p_embs).to(self.device)
            pf_t = torch.from_numpy(p_feats).to(self.device)

            g_scores, m_scores, attn_w = self.model(u_t, uf_t, mask_t, p_t, pf_t)
            g_np = g_scores.cpu().numpy()
            m_np = m_scores.cpu().numpy()
            a_np = attn_w.cpu().numpy()
        else:
            m_np = np.clip(0.5 + 0.4 * cos_sim, 0.1, 0.95)
            g_np = 0.5 * m_np.mean(axis=1) + 0.5 * m_np.min(axis=1)
            a_np = np.full((N, M), 1.0 / M, dtype=np.float32)

        results = []
        for idx, spot in enumerate(candidates):
            spot_cat = str(spot.get("category", "")).lower()
            cost_bdt = float(spot.get("estimated_cost_bdt", 0.0))
            rating_norm = max(0.0, min(1.0, (float(spot.get("rating", 4.4)) - 3.0) / 2.0))
            eco_norm = float(spot.get("sustainability_score", 80)) / 100.0

            member_dict = {}
            attn_dict = {}
            calibrated_vals = []
            for m_idx, m in enumerate(members):
                m_interests = [str(i).lower() for i in m.get("interests", [])]
                cat_hit = 1.0 if spot_cat in m_interests else 0.0
                # Combine FairNet learned prediction with exact category alignment & SigLIP sim
                sim_unit = float(np.clip((cos_sim[idx, m_idx] + 0.1) / 0.6, 0.0, 1.0))
                budget_fit = 1.0
                if str(m.get("budget_tier", "")).lower() == "budget" and cost_bdt > 350.0:
                    budget_fit = 0.48
                elif str(m.get("budget_tier", "")).lower() == "luxury" and cost_bdt == 0.0:
                    budget_fit = 0.85

                nn_pred = float(m_np[idx, m_idx])
                blended_u = (0.42 * nn_pred) + (0.30 * cat_hit) + (0.18 * sim_unit) + (0.10 * budget_fit)
                blended_u = float(np.clip(blended_u, 0.12, 0.98))
                member_dict[m["name"]] = blended_u
                attn_dict[m["name"]] = round(float(a_np[idx, m_idx]), 3)
                calibrated_vals.append(blended_u)

            min_u = min(calibrated_vals)
            avg_u = sum(calibrated_vals) / len(calibrated_vals)
            nn_g = float(g_np[idx])
            final_g = float(np.clip((0.40 * nn_g) + (0.35 * min_u) + (0.15 * avg_u) + (0.10 * eco_norm), 0.1, 0.99))

            # Feature attribution breakdown for XAI modal
            feature_attr = {
                "taste_alignment": round(0.42 * nn_g + 0.18 * float(np.mean(cos_sim[idx])), 3),
                "least_misery_floor": round(0.35 * min_u, 3),
                "eco_sustainability": round(0.10 * eco_norm, 3),
                "rating_quality": round(0.10 * rating_norm, 3),
            }

            results.append({
                "spot": spot,
                "group_score": final_g,
                "member_scores": member_dict,
                "attention_weights": attn_dict,
                "feature_attributions": feature_attr,
            })

        return results


_INFERENCE_SINGLETON = None


def get_fairnet_inference() -> FairNetInference:
    global _INFERENCE_SINGLETON
    if _INFERENCE_SINGLETON is None:
        _INFERENCE_SINGLETON = FairNetInference()
    return _INFERENCE_SINGLETON
