import json
import os
import sys
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is importable when running uvicorn from backend/ or root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.schemas import (
    TravelPlanRequest,
    TravelPlanResponse,
    SpotResponse,
    GroupTravelPlanRequest,
    GroupTravelPlanResponse,
    WeatherReplanRequest,
    WeatherReplanResponse,
    VetoSpotRequest,
    VetoSpotResponse,
    ActiveSwipeRequest,
    ActiveSwipeResponse,
    CopilotChatRequest,
    CopilotChatResponse,
    EcoReportRequest,
    BookingReserveRequest,
    BookingReserveResponse,
)
from app.algorithms.recommender import ContentBasedRecommender
from app.algorithms.group_consensus import GroupConsensusEngine
from app.algorithms.scheduler import ItineraryScheduler
from app.services.weather_service import WeatherContextService
from app.services.eco_service import EcoBusinessService

from backend.ml.active_swipe import ActiveSwipeEngine
from backend.ml.nash_veto import NashVetoEngine
from backend.ml.rag_copilot import NeuroSymbolicCopilot
from backend.ml.inference import get_fairnet_inference

app = FastAPI(
    title="TripSense: FairNet Neural Consensus, Neuro-Symbolic RAG & Sustainable Travel API",
    description="Q1 Blueprint B Backend - TripSense-FairNet (SigLIP + Cross-Attention), Active Bayesian Swipe, Nash Veto, & Neuro-Symbolic Copilot",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BD_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "bangladesh_spots.json")
GLOBAL_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "global_spots.json")
METRICS_PATH = os.path.join(PROJECT_ROOT, "backend", "ml", "artifacts", "q1_benchmark_results.json")

_SWIPE_ENGINE = None
_COPILOT_ENGINE = None


def load_spots() -> List[dict]:
    """
    Loads unified dataset combining verified Bangladesh pilot data
    and international benchmark destinations with business & eco defaults.
    """
    combined = []
    seen_ids = set()

    for path in [BD_DATA_PATH, GLOBAL_DATA_PATH]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    spots = json.load(f)
                    for s in spots:
                        if s["id"] not in seen_ids:
                            s.setdefault("estimated_cost_bdt", round(s.get("estimated_cost_usd", 0.0) * 115.0, 1))
                            s.setdefault("indoor_outdoor", "Outdoor")
                            s.setdefault("crowd_level", "Medium")
                            s.setdefault("hidden_gem", False)
                            s.setdefault("opening_hour", "08:00")
                            s.setdefault("closing_hour", "20:00")
                            s.setdefault("best_time", "Anytime")
                            s.setdefault("co2_kg_base", 1.8 if s.get("indoor_outdoor") == "Outdoor" else 0.9)
                            s.setdefault("sustainability_score", 86 if s.get("hidden_gem") else 74)
                            s.setdefault("local_sme", bool(s.get("hidden_gem", False)))
                            s.setdefault("local_partner_name", f"{s.get('city', 'Local')} Heritage & Eco Guild")
                            s.setdefault("local_revenue_share_pct", 85 if s.get("local_sme") else 55)
                            s.setdefault("eco_points_reward", 90 if s.get("hidden_gem") else 55)
                            s.setdefault("group_discount_pct", 15 if s.get("estimated_cost_bdt", 0) > 100 else 10)
                            s.setdefault("bookable", True)
                            s.setdefault("tags", [s.get("category", "Travel").lower(), s.get("city", "").lower()])
                            combined.append(s)
                            seen_ids.add(s["id"])
            except Exception as e:
                print(f"Error loading {path}: {e}")

    return combined


def get_swipe_engine() -> ActiveSwipeEngine:
    global _SWIPE_ENGINE
    if _SWIPE_ENGINE is None:
        _SWIPE_ENGINE = ActiveSwipeEngine()
    return _SWIPE_ENGINE


def get_copilot_engine() -> NeuroSymbolicCopilot:
    global _COPILOT_ENGINE
    if _COPILOT_ENGINE is None:
        _COPILOT_ENGINE = NeuroSymbolicCopilot(load_spots())
    return _COPILOT_ENGINE


@app.get("/health")
def health_check():
    spots = load_spots()
    cities = sorted(list(set(s.get("city", "") for s in spots if s.get("city"))))
    infer = get_fairnet_inference()
    return {
        "status": "healthy",
        "service": "TripSense FairNet + Neuro-Symbolic API",
        "version": "3.0.0",
        "fairnet_loaded": infer.loaded_real_model,
        "backbone": infer.backbone_name,
        "total_spots_loaded": len(spots),
        "available_cities": cities,
    }


@app.get("/api/destinations", response_model=List[str])
def get_available_destinations():
    spots = load_spots()
    cities = sorted(list(set(spot["city"] for spot in spots if "city" in spot)))
    return cities


@app.get("/api/spots", response_model=List[SpotResponse])
def get_spots_by_city(city: str = Query(..., description="City name e.g. Chittagong, Bandarban, Sylhet, Cox's Bazar, Dhaka")):
    spots = load_spots()
    filtered = [s for s in spots if s.get("city", "").lower() == city.lower()]
    if not filtered:
        raise HTTPException(status_code=404, detail=f"No attractions found for city '{city}'")
    return filtered


@app.post("/api/generate-itinerary", response_model=TravelPlanResponse)
def generate_single_user_itinerary(request: TravelPlanRequest):
    all_spots = load_spots()
    if not all_spots:
        raise HTTPException(status_code=500, detail="Destinations dataset is missing.")

    recommender = ContentBasedRecommender(all_spots)
    recommended_spots = recommender.recommend(
        city=request.city,
        user_interests=request.interests,
        budget_tier=request.budget_tier,
        top_k=20
    )

    if not recommended_spots:
        raise HTTPException(status_code=404, detail=f"No matching attractions found for city '{request.city}'")

    scheduler = ItineraryScheduler(recommended_spots)
    itinerary = scheduler.generate_itinerary(
        days=request.days,
        pace=request.pace,
        total_budget=request.total_budget_usd
    )

    return {
        "city": request.city,
        "total_days": itinerary["total_days"],
        "pace": itinerary["pace"],
        "total_estimated_cost_usd": itinerary["total_estimated_cost_usd"],
        "total_distance_km": itinerary["total_distance_km"],
        "daily_schedule": itinerary["daily_schedule"]
    }


@app.post("/api/group/generate-plan", response_model=GroupTravelPlanResponse)
def generate_group_travel_plan(request: GroupTravelPlanRequest):
    """
    Core Q1 Novelty: TripSense-FairNet Neural Group Consensus (or Least-Misery / Average)
    + 2-Opt TSP Route Optimization + XAI Feature Attributions + Sustainability Telemetry.
    """
    all_spots = load_spots()
    if not all_spots:
        raise HTTPException(status_code=500, detail="Destinations dataset is missing.")

    members_data = [m.model_dump() for m in request.members]

    group_engine = GroupConsensusEngine(all_spots)
    top_candidates, fairness_report = group_engine.recommend_for_group(
        city=request.city,
        members=members_data,
        strategy=request.consensus_strategy,
        promote_hidden_gems=request.promote_hidden_gems,
        top_k=25
    )

    if not top_candidates:
        raise HTTPException(status_code=404, detail=f"No attractions found for city '{request.city}'")

    scheduler = ItineraryScheduler(top_candidates)
    itinerary = scheduler.generate_itinerary(
        days=request.days,
        pace=request.pace,
        members=members_data
    )

    scheduled_spots = [s for d in itinerary["daily_schedule"] for s in d["spots"]]
    eco_summary = EcoBusinessService.compute_trip_eco_summary(
        all_spots=scheduled_spots,
        total_distance_km=itinerary["total_distance_km"],
        group_size=max(1, len(members_data)),
        transport_mode="shared_microbus",
    )

    return {
        "city": request.city,
        "total_days": itinerary["total_days"],
        "pace": itinerary["pace"],
        "consensus_strategy": request.consensus_strategy,
        "total_estimated_cost_bdt": itinerary["total_estimated_cost_bdt"],
        "total_estimated_cost_usd": itinerary["total_estimated_cost_usd"],
        "total_distance_km": itinerary["total_distance_km"],
        "fairness_report": fairness_report,
        "eco_summary": eco_summary,
        "daily_schedule": itinerary["daily_schedule"]
    }


@app.post("/api/itinerary/replan-weather", response_model=WeatherReplanResponse)
def replan_itinerary_for_weather(request: WeatherReplanRequest):
    all_spots = load_spots()
    city_spots = [s for s in all_spots if s.get("city", "").lower() == request.city.lower()]
    current_spots_data = [s.model_dump() for s in request.current_spots]
    members_data = [m.model_dump() for m in request.members]

    excluded_ids = set()
    if request.all_scheduled_spot_ids:
        current_day_ids = {s["id"] for s in current_spots_data}
        excluded_ids = set(request.all_scheduled_spot_ids) - current_day_ids

    available_filtered = [s for s in city_spots if s["id"] not in excluded_ids]

    return WeatherContextService.dynamically_replan_for_weather(
        current_schedule=current_spots_data,
        available_spots=available_filtered,
        weather_condition=request.weather_condition,
        group_members=members_data
    )


@app.post("/api/itinerary/veto-spot", response_model=VetoSpotResponse)
def veto_spot_and_replan(request: VetoSpotRequest):
    """
    Nash-Bargaining Counterfactual Critique Veto Engine.
    """
    all_spots = load_spots()
    city_spots = [s for s in all_spots if s.get("city", "").lower() == request.city.lower()]
    current_spots = [s.model_dump() for s in request.current_spots]
    members_data = [m.model_dump() for m in request.members]

    vetoed_spot_index = None
    vetoed_spot = None
    for idx, spot in enumerate(current_spots):
        if spot["id"] == request.spot_id:
            vetoed_spot_index = idx
            vetoed_spot = spot
            break

    if vetoed_spot_index is None or not vetoed_spot:
        raise HTTPException(status_code=404, detail=f"Spot with id {request.spot_id} not found in current schedule.")

    scheduled_ids = {s["id"] for s in current_spots}
    if request.all_scheduled_spot_ids:
        scheduled_ids.update(request.all_scheduled_spot_ids)

    candidate_spots = [s for s in city_spots if s["id"] not in scheduled_ids and s["id"] != request.spot_id]

    res = NashVetoEngine.resolve_veto(
        city=request.city,
        vetoed_spot=vetoed_spot,
        vetoed_spot_index=vetoed_spot_index,
        vetoed_by=request.vetoed_by,
        current_spots=current_spots,
        candidate_spots=candidate_spots,
        members=members_data,
    )

    if not res["success"]:
        return VetoSpotResponse(
            success=False,
            vetoed_by=request.vetoed_by,
            original_spot_name=vetoed_spot["name"],
            substitute_spot=None,
            notification=f"No alternative attractions remaining in {request.city} to substitute '{vetoed_spot['name']}'.",
            nash_welfare_gain=0.0,
            counterfactual_reason=res["counterfactual_reason"],
            updated_spots=request.current_spots
        )

    sub = res["substitute"]
    return VetoSpotResponse(
        success=True,
        vetoed_by=request.vetoed_by,
        original_spot_name=vetoed_spot["name"],
        substitute_spot=sub,
        notification=(
            f"🛡️ Nash Veto applied by {request.vetoed_by}: Replaced '{vetoed_spot['name'].split('(')[0].strip()}' "
            f"with '{sub['name'].split('(')[0].strip()}' (Welfare Δ {res['nash_welfare_gain']:+.1f}%)."
        ),
        nash_welfare_gain=res["nash_welfare_gain"],
        counterfactual_reason=res["counterfactual_reason"],
        updated_spots=res["updated_spots"]
    )


# --- Blueprint B ML, Neuro-Symbolic Copilot & Business/Eco Endpoints ---

@app.post("/api/ml/swipe/next", response_model=ActiveSwipeResponse)
def active_swipe_next(request: ActiveSwipeRequest):
    engine = get_swipe_engine()
    history_dicts = [h.model_dump() for h in request.history]
    return engine.step(history_dicts, max_cards=request.max_cards)


@app.get("/api/ml/metrics")
def get_ml_benchmark_metrics():
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"status": "training_pending", "message": "Run backend/ml/train_fairnet.py to populate Q1 benchmarks."}


@app.post("/api/copilot/chat", response_model=CopilotChatResponse)
def copilot_chat(request: CopilotChatRequest):
    copilot = get_copilot_engine()
    members_data = [m.model_dump() for m in request.members]
    return copilot.answer(
        query=request.query,
        city=request.city,
        members=members_data,
        plan_summary=request.plan_summary,
        expenses_total_bdt=request.expenses_total_bdt or 0.0,
    )


@app.post("/api/sustainability/eco-report")
def sustainability_eco_report(request: EcoReportRequest):
    spots_data = [s.model_dump() for s in request.spots]
    return EcoBusinessService.compute_trip_eco_summary(
        all_spots=spots_data,
        total_distance_km=request.total_distance_km,
        group_size=request.group_size,
        transport_mode=request.transport_mode,
    )


@app.post("/api/bookings/reserve", response_model=BookingReserveResponse)
def reserve_group_booking(request: BookingReserveRequest):
    all_spots = load_spots()
    spot = next((s for s in all_spots if s["id"] == request.spot_id), {"name": request.spot_name, "city": request.city})
    return EcoBusinessService.create_reservation(
        spot=spot,
        date=request.date,
        time_slot=request.time_slot,
        group_size=request.group_size,
        lead_name=request.lead_name,
        eco_pledge=request.eco_pledge,
        redeem_eco_points=request.redeem_eco_points,
        unit_cost_bdt=request.unit_cost_bdt,
    )


# Serve production frontend client bundle if built
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            raise HTTPException(status_code=404, detail="Not found")
        if full_path and full_path != "index.html":
            file_path = os.path.join(frontend_dist, full_path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return FileResponse(file_path)
        return FileResponse(
            os.path.join(frontend_dist, "index.html"),
            headers={"Cache-Control": "no-store, no-cache, must-revalidate", "Pragma": "no-cache"},
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
