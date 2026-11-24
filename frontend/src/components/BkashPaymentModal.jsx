import React, { useState } from "react";
import { X, CheckCircle2, ShieldCheck } from "lucide-react";

export default function BkashPaymentModal({ settlement, onClose, onConfirmSettlement }) {
  const [provider, setProvider] = useState("bKash"); // "bKash" | "Nagad"
  const [pin, setPin] = useState("7078");
  const [isProcessing, setIsProcessing] = useState(false);
  const [isComplete, setIsComplete] = useState(false);

  if (!settlement) return null;

  const brandColor = provider === "bKash" ? "#e2136e" : "#f7941d";

  const handlePay = (e) => {
    e.preventDefault();
    setIsProcessing(true);

    setTimeout(() => {
      setIsProcessing(false);
      setIsComplete(true);
      setTimeout(() => {
        onConfirmSettlement(settlement);
        onClose();
      }, 1200);
    }, 1000);
  };

  return (
    <div style={{
      position: "fixed",
      inset: 0,
      zIndex: 100000,
      background: "rgba(15, 23, 42, 0.75)",
      backdropFilter: "blur(6px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "16px",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    }}>
      <div style={{
        background: "#ffffff",
        borderRadius: "28px",
        padding: "26px",
        maxWidth: "400px",
        width: "100%",
        boxShadow: "0 25px 60px rgba(0,0,0,0.35)",
        animation: "slideUp 0.3s ease"
      }}>
        {/* Header with Provider Toggle */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
          <div style={{ display: "flex", gap: "8px" }}>
            <button
              onClick={() => setProvider("bKash")}
              style={{
                background: provider === "bKash" ? "#e2136e" : "#f1f5f9",
                color: provider === "bKash" ? "#ffffff" : "#475569",
                border: "none",
                borderRadius: "10px",
                padding: "6px 14px",
                fontSize: "12px",
                fontWeight: 800,
                cursor: "pointer"
              }}
            >
              bKash
            </button>

            <button
              onClick={() => setProvider("Nagad")}
              style={{
                background: provider === "Nagad" ? "#f7941d" : "#f1f5f9",
                color: provider === "Nagad" ? "#ffffff" : "#475569",
                border: "none",
                borderRadius: "10px",
                padding: "6px 14px",
                fontSize: "12px",
                fontWeight: 800,
                cursor: "pointer"
              }}
            >
              Nagad
            </button>
          </div>

          <button
            onClick={onClose}
            style={{
              background: "#f1f5f9",
              border: "none",
              borderRadius: "50%",
              width: "30px",
              height: "30px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}
          >
            <X size={16} />
          </button>
        </div>

        {isComplete ? (
          <div style={{ textAlign: "center", padding: "20px 0" }}>
            <div style={{
              width: "64px",
              height: "64px",
              borderRadius: "50%",
              background: "#ecfdf5",
              color: "#059669",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: "12px"
            }}>
              <CheckCircle2 size={36} />
            </div>
            <h3 style={{ fontSize: "18px", fontWeight: 900, color: "#065f46", margin: "0 0 6px 0" }}>
              Settlement Completed!
            </h3>
            <p style={{ fontSize: "13px", color: "#047857", margin: 0 }}>
              ৳{settlement.amount} paid to {settlement.to}. Debt marked as cleared.
            </p>
          </div>
        ) : (
          <form onSubmit={handlePay}>
            {/* Amount & Recipient Card */}
            <div style={{
              background: provider === "bKash" ? "linear-gradient(135deg, #fdf2f8 0%, #fce7f3 100%)" : "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)",
              border: `1.5px solid ${brandColor}`,
              borderRadius: "18px",
              padding: "16px",
              textAlign: "center",
              marginBottom: "18px"
            }}>
              <div style={{ fontSize: "11px", fontWeight: 700, color: "#59615E", textTransform: "uppercase" }}>
                TripSense Instant Settlement
              </div>
              <div style={{ fontSize: "32px", fontWeight: 900, color: brandColor, margin: "6px 0" }}>
                ৳ {settlement.amount}
              </div>
              <div style={{ fontSize: "12px", color: "#334155", fontWeight: 600 }}>
                <strong>{settlement.from}</strong> ➔ <strong>{settlement.to}</strong>
              </div>
            </div>

            {/* Mobile Wallet Number (Mocked) */}
            <div style={{ marginBottom: "12px", textAlign: "left" }}>
              <label style={{ fontSize: "11px", fontWeight: 700, color: "#475569" }}>
                {provider} Wallet Number:
              </label>
              <input
                type="text"
                readOnly
                value={`01712-***${settlement.to.length * 12}`}
                style={{
                  width: "100%",
                  padding: "10px",
                  borderRadius: "10px",
                  border: "1px solid #cbd5e1",
                  fontSize: "13px",
                  marginTop: "4px",
                  boxSizing: "border-box",
                  background: "#F6F4EF"
                }}
              />
            </div>

            {/* 4-digit PIN */}
            <div style={{ marginBottom: "20px", textAlign: "left" }}>
              <label style={{ fontSize: "11px", fontWeight: 700, color: "#475569" }}>
                Enter {provider} Demo PIN (e.g. 7078):
              </label>
              <input
                type="password"
                maxLength={5}
                value={pin}
                onChange={(e) => setPin(e.target.value)}
                style={{
                  width: "100%",
                  padding: "10px",
                  borderRadius: "10px",
                  border: "1px solid #cbd5e1",
                  fontSize: "16px",
                  textAlign: "center",
                  letterSpacing: "6px",
                  marginTop: "4px",
                  boxSizing: "border-box",
                  fontWeight: 800
                }}
                required
              />
            </div>

            {/* Settle Action */}
            <button
              type="submit"
              disabled={isProcessing}
              style={{
                width: "100%",
                padding: "13px",
                borderRadius: "14px",
                border: "none",
                background: brandColor,
                color: "#ffffff",
                fontSize: "14px",
                fontWeight: 800,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                boxShadow: `0 6px 18px ${brandColor}40`
              }}
            >
              <ShieldCheck size={18} />
              <span>{isProcessing ? "Processing Settlement..." : `Pay ৳${settlement.amount} via ${provider}`}</span>
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
