import React from "react";
import { Star, Car, Shield, Sparkles, ShieldAlert, CalendarCheck, Leaf } from "lucide-react";
import { getSpotImageUrl } from "../assets/images";
import { formatCurrency } from "../api/client";
import { TiltCard } from "./MotionPrimitives";

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
  const imageUrl = getSpotImageUrl(spot);
  const why = spot.why_this || {};
  const badges = why.badges || [];
  const isSub = Boolean(spot.is_weather_substitute);

  const crowdLevel = spot.crowd_level || "Medium";
  const isHiddenGem = Boolean(spot.hidden_gem);
  let crowdPercent = 50;
  let crowdColor = "#C9933B";
  let crowdLabel = "Moderate Flow (50%)";

  if (isHiddenGem || crowdLevel.toLowerCase() === "low") {
    crowdPercent = 25;
    crowdColor = "#25463B";
    crowdLabel = "Peaceful Gem (25%)";
  } else if (crowdLevel.toLowerCase() === "high") {
    crowdPercent = 85;
    crowdColor = "#E85D2A";
    crowdLabel = "Tourist Peak (85%)";
  }

  return (
    <TiltCard
      onClick={() => onSelect(spot)}
      className="spot-card"
      style={{
        background: "#FFFFFF",
        borderRadius: "20px",
        border: isSub ? "2px solid var(--alpine-moss)" : "1px solid var(--stone-border)",
        padding: "16px",
        marginBottom: "12px",
        boxShadow: isSub ? "0 8px 20px rgba(37, 70, 59, 0.14)" : "0 4px 14px rgba(26, 29, 28, 0.04)",
        cursor: "pointer",
        position: "relative",
      }}
    >
      {/* Transit Pill */}
      {index > 0 && spot.transit_est_mins !== undefined && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            fontSize: "11px",
            color: "var(--granite-600)",
            marginBottom: "10px",
            paddingBottom: "8px",
            borderBottom: "1px dashed var(--stone-border)",
            fontWeight: 600,
          }}
        >
          <Car size={13} color="#E85D2A" />
          <span className="font-mono-num">
            {spot.transit_est_mins > 0 ? `${spot.transit_est_mins} mins drive` : "Walking distance"}
            {spot.transit_from_prev_km ? ` (${spot.transit_from_prev_km} km)` : ""}
          </span>
        </div>
      )}

      {/* Body */}
      <div style={{ display: "flex", gap: "14px" }}>
        <div style={{ position: "relative", width: "92px", height: "92px", flexShrink: 0 }}>
          <img
            src={imageUrl}
            alt={spot.name}
            style={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: "14px", background: "var(--stone-muted)" }}
            loading="lazy"
          />
          <div
            className="font-mono-num"
            style={{
              position: "absolute",
              top: "-6px",
              left: "-6px",
              width: "26px",
              height: "26px",
              borderRadius: "50%",
              background: isSub ? "var(--alpine-moss)" : "var(--safety-orange)",
              color: "#FFFFFF",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "12px",
              fontWeight: 800,
              boxShadow: "0 3px 8px rgba(0,0,0,0.24)",
              border: "2px solid #FFFFFF",
            }}
          >
            {index + 1}
          </div>
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "6px" }}>
            <span style={{ fontSize: "11px", fontWeight: 800, color: "var(--safety-orange)", textTransform: "uppercase", letterSpacing: "0.5px" }}>
              {spot.scheduled_slot || `Stop #${index + 1}`}
            </span>
            <span className="font-mono-num" style={{ fontSize: "12px", fontWeight: 700, color: "var(--granite-950)", display: "inline-flex", alignItems: "center", gap: "3px" }}>
              <Star size={12} fill="#C9933B" color="#C9933B" />
              {spot.rating}
            </span>
          </div>

          <h4 className="font-display" style={{ margin: "3px 0 4px 0", fontSize: "16px", fontWeight: 800, color: "var(--granite-950)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
            {spot.name}
          </h4>

          <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: "8px", fontSize: "12px", color: "var(--granite-600)", marginBottom: "8px" }}>
            <span style={{ fontWeight: 700, color: "var(--granite-800)" }}>{spot.category}</span>
            <span>•</span>
            <span className="font-mono-num" style={{ fontWeight: 700, color: "var(--alpine-moss)" }}>
              {spot.estimated_cost_bdt > 0 ? formatCurrency(spot.estimated_cost_bdt, currency) : "Free"}
            </span>
            {spot.local_sme && (
              <>
                <span>•</span>
                <span style={{ display: "inline-flex", alignItems: "center", gap: "3px", color: "var(--alpine-moss)", fontWeight: 700, fontSize: "11px" }}>
                  <Leaf size={11} /> Local SME
                </span>
              </>
            )}
          </div>

          {/* Crowd Gauge */}
          <div style={{ marginBottom: "8px", display: "flex", alignItems: "center", gap: "8px" }}>
            <div style={{ flex: 1, height: "5px", background: "var(--stone-muted)", borderRadius: "999px", overflow: "hidden" }}>
              <div style={{ width: `${crowdPercent}%`, height: "100%", background: crowdColor, borderRadius: "999px" }} />
            </div>
            <span style={{ fontSize: "10px", fontWeight: 700, color: crowdColor, whiteSpace: "nowrap" }}>
              {crowdLabel}
            </span>
          </div>

          {/* Badges */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: "5px" }}>
            {badges.slice(0, 3).map((badge, bIdx) => (
              <span
                key={bIdx}
                style={{
                  fontSize: "10px",
                  fontWeight: 700,
                  padding: "3px 8px",
                  borderRadius: "8px",
                  background: isSub ? "var(--alpine-moss-soft)" : "var(--bg-surface)",
                  color: isSub ? "var(--alpine-moss)" : "var(--granite-800)",
                  border: "1px solid var(--stone-border)",
                }}
              >
                {badge}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Footer Actions: Why This + Reserve + Nash Veto */}
      <div
        style={{
          marginTop: "10px",
          paddingTop: "10px",
          borderTop: "1px solid var(--stone-muted)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "8px",
          flexWrap: "wrap",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "11px", color: "var(--alpine-moss)", fontWeight: 700 }}>
          {isSub ? <Shield size={13} /> : <Sparkles size={13} color="#E85D2A" />}
          <span>{isSub ? "Rain-Safe Substitute" : "Why this? Tap for FairNet breakdown"}</span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          {onBook && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onBook(spot);
              }}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "4px",
                background: "var(--alpine-moss)",
                color: "#FFFFFF",
                border: "none",
                borderRadius: "8px",
                padding: "5px 10px",
                fontSize: "11px",
                fontWeight: 800,
                cursor: "pointer",
              }}
            >
              <CalendarCheck size={12} />
              <span>Reserve</span>
            </button>
          )}

          {onVeto && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onVeto(spot);
              }}
              disabled={userVetoTokens <= 0}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "4px",
                background: userVetoTokens > 0 ? "var(--safety-orange-soft)" : "var(--stone-muted)",
                color: userVetoTokens > 0 ? "var(--safety-orange-hover)" : "var(--granite-600)",
                border: `1px solid ${userVetoTokens > 0 ? "#F7C6B3" : "var(--stone-border)"}`,
                borderRadius: "8px",
                padding: "5px 10px",
                fontSize: "11px",
                fontWeight: 800,
                cursor: userVetoTokens > 0 ? "pointer" : "not-allowed",
              }}
              title={userVetoTokens > 0 ? `Use ${currentMemberName}'s Veto Token` : "No Veto Tokens Left"}
            >
              <ShieldAlert size={12} />
              <span>Nash Veto ({userVetoTokens})</span>
            </button>
          )}
        </div>
      </div>
    </TiltCard>
  );
}
