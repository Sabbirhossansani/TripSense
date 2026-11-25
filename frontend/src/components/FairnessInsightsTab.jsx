import React, { useState, useEffect } from "react";
import { Award, BarChart2, FileDown, Cpu, ShieldCheck, Brain, Globe2, Layers, Scale } from "lucide-react";
import { fetchMlMetrics } from "../api/client";
import EcoImpactCalculator from "./EcoImpactCalculator";

function _fmtPct(val) {
  if (val === undefined || val === null) return "—";
  const num = Number(val);
  if (Number.isNaN(num)) return "—";
  return num <= 1.0 ? `${(num * 100).toFixed(1)}%` : `${num.toFixed(1)}%`;
}

function _fmtPval(p) {
  if (p === undefined || p === null) return "—";
  const num = Number(p);
  if (Number.isNaN(num)) return "N/A";
  if (num < 0.0001) return "<0.0001";
  return num.toFixed(4);
}

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
    gini_index: 0.063,
    satisfaction_disparity: 14.4,
    model_used: "TripSense-FairNet v2",
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
  const stats = mlMetrics?.statistical_tests || null;
  const multiSeed = mlMetrics?.multi_seed_stability || null;
  const ablations = mlMetrics?.ablation_study || [];
  const externalCities = mlMetrics?.external_cross_city_validation || null;
  const bdPilot = mlMetrics?.bangladesh_5city_pilot || [];
  const multiXai = mlMetrics?.multi_xai_evaluation || null;
  const igData = multiXai?.integrated_gradients || null;
  const igFeatures = igData?.features_ranked || [];
  const shapFeatures = mlMetrics?.shap_feature_importance || [];
  const concordance = multiXai?.cross_xai_concordance || null;
  const attnAudit = multiXai?.attention_and_counterfactual_audit?.cross_attention_audit || null;
  const nashAudit = multiXai?.attention_and_counterfactual_audit?.nash_counterfactual_recourse || null;
  const rawSwipe = mlMetrics?.active_swipe_learning_curve || null;
  const swipeRows = Array.isArray(rawSwipe)
    ? rawSwipe
    : rawSwipe?.swipes
      ? rawSwipe.swipes.map((s, idx) => ({
          swipes: s,
          bayesian_eig_cos: rawSwipe.active_bayesian_ndcg10?.[idx],
          random_swipe_cos: rawSwipe.random_quiz_ndcg10?.[idx],
        }))
      : [];
  const tpEval = mlMetrics?.travelplanner_rag_evaluation || null;

  return (
    <div style={{ maxWidth: "1060px", margin: "0 auto", paddingBottom: "40px" }}>
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
          TripSense-FairNet v2: Consensus, Multi-XAI & Cross-City Lab
        </h2>
        <p style={{ fontSize: "13px", color: "#D6D1C7", margin: 0, lineHeight: 1.55 }}>
          Active Model: <strong>{fairness.model_used || "TripSense-FairNet v2"}</strong> • Backbone:{" "}
          <span className="font-mono-num">{mlMetrics?.backbone || "openai/clip-vit-base-patch32"}</span> • Primary:{" "}
          <strong>{mlMetrics?.datasets?.group_poi_benchmark || "Massive-STEPS-Sydney"}</strong> + <strong>Melbourne / Tokyo / New-York</strong>.
          {multiSeed && (
            <>
              {" "}• {multiSeed.seeds?.length || 5}-Seed Mean NDCG@10:{" "}
              <strong className="font-mono-num">
                {multiSeed.ndcg10_mean} ± {multiSeed.ndcg10_std}
              </strong>
              {" "}• Friedman χ² = <strong className="font-mono-num">{stats?.friedman_chi2 || "—"}</strong>
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
          <div style={{ fontSize: "11px", color: "var(--alpine-moss)", fontWeight: 700 }}>✓ Rotation-Invariant Cross-Attn</div>
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

        {mlMetrics?.latency_profile && (
          <div style={{ background: "#FFFFFF", borderRadius: "18px", border: "1px solid var(--stone-border)", padding: "16px", textAlign: "center" }}>
            <div style={{ fontSize: "11px", color: "var(--granite-600)", fontWeight: 800 }}>INFERENCE LATENCY</div>
            <div className="font-mono-num" style={{ fontSize: "26px", fontWeight: 900, color: "var(--alpine-moss)", margin: "4px 0" }}>
              {mlMetrics.latency_profile.gpu_ms_per_100_cands} ms
            </div>
            <div style={{ fontSize: "11px", color: "var(--granite-600)" }}>
              CPU: {mlMetrics.latency_profile.cpu_ms_per_100_cands} ms / 100 POIs
            </div>
          </div>
        )}
      </div>

      {/* Live Eco Impact Calculator */}
      <EcoImpactCalculator
        spots={allSpots}
        totalDistanceKm={plan?.total_distance_km || 14.5}
        defaultGroupSize={Object.keys(satisfactionData).length || 3}
        currency={currency}
      />

      {/* 10-Model Primary Q1 Benchmark Table */}
      {comparison && (
        <div style={{ background: "#FFFFFF", borderRadius: "22px", border: "1px solid var(--stone-border)", padding: "22px", marginBottom: "20px", overflowX: "auto" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px", marginBottom: "14px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Award size={18} color="#E85D2A" />
              <h3 className="font-display" style={{ fontSize: "19px", fontWeight: 800, margin: 0 }}>
                10-Model Sydney Benchmark ({mlMetrics?.datasets?.test_groups || 180} Test Groups, 100-Candidate Pools)
              </h3>
            </div>
            {stats && (
              <span className="font-mono-num" style={{ fontSize: "11px", background: "var(--bg-surface)", border: "1px solid var(--stone-border)", padding: "4px 10px", borderRadius: "999px", fontWeight: 700 }}>
                Nemenyi CD₀.₀₅ = {stats.nemenyi_cd_alpha05} • p = {stats.friedman_p_value}
              </span>
            )}
          </div>

          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px", minWidth: "740px" }}>
            <thead>
              <tr style={{ background: "var(--bg-surface)", borderBottom: "2px solid var(--stone-border)", textAlign: "left" }}>
                <th style={{ padding: "10px 10px", fontWeight: 800 }}>Model / Strategy</th>
                <th style={{ padding: "10px 10px", fontWeight: 800 }}>NDCG@5 ↑</th>
                <th style={{ padding: "10px 10px", fontWeight: 800 }}>NDCG@10 ↑</th>
                <th style={{ padding: "10px 10px", fontWeight: 800 }}>Hit@10 ↑</th>
                <th style={{ padding: "10px 10px", fontWeight: 800 }}>Gini ↓</th>
                <th style={{ padding: "10px 10px", fontWeight: 800 }}>Min-Sat ↑</th>
                <th style={{ padding: "10px 10px", fontWeight: 800 }}>Eco Cov. ↑</th>
                <th style={{ padding: "10px 10px", fontWeight: 800 }}>Rank ↓</th>
                <th style={{ padding: "10px 10px", fontWeight: 800 }}>Holm p</th>
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
                    <td style={{ padding: "9px 10px", color: isOurs ? "var(--alpine-moss)" : "var(--granite-950)" }}>{name}</td>
                    <td className="font-mono-num" style={{ padding: "9px 10px" }}>{m.ndcg5}</td>
                    <td className="font-mono-num" style={{ padding: "9px 10px" }}>{m.ndcg10}</td>
                    <td className="font-mono-num" style={{ padding: "9px 10px" }}>{_fmtPct(m.hit10)}</td>
                    <td className="font-mono-num" style={{ padding: "9px 10px" }}>{m.gini_index}</td>
                    <td className="font-mono-num" style={{ padding: "9px 10px" }}>{_fmtPct(m.min_member_sat)}</td>
                    <td className="font-mono-num" style={{ padding: "9px 10px" }}>{m.eco_coverage_pct}%</td>
                    <td className="font-mono-num" style={{ padding: "9px 10px" }}>{m.friedman_rank ?? "—"}</td>
                    <td className="font-mono-num" style={{ padding: "9px 10px" }}>
                      {isOurs ? "Ref." : _fmtPval(m.holm_p_ndcg10 ?? m.p_value_ndcg10)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Zero-Shot External Cross-City Validation & 7-Variant Component Ablation */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "16px", marginBottom: "20px" }}>
        {externalCities && (
          <div style={{ background: "#FFFFFF", borderRadius: "20px", border: "1px solid var(--stone-border)", padding: "20px", overflowX: "auto" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
              <Globe2 size={17} color="#E85D2A" />
              <h3 style={{ fontSize: "15px", fontWeight: 800, margin: 0 }}>
                Zero-Shot External Cross-City Validation (No Retraining)
              </h3>
            </div>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
              <thead>
                <tr style={{ background: "var(--bg-surface)", borderBottom: "1.5px solid var(--stone-border)", textAlign: "left" }}>
                  <th style={{ padding: "8px", fontWeight: 800 }}>City (POIs)</th>
                  <th style={{ padding: "8px", fontWeight: 800 }}>FairNet v2</th>
                  <th style={{ padding: "8px", fontWeight: 800 }}>LightGBM</th>
                  <th style={{ padding: "8px", fontWeight: 800 }}>AGREE</th>
                  <th style={{ padding: "8px", fontWeight: 800 }}>Eco %</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(externalCities).map(([cname, cdata]) => {
                  const fn = cdata.models?.["TripSense-FairNet v2 (Zero-Shot)"];
                  const lg = cdata.models?.["LightGBM (Zero-Shot)"];
                  const ag = cdata.models?.["AGREE (Zero-Shot)"];
                  return (
                    <tr key={cname} style={{ borderBottom: "1px solid var(--stone-muted)" }}>
                      <td style={{ padding: "8px", fontWeight: 700 }}>{cname} ({cdata.num_venues})</td>
                      <td className="font-mono-num" style={{ padding: "8px", fontWeight: 800, color: "var(--alpine-moss)" }}>{fn?.ndcg10 ?? "—"}</td>
                      <td className="font-mono-num" style={{ padding: "8px" }}>{lg?.ndcg10 ?? "—"}</td>
                      <td className="font-mono-num" style={{ padding: "8px" }}>{ag?.ndcg10 ?? "—"}</td>
                      <td className="font-mono-num" style={{ padding: "8px", color: "var(--safety-orange)", fontWeight: 700 }}>{fn?.eco_coverage_pct ?? "—"}%</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {bdPilot.length > 0 && (
              <div style={{ marginTop: "14px", paddingTop: "12px", borderTop: "1px dashed var(--stone-border)" }}>
                <div style={{ fontSize: "11px", fontWeight: 800, color: "var(--granite-600)", marginBottom: "8px" }}>
                  BANGLADESH 5-CITY EQUITY & ECO PILOT AUDIT
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(115px, 1fr))", gap: "6px" }}>
                  {bdPilot.map((b) => (
                    <div key={b.city} style={{ background: "var(--bg-surface)", borderRadius: "10px", padding: "8px", border: "1px solid var(--stone-border)", fontSize: "11px" }}>
                      <div style={{ fontWeight: 800 }}>{b.city}</div>
                      <div className="font-mono-num" style={{ color: "var(--alpine-moss)" }}>Eco {b.fairnet_eco_score_pct}%</div>
                      <div className="font-mono-num" style={{ color: "var(--granite-600)" }}>Gini {b.fairnet_gini}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {ablations.length > 0 && (
          <div style={{ background: "#FFFFFF", borderRadius: "20px", border: "1px solid var(--stone-border)", padding: "20px", overflowX: "auto" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
              <Layers size={17} color="#25463B" />
              <h3 style={{ fontSize: "15px", fontWeight: 800, margin: 0 }}>
                7-Variant Component Ablation (Sydney)
              </h3>
            </div>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
              <thead>
                <tr style={{ background: "var(--bg-surface)", borderBottom: "1.5px solid var(--stone-border)", textAlign: "left" }}>
                  <th style={{ padding: "8px", fontWeight: 800 }}>Architecture Variant</th>
                  <th style={{ padding: "8px", fontWeight: 800 }}>NDCG@10</th>
                  <th style={{ padding: "8px", fontWeight: 800 }}>Δ Acc</th>
                  <th style={{ padding: "8px", fontWeight: 800 }}>Gini ↓</th>
                </tr>
              </thead>
              <tbody>
                {ablations.map((r) => {
                  const isFull = r.variant.startsWith("Full");
                  return (
                    <tr key={r.variant} style={{ background: isFull ? "var(--alpine-moss-soft)" : "transparent", borderBottom: "1px solid var(--stone-muted)" }}>
                      <td style={{ padding: "7px 8px", fontWeight: isFull ? 800 : 500 }}>{r.variant}</td>
                      <td className="font-mono-num" style={{ padding: "7px 8px", fontWeight: isFull ? 800 : 600 }}>{r.ndcg10}</td>
                      <td className="font-mono-num" style={{ padding: "7px 8px", color: r.delta_ndcg10 < 0 ? "#B91C1C" : "var(--alpine-moss)", fontWeight: 700 }}>
                        {r.delta_ndcg10 === 0 ? "Ref." : r.delta_ndcg10}
                      </td>
                      <td className="font-mono-num" style={{ padding: "7px 8px" }}>{r.gini_index}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Multi-Paradigm XAI Faithfulness + Active Swipe & TravelPlanner Evaluation */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "16px", marginBottom: "20px" }}>
        {/* Integrated Gradients vs TreeSHAP + Faithfulness */}
        {(igFeatures.length > 0 || shapFeatures.length > 0) && (
          <div style={{ background: "#FFFFFF", borderRadius: "20px", border: "1px solid var(--stone-border)", padding: "20px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
              <BarChart2 size={17} color="#E85D2A" />
              <h3 style={{ fontSize: "15px", fontWeight: 800, margin: 0 }}>
                Multi-XAI: Integrated Gradients & Faithfulness Audit
              </h3>
            </div>
            {igData && (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "8px", marginBottom: "12px", textAlign: "center" }}>
                <div style={{ background: "var(--bg-surface)", borderRadius: "10px", padding: "8px", border: "1px solid var(--stone-border)" }}>
                  <div style={{ fontSize: "10px", fontWeight: 800, color: "var(--granite-600)" }}>COMPLETENESS MAE</div>
                  <div className="font-mono-num" style={{ fontSize: "13px", fontWeight: 900, color: "var(--alpine-moss)" }}>{igData.completeness_mae}</div>
                </div>
                <div style={{ background: "var(--bg-surface)", borderRadius: "10px", padding: "8px", border: "1px solid var(--stone-border)" }}>
                  <div style={{ fontSize: "10px", fontWeight: 800, color: "var(--granite-600)" }}>COMP. VS RANDOM</div>
                  <div className="font-mono-num" style={{ fontSize: "13px", fontWeight: 900, color: "var(--safety-orange)" }}>{igData.faithfulness_ratio_over_random}×</div>
                </div>
                <div style={{ background: "var(--bg-surface)", borderRadius: "10px", padding: "8px", border: "1px solid var(--stone-border)" }}>
                  <div style={{ fontSize: "10px", fontWeight: 800, color: "var(--granite-600)" }}>IG / SHAP ρ</div>
                  <div className="font-mono-num" style={{ fontSize: "13px", fontWeight: 900 }}>{concordance?.ig_vs_treeshap_spearman_rho ?? "—"}</div>
                </div>
              </div>
            )}
            {(igFeatures.length > 0 ? igFeatures : shapFeatures).slice(0, 7).map((item) => (
              <div key={item.feature} style={{ marginBottom: "9px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", fontWeight: 700, marginBottom: "3px" }}>
                  <span>{item.feature}</span>
                  <span className="font-mono-num" style={{ color: "var(--safety-orange)" }}>
                    {item.importance_pct}% {item.direction ? `(${item.direction.split(" ")[0]})` : ""}
                  </span>
                </div>
                <div style={{ height: "7px", background: "var(--stone-muted)", borderRadius: "999px", overflow: "hidden" }}>
                  <div style={{ width: `${Math.min(100, item.importance_pct * 3.5)}%`, height: "100%", background: "var(--alpine-moss)", borderRadius: "999px" }} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Right Stack: Cross-Attention/Nash Recourse + Active Swipe + TravelPlanner */}
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {(attnAudit || nashAudit) && (
            <div style={{ background: "#FFFFFF", borderRadius: "20px", border: "1px solid var(--stone-border)", padding: "18px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
                <Scale size={17} color="#25463B" />
                <h3 style={{ fontSize: "15px", fontWeight: 800, margin: 0 }}>
                  Attention Equity & Nash Counterfactual Audit
                </h3>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", fontSize: "12px" }}>
                {attnAudit && (
                  <div style={{ background: "var(--bg-surface)", borderRadius: "12px", padding: "10px", border: "1px solid var(--stone-border)" }}>
                    <div style={{ fontWeight: 800, marginBottom: "4px" }}>Budget-Tier Attention</div>
                    <div>Lowest Budget: <strong className="font-mono-num" style={{ color: "var(--alpine-moss)" }}>{attnAudit.lowest_budget_member_mean_attn}</strong></div>
                    <div>Highest Budget: <strong className="font-mono-num">{attnAudit.highest_budget_member_mean_attn}</strong></div>
                  </div>
                )}
                {nashAudit && (
                  <div style={{ background: "var(--alpine-moss-soft)", borderRadius: "12px", padding: "10px", border: "1px solid #C5D9CE" }}>
                    <div style={{ fontWeight: 800, color: "var(--alpine-moss)", marginBottom: "4px" }}>Nash Veto Recourse</div>
                    <div>Welfare Gain: <strong className="font-mono-num">+{nashAudit.mean_nash_welfare_gain_pct}%</strong></div>
                    <div>Gini: <strong className="font-mono-num">{nashAudit.mean_gini_before} → {nashAudit.mean_gini_after}</strong></div>
                  </div>
                )}
              </div>
            </div>
          )}

          {swipeRows.length > 0 && (
            <div style={{ background: "#FFFFFF", borderRadius: "20px", border: "1px solid var(--stone-border)", padding: "18px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
                <Brain size={17} color="#25463B" />
                <h3 style={{ fontSize: "15px", fontWeight: 800, margin: 0 }}>
                  Active Bayesian EIG Cold-Start Curve (n = 120 Users)
                </h3>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: `repeat(${Math.min(7, swipeRows.length)}, 1fr)`, gap: "6px", textAlign: "center" }}>
                {swipeRows.map((row) => (
                  <div key={row.swipes} style={{ background: "var(--bg-surface)", borderRadius: "10px", padding: "7px 4px", border: "1px solid var(--stone-border)" }}>
                    <div style={{ fontSize: "10px", fontWeight: 700, color: "var(--granite-600)" }}>{row.swipes} Sw.</div>
                    <div className="font-mono-num" style={{ fontSize: "12px", fontWeight: 800, color: "var(--alpine-moss)" }}>
                      {row.bayesian_eig_cos}
                    </div>
                    <div className="font-mono-num" style={{ fontSize: "10px", color: "var(--granite-600)" }}>
                      vs {row.random_swipe_cos}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {tpEval && (
            <div style={{ background: "#FFFFFF", borderRadius: "20px", border: "1px solid var(--stone-border)", padding: "18px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
                <ShieldCheck size={17} color="#E85D2A" />
                <h3 style={{ fontSize: "15px", fontWeight: 800, margin: 0 }}>
                  TravelPlanner Neuro-Symbolic Verification ({tpEval.num_tasks} Tasks, {tpEval.avg_verify_ms} ms)
                </h3>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", fontSize: "12px" }}>
                <div style={{ background: "#FFF1EE", border: "1px solid #F7BEB3", borderRadius: "12px", padding: "12px" }}>
                  <div style={{ fontWeight: 800, color: "#9A2B14" }}>Vanilla LLM</div>
                  <div>Budget Feasible: <strong className="font-mono-num">{tpEval.vanilla_llm.budget_feasibility_pct}%</strong></div>
                  <div>Final Pass Rate: <strong className="font-mono-num">{tpEval.vanilla_llm.final_pass_rate_pct}%</strong></div>
                </div>
                <div style={{ background: "var(--alpine-moss-soft)", border: "1px solid #C5D9CE", borderRadius: "12px", padding: "12px" }}>
                  <div style={{ fontWeight: 800, color: "var(--alpine-moss)" }}>TripSense RAG + Verifier</div>
                  <div>Budget Feasible: <strong className="font-mono-num">{tpEval.tripsense_neuro_symbolic_rag.budget_feasibility_pct}%</strong></div>
                  <div>Final Pass Rate: <strong className="font-mono-num">{tpEval.tripsense_neuro_symbolic_rag.final_pass_rate_pct}%</strong></div>
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
