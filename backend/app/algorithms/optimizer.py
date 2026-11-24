import math
from typing import List, Dict, Any, Tuple

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth in Kilometers.
    """
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class TSPOptimizer:
    """
    Traveling Salesperson Problem (TSP) Optimizer for Travel Itineraries.
    Uses Nearest Neighbor Initial Heuristic + 2-Opt Local Search Improvement
    to order attractions geographical to minimize total travel time & distance.
    """

    @staticmethod
    def nearest_neighbor_tour(spots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not spots:
            return []
        
        unvisited = spots.copy()
        tour = [unvisited.pop(0)]  # Start with first recommended spot

        while unvisited:
            current = tour[-1]
            nearest_spot = min(
                unvisited,
                key=lambda s: haversine_distance(
                    current["latitude"], current["longitude"],
                    s["latitude"], s["longitude"]
                )
            )
            tour.append(nearest_spot)
            unvisited.remove(nearest_spot)

        return tour

    @classmethod
    def _calculate_total_distance(cls, tour: List[Dict[str, Any]]) -> float:
        total = 0.0
        for i in range(len(tour) - 1):
            total += haversine_distance(
                tour[i]["latitude"], tour[i]["longitude"],
                tour[i+1]["latitude"], tour[i+1]["longitude"]
            )
        return total

    @classmethod
    def optimize_2opt(cls, spots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Applies 2-Opt local search refinement to eliminate route crossings.
        """
        if len(spots) <= 3:
            return cls.nearest_neighbor_tour(spots)

        tour = cls.nearest_neighbor_tour(spots)
        best_distance = cls._calculate_total_distance(tour)
        improved = True

        while improved:
            improved = False
            for i in range(1, len(tour) - 1):
                for j in range(i + 1, len(tour)):
                    # Reverse sub-tour between i and j
                    new_tour = tour[:i] + tour[i:j+1][::-1] + tour[j+1:]
                    new_distance = cls._calculate_total_distance(new_tour)

                    if new_distance < best_distance:
                        tour = new_tour
                        best_distance = new_distance
                        improved = True
                        break
                if improved:
                    break

        return tour
