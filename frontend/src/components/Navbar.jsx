import React, { useState, useEffect } from "react";
import { Compass, Calendar, Wifi, WifiOff, CloudSun, LogOut, Sparkles, SlidersHorizontal, Film, Bot } from "lucide-react";

function computeCountdownTicker(dateStr) {
  try {
    const target = new Date(dateStr);
    const now = new Date();
    target.setHours(0, 0, 0, 0);
    now.setHours(0, 0, 0, 0);
    const diffTime = target.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    if (diffDays > 0) return `Starts in ${diffDays}d`;
    if (diffDays === 0) return "Starts today!";
    return "Live Expedition";
  } catch {
    return "Starts in 3d";
  }
}

export default function Navbar({
  city,
  startDate,
  endDate,
  days,
  roomCode,
  members = [],
  activeTab,
  setActiveTab,
  onOpenDatePicker,
  isOfflineMode,
  onToggleOffline,
  isOnline,
  currentUser,
  onLogout,
  onOpenLogin,
  onOpenTasteMatch,
  onOpenSetupWizard,
  onOpenReel,
  onOpenCopilot,
  lang = "EN",
  setLang,
  currency = "BDT",
  setCurrency,
}) {
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [countdownTicker, setCountdownTicker] = useState(() => computeCountdownTicker(startDate));

  const formatDate = (dateStr) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    } catch {
      return dateStr;
    }
  };

  const weatherMap = {
    "Chittagong": "28°C ⛅",
    "Cox's Bazar": "30°C 🌊",
    "Sylhet": "24°C 🌧️",
    "Bandarban": "23°C ⛰️",
    "Dhaka": "32°C ☀️",
    "Paris": "19°C 🗼",
    "Tokyo": "22°C 🌸"
  };
  const currentWeather = weatherMap[city] || "27°C ⛅";

  useEffect(() => {
    const timer = setTimeout(() => {
      setCountdownTicker(computeCountdownTicker(startDate));
    }, 0);
    return () => clearTimeout(timer);
  }, [startDate]);

  return (
    <header
      className="glass-panel"
      style={{
        position: "sticky",
        top: 0,
        zIndex: 100,
        borderTop: "none",
        borderLeft: "none",
        borderRight: "none",
        borderBottom: "1px solid var(--stone-border)",
      }}
    >
      {/* Top Row: Brand, Controls, Localization & Auth */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "10px 20px",
          maxWidth: "1320px",
          margin: "0 auto",
          gap: "10px",
          flexWrap: "wrap",
        }}
      >
        {/* Left: Editorial Brand + City/Date Pill */}
        <div style={{ display: "flex", alignItems: "center", gap: "14px", flexWrap: "wrap" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "9px" }}>
            <div
              style={{
                background: "var(--safety-orange)",
                color: "#FFFFFF",
                borderRadius: "11px",
                padding: "7px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 6px 14px rgba(232, 93, 42, 0.25)",
              }}
            >
              <Compass size={19} />
            </div>
            <div>
              <div className="font-display" style={{ fontSize: "19px", fontWeight: 900, color: "var(--granite-950)", lineHeight: 1 }}>
                TripSense
              </div>
              <div style={{ fontSize: "9px", fontWeight: 800, color: "var(--alpine-moss)", letterSpacing: "0.7px", marginTop: "2px" }}>
                FAIRNET • ECO TRAVEL
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={onOpenDatePicker}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              background: "#FFFFFF",
              border: "1px solid var(--stone-border)",
              borderRadius: "999px",
              padding: "6px 13px",
              fontSize: "12px",
              fontWeight: 700,
              color: "var(--granite-950)",
              cursor: "pointer",
              boxShadow: "0 2px 6px rgba(26,29,28,0.04)",
            }}
            title="Change Destination & Trip Dates"
          >
            <Calendar size={13} color="#E85D2A" />
            <span>{city} • {formatDate(startDate)} – {formatDate(endDate)} ({days}d)</span>
          </button>

          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "4px",
              background: "var(--alpine-moss-soft)",
              color: "var(--alpine-moss)",
              padding: "5px 10px",
              borderRadius: "999px",
              fontSize: "11px",
              fontWeight: 700,
              border: "1px solid #C5D9CE",
            }}
          >
            <CloudSun size={13} />
            <span>{currentWeather} • {countdownTicker}</span>
          </span>
        </div>

        {/* Right: Language, Currency, Offline, & Passport */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
          {/* Language Switcher EN | BN */}
          {setLang && (
            <div className="neu-control" style={{ display: "flex", gap: "2px" }}>
              {["EN", "BN"].map((l) => (
                <button
                  key={l}
                  type="button"
                  onClick={() => setLang(l)}
                  className={lang === l ? "neu-control-item-active" : ""}
                  style={{
                    border: "none",
                    borderRadius: "10px",
                    padding: "4px 8px",
                    fontSize: "10px",
                    fontWeight: 800,
                    cursor: "pointer",
                    background: lang === l ? "#FFFFFF" : "transparent",
                    color: lang === l ? "var(--granite-950)" : "var(--granite-600)",
                  }}
                >
                  {l}
                </button>
              ))}
            </div>
          )}

          {/* Currency Switcher ৳ | $ | € */}
          {setCurrency && (
            <div className="neu-control" style={{ display: "flex", gap: "2px" }}>
              {[
                { id: "BDT", sym: "৳" },
                { id: "USD", sym: "$" },
                { id: "EUR", sym: "€" },
              ].map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => setCurrency(c.id)}
                  className={currency === c.id ? "neu-control-item-active" : ""}
                  style={{
                    border: "none",
                    borderRadius: "10px",
                    padding: "4px 8px",
                    fontSize: "10px",
                    fontWeight: 800,
                    cursor: "pointer",
                    background: currency === c.id ? "#FFFFFF" : "transparent",
                    color: currency === c.id ? "var(--safety-orange)" : "var(--granite-600)",
                  }}
                >
                  {c.sym}
                </button>
              ))}
            </div>
          )}

          <span
            className="font-mono-num"
            style={{
              background: "var(--granite-950)",
              color: "#FAF9F6",
              padding: "5px 10px",
              borderRadius: "999px",
              fontSize: "11px",
              fontWeight: 700,
            }}
          >
            {roomCode} • {members.length}
          </span>

          <button
            type="button"
            onClick={onToggleOffline}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "4px",
              background: isOfflineMode ? "var(--brass-soft)" : "var(--alpine-moss-soft)",
              color: isOfflineMode ? "#805919" : "var(--alpine-moss)",
              border: `1px solid ${isOfflineMode ? "#E5C88B" : "#C5D9CE"}`,
              borderRadius: "999px",
              padding: "5px 10px",
              fontSize: "11px",
              fontWeight: 800,
              cursor: "pointer",
            }}
          >
            {isOfflineMode || !isOnline ? <WifiOff size={13} /> : <Wifi size={13} />}
            <span>{isOfflineMode || !isOnline ? "Offline" : "Live"}</span>
          </button>

          {currentUser ? (
            <div style={{ position: "relative" }}>
              <button
                type="button"
                onClick={() => setShowProfileMenu(!showProfileMenu)}
                style={{
                  width: "34px",
                  height: "34px",
                  borderRadius: "50%",
                  background: "var(--safety-orange)",
                  color: "#FFFFFF",
                  border: "2px solid #FFFFFF",
                  fontSize: "13px",
                  fontWeight: 800,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: "0 3px 10px rgba(232, 93, 42, 0.3)",
                }}
              >
                {currentUser.name?.[0]?.toUpperCase() || "R"}
              </button>

              {showProfileMenu && (
                <div
                  style={{
                    position: "absolute",
                    top: "42px",
                    right: 0,
                    background: "#FFFFFF",
                    border: "1px solid var(--stone-border)",
                    borderRadius: "16px",
                    boxShadow: "0 16px 36px rgba(26, 29, 28, 0.16)",
                    width: "225px",
                    padding: "8px",
                    zIndex: 1000,
                  }}
                >
                  <div style={{ padding: "8px 10px", borderBottom: "1px solid var(--stone-muted)", marginBottom: "6px" }}>
                    <div style={{ fontSize: "13px", fontWeight: 800, color: "var(--granite-950)" }}>{currentUser.name}</div>
                    <div style={{ fontSize: "11px", color: "var(--granite-600)" }}>{currentUser.email}</div>
                  </div>
                  <button type="button" onClick={() => { setShowProfileMenu(false); onOpenTasteMatch(); }} style={menuItemStyle}>
                    <Sparkles size={14} color="#E85D2A" /> <span>Retake Active Swipe Quiz</span>
                  </button>
                  <button type="button" onClick={() => { setShowProfileMenu(false); onOpenSetupWizard(); }} style={menuItemStyle}>
                    <SlidersHorizontal size={14} color="#25463B" /> <span>Trip Setup Wizard</span>
                  </button>
                  <button type="button" onClick={() => { setShowProfileMenu(false); onOpenReel(); }} style={menuItemStyle}>
                    <Film size={14} color="#C9933B" /> <span>15s Trip Recap Reel</span>
                  </button>
                  <button type="button" onClick={() => { setShowProfileMenu(false); onOpenCopilot(); }} style={menuItemStyle}>
                    <Bot size={14} color="#E85D2A" /> <span>AI Copilot (RAG)</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => { setShowProfileMenu(false); onLogout(); }}
                    style={{ ...menuItemStyle, color: "#B91C1C", borderTop: "1px solid var(--stone-muted)", marginTop: "4px", paddingTop: "8px" }}
                  >
                    <LogOut size={14} /> <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button
              type="button"
              onClick={onOpenLogin}
              style={{
                background: "var(--granite-950)",
                color: "#FFFFFF",
                border: "none",
                borderRadius: "999px",
                padding: "6px 14px",
                fontSize: "11px",
                fontWeight: 800,
                cursor: "pointer",
              }}
            >
              Passport Sign-In
            </button>
          )}
        </div>
      </div>

      {/* Bottom Tab Navigation Bar */}
      <nav
        style={{
          display: "flex",
          maxWidth: "1320px",
          margin: "0 auto",
          padding: "0 20px",
          gap: "22px",
          overflowX: "auto",
          scrollbarWidth: "none",
        }}
      >
        {[
          { id: "itinerary", label: "Itinerary & Map" },
          { id: "lobby", label: "Squad & Preferences" },
          { id: "expenses", label: "Expense Splitter" },
          { id: "fairness", label: "FairNet Q1 Lab & Eco" },
        ].map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: "transparent",
                border: "none",
                borderBottom: isActive ? "3px solid var(--safety-orange)" : "3px solid transparent",
                padding: "10px 2px",
                fontSize: "13px",
                fontWeight: isActive ? 800 : 600,
                color: isActive ? "var(--granite-950)" : "var(--granite-600)",
                cursor: "pointer",
                whiteSpace: "nowrap",
                transition: "all 0.2s ease",
              }}
            >
              {tab.label}
            </button>
          );
        })}
      </nav>
    </header>
  );
}

const menuItemStyle = {
  display: "flex",
  alignItems: "center",
  gap: "8px",
  width: "100%",
  padding: "8px 10px",
  background: "transparent",
  border: "none",
  borderRadius: "10px",
  fontSize: "12px",
  fontWeight: 700,
  color: "#1A1D1C",
  cursor: "pointer",
  textAlign: "left",
};
