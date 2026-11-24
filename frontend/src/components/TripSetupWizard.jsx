import React, { useState } from "react";
import {
  Calendar,
  Sparkles,
  Copy,
  Check,
  Share2,
  ArrowRight
} from "lucide-react";

const CITIES_WITH_WEATHER = [
  {
    name: "Chittagong",
    country: "Bangladesh",
    temp: "28°C",
    weather: "Partly Cloudy",
    icon: "⛅",
    vibe: "Port City & Coastal Hills",
    image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=400&q=80"
  },
  {
    name: "Cox's Bazar",
    country: "Bangladesh",
    temp: "30°C",
    weather: "Sunny Breeze",
    icon: "🌊",
    vibe: "Endless Sea Beach & Sunsets",
    image: "https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?auto=format&fit=crop&w=400&q=80"
  },
  {
    name: "Sylhet",
    country: "Bangladesh",
    temp: "24°C",
    weather: "Tropical Mist",
    icon: "🌧️",
    vibe: "Lush Tea Gardens & Waterfalls",
    image: "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=400&q=80"
  },
  {
    name: "Dhaka",
    country: "Bangladesh",
    temp: "32°C",
    weather: "Warm & Lively",
    icon: "☀️",
    vibe: "Mughal Forts & Heritage Trails",
    image: "https://images.unsplash.com/photo-1596178065887-1198b6148b2b?auto=format&fit=crop&w=400&q=80"
  },
  {
    name: "Paris",
    country: "France",
    temp: "19°C",
    weather: "Crisp Autumn",
    icon: "🗼",
    vibe: "Art, Architecture & Seine River",
    image: "https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?auto=format&fit=crop&w=400&q=80"
  },
  {
    name: "Tokyo",
    country: "Japan",
    temp: "22°C",
    weather: "Clear Sky",
    icon: "🌸",
    vibe: "Temples, Neon & Culinary Perfection",
    image: "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=400&q=80"
  }
];

const BUDGET_PRESETS = [
  {
    id: "Budget",
    label: "Backpacker",
    icon: "🎒",
    costDailyBdt: "৳1,500/day",
    desc: "CNG, street Mezban & free POIs"
  },
  {
    id: "Mid-range",
    label: "Explorer",
    icon: "🧭",
    costDailyBdt: "৳4,500/day",
    desc: "AC rides, curated museum tickets"
  },
  {
    id: "Luxury",
    label: "Premium",
    icon: "👑",
    costDailyBdt: "৳12,000+/day",
    desc: "Private cabs, resort dining, VIP entry"
  }
];

const PACE_PRESETS = [
  { id: "Relaxed", label: "Relaxed", spotsPerDay: "2 spots/day", icon: "🧘", desc: "Leisurely mornings, long lunches" },
  { id: "Moderate", label: "Moderate", spotsPerDay: "3-4 spots/day", icon: "🚶", desc: "Balanced sightseeing & rest" },
  { id: "High Energy", label: "High Energy", spotsPerDay: "5+ spots/day", icon: "⚡", desc: "Maximize landmarks & photos" }
];

export default function TripSetupWizard({
  initialCity = "Chittagong",
  initialDays = 3,
  initialMembers = [],
  onStartSolver,
  onCancel
}) {
  const [selectedCity, setSelectedCity] = useState(initialCity);
  const [days, setDays] = useState(initialDays);
  const [startDate, setStartDate] = useState("2026-08-12");
  const [budgetTier, setBudgetTier] = useState("Mid-range");
  const [pace, setPace] = useState("Moderate");
  const [roomCode, setRoomCode] = useState(() => `${initialCity.substring(0, 3).toUpperCase()}-707`);
  const [members, setMembers] = useState(
    initialMembers.length > 0
      ? initialMembers
      : [
          { name: "Rahat", interests: ["Historical", "Culture"], budget_tier: "Budget" },
          { name: "Sadia", interests: ["Beach", "Nature"], budget_tier: "Mid-range" },
          { name: "Fahim", interests: ["Food", "Adventure"], budget_tier: "Luxury" }
        ]
  );
  const [copied, setCopied] = useState(false);
  const [newMemberName, setNewMemberName] = useState("");

  const handleCitySelect = (cityName) => {
    setSelectedCity(cityName);
    const prefix = cityName.substring(0, 3).toUpperCase();
    const codeNum = (cityName.charCodeAt(0) * 7 + cityName.length * 13) % 900 + 100;
    setRoomCode(`${prefix}-${codeNum}`);
  };

  const handlePresetDays = (num) => {
    setDays(num);
  };

  const handleCopyInvite = () => {
    navigator.clipboard?.writeText(`https://tripsense.app/room/${roomCode}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleWhatsAppShare = () => {
    const text = encodeURIComponent(`Hey squad! Join our TripSense group trip to ${selectedCity}! Room Code: ${roomCode} - https://tripsense.app/room/${roomCode}`);
    window.open(`https://api.whatsapp.com/send?text=${text}`, "_blank");
  };

  const handleAddMember = (e) => {
    e.preventDefault();
    const name = newMemberName.trim();
    if (!name) return;
    if (members.some((m) => m.name.toLowerCase() === name.toLowerCase())) {
      alert(`${name} is already in the squad!`);
      return;
    }
    setMembers([...members, { name, interests: ["Culture", "Nature"], budget_tier: budgetTier }]);
    setNewMemberName("");
  };

  const handleRemoveMember = (idxToRemove) => {
    if (members.length <= 1) return;
    setMembers(members.filter((_, idx) => idx !== idxToRemove));
  };

  const handleLaunch = () => {
    // Calculate end date based on startDate and days
    const start = new Date(startDate);
    const end = new Date(start);
    end.setDate(end.getDate() + (days - 1));
    const endDateStr = end.toISOString().split("T")[0];

    // Propagate members with budgetTier if desired
    const updatedMembers = members.map((m) => ({
      ...m,
      budget_tier: m.budget_tier || budgetTier
    }));

    onStartSolver({
      city: selectedCity,
      startDate,
      endDate: endDateStr,
      days,
      roomCode,
      members: updatedMembers,
      pace,
      budgetTier
    });
  };

  return (
    <div style={{
      position: "fixed",
      inset: 0,
      zIndex: 99999,
      background: "rgba(15, 23, 42, 0.75)",
      backdropFilter: "blur(8px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "16px",
      overflowY: "auto",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    }}>
      <div style={{
        background: "#ffffff",
        borderRadius: "28px",
        width: "100%",
        maxWidth: "680px",
        maxHeight: "92vh",
        overflowY: "auto",
        boxShadow: "0 25px 60px rgba(0,0,0,0.35)",
        boxSizing: "border-box",
        padding: "28px 24px",
        animation: "slideUp 0.35s ease"
      }}>
        {/* Header Title */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "18px" }}>
          <div>
            <div style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              background: "#FFF0EA",
              color: "#CC4A1B",
              fontSize: "11px",
              fontWeight: 800,
              padding: "3px 10px",
              borderRadius: "12px",
              marginBottom: "4px"
            }}>
              <Sparkles size={12} />
              STEP-BY-STEP TRIP SETUP WIZARD
            </div>
            <h2 style={{ fontSize: "22px", fontWeight: 900, color: "#1A1D1C", margin: 0 }}>
              Design Your Group Getaway
            </h2>
          </div>

          {onCancel && (
            <button
              onClick={onCancel}
              style={{
                background: "#f1f5f9",
                border: "none",
                borderRadius: "12px",
                padding: "6px 12px",
                fontSize: "12px",
                fontWeight: 700,
                color: "#59615E",
                cursor: "pointer"
              }}
            >
              Cancel
            </button>
          )}
        </div>

        {/* 1. Destination Picker with Weather Badges */}
        <div style={{ marginBottom: "20px" }}>
          <label style={{
            display: "block",
            fontSize: "12px",
            fontWeight: 800,
            color: "#475569",
            textTransform: "uppercase",
            marginBottom: "8px"
          }}>
            1. Select Destination (with Live Weather Radar)
          </label>
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "10px"
          }}>
            {CITIES_WITH_WEATHER.map((c) => {
              const isSelected = selectedCity.toLowerCase() === c.name.toLowerCase();
              return (
                <div
                  key={c.name}
                  onClick={() => handleCitySelect(c.name)}
                  style={{
                    position: "relative",
                    borderRadius: "16px",
                    border: isSelected ? "2.5px solid #E85D2A" : "1px solid #E2DDD3",
                    background: isSelected ? "#FFF0EA" : "#ffffff",
                    padding: "10px",
                    cursor: "pointer",
                    transition: "all 0.15s ease",
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    boxShadow: isSelected ? "0 4px 14px rgba(79, 70, 229, 0.15)" : "none"
                  }}
                >
                  <img
                    src={c.image}
                    alt={c.name}
                    style={{ width: "42px", height: "42px", borderRadius: "10px", objectFit: "cover" }}
                  />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                      <span style={{ fontSize: "13px", fontWeight: 800, color: "#1A1D1C" }}>
                        {c.name}
                      </span>
                      <span style={{ fontSize: "11px", fontWeight: 700, color: "#E85D2A" }}>
                        {c.icon} {c.temp}
                      </span>
                    </div>
                    <div style={{ fontSize: "10px", color: "#59615E", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {c.weather} • {c.vibe}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 2. Smart Duration & Date Selector */}
        <div style={{ marginBottom: "20px" }}>
          <label style={{
            display: "block",
            fontSize: "12px",
            fontWeight: 800,
            color: "#475569",
            textTransform: "uppercase",
            marginBottom: "8px"
          }}>
            2. Smart Trip Duration & Dates
          </label>
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "10px" }}>
            <button
              type="button"
              onClick={() => handlePresetDays(2)}
              style={{
                flex: 1,
                padding: "8px 12px",
                borderRadius: "12px",
                border: days === 2 ? "2px solid #E85D2A" : "1px solid #cbd5e1",
                background: days === 2 ? "#FFF0EA" : "#ffffff",
                color: days === 2 ? "#CC4A1B" : "#334155",
                fontWeight: 700,
                fontSize: "12px",
                cursor: "pointer"
              }}
            >
              ⚡ 2 Days (Weekend)
            </button>
            <button
              type="button"
              onClick={() => handlePresetDays(3)}
              style={{
                flex: 1,
                padding: "8px 12px",
                borderRadius: "12px",
                border: days === 3 ? "2px solid #E85D2A" : "1px solid #cbd5e1",
                background: days === 3 ? "#FFF0EA" : "#ffffff",
                color: days === 3 ? "#CC4A1B" : "#334155",
                fontWeight: 700,
                fontSize: "12px",
                cursor: "pointer"
              }}
            >
              🌴 3 Days (Classic)
            </button>
            <button
              type="button"
              onClick={() => handlePresetDays(5)}
              style={{
                flex: 1,
                padding: "8px 12px",
                borderRadius: "12px",
                border: days === 5 ? "2px solid #E85D2A" : "1px solid #cbd5e1",
                background: days === 5 ? "#FFF0EA" : "#ffffff",
                color: days === 5 ? "#CC4A1B" : "#334155",
                fontWeight: 700,
                fontSize: "12px",
                cursor: "pointer"
              }}
            >
              🌍 5 Days (Extended)
            </button>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <Calendar size={18} color="#E85D2A" />
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              style={{
                padding: "8px 12px",
                borderRadius: "10px",
                border: "1px solid #cbd5e1",
                fontSize: "13px",
                fontWeight: 600
              }}
            />
            <span style={{ fontSize: "12px", color: "#59615E" }}>
              Departing on <strong>{startDate}</strong> for <strong>{days} Days</strong>
            </span>
          </div>
        </div>

        {/* 3. Vibe & Budget Tier */}
        <div style={{ marginBottom: "20px" }}>
          <label style={{
            display: "block",
            fontSize: "12px",
            fontWeight: 800,
            color: "#475569",
            textTransform: "uppercase",
            marginBottom: "8px"
          }}>
            3. Group Budget Vibe
          </label>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "8px" }}>
            {BUDGET_PRESETS.map((b) => (
              <div
                key={b.id}
                onClick={() => setBudgetTier(b.id)}
                style={{
                  borderRadius: "14px",
                  padding: "10px",
                  border: budgetTier === b.id ? "2px solid #10b981" : "1px solid #E2DDD3",
                  background: budgetTier === b.id ? "#ecfdf5" : "#ffffff",
                  cursor: "pointer",
                  textAlign: "center",
                  transition: "all 0.15s ease"
                }}
              >
                <div style={{ fontSize: "20px", marginBottom: "2px" }}>{b.icon}</div>
                <div style={{ fontSize: "13px", fontWeight: 800, color: "#1A1D1C" }}>{b.label}</div>
                <div style={{ fontSize: "11px", fontWeight: 700, color: "#059669", margin: "2px 0" }}>{b.costDailyBdt}</div>
                <div style={{ fontSize: "10px", color: "#59615E", lineHeight: 1.2 }}>{b.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* 4. Travel Pace Dial */}
        <div style={{ marginBottom: "20px" }}>
          <label style={{
            display: "block",
            fontSize: "12px",
            fontWeight: 800,
            color: "#475569",
            textTransform: "uppercase",
            marginBottom: "8px"
          }}>
            4. Travel Pace
          </label>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "8px" }}>
            {PACE_PRESETS.map((p) => (
              <div
                key={p.id}
                onClick={() => setPace(p.id)}
                style={{
                  borderRadius: "14px",
                  padding: "10px",
                  border: pace === p.id ? "2px solid #E85D2A" : "1px solid #E2DDD3",
                  background: pace === p.id ? "#FFF0EA" : "#ffffff",
                  cursor: "pointer",
                  textAlign: "center",
                  transition: "all 0.15s ease"
                }}
              >
                <div style={{ fontSize: "18px", marginBottom: "2px" }}>{p.icon}</div>
                <div style={{ fontSize: "13px", fontWeight: 800, color: "#1A1D1C" }}>{p.label}</div>
                <div style={{ fontSize: "11px", fontWeight: 700, color: "#E85D2A" }}>{p.spotsPerDay}</div>
                <div style={{ fontSize: "10px", color: "#59615E" }}>{p.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* 5. Squad Lobby Preview */}
        <div style={{
          background: "#F6F4EF",
          border: "1px solid #E2DDD3",
          borderRadius: "18px",
          padding: "16px",
          marginBottom: "24px"
        }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "10px" }}>
            <div>
              <span style={{ fontSize: "12px", fontWeight: 800, color: "#1A1D1C" }}>
                👥 Squad Room Code:
              </span>
              <span style={{
                marginLeft: "8px",
                background: "#1A1D1C",
                color: "#ffffff",
                padding: "3px 10px",
                borderRadius: "8px",
                fontSize: "12px",
                fontWeight: 900,
                letterSpacing: "1px"
              }}>
                {roomCode}
              </span>
            </div>

            <div style={{ display: "flex", gap: "6px" }}>
              <button
                type="button"
                onClick={handleCopyInvite}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                  background: "#ffffff",
                  border: "1px solid #cbd5e1",
                  borderRadius: "8px",
                  padding: "4px 8px",
                  fontSize: "11px",
                  fontWeight: 700,
                  cursor: "pointer",
                  color: "#334155"
                }}
              >
                {copied ? <Check size={12} color="#10b981" /> : <Copy size={12} />}
                <span>{copied ? "Copied!" : "Copy Link"}</span>
              </button>

              <button
                type="button"
                onClick={handleWhatsAppShare}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                  background: "#25d366",
                  border: "none",
                  borderRadius: "8px",
                  padding: "4px 8px",
                  fontSize: "11px",
                  fontWeight: 800,
                  cursor: "pointer",
                  color: "#ffffff"
                }}
              >
                <Share2 size={12} />
                <span>WhatsApp</span>
              </button>
            </div>
          </div>

          {/* Members Avatar Bubbles */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", alignItems: "center", marginBottom: "12px" }}>
            {members.map((m, idx) => (
              <div
                key={m.name}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  background: "#ffffff",
                  border: "1px solid #cbd5e1",
                  borderRadius: "999px",
                  padding: "4px 10px 4px 6px",
                  fontSize: "12px",
                  fontWeight: 700,
                  color: "#1e293b"
                }}
              >
                <div style={{
                  width: "22px",
                  height: "22px",
                  borderRadius: "50%",
                  background: idx === 0 ? "#E85D2A" : idx === 1 ? "#ec4899" : "#10b981",
                  color: "#ffffff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "11px",
                  fontWeight: 800
                }}>
                  {m.name.charAt(0)}
                </div>
                <span>{m.name}</span>
                {members.length > 1 && (
                  <button
                    onClick={() => handleRemoveMember(idx)}
                    style={{
                      background: "transparent",
                      border: "none",
                      color: "#94a3b8",
                      fontSize: "13px",
                      cursor: "pointer",
                      padding: "0 2px"
                    }}
                    title="Remove member"
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* Quick Add Tripmate Form */}
          <form onSubmit={handleAddMember} style={{ display: "flex", gap: "6px" }}>
            <input
              type="text"
              placeholder="Add friend name (e.g. Tanvir)"
              value={newMemberName}
              onChange={(e) => setNewMemberName(e.target.value)}
              style={{
                flex: 1,
                padding: "8px 12px",
                borderRadius: "10px",
                border: "1px solid #cbd5e1",
                fontSize: "12px",
                background: "#ffffff"
              }}
            />
            <button
              type="submit"
              style={{
                padding: "8px 14px",
                borderRadius: "10px",
                border: "none",
                background: "#E85D2A",
                color: "#ffffff",
                fontSize: "12px",
                fontWeight: 700,
                cursor: "pointer"
              }}
            >
              + Add
            </button>
          </form>
        </div>

        {/* Big Action CTA: Launch AI Solver */}
        <button
          onClick={handleLaunch}
          style={{
            width: "100%",
            padding: "16px",
            borderRadius: "18px",
            border: "none",
            background: "linear-gradient(135deg, #E85D2A 0%, #25463B 100%)",
            color: "#ffffff",
            fontSize: "16px",
            fontWeight: 800,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "10px",
            boxShadow: "0 10px 30px rgba(79, 70, 229, 0.4)",
            letterSpacing: "0.2px"
          }}
        >
          <Sparkles size={20} />
          <span>Launch AI Solver Recommender 🚀</span>
          <ArrowRight size={20} />
        </button>
      </div>
    </div>
  );
}
