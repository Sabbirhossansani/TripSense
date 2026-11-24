"""
Comprehensive Automated Verification Suite for TripSense Blueprint B ML,
Neuro-Symbolic RAG Copilot, Business & Sustainability Suite, and API Endpoints.
"""

import os
import sys
import json
from fastapi.testclient import TestClient

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, BACKEND_DIR)

from backend.app.main import app, load_spots

client = TestClient(app)


def test_all_blueprint_b():
    print("=" * 70)
    print("TRIPSENSE BLUEPRINT B ML & BUSINESS SUITE VERIFICATION")
    print("=" * 70)

    # 1. Health & Loaded Dataset (40+ BD POIs + Global POIs)
    r_health = client.get("/health")
    assert r_health.status_code == 200
    h = r_health.json()
    print(f"\n[TEST 1] /health: status={h['status']}, fairnet_loaded={h['fairnet_loaded']}, backbone={h['backbone']}, total_spots={h['total_spots_loaded']}")
    assert h["status"] == "healthy"
    assert h["total_spots_loaded"] >= 50
    assert "Bandarban" in h["available_cities"]

    # 2. FairNet Group Plan Generation + Eco Telemetry
    members = [
        {"name": "Rahat", "interests": ["Historical", "Culture"], "budget_tier": "Budget"},
        {"name": "Sadia", "interests": ["Beach", "Nature"], "budget_tier": "Mid-range"},
        {"name": "Fahim", "interests": ["Adventure", "Food"], "budget_tier": "Luxury"},
    ]
    r_plan = client.post("/api/group/generate-plan", json={
        "city": "Chittagong",
        "days": 3,
        "pace": "Moderate",
        "members": members,
        "consensus_strategy": "fairnet",
        "promote_hidden_gems": True,
    })
    assert r_plan.status_code == 200
    plan = r_plan.json()
    print(f"\n[TEST 2] FairNet Plan: model={plan['fairness_report'].get('model_used')}, fairness={plan['fairness_report']['fairness_score']}, gini={plan['fairness_report']['gini_index']}")
    print(f"         Eco Summary: co2_saved={plan['eco_summary']['co2_saved_kg']}kg, sme_ratio={plan['eco_summary']['local_sme_ratio_pct']}%, eco_pts={plan['eco_summary']['total_eco_points']}")
    assert len(plan["daily_schedule"]) == 3
    assert plan["eco_summary"]["co2_saved_kg"] >= 0

    # 3. Active Bayesian Swipe Endpoint
    r_sw0 = client.post("/api/ml/swipe/next", json={"history": [], "max_cards": 6})
    assert r_sw0.status_code == 200
    sw0 = r_sw0.json()
    assert sw0["completed"] is False and sw0["next_card"] is not None

    c1_id = sw0["next_card"]["id"]
    r_sw1 = client.post("/api/ml/swipe/next", json={
        "history": [{"card_id": c1_id, "action": "like"}],
        "max_cards": 6,
    })
    assert r_sw1.status_code == 200
    sw1 = r_sw1.json()
    assert sw1["confidence_pct"] > sw0["confidence_pct"]
    assert sw1["next_card"]["id"] != c1_id
    print(f"\n[TEST 3] Active Swipe Bayesian EIG: step 0 conf={sw0['confidence_pct']}% -> step 1 conf={sw1['confidence_pct']}% (next={sw1['next_card']['id']})")

    # 4. Nash-Bargaining Veto Token Endpoint (No cross-day duplicates)
    all_trip_ids = [s["id"] for d in plan["daily_schedule"] for s in d["spots"]]
    day1_spots = plan["daily_schedule"][0]["spots"]
    target_spot = day1_spots[0]
    r_veto = client.post("/api/itinerary/veto-spot", json={
        "city": "Chittagong",
        "spot_id": target_spot["id"],
        "vetoed_by": "Fahim",
        "members": members,
        "current_spots": day1_spots,
        "all_scheduled_spot_ids": all_trip_ids,
    })
    assert r_veto.status_code == 200
    v_res = r_veto.json()
    assert v_res["success"] is True
    assert v_res["substitute_spot"]["id"] not in all_trip_ids
    print(f"\n[TEST 4] Nash Veto Swap: '{target_spot['name']}' -> '{v_res['substitute_spot']['name']}' (Welfare Δ={v_res['nash_welfare_gain']:+.1f}%)")
    print(f"         Counterfactual: {v_res['counterfactual_reason']}")

    # 5. Neuro-Symbolic RAG Copilot (Banglish + English)
    r_chat = client.post("/api/copilot/chat", json={
        "query": "Bristi hole Chittagong e indoor kothay jawa jay?",
        "city": "Chittagong",
        "members": members,
        "expenses_total_bdt": 2250,
    })
    assert r_chat.status_code == 200
    chat = r_chat.json()
    assert chat["verified"] is True
    assert chat["hallucination_checks_passed"] >= 4
    assert len(chat["grounded_sources"]) >= 1
    print(f"\n[TEST 5] Neuro-Symbolic Copilot: verified={chat['verified']}, checks={chat['hallucination_checks_passed']}, provider={chat['provider_used']}")
    print(f"         Answer: {chat['answer'][:120]}...")

    # 6. Sustainability Eco-Report & Group Booking Voucher Endpoints
    r_eco = client.post("/api/sustainability/eco-report", json={
        "spots": day1_spots,
        "group_size": 4,
        "transport_mode": "ev_cng",
        "total_distance_km": 16.5,
    })
    assert r_eco.status_code == 200
    eco = r_eco.json()
    assert eco["co2_saved_kg"] > 0

    r_book = client.post("/api/bookings/reserve", json={
        "spot_id": day1_spots[0]["id"],
        "spot_name": day1_spots[0]["name"],
        "city": "Chittagong",
        "date": "2026-08-12",
        "time_slot": "Morning (09:00 AM - 12:00 PM)",
        "group_size": 4,
        "lead_name": "Sadia",
        "lead_contact": "+8801711000000",
        "eco_pledge": True,
        "redeem_eco_points": 100,
        "unit_cost_bdt": 200.0,
    })
    assert r_book.status_code == 200
    bk = r_book.json()
    assert bk["status"] == "CONFIRMED"
    assert bk["voucher_code"].startswith("TS-BD-")
    assert bk["group_discount_pct"] >= 15
    print(f"\n[TEST 6] Eco & Booking API: CO2 saved={eco['co2_saved_kg']}kg | Voucher={bk['voucher_code']} (Final=৳{bk['final_total_bdt']}, SME Rev=৳{bk['local_sme_revenue_bdt']})")

    # 7. Q1 Metrics Artifact Endpoint
    r_metrics = client.get("/api/ml/metrics")
    assert r_metrics.status_code == 200
    metrics = r_metrics.json()
    assert "group_consensus_comparison" in metrics, "q1_benchmark_results.json must be populated!"
    print(f"\n[TEST 7] Q1 Benchmark Metrics Endpoint: backbone={metrics['backbone']}, models={len(metrics['group_consensus_comparison'])}")

    print("\n" + "=" * 70)
    print("ALL BLUEPRINT B ML, NEURO-SYMBOLIC & BUSINESS TESTS PASSED! ✓")
    print("=" * 70)


if __name__ == "__main__":
    test_all_blueprint_b()
