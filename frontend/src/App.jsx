import React, { useState, useEffect, useCallback, useRef } from "react";
import Navbar from "./components/Navbar";
import ItineraryTab from "./components/ItineraryTab";
import LobbyTab from "./components/LobbyTab";
import ExpenseSplitterTab from "./components/ExpenseSplitterTab";
import FairnessInsightsTab from "./components/FairnessInsightsTab";
import SpotDetailModal from "./components/SpotDetailModal";
import DestinationDatePickerModal from "./components/DestinationDatePickerModal";
import LoginScreen from "./components/LoginScreen";
import TasteMatchDeck from "./components/TasteMatchDeck";
import TripSetupWizard from "./components/TripSetupWizard";
import AiSolverModal from "./components/AiSolverModal";
import ViralReelModal from "./components/ViralReelModal";
import AiCopilotModal from "./components/AiCopilotModal";
import BookingDrawer from "./components/BookingDrawer";
import CookieConsentBanner from "./components/CookieConsentBanner";
import EditorialFooter from "./components/EditorialFooter";
import FloatingQuickActions from "./components/FloatingQuickActions";
import {
  fetchDestinations,
  generateGroupPlan,
  replanWeather,
  vetoSpot,
  saveRoomState,
  loadExpenses,
  saveExpenses,
  loadSettledDebts,
  saveSettledDebts,
  saveUser,
  loadUser,
  clearUser,
  saveVetoTokens,
  loadVetoTokens
} from "./api/client";
import { Compass, Map, DollarSign, Users, Award, Bot } from "lucide-react";
import "./App.css";

const DEFAULT_MEMBERS = [
  { name: "Rahat", interests: ["Historical", "Culture"], budget_tier: "Budget" },
  { name: "Sadia", interests: ["Beach", "Nature"], budget_tier: "Mid-range" },
  { name: "Fahim", interests: ["Adventure", "Food"], budget_tier: "Luxury" }
];

const DEFAULT_EXPENSES = [
  {
    id: "exp-1",
    title: "Chittagong Mezban Beef Lunch",
    amountBDT: 1800,
    paidBy: "Rahat",
    splitWith: ["Rahat", "Sadia", "Fahim"],
    date: "Aug 12"
  },
  {
    id: "exp-2",
    title: "CNG / Shared Microbus to Patenga",
    amountBDT: 450,
    paidBy: "Sadia",
    splitWith: ["Rahat", "Sadia", "Fahim"],
    date: "Aug 12"
  }
];

export default function App() {
  const [currentUser, setCurrentUser] = useState(() => loadUser() || null);
  const [showLoginModal, setShowLoginModal] = useState(false);

  // Onboarding, Wizard, Copilot & Booking Drawer
  const [showTasteMatch, setShowTasteMatch] = useState(false);
  const [showSetupWizard, setShowSetupWizard] = useState(false);
  const [isSolverActive, setIsSolverActive] = useState(false);
  const [isReelOpen, setIsReelOpen] = useState(false);
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [bookingSpot, setBookingSpot] = useState(null);
  const [vetoNotification, setVetoNotification] = useState(null);

  // Localization (Language & Multi-Currency)
  const [lang, setLang] = useState("EN");
  const [currency, setCurrency] = useState("BDT");

  // Navigation & modals
  const [activeTab, setActiveTab] = useState("itinerary");
  const [isDatePickerOpen, setIsDatePickerOpen] = useState(false);
  const [activeModalSpot, setActiveModalSpot] = useState(null);

  // Offline & Connectivity
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isOfflineMode, setIsOfflineMode] = useState(false);

  // Trip Configuration
  const [city, setCity] = useState("Chittagong");
  const [startDate, setStartDate] = useState("2026-08-12");
  const [endDate, setEndDate] = useState("2026-08-14");
  const [days, setDays] = useState(3);
  const [roomCode, setRoomCode] = useState("CTG-882");
  const [availableDestinations, setAvailableDestinations] = useState([
    "Chittagong", "Cox's Bazar", "Sylhet", "Bandarban", "Dhaka"
  ]);

  // Group Consensus Settings (Default: TripSense-FairNet Neural Model)
  const [members, setMembers] = useState(DEFAULT_MEMBERS);
  const [consensusStrategy, setConsensusStrategy] = useState("fairnet");
  const [promoteHiddenGems, setPromoteHiddenGems] = useState(true);
  const [pace, setPace] = useState("Moderate");

  const [vetoTokens, setVetoTokens] = useState(() => loadVetoTokens() || { Rahat: 1, Sadia: 1, Fahim: 1 });

  // Plan Data
  const [plan, setPlan] = useState(null);
  const [originalPlan, setOriginalPlan] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Weather Dynamic Replanning
  const [isRainSimulated, setIsRainSimulated] = useState(false);
  const [isRerouted, setIsRerouted] = useState(false);
  const [isReplanning, setIsReplanning] = useState(false);
  const [replannedNotifications, setReplannedNotifications] = useState([]);

  // Expenses
  const [expenses, setExpenses] = useState(() => loadExpenses() || DEFAULT_EXPENSES);
  const [settledDebts, setSettledDebts] = useState(() => loadSettledDebts() || {});

  const hasInitialized = useRef(false);

  useEffect(() => { saveVetoTokens(vetoTokens); }, [vetoTokens]);
  useEffect(() => { saveExpenses(expenses); }, [expenses]);
  useEffect(() => { saveSettledDebts(settledDebts); }, [settledDebts]);

  const handleSetMembers = (newMembers) => {
    const newNames = newMembers.map((m) => m.name);
    setMembers(newMembers);
    setExpenses((prevExpenses) =>
      prevExpenses.map((exp) => {
        const validPaidBy = newNames.includes(exp.paidBy) ? exp.paidBy : (newNames[0] || "");
        const validSplit = (exp.splitWith || []).filter((name) => newNames.includes(name));
        return { ...exp, paidBy: validPaidBy, splitWith: validSplit.length > 0 ? validSplit : newNames };
      })
    );
    setVetoTokens((prev) => {
      const updated = { ...prev };
      newNames.forEach((n) => {
        if (updated[n] === undefined) updated[n] = 1;
      });
      return updated;
    });
  };

  useEffect(() => {
    const on = () => setIsOnline(true);
    const off = () => setIsOnline(false);
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    return () => {
      window.removeEventListener("online", on);
      window.removeEventListener("offline", off);
    };
  }, []);

  useEffect(() => {
    fetchDestinations(isOfflineMode).then(({ data }) => {
      if (data && data.length > 0) setAvailableDestinations(data);
    });
  }, [isOfflineMode]);

  useEffect(() => {
    saveRoomState({ city, startDate, endDate, days, roomCode, members, consensusStrategy, promoteHiddenGems, pace });
  }, [city, startDate, endDate, days, roomCode, members, consensusStrategy, promoteHiddenGems, pace]);

  const handleGeneratePlan = useCallback(async (overrides = {}) => {
    const targetCity = overrides.city || city;
    const targetDays = overrides.days || days;
    const targetPace = overrides.pace || pace;
    const targetMembers = overrides.members || members;
    const targetStrategy = overrides.consensusStrategy || consensusStrategy;
    const targetPromoteGems = overrides.promoteHiddenGems !== undefined ? overrides.promoteHiddenGems : promoteHiddenGems;

    setIsLoading(true);
    setErrorMsg(null);
    setIsRerouted(false);
    setIsRainSimulated(false);
    setReplannedNotifications([]);

    try {
      const payload = {
        city: targetCity,
        days: targetDays,
        pace: targetPace,
        members: targetMembers,
        consensus_strategy: targetStrategy,
        promote_hidden_gems: targetPromoteGems
      };
      const { data } = await generateGroupPlan(payload, isOfflineMode);
      setPlan(data);
      setOriginalPlan(data);
      setActiveTab("itinerary");
    } catch (err) {
      setErrorMsg(err.message || "Failed to generate plan.");
    } finally {
      setIsLoading(false);
    }
  }, [city, days, pace, members, consensusStrategy, promoteHiddenGems, isOfflineMode]);

  // Immediately load the flagship Chittagong FairNet showcase so editorial homepage is live on arrival
  useEffect(() => {
    if (!hasInitialized.current) {
      hasInitialized.current = true;
      handleGeneratePlan();
    }
  }, [handleGeneratePlan]);

  const handleAutoRerouteWeather = async () => {
    if (!plan || !plan.daily_schedule || plan.daily_schedule.length === 0) return;
    setIsReplanning(true);
    try {
      const allNotifications = [];
      let totalSwapped = 0;
      const updatedDailySchedule = [];
      let newTotalCostBdt = 0;
      let newTotalCostUsd = 0;
      let newTotalDistance = 0;

      const usedSpotIds = new Set();
      plan.daily_schedule.forEach((d) => d.spots.forEach((s) => usedSpotIds.add(s.id)));

      for (const day of plan.daily_schedule) {
        const hasOutdoor = day.spots.some((s) => s.indoor_outdoor === "Outdoor");
        if (hasOutdoor) {
          const otherDaysIds = Array.from(usedSpotIds).filter((id) => !day.spots.some((s) => s.id === id));
          const result = await replanWeather({
            city,
            weather_condition: "Heavy Rain",
            members,
            current_spots: day.spots,
            all_scheduled_spot_ids: otherDaysIds
          });
          if (result && result.updated_spots) {
            const daySpots = result.updated_spots;
            totalSwapped += (result.swapped_spots_count || 0);
            if (result.notifications?.length) allNotifications.push(...result.notifications);

            day.spots.forEach((s) => usedSpotIds.delete(s.id));
            daySpots.forEach((s) => usedSpotIds.add(s.id));

            const dayCostBdt = daySpots.reduce((sum, s) => sum + (s.estimated_cost_bdt || 0), 0);
            const dayCostUsd = daySpots.reduce((sum, s) => sum + (s.estimated_cost_usd || 0), 0);
            const dayDistance = daySpots.reduce((sum, s) => sum + (s.transit_from_prev_km || 0), 0);

            newTotalCostBdt += dayCostBdt;
            newTotalCostUsd += dayCostUsd;
            newTotalDistance += dayDistance;

            updatedDailySchedule.push({
              ...day,
              spots: daySpots,
              daily_cost_bdt: Math.round(dayCostBdt * 10) / 10,
              daily_cost_usd: Math.round(dayCostUsd * 10) / 10,
              daily_distance_km: Math.round(dayDistance * 100) / 100
            });
            continue;
          }
        }
        newTotalCostBdt += (day.daily_cost_bdt || 0);
        newTotalCostUsd += (day.daily_cost_usd || 0);
        newTotalDistance += (day.daily_distance_km || 0);
        updatedDailySchedule.push(day);
      }

      setPlan({
        ...plan,
        total_estimated_cost_bdt: Math.round(newTotalCostBdt * 10) / 10,
        total_estimated_cost_usd: Math.round(newTotalCostUsd * 10) / 10,
        total_distance_km: Math.round(newTotalDistance * 100) / 100,
        daily_schedule: updatedDailySchedule
      });
      setIsRerouted(totalSwapped > 0);
      setReplannedNotifications(
        totalSwapped > 0 ? allNotifications : [`⚠️ No indoor substitutes available in ${city}.`]
      );
    } catch (err) {
      alert("Failed to adapt itinerary for weather: " + err.message);
    } finally {
      setIsReplanning(false);
    }
  };

  const handleRevertWeatherPlan = () => {
    if (originalPlan) {
      setPlan(JSON.parse(JSON.stringify(originalPlan)));
      setIsRerouted(false);
      setReplannedNotifications([]);
    }
  };

  const handleToggleRainSimulation = () => {
    if (isRainSimulated) {
      setIsRainSimulated(false);
      if (isRerouted) handleRevertWeatherPlan();
    } else {
      setIsRainSimulated(true);
    }
  };

  const handleVetoSpot = async (spot, memberName) => {
    if (!plan || !plan.daily_schedule) return null;
    const targetDayIndex = plan.daily_schedule.findIndex((d) => d.spots.some((s) => s.id === spot.id));
    if (targetDayIndex === -1) return null;
    const targetDay = plan.daily_schedule[targetDayIndex];

    try {
      const allTripSpotIds = plan.daily_schedule.flatMap((d) => d.spots.map((s) => s.id));
      const result = await vetoSpot({
        city,
        spot_id: spot.id,
        vetoed_by: memberName,
        members,
        current_spots: targetDay.spots,
        all_scheduled_spot_ids: allTripSpotIds
      });

      if (result) {
        if (result.notification) {
          setVetoNotification(result.notification);
          setTimeout(() => setVetoNotification(null), 6000);
        }
        if (result.success && result.updated_spots) {
          const updatedDailySchedule = [...plan.daily_schedule];
          const updatedSpots = result.updated_spots;
          const dayCostBdt = updatedSpots.reduce((sum, s) => sum + (s.estimated_cost_bdt || 0), 0);
          const dayCostUsd = updatedSpots.reduce((sum, s) => sum + (s.estimated_cost_usd || 0), 0);
          const dayDistance = updatedSpots.reduce((sum, s) => sum + (s.transit_from_prev_km || 0), 0);

          updatedDailySchedule[targetDayIndex] = {
            ...targetDay,
            spots: updatedSpots,
            daily_cost_bdt: Math.round(dayCostBdt * 10) / 10,
            daily_cost_usd: Math.round(dayCostUsd * 10) / 10,
            daily_distance_km: Math.round(dayDistance * 100) / 100
          };

          setPlan({
            ...plan,
            daily_schedule: updatedDailySchedule,
            total_estimated_cost_bdt: Math.round(updatedDailySchedule.reduce((sum, d) => sum + (d.daily_cost_bdt || 0), 0) * 10) / 10,
            total_estimated_cost_usd: Math.round(updatedDailySchedule.reduce((sum, d) => sum + (d.daily_cost_usd || 0), 0) * 10) / 10,
            total_distance_km: Math.round(updatedDailySchedule.reduce((sum, d) => sum + (d.daily_distance_km || 0), 0) * 100) / 100
          });

          setVetoTokens((prev) => ({
            ...prev,
            [memberName]: Math.max(0, (prev[memberName] || 1) - 1)
          }));
        }
        return result;
      }
    } catch (err) {
      alert("Failed to veto spot: " + err.message);
    }
    return null;
  };

  const handleUserLogin = (user) => {
    saveUser(user);
    setCurrentUser(user);
    setShowLoginModal(false);
    setMembers((prev) => {
      if (prev.some((m) => m.name.toLowerCase() === user.name.toLowerCase())) return prev;
      return [{ name: user.name, interests: user.interests || ["Historical", "Beach"], budget_tier: user.budget_tier || "Mid-range" }, ...prev];
    });
    setShowTasteMatch(true);
  };

  const handleLogout = () => {
    clearUser();
    setCurrentUser(null);
  };

  const handleTasteMatchComplete = (interests, tasteEmbedding) => {
    setShowTasteMatch(false);
    const activeName = currentUser?.name || members[0]?.name || "Rahat";
    if (currentUser) {
      const updatedUser = { ...currentUser, interests, taste_embedding: tasteEmbedding };
      saveUser(updatedUser);
      setCurrentUser(updatedUser);
    }
    const updatedMembers = members.map((m) =>
      m.name.toLowerCase() === activeName.toLowerCase()
        ? { ...m, interests, taste_embedding: tasteEmbedding }
        : m
    );
    setMembers(updatedMembers);
    setShowSetupWizard(true);
  };

  const handleWizardStartSolver = (config) => {
    setCity(config.city);
    setDays(config.days);
    setStartDate(config.startDate);
    setEndDate(config.endDate);
    setRoomCode(config.roomCode);
    setMembers(config.members);
    setPace(config.pace);
    setShowSetupWizard(false);
    setIsSolverActive(true);
    handleGeneratePlan({ city: config.city, days: config.days, members: config.members, pace: config.pace });
  };

  const allItinerarySpots = (plan?.daily_schedule || []).flatMap((d) => d.spots || []);

  return (
    <div className="tripsense-app">
      {showLoginModal && (
        <LoginScreen onLogin={handleUserLogin} onClose={() => setShowLoginModal(false)} />
      )}

      {showTasteMatch && (
        <TasteMatchDeck
          userName={currentUser?.name || members[0]?.name || "Explorer"}
          onComplete={handleTasteMatchComplete}
          onSkip={() => { setShowTasteMatch(false); setShowSetupWizard(true); }}
        />
      )}

      {showSetupWizard && (
        <TripSetupWizard
          initialCity={city}
          initialDays={days}
          initialMembers={members}
          onStartSolver={handleWizardStartSolver}
          onCancel={() => setShowSetupWizard(false)}
        />
      )}

      {isSolverActive && (
        <AiSolverModal city={city} onFinish={() => { setIsSolverActive(false); setActiveTab("itinerary"); }} />
      )}

      {isReelOpen && (
        <ViralReelModal plan={plan} city={city} members={members} onClose={() => setIsReelOpen(false)} />
      )}

      <AiCopilotModal
        isOpen={isCopilotOpen}
        onClose={() => setIsCopilotOpen(false)}
        city={city}
        plan={plan}
        members={members}
        expenses={expenses}
        onSimulateRain={handleToggleRainSimulation}
        onOpenFairness={() => setActiveTab("fairness")}
        onOpenExpenses={() => setActiveTab("expenses")}
      />

      <BookingDrawer
        spot={bookingSpot}
        isOpen={Boolean(bookingSpot)}
        onClose={() => setBookingSpot(null)}
        defaultDate={startDate}
        defaultGroupSize={members.length || 3}
        defaultLeadName={currentUser?.name || members[0]?.name || "Rahat"}
        currency={currency}
        availableEcoPoints={plan?.eco_summary?.total_eco_points || 180}
      />

      <Navbar
        city={city}
        startDate={startDate}
        endDate={endDate}
        days={days}
        roomCode={roomCode}
        members={members}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenDatePicker={() => setIsDatePickerOpen(true)}
        isOfflineMode={isOfflineMode}
        onToggleOffline={() => setIsOfflineMode(!isOfflineMode)}
        isOnline={isOnline}
        currentUser={currentUser}
        onLogout={handleLogout}
        onOpenLogin={() => setShowLoginModal(true)}
        onOpenTasteMatch={() => setShowTasteMatch(true)}
        onOpenSetupWizard={() => setShowSetupWizard(true)}
        onOpenReel={() => setIsReelOpen(true)}
        onOpenCopilot={() => setIsCopilotOpen(true)}
        lang={lang}
        setLang={setLang}
        currency={currency}
        setCurrency={setCurrency}
      />

      <main className="main-content">
        {(isOfflineMode || !isOnline) && (
          <div className="offline-notice-banner">
            <span className="dot" />
            <span>
              <strong>Offline Cache Active:</strong> Serving locally persisted itinerary, group consensus, and expense ledger.
            </span>
          </div>
        )}

        {errorMsg && (
          <div className="error-notice-banner">
            <span>⚠️ {errorMsg}</span>
            <button type="button" onClick={() => handleGeneratePlan()}>Retry</button>
          </div>
        )}

        <div style={{ display: activeTab === "itinerary" ? "block" : "none" }}>
          <ItineraryTab
            plan={plan}
            city={city}
            startDate={startDate}
            onGeneratePlan={() => handleGeneratePlan()}
            isLoading={isLoading}
            onSelectSpot={(spot) => setActiveModalSpot(spot)}
            isRainSimulated={isRainSimulated}
            onToggleRainSimulation={handleToggleRainSimulation}
            onAutoReroute={handleAutoRerouteWeather}
            isRerouted={isRerouted}
            onRevertPlan={handleRevertWeatherPlan}
            isReplanning={isReplanning}
            replannedNotifications={replannedNotifications}
            members={members}
            vetoTokens={vetoTokens}
            onVetoSpot={handleVetoSpot}
            onBookSpot={(spot) => setBookingSpot(spot)}
            currentUser={currentUser}
            expenses={expenses}
            onOpenReel={() => setIsReelOpen(true)}
            onOpenSetupWizard={() => setShowSetupWizard(true)}
            onOpenSwipe={() => setShowTasteMatch(true)}
            onOpenLogin={() => setShowLoginModal(true)}
            onOpenMlLab={() => setActiveTab("fairness")}
            vetoNotification={vetoNotification}
            lang={lang}
            currency={currency}
          />
        </div>

        <div style={{ display: activeTab === "lobby" ? "block" : "none" }}>
          <LobbyTab
            roomCode={roomCode}
            members={members}
            setMembers={handleSetMembers}
            consensusStrategy={consensusStrategy}
            setConsensusStrategy={setConsensusStrategy}
            promoteHiddenGems={promoteHiddenGems}
            setPromoteHiddenGems={setPromoteHiddenGems}
            pace={pace}
            setPace={setPace}
            onGeneratePlan={() => handleGeneratePlan()}
            isLoading={isLoading}
          />
        </div>

        <div style={{ display: activeTab === "expenses" ? "block" : "none" }}>
          <ExpenseSplitterTab
            members={members}
            itinerarySpots={allItinerarySpots}
            expenses={expenses}
            setExpenses={setExpenses}
            settledDebts={settledDebts}
            setSettledDebts={setSettledDebts}
          />
        </div>

        <div style={{ display: activeTab === "fairness" ? "block" : "none" }}>
          <FairnessInsightsTab
            plan={plan}
            members={members}
            consensusStrategy={consensusStrategy}
            city={city}
            currency={currency}
          />
        </div>
      </main>

      <EditorialFooter onOpenMlLab={() => setActiveTab("fairness")} />
      <FloatingQuickActions city={city} roomCode={roomCode} onOpenCopilot={() => setIsCopilotOpen(true)} />
      <CookieConsentBanner />

      <DestinationDatePickerModal
        isOpen={isDatePickerOpen}
        onClose={() => setIsDatePickerOpen(false)}
        currentCity={city}
        startDate={startDate}
        endDate={endDate}
        availableDestinations={availableDestinations}
        onSave={(data) => {
          setCity(data.city);
          setStartDate(data.startDate);
          setEndDate(data.endDate);
          setDays(data.days);
          const prefix = data.city.substring(0, 3).toUpperCase();
          setRoomCode(`${prefix}-${Math.floor(100 + Math.random() * 900)}`);
          handleGeneratePlan({ city: data.city, days: data.days });
        }}
      />

      <SpotDetailModal
        spot={activeModalSpot}
        onClose={() => setActiveModalSpot(null)}
        onVeto={(spot) => handleVetoSpot(spot, currentUser?.name || "Rahat")}
        onBook={(spot) => setBookingSpot(spot)}
        userVetoTokens={vetoTokens[currentUser?.name || "Rahat"] ?? 1}
        currentMemberName={currentUser?.name || "Rahat"}
        currency={currency}
      />

      {/* Mobile Bottom Dock */}
      <nav className="mobile-bottom-dock">
        {[
          { id: "itinerary", label: "Explore", icon: Compass },
          { id: "map", label: "Map", icon: Map },
          { id: "expenses", label: "Splitwise", icon: DollarSign },
          { id: "lobby", label: "Squad", icon: Users },
          { id: "fairness", label: "Q1 Lab", icon: Award },
          { id: "copilot", label: "Copilot", icon: Bot },
        ].map((item) => {
          const Icon = item.icon;
          const active = activeTab === item.id || (item.id === "copilot" && isCopilotOpen);
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => {
                if (item.id === "map") {
                  setActiveTab("itinerary");
                  setTimeout(() => document.getElementById("map-section")?.scrollIntoView({ behavior: "smooth" }), 80);
                } else if (item.id === "copilot") {
                  setIsCopilotOpen(true);
                } else {
                  setActiveTab(item.id);
                }
              }}
              style={{
                background: "none",
                border: "none",
                color: active ? "var(--safety-orange)" : "var(--granite-600)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "2px",
                fontSize: "10px",
                fontWeight: active ? 800 : 600,
                cursor: "pointer",
              }}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}
