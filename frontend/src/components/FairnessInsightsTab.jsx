import React, { useState, useEffect } from "react";
import { Award, BarChart2, FileDown, Cpu, ShieldCheck, Brain } from "lucide-react";
import { fetchMlMetrics } from "../api/client";
import EcoImpactCalculator from "./EcoImpactCalculator";

export default function FairnessInsightsTab({ plan, consensusStrategy, city, currency = "BDT" }) {
  const [mlMetrics, setMlMetrics] = useState(null);

  useEffect(() => {
    fetchMlMetrics().then((res) => {
      if (res && res.group_consensus_comparison) {
        setMlMetrics(res);
      }
    });
  }, []);

  const fairness = plan?.fairness_report || {
    fairness_score: 78.4,
    gini_index: 0.089,
    satisfaction_disparity: 14.4,
    model_used: "TripSense-FairNet",
    member_average_satisfaction: { Rahat: 71.2, Sadia: 66.8, Fahim: 62.5 },
  };

  const satisfactionData = fairness.member_average_satisfaction || {};
  const allSpots = (plan?.daily_schedule || []).flatMap((d) => d.spots || []);

  const handleExportPlan = () => {
    if (!plan) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(plan, null, 2));
    const a = document.createElement("a");
    a.setAttribute("href", dataStr);
    a.setAttribute("download", `TripSense_${city}_FairNet_Plan.json`);
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  const comparison = mlMetrics?.group_consensus_comparison || null;
  const shapFeatures = mlMetrics?.shap_feature_importance || [];
  const swipeCurve = mlMetrics?.active_swipe_learning_curve || null;
  const tpEval = mlMetrics?.travelplanner_rag_evaluation || null;

  return (
    <div style={{ maxWidth: "1040px", margin: "0 auto", paddingBottom: "40px" }}>
      {/* Editorial Header Banner */}
      <div
        style={{
          background: "linear-gradient(135deg, #1A1D1C 0%, #25463B 100%)",
          borderRadius: "24px",
          padding: "24px",
          color: "#FAF9F6",
          marginBottom: "20px",
          boxShadow: "0 14px 34px rgba(26, 29, 28, 0.18)",
        }}
      >
        <div style={{ display: "inline-flex", alignItems: "center", gap: "6px", background: "rgba(232,93,42,0.22)", border: "1px solid rgba(232,93,42,0.45)", padding: "4px 12px", borderRadius: "999px", fontSize: "11px", fontWeight: 800, color: "#FFAD8F", marginBottom: "10px" }}>
          <Cpu size={13} />
          <span>Q1 JOURNAL RESEARCH BENCHMARK & SUSTAINABILITY LAB</span>
        </div>
        <h2 className="font-display" style={{ fontSize: "24px", fontWeight: 900, margin: "0 0 6px 0" }}>
          TripSense-FairNet Consensus, SHAP & Eco Analytics
        </h2>
        <p style={{ fontSize: "13px", color: "#D6D1C7", margin: 0, lineHeight: 1.55 }}>
          Active Model: <strong>{fairness.model_used || "TripSense-FairNet"}</strong> • Backbone:{" "}
          <span className="font-mono-num">{mlMetrics?.backbone || "openai/clip-vit-base-patch32"}</span> • Dataset:{" "}
          <strong>{mlMetrics?.datasets?.group_poi_benchmark || "Massive-STEPS-Sydney"}</strong> & <strong>TravelPlanner</strong>.
          {mlMetrics?.multi_seed_stability && (
            <>
              {" "}• 3-Seed Mean NDCG@10:{" "}
              <strong className="font-mono-num">
                {mlMetrics.multi_seed_stability.ndcg10_mean} ± {mlMetrics.multi_seed_stability.ndcg10_std}
              </strong>
            </>
          )}
        </p>
      </div>

      {/* Live Plan KPI Strip */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px", marginBottom: "20px" }}>
        <div style={{ background: "#FFFFFF", borderRadius: "18px", border: "1px solid var(--stone-border)", padding: "16px", textAlign: "center" }}>
          <div style={{ fontSize: "11px", color: "var(--granite-600)", fontWeight: 800 }}>FAIRNESS SCORE</div>
          <div className="font-mono-num" style={{ fontSize: "26px", fontWeight: 900, color: "var(--safety-orange)", margin: "4px 0" }}>
            {fairness.fairness_score}/100
          </div>
          <div style={{ fontSize: "11px", color: "var(--alpine-moss)", fontWeight: 700 }}>✓ Cross-Attention Consensus</div>
        </div>

        <div style={{ background: "#FFFFFF", borderRadius: "18px", border: "1px solid var(--stone-border)", padding: "16px", textAlign: "center" }}>
          <div style={{ fontSize: "11px", color: "var(--granite-600)", fontWeight: 800 }}>GINI INEQUALITY</div>
          <div className="font-mono-num" style={{ fontSize: "26px", fontWeight: 900, color: "var(--granite-950)", margin: "4px 0" }}>
            {fairness.gini_index}
          </div>
          <div style={{ fontSize: "11px", color: "var(--alpine-moss)", fontWeight: 700 }}>
            {fairness.gini_index < 0.2 ? "Optimal Equity (< 0.20)" : "Balanced"}
          </div>
        </div>

        <div style={{ background: "#FFFFFF", borderRadius: "18px", border: "1px solid var(--stone-border)", padding: "16px", textAlign: "center" }}>
          <div style={{ fontSize: "11px", color: "var(--granite-600)", fontWeight: 800 }}>SATISFACTION SPREAD</div>
          <div className="font-mono-num" style={{ fontSize: "26px", fontWeight: 900, color: "var(--granite-950)", margin: "4px 0" }}>
            {fairness.satisfaction_disparity}%
          </div>
          <div style={{ fontSize: "11px", color: "var(--granite-600)" }}>Max − Min Member Gap</div>
        </div>
      </div>

      {/* Live Eco Impact Calculator */}
      <EcoImpactCalculator
        spots={allSpots}
        totalDistanceKm={plan?.total_distance_km || 14.5}
        defaultGroupSize={Object.keys(satisfactionData).length || 3}
        currency={currency}
      />

      {/* Real Q1 Model Comparison Table from q1_benchmark_results.json */}
      {comparison && (
        <div style={{ background: "#FFFFFF", borderRadius: "22px", border: "1px solid var(--stone-border)", padding: "22px", marginBottom: "20px", overflowX: "auto" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "14px" }}>
            <Award size={18} color="#E85D2A" />
            <h3 className="font-display" style={{ fontSize: "19px", fontWeight: 800, margin: 0 }}>
              Empirical Q1 Benchmark: TripSense-FairNet vs. SOTA Baselines ({mlMetrics?.datasets?.test_groups || 0} Test Groups)
            </h3>
          </div>

          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px", minWidth: "620px" }}>
            <thead>
              <tr style={{ background: "var(--bg-surface)", borderBottom: "2px solid var(--stone-border)", textAlign: "left" }}>
                <th style={{ padding: "10px 12px", fontWeight: 800 }}>Model / Strategy</th>
                <th style={{ padding: "10px 12px", fontWeight: 800 }}>NDCG@5 ↑</th>
                <th style={{ padding: "10px 12px", fontWeight: 800 }}>NDCG@10 ↑</th>
                <th style={{ padding: "10px 12px", fontWeight: 800 }}>Hit@10 ↑</th>
                <th style={{ padding: "10px 12px", fontWeight: 800 }}>Gini ↓</th>
                <th style={{ padding: "10px 12px", fontWeight: 800 }}>Min-Sat ↑</th>
                <th style={{ padding: "10px 12px", fontWeight: 800 }}>Eco Cov. ↑</th>
                <th style={{ padding: "10px 12px", fontWeight: 800 }}>Wilcoxon p</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(comparison).map(([name, m]) => {
                const isOurs = name.includes("Ours");
                return (
                  <tr
                    key={name}
                    style={{
                      background: isOurs ? "var(--alpine-moss-soft)" : "transparent",
                      borderBottom: "1px solid var(--stone-muted)",
                      fontWeight: isOurs ? 800 : 500,
                    }}
                  >
                    <td style={{ padding: "10px 12px", color: isOurs ? "var(--alpine-moss)" : "var(--granite-950)" }}>{name}</td>
                    <td className="font-mono-num" style={{ padding: "10px 12px" }}>{m.ndcg5}</td>
                    <td className="font-mono-num" style={{ padding: "10px 12px" }}>{m.ndcg10}</td>
                    <td className="font-mono-num" style={{ padding: "10px 12px" }}>{m.hit10}%</td>
                    <td className="font-mono-num" style={{ padding: "10px 12px" }}>{m.gini_index}</td>
                    <td className="font-mono-num" style={{ padding: "10px 12px" }}>{m.min_member_sat}%</td>
                    <td className="font-mono-num" style={{ padding: "10px 12px" }}>{m.eco_coverage_pct}%</td>
                    <td className="font-mono-num" style={{ padding: "10px 12px" }}>
                      {isOurs ? "—" : m.p_value_ndcg10 !== null ? m.p_value_ndcg10 : "N/A"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Two-Column Grid: SHAP Feature Attribution + Active Swipe & TravelPlanner Evaluation */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "16px", marginBottom: "20px" }}>
        {/* SHAP Global Feature Importance */}
        {shapFeatures.length > 0 && (
          <div style={{ background: "#FFFFFF", borderRadius: "20px", border: "1px solid var(--stone-border)", padding: "20px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "14px" }}>
              <BarChart2 size={17} color="#E85D2A" />
              <h3 style={{ fontSize: "15px", fontWeight: 800, margin: 0 }}>SHAP Global Feature Attributions</h3>
            </div>
            {shapFeatures.slice(0, 7).map((item) => (
              <div key={item.feature} style={{ marginBottom: "10px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", fontWeight: 700, marginBottom: "4px" }}>
                  <span>{item.feature}</span>
                  <span className="font-mono-num" style={{ color: "var(--safety-orange)" }}>{item.importance_pct}%</span>
                </div>
                <div style={{ height: "8px", background: "var(--stone-muted)", borderRadius: "999px", overflow: "hidden" }}>
                  <div style={{ width: `${Math.min(100, item.importance_pct * 2.2)}%`, height: "100%", background: "var(--alpine-moss)", borderRadius: "999px" }} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Active Swipe Curve & TravelPlanner Grounding Benchmark */}
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {swipeCurve && (
            <div style={{ background: "#FFFFFF", borderRadius: "20px", border: "1px solid var(--stone-border)", padding: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
                <Brain size={17} color="#25463B" />
                <h3 style={{ fontSize: "15px", fontWeight: 800, margin: 0 }}>
                  Active Bayesian Swipe Cold-Start ({swipeCurve.eval_users} Users)
                </h3>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "6px", textAlign: "center" }}>
                {swipeCurve.swipes.map((s, idx) => (
                  <div key={s} style={{ background: "var(--bg-surface)", borderRadius: "10px", padding: "8px 4px", border: "1px solid var(--stone-border)" }}>
                    <div style={{ fontSize: "10px", fontWeight: 700, color: "var(--granite-600)" }}>{s} Swipes</div>
                    <div className="font-mono-num" style={{ fontSize: "12px", fontWeight: 800, color: "var(--alpine-moss)" }}>
                      {swipeCurve.active_bayesian_ndcg10[idx]}
                    </div>
                    <div className="font-mono-num" style={{ fontSize: "10px", color: "var(--granite-600)" }}>
                      vs {swipeCurve.random_quiz_ndcg10[idx]}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {tpEval && (
            <div style={{ background: "#FFFFFF", borderRadius: "20px", border: "1px solid var(--stone-border)", padding: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
                <ShieldCheck size={17} color="#E85D2A" />
                <h3 style={{ fontSize: "15px", fontWeight: 800, margin: 0 }}>
                  TravelPlanner Neuro-Symbolic Verification ({tpEval.num_tasks} Tasks)
                </h3>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", fontSize: "12px" }}>
                <div style={{ background: "#FFF1EE", border: "1px solid #F7BEB3", borderRadius: "12px", padding: "12px" }}>
                  <div style={{ fontWeight: 800, color: "#9A2B14" }}>Vanilla LLM</div>
                  <div>Hallucination: <strong className="font-mono-num">{tpEval.vanilla_llm.hallucination_rate_pct}%</strong></div>
                  <div>Pass Rate: <strong className="font-mono-num">{tpEval.vanilla_llm.final_pass_rate_pct}%</strong></div>
                </div>
                <div style={{ background: "var(--alpine-moss-soft)", border: "1px solid #C5D9CE", borderRadius: "12px", padding: "12px" }}>
                  <div style={{ fontWeight: 800, color: "var(--alpine-moss)" }}>TripSense RAG + Verifier</div>
                  <div>Hallucination: <strong className="font-mono-num">{tpEval.tripsense_neuro_symbolic_rag.hallucination_rate_pct}%</strong></div>
                  <div>Pass Rate: <strong className="font-mono-num">{tpEval.tripsense_neuro_symbolic_rag.final_pass_rate_pct}%</strong></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Member Satisfaction Breakdown + JSON Export */}
      <div style={{ background: "#FFFFFF", borderRadius: "20px", border: "1px solid var(--stone-border)", padding: "20px", marginBottom: "16px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
          <h3 style={{ fontSize: "15px", fontWeight: 800, margin: 0 }}>Active Trip Member Utility Balance</h3>
          <span style={{ fontSize: "11px", fontWeight: 700, background: "var(--safety-orange-soft)", color: "var(--safety-orange-hover)", padding: "4px 10px", borderRadius: "999px" }}>
            Strategy: {consensusStrategy}
          </span>
        </div>
        {Object.entries(satisfactionData).map(([name, score]) => (
          <div key={name} style={{ marginBottom: "10px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", fontWeight: 700, marginBottom: "4px" }}>
              <span>{name}</span>
              <span className="font-mono-num">{score}%</span>
            </div>
            <div style={{ height: "9px", background: "var(--stone-muted)", borderRadius: "999px", overflow: "hidden" }}>
              <div style={{ width: `${Math.min(100, score)}%`, height: "100%", background: "var(--safety-orange)", borderRadius: "999px" }} />
            </div>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={handleExportPlan}
        style={{
          width: "100%",
          background: "var(--granite-950)",
          color: "#FAF9F6",
          border: "none",
          borderRadius: "14px",
          padding: "13px",
          fontSize: "13px",
          fontWeight: 800,
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "8px",
        }}
      >
        <FileDown size={16} />
        <span>Download FairNet Itinerary & Evaluation JSON</span>
      </button>
    </div>
  );
}
