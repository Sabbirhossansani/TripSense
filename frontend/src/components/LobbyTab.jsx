import React, { useState } from "react";
import { Users, UserPlus, Trash2, Check, Copy, Sparkles, Sliders } from "lucide-react";

const AVAILABLE_INTERESTS = [
  { id: "Historical", label: "Historical 🏛️" },
  { id: "Beach", label: "Beach 🏖️" },
  { id: "Nature", label: "Nature 🌿" },
  { id: "Food", label: "Food & Drink 🍲" },
  { id: "Culture", label: "Culture 🎭" },
  { id: "Adventure", label: "Adventure 🧗" },
  { id: "Relaxation", label: "Relaxation 🧘" },
  { id: "Religious", label: "Religious 🕌" }
];

const BUDGET_TIERS = ["Budget", "Mid-range", "Luxury"];

const MEMBER_COLORS = ["#E85D2A", "#ec4899", "#f59e0b", "#10b981", "#8b5cf6", "#06b6d4"];

export default function LobbyTab({
  roomCode = "CTG-882",
  members = [],
  setMembers,
  consensusStrategy,
  setConsensusStrategy,
  promoteHiddenGems,
  setPromoteHiddenGems,
  pace,
  setPace,
  onGeneratePlan,
  isLoading
}) {
  const [copied, setCopied] = useState(false);
  const [editingMemberIndex, setEditingMemberIndex] = useState(null);
  const [newMemberName, setNewMemberName] = useState("");
  const [isAddingMember, setIsAddingMember] = useState(false);

  const handleCopyCode = () => {
    navigator.clipboard?.writeText(roomCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleAddMember = (e) => {
    e.preventDefault();
    const trimmed = newMemberName.trim();
    if (!trimmed) return;

    if (members.some((m) => m.name.toLowerCase() === trimmed.toLowerCase())) {
      alert(`A tripmate named "${trimmed}" is already in the lobby.`);
      return;
    }

    const newMember = {
      name: trimmed,
      interests: ["Historical", "Culture"],
      budget_tier: "Mid-range"
    };

    setMembers([...members, newMember]);
    setNewMemberName("");
    setIsAddingMember(false);
  };

  const handleRemoveMember = (indexToRemove) => {
    if (members.length <= 1) {
      alert("At least one member is required in the group.");
      return;
    }
    setMembers(members.filter((_, idx) => idx !== indexToRemove));
  };

  const handleToggleInterest = (memberIdx, interestId) => {
    const updated = [...members];
    const member = { ...updated[memberIdx] };
    const currentInterests = new Set(member.interests || []);

    if (currentInterests.has(interestId)) {
      if (currentInterests.size > 1) {
        currentInterests.delete(interestId);
      }
    } else {
      currentInterests.add(interestId);
    }

    member.interests = Array.from(currentInterests);
    updated[memberIdx] = member;
    setMembers(updated);
  };

  const handleBudgetChange = (memberIdx, tier) => {
    const updated = [...members];
    updated[memberIdx] = { ...updated[memberIdx], budget_tier: tier };
    setMembers(updated);
  };

  return (
    <div style={{ maxWidth: "720px", margin: "0 auto", paddingBottom: "40px" }}>
      {/* Group Room Header Banner */}
      <div style={{
        background: "linear-gradient(135deg, #25463B 0%, #1A1D1C 100%)",
        borderRadius: "20px",
        padding: "20px",
        color: "#ffffff",
        marginBottom: "20px",
        boxShadow: "0 10px 25px rgba(30, 27, 75, 0.25)",
        position: "relative",
        overflow: "hidden"
      }}>
        <div style={{
          position: "absolute",
          top: "-20px",
          right: "-20px",
          width: "120px",
          height: "120px",
          background: "radial-gradient(circle, rgba(99,102,241,0.3) 0%, transparent 70%)",
          borderRadius: "50%"
        }} />

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", position: "relative", zIndex: 1 }}>
          <div>
            <div style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              background: "rgba(255, 255, 255, 0.15)",
              padding: "4px 10px",
              borderRadius: "16px",
              fontSize: "11px",
              fontWeight: 700,
              letterSpacing: "0.5px",
              marginBottom: "8px"
            }}>
              <Users size={12} />
              COLLABORATIVE TRIP ROOM
            </div>
            <h2 style={{ fontSize: "20px", fontWeight: 800, margin: "0 0 4px 0" }}>
              TripSense Group Lobby
            </h2>
            <p style={{ fontSize: "12px", color: "#F7C6B3", margin: 0 }}>
              Multi-user preference voting with algorithmic fairness consensus
            </p>
          </div>

          {/* Room Code Badge */}
          <div style={{
            background: "rgba(255, 255, 255, 0.12)",
            border: "1px solid rgba(255, 255, 255, 0.25)",
            backdropFilter: "blur(8px)",
            borderRadius: "14px",
            padding: "8px 14px",
            textAlign: "center"
          }}>
            <div style={{ fontSize: "10px", color: "#a5b4fc", textTransform: "uppercase", fontWeight: 700 }}>
              Room Code
            </div>
            <div style={{ fontSize: "18px", fontWeight: 900, letterSpacing: "1px", margin: "2px 0 4px 0" }}>
              {roomCode}
            </div>
            <button
              onClick={handleCopyCode}
              style={{
                background: copied ? "#10b981" : "rgba(255, 255, 255, 0.2)",
                color: "#ffffff",
                border: "none",
                borderRadius: "6px",
                padding: "3px 8px",
                fontSize: "10px",
                fontWeight: 700,
                display: "inline-flex",
                alignItems: "center",
                gap: "4px",
                cursor: "pointer"
              }}
            >
              {copied ? <Check size={11} /> : <Copy size={11} />}
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>
        </div>
      </div>

      {/* Tripmates Management List */}
      <div style={{ marginBottom: "24px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
          <div>
            <h3 style={{ fontSize: "16px", fontWeight: 800, color: "#1A1D1C", margin: 0 }}>
              Tripmates & Individual Preferences ({members.length})
            </h3>
            <p style={{ fontSize: "12px", color: "#59615E", margin: 0 }}>
              Each friend has independent category interests and budget tier
            </p>
          </div>

          <button
            onClick={() => setIsAddingMember(!isAddingMember)}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              background: "#FFF0EA",
              color: "#CC4A1B",
              border: "1px solid #F7C6B3",
              padding: "6px 12px",
              borderRadius: "10px",
              fontSize: "12px",
              fontWeight: 700,
              cursor: "pointer"
            }}
          >
            <UserPlus size={14} />
            Add Tripmate
          </button>
        </div>

        {/* Add Member Form Modal / Expandable */}
        {isAddingMember && (
          <form
            onSubmit={handleAddMember}
            style={{
              background: "#ffffff",
              border: "2px dashed #E85D2A",
              borderRadius: "16px",
              padding: "16px",
              marginBottom: "16px",
              display: "flex",
              gap: "10px",
              alignItems: "center"
            }}
          >
            <input
              type="text"
              placeholder="Friend's Name (e.g. Tahmid, Nabila)"
              value={newMemberName}
              onChange={(e) => setNewMemberName(e.target.value)}
              autoFocus
              style={{
                flex: 1,
                padding: "10px 12px",
                borderRadius: "10px",
                border: "1px solid #cbd5e1",
                fontSize: "13px"
              }}
            />
            <button
              type="submit"
              style={{
                background: "#E85D2A",
                color: "#ffffff",
                border: "none",
                padding: "10px 16px",
                borderRadius: "10px",
                fontSize: "13px",
                fontWeight: 700,
                cursor: "pointer"
              }}
            >
              Add
            </button>
            <button
              type="button"
              onClick={() => setIsAddingMember(false)}
              style={{
                background: "#f1f5f9",
                color: "#475569",
                border: "none",
                padding: "10px 12px",
                borderRadius: "10px",
                fontSize: "13px",
                fontWeight: 600,
                cursor: "pointer"
              }}
            >
              Cancel
            </button>
          </form>
        )}

        {/* Members Cards */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {members.map((member, idx) => {
            const avatarColor = MEMBER_COLORS[idx % MEMBER_COLORS.length];
            const isEditing = editingMemberIndex === idx;

            return (
              <div
                key={idx}
                style={{
                  background: "#ffffff",
                  borderRadius: "16px",
                  border: "1px solid #E2DDD3",
                  padding: "16px",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.03)"
                }}
              >
                {/* Member Header */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <div style={{
                      width: "40px",
                      height: "40px",
                      borderRadius: "50%",
                      background: avatarColor,
                      color: "#ffffff",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "15px",
                      fontWeight: 800,
                      boxShadow: "0 2px 6px rgba(0,0,0,0.15)"
                    }}>
                      {member.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h4 style={{ margin: 0, fontSize: "15px", fontWeight: 700, color: "#1A1D1C" }}>
                        {member.name}
                      </h4>
                      <span style={{ fontSize: "11px", color: "#59615E" }}>
                        Budget: <strong>{member.budget_tier || "Mid-range"}</strong> • {member.interests?.length || 0} interests selected
                      </span>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <button
                      onClick={() => setEditingMemberIndex(isEditing ? null : idx)}
                      style={{
                        padding: "5px 10px",
                        borderRadius: "8px",
                        fontSize: "11px",
                        fontWeight: 600,
                        border: "1px solid #cbd5e1",
                        background: isEditing ? "#f1f5f9" : "#ffffff",
                        color: "#334155",
                        cursor: "pointer"
                      }}
                    >
                      {isEditing ? "Done" : "Customize"}
                    </button>

                    {members.length > 1 && (
                      <button
                        onClick={() => handleRemoveMember(idx)}
                        title="Remove member"
                        style={{
                          background: "#fff1f2",
                          border: "none",
                          borderRadius: "8px",
                          width: "30px",
                          height: "30px",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          cursor: "pointer",
                          color: "#e11d48"
                        }}
                      >
                        <Trash2 size={14} />
                      </button>
                    )}
                  </div>
                </div>

                {/* Preference Tag Chips (Quiz selector) */}
                <div>
                  <div style={{ fontSize: "11px", fontWeight: 700, color: "#475569", marginBottom: "6px" }}>
                    Interests & Preferences:
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                    {AVAILABLE_INTERESTS.map((interest) => {
                      const isSelected = (member.interests || []).includes(interest.id);
                      return (
                        <button
                          key={interest.id}
                          type="button"
                          onClick={() => handleToggleInterest(idx, interest.id)}
                          style={{
                            padding: "4px 10px",
                            borderRadius: "14px",
                            fontSize: "11px",
                            fontWeight: isSelected ? 700 : 500,
                            border: isSelected ? "1.5px solid #E85D2A" : "1px solid #E2DDD3",
                            background: isSelected ? "#FFF0EA" : "#F6F4EF",
                            color: isSelected ? "#CC4A1B" : "#59615E",
                            cursor: "pointer",
                            transition: "all 0.15s ease"
                          }}
                        >
                          {interest.label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Budget Tier Selector (Shown when editing or expanded) */}
                {isEditing && (
                  <div style={{ marginTop: "14px", paddingTop: "12px", borderTop: "1px dashed #E2DDD3" }}>
                    <div style={{ fontSize: "11px", fontWeight: 700, color: "#475569", marginBottom: "6px" }}>
                      Budget Tier for {member.name}:
                    </div>
                    <div style={{ display: "flex", gap: "8px" }}>
                      {BUDGET_TIERS.map((tier) => (
                        <button
                          key={tier}
                          type="button"
                          onClick={() => handleBudgetChange(idx, tier)}
                          style={{
                            flex: 1,
                            padding: "6px",
                            borderRadius: "8px",
                            fontSize: "12px",
                            fontWeight: member.budget_tier === tier ? 700 : 500,
                            border: member.budget_tier === tier ? "2px solid #E85D2A" : "1px solid #cbd5e1",
                            background: member.budget_tier === tier ? "#FFF0EA" : "#ffffff",
                            color: member.budget_tier === tier ? "#CC4A1B" : "#475569",
                            cursor: "pointer"
                          }}
                        >
                          {tier === "Budget" && "৳ Budget"}
                          {tier === "Mid-range" && "৳৳ Mid-range"}
                          {tier === "Luxury" && "৳৳৳ Luxury"}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* FYDP Algorithm Settings Card */}
      <div style={{
        background: "#ffffff",
        borderRadius: "16px",
        border: "1px solid #E2DDD3",
        padding: "18px",
        marginBottom: "24px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.03)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "14px" }}>
          <Sliders size={18} color="#E85D2A" />
          <h3 style={{ fontSize: "15px", fontWeight: 800, color: "#1A1D1C", margin: 0 }}>
            Consensus & Scheduling Engine Options
          </h3>
        </div>

        {/* Consensus Strategy Selector */}
        <div style={{ marginBottom: "16px" }}>
          <div style={{ fontSize: "12px", fontWeight: 700, color: "#334155", marginBottom: "6px" }}>
            Group Aggregation Strategy:
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "10px" }}>
            <div
              onClick={() => setConsensusStrategy("fairnet")}
              style={{
                border: consensusStrategy === "fairnet" ? "2px solid #25463B" : "1px solid #cbd5e1",
                background: consensusStrategy === "fairnet" ? "#E8F0EC" : "#ffffff",
                borderRadius: "12px",
                padding: "12px",
                cursor: "pointer",
                transition: "all 0.15s ease"
              }}
            >
              <div style={{ fontSize: "13px", fontWeight: 800, color: consensusStrategy === "fairnet" ? "#25463B" : "#1e293b" }}>
                🧠 TripSense-FairNet (Q1 ML)
              </div>
              <div style={{ fontSize: "11px", color: "#59615E", marginTop: "3px" }}>
                Trained Cross-Attention + Fairness-BPR neural consensus with eco weighting.
              </div>
            </div>

            <div
              onClick={() => setConsensusStrategy("least_misery")}
              style={{
                border: consensusStrategy === "least_misery" ? "2px solid #E85D2A" : "1px solid #cbd5e1",
                background: consensusStrategy === "least_misery" ? "#FFF0EA" : "#ffffff",
                borderRadius: "12px",
                padding: "12px",
                cursor: "pointer",
                transition: "all 0.15s ease"
              }}
            >
              <div style={{ fontSize: "13px", fontWeight: 800, color: consensusStrategy === "least_misery" ? "#CC4A1B" : "#1e293b" }}>
                🛡️ Least-Misery (Fairness)
              </div>
              <div style={{ fontSize: "11px", color: "#59615E", marginTop: "3px" }}>
                Prioritizes minimizing dissatisfaction. No member gets alienated.
              </div>
            </div>

            <div
              onClick={() => setConsensusStrategy("average")}
              style={{
                border: consensusStrategy === "average" ? "2px solid #E85D2A" : "1px solid #cbd5e1",
                background: consensusStrategy === "average" ? "#FFF0EA" : "#ffffff",
                borderRadius: "12px",
                padding: "12px",
                cursor: "pointer",
                transition: "all 0.15s ease"
              }}
            >
              <div style={{ fontSize: "13px", fontWeight: 800, color: consensusStrategy === "average" ? "#CC4A1B" : "#1e293b" }}>
                📊 Average Satisfaction
              </div>
              <div style={{ fontSize: "11px", color: "#59615E", marginTop: "3px" }}>
                Maximizes cumulative group score across all recommendations.
              </div>
            </div>
          </div>
        </div>

        {/* Travel Pace */}
        <div style={{ marginBottom: "16px" }}>
          <div style={{ fontSize: "12px", fontWeight: 700, color: "#334155", marginBottom: "6px" }}>
            Daily Itinerary Pace:
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "8px" }}>
            {["Relaxed", "Moderate", "High Efficiency"].map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => setPace(p)}
                style={{
                  padding: "8px 6px",
                  borderRadius: "10px",
                  fontSize: "12px",
                  fontWeight: pace === p ? 700 : 500,
                  border: pace === p ? "2px solid #E85D2A" : "1px solid #cbd5e1",
                  background: pace === p ? "#FFF0EA" : "#ffffff",
                  color: pace === p ? "#CC4A1B" : "#475569",
                  cursor: "pointer"
                }}
              >
                {p === "Relaxed" && "🌿 Relaxed (2/day)"}
                {p === "Moderate" && "⚡ Moderate (3/day)"}
                {p === "High Efficiency" && "🚀 High (4/day)"}
              </button>
            ))}
          </div>
        </div>

        {/* Anti-Overtourism Hidden Gems Toggle */}
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "10px 12px",
          background: "#fafaf9",
          borderRadius: "10px",
          border: "1px solid #e7e5e4"
        }}>
          <div>
            <div style={{ fontSize: "12px", fontWeight: 700, color: "#292524" }}>
              ✨ Anti-Overtourism Hidden Gems Boost
            </div>
            <div style={{ fontSize: "11px", color: "#78716c" }}>
              Applies algorithmic boost to uncrowded cultural landmarks
            </div>
          </div>
          <input
            type="checkbox"
            checked={promoteHiddenGems}
            onChange={(e) => setPromoteHiddenGems(e.target.checked)}
            style={{ width: "18px", height: "18px", cursor: "pointer", accentColor: "#E85D2A" }}
          />
        </div>
      </div>

      {/* Main Action Button */}
      <button
        onClick={onGeneratePlan}
        disabled={isLoading}
        style={{
          width: "100%",
          background: "linear-gradient(135deg, #E85D2A 0%, #CC4A1B 100%)",
          color: "#ffffff",
          border: "none",
          padding: "16px",
          borderRadius: "16px",
          fontSize: "15px",
          fontWeight: 800,
          cursor: isLoading ? "not-allowed" : "pointer",
          boxShadow: "0 6px 20px rgba(79, 70, 229, 0.35)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "8px",
          transition: "transform 0.15s ease"
        }}
      >
        <Sparkles size={18} />
        {isLoading ? "Running Group Consensus & TSP Optimizer..." : "Generate Group Travel Plan 🚀"}
      </button>
    </div>
  );
}
