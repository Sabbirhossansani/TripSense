import React, { useState, useEffect } from "react";
import { Compass, Sparkles, ArrowRight, Smartphone, CheckCircle2, Globe2, X } from "lucide-react";

const SCENIC_SLIDES = [
  {
    city: "Cox's Bazar, Bangladesh",
    subtitle: "World's longest natural sea beach & coral sunsets",
    image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
  },
  {
    city: "Sajek & Bandarban, Bangladesh",
    subtitle: "Emerald mountain ridges floating in monsoon clouds",
    image: "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1200&q=80",
  },
  {
    city: "Ratargul, Sylhet",
    subtitle: "Zero-emission wooden boat rides beneath swamp canopies",
    image: "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1200&q=80",
  },
];

const QUOTES = [
  "Travel together without compromise — FairNet neural consensus.",
  "Collect moments, protect ecosystems, support local hosts.",
  "Zero-hallucination itinerary repair when the weather shifts.",
];

export default function LoginScreen({ onLogin, onClose }) {
  const [slideIdx, setSlideIdx] = useState(0);
  const [quoteIdx, setQuoteIdx] = useState(0);
  const [showPhoneInput, setShowPhoneInput] = useState(false);
  const [phoneNum, setPhoneNum] = useState("+880 17");
  const [otpSent, setOtpSent] = useState(false);
  const [otpCode, setOtpCode] = useState("");
  const [stampAnim, setStampAnim] = useState(false);

  useEffect(() => {
    const t = setInterval(() => {
      setSlideIdx((p) => (p + 1) % SCENIC_SLIDES.length);
      setQuoteIdx((p) => (p + 1) % QUOTES.length);
    }, 5000);
    return () => clearInterval(t);
  }, []);

  const triggerStampLogin = (userObj) => {
    setStampAnim(true);
    setTimeout(() => {
      onLogin(userObj);
    }, 550);
  };

  const handleSocialAuth = (provider) => {
    const profileMap = {
      Google: { name: "Sadia", email: "sadia@tripsense.io", provider: "Google", budget_tier: "Mid-range" },
      Apple: { name: "Fahim", email: "fahim@tripsense.io", provider: "Apple", budget_tier: "Luxury" },
      Guest: { name: "Rahat", email: "guest@tripsense.io", provider: "Guest", budget_tier: "Budget" },
    };
    triggerStampLogin(profileMap[provider] || profileMap.Guest);
  };

  const handleSendOtp = (e) => {
    e.preventDefault();
    if (phoneNum.length < 6) return;
    setOtpSent(true);
  };

  const handleVerifyOtp = (e) => {
    e.preventDefault();
    triggerStampLogin({
      name: "Rahat",
      email: `${phoneNum}@mobile.bd`,
      provider: "Phone OTP",
      budget_tier: "Budget",
    });
  };

  const currentSlide = SCENIC_SLIDES[slideIdx];

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 99999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#1A1D1C",
        overflow: "hidden",
      }}
    >
      {SCENIC_SLIDES.map((s, idx) => (
        <div
          key={idx}
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage: `url(${s.image})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
            opacity: slideIdx === idx ? 0.42 : 0,
            transition: "opacity 1.2s ease-in-out",
            transform: slideIdx === idx ? "scale(1.04)" : "scale(1.0)",
          }}
        />
      ))}

      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "linear-gradient(180deg, rgba(26,29,28,0.68) 0%, rgba(26,29,28,0.92) 100%)",
        }}
      />

      <div
        className="glass-dark"
        style={{
          position: "relative",
          zIndex: 10,
          width: "100%",
          maxWidth: "430px",
          margin: "16px",
          borderRadius: "28px",
          padding: "30px 26px",
          color: "#F6F4EF",
        }}
      >
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            style={{
              position: "absolute",
              top: "16px",
              right: "16px",
              background: "rgba(255,255,255,0.12)",
              border: "none",
              borderRadius: "50%",
              width: "32px",
              height: "32px",
              color: "#FAF9F6",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <X size={16} />
          </button>
        )}

        <div style={{ textAlign: "center", marginBottom: "22px" }}>
          <div
            style={{
              width: "62px",
              height: "62px",
              borderRadius: "18px",
              background: "var(--safety-orange)",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 12px 26px rgba(232, 93, 42, 0.4)",
              marginBottom: "14px",
              transform: stampAnim ? "scale(1.2) rotate(-8deg)" : "scale(1) rotate(0deg)",
              transition: "all 0.35s cubic-bezier(0.16, 1, 0.3, 1)",
            }}
          >
            <Compass size={32} color="#FFFFFF" />
          </div>

          <h1 className="font-display" style={{ fontSize: "30px", fontWeight: 900, margin: "0 0 6px 0", color: "#FAF9F6" }}>
            TripSense
          </h1>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              background: "rgba(255,255,255,0.1)",
              padding: "4px 12px",
              borderRadius: "999px",
              fontSize: "11px",
              fontWeight: 700,
              color: "#FFAD8F",
              marginBottom: "12px",
            }}
          >
            <Sparkles size={12} />
            <span>FAIRNET • NEURO-SYMBOLIC EXPEDITIONS</span>
          </div>

          <p style={{ fontSize: "13px", color: "#D6D1C7", margin: 0, lineHeight: 1.5, fontStyle: "italic" }}>
            "{QUOTES[quoteIdx]}"
          </p>
        </div>

        <div
          style={{
            background: "rgba(255,255,255,0.06)",
            borderRadius: "14px",
            padding: "10px 14px",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            marginBottom: "20px",
            border: "1px solid rgba(255,255,255,0.1)",
          }}
        >
          <Globe2 size={18} color="#9FE0C4" />
          <div>
            <div style={{ fontSize: "12px", fontWeight: 700, color: "#FAF9F6" }}>{currentSlide.city}</div>
            <div style={{ fontSize: "11px", color: "#B8C0BC" }}>{currentSlide.subtitle}</div>
          </div>
        </div>

        {!showPhoneInput ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            <button
              type="button"
              onClick={() => handleSocialAuth("Google")}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "10px",
                background: "#FAF9F6",
                color: "#1A1D1C",
                border: "none",
                borderRadius: "14px",
                padding: "13px 16px",
                fontSize: "14px",
                fontWeight: 800,
                cursor: "pointer",
              }}
            >
              <span>Continue with Google</span>
            </button>

            <button
              type="button"
              onClick={() => handleSocialAuth("Apple")}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "10px",
                background: "#2A2F2D",
                color: "#FAF9F6",
                border: "1px solid rgba(255,255,255,0.18)",
                borderRadius: "14px",
                padding: "13px 16px",
                fontSize: "14px",
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              <span>Continue with Apple</span>
            </button>

            <button
              type="button"
              onClick={() => setShowPhoneInput(true)}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                background: "rgba(255,255,255,0.08)",
                color: "#FAF9F6",
                border: "1px solid rgba(255,255,255,0.18)",
                borderRadius: "14px",
                padding: "12px 16px",
                fontSize: "13px",
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              <Smartphone size={16} />
              <span>Sign in with Phone (SMS OTP)</span>
            </button>

            <div style={{ textAlign: "center", margin: "4px 0", fontSize: "11px", color: "#9AA39F" }}>
              — or explore instantly —
            </div>

            <button
              type="button"
              onClick={() => handleSocialAuth("Guest")}
              className="liquid-btn"
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                background: "var(--safety-orange)",
                color: "#FFFFFF",
                border: "none",
                borderRadius: "14px",
                padding: "13px 16px",
                fontSize: "14px",
                fontWeight: 800,
                cursor: "pointer",
                boxShadow: "0 10px 24px rgba(232, 93, 42, 0.35)",
              }}
            >
              <span>Explore as Guest (1-Tap)</span>
              <ArrowRight size={16} />
            </button>
          </div>
        ) : (
          <form onSubmit={otpSent ? handleVerifyOtp : handleSendOtp}>
            {!otpSent ? (
              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: 700, marginBottom: "6px" }}>
                  Mobile Number (Bangladesh / International)
                </label>
                <input
                  type="text"
                  value={phoneNum}
                  onChange={(e) => setPhoneNum(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "12px 14px",
                    borderRadius: "12px",
                    border: "1px solid rgba(255,255,255,0.22)",
                    background: "rgba(0,0,0,0.35)",
                    color: "#FFFFFF",
                    fontSize: "14px",
                    marginBottom: "12px",
                  }}
                />
                <div style={{ display: "flex", gap: "8px" }}>
                  <button
                    type="button"
                    onClick={() => setShowPhoneInput(false)}
                    style={{ flex: 1, padding: "12px", borderRadius: "12px", background: "rgba(255,255,255,0.1)", color: "#fff", border: "none", cursor: "pointer", fontWeight: 700 }}
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    style={{ flex: 2, padding: "12px", borderRadius: "12px", background: "var(--safety-orange)", color: "#fff", border: "none", cursor: "pointer", fontWeight: 800 }}
                  >
                    Send Verification Code
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: 700, marginBottom: "6px" }}>
                  Enter 4-Digit Demo OTP (e.g. 1234)
                </label>
                <input
                  type="text"
                  maxLength={4}
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value)}
                  placeholder="1234"
                  style={{
                    width: "100%",
                    padding: "12px 14px",
                    borderRadius: "12px",
                    border: "1px solid var(--alpine-moss-mid)",
                    background: "rgba(0,0,0,0.4)",
                    color: "#FFFFFF",
                    fontSize: "18px",
                    letterSpacing: "6px",
                    textAlign: "center",
                    fontWeight: 800,
                    marginBottom: "12px",
                  }}
                />
                <button
                  type="submit"
                  style={{ width: "100%", padding: "12px", borderRadius: "12px", background: "var(--alpine-moss)", color: "#fff", border: "none", cursor: "pointer", fontWeight: 800 }}
                >
                  Verify & Stamp Passport
                </button>
              </div>
            )}
          </form>
        )}

        {stampAnim && (
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -50%) rotate(-12deg)",
              border: "4px solid #9FE0C4",
              borderRadius: "16px",
              padding: "10px 22px",
              background: "rgba(37, 70, 59, 0.92)",
              color: "#FFFFFF",
              fontSize: "20px",
              fontWeight: 900,
              letterSpacing: "2px",
              zIndex: 50,
              boxShadow: "0 10px 30px rgba(0,0,0,0.45)",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <CheckCircle2 size={24} />
            <span>STAMPED!</span>
          </div>
        )}
      </div>
    </div>
  );
}
