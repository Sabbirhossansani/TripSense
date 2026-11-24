import React, { useState } from "react";
import {
  Navigation,
  Sparkles,
  Film,
  SlidersHorizontal,
  ShieldAlert,
  Compass,
  CheckCircle2,
  Leaf,
} from "lucide-react";
import LeafletMap from "./LeafletMap";
import SpotCard from "./SpotCard";
import WeatherAlertBanner from "./WeatherAlertBanner";
import MemberProfileModal from "./MemberProfileModal";
import EditorialHero from "./EditorialHero";
import BeforeAfterComparer from "./BeforeAfterComparer";
import EcoImpactCalculator from "./EcoImpactCalculator";
import { ShimmerCardSkeleton } from "./MotionPrimitives";
import { SPOT_IMAGES } from "../assets/images";
import { formatCurrency } from "../api/client";

export default function ItineraryTab({
  plan,
  city,
  startDate,
  onGeneratePlan,
  isLoading,
  onSelectSpot,
  isRainSimulated,
  onToggleRainSimulation,
  onAutoReroute,
  isRerouted,
  onRevertPlan,
  isReplanning,
  replannedNotifications,
  members = [],
  vetoTokens = {},
  onVetoSpot,
  onBookSpot,
  currentUser,
  expenses = [],
  onOpenReel,
  onOpenSetupWizard,
  onOpenSwipe,
  onOpenLogin,
  onOpenMlLab,
  vetoNotification: externalVetoNotification = null,
  lang = "EN",
  currency = "BDT",
}) {
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);
  const [mapExpanded, setMapExpanded] = useState(false);
  const [activeProfileMember, setActiveProfileMember] = useState(null);
  const [localVetoNotification, setLocalVetoNotification] = useState(null);

  const activeVetoNotification = externalVetoNotification || localVetoNotification;

  const dailySchedule = plan?.daily_schedule || [];
  const currentDay = dailySchedule[selectedDayIndex] || dailySchedule[0] || null;
  const currentSpots = currentDay?.spots || [];
  const allSpots = dailySchedule.flatMap((d) => d.spots || []);

  const heroImage =
    SPOT_IMAGES[101] ||
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80";

  const totalSpentBdt = expenses.reduce((sum, e) => sum + (e.amountBDT || 0), 0);
  const estimatedCostBdt = plan?.total_estimated_cost_bdt || 2500;
  const budgetRatio = Math.min(100, Math.round((totalSpentBdt / Math.max(1, estimatedCostBdt)) * 100));

  const getDayDateLabel = (dayIdx) => {
    try {
      const d = new Date(startDate || "2026-08-12");
      d.setDate(d.getDate() + dayIdx);
      return d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
    } catch {
      return `Day ${dayIdx + 1}`;
    }
  };

  const handleVeto = async (spot) => {
    const memberName = currentUser?.name || members[0]?.name || "Sadia";
    const userRemainingTokens = vetoTokens[memberName] ?? 1;

    if (userRemainingTokens <= 0) {
      alert(`${memberName} has already used their 1 Nash Veto Token for this trip!`);
      return;
    }

    if (onVetoSpot) {
      const res = await onVetoSpot(spot, memberName);
      if (res && res.notification) {
        setLocalVetoNotification(res.notification);
        setTimeout(() => setLocalVetoNotification(null), 5000);
      }
    }
  };

  const activeUserName = currentUser?.name || members[0]?.name || "Rahat";
  const userTokens = vetoTokens[activeUserName] ?? 1;
  const fairnessReport = plan?.fairness_report || { fairness_score: 78.4 };
  const ecoSummary = plan?.eco_summary || { co2_saved_kg: 11.4, local_sme_ratio_pct: 83.3, total_eco_points: 520 };

  return (
    <div style={{ width: "100%", paddingBottom: "40px" }}>
      {/* Editorial Hero Showcase */}
      <EditorialHero
        city={city}
        fairnessScore={fairnessReport.fairness_score}
        co2SavedKg={ecoSummary.co2_saved_kg}
        lang={lang}
        currentUser={currentUser}
        onStartSwipe={onOpenSwipe}
        onOpenWizard={onOpenSetupWizard}
        onOpenLogin={onOpenLogin}
        onOpenMlLab={onOpenMlLab}
      />

      {/* Loading Skeletons (Zero CLS) */}
      {isLoading && (!plan || dailySchedule.length === 0) && (
        <div style={{ marginBottom: "20px" }}>
          <ShimmerCardSkeleton height={160} />
          <ShimmerCardSkeleton height={130} />
          <ShimmerCardSkeleton height={130} />
        </div>
      )}

      {/* Fallback CTA if no plan loaded and not loading */}
      {!isLoading && (!plan || dailySchedule.length === 0) && (
        <div
          style={{
            maxWidth: "620px",
            margin: "24px auto",
            textAlign: "center",
            background: "#FFFFFF",
            borderRadius: "24px",
            padding: "36px 24px",
            border: "1px solid var(--stone-border)",
          }}
        >
          <div style={{ width: "60px", height: "60px", borderRadius: "18px", background: "var(--safety-orange-soft)", color: "var(--safety-orange)", display: "inline-flex", alignItems: "center", justifyContent: "center", marginBottom: "14px" }}>
            <Navigation size={30} />
          </div>
          <h2 className="font-display" style={{ fontSize: "22px", fontWeight: 800, marginBottom: "8px" }}>
            Ready to Generate Your {city} FairNet Plan?
          </h2>
          <p style={{ fontSize: "13px", color: "var(--granite-600)", lineHeight: 1.5, marginBottom: "20px" }}>
            Balances all squad preferences using TripSense-FairNet neural consensus & 2-Opt TSP route scheduling.
          </p>
          <button
            type="button"
            onClick={onGeneratePlan}
            className="liquid-btn"
            style={{
              background: "var(--safety-orange)",
              color: "#FFFFFF",
              border: "none",
              padding: "13px 26px",
              borderRadius: "14px",
              fontSize: "14px",
              fontWeight: 800,
              cursor: "pointer",
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <Sparkles size={16} />
            <span>Generate {city} Itinerary</span>
          </button>
        </div>
      )}

      {/* Active Command Center + Asymmetrical Editorial Workspace */}
      {plan && dailySchedule.length > 0 && (
        <>
          {/* Command Center Summary Banner */}
          <div
            style={{
              position: "relative",
              borderRadius: "24px",
              overflow: "hidden",
              marginBottom: "16px",
              boxShadow: "0 12px 30px rgba(26, 29, 28, 0.12)",
              background: "#1A1D1C",
            }}
          >
            <div style={{ position: "absolute", inset: 0, backgroundImage: `url(${heroImage})`, backgroundSize: "cover", backgroundPosition: "center", opacity: 0.34 }} />

            <div style={{ position: "relative", zIndex: 10, padding: "22px", color: "#FAF9F6" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px", marginBottom: "14px" }}>
                <div>
                  <div style={{ display: "inline-flex", alignItems: "center", gap: "6px", background: "rgba(255,255,255,0.16)", backdropFilter: "blur(6px)", padding: "4px 12px", borderRadius: "999px", fontSize: "11px", fontWeight: 800, marginBottom: "6px" }}>
                    <Compass size={13} color="#FF9F7A" />
                    <span>{dailySchedule.length}-DAY EXPEDITION • {fairnessReport.model_used || "TRIPSENSE-FAIRNET"}</span>
                  </div>
                  <h2 className="font-display" style={{ fontSize: "24px", fontWeight: 900, margin: 0 }}>
                    {city} Squad Command Center
                  </h2>
                </div>

                <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                  {onOpenReel && (
                    <button
                      type="button"
                      onClick={onOpenReel}
                      className="liquid-btn"
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        background: "var(--safety-orange)",
                        border: "none",
                        borderRadius: "12px",
                        padding: "9px 14px",
                        fontSize: "12px",
                        fontWeight: 800,
                        color: "#FFFFFF",
                        cursor: "pointer",
                      }}
                    >
                      <Film size={14} />
                      <span>15s Trip Reel</span>
                    </button>
                  )}

                  {onOpenSetupWizard && (
                    <button
                      type="button"
                      onClick={onOpenSetupWizard}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        background: "rgba(255,255,255,0.16)",
                        border: "1px solid rgba(255,255,255,0.3)",
                        borderRadius: "12px",
                        padding: "9px 13px",
                        fontSize: "12px",
                        fontWeight: 700,
                        color: "#FFFFFF",
                        cursor: "pointer",
                      }}
                    >
                      <SlidersHorizontal size={14} />
                      <span>Setup Wizard</span>
                    </button>
                  )}
                </div>
              </div>

              <div className="glass-dark" style={{ borderRadius: "16px", padding: "14px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <span style={{ fontSize: "11px", fontWeight: 700, color: "#B8C0BC" }}>SQUAD BUDGET METER</span>
                  <span className="font-mono-num" style={{ fontSize: "12px", fontWeight: 800, color: "#9FE0C4" }}>
                    {formatCurrency(totalSpentBdt, currency)} logged / ~{formatCurrency(estimatedCostBdt, currency)} est.
                  </span>
                </div>

                <div style={{ width: "100%", height: "6px", background: "rgba(255,255,255,0.16)", borderRadius: "999px", overflow: "hidden", marginBottom: "10px" }}>
                  <div style={{ width: `${budgetRatio}%`, height: "100%", background: budgetRatio > 90 ? "#E85D2A" : "linear-gradient(90deg, #386655 0%, #C9933B 100%)", borderRadius: "999px" }} />
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
                  <div style={{ display: "flex", gap: "14px", fontSize: "11px", color: "#E2DDD3", flexWrap: "wrap" }}>
                    <span>📍 <strong className="font-mono-num">{allSpots.length}</strong> POIs</span>
                    <span>🚗 <strong className="font-mono-num">{plan.total_distance_km} km</strong> 2-Opt Route</span>
                    <span>⚖️ <strong className="font-mono-num">{fairnessReport.fairness_score}/100</strong> Fairness</span>
                    <span style={{ color: "#9FE0C4" }}><Leaf size={11} style={{ verticalAlign: "middle" }} /> <strong>{ecoSummary.co2_saved_kg} kg</strong> CO₂ Saved</span>
                  </div>

                  <div style={{ display: "inline-flex", alignItems: "center", gap: "4px", background: "rgba(56,102,85,0.45)", color: "#A7F3D0", padding: "3px 10px", borderRadius: "999px", fontSize: "10px", fontWeight: 700 }}>
                    <CheckCircle2 size={11} />
                    <span>FairNet + Least-Misery Verified</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Squad Status Row */}
          <div style={{ background: "#FFFFFF", borderRadius: "18px", border: "1px solid var(--stone-border)", padding: "12px 16px", marginBottom: "14px", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
              <span style={{ fontSize: "12px", fontWeight: 800, color: "var(--granite-800)" }}>Squad Status:</span>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                {members.map((m, idx) => {
                  const tokensLeft = vetoTokens[m.name] ?? 1;
                  return (
                    <div
                      key={m.name}
                      onClick={() => setActiveProfileMember(m)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        background: "var(--bg-surface)",
                        border: "1px solid var(--stone-border)",
                        borderRadius: "999px",
                        padding: "3px 10px 3px 4px",
                        cursor: "pointer",
                      }}
                    >
                      <div
                        style={{
                          position: "relative",
                          width: "22px",
                          height: "22px",
                          borderRadius: "50%",
                          background: ["#E85D2A", "#25463B", "#C9933B", "#2A2F2D"][idx % 4],
                          color: "#FFFFFF",
                          fontSize: "11px",
                          fontWeight: 800,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        {m.name.charAt(0)}
                        <span style={{ position: "absolute", bottom: "-1px", right: "-1px", width: "7px", height: "7px", borderRadius: "50%", background: "#386655", border: "1.5px solid #FFFFFF" }} />
                      </div>
                      <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--granite-950)" }}>{m.name}</span>
                      <span style={{ fontSize: "9px", fontWeight: 800, padding: "2px 6px", borderRadius: "999px", background: tokensLeft > 0 ? "var(--alpine-moss-soft)" : "var(--stone-muted)", color: tokensLeft > 0 ? "var(--alpine-moss)" : "var(--granite-600)" }}>
                        {tokensLeft > 0 ? "1 Veto" : "Used"}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div style={{ fontSize: "11px", color: "var(--granite-600)" }}>
              Active: <strong>{activeUserName}</strong> ({userTokens} Veto Left)
            </div>
          </div>

          {activeVetoNotification && (
            <div style={{ background: "var(--safety-orange-soft)", border: "1.5px solid #F7C6B3", borderRadius: "14px", padding: "10px 14px", marginBottom: "14px", display: "flex", alignItems: "center", gap: "8px", fontSize: "12px", color: "#9A2B14", fontWeight: 700 }}>
              <ShieldAlert size={16} />
              <span>{activeVetoNotification}</span>
            </div>
          )}

          <WeatherAlertBanner
            city={city}
            isRainSimulated={isRainSimulated}
            onToggleRainSimulation={onToggleRainSimulation}
            onAutoReroute={onAutoReroute}
            isRerouted={isRerouted}
            onRevertPlan={onRevertPlan}
            isLoading={isReplanning}
            replannedNotifications={replannedNotifications}
          />

          {/* Days Tabs */}
          <div style={{ display: "flex", gap: "8px", overflowX: "auto", paddingBottom: "8px", marginBottom: "12px" }}>
            {dailySchedule.map((day, idx) => {
              const isSelected = selectedDayIndex === idx;
              return (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setSelectedDayIndex(idx)}
                  style={{
                    flex: "1 0 auto",
                    minWidth: "120px",
                    padding: "10px 14px",
                    borderRadius: "14px",
                    border: isSelected ? "2px solid var(--safety-orange)" : "1px solid var(--stone-border)",
                    background: isSelected ? "var(--safety-orange-soft)" : "#FFFFFF",
                    cursor: "pointer",
                    textAlign: "left",
                  }}
                >
                  <div style={{ fontSize: "12px", fontWeight: 800, color: isSelected ? "var(--safety-orange-hover)" : "var(--granite-950)" }}>
                    Day {day.day}
                  </div>
                  <div style={{ fontSize: "11px", color: isSelected ? "var(--safety-orange)" : "var(--granite-600)", fontWeight: 600 }}>
                    {getDayDateLabel(idx)}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Asymmetrical Editorial Split Layout: Sticky Map (Left/Top) + Timeline Cards (Right/Bottom) */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
              gap: "20px",
              alignItems: "start",
              marginBottom: "26px",
            }}
          >
            {/* Map Column */}
            <div
              id="map-section"
              style={{
                background: "#FFFFFF",
                borderRadius: "22px",
                border: "1px solid var(--stone-border)",
                overflow: "hidden",
                boxShadow: "0 8px 24px rgba(26,29,28,0.06)",
                height: mapExpanded ? "70vh" : "420px",
                transition: "height 0.3s ease",
                position: "sticky",
                top: "120px",
              }}
            >
              <LeafletMap spots={currentSpots} onSelectSpot={onSelectSpot} city={city} isTabActive={true} />
              <button
                type="button"
                onClick={() => {
                  setMapExpanded(!mapExpanded);
                  setTimeout(() => window.dispatchEvent(new Event("resize")), 320);
                }}
                style={{
                  position: "absolute",
                  top: "12px",
                  left: "12px",
                  zIndex: 10,
                  background: "rgba(250, 249, 246, 0.92)",
                  border: "1px solid var(--stone-border)",
                  padding: "6px 12px",
                  borderRadius: "10px",
                  fontSize: "11px",
                  fontWeight: 800,
                  color: "var(--granite-950)",
                  cursor: "pointer",
                }}
              >
                {mapExpanded ? "Collapse Map" : "Expand Map"}
              </button>
            </div>

            {/* Timeline Column */}
            <div>
              {currentDay && (
                <div style={{ background: "#FFFFFF", borderRadius: "16px", border: "1px solid var(--stone-border)", padding: "14px 16px", marginBottom: "14px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
                  <div>
                    <div className="font-display" style={{ fontSize: "16px", fontWeight: 800, color: "var(--granite-950)" }}>
                      {currentDay.title || `Day ${currentDay.day}`}
                    </div>
                    <div style={{ fontSize: "11px", color: "var(--granite-600)" }}>
                      {currentSpots.length} stops • 2-Opt shortest route
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: "14px" }}>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: "10px", fontWeight: 700, color: "var(--granite-600)" }}>DAY COST</div>
                      <div className="font-mono-num" style={{ fontSize: "13px", fontWeight: 800 }}>{formatCurrency(currentDay.daily_cost_bdt ?? 0, currency)}</div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: "10px", fontWeight: 700, color: "var(--granite-600)" }}>TRANSIT</div>
                      <div className="font-mono-num" style={{ fontSize: "13px", fontWeight: 800 }}>{currentDay.daily_distance_km ?? 0} km</div>
                    </div>
                  </div>
                </div>
              )}

              {currentSpots.map((spot, index) => (
                <SpotCard
                  key={spot.id || index}
                  spot={spot}
                  index={index}
                  onSelect={onSelectSpot}
                  onVeto={handleVeto}
                  onBook={onBookSpot}
                  userVetoTokens={userTokens}
                  currentMemberName={activeUserName}
                  currency={currency}
                />
              ))}
            </div>
          </div>

          {/* Interactive Before / After Showcase Comparer */}
          <BeforeAfterComparer city={city} />

          {/* Interactive Sustainability & SME Calculator */}
          <EcoImpactCalculator
            spots={allSpots}
            totalDistanceKm={plan.total_distance_km || 14.5}
            defaultGroupSize={members.length || 3}
            currency={currency}
          />
        </>
      )}

      {activeProfileMember && (
        <MemberProfileModal
          member={activeProfileMember}
          satisfaction={Math.round(fairnessReport.member_average_satisfaction?.[activeProfileMember.name] || 75)}
          vetoLeft={vetoTokens[activeProfileMember.name] ?? 1}
          onClose={() => setActiveProfileMember(null)}
        />
      )}
    </div>
  );
}
