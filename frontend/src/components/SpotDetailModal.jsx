import React from "react";
import { X, Star, Sparkles, ShieldCheck, ShieldAlert, CalendarCheck, Store } from "lucide-react";
import { getSpotImageUrl } from "../assets/images";
import { formatCurrency } from "../api/client";

export default function SpotDetailModal({
  spot,
  onClose,
  onVeto,
  onBook,
  userVetoTokens = 1,
  currentMemberName: _currentMemberName = "Rahat",
  currency = "BDT",
}) {
  if (!spot) return null;

  const imageUrl = getSpotImageUrl(spot);
  const why = spot.why_this || {};
  const badges = why.badges || [];
  const consensus = spot.group_consensus || {};
  const memberBreakdown = consensus.member_breakdown || {};
  const featureAttrs = why.feature_attributions || spot.feature_attributions || null;

  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 10000,
        backgroundColor: "rgba(26, 29, 28, 0.65)",
        backdropFilter: "blur(6px)",
        display: "flex",
        alignItems: "flex-end",
        justifyContent: "center",
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          backgroundColor: "#FAF9F6",
          width: "100%",
          maxWidth: "560px",
          maxHeight: "90vh",
          borderTopLeftRadius: "28px",
          borderTopRightRadius: "28px",
          overflowY: "auto",
          boxShadow: "0 -12px 40px rgba(0,0,0,0.28)",
          animation: "slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
        }}
      >
        <div style={{ position: "relative", height: "225px", width: "100%" }}>
          <img src={imageUrl} alt={spot.name} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to top, rgba(26,29,28,0.88) 0%, transparent 65%)" }} />

          <button
            type="button"
            onClick={onClose}
            style={{
              position: "absolute",
              top: "14px",
              right: "14px",
              background: "rgba(26,29,28,0.7)",
              border: "none",
              borderRadius: "50%",
              width: "36px",
              height: "36px",
              color: "#FFFFFF",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <X size={20} />
          </button>

          <div style={{ position: "absolute", bottom: "16px", left: "20px", right: "20px", color: "#FFFFFF" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
              <span style={{ background: "var(--safety-orange)", padding: "3px 10px", borderRadius: "999px", fontSize: "11px", fontWeight: 800 }}>
                {spot.category}
              </span>
              <span className="font-mono-num" style={{ display: "inline-flex", alignItems: "center", gap: "4px", background: "rgba(26,29,28,0.65)", padding: "3px 10px", borderRadius: "999px", fontSize: "11px", fontWeight: 700 }}>
                <Star size={12} fill="#C9933B" color="#C9933B" />
                {spot.rating}
              </span>
              <span style={{ background: spot.indoor_outdoor === "Indoor" ? "var(--alpine-moss)" : "#2A2F2D", padding: "3px 10px", borderRadius: "999px", fontSize: "11px", fontWeight: 700 }}>
                {spot.indoor_outdoor}
              </span>
            </div>
            <h2 className="font-display" style={{ margin: 0, fontSize: "21px", fontWeight: 900 }}>{spot.name}</h2>
          </div>
        </div>

        <div style={{ padding: "20px" }}>
          {/* Quick Facts */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "10px", marginBottom: "18px", background: "#FFFFFF", padding: "12px", borderRadius: "16px", border: "1px solid var(--stone-border)", textAlign: "center" }}>
            <div>
              <div style={{ fontSize: "11px", color: "var(--granite-600)" }}>Entry Cost</div>
              <div className="font-mono-num" style={{ fontSize: "15px", fontWeight: 800, color: "var(--alpine-moss)" }}>
                {spot.estimated_cost_bdt > 0 ? formatCurrency(spot.estimated_cost_bdt, currency) : "Free"}
              </div>
            </div>
            <div>
              <div style={{ fontSize: "11px", color: "var(--granite-600)" }}>Open Hours</div>
              <div className="font-mono-num" style={{ fontSize: "13px", fontWeight: 700, color: "var(--granite-950)" }}>
                {spot.opening_hour || "08:00"}–{spot.closing_hour || "20:00"}
              </div>
            </div>
            <div>
              <div style={{ fontSize: "11px", color: "var(--granite-600)" }}>Eco Score</div>
              <div className="font-mono-num" style={{ fontSize: "15px", fontWeight: 800, color: "var(--safety-orange)" }}>
                {spot.sustainability_score || 84}/100
              </div>
            </div>
          </div>

          {/* Local SME Partner Callout */}
          {spot.local_partner_name && (
            <div style={{ display: "flex", alignItems: "center", gap: "10px", background: "var(--alpine-moss-soft)", border: "1px solid #C5D9CE", borderRadius: "14px", padding: "10px 14px", marginBottom: "16px" }}>
              <Store size={18} color="#25463B" />
              <div style={{ fontSize: "12px", color: "var(--alpine-moss)" }}>
                <strong>Local Partner:</strong> {spot.local_partner_name} ({spot.local_revenue_share_pct || 85}% revenue retained locally • +{spot.eco_points_reward || 65} Eco-Points)
              </div>
            </div>
          )}

          {/* Explainable AI Panel */}
          <div style={{ background: "#FFFFFF", border: "1px solid var(--stone-border)", borderRadius: "18px", padding: "16px", marginBottom: "18px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", fontWeight: 800, color: "var(--granite-950)", marginBottom: "8px" }}>
              <Sparkles size={16} color="#E85D2A" />
              <span>Why did TripSense-FairNet select this?</span>
            </div>

            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginBottom: "10px" }}>
              {badges.map((b, i) => (
                <span key={i} style={{ background: "var(--bg-surface)", color: "var(--granite-800)", padding: "4px 10px", borderRadius: "8px", fontSize: "11px", fontWeight: 700, border: "1px solid var(--stone-border)" }}>
                  ✓ {b}
                </span>
              ))}
            </div>

            <p style={{ margin: 0, fontSize: "13px", lineHeight: 1.55, color: "var(--granite-800)" }}>
              {why.narrative || spot.description}
            </p>

            {featureAttrs && (
              <div style={{ marginTop: "12px", paddingTop: "10px", borderTop: "1px dashed var(--stone-border)", display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "8px", fontSize: "11px" }}>
                <div>Taste Alignment: <strong className="font-mono-num">+{featureAttrs.taste_alignment}</strong></div>
                <div>Least-Misery Floor: <strong className="font-mono-num">+{featureAttrs.least_misery_floor}</strong></div>
                <div>Eco Sustainability: <strong className="font-mono-num">+{featureAttrs.eco_sustainability}</strong></div>
                <div>Quality Rating: <strong className="font-mono-num">+{featureAttrs.rating_quality}</strong></div>
              </div>
            )}
          </div>

          {/* Group Preference Alignment */}
          {Object.keys(memberBreakdown).length > 0 && (
            <div style={{ marginBottom: "18px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "13px", fontWeight: 800, marginBottom: "10px" }}>
                <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <ShieldCheck size={16} color="#25463B" /> Group Preference Alignment
                </span>
                <span className="font-mono-num" style={{ fontSize: "12px", color: "var(--alpine-moss)" }}>
                  Overall Match: {spot.match_score}%
                </span>
              </div>

              {Object.entries(memberBreakdown).map(([memberName, score]) => (
                <div key={memberName} style={{ marginBottom: "8px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", fontWeight: 700, marginBottom: "4px" }}>
                    <span>{memberName}</span>
                    <span className="font-mono-num">{score}%</span>
                  </div>
                  <div style={{ height: "8px", background: "var(--stone-muted)", borderRadius: "999px", overflow: "hidden" }}>
                    <div
                      style={{
                        width: `${Math.min(100, score)}%`,
                        height: "100%",
                        background: score > 65 ? "var(--alpine-moss)" : score > 40 ? "var(--brass-ochre)" : "var(--safety-orange)",
                        borderRadius: "999px",
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Description */}
          <p style={{ fontSize: "13px", lineHeight: 1.6, color: "var(--granite-600)", marginBottom: "20px" }}>
            {spot.description}
          </p>

          {/* Action Buttons */}
          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
            {onBook && (
              <button
                type="button"
                onClick={() => {
                  onClose();
                  onBook(spot);
                }}
                className="liquid-btn"
                style={{
                  flex: 2,
                  background: "var(--safety-orange)",
                  color: "#FFFFFF",
                  border: "none",
                  borderRadius: "14px",
                  padding: "13px",
                  fontSize: "13px",
                  fontWeight: 800,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "6px",
                }}
              >
                <CalendarCheck size={16} />
                <span>Reserve Partner Voucher</span>
              </button>
            )}

            {onVeto && (
              <button
                type="button"
                onClick={() => {
                  onVeto(spot);
                  onClose();
                }}
                disabled={userVetoTokens <= 0}
                style={{
                  flex: 1,
                  background: userVetoTokens > 0 ? "var(--safety-orange-soft)" : "var(--stone-muted)",
                  color: userVetoTokens > 0 ? "var(--safety-orange-hover)" : "var(--granite-600)",
                  border: `1px solid ${userVetoTokens > 0 ? "#F7C6B3" : "var(--stone-border)"}`,
                  borderRadius: "14px",
                  padding: "13px",
                  fontSize: "12px",
                  fontWeight: 800,
                  cursor: userVetoTokens > 0 ? "pointer" : "not-allowed",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "6px",
                }}
              >
                <ShieldAlert size={15} />
                <span>Nash Veto ({userVetoTokens})</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
