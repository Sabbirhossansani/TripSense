import React, { useState } from "react";
import { Plus, Trash2, CheckCircle2, Receipt, Sparkles, Camera } from "lucide-react";
import ReceiptScanModal from "./ReceiptScanModal";
import BkashPaymentModal from "./BkashPaymentModal";

export default function ExpenseSplitterTab({
  members = [],
  itinerarySpots = [],
  expenses = [],
  setExpenses,
  settledDebts = {},
  setSettledDebts
}) {
  const memberNames = members.map((m) => m.name);

  const [counter, setCounter] = useState(100);
  const [newTitle, setNewTitle] = useState("");
  const [newAmount, setNewAmount] = useState("");
  const [paidBy, setPaidBy] = useState(memberNames[0] || "Rahat");
  const [isAdding, setIsAdding] = useState(false);
  const [isScanModalOpen, setIsScanModalOpen] = useState(false);
  const [activeBkashSettlement, setActiveBkashSettlement] = useState(null);

  const activePaidBy = memberNames.includes(paidBy) ? paidBy : (memberNames[0] || "Rahat");

  // Add Expense
  const handleAddExpense = (e) => {
    e.preventDefault();
    const parsedAmount = parseFloat(newAmount);
    if (!newTitle.trim() || isNaN(parsedAmount) || parsedAmount <= 0) return;

    const nextId = counter + 1;
    setCounter(nextId);

    const newExp = {
      id: `exp-${nextId}`,
      title: newTitle.trim(),
      amountBDT: Math.round(parsedAmount),
      paidBy: activePaidBy,
      splitWith: [...memberNames],
      date: "Today"
    };

    setExpenses([newExp, ...expenses]);
    setNewTitle("");
    setNewAmount("");
    setIsAdding(false);
  };

  // Remove Expense
  const handleRemoveExpense = (id) => {
    setExpenses(expenses.filter((e) => e.id !== id));
  };

  // Import Ticket Costs from Itinerary (with deduplication)
  const handleImportItineraryCosts = () => {
    let currentCount = counter;
    const existingTitles = new Set(expenses.map((e) => e.title));
    const imported = [];

    itinerarySpots.forEach((spot) => {
      const cost = spot.estimated_cost_bdt || 0;
      const title = `Admission: ${spot.name}`;
      if (cost > 0 && !existingTitles.has(title)) {
        currentCount += 1;
        imported.push({
          id: `spot-cost-${spot.id}-${currentCount}`,
          title: title,
          amountBDT: Math.round(cost * Math.max(1, memberNames.length)), // total group admission
          paidBy: memberNames[0] || "Rahat",
          splitWith: [...memberNames],
          date: spot.scheduled_slot || "Trip Itinerary"
        });
      }
    });

    setCounter(currentCount);

    if (imported.length === 0) {
      alert("All admission tickets for this itinerary have already been imported or are free entry!");
      return;
    }

    setExpenses([...imported, ...expenses]);
  };

  // Calculate Balances & Debt Settlements
  const totalSpent = expenses.reduce((sum, e) => sum + e.amountBDT, 0);

  const paidAmounts = {};
  const shouldPayAmounts = {};

  memberNames.forEach((m) => {
    paidAmounts[m] = 0;
    shouldPayAmounts[m] = 0;
  });

  expenses.forEach((e) => {
    // If payer is in current group, attribute to them; if removed, attribute to first available member
    const actualPayer = memberNames.includes(e.paidBy) ? e.paidBy : (memberNames[0] || "");
    if (actualPayer && paidAmounts[actualPayer] !== undefined) {
      paidAmounts[actualPayer] += e.amountBDT;
    }

    // Split only among members who are currently in the room
    const activeSplit = (e.splitWith || []).filter((m) => memberNames.includes(m));
    const finalSplit = activeSplit.length > 0 ? activeSplit : memberNames;
    const share = e.amountBDT / Math.max(1, finalSplit.length);

    finalSplit.forEach((m) => {
      if (shouldPayAmounts[m] !== undefined) {
        shouldPayAmounts[m] += share;
      }
    });
  });

  // Net Balance: paid - shouldPay (sum is guaranteed to be 0)
  const netBalances = {};
  memberNames.forEach((m) => {
    netBalances[m] = (paidAmounts[m] || 0) - (shouldPayAmounts[m] || 0);
  });

  // Minimal transaction settlement algorithm
  const calculateSettlements = () => {
    const creditors = []; // positive balance (should receive)
    const debtors = []; // negative balance (owes money)

    memberNames.forEach((m) => {
      const bal = netBalances[m] || 0;
      if (bal > 1) {
        creditors.push({ name: m, amount: bal });
      } else if (bal < -1) {
        debtors.push({ name: m, amount: -bal });
      }
    });

    creditors.sort((a, b) => b.amount - a.amount);
    debtors.sort((a, b) => b.amount - a.amount);

    const settlements = [];
    let i = 0;
    let j = 0;

    while (i < debtors.length && j < creditors.length) {
      const debtor = debtors[i];
      const creditor = creditors[j];
      const transfer = Math.min(debtor.amount, creditor.amount);

      if (transfer > 1) {
        settlements.push({
          id: `${debtor.name}->${creditor.name}`,
          from: debtor.name,
          to: creditor.name,
          amount: Math.round(transfer)
        });
      }

      debtor.amount -= transfer;
      creditor.amount -= transfer;

      if (debtor.amount < 1) i++;
      if (creditor.amount < 1) j++;
    }

    return settlements;
  };

  const settlements = calculateSettlements();

  const toggleDebtSettled = (id) => {
    setSettledDebts({ ...settledDebts, [id]: !settledDebts[id] });
  };

  return (
    <div style={{ maxWidth: "760px", margin: "0 auto", paddingBottom: "50px" }}>
      {/* Overview Cards */}
      <div style={{
        background: "linear-gradient(135deg, #1A1D1C 0%, #1e293b 100%)",
        borderRadius: "20px",
        padding: "20px",
        color: "#ffffff",
        marginBottom: "20px",
        boxShadow: "0 8px 24px rgba(15, 23, 42, 0.2)"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "10px" }}>
          <div>
            <div style={{ fontSize: "11px", color: "#94a3b8", textTransform: "uppercase", fontWeight: 700, letterSpacing: "0.5px" }}>
              Total Shared Group Expenses
            </div>
            <div style={{ fontSize: "28px", fontWeight: 900, color: "#38bdf8", marginTop: "2px" }}>
              ৳{Math.round(totalSpent).toLocaleString()} <span style={{ fontSize: "14px", color: "#94a3b8", fontWeight: 500 }}>(~${(totalSpent / 115).toFixed(1)})</span>
            </div>
          </div>

          <button
            onClick={handleImportItineraryCosts}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              background: "rgba(56, 189, 248, 0.15)",
              border: "1px solid rgba(56, 189, 248, 0.4)",
              color: "#38bdf8",
              padding: "8px 12px",
              borderRadius: "10px",
              fontSize: "11px",
              fontWeight: 700,
              cursor: "pointer"
            }}
          >
            <Sparkles size={13} />
            Import Itinerary Tickets
          </button>
        </div>

        {/* Member balances summary strip */}
        <div style={{ display: "grid", gridTemplateColumns: `repeat(${Math.max(1, memberNames.length)}, 1fr)`, gap: "8px" }}>
          {memberNames.map((m) => {
            const bal = netBalances[m] || 0;
            const isCreditor = bal > 1;
            const isDebtor = bal < -1;

            return (
              <div
                key={m}
                style={{
                  background: "rgba(255, 255, 255, 0.08)",
                  borderRadius: "12px",
                  padding: "10px",
                  textAlign: "center"
                }}
              >
                <div style={{ fontSize: "12px", fontWeight: 700, color: "#F6F4EF" }}>{m}</div>
                <div style={{ fontSize: "10px", color: "#94a3b8", margin: "2px 0 4px" }}>
                  Paid: ৳{Math.round(paidAmounts[m] || 0)}
                </div>
                <div style={{
                  fontSize: "12px",
                  fontWeight: 800,
                  color: isCreditor ? "#4ade80" : isDebtor ? "#f87171" : "#94a3b8"
                }}>
                  {isCreditor ? `+৳${Math.round(bal)}` : isDebtor ? `-৳${Math.round(-bal)}` : "Settled"}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Smart Settlements Card ("Who Owes Whom") */}
      <div style={{
        background: "#ffffff",
        borderRadius: "16px",
        border: "1px solid #E2DDD3",
        padding: "16px",
        marginBottom: "20px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.03)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "12px" }}>
          <Receipt size={17} color="#E85D2A" />
          <h3 style={{ fontSize: "14px", fontWeight: 800, color: "#1A1D1C", margin: 0 }}>
            Smart Debt Settlement Matrix
          </h3>
        </div>

        {settlements.length === 0 ? (
          <div style={{
            background: "#f0fdf4",
            border: "1px solid #bbf7d0",
            borderRadius: "10px",
            padding: "12px",
            textAlign: "center",
            fontSize: "12px",
            color: "#166534",
            fontWeight: 600
          }}>
            ✓ All friends are completely balanced! No pending debts.
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {settlements.map((s) => {
              const isSettled = settledDebts[s.id];
              return (
                <div
                  key={s.id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "10px 14px",
                    borderRadius: "10px",
                    background: isSettled ? "#f1f5f9" : "#fffbeb",
                    border: isSettled ? "1px solid #cbd5e1" : "1px solid #fde68a",
                    opacity: isSettled ? 0.6 : 1,
                    transition: "all 0.2s ease"
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px" }}>
                    <strong style={{ color: "#1A1D1C" }}>{s.from}</strong>
                    <span style={{ color: "#59615E", fontSize: "12px" }}>owes</span>
                    <strong style={{ color: "#1A1D1C" }}>{s.to}</strong>
                    <span style={{
                      fontWeight: 800,
                      color: isSettled ? "#59615E" : "#b45309",
                      background: isSettled ? "#E2DDD3" : "#fef3c7",
                      padding: "2px 8px",
                      borderRadius: "6px"
                    }}>
                      ৳{s.amount}
                    </span>
                  </div>

                  <div style={{ display: "flex", gap: "6px" }}>
                    {!isSettled && (
                      <button
                        onClick={() => setActiveBkashSettlement(s)}
                        style={{
                          background: "#e2136e",
                          color: "#ffffff",
                          border: "none",
                          borderRadius: "6px",
                          padding: "4px 8px",
                          fontSize: "11px",
                          fontWeight: 700,
                          cursor: "pointer",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "4px"
                        }}
                      >
                        📱 Pay bKash
                      </button>
                    )}

                    <button
                      onClick={() => toggleDebtSettled(s.id)}
                      style={{
                        background: isSettled ? "#10b981" : "#ffffff",
                        color: isSettled ? "#ffffff" : "#475569",
                        border: "1px solid #cbd5e1",
                        borderRadius: "6px",
                        padding: "4px 8px",
                        fontSize: "11px",
                        fontWeight: 600,
                        cursor: "pointer",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "4px"
                      }}
                    >
                      <CheckCircle2 size={12} />
                      {isSettled ? "Settled" : "Mark Paid"}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Expense Entries Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px", flexWrap: "wrap", gap: "8px" }}>
        <h3 style={{ fontSize: "15px", fontWeight: 800, color: "#1A1D1C", margin: 0 }}>
          Expenses History ({expenses.length})
        </h3>
        <div style={{ display: "flex", gap: "8px" }}>
          <button
            onClick={() => setIsScanModalOpen(true)}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "5px",
              background: "#eff6ff",
              color: "#1d4ed8",
              border: "1px solid #bfdbfe",
              padding: "6px 12px",
              borderRadius: "10px",
              fontSize: "12px",
              fontWeight: 700,
              cursor: "pointer"
            }}
          >
            <Camera size={14} />
            Scan Receipt 📸
          </button>
          <button
            onClick={() => setIsAdding(!isAdding)}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "5px",
              background: "#E85D2A",
              color: "#ffffff",
              border: "none",
              padding: "6px 12px",
              borderRadius: "10px",
              fontSize: "12px",
              fontWeight: 700,
              cursor: "pointer"
            }}
          >
            <Plus size={14} />
            Add Expense
          </button>
        </div>
      </div>

      {/* Add Expense Form */}
      {isAdding && (
        <form
          onSubmit={handleAddExpense}
          style={{
            background: "#ffffff",
            border: "2px dashed #E85D2A",
            borderRadius: "16px",
            padding: "16px",
            marginBottom: "16px",
            display: "flex",
            flexDirection: "column",
            gap: "10px"
          }}
        >
          <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "10px" }}>
            <input
              type="text"
              placeholder="What was it? (e.g. Seafood Dinner, Rickshaw)"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              autoFocus
              style={{
                padding: "10px 12px",
                borderRadius: "10px",
                border: "1px solid #cbd5e1",
                fontSize: "13px"
              }}
            />
            <input
              type="number"
              placeholder="Amount (৳)"
              value={newAmount}
              onChange={(e) => setNewAmount(e.target.value)}
              style={{
                padding: "10px 12px",
                borderRadius: "10px",
                border: "1px solid #cbd5e1",
                fontSize: "13px"
              }}
            />
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
            <label style={{ fontSize: "12px", color: "#475569", fontWeight: 600 }}>Paid By:</label>
            <select
              value={activePaidBy}
              onChange={(e) => setPaidBy(e.target.value)}
              style={{
                padding: "6px 10px",
                borderRadius: "8px",
                border: "1px solid #cbd5e1",
                fontSize: "12px",
                fontWeight: 600
              }}
            >
              {memberNames.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
            <span style={{ fontSize: "11px", color: "#59615E", marginLeft: "auto" }}>
              Split equally among all {memberNames.length} friends
            </span>
          </div>

          <div style={{ display: "flex", gap: "8px", marginTop: "4px" }}>
            <button
              type="submit"
              style={{
                background: "#E85D2A",
                color: "#ffffff",
                border: "none",
                padding: "8px 16px",
                borderRadius: "8px",
                fontSize: "12px",
                fontWeight: 700,
                cursor: "pointer"
              }}
            >
              Save Expense
            </button>
            <button
              type="button"
              onClick={() => setIsAdding(false)}
              style={{
                background: "#f1f5f9",
                color: "#475569",
                border: "none",
                padding: "8px 12px",
                borderRadius: "8px",
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer"
              }}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Expenses List */}
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {expenses.length === 0 ? (
          <div style={{
            background: "#ffffff",
            borderRadius: "12px",
            border: "1px dashed #cbd5e1",
            padding: "24px",
            textAlign: "center",
            color: "#59615E",
            fontSize: "13px"
          }}>
            No shared expenses recorded yet. Click "Add Expense" or import ticket costs from your itinerary!
          </div>
        ) : (
          expenses.map((exp) => (
            <div
              key={exp.id}
              style={{
                background: "#ffffff",
                borderRadius: "12px",
                border: "1px solid #E2DDD3",
                padding: "12px 14px",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between"
              }}
            >
              <div>
                <div style={{ fontSize: "13px", fontWeight: 700, color: "#1A1D1C" }}>
                  {exp.title}
                </div>
                <div style={{ fontSize: "11px", color: "#59615E", marginTop: "2px" }}>
                  Paid by <strong>{exp.paidBy}</strong> • {exp.date} • Split with {exp.splitWith?.length || memberNames.length} friends
                </div>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <span style={{ fontSize: "14px", fontWeight: 800, color: "#1A1D1C" }}>
                  ৳{exp.amountBDT.toLocaleString()}
                </span>
                <button
                  onClick={() => handleRemoveExpense(exp.id)}
                  title="Delete expense"
                  style={{
                    background: "transparent",
                    border: "none",
                    color: "#94a3b8",
                    cursor: "pointer",
                    padding: "4px"
                  }}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Smart Receipt Scanner Modal */}
      <ReceiptScanModal
        isOpen={isScanModalOpen}
        onClose={() => setIsScanModalOpen(false)}
        members={members}
        onImportExpense={(newExp) => {
          const nextId = counter + 1;
          setCounter(nextId);
          setExpenses([{ ...newExp, id: `exp-${nextId}` }, ...expenses]);
        }}
      />

      {/* Simulated bKash / Nagad Instant Payment Modal */}
      <BkashPaymentModal
        settlement={activeBkashSettlement}
        onClose={() => setActiveBkashSettlement(null)}
        onConfirmSettlement={(settle) => {
          setSettledDebts({ ...settledDebts, [settle.id]: true });
        }}
      />
    </div>
  );
}
