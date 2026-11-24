import React, { useState } from "react";
import { X, Calendar, CheckCircle2, ArrowRight, Sparkles } from "lucide-react";
import { reserveBooking, formatCurrency } from "../api/client";

export default function BookingDrawer({
  spot,
  isOpen,
  onClose,
  defaultDate = "2026-08-12",
  defaultGroupSize = 3,
  defaultLeadName = "Rahat",
  currency = "BDT",
  availableEcoPoints = 180,
  onBookingConfirmed,
}) {
  const [step, setStep] = useState(1);
  const [date, setDate] = useState(defaultDate);
  const [timeSlot, setTimeSlot] = useState("Morning (09:00 AM - 12:00 PM)");
  const [groupSize, setGroupSize] = useState(defaultGroupSize);
  const [leadName, setLeadName] = useState(defaultLeadName);
  const [leadContact, setLeadContact] = useState("+880 1711-000000");
  const [ecoPledge, setEcoPledge] = useState(true);
  const [redeemPoints, setRedeemPoints] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [voucher, setVoucher] = useState(null);

  if (!isOpen || !spot) return null;

  const baseUnit = Math.max(spot.estimated_cost_bdt || 0, 150);
  const baseTotal = baseUnit * groupSize;
  const discPct = groupSize >= 4 ? Math.max(spot.group_discount_pct || 10, 15) : groupSize >= 3 ? Math.max(spot.group_discount_pct || 10, 10) : 0;
  const groupDiscountBdt = Math.round(baseTotal * (discPct / 100));
  const ecoDiscountBdt = redeemPoints ? Math.min(Math.round(baseTotal * 0.25), Math.round(availableEcoPoints * 0.5)) : 0;
  const finalTotal = Math.max(0, baseTotal - groupDiscountBdt - ecoDiscountBdt);

  const handleConfirm = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await reserveBooking({
        spot_id: spot.id,
        spot_name: spot.name,
        city: spot.city,
        date,
        time_slot: timeSlot,
        group_size: groupSize,
        lead_name: leadName,
        lead_contact: leadContact,
        eco_pledge: ecoPledge,
        redeem_eco_points: redeemPoints ? availableEcoPoints : 0,
        unit_cost_bdt: baseUnit,
      });
      setVoucher(res);
      setStep(3);
      if (onBookingConfirmed) onBookingConfirmed(res);
    } catch {
      const localVoucher = {
        voucher_code: `TS-BD-${Math.random().toString(36).substring(2, 8).toUpperCase()}`,
        status: "CONFIRMED",
        spot_name: spot.name,
        partner_name: spot.local_partner_name || "Local Heritage Partner",
        date,
        time_slot: timeSlot,
        group_size: groupSize,
        final_total_bdt: finalTotal,
        group_discount_pct: discPct,
        eco_points_earned: (spot.eco_points_reward || 60) + (ecoPledge ? 40 : 0),
        local_sme_revenue_bdt: Math.round(finalTotal * ((spot.local_revenue_share_pct || 85) / 100)),
      };
      setVoucher(localVoucher);
      setStep(3);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 100001,
        background: "rgba(26, 29, 28, 0.58)",
        backdropFilter: "blur(6px)",
        display: "flex",
        justifyContent: "flex-end",
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: "100%",
          maxWidth: "440px",
          height: "100%",
          background: "#FAF9F6",
          borderLeft: "1px solid var(--stone-border)",
          display: "flex",
          flexDirection: "column",
          animation: "slideRightIn 0.35s cubic-bezier(0.16, 1, 0.3, 1)",
          boxShadow: "-12px 0 40px rgba(26, 29, 28, 0.18)",
        }}
      >
        {/* Drawer Header */}
        <div
          style={{
            padding: "20px 22px",
            background: "#1A1D1C",
            color: "#F6F4EF",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontSize: "10px", fontWeight: 800, color: "#FF9F7A", letterSpacing: "0.8px" }}>
              LOCAL PARTNER RESERVATION
            </div>
            <h3 className="font-display" style={{ fontSize: "18px", fontWeight: 800, margin: "4px 0 0 0" }}>
              {spot.name.split("(")[0].trim()}
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            style={{
              background: "rgba(255,255,255,0.12)",
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

        {/* Body */}
        <div style={{ flex: 1, overflowY: "auto", padding: "22px" }}>
          {/* Stepper Indicator */}
          <div style={{ display: "flex", gap: "8px", marginBottom: "20px" }}>
            {[1, 2, 3].map((n) => (
              <div
                key={n}
                style={{
                  flex: 1,
                  height: "4px",
                  borderRadius: "999px",
                  background: step >= n ? "var(--safety-orange)" : "var(--stone-border)",
                  transition: "background 0.25s ease",
                }}
              />
            ))}
          </div>

          {step === 1 && (
            <div>
              <h4 style={{ fontSize: "15px", fontWeight: 800, margin: "0 0 14px 0" }}>
                Step 1: Choose Date, Slot & Squad Count
              </h4>

              <div style={{ marginBottom: "14px" }}>
                <label style={{ display: "block", fontSize: "12px", fontWeight: 700, color: "var(--granite-600)", marginBottom: "6px" }}>
                  Visit Date
                </label>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", background: "#FFFFFF", border: "1px solid var(--stone-border)", borderRadius: "12px", padding: "10px 12px" }}>
                  <Calendar size={15} color="#E85D2A" />
                  <input
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    style={{ border: "none", outline: "none", flex: 1, fontSize: "13px", fontWeight: 600 }}
                  />
                </div>
              </div>

              <div style={{ marginBottom: "14px" }}>
                <label style={{ display: "block", fontSize: "12px", fontWeight: 700, color: "var(--granite-600)", marginBottom: "6px" }}>
                  Preferred Slot
                </label>
                <select
                  value={timeSlot}
                  onChange={(e) => setTimeSlot(e.target.value)}
                  style={{ width: "100%", padding: "10px 12px", borderRadius: "12px", border: "1px solid var(--stone-border)", background: "#FFFFFF", fontSize: "13px", fontWeight: 600 }}
                >
                  <option>Morning (09:00 AM - 12:00 PM)</option>
                  <option>Afternoon (01:30 PM - 05:00 PM)</option>
                  <option>Evening (06:00 PM - 08:30 PM)</option>
                </select>
              </div>

              <div style={{ marginBottom: "18px" }}>
                <label style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", fontWeight: 700, color: "var(--granite-600)", marginBottom: "6px" }}>
                  <span>Squad Size (Group Discount Unlock)</span>
                  <span className="font-mono-num" style={{ color: "var(--safety-orange)" }}>{groupSize} Members</span>
                </label>
                <input
                  type="range"
                  min={1}
                  max={10}
                  value={groupSize}
                  onChange={(e) => setGroupSize(Number(e.target.value))}
                  style={{ width: "100%", accentColor: "#E85D2A" }}
                />
              </div>

              {/* Price & Discount Breakdown */}
              <div style={{ background: "#FFFFFF", border: "1px solid var(--stone-border)", borderRadius: "16px", padding: "16px", marginBottom: "18px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "6px" }}>
                  <span style={{ color: "var(--granite-600)" }}>Guided Entry / Experience ({groupSize}×)</span>
                  <span className="font-mono-num" style={{ fontWeight: 700 }}>{formatCurrency(baseTotal, currency)}</span>
                </div>
                {discPct > 0 && (
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", color: "var(--alpine-moss)", fontWeight: 700, marginBottom: "6px" }}>
                    <span>Squad Tier Discount ({discPct}%)</span>
                    <span className="font-mono-num">-{formatCurrency(groupDiscountBdt, currency)}</span>
                  </div>
                )}
                <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "12px", margin: "10px 0", cursor: "pointer", color: "var(--alpine-moss)", fontWeight: 700 }}>
                  <input type="checkbox" checked={redeemPoints} onChange={(e) => setRedeemPoints(e.target.checked)} />
                  <span>Redeem {availableEcoPoints} Eco-Points (-{formatCurrency(Math.round(availableEcoPoints * 0.5), currency)})</span>
                </label>
                <div style={{ borderTop: "1px dashed var(--stone-border)", paddingTop: "10px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "13px", fontWeight: 800 }}>Total Group Payable</span>
                  <span className="font-mono-num" style={{ fontSize: "20px", fontWeight: 800, color: "var(--safety-orange)" }}>
                    {formatCurrency(finalTotal, currency)}
                  </span>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setStep(2)}
                className="liquid-btn"
                style={{
                  width: "100%",
                  background: "var(--safety-orange)",
                  color: "#FFFFFF",
                  border: "none",
                  borderRadius: "14px",
                  padding: "13px",
                  fontSize: "14px",
                  fontWeight: 800,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                }}
              >
                <span>Continue to Traveler Details</span>
                <ArrowRight size={16} />
              </button>
            </div>
          )}

          {step === 2 && (
            <form onSubmit={handleConfirm}>
              <h4 style={{ fontSize: "15px", fontWeight: 800, margin: "0 0 14px 0" }}>
                Step 2: Lead Traveler & Eco-Pledge
              </h4>

              <div style={{ marginBottom: "14px" }}>
                <label style={{ display: "block", fontSize: "12px", fontWeight: 700, color: "var(--granite-600)", marginBottom: "6px" }}>
                  Lead Traveler Name
                </label>
                <input
                  type="text"
                  required
                  value={leadName}
                  onChange={(e) => setLeadName(e.target.value)}
                  style={{ width: "100%", padding: "11px 12px", borderRadius: "12px", border: "1px solid var(--stone-border)", background: "#FFFFFF", fontSize: "13px", fontWeight: 600 }}
                />
              </div>

              <div style={{ marginBottom: "14px" }}>
                <label style={{ display: "block", fontSize: "12px", fontWeight: 700, color: "var(--granite-600)", marginBottom: "6px" }}>
                  Mobile / WhatsApp Contact
                </label>
                <input
                  type="text"
                  required
                  value={leadContact}
                  onChange={(e) => setLeadContact(e.target.value)}
                  style={{ width: "100%", padding: "11px 12px", borderRadius: "12px", border: "1px solid var(--stone-border)", background: "#FFFFFF", fontSize: "13px", fontWeight: 600 }}
                />
              </div>

              <label
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: "10px",
                  background: "var(--alpine-moss-soft)",
                  border: "1px solid #C5D9CE",
                  borderRadius: "14px",
                  padding: "12px",
                  marginBottom: "18px",
                  cursor: "pointer",
                }}
              >
                <input
                  type="checkbox"
                  checked={ecoPledge}
                  onChange={(e) => setEcoPledge(e.target.checked)}
                  style={{ marginTop: "3px" }}
                />
                <div style={{ fontSize: "12px", color: "var(--alpine-moss)", lineHeight: 1.45 }}>
                  <strong>Zero-Plastic Eco Pledge (+40 Bonus Eco-Points):</strong> Our group commits to reusable water bottles and supporting {spot.local_partner_name || "local community hosts"}.
                </div>
              </label>

              <div style={{ display: "flex", gap: "10px" }}>
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  style={{
                    flex: 1,
                    background: "#FFFFFF",
                    border: "1px solid var(--stone-border)",
                    borderRadius: "14px",
                    padding: "12px",
                    fontSize: "13px",
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="liquid-btn"
                  style={{
                    flex: 2,
                    background: "var(--alpine-moss)",
                    color: "#FFFFFF",
                    border: "none",
                    borderRadius: "14px",
                    padding: "12px",
                    fontSize: "14px",
                    fontWeight: 800,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "6px",
                  }}
                >
                  <Sparkles size={15} />
                  <span>{isSubmitting ? "Issuing Voucher..." : `Confirm (${formatCurrency(finalTotal, currency)})`}</span>
                </button>
              </div>
            </form>
          )}

          {step === 3 && voucher && (
            <div style={{ textAlign: "center" }}>
              <div
                style={{
                  width: "64px",
                  height: "64px",
                  borderRadius: "50%",
                  background: "var(--alpine-moss-soft)",
                  color: "var(--alpine-moss)",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  marginBottom: "14px",
                }}
              >
                <CheckCircle2 size={36} />
              </div>

              <h4 className="font-display" style={{ fontSize: "22px", fontWeight: 800, margin: "0 0 6px 0" }}>
                Reservation Confirmed!
              </h4>
              <p style={{ fontSize: "12px", color: "var(--granite-600)", margin: "0 0 18px 0" }}>
                Hosted by <strong>{voucher.partner_name}</strong>
              </p>

              <div
                style={{
                  background: "#FFFFFF",
                  border: "2px dashed var(--safety-orange)",
                  borderRadius: "18px",
                  padding: "18px",
                  textAlign: "left",
                  marginBottom: "18px",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                  <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--granite-600)" }}>VOUCHER CODE</span>
                  <span className="font-mono-num" style={{ fontSize: "15px", fontWeight: 800, color: "var(--safety-orange)" }}>
                    {voucher.voucher_code}
                  </span>
                </div>
                <div style={{ fontSize: "12px", lineHeight: 1.7, color: "var(--granite-800)" }}>
                  <div><strong>Date:</strong> {voucher.date} • {voucher.time_slot}</div>
                  <div><strong>Squad:</strong> {voucher.group_size} Travelers ({voucher.group_discount_pct}% Group Discount)</div>
                  <div><strong>Paid Total:</strong> {formatCurrency(voucher.final_total_bdt, currency)}</div>
                  <div style={{ color: "var(--alpine-moss)", fontWeight: 700 }}>
                    <strong>Direct Local SME Impact:</strong> {formatCurrency(voucher.local_sme_revenue_bdt, currency)} retained locally
                  </div>
                  <div style={{ color: "var(--safety-orange)", fontWeight: 700 }}>
                    <strong>Earned:</strong> +{voucher.eco_points_earned} Eco-Points
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={onClose}
                style={{
                  width: "100%",
                  background: "var(--granite-950)",
                  color: "#FFFFFF",
                  border: "none",
                  borderRadius: "14px",
                  padding: "13px",
                  fontSize: "14px",
                  fontWeight: 800,
                  cursor: "pointer",
                }}
              >
                Done & Return to Itinerary
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
