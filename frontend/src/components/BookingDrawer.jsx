import React, { useState } from "react";
import { Drawer } from "vaul";
import { toast } from "sonner";
import { X, CalendarCheck, Leaf, Users, CheckCircle2, Sparkles } from "lucide-react";
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
}) {
  const [step, setStep] = useState(1);
  const [date, setDate] = useState(defaultDate);
  const [timeSlot, setTimeSlot] = useState("Morning (09:00 AM - 12:00 PM)");
  const [groupSize, setGroupSize] = useState(defaultGroupSize);
  const [leadName, setLeadName] = useState(defaultLeadName);
  const [leadContact, setLeadContact] = useState("+880 1711-000000");
  const [ecoPledge, setEcoPledge] = useState(true);
  const [useEcoPoints, setUseEcoPoints] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [confirmation, setConfirmation] = useState(null);

  if (!spot) return null;

  const unitCost = Number(spot.estimated_cost_bdt || 150);
  const baseTotal = unitCost * groupSize;
  const groupDiscountPct = groupSize >= 4 ? 15 : 10;
  const groupDiscountBdt = Math.round((baseTotal * groupDiscountPct) / 100);
  const ecoDiscountBdt = useEcoPoints ? Math.min(Math.max(0, baseTotal - groupDiscountBdt), Math.floor(availableEcoPoints * 0.5)) : 0;
  const finalPayable = Math.max(0, baseTotal - groupDiscountBdt - ecoDiscountBdt);

  const handleClose = () => {
    setStep(1);
    setConfirmation(null);
    onClose();
  };

  const handleConfirm = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await reserveBooking({
        spot_id: spot.id,
        spot_name: spot.name,
        city: spot.city || "Chittagong",
        date,
        time_slot: timeSlot,
        group_size: Number(groupSize),
        lead_name: leadName,
        lead_contact: leadContact,
        eco_pledge: ecoPledge,
        redeem_eco_points: useEcoPoints ? availableEcoPoints : 0,
        unit_cost_bdt: unitCost,
      });
      setConfirmation(res);
      setStep(3);
      toast.success(`Voucher ${res.voucher_code} issued for ${spot.name.split("(")[0].trim()}!`);
    } catch {
      toast.error("Could not complete reservation.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Drawer.Root open={isOpen} onOpenChange={(open) => { if (!open) handleClose(); }}>
      <Drawer.Portal>
        <Drawer.Overlay className="fixed inset-0 bg-[#141715]/60 backdrop-blur-sm z-[100000]" />
        <Drawer.Content className="fixed bottom-0 left-0 right-0 z-[100001] mx-auto max-w-xl rounded-t-[28px] bg-[#F8F6F1] border border-[#E6E1D6] shadow-2xl flex flex-col max-h-[90vh] focus:outline-none">
          <div className="mx-auto mt-3 mb-1 h-1.5 w-12 rounded-full bg-[#D5CEBF]" />

          {/* Header */}
          <div className="px-6 py-4 flex items-center justify-between border-b border-[#E6E1D6]">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#1E4D3F]">
                Verified Local Partner Pass
              </span>
              <Drawer.Title className="font-display text-xl font-semibold text-[#141715] mt-0.5">
                {spot.name.split("(")[0].trim()}
              </Drawer.Title>
            </div>
            <button
              type="button"
              onClick={handleClose}
              className="w-8 h-8 rounded-full bg-white border border-[#E6E1D6] flex items-center justify-center text-[#141715] cursor-pointer hover:bg-[#EFECE4]"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Body */}
          <div className="p-6 overflow-y-auto space-y-5">
            {step === 1 && (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-[#5A605C] mb-1.5">Date</label>
                    <input
                      type="date"
                      value={date}
                      onChange={(e) => setDate(e.target.value)}
                      className="w-full rounded-xl bg-white border border-[#E6E1D6] px-3.5 py-2.5 text-sm text-[#141715]"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-[#5A605C] mb-1.5">
                      Squad Count ({groupSize} travelers)
                    </label>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => setGroupSize(Math.max(1, groupSize - 1))}
                        className="w-10 h-10 rounded-xl bg-white border border-[#E6E1D6] text-base font-bold cursor-pointer"
                      >
                        −
                      </button>
                      <div className="flex-1 text-center font-mono-num text-sm font-bold bg-white border border-[#E6E1D6] py-2.5 rounded-xl">
                        <Users className="w-3.5 h-3.5 inline mr-1.5 text-[#1E4D3F]" />
                        {groupSize}
                      </div>
                      <button
                        type="button"
                        onClick={() => setGroupSize(Math.min(15, groupSize + 1))}
                        className="w-10 h-10 rounded-xl bg-white border border-[#E6E1D6] text-base font-bold cursor-pointer"
                      >
                        +
                      </button>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#5A605C] mb-1.5">Time Window</label>
                  <select
                    value={timeSlot}
                    onChange={(e) => setTimeSlot(e.target.value)}
                    className="w-full rounded-xl bg-white border border-[#E6E1D6] px-3.5 py-2.5 text-sm text-[#141715]"
                  >
                    <option>Morning (09:00 AM - 12:00 PM)</option>
                    <option>Afternoon (01:30 PM - 05:00 PM)</option>
                    <option>Evening (06:00 PM - 09:00 PM)</option>
                  </select>
                </div>

                <label className="flex items-center justify-between gap-3 p-3.5 rounded-2xl bg-[#E8F2EE] border border-[#C6DED4] cursor-pointer">
                  <span className="flex items-center gap-2 text-xs font-semibold text-[#1E4D3F]">
                    <Sparkles className="w-4 h-4" />
                    Redeem {availableEcoPoints} Eco-Points (-{formatCurrency(Math.floor(availableEcoPoints * 0.5), currency)})
                  </span>
                  <input
                    type="checkbox"
                    checked={useEcoPoints}
                    onChange={(e) => setUseEcoPoints(e.target.checked)}
                    className="w-4 h-4 accent-[#1E4D3F]"
                  />
                </label>

                <div className="rounded-2xl bg-white border border-[#E6E1D6] p-4 space-y-2 text-xs">
                  <div className="flex justify-between text-[#5A605C]">
                    <span>Squad subtotal ({groupSize} × {formatCurrency(unitCost, currency)})</span>
                    <span className="font-mono-num">{formatCurrency(baseTotal, currency)}</span>
                  </div>
                  <div className="flex justify-between text-[#1E4D3F] font-semibold">
                    <span>Squad Discount ({groupDiscountPct}%)</span>
                    <span className="font-mono-num">-{formatCurrency(groupDiscountBdt, currency)}</span>
                  </div>
                  {ecoDiscountBdt > 0 && (
                    <div className="flex justify-between text-[#D94E28] font-semibold">
                      <span>Eco-Points Credit</span>
                      <span className="font-mono-num">-{formatCurrency(ecoDiscountBdt, currency)}</span>
                    </div>
                  )}
                  <div className="pt-2 border-t border-[#EFECE4] flex justify-between text-sm font-bold text-[#141715]">
                    <span>Total Group Payable</span>
                    <span className="font-mono-num">{formatCurrency(finalPayable, currency)}</span>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setStep(2)}
                  className="w-full rounded-full bg-[#141715] hover:bg-[#262C29] text-white py-3 text-sm font-semibold border-none cursor-pointer transition"
                >
                  Continue to Traveler Details
                </button>
              </>
            )}

            {step === 2 && (
              <form onSubmit={handleConfirm} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-[#5A605C] mb-1.5">Lead Traveler Name</label>
                  <input
                    required
                    type="text"
                    value={leadName}
                    onChange={(e) => setLeadName(e.target.value)}
                    className="w-full rounded-xl bg-white border border-[#E6E1D6] px-3.5 py-2.5 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-[#5A605C] mb-1.5">Phone / WhatsApp</label>
                  <input
                    required
                    type="text"
                    value={leadContact}
                    onChange={(e) => setLeadContact(e.target.value)}
                    className="w-full rounded-xl bg-white border border-[#E6E1D6] px-3.5 py-2.5 text-sm"
                  />
                </div>
                <label className="flex items-center gap-2.5 text-xs font-medium text-[#1E4D3F] bg-[#E8F2EE] p-3.5 rounded-2xl cursor-pointer">
                  <input
                    type="checkbox"
                    checked={ecoPledge}
                    onChange={(e) => setEcoPledge(e.target.checked)}
                    className="w-4 h-4 accent-[#1E4D3F]"
                  />
                  <Leaf className="w-4 h-4 shrink-0" />
                  <span>Zero-Plastic Eco Pledge (+40 Bonus Eco-Points)</span>
                </label>

                <div className="flex gap-2.5 pt-2">
                  <button
                    type="button"
                    onClick={() => setStep(1)}
                    className="px-5 py-3 rounded-full bg-white border border-[#E6E1D6] text-xs font-semibold text-[#141715] cursor-pointer"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="flex-1 rounded-full bg-[#D94E28] hover:bg-[#BF401E] text-white py-3 text-sm font-semibold border-none cursor-pointer transition inline-flex items-center justify-center gap-2"
                  >
                    <CalendarCheck className="w-4 h-4" />
                    <span>{submitting ? "Issuing Voucher..." : `Confirm (${formatCurrency(finalPayable, currency)})`}</span>
                  </button>
                </div>
              </form>
            )}

            {step === 3 && confirmation && (
              <div className="text-center space-y-4 py-2">
                <div className="w-12 h-12 rounded-full bg-[#E8F2EE] text-[#1E4D3F] inline-flex items-center justify-center">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-display text-2xl font-semibold text-[#141715] m-0">
                    Booking Confirmed
                  </h3>
                  <p className="text-xs text-[#5A605C] mt-1">
                    Host: {confirmation.partner_name}
                  </p>
                </div>

                <div className="rounded-2xl bg-[#141715] text-white p-5 space-y-1.5">
                  <div className="text-[10px] uppercase tracking-[0.16em] text-white/60">Digital Pass Code</div>
                  <div className="font-mono-num text-2xl font-bold text-[#F4A586]">
                    {confirmation.voucher_code}
                  </div>
                  <div className="text-xs text-white/80">
                    {confirmation.date} • {confirmation.group_size} Travelers
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="rounded-xl bg-white border border-[#E6E1D6] p-3">
                    <div className="text-[#5A605C]">Paid Total</div>
                    <div className="font-mono-num font-bold text-sm text-[#141715] mt-0.5">
                      {formatCurrency(confirmation.final_total_bdt, currency)}
                    </div>
                  </div>
                  <div className="rounded-xl bg-[#E8F2EE] border border-[#C6DED4] p-3">
                    <div className="text-[#1E4D3F]">Local SME Impact</div>
                    <div className="font-mono-num font-bold text-sm text-[#1E4D3F] mt-0.5">
                      {formatCurrency(confirmation.local_sme_revenue_bdt, currency)}
                    </div>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleClose}
                  className="w-full rounded-full bg-[#141715] text-white py-3 text-sm font-semibold border-none cursor-pointer"
                >
                  Done &amp; Return to Itinerary
                </button>
              </div>
            )}
          </div>
        </Drawer.Content>
      </Drawer.Portal>
    </Drawer.Root>
  );
}
