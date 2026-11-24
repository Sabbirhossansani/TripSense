from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class UserProfile(BaseModel):
    name: str = Field(..., example="Rahat", description="Member name")
    interests: List[str] = Field(..., example=["Historical", "Culture"], description="Selected interest categories")
    budget_tier: Optional[str] = Field("Mid-range", example="Budget", description="Budget, Mid-range, or Luxury")
    taste_embedding: Optional[List[float]] = None

class TravelPlanRequest(BaseModel):
    city: str = Field(..., example="Chittagong", description="Target destination city")
    days: int = Field(3, ge=1, le=14, description="Duration of trip in days")
    budget_tier: str = Field("Mid-range", example="Mid-range", description="Budget, Mid-range, or Luxury")
    total_budget_usd: float = Field(1000.0, ge=50.0, description="Approximate total trip budget in USD")
    interests: List[str] = Field(["Historical", "Culture", "Food"], description="Selected interest tags")
    pace: str = Field("Moderate", example="Moderate", description="Relaxed, Moderate, or High Efficiency")

class GroupTravelPlanRequest(BaseModel):
    city: str = Field("Chittagong", example="Chittagong", description="Target destination city")
    days: int = Field(3, ge=1, le=14, description="Duration of trip in days")
    pace: str = Field("Moderate", example="Moderate", description="Relaxed, Moderate, or High Efficiency")
    members: List[UserProfile] = Field(..., description="List of all participating group members")
    consensus_strategy: str = Field("fairnet", example="fairnet", description="fairnet, least_misery, or average")
    promote_hidden_gems: bool = Field(True, description="Enable anti-overtourism boost for hidden gems")

class ExplanationDetails(BaseModel):
    badges: List[str] = []
    narrative: str = ""
    interested_members: List[str] = []
    member_match_ratio: str = ""
    indoor_outdoor: str = "Outdoor"
    is_hidden_gem: bool = False
    feature_attributions: Optional[Dict[str, float]] = None

class SpotResponse(BaseModel):
    id: int
    name: str
    city: str
    country: str
    category: str
    latitude: float
    longitude: float
    avg_visit_duration_hours: float
    estimated_cost_usd: float = 0.0
    estimated_cost_bdt: Optional[float] = 0.0
    rating: float
    description: str
    indoor_outdoor: Optional[str] = "Outdoor"
    crowd_level: Optional[str] = "Medium"
    hidden_gem: Optional[bool] = False
    opening_hour: Optional[str] = "08:00"
    closing_hour: Optional[str] = "20:00"
    best_time: Optional[str] = "Anytime"
    co2_kg_base: Optional[float] = 1.5
    sustainability_score: Optional[int] = 80
    local_sme: Optional[bool] = False
    local_partner_name: Optional[str] = "Local Community Host"
    local_revenue_share_pct: Optional[int] = 60
    eco_points_reward: Optional[int] = 60
    group_discount_pct: Optional[int] = 10
    bookable: Optional[bool] = True
    tags: Optional[List[str]] = []
    match_score: Optional[float] = 0.0
    scheduled_slot: Optional[str] = None
    transit_from_prev_km: Optional[float] = 0.0
    transit_est_mins: Optional[int] = 0
    is_weather_substitute: Optional[bool] = False
    why_this: Optional[ExplanationDetails] = None
    group_consensus: Optional[Dict[str, Any]] = None

class DailySchedule(BaseModel):
    day: int
    title: str
    spots: List[SpotResponse]
    daily_cost_bdt: float = 0.0
    daily_cost_usd: float = 0.0
    daily_distance_km: float = 0.0

class TravelPlanResponse(BaseModel):
    city: str
    total_days: int
    pace: str
    total_estimated_cost_usd: float
    total_distance_km: float
    daily_schedule: List[DailySchedule]

class GroupFairnessReport(BaseModel):
    fairness_score: float
    satisfaction_disparity: float
    gini_index: float
    member_average_satisfaction: Dict[str, float]
    model_used: Optional[str] = "TripSense-FairNet"

class EcoTripSummary(BaseModel):
    total_co2_kg: float
    standard_car_co2_kg: float
    co2_saved_kg: float
    trees_equivalent: float
    avg_sustainability_score: float
    local_sme_count: int
    local_sme_ratio_pct: float
    total_eco_points: int
    estimated_local_revenue_bdt: float

class GroupTravelPlanResponse(BaseModel):
    city: str
    total_days: int
    pace: str
    consensus_strategy: str
    total_estimated_cost_bdt: float
    total_estimated_cost_usd: float
    total_distance_km: float
    fairness_report: GroupFairnessReport
    eco_summary: Optional[EcoTripSummary] = None
    daily_schedule: List[DailySchedule]

class WeatherReplanRequest(BaseModel):
    city: str = Field("Chittagong", example="Chittagong")
    weather_condition: str = Field("Heavy Rain", example="Heavy Rain")
    members: List[UserProfile]
    current_spots: List[SpotResponse]
    all_scheduled_spot_ids: Optional[List[int]] = None

class WeatherReplanResponse(BaseModel):
    rerouted: bool
    weather_condition: str
    swapped_spots_count: int
    notifications: List[str]
    updated_spots: List[SpotResponse]

class VetoSpotRequest(BaseModel):
    city: str = Field("Chittagong", example="Chittagong")
    spot_id: int
    vetoed_by: str = Field("Sadia", example="Sadia")
    members: List[UserProfile]
    current_spots: List[SpotResponse]
    all_scheduled_spot_ids: Optional[List[int]] = None

class VetoSpotResponse(BaseModel):
    success: bool
    vetoed_by: str
    original_spot_name: str
    substitute_spot: Optional[SpotResponse] = None
    notification: str
    nash_welfare_gain: Optional[float] = 0.0
    counterfactual_reason: Optional[str] = ""
    updated_spots: List[SpotResponse]

# --- Blueprint B ML & Business/Sustainability Schemas ---

class SwipeHistoryItem(BaseModel):
    card_id: str
    action: str  # "like" | "super" | "pass"

class ActiveSwipeRequest(BaseModel):
    history: List[SwipeHistoryItem] = []
    max_cards: int = Field(6, ge=3, le=12)

class ActiveSwipeResponse(BaseModel):
    completed: bool
    step: int
    total_steps: int
    confidence_pct: float
    next_card: Optional[Dict[str, Any]] = None
    inferred_interests: List[str]
    category_scores: Dict[str, float]
    taste_embedding: List[float]
    information_gain: float

class CopilotChatRequest(BaseModel):
    query: str
    city: str = "Chittagong"
    members: List[UserProfile] = []
    plan_summary: Optional[Dict[str, Any]] = None
    expenses_total_bdt: Optional[float] = 0.0

class CopilotChatResponse(BaseModel):
    answer: str
    verified: bool
    hallucination_checks_passed: int
    grounded_sources: List[Dict[str, Any]]
    verification_log: List[str]
    provider_used: str
    latency_ms: float

class EcoReportRequest(BaseModel):
    spots: List[SpotResponse] = []
    group_size: int = Field(3, ge=1, le=20)
    transport_mode: str = Field("shared_microbus", description="private_car, shared_microbus, ev_cng, walk_transit")
    total_distance_km: float = 15.0

class BookingReserveRequest(BaseModel):
    spot_id: int
    spot_name: str
    city: str
    date: str
    time_slot: str
    group_size: int = Field(3, ge=1, le=20)
    lead_name: str
    lead_contact: str
    eco_pledge: bool = True
    redeem_eco_points: int = 0
    unit_cost_bdt: float = 150.0

class BookingReserveResponse(BaseModel):
    voucher_code: str
    status: str
    spot_name: str
    partner_name: str
    date: str
    time_slot: str
    group_size: int
    base_total_bdt: float
    group_discount_pct: int
    group_discount_bdt: float
    eco_points_discount_bdt: float
    final_total_bdt: float
    eco_points_earned: int
    local_sme_revenue_bdt: float
    eco_pledge: bool
