import React, { useState } from "react";
import { Shield, X } from "lucide-react";

export default function CookieConsentBanner() {
  const [consent, setConsent] = useState(() => {
    try {
      return localStorage.getItem("tripsense_privacy_consent") || "";
    } catch {
      return "";
    }
  });
  const [showSettings, setShowSettings] = useState(false);

  if (consent) return null;

  const saveChoice = (val) => {
    try {
      localStorage.setItem("tripsense_privacy_consent", val);
    } catch {}
    setConsent(val);
  };

  return (
    <div
      className="glass-panel"
      style={{
        position: "fixed",
        bottom: "18px",
        left: "18px",
        zIndex: 9000,
        maxWidth: "390px",
        borderRadius: "20px",
        padding: "16px 18px",
        border: "1px solid var(--stone-border)",
        boxShadow: "0 18px 40px rgba(26, 29, 28, 0.16)",
        animation: "slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
      }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "10px", marginBottom: "8px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "7px", fontSize: "12px", fontWeight: 800, color: "var(--granite-950)" }}>
          <Shield size={15} color="#25463B" />
          <span>Privacy & Offline Telemetry</span>
        </div>
        <button
          type="button"
          onClick={() => saveChoice("necessary")}
          style={{ background: "transparent", border: "none", cursor: "pointer", color: "var(--granite-600)", padding: 0 }}
          aria-label="Close privacy banner"
        >
          <X size={15} />
        </button>
      </div>

      <p style={{ fontSize: "11px", lineHeight: 1.5, color: "var(--granite-600)", margin: "0 0 12px 0" }}>
        TripSense stores your itinerary, Eco-Points wallet, and expense ledger locally for offline resilience and GDPR-aligned transparency.
      </p>

      {showSettings && (
        <div style={{ background: "var(--bg-surface)", borderRadius: "10px", padding: "8px 10px", marginBottom: "10px", fontSize: "11px", color: "var(--granite-800)", border: "1px solid var(--stone-border)" }}>
          <div>✓ Strictly Necessary: Offline Itinerary & Expense Ledger</div>
          <div>✓ Active Swipe Taste Calibration (On-Device / Session)</div>
        </div>
      )}

      <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
        <button
          type="button"
          onClick={() => saveChoice("necessary")}
          style={{
            flex: 1,
            background: "#FFFFFF",
            color: "var(--granite-950)",
            border: "1px solid var(--stone-border)",
            borderRadius: "10px",
            padding: "7px 10px",
            fontSize: "11px",
            fontWeight: 700,
            cursor: "pointer",
          }}
        >
          Accept Necessary
        </button>
        <button
          type="button"
          onClick={() => setShowSettings(!showSettings)}
          style={{
            background: "transparent",
            color: "var(--granite-600)",
            border: "1px solid var(--stone-border)",
            borderRadius: "10px",
            padding: "7px 10px",
            fontSize: "11px",
            fontWeight: 700,
            cursor: "pointer",
          }}
        >
          Settings
        </button>
        <button
          type="button"
          onClick={() => saveChoice("all")}
          style={{
            flex: 1,
            background: "var(--alpine-moss)",
            color: "#FFFFFF",
            border: "none",
            borderRadius: "10px",
            padding: "7px 10px",
            fontSize: "11px",
            fontWeight: 800,
            cursor: "pointer",
          }}
        >
          Accept All
        </button>
      </div>
    </div>
  );
}
