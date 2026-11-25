import React, { useState } from "react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import {
  Navigation,
  Sparkles,
  Film,
  Users,
  CloudRain,
  Bot,
  Calendar,
  Leaf,
  Scale,
  Maximize2,
  Minimize2,
} from "lucide-react";
import LeafletMap from "./LeafletMap";
import SpotCard from "./SpotCard";
import WeatherAlertBanner from "./WeatherAlertBanner";
import MemberProfileModal from "./MemberProfileModal";
import { ShimmerCardSkeleton, StaggerContainer, StaggerItem } from "./MotionPrimitives";
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
  onOpenReel,
  onOpenDatePicker,
  onOpenSquad,
  onOpenCopilot,
  currency = "BDT",
}) {
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);
  const [mapExpanded, setMapExpanded] = useState(false);
  const [activeProfileMember, setActiveProfileMember] = useState(null);

  const dailySchedule = plan?.daily_schedule || [];
  const currentDay = dailySchedule[selectedDayIndex] || dailySchedule[0] || null;
  const currentSpots = currentDay?.spots || [];

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
    const memberName = currentUser?.name || members[0]?.name || "Rahat";
    const userRemainingTokens = vetoTokens[memberName] ?? 1;

    if (userRemainingTokens <= 0) {
      toast.warning(`${memberName} has already used their Nash Veto token for this trip.`);
      return;
    }

    if (onVetoSpot) {
      const res = await onVetoSpot(spot, memberName);
      if (res && res.notification) {
        if (res.success) toast.success(res.notification);
        else toast.info(res.notification);
      }
    }
  };

  const activeUserName = currentUser?.name || members[0]?.name || "Rahat";
  const userTokens = vetoTokens[activeUserName] ?? 1;
  const fairnessReport = plan?.fairness_report || { fairness_score: 94.2 };
  const ecoSummary = plan?.eco_summary || { co2_saved_kg: 18.4, total_eco_points: 520 };

  return (
    <div className="max-w-[1380px] mx-auto px-4 sm:px-6 pt-5 pb-24">
      {/* Loading Skeletons */}
      {isLoading && (!plan || dailySchedule.length === 0) && (
        <div className="space-y-3 max-w-3xl mx-auto mt-8">
          <ShimmerCardSkeleton height={110} />
          <ShimmerCardSkeleton height={135} />
          <ShimmerCardSkeleton height={135} />
        </div>
      )}

      {/* Empty State */}
      {!isLoading && (!plan || dailySchedule.length === 0) && (
        <div className="max-w-lg mx-auto my-12 text-center bg-white rounded-3xl border border-[#E6E1D6] p-10">
          <div className="w-12 h-12 rounded-2xl bg-[#FDF0EB] text-[#D94E28] inline-flex items-center justify-center mb-4">
            <Navigation className="w-6 h-6" />
          </div>
          <h2 className="font-display text-2xl font-semibold text-[#141715]">
            Build your {city} itinerary
          </h2>
          <p className="text-sm text-[#5A605C] mt-2 mb-6">
            FairNet balances every friend&apos;s taste and budget along a shortest-path 2-Opt route.
          </p>
          <button
            type="button"
            onClick={onGeneratePlan}
            className="inline-flex items-center gap-2 rounded-full bg-[#D94E28] hover:bg-[#BF401E] text-white px-6 py-3 text-sm font-semibold border-none cursor-pointer transition"
          >
            <Sparkles className="w-4 h-4" />
            <span>Generate {city} Plan</span>
          </button>
        </div>
      )}

      {/* Clean Mindtrip Split-Screen Trip Workspace */}
      {plan && dailySchedule.length > 0 && (
        <>
          {/* ONE Clean, Breathable Trip Context Header */}
          <div className="bg-white border border-[#E6E1D6] rounded-3xl p-5 sm:p-6 mb-6 shadow-[0_2px_12px_rgba(20,23,21,0.03)]">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              {/* Left: Title + Calm Metrics */}
              <div>
                <div className="flex flex-wrap items-center gap-2.5">
                  <h1 className="font-display text-2xl sm:text-3xl font-semibold tracking-tight text-[#141715] m-0">
                    {city}
                  </h1>
                  <button
                    type="button"
                    onClick={onOpenDatePicker}
                    className="inline-flex items-center gap-1.5 rounded-full bg-[#F8F6F1] hover:bg-[#EFECE4] border border-[#E6E1D6] px-3 py-1 text-xs font-medium text-[#141715] cursor-pointer transition"
                  >
                    <Calendar className="w-3.5 h-3.5 text-[#D94E28]" />
                    <span>{dailySchedule.length} Days • Change</span>
                  </button>
                </div>

                <div className="mt-2.5 flex flex-wrap items-center gap-x-5 gap-y-1.5 text-xs text-[#5A605C]">
                  <span className="inline-flex items-center gap-1.5 font-mono-num">
                    <Scale className="w-3.5 h-3.5 text-[#D94E28]" />
                    <strong className="text-[#141715]">{fairnessReport.fairness_score}/100</strong> FairNet
                  </span>
                  <span className="inline-flex items-center gap-1.5 font-mono-num">
                    <Leaf className="w-3.5 h-3.5 text-[#1E4D3F]" />
                    <strong className="text-[#1E4D3F]">-{ecoSummary.co2_saved_kg} kg</strong> CO₂ saved
                  </span>
                  <span className="font-mono-num">
                    <strong className="text-[#141715]">{plan.total_distance_km} km</strong> 2-Opt route
                  </span>
                  <span className="font-mono-num">
                    Est. <strong className="text-[#141715]">{formatCurrency(plan.total_estimated_cost_bdt, currency)}</strong>
                  </span>
                </div>
              </div>

              {/* Right: Clean Single-Row Action Bar */}
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={onOpenSquad}
                  className="inline-flex items-center gap-1.5 rounded-full bg-[#F8F6F1] hover:bg-[#EFECE4] border border-[#E6E1D6] px-3.5 py-2 text-xs font-semibold text-[#141715] cursor-pointer transition"
                >
                  <Users className="w-3.5 h-3.5 text-[#1E4D3F]" />
                  <span>Squad ({members.length})</span>
                </button>

                <button
                  type="button"
                  onClick={onToggleRainSimulation}
                  className={`inline-flex items-center gap-1.5 rounded-full px-3.5 py-2 text-xs font-semibold border cursor-pointer transition ${
                    isRainSimulated || isRerouted
                      ? "bg-[#1E4D3F] text-white border-[#1E4D3F]"
                      : "bg-[#F8F6F1] hover:bg-[#EFECE4] text-[#141715] border-[#E6E1D6]"
                  }`}
                >
                  <CloudRain className="w-3.5 h-3.5" />
                  <span>{isRainSimulated || isRerouted ? "Rain Active" : "Rain Shield"}</span>
                </button>

                {onOpenReel && (
                  <button
                    type="button"
                    onClick={onOpenReel}
                    className="inline-flex items-center gap-1.5 rounded-full bg-[#F8F6F1] hover:bg-[#EFECE4] border border-[#E6E1D6] px-3.5 py-2 text-xs font-semibold text-[#141715] cursor-pointer transition"
                  >
                    <Film className="w-3.5 h-3.5 text-[#B8863B]" />
                    <span>15s Reel</span>
                  </button>
                )}

                {onOpenCopilot && (
                  <button
                    type="button"
                    onClick={onOpenCopilot}
                    className="inline-flex items-center gap-1.5 rounded-full bg-[#141715] hover:bg-[#262C29] text-white px-4 py-2 text-xs font-semibold border-none cursor-pointer transition"
                  >
                    <Bot className="w-3.5 h-3.5 text-[#F4A586]" />
                    <span>AI Concierge</span>
                  </button>
                )}
              </div>
            </div>

            {/* Subtle Squad Chips Strip */}
            <div className="mt-4 pt-3.5 border-t border-[#F1EDE5] flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                {members.map((m, idx) => {
                  const left = vetoTokens[m.name] ?? 1;
                  const colors = ["bg-[#D94E28]", "bg-[#1E4D3F]", "bg-[#B8863B]", "bg-[#262C29]"];
                  return (
                    <button
                      key={m.name}
                      type="button"
                      onClick={() => setActiveProfileMember(m)}
                      className="inline-flex items-center gap-2 rounded-full bg-[#F8F6F1] hover:bg-[#EFECE4] border border-[#E6E1D6] pl-1 pr-2.5 py-1 text-xs cursor-pointer transition"
                    >
                      <span
                        className={`w-5 h-5 rounded-full ${colors[idx % colors.length]} text-white text-[10px] font-bold flex items-center justify-center`}
                      >
                        {m.name.charAt(0)}
                      </span>
                      <span className="font-semibold text-[#141715]">{m.name}</span>
                      <span className="text-[10px] font-medium text-[#5A605C]">
                        {left > 0 ? "1 Veto" : "Used"}
                      </span>
                    </button>
                  );
                })}
              </div>
              <span className="text-[11px] text-[#5A605C]">
                Active: <strong className="text-[#141715]">{activeUserName}</strong>
              </span>
            </div>
          </div>

          {/* Progressive Disclosure Weather Banner — ONLY visible when Rain Mode or Reroute is active */}
          {(isRainSimulated || isRerouted) && (
            <div className="mb-5">
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
            </div>
          )}

          {/* Split-Screen Workspace: Left Timeline (7 cols) + Right Sticky Map (5 cols) */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Timeline Column */}
            <div className="lg:col-span-7 min-w-0">
              {/* Day Selector Pills with spring layoutId */}
              <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-2 mb-4">
                {dailySchedule.map((day, idx) => {
                  const isSelected = selectedDayIndex === idx;
                  return (
                    <button
                      key={day.day}
                      type="button"
                      onClick={() => setSelectedDayIndex(idx)}
                      className="relative shrink-0 rounded-2xl px-4 py-2.5 text-left border border-[#E6E1D6] bg-white cursor-pointer overflow-hidden"
                    >
                      {isSelected && (
                        <motion.span
                          layoutId="activeDayPill"
                          transition={{ type: "spring", stiffness: 360, damping: 32 }}
                          className="absolute inset-0 rounded-2xl bg-[#141715]"
                        />
                      )}
                      <div className="relative z-10">
                        <div className={`text-xs font-bold ${isSelected ? "text-white" : "text-[#141715]"}`}>
                          Day {day.day}
                        </div>
                        <div className={`text-[11px] ${isSelected ? "text-white/75" : "text-[#5A605C]"}`}>
                          {getDayDateLabel(idx)}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Clean Day Summary Strip */}
              {currentDay && (
                <div className="flex flex-wrap items-center justify-between gap-3 px-1 pb-3 mb-2">
                  <div>
                    <h2 className="font-display text-lg font-semibold text-[#141715] m-0">
                      {currentDay.title || `Day ${currentDay.day}`}
                    </h2>
                    <p className="text-xs text-[#5A605C] m-0">
                      {currentSpots.length} curated stops • shortest-path 2-Opt sequence
                    </p>
                  </div>
                  <div className="flex items-center gap-4 text-xs font-mono-num">
                    <span className="text-[#5A605C]">
                      Cost <strong className="text-[#141715]">{formatCurrency(currentDay.daily_cost_bdt ?? 0, currency)}</strong>
                    </span>
                    <span className="text-[#5A605C]">
                      Transit <strong className="text-[#141715]">{currentDay.daily_distance_km ?? 0} km</strong>
                    </span>
                  </div>
                </div>
              )}

              {/* Breathable Staggered Spot Cards */}
              <StaggerContainer key={`day-${selectedDayIndex}`}>
                {currentSpots.map((spot, index) => (
                  <StaggerItem key={spot.id || index}>
                    <SpotCard
                      spot={spot}
                      index={index}
                      onSelect={onSelectSpot}
                      onVeto={handleVeto}
                      onBook={onBookSpot}
                      userVetoTokens={userTokens}
                      currentMemberName={activeUserName}
                      currency={currency}
                    />
                  </StaggerItem>
                ))}
              </StaggerContainer>
            </div>

            {/* Sticky Interactive Map Column */}
            <div
              id="map-section"
              className={`lg:col-span-5 relative rounded-3xl overflow-hidden border border-[#E6E1D6] bg-white shadow-[0_6px_26px_rgba(20,23,21,0.05)] lg:sticky lg:top-20 transition-all duration-300 ${
                mapExpanded ? "h-[75vh]" : "h-[380px] lg:h-[calc(100vh-7.5rem)]"
              }`}
            >
              <LeafletMap spots={currentSpots} onSelectSpot={onSelectSpot} city={city} isTabActive={true} />
              <button
                type="button"
                onClick={() => {
                  setMapExpanded((e) => !e);
                  setTimeout(() => window.dispatchEvent(new Event("resize")), 320);
                }}
                className="absolute top-3 left-3 z-20 inline-flex items-center gap-1.5 rounded-full bg-white/95 backdrop-blur-md border border-[#E6E1D6] px-3 py-1.5 text-[11px] font-semibold text-[#141715] shadow-sm cursor-pointer hover:bg-[#F8F6F1] transition"
              >
                {mapExpanded ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
                <span>{mapExpanded ? "Compact" : "Expand"}</span>
              </button>
            </div>
          </div>
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
