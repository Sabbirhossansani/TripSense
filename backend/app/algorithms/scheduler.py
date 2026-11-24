from typing import List, Dict, Any
from app.algorithms.optimizer import TSPOptimizer, haversine_distance
from app.algorithms.explainability import ExplainabilityGenerator

class ItineraryScheduler:
    """
    Day-by-Day Itinerary Generator & Time Allocation Engine.
    Divides spots into daily slots (Morning, Afternoon, Evening) based on pace,
    calculates transit times using 2-Opt TSP optimization, and attaches
    Explainability metadata for group members.
    """

    PACE_MAP = {
        "Relaxed": 2,
        "Moderate": 3,
        "High Efficiency": 4
    }

    TIME_SLOTS = [
        "Morning (09:00 AM - 12:00 PM)",
        "Afternoon (01:30 PM - 05:00 PM)",
        "Evening (06:30 PM - 09:30 PM)"
    ]

    def __init__(self, recommender_spots: List[Dict[str, Any]]):
        self.spots = recommender_spots

    def generate_itinerary(
        self,
        days: int,
        pace: str = "Moderate",
        total_budget: float = 1000.0,
        members: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        spots_per_day = self.PACE_MAP.get(pace, 3)
        total_needed_spots = min(len(self.spots), days * spots_per_day)
        selected_spots = self.spots[:total_needed_spots]

        # Optimize overall sequence using TSP 2-Opt
        optimized_spots = TSPOptimizer.optimize_2opt(selected_spots)

        daily_itinerary = []
        spot_index = 0
        total_trip_cost_usd = 0.0
        total_trip_cost_bdt = 0.0
        total_trip_distance_km = 0.0

        for day in range(1, days + 1):
            day_spots = []
            day_cost_usd = 0.0
            day_cost_bdt = 0.0
            day_distance = 0.0

            # Allocate spots for the day
            slots_for_today = min(spots_per_day, len(optimized_spots) - spot_index)

            for slot_idx in range(slots_for_today):
                if spot_index >= len(optimized_spots):
                    break

                spot = dict(optimized_spots[spot_index])
                time_slot = self.TIME_SLOTS[slot_idx % len(self.TIME_SLOTS)]
                spot["scheduled_slot"] = time_slot

                # Calculate transit distance from previous spot if any
                prev_spot = day_spots[-1] if day_spots else None
                if prev_spot:
                    dist = haversine_distance(
                        prev_spot["latitude"], prev_spot["longitude"],
                        spot["latitude"], spot["longitude"]
                    )
                    spot["transit_from_prev_km"] = round(dist, 2)
                    spot["transit_est_mins"] = round((dist / 30.0) * 60)  # Assume avg 30 km/h city speed
                    day_distance += dist
                else:
                    spot["transit_from_prev_km"] = 0.0
                    spot["transit_est_mins"] = 0

                # Generate explainability
                if members:
                    spot["why_this"] = ExplainabilityGenerator.generate_explanation(
                        spot, members, prev_spot=prev_spot
                    )

                cost_usd = spot.get("estimated_cost_usd", 0.0)
                cost_bdt = spot.get("estimated_cost_bdt", cost_usd * 115.0)

                day_cost_usd += cost_usd
                day_cost_bdt += cost_bdt
                day_spots.append(spot)
                spot_index += 1

            total_trip_cost_usd += day_cost_usd
            total_trip_cost_bdt += day_cost_bdt
            total_trip_distance_km += day_distance

            daily_itinerary.append({
                "day": day,
                "title": f"Day {day}: Exploring Key Attractions",
                "spots": day_spots,
                "daily_cost_bdt": round(day_cost_bdt, 2),
                "daily_cost_usd": round(day_cost_usd, 2),
                "daily_distance_km": round(day_distance, 2)
            })

        return {
            "total_days": days,
            "pace": pace,
            "total_estimated_cost_bdt": round(total_trip_cost_bdt, 2),
            "total_estimated_cost_usd": round(total_trip_cost_usd, 2),
            "total_distance_km": round(total_trip_distance_km, 2),
            "daily_schedule": daily_itinerary
        }
