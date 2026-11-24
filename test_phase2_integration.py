"""
TripSense Phase 2 End-to-End Integration Test
Verifies:
1. Backend API endpoints (health, destinations, spots, group consensus planning, weather replanning)
2. Frontend build artifacts (dist/index.html, dist/assets bundle)
3. FastAPI static mounting & SPA fallback
"""

import sys
import os
import json
from fastapi.testclient import TestClient

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add backend directory to sys.path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_dir)

from app.main import app

client = TestClient(app)

print("=" * 65)
print("TRIPSENSE PHASE 2 FULL-STACK INTEGRATION & VERIFICATION TEST")
print("=" * 65)

# Test 1: Health Check
print("\n[TEST 1] Testing GET /health...")
res = client.get("/health")
assert res.status_code == 200, f"Expected 200, got {res.status_code}"
data = res.json()
print("  ✓ Status:", data["status"])
print("  ✓ Service:", data["service"])
print("  ✓ Version:", data["version"])
print("  ✓ Total Spots:", data["total_spots_loaded"])
assert "Chittagong" in data["available_cities"]
print("  ✓ Chittagong verified in available cities!")

# Test 2: Destinations
print("\n[TEST 2] Testing GET /api/destinations...")
res = client.get("/api/destinations")
assert res.status_code == 200
destinations = res.json()
print(f"  ✓ {len(destinations)} destinations available: {destinations}")
assert "Chittagong" in destinations
assert "Sylhet" in destinations

# Test 3: Spots Query
print("\n[TEST 3] Testing GET /api/spots?city=Chittagong...")
res = client.get("/api/spots?city=Chittagong")
assert res.status_code == 200
spots = res.json()
print(f"  ✓ Retrieved {len(spots)} Chittagong POIs:")
for s in spots[:3]:
    print(f"    - {s['name']} (Cat: {s['category']}, Cost: ৳{s.get('estimated_cost_bdt')}, In/Out: {s.get('indoor_outdoor')})")

# Test 4: Group Travel Plan Generation (Least-Misery Consensus)
print("\n[TEST 4] Testing POST /api/group/generate-plan (Group Consensus & 2-Opt TSP)...")
group_payload = {
    "city": "Chittagong",
    "days": 3,
    "pace": "Moderate",
    "members": [
        {"name": "Rahat", "interests": ["Historical", "Culture"], "budget_tier": "Budget"},
        {"name": "Sadia", "interests": ["Beach", "Nature"], "budget_tier": "Mid-range"},
        {"name": "Fahim", "interests": ["Adventure", "Food"], "budget_tier": "Luxury"}
    ],
    "consensus_strategy": "least_misery",
    "promote_hidden_gems": True
}
res = client.post("/api/group/generate-plan", json=group_payload)
assert res.status_code == 200, f"Generate plan failed: {res.text}"
plan = res.json()
print("  ✓ Total Days:", plan["total_days"])
print("  ✓ Total Estimated Cost: ৳", plan["total_estimated_cost_bdt"])
print("  ✓ Total Distance: ", plan["total_distance_km"], "km")
print("  ✓ Fairness Score: ", plan["fairness_report"]["fairness_score"], "/ 100")
print("  ✓ Gini Index: ", plan["fairness_report"]["gini_index"])
print("  ✓ Disparity: ", plan["fairness_report"]["satisfaction_disparity"])
print("  ✓ Daily Schedule count: ", len(plan["daily_schedule"]))

# Verify Explainability badges
first_spot = plan["daily_schedule"][0]["spots"][0]
assert "why_this" in first_spot, "Explainability why_this missing"
print(f"  ✓ First Spot: '{first_spot['name']}'")
print(f"  ✓ Explainability Badges: {first_spot['why_this']['badges']}")
print(f"  ✓ Narrative: {first_spot['why_this']['narrative'][:80]}...")

# Test 5: Dynamic Weather Replanning
print("\n[TEST 5] Testing POST /api/itinerary/replan-weather (Context Engine Rain Swap)...")
day1_spots = plan["daily_schedule"][0]["spots"]
weather_payload = {
    "city": "Chittagong",
    "weather_condition": "Heavy Rain",
    "members": group_payload["members"],
    "current_spots": day1_spots
}
res = client.post("/api/itinerary/replan-weather", json=weather_payload)
assert res.status_code == 200, f"Weather replan failed: {res.text}"
weather_result = res.json()
print("  ✓ Rerouted:", weather_result["rerouted"])
print("  ✓ Swapped Spots Count:", weather_result["swapped_spots_count"])
print("  ✓ Notifications:")
for notif in weather_result["notifications"]:
    print(f"    {notif}")

# Test 5b: Veto Token Spot Swapping
print("\n[TEST 5b] Testing POST /api/itinerary/veto-spot (Veto Token Swap)...")
veto_target_spot = day1_spots[0]
veto_payload = {
    "city": "Chittagong",
    "spot_id": veto_target_spot["id"],
    "vetoed_by": "Sadia",
    "members": group_payload["members"],
    "current_spots": day1_spots
}
res = client.post("/api/itinerary/veto-spot", json=veto_payload)
assert res.status_code == 200, f"Veto spot failed: {res.text}"
veto_result = res.json()
print("  ✓ Veto Success:", veto_result["success"])
print("  ✓ Vetoed By:", veto_result["vetoed_by"])
print("  ✓ Original Spot:", veto_result["original_spot_name"])
if veto_result["substitute_spot"]:
    print("  ✓ Substituted With:", veto_result["substitute_spot"]["name"])
print("  ✓ Notification:", veto_result["notification"])
assert len(veto_result["updated_spots"]) == len(day1_spots)
print("  ✓ Updated schedule length preserved successfully!")

# Test 6: Frontend Dist & SPA Fallback Serving
print("\n[TEST 6] Testing Frontend Client SPA Serving via FastAPI...")
res = client.get("/")
assert res.status_code == 200, f"Expected 200 from root SPA, got {res.status_code}"
assert "<title>TripSense — Editorial Group Adventure & Eco Travel Planner</title>" in res.text
print("  ✓ Root index.html successfully served with correct title!")

# Test client route fallback
res = client.get("/room/CTG-882")
assert res.status_code == 200
assert "<div id=\"root\"></div>" in res.text
print("  ✓ SPA route fallback (/room/CTG-882) successfully served index.html!")

print("\n" + "=" * 65)
print("ALL PHASE 2 FULL-STACK INTEGRATION TESTS PASSED SUCCESSFULLY! 🚀")
print("=" * 65)
