import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Star,
  Car,
  ShieldAlert,
  CalendarCheck,
  Leaf,
  ChevronDown,
  Sparkles,
  Home,
} from "lucide-react";
import { getSpotImageUrl } from "../assets/images";
import { formatCurrency } from "../api/client";

export default function SpotCard({
  spot,
  index,
  onSelect,
  onVeto,
  onBook,
  userVetoTokens = 1,
  currentMemberName = "Rahat",
  currency = "BDT",
}) {
  const [showWhy, setShowWhy] = useState(false);
  const imageUrl = getSpotImageUrl(spot);
  const why = spot.why_this || {};
  const isSub = Boolean(spot.is_weather_substitute);
  const memberBreakdown = spot.group_consensus?.member_breakdown || {};

  return (
    <div className="mb-3.5">
      {/* Subtle Transit Connector between stops */}
      {index > 0 && spot.transit_est_mins !== undefined && (
        <div className="flex items-center gap-2 pl-5 py-1.5 text-[11px] font-medium text-[#5A605C]">
          <span className="w-px h-4 bg-[#DDD6C7]" />
          <Car className="w-3.5 h-3.5 text-[#D94E28]" />
          <span className="font-mono-num">
            {spot.transit_est_mins > 0 ? `${spot.transit_est_mins} min` : "Walk"}
            {spot.transit_from_prev_km ? ` • ${spot.transit_from_prev_km} km` : ""}
          </span>
        </div>
      )}

      {/* Calm, Breathable Editorial Card */}
      <article
        onClick={() => onSelect(spot)}
        className={`group rounded-2xl bg-white p-4 sm:p-5 border transition-all duration-200 cursor-pointer ${
          isSub
            ? "border-[#1E4D3F] shadow-[0_6px_22px_rgba(30,77,63,0.1)]"
            : "border-[#E6E1D6] hover:border-[#CFC6B4] shadow-[0_2px_10px_rgba(20,23,21,0.03)] hover:shadow-[0_10px_28px_rgba(20,23,21,0.07)]"
        }`}
      >
        <div className="flex gap-4 items-start">
          {/* Crisp Photo Thumbnail */}
          <div className="relative w-22 h-22 sm:w-28 sm:h-28 rounded-2xl overflow-hidden shrink-0 bg-[#EFECE4]">
            <img
              src={imageUrl}
              alt={spot.name}
              loading="lazy"
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
            <span
              className={`font-mono-num absolute top-2 left-2 w-6 h-6 rounded-full text-white text-[11px] font-bold flex items-center justify-center shadow ${
                isSub ? "bg-[#1E4D3F]" : "bg-[#141715]/85 backdrop-blur-sm"
              }`}
            >
              {index + 1}
            </span>
          </div>

          {/* Primary Content Column */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <span className="text-[11px] font-bold uppercase tracking-[0.08em] text-[#D94E28] truncate">
                {spot.scheduled_slot ? spot.scheduled_slot.split("(")[0].trim() : `Stop ${index + 1}`}
                {isSub ? " • Rain Safe" : ""}
              </span>
              <span className="font-mono-num inline-flex items-center gap-1 text-xs font-semibold text-[#141715] shrink-0">
                <Star className="w-3.5 h-3.5 fill-[#B8863B] text-[#B8863B]" />
                {spot.rating}
              </span>
            </div>

            <h4 className="font-display text-base sm:text-lg font-semibold text-[#141715] mt-1 leading-snug truncate">
              {spot.name.split("(")[0].trim()}
            </h4>

            {/* Clean 3-Item Metadata Row (Zero Badge Soup!) */}
            <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-[#5A605C]">
              <span className="px-2.5 py-0.5 rounded-full bg-[#F8F6F1] border border-[#E6E1D6] font-medium text-[#141715]">
                {spot.category}
              </span>
              <span className="font-mono-num font-semibold text-[#141715]">
                {spot.estimated_cost_bdt > 0 ? formatCurrency(spot.estimated_cost_bdt, currency) : "Free"}
              </span>
              {spot.indoor_outdoor === "Indoor" ? (
                <span className="inline-flex items-center gap-1 text-[#1E4D3F] font-medium">
                  <Home className="w-3 h-3" /> Indoor
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-[#1E4D3F] font-medium">
                  <Leaf className="w-3 h-3" /> Eco {spot.sustainability_score || 85}
                </span>
              )}
            </div>

            {/* Clean Action Bar + Progressive Disclosure Toggle */}
            <div className="mt-3.5 pt-3 border-t border-[#F1EDE5] flex flex-wrap items-center justify-between gap-2">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowWhy((s) => !s);
                }}
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#5A605C] hover:text-[#141715] bg-transparent border-none p-0 cursor-pointer"
              >
                <Sparkles className="w-3.5 h-3.5 text-[#1E4D3F]" />
                <span>Why FairNet picked this</span>
                <ChevronDown
                  className={`w-3.5 h-3.5 transition-transform ${showWhy ? "rotate-180" : ""}`}
                />
              </button>

              <div className="flex items-center gap-2">
                {onBook && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onBook(spot);
                    }}
                    className="inline-flex items-center gap-1.5 rounded-full bg-[#E8F2EE] hover:bg-[#1E4D3F] text-[#1E4D3F] hover:text-white px-3 py-1.5 text-[11px] font-semibold border-none transition cursor-pointer"
                  >
                    <CalendarCheck className="w-3.5 h-3.5" />
                    <span>Reserve</span>
                  </button>
                )}

                {onVeto && (
                  <button
                    type="button"
                    disabled={userVetoTokens <= 0}
                    title={
                      userVetoTokens > 0
                        ? `Use ${currentMemberName}'s Nash Veto token`
                        : "Veto token already used"
                    }
                    onClick={(e) => {
                      e.stopPropagation();
                      onVeto(spot);
                    }}
                    className={`inline-flex items-center gap-1 rounded-full px-3 py-1.5 text-[11px] font-semibold border transition ${
                      userVetoTokens > 0
                        ? "bg-white hover:bg-[#FDF0EB] text-[#141715] hover:text-[#D94E28] border-[#E6E1D6] hover:border-[#F2C3B2] cursor-pointer"
                        : "bg-[#F8F6F1] text-[#9BA09D] border-[#ECE7DC] cursor-not-allowed"
                    }`}
                  >
                    <ShieldAlert className="w-3.5 h-3.5" />
                    <span>Veto ({userVetoTokens})</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Progressive Disclosure: FairNet Explanation Drawer */}
        <AnimatePresence>
          {showWhy && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.24, ease: [0.22, 1, 0.36, 1] }}
              onClick={(e) => e.stopPropagation()}
              className="overflow-hidden"
            >
              <div className="mt-3.5 pt-3 border-t border-dashed border-[#E6E1D6] text-xs text-[#5A605C] space-y-2.5">
                <p className="m-0 leading-relaxed text-[#262C29]">
                  {why.narrative || spot.description}
                </p>
                {Object.keys(memberBreakdown).length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(memberBreakdown).map(([name, score]) => (
                      <span
                        key={name}
                        className="font-mono-num text-[11px] bg-[#F8F6F1] border border-[#E6E1D6] px-2.5 py-0.5 rounded-full text-[#141715]"
                      >
                        {name}: <strong>{score}%</strong>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </article>
    </div>
  );
}
