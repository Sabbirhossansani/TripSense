from typing import List, Dict, Any
from app.algorithms.optimizer import haversine_distance
from app.algorithms.explainability import ExplainabilityGenerator

class WeatherContextService:
    """
    Academic Context-Aware Dynamic Replanning Service.
    Monitors weather state (Rain, Storm, Sunny) and automatically adjusts
    daily schedules by substituting compromised Outdoor spots with optimal Indoor POIs.
    """

    ADVERSE_CONDITIONS = ["Rain", "Thunderstorm", "Heavy Rain", "Drizzle"]

    @classmethod
    def is_adverse_weather(cls, condition: str) -> bool:
        return any(c.lower() in condition.lower() for c in cls.ADVERSE_CONDITIONS)

    @classmethod
    def dynamically_replan_for_weather(
        cls,
        current_schedule: List[Dict[str, Any]],
        available_spots: List[Dict[str, Any]],
        weather_condition: str,
        group_members: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Scans today's schedule for Outdoor spots if adverse weather occurs.
        Swaps affected spots with the closest high-rated Indoor attraction.
        """
        if not cls.is_adverse_weather(weather_condition):
            return {
                "rerouted": False,
                "message": f"Weather is {weather_condition}. No itinerary changes required.",
                "updated_spots": current_schedule,
                "swapped_spots_count": 0
            }

        # Available indoor candidates not already in current schedule
        scheduled_ids = {s["id"] for s in current_schedule}
        indoor_candidates = [
            s for s in available_spots
            if s.get("indoor_outdoor") == "Indoor" and s["id"] not in scheduled_ids
        ]

        updated_schedule = []
        notifications = []
        swapped_count = 0

        for spot in current_schedule:
            if spot.get("indoor_outdoor") == "Outdoor" and indoor_candidates:
                # Find closest indoor candidate
                closest_indoor = min(
                    indoor_candidates,
                    key=lambda cand: haversine_distance(
                        spot["latitude"], spot["longitude"],
                        cand["latitude"], cand["longitude"]
                    )
                )

                # Prepare replacement spot
                substitute = dict(closest_indoor)
                substitute["scheduled_slot"] = spot.get("scheduled_slot", "Afternoon")
                substitute["is_weather_substitute"] = True

                # Compute group consensus breakdown and match score for substitute
                from app.algorithms.group_consensus import GroupConsensusEngine
                engine = GroupConsensusEngine([closest_indoor])
                member_scores = {}
                for m in group_members:
                    member_scores[m["name"]] = engine.compute_individual_score(m, closest_indoor)
                scores_list = list(member_scores.values())
                avg_score = sum(scores_list) / len(scores_list) if scores_list else 0.5
                min_score = min(scores_list) if scores_list else 0.5

                substitute["match_score"] = round(((0.60 * min_score) + (0.40 * avg_score)) * 100, 2)
                substitute["group_consensus"] = {
                    "avg_score": round(avg_score * 100, 1),
                    "least_misery_score": round(min_score * 100, 1),
                    "member_breakdown": {k: round(v * 100, 1) for k, v in member_scores.items()}
                }

                # Generate updated explainability with weather badge
                prev_spot = updated_schedule[-1] if updated_schedule else None
                substitute["why_this"] = ExplainabilityGenerator.generate_explanation(
                    substitute, group_members, prev_spot=prev_spot, is_weather_substitute=True
                )

                notifications.append(
                    f"⚠️ Rain Alert: Substituted outdoor spot '{spot['name']}' with indoor landmark '{substitute['name']}'."
                )
                updated_schedule.append(substitute)
                indoor_candidates.remove(closest_indoor)
                swapped_count += 1
            else:
                updated_schedule.append(spot)

        # Recalculate transit distance & time between all consecutive spots
        for idx in range(len(updated_schedule)):
            if idx == 0:
                updated_schedule[idx]["transit_from_prev_km"] = 0.0
                updated_schedule[idx]["transit_est_mins"] = 0
            else:
                p_spot = updated_schedule[idx - 1]
                c_spot = updated_schedule[idx]
                dist = haversine_distance(
                    p_spot["latitude"], p_spot["longitude"],
                    c_spot["latitude"], c_spot["longitude"]
                )
                c_spot["transit_from_prev_km"] = round(dist, 2)
                c_spot["transit_est_mins"] = round((dist / 30.0) * 60)

        return {
            "rerouted": swapped_count > 0,
            "weather_condition": weather_condition,
            "swapped_spots_count": swapped_count,
            "notifications": notifications,
            "updated_spots": updated_schedule
        }
