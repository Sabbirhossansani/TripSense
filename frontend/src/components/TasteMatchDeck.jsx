import React, { useState, useEffect, useRef } from "react";
import { Heart, X, Star, Sparkles, Check, ChevronRight, Brain } from "lucide-react";
import { nextActiveSwipe } from "../api/client";

const FALLBACK_CARD = {
  id: "card-street-food",
  title: "Chittagong Mezban & Old Dhaka Night Food Lanes",
  category: "Food",
  badge: "Culinary Trail",
  tag: "Local SME Kitchens",
  image: "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=900&q=80",
  description: "Slow-cooked spiced Mezban beef, smoky charcoal kebabs, traditional Bakarkhani, and heritage food alleys.",
};

export default function TasteMatchDeck({ onComplete, onSkip, userName = "Explorer" }) {
  const [history, setHistory] = useState([]);
  const [swipeState, setSwipeState] = useState({
    completed: false,
    step: 0,
    total_steps: 6,
    confidence_pct: 22.0,
    next_card: FALLBACK_CARD,
    inferred_interests: ["Food", "Nature", "Historical"],
    category_scores: {},
    taste_embedding: [],
    information_gain: 0.42,
  });
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [stampFeedback, setStampFeedback] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const dragStartRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    let active = true;
    nextActiveSwipe([], 6)
      .then((res) => {
        if (active && res) setSwipeState(res);
      })
      .catch(() => {});
    return () => { active = false; };
  }, []);

  const currentCard = swipeState.next_card || FALLBACK_CARD;
  const totalCards = swipeState.total_steps || 6;

  const handleVote = async (action) => {
    if (isSyncing || swipeState.completed) return;
    setStampFeedback(action);
    const nextHist = [...history, { card_id: currentCard.id, action }];
    setHistory(nextHist);
    setIsSyncing(true);

    setTimeout(async () => {
      setDragOffset({ x: 0, y: 0 });
      setStampFeedback(null);
      try {
        const res = await nextActiveSwipe(nextHist, totalCards);
        setSwipeState(res);
      } catch {
        const step = nextHist.length;
        setSwipeState((prev) => ({
          ...prev,
          completed: step >= totalCards,
          step,
          confidence_pct: Math.min(95, Math.round(25 + step * 11.5)),
        }));
      } finally {
        setIsSyncing(false);
      }
    }, 240);
  };

  const handlePointerDown = (e) => {
    setIsDragging(true);
    dragStartRef.current = { x: e.clientX, y: e.clientY };
  };

  const handlePointerMove = (e) => {
    if (!isDragging) return;
    const dx = e.clientX - dragStartRef.current.x;
    const dy = e.clientY - dragStartRef.current.y;
    setDragOffset({ x: dx, y: dy });
    if (dx > 65) setStampFeedback("like");
    else if (dx < -65) setStampFeedback("pass");
    else if (dy < -65) setStampFeedback("super");
    else setStampFeedback(null);
  };

  const handlePointerUp = () => {
    if (!isDragging) return;
    setIsDragging(false);
    if (dragOffset.x > 85) handleVote("like");
    else if (dragOffset.x < -85) handleVote("pass");
    else if (dragOffset.y < -85) handleVote("super");
    else {
      setDragOffset({ x: 0, y: 0 });
      setStampFeedback(null);
    }
  };

  if (swipeState.completed) {
    return (
      <div
        style={{
          position: "fixed",
          inset: 0,
          zIndex: 99999,
          background: "linear-gradient(155deg, #1A1D1C 0%, #25463B 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "16px",
        }}
      >
        <div
          style={{
            background: "#FAF9F6",
            borderRadius: "28px",
            padding: "34px 26px",
            maxWidth: "450px",
            width: "100%",
            textAlign: "center",
            boxShadow: "0 25px 60px rgba(0,0,0,0.45)",
            border: "1px solid var(--stone-border)",
          }}
        >
          <div
            style={{
              width: "70px",
              height: "70px",
              borderRadius: "50%",
              background: "var(--alpine-moss)",
              color: "#FFFFFF",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: "14px",
              boxShadow: "0 10px 24px rgba(37, 70, 59, 0.35)",
            }}
          >
            <Sparkles size={34} />
          </div>

          <h2 className="font-display" style={{ fontSize: "24px", fontWeight: 900, color: "var(--granite-950)", margin: "0 0 6px 0" }}>
            {userName}'s Taste Vector Calibrated
          </h2>
          <p style={{ fontSize: "13px", color: "var(--granite-600)", margin: "0 0 18px 0", lineHeight: 1.5 }}>
            Bayesian Active Learning converged at <strong className="font-mono-num" style={{ color: "var(--alpine-moss)" }}>{swipeState.confidence_pct}%</strong> confidence. Ready for <strong>TripSense-FairNet</strong> group consensus!
          </p>

          <div style={{ background: "#FFFFFF", border: "1px solid var(--stone-border)", borderRadius: "16px", padding: "14px", marginBottom: "22px" }}>
            <div style={{ fontSize: "11px", fontWeight: 800, color: "var(--granite-600)", textTransform: "uppercase", marginBottom: "10px" }}>
              Inferred Multimodal Affinities
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", justifyContent: "center" }}>
              {(swipeState.inferred_interests || []).map((cat) => (
                <span
                  key={cat}
                  style={{
                    background: "var(--safety-orange-soft)",
                    color: "var(--safety-orange-hover)",
                    border: "1px solid #F7C6B3",
                    padding: "6px 14px",
                    borderRadius: "999px",
                    fontSize: "12px",
                    fontWeight: 800,
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "5px",
                  }}
                >
                  <Check size={13} strokeWidth={3} />
                  {cat}
                </span>
              ))}
            </div>
          </div>

          <button
            type="button"
            onClick={() => onComplete(swipeState.inferred_interests, swipeState.taste_embedding)}
            className="liquid-btn"
            style={{
              width: "100%",
              padding: "14px 20px",
              borderRadius: "16px",
              border: "none",
              background: "var(--safety-orange)",
              color: "#FFFFFF",
              fontSize: "15px",
              fontWeight: 800,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              boxShadow: "0 10px 24px rgba(232, 93, 42, 0.35)",
            }}
          >
            <span>Proceed to Trip Setup Wizard</span>
            <ChevronRight size={18} />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 99999,
        background: "linear-gradient(155deg, #1A1D1C 0%, #25463B 100%)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "20px 16px",
        userSelect: "none",
        touchAction: "none",
      }}
    >
      {/* Header & Active Confidence Meter */}
      <div style={{ width: "100%", maxWidth: "410px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Brain size={16} color="#FF9F7A" />
            <span className="font-display" style={{ fontSize: "16px", fontWeight: 800, color: "#FAF9F6" }}>
              Active Taste Match
            </span>
            <span className="font-mono-num" style={{ background: "rgba(232,93,42,0.25)", color: "#FFAD8F", padding: "3px 8px", borderRadius: "999px", fontSize: "10px", fontWeight: 700 }}>
              Confidence {swipeState.confidence_pct}%
            </span>
          </div>

          <button
            type="button"
            onClick={onSkip}
            style={{ background: "transparent", border: "none", color: "#B8C0BC", fontSize: "12px", fontWeight: 700, cursor: "pointer" }}
          >
            Skip
          </button>
        </div>

        <div style={{ width: "100%", height: "6px", background: "rgba(255,255,255,0.14)", borderRadius: "999px", overflow: "hidden" }}>
          <div
            style={{
              width: `${Math.min(100, ((swipeState.step + 1) / totalCards) * 100)}%`,
              height: "100%",
              background: "linear-gradient(90deg, #E85D2A 0%, #C9933B 100%)",
              borderRadius: "999px",
              transition: "width 0.3s ease",
            }}
          />
        </div>
        <div style={{ fontSize: "11px", color: "#B8C0BC", marginTop: "6px", textAlign: "center", fontWeight: 600 }}>
          Swipe {swipeState.step + 1} of {totalCards} • EIG Info Gain: <span className="font-mono-num">{swipeState.information_gain}</span>
        </div>
      </div>

      {/* Draggable Card */}
      <div style={{ position: "relative", width: "100%", maxWidth: "380px", height: "450px", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onPointerCancel={handlePointerUp}
          style={{
            position: "absolute",
            width: "100%",
            height: "100%",
            borderRadius: "24px",
            overflow: "hidden",
            boxShadow: "0 24px 48px rgba(0,0,0,0.55)",
            border: "1px solid rgba(255,255,255,0.16)",
            cursor: isDragging ? "grabbing" : "grab",
            transform: `translate(${dragOffset.x}px, ${dragOffset.y}px) rotate(${dragOffset.x * 0.08}deg)`,
            transition: isDragging ? "none" : "transform 0.28s cubic-bezier(0.16, 1, 0.3, 1)",
            background: "#1A1D1C",
          }}
        >
          <img
            src={currentCard.image}
            alt={currentCard.title}
            style={{ width: "100%", height: "100%", objectFit: "cover", pointerEvents: "none" }}
          />
          <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to top, rgba(26,29,28,0.95) 0%, rgba(26,29,28,0.25) 55%, transparent 100%)", pointerEvents: "none" }} />

          {stampFeedback === "like" && (
            <div style={{ position: "absolute", top: "28px", right: "22px", border: "4px solid #386655", borderRadius: "12px", padding: "6px 14px", color: "#A7F3D0", fontSize: "22px", fontWeight: 900, transform: "rotate(14deg)", background: "rgba(26,29,28,0.75)" }}>
              MATCH ❤️
            </div>
          )}
          {stampFeedback === "pass" && (
            <div style={{ position: "absolute", top: "28px", left: "22px", border: "4px solid #E85D2A", borderRadius: "12px", padding: "6px 14px", color: "#FF9F7A", fontSize: "22px", fontWeight: 900, transform: "rotate(-14deg)", background: "rgba(26,29,28,0.75)" }}>
              PASS ✕
            </div>
          )}
          {stampFeedback === "super" && (
            <div style={{ position: "absolute", top: "28px", left: "50%", transform: "translateX(-50%)", border: "4px solid #C9933B", borderRadius: "12px", padding: "6px 16px", color: "#FDE68A", fontSize: "20px", fontWeight: 900, background: "rgba(26,29,28,0.78)" }}>
              MUST GO ★
            </div>
          )}

          <div style={{ position: "absolute", bottom: "18px", left: "18px", right: "18px", color: "#FAF9F6" }}>
            <div style={{ display: "flex", gap: "6px", marginBottom: "8px" }}>
              <span style={{ background: "var(--safety-orange)", padding: "3px 10px", borderRadius: "999px", fontSize: "11px", fontWeight: 800 }}>
                {currentCard.badge}
              </span>
              <span style={{ background: "rgba(255,255,255,0.16)", backdropFilter: "blur(6px)", padding: "3px 10px", borderRadius: "999px", fontSize: "11px", fontWeight: 700 }}>
                {currentCard.tag}
              </span>
            </div>
            <h3 className="font-display" style={{ fontSize: "21px", fontWeight: 800, lineHeight: 1.2, margin: "0 0 6px 0" }}>
              {currentCard.title}
            </h3>
            <p style={{ fontSize: "12px", color: "#D6D1C7", lineHeight: 1.45, margin: 0 }}>
              {currentCard.description}
            </p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "24px" }}>
        <button
          type="button"
          onClick={() => handleVote("pass")}
          style={{ width: "56px", height: "56px", borderRadius: "50%", border: "2px solid #E85D2A", background: "rgba(232,93,42,0.14)", color: "#FF9F7A", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer" }}
          title="Pass"
        >
          <X size={26} strokeWidth={2.8} />
        </button>
        <button
          type="button"
          onClick={() => handleVote("super")}
          style={{ width: "48px", height: "48px", borderRadius: "50%", border: "2px solid #C9933B", background: "rgba(201,147,59,0.16)", color: "#FDE68A", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer" }}
          title="Must Go"
        >
          <Star size={22} fill="#C9933B" />
        </button>
        <button
          type="button"
          onClick={() => handleVote("like")}
          style={{ width: "56px", height: "56px", borderRadius: "50%", border: "2px solid #386655", background: "rgba(56,102,85,0.22)", color: "#A7F3D0", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer" }}
          title="Match"
        >
          <Heart size={26} fill="#386655" />
        </button>
      </div>
    </div>
  );
}
