"""
Business & Sustainability Telemetry Service for TripSense.

Calculates:
  1. Carbon Footprint (kg CO2) across transport modes vs. standard unoptimized private cars.
  2. Local SME Community Revenue Share (BDT & %) — tracking B2B2C tourism equity.
  3. Green Eco-Points Reward Wallet & Group Reservation Vouchers with tier discounts.
"""

import uuid
from typing import List, Dict, Any

# Emissions in kg CO2 per km per group vehicle/traveler footprint
TRANSPORT_EMISSION_FACTORS = {
    "private_car": 0.24,      # Standard petrol SUV / car
    "shared_microbus": 0.085, # Shared Hiace / coaster split across group
    "ev_cng": 0.055,          # CNG / electric shuttle
    "walk_transit": 0.025,    # Public transit + walking
}


class EcoBusinessService:
    @staticmethod
    def compute_trip_eco_summary(
        all_spots: List[Dict[str, Any]],
        total_distance_km: float,
        group_size: int = 3,
        transport_mode: str = "shared_microbus",
    ) -> Dict[str, Any]:
        if not all_spots:
            return {
                "total_co2_kg": 0.0,
                "standard_car_co2_kg": 0.0,
                "co2_saved_kg": 0.0,
                "trees_equivalent": 0.0,
                "avg_sustainability_score": 80.0,
                "local_sme_count": 0,
                "local_sme_ratio_pct": 0.0,
                "total_eco_points": 0,
                "estimated_local_revenue_bdt": 0.0,
            }

        factor = TRANSPORT_EMISSION_FACTORS.get(transport_mode, 0.085)
        transit_co2 = max(1.0, total_distance_km) * factor
        activity_co2 = sum(float(s.get("co2_kg_base", 1.2)) for s in all_spots) * max(1, group_size) * 0.45
        total_co2 = round(transit_co2 + activity_co2, 2)

        # Standard unoptimized solo/private-car baseline (39.4% longer unoptimized path + high-crowd car)
        unopt_distance = max(2.0, total_distance_km) * 1.48
        standard_car_co2 = round(
            (unopt_distance * TRANSPORT_EMISSION_FACTORS["private_car"] * max(1, (group_size + 1) // 2))
            + (sum(float(s.get("co2_kg_base", 1.5)) for s in all_spots) * max(1, group_size) * 0.70),
            2,
        )

        co2_saved = round(max(0.0, standard_car_co2 - total_co2), 2)
        trees_eq = round(co2_saved / 21.0, 2)  # ~21 kg CO2 absorbed per mature tree/year

        avg_sust = round(sum(float(s.get("sustainability_score", 80)) for s in all_spots) / len(all_spots), 1)
        sme_spots = [s for s in all_spots if s.get("local_sme", False)]
        sme_ratio = round((len(sme_spots) / len(all_spots)) * 100.0, 1)
        eco_points = int(sum(int(s.get("eco_points_reward", 60)) for s in all_spots) + co2_saved * 8)

        # Direct economic retention inside local community SMEs (tickets + typical ৳350 meal/craft spend per stop)
        local_rev = 0.0
        for s in all_spots:
            base_spend = (float(s.get("estimated_cost_bdt", 0.0)) + 250.0) * max(1, group_size)
            share = float(s.get("local_revenue_share_pct", 60)) / 100.0
            local_rev += base_spend * share

        return {
            "total_co2_kg": total_co2,
            "standard_car_co2_kg": standard_car_co2,
            "co2_saved_kg": co2_saved,
            "trees_equivalent": trees_eq,
            "avg_sustainability_score": avg_sust,
            "local_sme_count": len(sme_spots),
            "local_sme_ratio_pct": sme_ratio,
            "total_eco_points": eco_points,
            "estimated_local_revenue_bdt": round(local_rev, 0),
        }

    @staticmethod
    def create_reservation(
        spot: Dict[str, Any],
        date: str,
        time_slot: str,
        group_size: int,
        lead_name: str,
        eco_pledge: bool,
        redeem_eco_points: int,
        unit_cost_bdt: float,
    ) -> Dict[str, Any]:
        effective_unit = max(float(spot.get("estimated_cost_bdt", 0.0)), float(unit_cost_bdt or 0.0))
        if effective_unit == 0.0:
            effective_unit = 150.0  # Guided heritage / eco experience bundle option

        base_total = round(effective_unit * group_size, 2)
        base_disc_pct = int(spot.get("group_discount_pct", 10))
        if group_size >= 4:
            disc_pct = max(base_disc_pct, 15)
        elif group_size >= 3:
            disc_pct = max(base_disc_pct, 10)
        else:
            disc_pct = 0

        group_disc_bdt = round(base_total * (disc_pct / 100.0), 2)
        eco_disc_bdt = round(min(base_total * 0.25, max(0, redeem_eco_points) * 0.5), 2)
        final_total = round(max(0.0, base_total - group_disc_bdt - eco_disc_bdt), 2)

        earned_pts = int(spot.get("eco_points_reward", 60)) + (40 if eco_pledge else 0)
        share_pct = float(spot.get("local_revenue_share_pct", 80)) / 100.0
        local_rev = round(final_total * share_pct, 2)

        code = f"TS-BD-{uuid.uuid4().hex[:6].upper()}"
        return {
            "voucher_code": code,
            "status": "CONFIRMED",
            "spot_name": spot.get("name", "TripSense Partner"),
            "partner_name": spot.get("local_partner_name", "Verified Community Host"),
            "date": date,
            "time_slot": time_slot,
            "group_size": group_size,
            "base_total_bdt": base_total,
            "group_discount_pct": disc_pct,
            "group_discount_bdt": group_disc_bdt,
            "eco_points_discount_bdt": eco_disc_bdt,
            "final_total_bdt": final_total,
            "eco_points_earned": earned_pts,
            "local_sme_revenue_bdt": local_rev,
            "eco_pledge": eco_pledge,
        }
