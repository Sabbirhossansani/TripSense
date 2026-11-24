import React, { useState } from "react";
import { X, Camera, Scan, Plus } from "lucide-react";

const SAMPLE_RECEIPTS = [
  {
    merchant: "Mezban Haat Chittagong",
    category: "Food",
    totalBdt: 2200,
    items: [
      { name: "Traditional Mezban Gosht", price: 1600 },
      { name: "Chonar Dal with Gosht", price: 350 },
      { name: "Borhani (1 Pitcher)", price: 250 }
    ]
  },
  {
    merchant: "Chittagong Port CNG Taxi",
    category: "Transit",
    totalBdt: 450,
    items: [
      { name: "GEC Circle to Patenga Beach (Trip Meter)", price: 450 }
    ]
  },
  {
    merchant: "Foy's Lake Concord Park Ticket Counter",
    category: "Activities",
    totalBdt: 1200,
    items: [
      { name: "Group Park Entry + Boat Ride (3 Persons)", price: 1200 }
    ]
  }
];

export default function ReceiptScanModal({ isOpen, onClose, onImportExpense, members = [] }) {
  const [selectedReceipt, setSelectedReceipt] = useState(SAMPLE_RECEIPTS[0]);
  const [isScanning, setIsScanning] = useState(false);
  const [scanComplete, setScanComplete] = useState(false);
  const [paidBy, setPaidBy] = useState(members[0]?.name || "Rahat");

  if (!isOpen) return null;

  const handleStartScan = (receipt) => {
    setSelectedReceipt(receipt);
    setIsScanning(true);
    setScanComplete(false);

    setTimeout(() => {
      setIsScanning(false);
      setScanComplete(true);
    }, 1200);
  };

  const handleConfirmImport = () => {
    onImportExpense({
      title: `${selectedReceipt.merchant} (${selectedReceipt.items[0]?.name})`,
      amountBDT: selectedReceipt.totalBdt,
      paidBy: paidBy,
      splitWith: members.map((m) => m.name),
      date: "Receipt Scan"
    });
    onClose();
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
        maxWidth: "460px",
        width: "100%",
        boxShadow: "0 25px 60px rgba(0,0,0,0.35)",
        animation: "slideUp 0.3s ease"
      }}>
        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "#FFF0EA",
              color: "#E85D2A",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}>
              <Camera size={20} />
            </div>
            <div>
              <h3 style={{ fontSize: "16px", fontWeight: 800, margin: 0, color: "#1A1D1C" }}>
                AI Smart Receipt Scanner
              </h3>
              <div style={{ fontSize: "11px", color: "#59615E" }}>
                Instant OCR extraction for dining, CNG & entry tickets
              </div>
            </div>
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

        {/* Camera Viewfinder Simulation */}
        <div style={{
          position: "relative",
          height: "180px",
          borderRadius: "18px",
          background: "#1A1D1C",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          color: "#ffffff",
          marginBottom: "16px",
          boxShadow: "inset 0 0 20px rgba(0,0,0,0.6)"
        }}>
          {/* Laser Scan Line Animation */}
          {isScanning && (
            <div style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              height: "3px",
              background: "#10b981",
              boxShadow: "0 0 12px #10b981",
              animation: "slideDown 1.2s infinite ease-in-out"
            }} />
          )}

          <div style={{
            border: "2px dashed rgba(255, 255, 255, 0.4)",
            borderRadius: "14px",
            padding: "16px 24px",
            textAlign: "center",
            background: "rgba(255, 255, 255, 0.05)"
          }}>
            <Scan size={32} color={scanComplete ? "#10b981" : "#E85D2A"} style={{ marginBottom: "8px" }} />
            <div style={{ fontSize: "13px", fontWeight: 700 }}>
              {isScanning ? "Processing OCR Line Items..." : scanComplete ? "✓ Receipt Scanned Successfully!" : "Point Camera at Paper Bill"}
            </div>
            <div style={{ fontSize: "11px", color: "#94a3b8" }}>
              {selectedReceipt.merchant}
            </div>
          </div>
        </div>

        {/* Preset Receipts Selector */}
        <div style={{ marginBottom: "14px" }}>
          <div style={{ fontSize: "11px", fontWeight: 700, color: "#59615E", marginBottom: "6px" }}>
            SELECT DEMO RECEIPT TO SCAN:
          </div>
          <div style={{ display: "flex", gap: "6px" }}>
            {SAMPLE_RECEIPTS.map((rec) => (
              <button
                key={rec.merchant}
                type="button"
                onClick={() => handleStartScan(rec)}
                style={{
                  flex: 1,
                  padding: "6px 8px",
                  borderRadius: "10px",
                  border: selectedReceipt.merchant === rec.merchant ? "1.5px solid #E85D2A" : "1px solid #cbd5e1",
                  background: selectedReceipt.merchant === rec.merchant ? "#FFF0EA" : "#ffffff",
                  fontSize: "11px",
                  fontWeight: 700,
                  color: "#1e293b",
                  cursor: "pointer"
                }}
              >
                {rec.category}: ৳{rec.totalBdt}
              </button>
            ))}
          </div>
        </div>

        {/* Extracted Items Breakdown */}
        <div style={{
          background: "#F6F4EF",
          border: "1px solid #E2DDD3",
          borderRadius: "14px",
          padding: "12px",
          marginBottom: "16px"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", fontWeight: 800, marginBottom: "8px", color: "#1A1D1C" }}>
            <span>{selectedReceipt.merchant}</span>
            <span style={{ color: "#059669" }}>Total: ৳{selectedReceipt.totalBdt}</span>
          </div>
          {selectedReceipt.items.map((item, idx) => (
            <div key={idx} style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "#59615E", marginBottom: "4px" }}>
              <span>• {item.name}</span>
              <span>৳{item.price}</span>
            </div>
          ))}
        </div>

        {/* Who Paid Dropdown */}
        <div style={{ marginBottom: "18px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ fontSize: "12px", fontWeight: 700, color: "#334155" }}>
            Paid By:
          </span>
          <select
            value={paidBy}
            onChange={(e) => setPaidBy(e.target.value)}
            style={{
              padding: "6px 12px",
              borderRadius: "10px",
              border: "1px solid #cbd5e1",
              fontSize: "12px",
              fontWeight: 700
            }}
          >
            {members.map((m) => (
              <option key={m.name} value={m.name}>
                {m.name}
              </option>
            ))}
          </select>
        </div>

        {/* Action Button */}
        <button
          onClick={handleConfirmImport}
          style={{
            width: "100%",
            padding: "12px",
            borderRadius: "14px",
            border: "none",
            background: "#E85D2A",
            color: "#ffffff",
            fontSize: "13px",
            fontWeight: 800,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "6px",
            boxShadow: "0 6px 16px rgba(79, 70, 229, 0.3)"
          }}
        >
          <Plus size={16} />
          <span>Add Scanned Receipt to Group Split (৳{selectedReceipt.totalBdt})</span>
        </button>
      </div>
    </div>
  );
}
