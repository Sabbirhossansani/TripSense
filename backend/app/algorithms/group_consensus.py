import math
from typing import List, Dict, Any, Tuple


class GroupConsensusEngine:
    """
    Academic Group Recommender System (GRS) Engine.
    Supports:
      1. TripSense-FairNet Neural Cross-Attention Consensus (default Q1 ML model)
      2. Least-Misery Social Choice Heuristic
      3. Average Utilitarian Strategy
      4. Group Fairness Metrics (Gini coefficient, Disparity, Fairness Score)
    """

    CATEGORIES = ["Historical", "Culture", "Nature", "Adventure", "Food", "Shopping", "Relaxation", "Beach"]

    def __init__(self, spots: List[Dict[str, Any]]):
        self.spots = spots

    def _interest_vector(self, interests: List[str]) -> List[float]:
        vec = [1.0 if cat.lower() in [i.lower() for i in interests] else 0.0 for cat in self.CATEGORIES]
        norm = math.sqrt(sum(x**2 for x in vec))
        return [x / norm if norm > 0 else 0.0 for x in vec]

    def _spot_vector(self, spot_category: str) -> List[float]:
        vec = [1.0 if cat.lower() == spot_category.lower() else 0.0 for cat in self.CATEGORIES]
        norm = math.sqrt(sum(x**2 for x in vec))
        return [x / norm if norm > 0 else 0.0 for x in vec]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        return sum(v1 * v2 for v1, v2 in zip(vec1, vec2))

    def compute_individual_score(self, user: Dict[str, Any], spot: Dict[str, Any]) -> float:
        """
        Computes normalized utility (0.0 to 1.0) of a spot for a single user.
        """
        user_vec = self._interest_vector(user.get("interests", []))
        spot_vec = self._spot_vector(spot.get("category", "Culture"))

        interest_match = self._cosine_similarity(user_vec, spot_vec) if sum(user_vec) > 0 else 0.5
        rating = spot.get("rating", 4.0)
        rating_score = max(0.0, min(1.0, (rating - 3.0) / 2.0))

        budget_tier = user.get("budget_tier", "Mid-range")
        cost = spot.get("estimated_cost_bdt", spot.get("estimated_cost_usd", 0.0) * 115.0)
        budget_score = 1.0
        if budget_tier == "Budget" and cost > 300.0:
            budget_score = 0.5
        elif budget_tier == "Luxury" and cost == 0.0:
            budget_score = 0.85

        score = (0.65 * interest_match) + (0.25 * rating_score) + (0.10 * budget_score)
        return round(score, 4)

    def recommend_for_group(
        self,
        city: str,
        members: List[Dict[str, Any]],
        strategy: str = "fairnet",
        promote_hidden_gems: bool = True,
        top_k: int = 15
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Ranks candidate spots for the group according to the chosen consensus strategy.
        Returns:
            - Ranked spots with group consensus breakdown & feature attributions
            - Fairness metrics (Fairness Score, Gini, Disparity, Model Used)
        """
        city_spots = [s for s in self.spots if s.get("city", "").lower() == city.lower()]
        if not city_spots:
            city_spots = self.spots

        model_label = "TripSense-FairNet (CLIP + Neural Cross-Attention)"
        scored_candidates = []

        if strategy.lower() == "fairnet":
            try:
                from backend.ml.inference import get_fairnet_inference
                infer = get_fairnet_inference()
                neural_results = infer.score_candidates(members, city_spots)
                if not infer.loaded_real_model:
                    model_label = "FairNet Fallback (CLIP Semantic)"

                for res in neural_results:
                    spot = res["spot"]
                    base_u = res["group_score"]
                    hidden_bonus = 0.0
                    if promote_hidden_gems and spot.get("hidden_gem", False):
                        hidden_bonus += 0.06
                    if spot.get("crowd_level") == "Low":
                        hidden_bonus += 0.03
                    final_utility = min(1.0, base_u + hidden_bonus)

                    m_pcts = {k: round(v * 100, 1) for k, v in res["member_scores"].items()}
                    vals = list(m_pcts.values()) or [50.0]

                    spot_copy = dict(spot)
                    spot_copy["match_score"] = round(final_utility * 100, 2)
                    spot_copy["feature_attributions"] = res.get("feature_attributions")
                    spot_copy["group_consensus"] = {
                        "avg_score": round(sum(vals) / len(vals), 1),
                        "least_misery_score": round(min(vals), 1),
                        "member_breakdown": m_pcts,
                        "attention_weights": res.get("attention_weights", {}),
                    }
                    scored_candidates.append((final_utility, spot_copy))
            except Exception as e:
                print(f"[GroupConsensusEngine] FairNet inference fallback: {e}")
                scored_candidates = []
                model_label = "Least-Misery Social Choice Fallback"

        if not scored_candidates:
            if strategy.lower() != "fairnet":
                model_label = f"{strategy.replace('_', ' ').title()} Strategy"
            for spot in city_spots:
                member_scores = {m["name"]: self.compute_individual_score(m, spot) for m in members}
                scores_list = list(member_scores.values())
                avg_score = sum(scores_list) / len(scores_list) if scores_list else 0.5
                min_score = min(scores_list) if scores_list else 0.5

                if strategy.lower() == "least_misery":
                    consensus_score = (0.60 * min_score) + (0.40 * avg_score)
                elif strategy.lower() == "average":
                    consensus_score = avg_score
                else:
                    consensus_score = (0.50 * avg_score) + (0.50 * min_score)

                hidden_gem_bonus = 0.0
                if promote_hidden_gems and spot.get("hidden_gem", False):
                    hidden_gem_bonus = 0.08
                if spot.get("crowd_level") == "Low":
                    hidden_gem_bonus += 0.03

                final_utility = min(1.0, consensus_score + hidden_gem_bonus)

                spot_copy = dict(spot)
                spot_copy["match_score"] = round(final_utility * 100, 2)
                spot_copy["group_consensus"] = {
                    "avg_score": round(avg_score * 100, 1),
                    "least_misery_score": round(min_score * 100, 1),
                    "member_breakdown": {k: round(v * 100, 1) for k, v in member_scores.items()}
                }
                scored_candidates.append((final_utility, spot_copy))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        top_spots = [spot for _, spot in scored_candidates[:top_k]]

        fairness_metrics = self.calculate_fairness_metrics(members, top_spots)
        fairness_metrics["model_used"] = model_label

        return top_spots, fairness_metrics

    def calculate_fairness_metrics(
        self,
        members: List[Dict[str, Any]],
        recommended_spots: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Academic metrics for thesis Chapter 4 / Q1 evaluation:
        1. Member Mean Satisfaction
        2. Satisfaction Disparity (Max - Min)
        3. Gini Coefficient of group satisfaction
        """
        if not recommended_spots or not members:
            return {"gini_index": 0.0, "fairness_score": 100.0, "satisfaction_disparity": 0.0, "member_average_satisfaction": {}}

        member_satisfactions = {m["name"]: 0.0 for m in members}
        for spot in recommended_spots:
            breakdown = spot.get("group_consensus", {}).get("member_breakdown", {})
            for name, score in breakdown.items():
                if name in member_satisfactions:
                    member_satisfactions[name] += score

        n_spots = len(recommended_spots)
        avg_satisfactions = [score / n_spots for score in member_satisfactions.values()]

        min_sat = min(avg_satisfactions)
        max_sat = max(avg_satisfactions)
        disparity = round(max_sat - min_sat, 2)

        sorted_sats = sorted(avg_satisfactions)
        n = len(sorted_sats)
        if n > 1 and sum(sorted_sats) > 0:
            numer = sum((2 * (i + 1) - n - 1) * sorted_sats[i] for i in range(n))
            denom = n * sum(sorted_sats)
            gini = round(numer / denom, 4)
        else:
            gini = 0.0

        fairness_score = round(max(0.0, 100.0 - (disparity * 1.5)), 2)

        return {
            "fairness_score": fairness_score,
            "satisfaction_disparity": disparity,
            "gini_index": gini,
            "member_average_satisfaction": {
                name: round(sat / n_spots, 1) for name, sat in member_satisfactions.items()
            }
        }
