import React, { useState } from "react";
import { X, Calendar, Compass } from "lucide-react";

export default function DestinationDatePickerModal({
  isOpen,
  onClose,
  currentCity,
  startDate,
  endDate,
  onSave,
  availableDestinations = []
}) {
  const [selectedCity, setSelectedCity] = useState(currentCity || "Chittagong");
  const [start, setStart] = useState(startDate || "2026-08-12");
  const [end, setEnd] = useState(endDate || "2026-08-14");

  if (!isOpen) return null;

  // Calculate days
  const calculateDays = () => {
    try {
      const d1 = new Date(start);
      const d2 = new Date(end);
      const diffTime = d2.getTime() - d1.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
      return Math.max(1, Math.min(10, diffDays || 3));
    } catch {
      return 3;
    }
  };

  const daysCount = calculateDays();

  const handleApply = () => {
    onSave({
      city: selectedCity,
      startDate: start,
      endDate: end,
      days: daysCount
    });
    onClose();
  };

  const popularCities = ["Chittagong", "Cox's Bazar", "Sylhet", "Dhaka"];

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        background: "rgba(15, 23, 42, 0.6)",
        backdropFilter: "blur(4px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "16px",
        animation: "fadeIn 0.2s ease"
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: "#ffffff",
          width: "100%",
          maxWidth: "460px",
          borderRadius: "20px",
          padding: "24px",
          boxShadow: "0 20px 40px rgba(0,0,0,0.15)",
          position: "relative"
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "18px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div style={{
              background: "#FFF0EA",
              color: "#E85D2A",
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}>
              <Compass size={20} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: "16px", fontWeight: 800, color: "#1A1D1C" }}>
                Trip Destination & Dates
              </h3>
              <p style={{ margin: 0, fontSize: "12px", color: "#59615E" }}>
                Select target city and travel itinerary timeframe
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "#f1f5f9",
              border: "none",
              borderRadius: "50%",
              width: "32px",
              height: "32px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer"
            }}
          >
            <X size={16} color="#59615E" />
          </button>
        </div>

        {/* Destination Quick Chips */}
        <div style={{ marginBottom: "16px" }}>
          <label style={{ display: "block", fontSize: "12px", fontWeight: 700, color: "#334155", marginBottom: "6px" }}>
            Destination City
          </label>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginBottom: "10px" }}>
            {popularCities.map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => setSelectedCity(c)}
                style={{
                  padding: "6px 12px",
                  borderRadius: "10px",
                  fontSize: "12px",
                  fontWeight: 600,
                  border: selectedCity === c ? "2px solid #E85D2A" : "1px solid #cbd5e1",
                  background: selectedCity === c ? "#FFF0EA" : "#ffffff",
                  color: selectedCity === c ? "#CC4A1B" : "#475569",
                  cursor: "pointer"
                }}
              >
                {c === "Chittagong" ? "🌊 Chittagong (Pilot)" : c}
              </button>
            ))}
          </div>

          <select
            value={selectedCity}
            onChange={(e) => setSelectedCity(e.target.value)}
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: "10px",
              border: "1px solid #cbd5e1",
              fontSize: "14px",
              fontWeight: 600,
              color: "#1A1D1C",
              background: "#ffffff"
            }}
          >
            {availableDestinations.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>

        {/* Date Pickers */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "18px" }}>
          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: 700, color: "#334155", marginBottom: "6px" }}>
              Start Date
            </label>
            <input
              type="date"
              value={start}
              onChange={(e) => setStart(e.target.value)}
              style={{
                width: "100%",
                padding: "8px 10px",
                borderRadius: "10px",
                border: "1px solid #cbd5e1",
                fontSize: "13px",
                color: "#1A1D1C",
                boxSizing: "border-box"
              }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: 700, color: "#334155", marginBottom: "6px" }}>
              End Date
            </label>
            <input
              type="date"
              value={end}
              min={start}
              onChange={(e) => setEnd(e.target.value)}
              style={{
                width: "100%",
                padding: "8px 10px",
                borderRadius: "10px",
                border: "1px solid #cbd5e1",
                fontSize: "13px",
                color: "#1A1D1C",
                boxSizing: "border-box"
              }}
            />
          </div>
        </div>

        {/* Duration indicator */}
        <div style={{
          background: "#f0fdf4",
          border: "1px solid #bbf7d0",
          borderRadius: "10px",
          padding: "10px 12px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "20px"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "#166534", fontWeight: 600 }}>
            <Calendar size={14} />
            <span>Itinerary Duration:</span>
          </div>
          <span style={{ fontSize: "13px", fontWeight: 800, color: "#15803d" }}>
            {daysCount} {daysCount === 1 ? "Day" : "Days"}
          </span>
        </div>

        {/* Action Button */}
        <button
          onClick={handleApply}
          style={{
            width: "100%",
            background: "#E85D2A",
            color: "#ffffff",
            border: "none",
            padding: "12px",
            borderRadius: "12px",
            fontSize: "14px",
            fontWeight: 700,
            cursor: "pointer",
            boxShadow: "0 4px 12px rgba(79, 70, 229, 0.3)"
          }}
        >
          Update Trip & Refresh Plan
        </button>
      </div>
    </div>
  );
}
