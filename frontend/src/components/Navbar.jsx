import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Compass,
  Calendar,
  Wifi,
  WifiOff,
  LogOut,
  Sparkles,
  SlidersHorizontal,
  Film,
  Bot,
  Users,
  ChevronDown,
  User,
} from "lucide-react";

const NAV_TABS = [
  { id: "home", label: "Explore" },
  { id: "itinerary", label: "Itinerary" },
  { id: "expenses", label: "Expenses" },
  { id: "fairness", label: "AI Lab" },
];

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
  onOpenSquad,
  connectionState,
  onOpenConnect,
  lang = "EN",
  setLang,
  currency = "BDT",
  setCurrency,
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const onDocClick = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  const isLive = connectionState?.mode === "live";

  const formatDate = (dateStr) => {
    try {
      return new Date(dateStr).toLocaleDateString("en-US", { month: "short", day: "numeric" });
    } catch {
      return dateStr;
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-[#F8F6F1]/85 backdrop-blur-xl border-b border-[#E6E1D6]/80">
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        {/* Left: Minimal Editorial Brand */}
        <button
          type="button"
          onClick={() => setActiveTab("home")}
          className="flex items-center gap-2.5 text-left group cursor-pointer bg-transparent border-none p-0"
        >
          <span className="w-8 h-8 rounded-xl bg-[#D94E28] text-white flex items-center justify-center shadow-sm group-hover:scale-105 transition-transform">
            <Compass className="w-4 h-4" />
          </span>
          <span className="font-display text-xl font-bold tracking-tight text-[#141715]">
            TripSense
          </span>
        </button>

        {/* Center: Clean Single-Row 4-Tab Pill Switcher (Desktop) */}
        <nav
          aria-label="Primary Navigation"
          className="hidden md:flex items-center gap-1 bg-[#EFECE4]/90 border border-[#E6E1D6] rounded-full p-1"
        >
          {NAV_TABS.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`relative px-4 py-1.5 rounded-full text-xs font-semibold transition-colors cursor-pointer bg-transparent border-none ${
                  isActive ? "text-[#141715]" : "text-[#5A605C] hover:text-[#141715]"
                }`}
              >
                {isActive && (
                  <motion.span
                    layoutId="activeHeaderPill"
                    transition={{ type: "spring", stiffness: 380, damping: 32 }}
                    className="absolute inset-0 rounded-full bg-white shadow-[0_2px_8px_rgba(20,23,21,0.08)]"
                  />
                )}
                <span className="relative z-10">{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right: Quiet AI Status Dot + Single Unified Account & Preferences Menu */}
        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={onOpenConnect}
            title="Configure Cloud / Laptop AI Engine"
            className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[11px] font-semibold border transition cursor-pointer ${
              isLive
                ? "bg-[#E8F2EE] text-[#1E4D3F] border-[#C1DBD1] hover:bg-[#DCECE5]"
                : "bg-[#FBF4E6] text-[#835B19] border-[#E7D0A4] hover:bg-[#F5E9CE]"
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${isLive ? "bg-[#1E4D3F]" : "bg-[#B8863B]"}`}
            />
            <span>{isLive ? `Live AI` : "Demo Mode"}</span>
          </button>

          {/* Unified Preferences & Passport Popover */}
          <div className="relative" ref={menuRef}>
            <button
              type="button"
              onClick={() => setMenuOpen((o) => !o)}
              aria-expanded={menuOpen}
              className="inline-flex items-center gap-2 rounded-full bg-white hover:bg-[#EFECE4]/60 border border-[#E6E1D6] pl-1.5 pr-3 py-1 text-xs font-semibold text-[#141715] shadow-[0_1px_4px_rgba(20,23,21,0.04)] transition cursor-pointer"
            >
              <span className="w-6 h-6 rounded-full bg-[#141715] text-white flex items-center justify-center text-[11px] font-bold">
                {currentUser?.name ? currentUser.name[0].toUpperCase() : <User className="w-3.5 h-3.5" />}
              </span>
              <span className="hidden sm:inline max-w-[90px] truncate">
                {currentUser?.name || "Menu"}
              </span>
              <ChevronDown className="w-3.5 h-3.5 text-[#5A605C]" />
            </button>

            <AnimatePresence>
              {menuOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 8, scale: 0.97 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 6, scale: 0.97 }}
                  transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
                  className="absolute right-0 mt-2 w-72 rounded-2xl bg-white border border-[#E6E1D6] shadow-[0_20px_50px_rgba(20,23,21,0.14)] p-3 z-50"
                >
                  {/* Profile / Trip Context Header */}
                  <div className="px-2.5 py-2 border-b border-[#EFECE4] mb-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#141715]">
                        {currentUser ? currentUser.name : "Guest Explorer"}
                      </span>
                      <span className="font-mono-num text-[10px] font-semibold bg-[#F8F6F1] border border-[#E6E1D6] px-2 py-0.5 rounded-full text-[#5A605C]">
                        {roomCode} • {members.length}
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setMenuOpen(false);
                        onOpenDatePicker();
                      }}
                      className="mt-1.5 flex items-center gap-1.5 text-[11px] text-[#5A605C] hover:text-[#D94E28] bg-transparent border-none p-0 cursor-pointer"
                    >
                      <Calendar className="w-3 h-3 text-[#D94E28]" />
                      <span>
                        {city} • {formatDate(startDate)} – {formatDate(endDate)} ({days}d)
                      </span>
                    </button>
                  </div>

                  {/* Clean Localization Toggles (tucked away cleanly!) */}
                  <div className="flex items-center justify-between gap-2 px-2 py-1.5 mb-2 bg-[#F8F6F1] rounded-xl">
                    {setLang && (
                      <div className="flex items-center gap-1">
                        {["EN", "BN"].map((l) => (
                          <button
                            key={l}
                            type="button"
                            onClick={() => setLang(l)}
                            className={`px-2.5 py-1 rounded-lg text-[10px] font-bold border-none cursor-pointer transition ${
                              lang === l ? "bg-white text-[#141715] shadow-xs" : "bg-transparent text-[#5A605C]"
                            }`}
                          >
                            {l}
                          </button>
                        ))}
                      </div>
                    )}

                    {setCurrency && (
                      <div className="flex items-center gap-1">
                        {[
                          { id: "BDT", sym: "৳" },
                          { id: "USD", sym: "$" },
                          { id: "EUR", sym: "€" },
                        ].map((c) => (
                          <button
                            key={c.id}
                            type="button"
                            onClick={() => setCurrency(c.id)}
                            className={`px-2 py-1 rounded-lg text-[10px] font-bold border-none cursor-pointer transition ${
                              currency === c.id ? "bg-white text-[#D94E28] shadow-xs" : "bg-transparent text-[#5A605C]"
                            }`}
                          >
                            {c.sym}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Clean Menu Actions */}
                  <div className="space-y-0.5 text-xs font-medium text-[#141715]">
                    <button
                      type="button"
                      onClick={() => { setMenuOpen(false); onOpenTasteMatch(); }}
                      className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-xl hover:bg-[#F8F6F1] bg-transparent border-none text-left cursor-pointer"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-[#D94E28]" />
                      <span>60-Sec Taste Swipe</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => { setMenuOpen(false); onOpenSquad(); }}
                      className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-xl hover:bg-[#F8F6F1] bg-transparent border-none text-left cursor-pointer"
                    >
                      <Users className="w-3.5 h-3.5 text-[#1E4D3F]" />
                      <span>Squad & Fairness Settings</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => { setMenuOpen(false); onOpenSetupWizard(); }}
                      className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-xl hover:bg-[#F8F6F1] bg-transparent border-none text-left cursor-pointer"
                    >
                      <SlidersHorizontal className="w-3.5 h-3.5 text-[#5A605C]" />
                      <span>Trip Setup Wizard</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => { setMenuOpen(false); onOpenReel(); }}
                      className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-xl hover:bg-[#F8F6F1] bg-transparent border-none text-left cursor-pointer"
                    >
                      <Film className="w-3.5 h-3.5 text-[#B8863B]" />
                      <span>15s Trip Recap Reel</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => { setMenuOpen(false); onOpenCopilot(); }}
                      className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-xl hover:bg-[#F8F6F1] bg-transparent border-none text-left cursor-pointer"
                    >
                      <Bot className="w-3.5 h-3.5 text-[#D94E28]" />
                      <span>AI Concierge (RAG)</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => { onToggleOffline(); }}
                      className="w-full flex items-center justify-between px-2.5 py-2 rounded-xl hover:bg-[#F8F6F1] bg-transparent border-none text-left cursor-pointer"
                    >
                      <span className="flex items-center gap-2.5">
                        {isOfflineMode || !isOnline ? (
                          <WifiOff className="w-3.5 h-3.5 text-[#B8863B]" />
                        ) : (
                          <Wifi className="w-3.5 h-3.5 text-[#1E4D3F]" />
                        )}
                        <span>Offline Demo Mode</span>
                      </span>
                      <span className="text-[10px] font-bold text-[#5A605C]">
                        {isOfflineMode ? "ON" : "AUTO"}
                      </span>
                    </button>
                  </div>

                  {/* Sign In / Sign Out */}
                  <div className="mt-2 pt-2 border-t border-[#EFECE4]">
                    {currentUser ? (
                      <button
                        type="button"
                        onClick={() => { setMenuOpen(false); onLogout(); }}
                        className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-xl hover:bg-red-50 text-red-700 bg-transparent border-none text-xs font-semibold cursor-pointer"
                      >
                        <LogOut className="w-3.5 h-3.5" />
                        <span>Sign Out</span>
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={() => { setMenuOpen(false); onOpenLogin(); }}
                        className="w-full rounded-xl bg-[#141715] hover:bg-[#262C29] text-white py-2 text-xs font-semibold border-none cursor-pointer transition"
                      >
                        Passport Sign-In
                      </button>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </header>
  );
}
