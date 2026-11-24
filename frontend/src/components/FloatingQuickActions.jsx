import React from "react";
import { MessageCircle, MapPin, Bot } from "lucide-react";

export default function FloatingQuickActions({
  city = "Chittagong",
  roomCode = "CTG-882",
  onOpenCopilot,
}) {
  const whatsappText = encodeURIComponent(
    `Join our ${city} eco-smart squad trip on TripSense! Room Code: ${roomCode} — Zero-hallucination itinerary & fair group planning.`
  );

  return (
    <div
      style={{
        position: "fixed",
        bottom: "76px",
        right: "18px",
        zIndex: 92,
        display: "flex",
        flexDirection: "column",
        gap: "8px",
        alignItems: "flex-end",
      }}
    >
      <a
        href={`https://wa.me/?text=${whatsappText}`}
        target="_blank"
        rel="noreferrer"
        style={{
          background: "#25463B",
          color: "#FFFFFF",
          padding: "9px 14px",
          borderRadius: "999px",
          fontSize: "11px",
          fontWeight: 800,
          textDecoration: "none",
          display: "inline-flex",
          alignItems: "center",
          gap: "6px",
          boxShadow: "0 8px 20px rgba(26, 29, 28, 0.2)",
          border: "1px solid rgba(255,255,255,0.16)",
        }}
      >
        <MessageCircle size={14} />
        <span>WhatsApp Squad</span>
      </a>

      <a
        href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(city + " tourist attractions")}`}
        target="_blank"
        rel="noreferrer"
        style={{
          background: "#FFFFFF",
          color: "#1A1D1C",
          padding: "9px 14px",
          borderRadius: "999px",
          fontSize: "11px",
          fontWeight: 800,
          textDecoration: "none",
          display: "inline-flex",
          alignItems: "center",
          gap: "6px",
          boxShadow: "0 8px 20px rgba(26, 29, 28, 0.14)",
          border: "1px solid var(--stone-border)",
        }}
      >
        <MapPin size={14} color="#E85D2A" />
        <span>Google Maps</span>
      </a>

      <button
        type="button"
        onClick={onOpenCopilot}
        className="liquid-btn"
        style={{
          background: "var(--safety-orange)",
          color: "#FFFFFF",
          padding: "11px 16px",
          borderRadius: "999px",
          fontSize: "12px",
          fontWeight: 800,
          border: "none",
          cursor: "pointer",
          display: "inline-flex",
          alignItems: "center",
          gap: "7px",
          boxShadow: "0 12px 26px rgba(232, 93, 42, 0.35)",
        }}
      >
        <Bot size={16} />
        <span>Ask AI Copilot</span>
      </button>
    </div>
  );
}
