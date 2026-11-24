import React, { useState } from "react";
import { Compass, Shield, X } from "lucide-react";

export default function EditorialFooter({ onOpenMlLab }) {
  const [legalModal, setLegalModal] = useState(null);

  return (
    <>
      <footer
        style={{
          background: "#1A1D1C",
          color: "#E2DDD3",
          padding: "36px 24px 90px 24px",
          marginTop: "32px",
          borderTop: "1px solid #2A2F2D",
        }}
      >
        <div
          style={{
            maxWidth: "1320px",
            margin: "0 auto",
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "24px",
            alignItems: "start",
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "10px" }}>
              <div
                style={{
                  width: "34px",
                  height: "34px",
                  borderRadius: "10px",
                  background: "var(--safety-orange)",
                  color: "#FFFFFF",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Compass size={19} />
              </div>
              <span className="font-display" style={{ fontSize: "20px", fontWeight: 900, color: "#FAF9F6" }}>
                TripSense
              </span>
            </div>
            <p style={{ fontSize: "12px", color: "#9AA39F", lineHeight: 1.6, margin: 0 }}>
              Explainable, Group-Aware & Sustainable Travel Companion powered by TripSense-FairNet, SigLIP Active Learning, and Neuro-Symbolic RAG.
            </p>
          </div>

          <div>
            <div style={{ fontSize: "11px", fontWeight: 800, color: "#FF9F7A", letterSpacing: "0.7px", marginBottom: "10px" }}>
              RESEARCH & ARCHITECTURE
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "12px" }}>
              <button
                type="button"
                onClick={onOpenMlLab}
                style={{ background: "none", border: "none", color: "#E2DDD3", textAlign: "left", padding: 0, cursor: "pointer", fontWeight: 600 }}
              >
                Q1 Benchmark Results & SHAP Lab
              </button>
              <span style={{ color: "#9AA39F" }}>Daffodil International University (CSE)</span>
              <span style={{ color: "#9AA39F" }}>Dataset: Massive-STEPS & TravelPlanner</span>
            </div>
          </div>

          <div>
            <div style={{ fontSize: "11px", fontWeight: 800, color: "#9FE0C4", letterSpacing: "0.7px", marginBottom: "10px" }}>
              GOVERNANCE & LEGAL
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "12px", fontSize: "12px" }}>
              <button
                type="button"
                onClick={() => setLegalModal("Privacy Policy (GDPR & Local Cache)")}
                style={{ background: "none", border: "none", color: "#E2DDD3", padding: 0, cursor: "pointer", textDecoration: "underline" }}
              >
                Privacy Policy
              </button>
              <button
                type="button"
                onClick={() => setLegalModal("Terms of Service")}
                style={{ background: "none", border: "none", color: "#E2DDD3", padding: 0, cursor: "pointer", textDecoration: "underline" }}
              >
                Terms of Service
              </button>
              <button
                type="button"
                onClick={() => setLegalModal("Sustainability & Local SME Charter")}
                style={{ background: "none", border: "none", color: "#E2DDD3", padding: 0, cursor: "pointer", textDecoration: "underline" }}
              >
                Sustainability Charter
              </button>
              <button
                type="button"
                onClick={() => setLegalModal("Impressum & Academic Attribution")}
                style={{ background: "none", border: "none", color: "#E2DDD3", padding: 0, cursor: "pointer", textDecoration: "underline" }}
              >
                Impressum
              </button>
            </div>
            <div style={{ marginTop: "14px", fontSize: "11px", color: "#7C8581" }}>
              © 2026 Sabbirhossansani • TripSense Sustainable Travel Platform
            </div>
          </div>
        </div>
      </footer>

      {legalModal && (
        <div
          onClick={() => setLegalModal(null)}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 100005,
            background: "rgba(26, 29, 28, 0.72)",
            backdropFilter: "blur(6px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "16px",
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "#FAF9F6",
              borderRadius: "20px",
              padding: "24px",
              maxWidth: "460px",
              width: "100%",
              border: "1px solid var(--stone-border)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: 800, fontSize: "15px" }}>
                <Shield size={16} color="#25463B" />
                <span>{legalModal}</span>
              </div>
              <button
                type="button"
                onClick={() => setLegalModal(null)}
                style={{ background: "none", border: "none", cursor: "pointer" }}
              >
                <X size={18} />
              </button>
            </div>
            <p style={{ fontSize: "13px", lineHeight: 1.6, color: "var(--granite-600)", margin: 0 }}>
              TripSense enforces strict on-device itinerary caching, zero third-party ad tracking, and transparent partner revenue attribution (80–98% directly retained by verified local SME hosts). All AI Copilot responses pass deterministic symbolic fact-checking prior to display.
            </p>
          </div>
        </div>
      )}
    </>
  );
}
