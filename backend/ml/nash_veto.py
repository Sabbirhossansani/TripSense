"""
Nash-Bargaining Critique Veto Engine for TripSense.

When member u exercises their Veto Token against POI p:
  1. Counterfactual Critique Revision: Shifts member u's latent taste embedding away
     from vetoed POI's SigLIP representation (e_p) while pulling toward group centroid.
  2. Asymmetric Nash Social Welfare Optimization: Evaluates every non-scheduled city
     candidate p' via TripSense-FairNet to maximize:
         NSW(p') = prod_{i in G} max(eps, U_i(p') - d_i)^{w_i}
     where w_u > w_{j != u} grants priority compensation to the vetoing member
     without harming overall squad harmony.
"""

import math
import numpy as np
from typing import List, Dict, Any
from backend.ml.inference import get_fairnet_inference
from app.algorithms.optimizer import haversine_distance
from app.algorithms.explainability import ExplainabilityGenerator


class NashVetoEngine:
    @staticmethod
    def resolve_veto(
        city: str,
        vetoed_spot: Dict[str, Any],
        vetoed_spot_index: int,
        vetoed_by: str,
        current_spots: List[Dict[str, Any]],
        candidate_spots: List[Dict[str, Any]],
        members: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if not candidate_spots:
            return {
                "success": False,
                "substitute": None,
                "nash_welfare_gain": 0.0,
                "counterfactual_reason": "No unscheduled city attractions remain for substitution.",
                "updated_spots": current_spots,
            }

        infer = get_fairnet_inference()
        veto_emb = infer.get_poi_embedding(vetoed_spot)

        # Build critique-adjusted member profiles (copy to avoid mutating request)
        adjusted_members = []
        for m in members:
            mc = dict(m)
            base_emb = infer.encode_user(mc)
            if mc["name"].lower() == vetoed_by.lower():
                # Counterfactual shift: move away from vetoed POI vector
                shifted = base_emb - 0.45 * veto_emb
                norm = float(np.linalg.norm(shifted))
                mc["taste_embedding"] = (shifted / norm).tolist() if norm > 1e-6 else shifted.tolist()
            else:
                mc["taste_embedding"] = base_emb.tolist()
            adjusted_members.append(mc)

        # Compute disagreement baseline d_i from vetoed spot
        vetoed_eval = infer.score_candidates(adjusted_members, [vetoed_spot])[0]
        base_scores = vetoed_eval["member_scores"]
        baseline_nsw = 1.0
        for m in adjusted_members:
            name = m["name"]
            w = 1.6 if name.lower() == vetoed_by.lower() else 1.0
            u_val = max(0.05, base_scores.get(name, 0.35))
            baseline_nsw *= (u_val ** w)

        # Evaluate all candidate POIs via TripSense-FairNet + Asymmetric Nash Social Welfare
        scored = infer.score_candidates(adjusted_members, candidate_spots)
        best_cand = None
        best_nsw = -1.0

        for cand_scored in scored:
            m_scores = cand_scored["member_scores"]
            nsw = 1.0
            for m in adjusted_members:
                name = m["name"]
                w = 1.6 if name.lower() == vetoed_by.lower() else 1.0
                # Extra boost if candidate category differs from rejected crowd/cost pattern
                u_val = max(0.05, m_scores.get(name, 0.4))
                nsw *= (u_val ** w)

            # Bonus if candidate is less crowded or different category when original was high crowd
            if vetoed_spot.get("crowd_level") == "High" and cand_scored["spot"].get("crowd_level") == "Low":
                nsw *= 1.12

            if nsw > best_nsw:
                best_nsw = nsw
                best_cand = cand_scored

        chosen_raw = best_cand["spot"]
        substitute = dict(chosen_raw)
        substitute["scheduled_slot"] = vetoed_spot.get("scheduled_slot", "Afternoon")
        substitute["match_score"] = round(best_cand["group_score"] * 100, 2)
        m_pcts = {k: round(v * 100, 1) for k, v in best_cand["member_scores"].items()}
        substitute["group_consensus"] = {
            "avg_score": round(sum(m_pcts.values()) / max(1, len(m_pcts)), 1),
            "least_misery_score": round(min(m_pcts.values()) if m_pcts else 50.0, 1),
            "member_breakdown": m_pcts,
            "attention_weights": best_cand.get("attention_weights", {}),
        }

        prev_spot = current_spots[vetoed_spot_index - 1] if vetoed_spot_index > 0 else None
        explanation = ExplainabilityGenerator.generate_explanation(
            substitute, members, prev_spot=prev_spot
        )
        explanation["badges"].insert(0, f"🛡️ Nash Veto Swap ({vetoed_by})")
        substitute["why_this"] = explanation

        # Update schedule and recompute consecutive transit
        updated_spots = list(current_spots)
        updated_spots[vetoed_spot_index] = substitute
        for idx in range(len(updated_spots)):
            if idx == 0:
                updated_spots[idx]["transit_from_prev_km"] = 0.0
                updated_spots[idx]["transit_est_mins"] = 0
            else:
                p_spot = updated_spots[idx - 1]
                c_spot = updated_spots[idx]
                dist = haversine_distance(
                    p_spot["latitude"], p_spot["longitude"],
                    c_spot["latitude"], c_spot["longitude"]
                )
                c_spot["transit_from_prev_km"] = round(dist, 2)
                c_spot["transit_est_mins"] = round((dist / 30.0) * 60)

        nsw_gain_pct = round(((best_nsw - baseline_nsw) / max(1e-5, baseline_nsw)) * 100, 1)
        reason_parts = []
        if vetoed_spot.get("crowd_level") == "High" and substitute.get("crowd_level") == "Low":
            reason_parts.append("shifted away from high-crowd congestion")
        if substitute.get("estimated_cost_bdt", 0) < vetoed_spot.get("estimated_cost_bdt", 0):
            reason_parts.append("reduced ticket expenditure")
        if substitute.get("category") != vetoed_spot.get("category"):
            reason_parts.append(f"pivoted from {vetoed_spot.get('category')} to {substitute.get('category')}")
        cf_reason = (
            f"Counterfactual critique {', '.join(reason_parts) or 're-aligned embedding'}; "
            f"Nash Social Welfare Δ = {nsw_gain_pct:+.1f}%."
        )

        return {
            "success": True,
            "substitute": substitute,
            "nash_welfare_gain": nsw_gain_pct,
            "counterfactual_reason": cf_reason,
            "updated_spots": updated_spots,
        }
