import React from "react";
import { Sparkles, Compass, Leaf, ShieldCheck, ArrowUpRight, Layers, Cpu } from "lucide-react";
import { MagneticButton, ScrollReveal, ParallaxPhoto, StaggerContainer, StaggerItem } from "./MotionPrimitives";

export default function EditorialHero({
  city = "Chittagong",
  fairnessScore = 78.4,
  co2SavedKg = 11.6,
  lang = "EN",
  currentUser,
  connectionState,
  onStartSwipe,
  onOpenWizard,
  onOpenLogin,
  onOpenMlLab,
  onOpenConnect,
}) {
  const isBn = lang === "BN";
  const isLiveApi = connectionState?.mode === "live";

  return (
    <ScrollReveal>
      <section
        className="editorial-card editorial-grain"
        style={{
          position: "relative",
          padding: "32px 28px",
          marginBottom: "26px",
          overflow: "hidden",
        }}
      >
        {/* Subtle Editorial Topographic Texture Accent */}
        <div
          style={{
            position: "absolute",
            top: "-60px",
            right: "-60px",
            width: "320px",
            height: "320px",
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(232,93,42,0.08) 0%, rgba(37,70,59,0.04) 55%, transparent 72%)",
            pointerEvents: "none",
          }}
        />

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
            gap: "28px",
            alignItems: "center",
          }}
        >
          {/* Left Editorial Column */}
          <div>
            <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "8px", marginBottom: "14px" }}>
              <span
                style={{
                  background: "var(--alpine-moss-soft)",
                  color: "var(--alpine-moss)",
                  border: "1px solid #C5D9CE",
                  padding: "5px 12px",
                  borderRadius: "999px",
                  fontSize: "11px",
                  fontWeight: 800,
                  letterSpacing: "0.4px",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                <Layers size={12} />
                TRIPSENSE-FAIRNET v3.0 • NEURO-SYMBOLIC AI
              </span>
              <span
                style={{
                  background: "var(--safety-orange-soft)",
                  color: "var(--safety-orange-hover)",
                  border: "1px solid #F7C6B3",
                  padding: "5px 12px",
                  borderRadius: "999px",
                  fontSize: "11px",
                  fontWeight: 700,
                }}
              >
                {isBn ? "জিরো হ্যালুসিনেশন গ্যারান্টি" : "0% Hallucination Guarantee"}
              </span>
            </div>

            <h1
              className="font-display"
              style={{
                fontSize: "clamp(28px, 4vw, 42px)",
                fontWeight: 900,
                lineHeight: 1.08,
                color: "var(--granite-950)",
                margin: "0 0 14px 0",
                letterSpacing: "-0.02em",
              }}
            >
              {isBn ? (
                <>
                  দলগত ভ্রমণের <span style={{ color: "var(--safety-orange)", fontStyle: "italic" }}>সুষম ঐকমত্য</span> ও পরিবেশবান্ধব রুট।
                </>
              ) : (
                <>
                  Travel together without{" "}
                  <span style={{ color: "var(--safety-orange)", fontStyle: "italic" }}>compromise</span>—guided by FairNet AI.
                </>
              )}
            </h1>

            <p
              style={{
                fontSize: "14px",
                lineHeight: 1.65,
                color: "var(--granite-600)",
                margin: "0 0 22px 0",
                maxWidth: "560px",
              }}
            >
              {isBn
                ? `${city} ও বাংলাদেশের সেরা স্থানগুলোতে বন্ধুদের আলাদা পছন্দ, বাজেট এবং বৃষ্টির পূর্বাভাস মিলিয়ে নিখুঁত রুট তৈরি করুন—স্থানীয় কমিউনিটি ও কার্বন সাশ্রয়ের সাথে।`
                : `Calibrate your squad's real tastes in 5 active swipes, balance conflicting budgets with our trained TripSense-FairNet neural consensus model, and reroute live during monsoon rain while supporting local SMEs in ${city}.`}
            </p>

            {/* Primary CTA Buttons */}
            <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", alignItems: "center" }}>
              <MagneticButton
                onClick={onStartSwipe}
                style={{
                  background: "var(--safety-orange)",
                  color: "#FFFFFF",
                  border: "none",
                  borderRadius: "14px",
                  padding: "13px 22px",
                  fontSize: "13px",
                  fontWeight: 800,
                  cursor: "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                  boxShadow: "0 10px 22px rgba(232, 93, 42, 0.28)",
                }}
              >
                <Sparkles size={15} />
                <span>{isBn ? "অ্যাক্টিভ সোয়াইপ কুইজ শুরু করুন" : "Launch Active Taste Swipe"}</span>
              </MagneticButton>

              <MagneticButton
                onClick={onOpenWizard}
                style={{
                  background: "var(--granite-950)",
                  color: "#FFFFFF",
                  border: "none",
                  borderRadius: "14px",
                  padding: "13px 20px",
                  fontSize: "13px",
                  fontWeight: 700,
                  cursor: "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                <Compass size={15} />
                <span>{isBn ? "ট্রিপ সেটআপ উইজার্ড" : "Configure Squad Trip"}</span>
              </MagneticButton>

              {!currentUser && (
                <button
                  type="button"
                  onClick={onOpenLogin}
                  style={{
                    background: "var(--bg-surface)",
                    color: "var(--granite-950)",
                    border: "1px solid var(--stone-border)",
                    borderRadius: "14px",
                    padding: "12px 16px",
                    fontSize: "13px",
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  Passport Sign-In
                </button>
              )}

              <button
                type="button"
                onClick={onOpenMlLab}
                style={{
                  background: "transparent",
                  color: "var(--alpine-moss)",
                  border: "none",
                  padding: "10px 8px",
                  fontSize: "12px",
                  fontWeight: 800,
                  cursor: "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                  textDecoration: "underline",
                  textUnderlineOffset: "4px",
                }}
              >
                <span>Inspect Q1 ML Benchmarks</span>
                <ArrowUpRight size={14} />
              </button>
            </div>
          </div>

          {/* Right Staggered Editorial Photo Collage + Overlapping Telemetry Card */}
          <StaggerContainer style={{ position: "relative", minHeight: "280px", display: "grid", gridTemplateColumns: "1.18fr 0.82fr", gap: "12px", alignItems: "stretch" }}>
            <StaggerItem style={{ position: "relative", borderRadius: "20px", overflow: "hidden", minHeight: "260px", border: "1px solid var(--stone-border)" }}>
              <ParallaxPhoto
                src="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80"
                alt="Coastal Expedition"
                style={{ width: "100%", height: "100%", minHeight: "260px" }}
              />
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  background: "linear-gradient(to top, rgba(18,23,21,0.84) 0%, transparent 55%)",
                  pointerEvents: "none",
                }}
              />
              <div style={{ position: "absolute", bottom: "14px", left: "14px", right: "14px", color: "#FFFFFF" }}>
                <div className="font-mono-num" style={{ fontSize: "10px", opacity: 0.85, letterSpacing: "0.8px" }}>
                  22.3569° N, 91.7832° E
                </div>
                <div className="font-display" style={{ fontSize: "18px", fontWeight: 700 }}>
                  {city} Coastal & Heritage Trail
                </div>
              </div>
            </StaggerItem>

            <StaggerItem style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div style={{ position: "relative", borderRadius: "18px", overflow: "hidden", flex: 1, minHeight: "124px", border: "1px solid var(--stone-border)" }}>
                <ParallaxPhoto
                  src="https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=600&q=80"
                  alt="Eco Forest"
                  style={{ width: "100%", height: "100%", minHeight: "124px" }}
                />
                <div
                  style={{
                    position: "absolute",
                    top: "10px",
                    left: "10px",
                    background: "rgba(31, 75, 62, 0.92)",
                    color: "#FFFFFF",
                    padding: "4px 10px",
                    borderRadius: "999px",
                    fontSize: "10px",
                    fontWeight: 700,
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "4px",
                  }}
                >
                  <Leaf size={11} />
                  <span>-{co2SavedKg} kg CO₂</span>
                </div>
              </div>

              {/* Overlapping Metric & Live Engine Telemetry Card */}
              <div
                style={{
                  background: "var(--granite-950)",
                  color: "#F7F4EE",
                  borderRadius: "18px",
                  padding: "14px",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span style={{ fontSize: "10px", fontWeight: 700, color: "#B8C0BC", letterSpacing: "0.6px" }}>
                    GROUP FAIRNESS
                  </span>
                  <ShieldCheck size={14} color="#D94E28" />
                </div>
                <div className="font-mono-num" style={{ fontSize: "24px", fontWeight: 700, margin: "4px 0" }}>
                  {fairnessScore}
                  <span style={{ fontSize: "12px", color: "#9AA39F", fontWeight: 500 }}>/100</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "6px", flexWrap: "wrap" }}>
                  <span style={{ fontSize: "10px", color: "#9FE0C4", fontWeight: 600 }}>
                    ✓ FairNet Protected
                  </span>
                  {onOpenConnect && (
                    <button
                      type="button"
                      onClick={onOpenConnect}
                      style={{
                        background: isLiveApi ? "rgba(159,224,196,0.16)" : "rgba(184,134,59,0.22)",
                        color: isLiveApi ? "#9FE0C4" : "#F3D39A",
                        border: "1px solid rgba(255,255,255,0.14)",
                        borderRadius: "999px",
                        padding: "2px 8px",
                        fontSize: "9px",
                        fontWeight: 800,
                        cursor: "pointer",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "4px",
                      }}
                    >
                      <Cpu size={10} />
                      <span>{isLiveApi ? "Live AI" : "Instant Demo"}</span>
                    </button>
                  )}
                </div>
              </div>
            </StaggerItem>
          </StaggerContainer>
        </div>
      </section>
    </ScrollReveal>
  );
}
