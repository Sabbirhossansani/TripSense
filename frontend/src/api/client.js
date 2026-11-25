/**
 * TripSense Hybrid Cloud / Laptop / Zero-Latency Offline Demo API Client.
 *
 * Connection priority:
 *   1. User-configured remote AI URL in localStorage (`tripsense_backend_url`) — e.g. HF Space, Cloudflare Tunnel, Azure
 *   2. Build-time `VITE_API_URL` environment variable
 *   3. Local Vite dev backend (`http://127.0.0.1:8000` when running on port 5173)
 *   4. Same-origin (`""`) when hosted directly via FastAPI/uvicorn
 *
 * Whenever no remote PyTorch backend is online (e.g. cold static Vercel deployment),
 * every API function transparently returns grounded domain results via `offlineDemoEngine.js`.
 */
import {
  demoDestinations,
  demoSpots,
  demoGenerateGroupPlan,
  demoReplanWeather,
  demoVetoSpot,
  demoNextActiveSwipe,
  demoCopilotChat,
  demoEcoReport,
  demoReserveBooking,
  demoMlMetrics,
} from "../data/offlineDemoEngine";

const BACKEND_URL_KEY = "tripsense_backend_url";

export function getBackendUrl() {
  try {
    const saved = localStorage.getItem(BACKEND_URL_KEY);
    if (saved && saved.trim()) return saved.trim().replace(/\/+$/, "");
  } catch {}
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && envUrl.trim()) return envUrl.trim().replace(/\/+$/, "");
  if (typeof window !== "undefined" && window.location.port === "5173") {
    return "http://127.0.0.1:8000";
  }
  return "";
}

export function setBackendUrl(url) {
  try {
    if (url && url.trim()) {
      localStorage.setItem(BACKEND_URL_KEY, url.trim().replace(/\/+$/, ""));
    } else {
      localStorage.removeItem(BACKEND_URL_KEY);
    }
  } catch {}
}

export function resetBackendUrl() {
  try {
    localStorage.removeItem(BACKEND_URL_KEY);
  } catch {}
}

async function fetchJsonSafe(path, options = {}, timeoutMs = 4500) {
  const base = getBackendUrl();
  const url = `${base}${path}`;
  const res = await fetch(url, {
    ...options,
    signal: AbortSignal.timeout(timeoutMs),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const ct = (res.headers.get("content-type") || "").toLowerCase();
  if (!ct.includes("application/json")) {
    // Prevents static Vercel SPA HTML rewrite from masquerading as API JSON
    throw new Error("Non-JSON response (static host active)");
  }
  return await res.json();
}

export async function probeBackendConnection(overrideUrl) {
  const base = overrideUrl !== undefined ? overrideUrl.replace(/\/+$/, "") : getBackendUrl();
  const t0 = performance.now();
  try {
    const res = await fetch(`${base}/health`, { signal: AbortSignal.timeout(2500) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const ct = (res.headers.get("content-type") || "").toLowerCase();
    if (!ct.includes("application/json")) throw new Error("Static host");
    const data = await res.json();
    if (data?.status !== "healthy") throw new Error("Unhealthy status");
    return {
      mode: "live",
      url: base || window.location.origin,
      latencyMs: Math.max(1, Math.round(performance.now() - t0)),
      backbone: data.backbone || "openai/clip-vit-base-patch32",
      fairnetLoaded: Boolean(data.fairnet_loaded),
      totalSpots: data.total_spots_loaded || 68,
    };
  } catch {
    return {
      mode: "demo",
      url: "built-in-demo",
      latencyMs: 1,
      backbone: "Instant Grounded Engine",
      fairnetLoaded: false,
      totalSpots: 68,
    };
  }
}

const CACHE_KEYS = {
  DESTINATIONS: "tripsense_cache_destinations",
  PLAN: "tripsense_cache_plan",
  SPOTS: "tripsense_cache_spots_",
  ROOM: "tripsense_cache_room",
  EXPENSES: "tripsense_expenses_v2",
  SETTLED_DEBTS: "tripsense_settled_debts_v2",
};

export function formatCurrency(amountBDT, currency = "BDT") {
  const val = Number(amountBDT || 0);
  if (currency === "USD") return `$${(val / 115.0).toFixed(1)}`;
  if (currency === "EUR") return `€${(val / 124.0).toFixed(1)}`;
  return `৳${Math.round(val).toLocaleString()}`;
}

export async function checkBackendHealth() {
  return probeBackendConnection();
}

export async function fetchDestinations(forceOffline = false) {
  if (!forceOffline) {
    try {
      const data = await fetchJsonSafe("/api/destinations", {}, 3000);
      localStorage.setItem(CACHE_KEYS.DESTINATIONS, JSON.stringify(data));
      return { data, fromCache: false, source: "live" };
    } catch {}
  }
  const cached = localStorage.getItem(CACHE_KEYS.DESTINATIONS);
  if (cached) return { data: JSON.parse(cached), fromCache: true, source: "demo" };
  return { data: demoDestinations(), fromCache: true, source: "demo" };
}

export async function fetchSpots(city, forceOffline = false) {
  const cityKey = (city || "").toLowerCase();
  const cacheKey = CACHE_KEYS.SPOTS + cityKey;
  if (!forceOffline) {
    try {
      const data = await fetchJsonSafe(`/api/spots?city=${encodeURIComponent(city)}`, {}, 3000);
      localStorage.setItem(cacheKey, JSON.stringify(data));
      return { data, fromCache: false, source: "live" };
    } catch {}
  }
  const cached = localStorage.getItem(cacheKey);
  if (cached) return { data: JSON.parse(cached), fromCache: true, source: "demo" };
  return { data: demoSpots(city), fromCache: true, source: "demo" };
}

export async function generateGroupPlan(payload, forceOffline = false) {
  const cityKey = (payload.city || "").toLowerCase();
  const daysKey = payload.days || 3;
  const specificKey = `${CACHE_KEYS.PLAN}_${cityKey}_${daysKey}`;

  if (!forceOffline) {
    try {
      const data = await fetchJsonSafe(
        "/api/group/generate-plan",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        },
        9000
      );
      localStorage.setItem(specificKey, JSON.stringify(data));
      localStorage.setItem(CACHE_KEYS.PLAN, JSON.stringify(data));
      return { data, fromCache: false, source: "live" };
    } catch {}
  }

  // Instant grounded demo synthesis ensures 0ms reliability even on cold static Vercel
  const demoPlan = demoGenerateGroupPlan(payload);
  return { data: demoPlan, fromCache: true, source: "demo" };
}

export async function replanWeather(payload) {
  try {
    return await fetchJsonSafe(
      "/api/itinerary/replan-weather",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
      6000
    );
  } catch {
    return demoReplanWeather(payload);
  }
}

export async function vetoSpot(payload) {
  try {
    return await fetchJsonSafe(
      "/api/itinerary/veto-spot",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
      7000
    );
  } catch {
    return demoVetoSpot(payload);
  }
}

export async function nextActiveSwipe(history = [], maxCards = 6) {
  try {
    return await fetchJsonSafe(
      "/api/ml/swipe/next",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ history, max_cards: maxCards }),
      },
      4500
    );
  } catch {
    return demoNextActiveSwipe(history, maxCards);
  }
}

export async function fetchMlMetrics() {
  try {
    const res = await fetchJsonSafe("/api/ml/metrics", {}, 4000);
    if (res && res.group_consensus_comparison) return res;
  } catch {}
  return demoMlMetrics();
}

export async function sendCopilotChat(payload) {
  try {
    return await fetchJsonSafe(
      "/api/copilot/chat",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
      12000
    );
  } catch {
    return demoCopilotChat(payload);
  }
}

export async function fetchEcoReport(payload) {
  try {
    return await fetchJsonSafe(
      "/api/sustainability/eco-report",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
      5000
    );
  } catch {
    return demoEcoReport(payload);
  }
}

export async function reserveBooking(payload) {
  try {
    return await fetchJsonSafe(
      "/api/bookings/reserve",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
      6000
    );
  } catch {
    return demoReserveBooking(payload);
  }
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
