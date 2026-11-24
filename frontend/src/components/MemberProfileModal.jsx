import React from "react";
import { X } from "lucide-react";

export default function MemberProfileModal({ member, satisfaction = 85, vetoLeft = 1, onClose }) {
  if (!member) return null;

  return (
    <div style={{
      position: "fixed",
      inset: 0,
      zIndex: 100000,
      background: "rgba(15, 23, 42, 0.7)",
      backdropFilter: "blur(6px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "16px",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    }}>
      <div style={{
        background: "#ffffff",
        borderRadius: "28px",
        padding: "26px",
        maxWidth: "400px",
        width: "100%",
        boxShadow: "0 25px 60px rgba(0,0,0,0.35)",
        animation: "slideUp 0.3s ease",
        textAlign: "center"
      }}>
        {/* Top close */}
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "8px" }}>
          <button
            onClick={onClose}
            style={{
              background: "#f1f5f9",
              border: "none",
              borderRadius: "50%",
              width: "32px",
              height: "32px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Avatar */}
        <div style={{
          width: "72px",
          height: "72px",
          borderRadius: "50%",
          background: "linear-gradient(135deg, #E85D2A 0%, #E85D2A 100%)",
          color: "#ffffff",
          fontSize: "28px",
          fontWeight: 900,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          margin: "0 auto 12px auto",
          boxShadow: "0 8px 20px rgba(99, 102, 241, 0.35)"
        }}>
          {member.name.charAt(0).toUpperCase()}
        </div>

        <h3 style={{ fontSize: "20px", fontWeight: 900, color: "#1A1D1C", margin: "0 0 4px 0" }}>
          {member.name}
        </h3>

        <div style={{ display: "inline-block", background: "#f1f5f9", padding: "3px 12px", borderRadius: "12px", fontSize: "11px", fontWeight: 700, color: "#475569", marginBottom: "16px" }}>
          Tier: {member.budget_tier || "Mid-range"} • Active Tripmate
        </div>

        {/* 2 Stats Badges */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "18px" }}>
          <div style={{ background: "#FFF0EA", borderRadius: "14px", padding: "12px", border: "1px solid #F7C6B3" }}>
            <div style={{ fontSize: "11px", color: "#E85D2A", fontWeight: 700 }}>SATISFACTION</div>
            <div style={{ fontSize: "20px", fontWeight: 900, color: "#1A1D1C" }}>{satisfaction}%</div>
          </div>

          <div style={{ background: vetoLeft > 0 ? "#ecfdf5" : "#fef2f2", borderRadius: "14px", padding: "12px", border: `1px solid ${vetoLeft > 0 ? '#a7f3d0' : '#fecaca'}` }}>
            <div style={{ fontSize: "11px", color: vetoLeft > 0 ? "#059669" : "#b91c1c", fontWeight: 700 }}>VETO TOKEN</div>
            <div style={{ fontSize: "15px", fontWeight: 900, color: vetoLeft > 0 ? "#065f46" : "#991b1b" }}>
              {vetoLeft > 0 ? "🛡️ 1 Token Ready" : "❌ Used"}
            </div>
          </div>
        </div>

        {/* Interests */}
        <div style={{ textAlign: "left", background: "#F6F4EF", borderRadius: "14px", padding: "12px", marginBottom: "16px" }}>
          <div style={{ fontSize: "11px", fontWeight: 700, color: "#59615E", textTransform: "uppercase", marginBottom: "8px" }}>
            Calibrated Preferences
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
            {(member.interests || []).map((int) => (
              <span
                key={int}
                style={{
                  background: "#ffffff",
                  border: "1px solid #cbd5e1",
                  color: "#334155",
                  padding: "4px 10px",
                  borderRadius: "10px",
                  fontSize: "11px",
                  fontWeight: 700
                }}
              >
                ✨ {int}
              </span>
            ))}
          </div>
        </div>

        <button
          onClick={onClose}
          style={{
            width: "100%",
            padding: "10px",
            borderRadius: "12px",
            border: "none",
            background: "#E85D2A",
            color: "#ffffff",
            fontSize: "13px",
            fontWeight: 800,
            cursor: "pointer"
          }}
        >
          Close
        </button>
      </div>
    </div>
  );
}
