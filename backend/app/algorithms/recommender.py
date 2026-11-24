import math
from typing import List, Dict, Any

class ContentBasedRecommender:
    """
    Academic Content-Based Filtering Engine.
    Matches User Preferences (Interest Tags, Budget Tier, Rating Preference)
    with Candidate Spots using Vector Cosine Similarity & Multi-Attribute Scoring.
    """
    
    CATEGORIES = ["Historical", "Culture", "Nature", "Adventure", "Food", "Shopping", "Relaxation"]

    def __init__(self, spots: List[Dict[str, Any]]):
        self.spots = spots

    def _create_interest_vector(self, user_interests: List[str]) -> List[float]:
        """Convert list of user interest categories into a normalized binary vector."""
        vec = [1.0 if cat.lower() in [i.lower() for i in user_interests] else 0.0 for cat in self.CATEGORIES]
        norm = math.sqrt(sum(x**2 for x in vec))
        return [x / norm if norm > 0 else 0.0 for x in vec]

    def _create_spot_vector(self, spot_category: str) -> List[float]:
        """Convert spot category into a normalized binary vector."""
        vec = [1.0 if cat.lower() == spot_category.lower() else 0.0 for cat in self.CATEGORIES]
        norm = math.sqrt(sum(x**2 for x in vec))
        return [x / norm if norm > 0 else 0.0 for x in vec]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two feature vectors."""
        dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
        return dot_product

    def recommend(
        self,
        city: str,
        user_interests: List[str],
        budget_tier: str = "Mid-range",
        min_rating: float = 4.0,
        top_k: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Filters and ranks spots based on user interest vector similarity,
        rating weights, and budget constraints.
        """
        # 1. Filter by city
        city_spots = [s for s in self.spots if s["city"].lower() == city.lower()]
        if not city_spots:
            # Fallback to all spots if exact city not found
            city_spots = self.spots

        user_vec = self._create_interest_vector(user_interests)
        scored_spots = []

        for spot in city_spots:
            spot_vec = self._create_spot_vector(spot.get("category", "Culture"))
            interest_score = self._cosine_similarity(user_vec, spot_vec) if sum(user_vec) > 0 else 0.5
            
            # Rating Score normalized (0 to 1)
            rating_score = (spot.get("rating", 4.0) - 3.0) / 2.0
            rating_score = max(0.0, min(1.0, rating_score))

            # Budget Penalty / Adjustment
            cost = spot.get("estimated_cost_usd", 0.0)
            budget_score = 1.0
            if budget_tier == "Budget" and cost > 25.0:
                budget_score = 0.5
            elif budget_tier == "Luxury" and cost == 0.0:
                budget_score = 0.8

            # Final Hybrid Score (70% Interest match, 20% Rating, 10% Budget fit)
            final_score = (0.7 * interest_score) + (0.2 * rating_score) + (0.1 * budget_score)

            spot_copy = dict(spot)
            spot_copy["match_score"] = round(final_score * 100, 2)
            scored_spots.append((final_score, spot_copy))

        # Sort descending by match score
        scored_spots.sort(key=lambda x: x[0], reverse=True)
        return [spot for _, spot in scored_spots[:top_k]]
