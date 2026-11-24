from typing import Dict, Any, List


class ExplainabilityGenerator:
    """
    Academic Explainable AI (XAI) Module for TripSense.
    Generates rule-grounded + FairNet feature-attributed explanations
    and visual pill tags explaining why a specific POI was selected for the group.
    """

    @staticmethod
    def generate_explanation(
        spot: Dict[str, Any],
        members: List[Dict[str, Any]],
        prev_spot: Dict[str, Any] = None,
        is_weather_substitute: bool = False
    ) -> Dict[str, Any]:
        category = spot.get("category", "Culture")
        cost_bdt = spot.get("estimated_cost_bdt", 0.0)
        best_time = spot.get("best_time", "Anytime")
        is_hidden_gem = spot.get("hidden_gem", False)
        crowd_level = spot.get("crowd_level", "Medium")
        is_sme = spot.get("local_sme", False)
        eco_score = spot.get("sustainability_score", 80)

        interested_members = [
            m["name"] for m in members
            if category.lower() in [i.lower() for i in m.get("interests", [])]
        ]
        total_members = len(members)

        badges = []
        if len(interested_members) >= max(1, total_members // 2):
            badges.append(f"{len(interested_members)}/{total_members} Friends Agree")

        if is_weather_substitute:
            badges.append("Rain-Safe Indoor Spot")
        elif spot.get("indoor_outdoor") == "Indoor":
            badges.append("Indoor Friendly")

        if is_hidden_gem:
            badges.append("Hidden Gem")
        elif crowd_level == "Low":
            badges.append("Peaceful / Low Crowd")

        if is_sme:
            badges.append("Local SME Host")

        if eco_score >= 85:
            badges.append(f"Eco {eco_score}/100")

        if cost_bdt == 0.0:
            badges.append("Free Entry")
        elif cost_bdt <= 100.0:
            badges.append("Budget Friendly")

        badges.append(f"Best in {best_time}")

        reasons = []
        if is_weather_substitute:
            reasons.append("Swapped as a rain-safe indoor alternative due to adverse weather.")

        if interested_members:
            names_str = ", ".join(interested_members)
            reasons.append(f"Aligns with {names_str}'s preference for {category}.")
        else:
            reasons.append(f"Balanced consensus pick ({spot.get('rating', 4.5)}★) protecting overall squad harmony.")

        if prev_spot and spot.get("transit_est_mins", 0) > 0:
            reasons.append(
                f"Only {spot['transit_est_mins']} mins drive ({spot.get('transit_from_prev_km', 0)} km) from {prev_spot.get('name', 'previous stop')}."
            )

        if is_hidden_gem:
            reasons.append("Anti-overtourism hidden gem with low congestion.")

        if is_sme:
            partner = spot.get("local_partner_name", "local hosts")
            share = spot.get("local_revenue_share_pct", 85)
            reasons.append(f"Directs {share}% of local spending to {partner}.")

        if cost_bdt == 0.0:
            reasons.append("Free entry keeps shared expenses low.")
        else:
            reasons.append(f"Entry fee ~৳{int(cost_bdt)} fits group budget constraints.")

        return {
            "badges": badges[:6],
            "narrative": " ".join(reasons),
            "interested_members": interested_members,
            "member_match_ratio": f"{len(interested_members)}/{total_members}",
            "indoor_outdoor": spot.get("indoor_outdoor", "Outdoor"),
            "is_hidden_gem": is_hidden_gem,
            "feature_attributions": spot.get("feature_attributions"),
        }
