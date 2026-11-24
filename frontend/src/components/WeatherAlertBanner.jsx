import React from "react";
import { CloudRain, Sun, RotateCcw, AlertTriangle, CheckCircle2 } from "lucide-react";

export default function WeatherAlertBanner({
  city,
  isRainSimulated,
  onToggleRainSimulation,
  onAutoReroute,
  isRerouted,
  onRevertPlan,
  isLoading,
  replannedNotifications = []
}) {
  return (
    <div style={{ marginBottom: "14px" }}>
      {/* Simulation Controls Strip */}
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        background: "#F6F4EF",
        border: "1px solid #E2DDD3",
        borderRadius: "12px",
        padding: "8px 12px",
        marginBottom: "8px",
        fontSize: "12px"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#475569" }}>
          <span style={{ fontWeight: 600 }}>Weather Context Engine:</span>
          <span>{isRainSimulated ? "🌧️ Monsoon Rain Forecast" : "☀️ Clear Weather (31°C)"}</span>
        </div>
        <button
          onClick={onToggleRainSimulation}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "5px",
            background: isRainSimulated ? "#fef3c7" : "#eff6ff",
            color: isRainSimulated ? "#b45309" : "#1d4ed8",
            border: `1px solid ${isRainSimulated ? '#fde68a' : '#bfdbfe'}`,
            padding: "4px 10px",
            borderRadius: "8px",
            fontSize: "11px",
            fontWeight: 700,
            cursor: "pointer"
          }}
        >
          {isRainSimulated ? <Sun size={13} /> : <CloudRain size={13} />}
          {isRainSimulated ? "Reset to Sunny Weather" : "Simulate Heavy Rain Alert"}
        </button>
      </div>

      {/* Dynamic Warning Alert Banner (When Rain is active) */}
      {isRainSimulated && (
        <div style={{
          background: isRerouted
            ? "linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)"
            : "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)",
          border: `1.5px solid ${isRerouted ? '#10b981' : '#f59e0b'}`,
          borderRadius: "14px",
          padding: "12px 14px",
          boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
          animation: "fadeIn 0.25s ease"
        }}>
          <div style={{ display: "flex", alignItems: "flex-start", gap: "10px" }}>
            {isRerouted ? (
              <CheckCircle2 size={20} color="#059669" style={{ flexShrink: 0, marginTop: "2px" }} />
            ) : (
              <AlertTriangle size={20} color="#d97706" style={{ flexShrink: 0, marginTop: "2px" }} />
            )}

            <div style={{ flex: 1 }}>
              <div style={{
                fontSize: "13px",
                fontWeight: 800,
                color: isRerouted ? "#065f46" : "#92400e",
                marginBottom: "3px"
              }}>
                {isRerouted
                  ? "✓ Weather Adaptation Successful: Outdoor Spots Rerouted!"
                  : `⚠️ Rain Alert in ${city}: Outdoor spots risk flooding & disruptions!`}
              </div>

              <div style={{
                fontSize: "12px",
                color: isRerouted ? "#047857" : "#b45309",
                lineHeight: 1.4,
                marginBottom: "8px"
              }}>
                {isRerouted
                  ? (replannedNotifications.length > 0 ? replannedNotifications.join(" ") : "Itinerary automatically swapped outdoor locations with high-rated indoor museums and cultural spots.")
                  : `Continuous rainfall detected in ${city}. TripSense context engine recommends auto-rerouting outdoor POIs to indoor heritage museums.`}
              </div>

              {/* Action buttons */}
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                {!isRerouted ? (
                  <button
                    onClick={onAutoReroute}
                    disabled={isLoading}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "6px",
                      background: "#d97706",
                      color: "#ffffff",
                      border: "none",
                      padding: "6px 12px",
                      borderRadius: "8px",
                      fontSize: "12px",
                      fontWeight: 700,
                      cursor: isLoading ? "not-allowed" : "pointer",
                      boxShadow: "0 2px 6px rgba(217, 119, 6, 0.3)"
                    }}
                  >
                    <CloudRain size={14} />
                    {isLoading ? "Rerouting Schedule..." : "Auto-Reroute to Indoor Landmarks 🌧️"}
                  </button>
                ) : (
                  <button
                    onClick={onRevertPlan}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "6px",
                      background: "#ffffff",
                      color: "#065f46",
                      border: "1px solid #10b981",
                      padding: "5px 12px",
                      borderRadius: "8px",
                      fontSize: "11px",
                      fontWeight: 700,
                      cursor: "pointer"
                    }}
                  >
                    <RotateCcw size={12} />
                    Revert to Original Plan ☀️
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
