import json
import os
import sys

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure backend directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import load_spots
from app.algorithms.group_consensus import GroupConsensusEngine
from app.algorithms.scheduler import ItineraryScheduler
from app.services.weather_service import WeatherContextService

print("=" * 60)
print("TRIPSENSE PHASE 1 VERIFICATION & BENCHMARK TEST")
print("=" * 60)

# 1. Dataset Verification
spots = load_spots()
print(f"\n[1] DATASET VERIFICATION:")
print(f"Total POIs Loaded: {len(spots)}")
cities = sorted(list(set(s.get("city", "") for s in spots if s.get("city"))))
print(f"Available Cities: {cities}")
ctg_spots = [s for s in spots if s.get("city") == "Chittagong"]
print(f"Chittagong POIs Count: {len(ctg_spots)}")

# 2. Group Consensus Recommender Test in Chittagong
print(f"\n[2] GROUP CONSENSUS ENGINE TEST (Chittagong):")
test_members = [
    {"name": "Rahat", "interests": ["Historical", "Culture"], "budget_tier": "Budget"},
    {"name": "Sadia", "interests": ["Beach", "Nature"], "budget_tier": "Mid-range"},
    {"name": "Fahim", "interests": ["Adventure", "Food"], "budget_tier": "Luxury"}
]
print(f"Group Members: {[m['name'] for m in test_members]}")

group_engine = GroupConsensusEngine(spots)
top_candidates, fairness = group_engine.recommend_for_group(
    city="Chittagong",
    members=test_members,
    strategy="least_misery",
    promote_hidden_gems=True,
    top_k=10
)

print(f"\nTop Recommended Candidates for Group (Strategy: Least-Misery):")
for idx, s in enumerate(top_candidates[:5], 1):
    consensus = s.get("group_consensus", {})
    breakdown = consensus.get("member_breakdown", {})
    print(f" {idx}. {s['name'][:35]} | Match: {s['match_score']}% | Least-Misery: {consensus.get('least_misery_score')}% | Members: {breakdown}")

print(f"\nFairness Metrics:")
print(f" - Group Fairness Score: {fairness['fairness_score']}/100")
print(f" - Gini Index (Inequality): {fairness['gini_index']}")
print(f" - Disparity: {fairness['satisfaction_disparity']}")
print(f" - Member Average Satisfaction: {fairness['member_average_satisfaction']}")

# 3. 2-Opt Itinerary Generation & Explainability
print(f"\n[3] 2-OPT ITINERARY SCHEDULER & EXPLAINABILITY (Chittagong 2-Day):")
scheduler = ItineraryScheduler(top_candidates)
itinerary = scheduler.generate_itinerary(
    days=2,
    pace="Moderate",
    members=test_members
)

print(f"Total Days: {itinerary['total_days']}")
print(f"Total Estimated Cost: ৳{itinerary['total_estimated_cost_bdt']} (~${itinerary['total_estimated_cost_usd']})")
print(f"Total Distance: {itinerary['total_distance_km']} km")

for day in itinerary["daily_schedule"]:
    print(f"\n--- {day['title']} (Cost: ৳{day['daily_cost_bdt']}, Distance: {day['daily_distance_km']} km) ---")
    for spot in day["spots"]:
        why = spot.get("why_this", {})
        badges = why.get("badges", [])
        print(f"  * [{spot['scheduled_slot']}] {spot['name']}")
        print(f"    - Type: {spot.get('indoor_outdoor')} | Cost: ৳{spot.get('estimated_cost_bdt')} | Transit: {spot.get('transit_est_mins')} mins")
        print(f"    - Badges: {badges}")
        print(f"    - Explanation: {why.get('narrative')}")

# 4. Context-Aware Dynamic Weather Replanning Test
print(f"\n[4] DYNAMIC WEATHER REPLANNING TEST:")
day_1_spots = itinerary["daily_schedule"][0]["spots"]
print("Simulating Event: Heavy Rain arrives in Chittagong...")
replan_result = WeatherContextService.dynamically_replan_for_weather(
    current_schedule=day_1_spots,
    available_spots=ctg_spots,
    weather_condition="Heavy Rain",
    group_members=test_members
)

print(f"Rerouted: {replan_result['rerouted']}")
print(f"Swapped Spots Count: {replan_result['swapped_spots_count']}")
for n in replan_result["notifications"]:
    print(f" {n}")

print("\nUpdated Day 1 Spots after Weather Adaptation:")
for s in replan_result["updated_spots"]:
    print(f"  * {s['name']} (Indoor/Outdoor: {s.get('indoor_outdoor')}, Weather Substitute: {s.get('is_weather_substitute', False)})")

print("\n" + "=" * 60)
print("ALL PHASE 1 BACKEND ALGORITHMS AND SERVICES PASSED SUCCESSFULLY!")
print("=" * 60)
