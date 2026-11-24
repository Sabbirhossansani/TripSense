import React, { useState, useEffect } from "react";
import { Leaf, Trees, Store, Award, Car, Bus, Zap, Footprints } from "lucide-react";
import { fetchEcoReport, formatCurrency } from "../api/client";
import { ScrollReveal } from "./MotionPrimitives";

const TRANSPORT_OPTIONS = [
  { id: "private_car", label: "Private Car", icon: Car, tag: "Baseline" },
  { id: "shared_microbus", label: "Shared Microbus", icon: Bus, tag: "-65% CO₂" },
  { id: "ev_cng", label: "EV / Green CNG", icon: Zap, tag: "-77% CO₂" },
  { id: "walk_transit", label: "Walk + Transit", icon: Footprints, tag: "-89% CO₂" },
];

export default function EcoImpactCalculator({
  spots = [],
  totalDistanceKm = 15.0,
  defaultGroupSize = 3,
  currency = "BDT",
}) {
  const [groupSize, setGroupSize] = useState(defaultGroupSize);
  const [transportMode, setTransportMode] = useState("shared_microbus");
  const [report, setReport] = useState({
    total_co2_kg: 6.4,
    standard_car_co2_kg: 18.2,
    co2_saved_kg: 11.8,
    trees_equivalent: 0.56,
    avg_sustainability_score: 86.5,
    local_sme_count: 5,
    local_sme_ratio_pct: 83.3,
    total_eco_points: 540,
    estimated_local_revenue_bdt: 6850,
  });

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const res = await fetchEcoReport({
          spots: spots.slice(0, 12),
          group_size: groupSize,
          transport_mode: transportMode,
          total_distance_km: totalDistanceKm || 15.0,
        });
        if (active && res) setReport(res);
      } catch {
        // Fallback local arithmetic if offline
        const mult = transportMode === "private_car" ? 0.24 : transportMode === "ev_cng" ? 0.055 : transportMode === "walk_transit" ? 0.025 : 0.085;
        const totalCo2 = Number(((totalDistanceKm || 15) * mult + groupSize * 1.4).toFixed(2));
        const stdCo2 = Number(((totalDistanceKm || 15) * 1.48 * 0.24 + groupSize * 2.5).toFixed(2));
        const saved = Math.max(0, Number((stdCo2 - totalCo2).toFixed(2)));
        if (active) {
          setReport((prev) => ({
            ...prev,
            total_co2_kg: totalCo2,
            standard_car_co2_kg: stdCo2,
            co2_saved_kg: saved,
            trees_equivalent: Number((saved / 21).toFixed(2)),
            estimated_local_revenue_bdt: Math.round(groupSize * 2200),
            total_eco_points: Math.round(350 + saved * 10),
          }));
        }
      }
    };
    load();
    return () => { active = false; };
  }, [groupSize, transportMode, totalDistanceKm, spots]);

  return (
    <ScrollReveal delay={0.08}>
      <section
        style={{
          background: "#FFFFFF",
          border: "1px solid var(--stone-border)",
          borderRadius: "24px",
          padding: "22px",
          marginBottom: "22px",
          boxShadow: "0 10px 28px rgba(26, 29, 28, 0.04)",
        }}
      >
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "12px", marginBottom: "18px" }}>
          <div>
            <div style={{ display: "inline-flex", alignItems: "center", gap: "6px", fontSize: "11px", fontWeight: 800, color: "var(--alpine-moss)", textTransform: "uppercase", letterSpacing: "0.7px" }}>
              <Leaf size={13} />
              <span>Sustainability & Local Economy Simulator</span>
            </div>
            <h2 className="font-display" style={{ fontSize: "22px", fontWeight: 800, color: "var(--granite-950)", margin: "4px 0 0 0" }}>
              Live Carbon & Local SME Impact Calculator
            </h2>
          </div>

          <div
            style={{
              background: "var(--alpine-moss-soft)",
              border: "1px solid #C5D9CE",
              borderRadius: "14px",
              padding: "8px 14px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <Award size={18} color="#25463B" />
            <div>
              <div style={{ fontSize: "10px", fontWeight: 700, color: "var(--alpine-moss)" }}>ECO-POINTS REWARD</div>
              <div className="font-mono-num" style={{ fontSize: "15px", fontWeight: 800, color: "var(--granite-950)" }}>
                +{report.total_eco_points} pts
              </div>
            </div>
          </div>
        </div>

        {/* Interactive Controls */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "16px", marginBottom: "18px" }}>
          {/* Group Size Slider */}
          <div style={{ background: "var(--bg-surface)", border: "1px solid var(--stone-border)", borderRadius: "16px", padding: "14px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
              <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--granite-800)" }}>
                Squad Headcount
              </span>
              <span className="font-mono-num" style={{ fontSize: "13px", fontWeight: 800, color: "var(--safety-orange)" }}>
                {groupSize} Travelers
              </span>
            </div>
            <input
              type="range"
              min={1}
              max={12}
              value={groupSize}
              onChange={(e) => setGroupSize(Number(e.target.value))}
              style={{ width: "100%", accentColor: "#E85D2A", cursor: "pointer" }}
            />
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "10px", color: "var(--granite-600)", marginTop: "4px" }}>
              <span>1 Solo</span>
              <span>4 Squad (15% Group Discount)</span>
              <span>12 Bus</span>
            </div>
          </div>

          {/* Transport Mode Tactile Selector */}
          <div style={{ background: "var(--bg-surface)", border: "1px solid var(--stone-border)", borderRadius: "16px", padding: "14px" }}>
            <div style={{ fontSize: "12px", fontWeight: 700, color: "var(--granite-800)", marginBottom: "8px" }}>
              Transit Mode
            </div>
            <div className="neu-control" style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "4px" }}>
              {TRANSPORT_OPTIONS.map((opt) => {
                const Icon = opt.icon;
                const active = transportMode === opt.id;
                return (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setTransportMode(opt.id)}
                    className={active ? "neu-control-item-active" : ""}
                    style={{
                      border: "none",
                      borderRadius: "10px",
                      padding: "7px 4px",
                      cursor: "pointer",
                      background: active ? "#FFFFFF" : "transparent",
                      color: active ? "var(--granite-950)" : "var(--granite-600)",
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      gap: "3px",
                      fontSize: "10px",
                      fontWeight: 700,
                      transition: "all 0.2s ease",
                    }}
                  >
                    <Icon size={14} color={active ? "#E85D2A" : "#59615E"} />
                    <span>{opt.label.split(" ")[0]}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Live Calculated Telemetry Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: "12px" }}>
          <div style={{ background: "var(--alpine-moss-soft)", borderRadius: "16px", padding: "14px", border: "1px solid #C5D9CE" }}>
            <div style={{ fontSize: "10px", fontWeight: 800, color: "var(--alpine-moss)" }}>NET CO₂ SAVED</div>
            <div className="font-mono-num" style={{ fontSize: "24px", fontWeight: 800, color: "var(--granite-950)", margin: "4px 0" }}>
              {report.co2_saved_kg} kg
            </div>
            <div style={{ fontSize: "11px", color: "var(--alpine-moss-mid)", fontWeight: 600 }}>
              vs. {report.standard_car_co2_kg} kg unoptimized car
            </div>
          </div>

          <div style={{ background: "var(--bg-surface)", borderRadius: "16px", padding: "14px", border: "1px solid var(--stone-border)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "10px", fontWeight: 800, color: "var(--granite-600)" }}>
              <Trees size={12} color="#25463B" />
              <span>TREE EQUIVALENT</span>
            </div>
            <div className="font-mono-num" style={{ fontSize: "24px", fontWeight: 800, color: "var(--granite-950)", margin: "4px 0" }}>
              {report.trees_equivalent}
            </div>
            <div style={{ fontSize: "11px", color: "var(--granite-600)" }}>
              Annual tree CO₂ offsets
            </div>
          </div>

          <div style={{ background: "var(--safety-orange-soft)", borderRadius: "16px", padding: "14px", border: "1px solid #F7C6B3" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "10px", fontWeight: 800, color: "var(--safety-orange-hover)" }}>
              <Store size={12} />
              <span>LOCAL SME REVENUE</span>
            </div>
            <div className="font-mono-num" style={{ fontSize: "24px", fontWeight: 800, color: "var(--granite-950)", margin: "4px 0" }}>
              {formatCurrency(report.estimated_local_revenue_bdt, currency)}
            </div>
            <div style={{ fontSize: "11px", color: "var(--safety-orange-hover)", fontWeight: 600 }}>
              {report.local_sme_ratio_pct}% goes to community hosts
            </div>
          </div>

          <div style={{ background: "var(--brass-soft)", borderRadius: "16px", padding: "14px", border: "1px solid #E5C88B" }}>
            <div style={{ fontSize: "10px", fontWeight: 800, color: "#805919" }}>B2B2C ECO-WALLET</div>
            <div className="font-mono-num" style={{ fontSize: "24px", fontWeight: 800, color: "var(--granite-950)", margin: "4px 0" }}>
              {formatCurrency(report.total_eco_points * 0.5, currency)}
            </div>
            <div style={{ fontSize: "11px", color: "#805919", fontWeight: 600 }}>
              Redeemable on guided tours
            </div>
          </div>
        </div>
      </section>
    </ScrollReveal>
  );
}
