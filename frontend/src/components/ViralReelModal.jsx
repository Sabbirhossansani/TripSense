import React, { useState, useEffect } from "react";
import { X, Play, Pause, Share2, Copy, Check, Sparkles } from "lucide-react";
import { SPOT_IMAGES } from "../assets/images";

export default function ViralReelModal({ plan, city = "Chittagong", members = [], onClose }) {
  const [activeSlide, setActiveSlide] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [copied, setCopied] = useState(false);

  const dailySchedule = plan?.daily_schedule || [];
  const allSpots = dailySchedule.flatMap((d) => d.spots || []);
  const fairness = plan?.fairness_report || { fairness_score: 75 };

  const slides = [
    {
      type: "intro",
      title: `${city.toUpperCase()} UNLOCKED ✈️`,
      subtitle: `${dailySchedule.length || 3} Days • Conflict-Free Group Adventure`,
      bg: SPOT_IMAGES[101] || "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1080&q=80",
      highlight: "Harmonized with Least-Misery AI"
    },
    {
      type: "spots",
      title: "EPIC HIGHLIGHTS 📸",
      subtitle: `${allSpots.length} Handpicked POIs with zero congestion`,
      bg: SPOT_IMAGES[104] || "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1080&q=80",
      highlight: allSpots.slice(0, 3).map((s) => s.name.split(" ")[0]).join(" • ")
    },
    {
      type: "stats",
      title: "SQUAD STATS 🔥",
      subtitle: `${members.map((m) => m.name).join(", ")} crushed this trip!`,
      bg: SPOT_IMAGES[102] || "https://images.unsplash.com/photo-1548625361-195fe578772a?auto=format&fit=crop&w=1080&q=80",
      stats: [
        { label: "Total Distance", val: `${plan?.total_distance_km || 14.2} km` },
        { label: "Fairness Score", val: `${fairness.fairness_score}/100` },
        { label: "Group Arguments", val: "0 (Zero!)" }
      ]
    },
    {
      type: "outro",
      title: "PASSPORT STAMPED 🏆",
      subtitle: "Verified TripSense FYDP Traveler",
      bg: "https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?auto=format&fit=crop&w=1080&q=80",
      highlight: "Ready for the next journey?"
    }
  ];

  // Auto advance slides every 3.5 seconds if playing
  useEffect(() => {
    if (!isPlaying) return;
    const interval = setInterval(() => {
      setActiveSlide((prev) => (prev + 1) % slides.length);
    }, 3500);
    return () => clearInterval(interval);
  }, [isPlaying, slides.length]);

  const currentSlide = slides[activeSlide];

  const handleCopyLink = () => {
    navigator.clipboard?.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleShareWhatsApp = () => {
    const text = encodeURIComponent(`Watch our 15-Sec TripSense Reel for our trip to ${city}! 🔥 Verified conflict-free with Least-Misery AI.`);
    window.open(`https://api.whatsapp.com/send?text=${text}`, "_blank");
  };

  return (
    <div style={{
      position: "fixed",
      inset: 0,
      zIndex: 100000,
      background: "rgba(15, 23, 42, 0.85)",
      backdropFilter: "blur(12px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "16px",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    }}>
      {/* 9:16 Vertical Reel Player Container */}
      <div style={{
        position: "relative",
        width: "100%",
        maxWidth: "380px",
        height: "640px",
        borderRadius: "28px",
        overflow: "hidden",
        boxShadow: "0 25px 60px rgba(0, 0, 0, 0.8), 0 0 0 1.5px rgba(255, 255, 255, 0.2)",
        background: "#1A1D1C"
      }}>
        {/* Background Image of Current Slide */}
        <div style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `url(${currentSlide.bg})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          transition: "background-image 0.5s ease-in-out",
          transform: "scale(1.04)"
        }} />

        {/* Gradient Overlay */}
        <div style={{
          position: "absolute",
          inset: 0,
          background: "linear-gradient(to bottom, rgba(15, 23, 42, 0.55) 0%, rgba(15, 23, 42, 0.2) 40%, rgba(15, 23, 42, 0.85) 100%)"
        }} />

        {/* Top Progress Bars (Instagram Stories style) */}
        <div style={{
          position: "absolute",
          top: "14px",
          left: "14px",
          right: "14px",
          display: "flex",
          gap: "4px",
          zIndex: 20
        }}>
          {slides.map((_, idx) => (
            <div
              key={idx}
              onClick={() => setActiveSlide(idx)}
              style={{
                flex: 1,
                height: "3.5px",
                borderRadius: "999px",
                background: idx < activeSlide ? "#ffffff" : idx === activeSlide ? "#ffffff" : "rgba(255, 255, 255, 0.35)",
                cursor: "pointer",
                transition: "all 0.2s ease"
              }}
            />
          ))}
        </div>

        {/* Top Controls Strip: Brand + Music Equalizer + Close */}
        <div style={{
          position: "absolute",
          top: "26px",
          left: "14px",
          right: "14px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          zIndex: 20
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{
              background: "rgba(79, 70, 229, 0.85)",
              color: "#ffffff",
              padding: "3px 10px",
              borderRadius: "12px",
              fontSize: "11px",
              fontWeight: 800,
              display: "flex",
              alignItems: "center",
              gap: "4px"
            }}>
              <Sparkles size={12} />
              15-SEC REEL
            </span>

            {/* Audio Wave / Equalizer Animation */}
            <div style={{
              display: "flex",
              alignItems: "flex-end",
              gap: "2px",
              height: "14px"
            }}>
              <span style={{ width: "3px", height: "8px", background: "#10b981", borderRadius: "1px" }} />
              <span style={{ width: "3px", height: "14px", background: "#10b981", borderRadius: "1px" }} />
              <span style={{ width: "3px", height: "10px", background: "#10b981", borderRadius: "1px" }} />
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              style={{
                background: "rgba(0, 0, 0, 0.4)",
                border: "none",
                borderRadius: "50%",
                width: "32px",
                height: "32px",
                color: "#ffffff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer"
              }}
            >
              {isPlaying ? <Pause size={14} /> : <Play size={14} />}
            </button>

            <button
              onClick={onClose}
              style={{
                background: "rgba(0, 0, 0, 0.4)",
                border: "none",
                borderRadius: "50%",
                width: "32px",
                height: "32px",
                color: "#ffffff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer"
              }}
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Center Touch Navigation Zones */}
        <div style={{
          position: "absolute",
          inset: "60px 0 120px 0",
          display: "flex",
          zIndex: 10
        }}>
          <div
            onClick={() => setActiveSlide((prev) => Math.max(0, prev - 1))}
            style={{ flex: 1, cursor: "pointer" }}
            title="Previous slide"
          />
          <div
            onClick={() => setActiveSlide((prev) => (prev + 1) % slides.length)}
            style={{ flex: 1, cursor: "pointer" }}
            title="Next slide"
          />
        </div>

        {/* Center Animated Content Card */}
        <div style={{
          position: "absolute",
          bottom: "100px",
          left: "20px",
          right: "20px",
          zIndex: 20,
          color: "#ffffff",
          textAlign: "left"
        }}>
          <h2 style={{
            fontSize: "26px",
            fontWeight: 900,
            lineHeight: 1.15,
            margin: "0 0 8px 0",
            letterSpacing: "-0.5px",
            textShadow: "0 2px 8px rgba(0,0,0,0.6)"
          }}>
            {currentSlide.title}
          </h2>

          <p style={{
            fontSize: "14px",
            color: "#E2DDD3",
            lineHeight: 1.4,
            margin: "0 0 14px 0",
            textShadow: "0 1px 4px rgba(0,0,0,0.6)"
          }}>
            {currentSlide.subtitle}
          </p>

          {/* Special stats block for Slide 3 */}
          {currentSlide.stats && (
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
              gap: "8px",
              background: "rgba(0, 0, 0, 0.45)",
              backdropFilter: "blur(6px)",
              padding: "10px",
              borderRadius: "14px",
              marginBottom: "10px"
            }}>
              {currentSlide.stats.map((st) => (
                <div key={st.label} style={{ textAlign: "center" }}>
                  <div style={{ fontSize: "16px", fontWeight: 900, color: "#10b981" }}>{st.val}</div>
                  <div style={{ fontSize: "10px", color: "#94a3b8", fontWeight: 600 }}>{st.label}</div>
                </div>
              ))}
            </div>
          )}

          {currentSlide.highlight && (
            <div style={{
              display: "inline-block",
              background: "rgba(255, 255, 255, 0.2)",
              backdropFilter: "blur(6px)",
              padding: "6px 14px",
              borderRadius: "20px",
              fontSize: "12px",
              fontWeight: 800,
              color: "#ffffff"
            }}>
              ✨ {currentSlide.highlight}
            </div>
          )}
        </div>

        {/* Bottom Social Share Actions Bar */}
        <div style={{
          position: "absolute",
          bottom: "16px",
          left: "16px",
          right: "16px",
          display: "flex",
          gap: "8px",
          zIndex: 20
        }}>
          <button
            onClick={handleShareWhatsApp}
            style={{
              flex: 1,
              padding: "10px",
              borderRadius: "14px",
              border: "none",
              background: "#25d366",
              color: "#ffffff",
              fontSize: "12px",
              fontWeight: 800,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "6px",
              boxShadow: "0 4px 12px rgba(37, 211, 102, 0.4)"
            }}
          >
            <Share2 size={14} />
            <span>WhatsApp</span>
          </button>

          <button
            onClick={handleCopyLink}
            style={{
              flex: 1,
              padding: "10px",
              borderRadius: "14px",
              border: "none",
              background: "#ffffff",
              color: "#1A1D1C",
              fontSize: "12px",
              fontWeight: 800,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "6px",
              boxShadow: "0 4px 12px rgba(0,0,0,0.3)"
            }}
          >
            {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
            <span>{copied ? "Link Copied!" : "Copy Reel"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
