import React, { useState, useRef } from "react";
import { MoveHorizontal, AlertTriangle, CheckCircle2 } from "lucide-react";
import { ScrollReveal } from "./MotionPrimitives";

export default function BeforeAfterComparer({ city = "Chittagong" }) {
  const [sliderPct, setSliderPct] = useState(52);
  const containerRef = useRef(null);
  const isDraggingRef = useRef(false);

  const updateFromClientX = (clientX) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const pct = ((clientX - rect.left) / rect.width) * 100;
    setSliderPct(Math.max(8, Math.min(92, pct)));
  };

  return (
    <ScrollReveal delay={0.05}>
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
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "flex-end", gap: "12px", marginBottom: "16px" }}>
          <div>
            <div style={{ fontSize: "11px", fontWeight: 800, color: "var(--safety-orange)", letterSpacing: "0.7px", textTransform: "uppercase" }}>
              Interactive Showcase Comparison
            </div>
            <h2 className="font-display" style={{ fontSize: "22px", fontWeight: 800, color: "var(--granite-950)", margin: "4px 0 0 0" }}>
              Drag to Compare: Ordinary App vs. TripSense FairNet
            </h2>
          </div>
          <div style={{ fontSize: "12px", color: "var(--granite-600)", fontWeight: 600 }}>
            Slide the handle across {city} itinerary metrics
          </div>
        </div>

        {/* Interactive Drag-to-Slide Viewport */}
        <div
          ref={containerRef}
          onPointerDown={(e) => {
            isDraggingRef.current = true;
            updateFromClientX(e.clientX);
          }}
          onPointerMove={(e) => {
            if (isDraggingRef.current) updateFromClientX(e.clientX);
          }}
          onPointerUp={() => {
            isDraggingRef.current = false;
          }}
          onPointerLeave={() => {
            isDraggingRef.current = false;
          }}
          style={{
            position: "relative",
            width: "100%",
            minHeight: "260px",
            borderRadius: "18px",
            overflow: "hidden",
            border: "1px solid var(--stone-border)",
            userSelect: "none",
            touchAction: "none",
            cursor: "ew-resize",
          }}
        >
          {/* RIGHT LAYER (AFTER: TripSense FairNet + Eco Plan) */}
          <div
            style={{
              width: "100%",
              minHeight: "260px",
              background: "linear-gradient(135deg, #1E3A30 0%, #25463B 100%)",
              color: "#F6F4EF",
              padding: "24px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
            }}
          >
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <span
                style={{
                  background: "rgba(255,255,255,0.14)",
                  border: "1px solid rgba(255,255,255,0.22)",
                  padding: "5px 12px",
                  borderRadius: "999px",
                  fontSize: "11px",
                  fontWeight: 800,
                  color: "#A7F3D0",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                <CheckCircle2 size={13} />
                AFTER: TRIPSENSE FAIRNET + ECO
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "12px", marginTop: "20px" }}>
              <div style={{ background: "rgba(255,255,255,0.08)", borderRadius: "14px", padding: "14px", border: "1px solid rgba(255,255,255,0.1)" }}>
                <div style={{ fontSize: "11px", color: "#B8D6C9", fontWeight: 700 }}>CROWD LEVEL</div>
                <div className="font-mono-num" style={{ fontSize: "24px", fontWeight: 800, color: "#FFFFFF", marginTop: "4px" }}>26%</div>
                <div style={{ fontSize: "11px", color: "#A7F3D0" }}>Peaceful Hidden Gems</div>
              </div>
              <div style={{ background: "rgba(255,255,255,0.08)", borderRadius: "14px", padding: "14px", border: "1px solid rgba(255,255,255,0.1)" }}>
                <div style={{ fontSize: "11px", color: "#B8D6C9", fontWeight: 700 }}>CARBON FOOTPRINT</div>
                <div className="font-mono-num" style={{ fontSize: "24px", fontWeight: 800, color: "#FFFFFF", marginTop: "4px" }}>6.2 kg</div>
                <div style={{ fontSize: "11px", color: "#A7F3D0" }}>66% CO₂ Saved vs Car</div>
              </div>
              <div style={{ background: "rgba(255,255,255,0.08)", borderRadius: "14px", padding: "14px", border: "1px solid rgba(255,255,255,0.1)" }}>
                <div style={{ fontSize: "11px", color: "#B8D6C9", fontWeight: 700 }}>GROUP FAIRNESS</div>
                <div className="font-mono-num" style={{ fontSize: "24px", fontWeight: 800, color: "#FFFFFF", marginTop: "4px" }}>Gini 0.08</div>
                <div style={{ fontSize: "11px", color: "#A7F3D0" }}>All 3 Friends Happy</div>
              </div>
              <div style={{ background: "rgba(255,255,255,0.08)", borderRadius: "14px", padding: "14px", border: "1px solid rgba(255,255,255,0.1)" }}>
                <div style={{ fontSize: "11px", color: "#B8D6C9", fontWeight: 700 }}>LOCAL SME SHARE</div>
                <div className="font-mono-num" style={{ fontSize: "24px", fontWeight: 800, color: "#FFFFFF", marginTop: "4px" }}>86%</div>
                <div style={{ fontSize: "11px", color: "#A7F3D0" }}>0% AI Hallucination</div>
              </div>
            </div>
          </div>

          {/* LEFT LAYER (BEFORE: Generic / Unoptimized Tourist Plan) Clipped by sliderPct */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              clipPath: `inset(0 ${100 - sliderPct}% 0 0)`,
              background: "linear-gradient(135deg, #2A2F2D 0%, #1A1D1C 100%)",
              color: "#F6F4EF",
              padding: "24px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
            }}
          >
            <div style={{ display: "flex", justifyContent: "flex-start" }}>
              <span
                style={{
                  background: "rgba(232, 93, 42, 0.2)",
                  border: "1px solid rgba(232, 93, 42, 0.55)",
                  padding: "5px 12px",
                  borderRadius: "999px",
                  fontSize: "11px",
                  fontWeight: 800,
                  color: "#FFB396",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                <AlertTriangle size={13} />
                BEFORE: STANDARD OVERCROWDED APP
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "12px", marginTop: "20px" }}>
              <div style={{ background: "rgba(255,255,255,0.06)", borderRadius: "14px", padding: "14px", border: "1px solid rgba(255,255,255,0.08)" }}>
                <div style={{ fontSize: "11px", color: "#B8C0BC", fontWeight: 700 }}>CROWD LEVEL</div>
                <div className="font-mono-num" style={{ fontSize: "24px", fontWeight: 800, color: "#FF8B60", marginTop: "4px" }}>86%</div>
                <div style={{ fontSize: "11px", color: "#D6CCC2" }}>Peak Tourist Trap</div>
              </div>
              <div style={{ background: "rgba(255,255,255,0.06)", borderRadius: "14px", padding: "14px", border: "1px solid rgba(255,255,255,0.08)" }}>
                <div style={{ fontSize: "11px", color: "#B8C0BC", fontWeight: 700 }}>CARBON FOOTPRINT</div>
                <div className="font-mono-num" style={{ fontSize: "24px", fontWeight: 800, color: "#FF8B60", marginTop: "4px" }}>18.4 kg</div>
                <div style={{ fontSize: "11px", color: "#D6CCC2" }}>Unoptimized Zig-Zag</div>
              </div>
              <div style={{ background: "rgba(255,255,255,0.06)", borderRadius: "14px", padding: "14px", border: "1px solid rgba(255,255,255,0.08)" }}>
                <div style={{ fontSize: "11px", color: "#B8C0BC", fontWeight: 700 }}>GROUP FAIRNESS</div>
                <div className="font-mono-num" style={{ fontSize: "24px", fontWeight: 800, color: "#FF8B60", marginTop: "4px" }}>1 Miserable</div>
                <div style={{ fontSize: "11px", color: "#D6CCC2" }}>Budget Member Ignored</div>
              </div>
              <div style={{ background: "rgba(255,255,255,0.06)", borderRadius: "14px", padding: "14px", border: "1px solid rgba(255,255,255,0.08)" }}>
                <div style={{ fontSize: "11px", color: "#B8C0BC", fontWeight: 700 }}>AI RELIABILITY</div>
                <div className="font-mono-num" style={{ fontSize: "24px", fontWeight: 800, color: "#FF8B60", marginTop: "4px" }}>78% Fake</div>
                <div style={{ fontSize: "11px", color: "#D6CCC2" }}>Closed / Hallucinated</div>
              </div>
            </div>
          </div>

          {/* Vertical Divider Line & Handle */}
          <div
            style={{
              position: "absolute",
              top: 0,
              bottom: 0,
              left: `${sliderPct}%`,
              width: "3px",
              background: "#FFFFFF",
              boxShadow: "0 0 12px rgba(0,0,0,0.45)",
              transform: "translateX(-50%)",
              pointerEvents: "none",
            }}
          >
            <div
              style={{
                position: "absolute",
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)",
                width: "40px",
                height: "40px",
                borderRadius: "50%",
                background: "var(--safety-orange)",
                color: "#FFFFFF",
                border: "3px solid #FFFFFF",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 4px 16px rgba(0,0,0,0.35)",
              }}
            >
              <MoveHorizontal size={18} />
            </div>
          </div>
        </div>
      </section>
    </ScrollReveal>
  );
}
