import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  Cpu,
  Cloud,
  Laptop,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  RefreshCw,
} from "lucide-react";
import {
  getBackendUrl,
  setBackendUrl,
  resetBackendUrl,
  probeBackendConnection,
} from "../api/client";

export default function BackendConnectModal({
  isOpen,
  onClose,
  connectionState,
  onConnectionUpdated,
}) {
  const [customUrl, setCustomUrl] = useState(() => getBackendUrl() || "");
  const [testing, setTesting] = useState(false);
  const [probeMsg, setProbeMsg] = useState(null);
  const [copiedCmd, setCopiedCmd] = useState(null);

  const presets = [
    {
      id: "hf",
      title: "Hugging Face Space (Free 16GB RAM)",
      subtitle: "Zero-cost PyTorch + CLIP cloud backend",
      placeholder: "https://sani0185-tripsense-api.hf.space",
      icon: Cloud,
      cmd: "python scripts/deploy_hf_space.py --space tripsense-api",
    },
    {
      id: "laptop",
      title: "RTX 3050 Laptop + Cloudflare Tunnel",
      subtitle: "Fastest local GPU inference over free HTTPS",
      placeholder: "http://127.0.0.1:8000",
      icon: Laptop,
      cmd: "powershell -ExecutionPolicy Bypass -File scripts/start_laptop_host.ps1",
    },
    {
      id: "azure",
      title: "Azure for Students / Custom Server",
      subtitle: "Student $100 credit VM or Render container",
      placeholder: "https://your-tripsense-api.azurewebsites.net",
      icon: Cpu,
      cmd: "uvicorn backend.app.main:app --host 0.0.0.0 --port 8000",
    },
  ];

  const handleCopy = (id, text) => {
    try {
      navigator.clipboard.writeText(text);
      setCopiedCmd(id);
      setTimeout(() => setCopiedCmd(null), 1800);
    } catch {}
  };

  const handleConnect = async (targetUrl) => {
    const clean = (targetUrl ?? customUrl).trim().replace(/\/+$/, "");
    setTesting(true);
    setProbeMsg(null);
    if (clean) {
      setBackendUrl(clean);
      setCustomUrl(clean);
    } else {
      resetBackendUrl();
    }
    const status = await probeBackendConnection(clean || undefined);
    setTesting(false);
    if (status.mode === "live") {
      setProbeMsg({
        ok: true,
        text: `Connected to Live Neural API (${status.latencyMs}ms • ${status.backbone || "CLIP + FairNet"})`,
      });
    } else {
      setProbeMsg({
        ok: false,
        text: "Endpoint offline or warming up — Instant Grounded Demo Engine remains active with 0ms latency.",
      });
    }
    if (onConnectionUpdated) onConnectionUpdated(status);
  };

  const handleUseDemo = async () => {
    resetBackendUrl();
    setCustomUrl("");
    const demoStatus = {
      mode: "demo",
      url: "built-in-demo",
      latencyMs: 1,
      backbone: "Instant Grounded Engine",
      fairnetLoaded: false,
    };
    setProbeMsg({
      ok: true,
      text: "Switched cleanly to Built-In Instant Demo Mode (68 verified POIs + Q1 FairNet benchmarks).",
    });
    if (onConnectionUpdated) onConnectionUpdated(demoStatus);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 100005,
            background: "rgba(18, 23, 21, 0.72)",
            backdropFilter: "blur(10px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "16px",
          }}
        >
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.97 }}
            transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
            style={{
              background: "var(--bg-chalk)",
              border: "1px solid var(--stone-border)",
              borderRadius: "28px",
              maxWidth: "590px",
              width: "100%",
              maxHeight: "90vh",
              overflowY: "auto",
              boxShadow: "0 28px 64px rgba(18, 23, 21, 0.38)",
            }}
          >
            {/* Header */}
            <div
              style={{
                background: "var(--granite-950)",
                color: "#FAF8F3",
                padding: "20px 24px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <div style={{ fontSize: "10px", fontWeight: 800, letterSpacing: "1px", color: "#E6A97A" }}>
                  HYBRID CLOUD • ZERO-COST AI RUNTIME
                </div>
                <h2 className="font-display" style={{ margin: "4px 0 0 0", fontSize: "21px", fontWeight: 800 }}>
                  Connect FairNet & Neuro-Symbolic Engine
                </h2>
              </div>
              <button
                type="button"
                onClick={onClose}
                style={{
                  background: "rgba(255,255,255,0.14)",
                  border: "none",
                  borderRadius: "50%",
                  width: "34px",
                  height: "34px",
                  color: "#FFFFFF",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <X size={18} />
              </button>
            </div>

            <div style={{ padding: "22px 24px" }}>
              {/* Current Mode Banner */}
              <div
                style={{
                  background: connectionState?.mode === "live" ? "var(--alpine-moss-soft)" : "var(--brass-soft)",
                  border: `1px solid ${connectionState?.mode === "live" ? "#B8D3C8" : "#E6CE9E"}`,
                  borderRadius: "16px",
                  padding: "14px 16px",
                  marginBottom: "18px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  flexWrap: "wrap",
                  gap: "10px",
                }}
              >
                <div>
                  <div
                    style={{
                      fontSize: "13px",
                      fontWeight: 800,
                      color: connectionState?.mode === "live" ? "var(--alpine-moss)" : "#7B5618",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                    }}
                  >
                    <Sparkles size={15} />
                    <span>
                      {connectionState?.mode === "live"
                        ? `Live Neural API Active (${connectionState.latencyMs || 12}ms)`
                        : "Instant Demo Mode Active (Built-In Fallback)"}
                    </span>
                  </div>
                  <div style={{ fontSize: "11px", color: "var(--granite-600)", marginTop: "3px" }}>
                    {connectionState?.mode === "live"
                      ? `Backbone: ${connectionState.backbone || "CLIP + FairNet"} • Auto-upgraded from local cache`
                      : "All 68 POIs, Swipe, Veto, Copilot & Q1 Benchmarks run at 0ms until a remote AI URL is online."}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleUseDemo}
                  style={{
                    background: "#FFFFFF",
                    color: "var(--granite-950)",
                    border: "1px solid var(--stone-border)",
                    borderRadius: "999px",
                    padding: "6px 12px",
                    fontSize: "11px",
                    fontWeight: 800,
                    cursor: "pointer",
                  }}
                >
                  Use Instant Demo
                </button>
              </div>

              {/* Endpoint Input */}
              <label
                style={{
                  display: "block",
                  fontSize: "11px",
                  fontWeight: 800,
                  letterSpacing: "0.6px",
                  color: "var(--granite-600)",
                  marginBottom: "6px",
                }}
              >
                REMOTE FASTAPI / CLOUDFLARE TUNNEL / HUGGING FACE SPACE URL
              </label>
              <div style={{ display: "flex", gap: "8px", marginBottom: "14px" }}>
                <input
                  type="url"
                  value={customUrl}
                  onChange={(e) => setCustomUrl(e.target.value)}
                  placeholder="https://your-space.hf.space or https://xxx.trycloudflare.com"
                  style={{
                    flex: 1,
                    padding: "11px 14px",
                    borderRadius: "12px",
                    border: "1px solid var(--stone-border)",
                    background: "#FFFFFF",
                    fontSize: "13px",
                    color: "var(--granite-950)",
                    fontFamily: "var(--font-mono)",
                  }}
                />
                <button
                  type="button"
                  onClick={() => handleConnect(customUrl)}
                  disabled={testing}
                  className="liquid-btn"
                  style={{
                    background: "var(--safety-orange)",
                    color: "#FFFFFF",
                    border: "none",
                    borderRadius: "12px",
                    padding: "0 18px",
                    fontSize: "12px",
                    fontWeight: 800,
                    cursor: "pointer",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  <RefreshCw size={14} className={testing ? "spin-slow" : ""} />
                  <span>{testing ? "Probing..." : "Test & Connect"}</span>
                </button>
              </div>

              {probeMsg && (
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "10px 14px",
                    borderRadius: "12px",
                    marginBottom: "16px",
                    fontSize: "12px",
                    fontWeight: 700,
                    background: probeMsg.ok ? "var(--alpine-moss-soft)" : "var(--safety-orange-soft)",
                    color: probeMsg.ok ? "var(--alpine-moss)" : "var(--safety-orange-hover)",
                  }}
                >
                  {probeMsg.ok ? <CheckCircle2 size={15} /> : <AlertCircle size={15} />}
                  <span>{probeMsg.text}</span>
                </div>
              )}

              {/* Free Hosting Presets */}
              <div style={{ fontSize: "11px", fontWeight: 800, letterSpacing: "0.6px", color: "var(--granite-600)", marginBottom: "10px" }}>
                ZERO-COST STUDENT HOSTING PRESETS
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {presets.map((p) => {
                  const Icon = p.icon;
                  return (
                    <div
                      key={p.id}
                      style={{
                        background: "#FFFFFF",
                        border: "1px solid var(--stone-border)",
                        borderRadius: "16px",
                        padding: "12px 14px",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "10px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                          <div
                            style={{
                              width: "34px",
                              height: "34px",
                              borderRadius: "10px",
                              background: "var(--bg-surface)",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              color: "var(--alpine-moss)",
                            }}
                          >
                            <Icon size={17} />
                          </div>
                          <div>
                            <div style={{ fontSize: "13px", fontWeight: 800, color: "var(--granite-950)" }}>
                              {p.title}
                            </div>
                            <div style={{ fontSize: "11px", color: "var(--granite-600)" }}>{p.subtitle}</div>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => {
                            setCustomUrl(p.placeholder);
                            handleConnect(p.placeholder);
                          }}
                          style={{
                            background: "var(--bg-surface)",
                            color: "var(--granite-950)",
                            border: "1px solid var(--stone-border)",
                            borderRadius: "999px",
                            padding: "5px 11px",
                            fontSize: "11px",
                            fontWeight: 700,
                            cursor: "pointer",
                          }}
                        >
                          Ping Preset
                        </button>
                      </div>

                      <div
                        style={{
                          marginTop: "9px",
                          background: "var(--granite-950)",
                          color: "#E8E4DA",
                          borderRadius: "10px",
                          padding: "7px 10px",
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          gap: "8px",
                          fontSize: "10px",
                          fontFamily: "var(--font-mono)",
                        }}
                      >
                        <span style={{ overflowX: "auto", whiteSpace: "nowrap" }}>{p.cmd}</span>
                        <button
                          type="button"
                          onClick={() => handleCopy(p.id, p.cmd)}
                          style={{
                            background: "transparent",
                            border: "none",
                            color: "#FAF8F3",
                            cursor: "pointer",
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "4px",
                            flexShrink: 0,
                          }}
                        >
                          {copiedCmd === p.id ? <Check size={13} color="#8CE0B5" /> : <Copy size={13} />}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
