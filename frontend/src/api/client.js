/**
 * TripSense API Client with Blueprint B ML Endpoints, Eco/Business Services,
 * Multi-Currency Formatting, & Offline Cache Support.
 */

const API_BASE = import.meta.env.VITE_API_URL || (window.location.port === '5173' ? 'http://127.0.0.1:8000' : '');

const CACHE_KEYS = {
  DESTINATIONS: "tripsense_cache_destinations",
  PLAN: "tripsense_cache_plan",
  SPOTS: "tripsense_cache_spots_",
  ROOM: "tripsense_cache_room",
  EXPENSES: "tripsense_expenses_v2",
  SETTLED_DEBTS: "tripsense_settled_debts_v2"
};

export function formatCurrency(amountBDT, currency = "BDT") {
  const val = Number(amountBDT || 0);
  if (currency === "USD") {
    return `$${(val / 115.0).toFixed(1)}`;
  }
  if (currency === "EUR") {
    return `€${(val / 124.0).toFixed(1)}`;
  }
  return `৳${Math.round(val).toLocaleString()}`;
}

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    if (!res.ok) throw new Error("Health check failed");
    return await res.json();
  } catch (err) {
    return { status: "offline", error: err.message };
  }
}

export async function fetchDestinations(forceOffline = false) {
  if (forceOffline) {
    const cached = localStorage.getItem(CACHE_KEYS.DESTINATIONS);
    if (cached) return { data: JSON.parse(cached), fromCache: true };
    return { data: ["Chittagong", "Cox's Bazar", "Sylhet", "Bandarban", "Dhaka", "Paris", "Tokyo"], fromCache: true };
  }

  try {
    const res = await fetch(`${API_BASE}/api/destinations`, { signal: AbortSignal.timeout(4000) });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    localStorage.setItem(CACHE_KEYS.DESTINATIONS, JSON.stringify(data));
    return { data, fromCache: false };
  } catch (err) {
    console.warn("Falling back to cached destinations:", err);
    const cached = localStorage.getItem(CACHE_KEYS.DESTINATIONS);
    if (cached) return { data: JSON.parse(cached), fromCache: true };
    return { data: ["Chittagong", "Cox's Bazar", "Sylhet", "Bandarban", "Dhaka", "Paris", "Tokyo"], fromCache: true };
  }
}

export async function fetchSpots(city, forceOffline = false) {
  const cityKey = (city || "").toLowerCase();
  const cacheKey = CACHE_KEYS.SPOTS + cityKey;

  if (forceOffline) {
    const cached = localStorage.getItem(cacheKey);
    return { data: cached ? JSON.parse(cached) : [], fromCache: true };
  }

  try {
    const res = await fetch(`${API_BASE}/api/spots?city=${encodeURIComponent(city)}`, { signal: AbortSignal.timeout(4000) });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    localStorage.setItem(cacheKey, JSON.stringify(data));
    return { data, fromCache: false };
  } catch (err) {
    console.warn(`Falling back to cached spots for ${city}:`, err);
    const cached = localStorage.getItem(cacheKey);
    if (cached) return { data: JSON.parse(cached), fromCache: true };
    return { data: [], fromCache: true };
  }
}

export async function generateGroupPlan(payload, forceOffline = false) {
  const cityKey = (payload.city || "").toLowerCase();
  const daysKey = payload.days || 3;
  const specificKey = `${CACHE_KEYS.PLAN}_${cityKey}_${daysKey}`;

  if (forceOffline) {
    const cached = localStorage.getItem(specificKey) || localStorage.getItem(CACHE_KEYS.PLAN);
    if (cached) return { data: JSON.parse(cached), fromCache: true };
  }

  try {
    const res = await fetch(`${API_BASE}/api/group/generate-plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(12000)
    });
    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`Plan generation failed (${res.status}): ${errText}`);
    }
    const data = await res.json();
    localStorage.setItem(specificKey, JSON.stringify(data));
    localStorage.setItem(CACHE_KEYS.PLAN, JSON.stringify(data));
    return { data, fromCache: false };
  } catch (err) {
    console.warn("Backend request failed, checking offline cache:", err);
    const cached = localStorage.getItem(specificKey) || localStorage.getItem(CACHE_KEYS.PLAN);
    if (cached) return { data: JSON.parse(cached), fromCache: true, error: err.message };
    throw err;
  }
}

export async function replanWeather(payload) {
  const res = await fetch(`${API_BASE}/api/itinerary/replan-weather`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(8000)
  });
  if (!res.ok) throw new Error(`Weather replan failed (${res.status})`);
  return await res.json();
}

export async function vetoSpot(payload) {
  const res = await fetch(`${API_BASE}/api/itinerary/veto-spot`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(10000)
  });
  if (!res.ok) throw new Error(`Veto spot failed (${res.status})`);
  return await res.json();
}

export async function nextActiveSwipe(history = [], maxCards = 6) {
  const res = await fetch(`${API_BASE}/api/ml/swipe/next`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ history, max_cards: maxCards }),
    signal: AbortSignal.timeout(6000)
  });
  if (!res.ok) throw new Error(`Active swipe failed (${res.status})`);
  return await res.json();
}

export async function fetchMlMetrics() {
  try {
    const res = await fetch(`${API_BASE}/api/ml/metrics`, { signal: AbortSignal.timeout(5000) });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function sendCopilotChat(payload) {
  const res = await fetch(`${API_BASE}/api/copilot/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(14000)
  });
  if (!res.ok) throw new Error(`Copilot chat failed (${res.status})`);
  return await res.json();
}

export async function fetchEcoReport(payload) {
  const res = await fetch(`${API_BASE}/api/sustainability/eco-report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(6000)
  });
  if (!res.ok) throw new Error(`Eco report failed (${res.status})`);
  return await res.json();
}

export async function reserveBooking(payload) {
  const res = await fetch(`${API_BASE}/api/bookings/reserve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(8000)
  });
  if (!res.ok) throw new Error(`Booking failed (${res.status})`);
  return await res.json();
}

export function saveRoomState(roomData) {
  try { localStorage.setItem(CACHE_KEYS.ROOM, JSON.stringify(roomData)); } catch {}
}

export function loadRoomState() {
  try {
    const data = localStorage.getItem(CACHE_KEYS.ROOM);
    return data ? JSON.parse(data) : null;
  } catch { return null; }
}

export function saveExpenses(expenses) {
  try { localStorage.setItem(CACHE_KEYS.EXPENSES, JSON.stringify(expenses)); } catch {}
}

export function loadExpenses() {
  try {
    const data = localStorage.getItem(CACHE_KEYS.EXPENSES);
    return data ? JSON.parse(data) : null;
  } catch { return null; }
}

export function saveSettledDebts(settledDebts) {
  try { localStorage.setItem(CACHE_KEYS.SETTLED_DEBTS, JSON.stringify(settledDebts)); } catch {}
}

export function loadSettledDebts() {
  try {
    const data = localStorage.getItem(CACHE_KEYS.SETTLED_DEBTS);
    return data ? JSON.parse(data) : null;
  } catch { return null; }
}

export function saveUser(userData) {
  try { localStorage.setItem("tripsense_auth_user", JSON.stringify(userData)); } catch {}
}

export function loadUser() {
  try {
    const data = localStorage.getItem("tripsense_auth_user");
    return data ? JSON.parse(data) : null;
  } catch { return null; }
}

export function clearUser() {
  try { localStorage.removeItem("tripsense_auth_user"); } catch {}
}

export function saveVetoTokens(tokens) {
  try { localStorage.setItem("tripsense_veto_tokens", JSON.stringify(tokens)); } catch {}
}

export function loadVetoTokens() {
  try {
    const data = localStorage.getItem("tripsense_veto_tokens");
    return data ? JSON.parse(data) : null;
  } catch { return null; }
}
