"""
Q1 Publication Figure Generator for TripSense-FairNet v2.
Produces 8 300-DPI PNG + vector PDF figures directly from
backend/ml/artifacts/q1_benchmark_results.json using pure Matplotlib.
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
METRICS_PATH = os.path.join(ROOT_DIR, "backend", "ml", "artifacts", "q1_benchmark_results.json")
OUT_DIR = os.path.join(ROOT_DIR, "docs", "q1_figures")
os.makedirs(OUT_DIR, exist_ok=True)

# Colorblind-safe Okabe-Ito inspired publication palette
C_OURS = "#0072B2"     # Deep ocean blue (TripSense-FairNet v2)
C_ECO = "#009E73"      # Forest emerald (Eco / Neuro-Symbolic)
C_LGBM = "#E69F00"     # Warm gold (LightGBM / GBDT)
C_AGREE = "#D55E00"    # Vermilion (AGREE SIGIR'18)
C_MLP = "#CC79A7"      # Muted plum (GroupMLP)
C_SLATE = "#64748B"    # Neutral slate (Heuristics)
C_SKY = "#56B4E9"      # Sky blue (Secondary bars)
C_DARK = "#0F172A"     # Deep ink

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Times New Roman", "serif"],
    "font.size": 9.5,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.labelsize": 9.5,
    "axes.edgecolor": "#CBD5E1",
    "axes.linewidth": 0.9,
    "axes.grid": True,
    "grid.color": "#E2E8F0",
    "grid.linestyle": "--",
    "grid.linewidth": 0.6,
    "grid.alpha": 0.75,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8.2,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.facecolor": "white",
})


def _save(fig, name: str):
    png = os.path.join(OUT_DIR, f"{name}.png")
    pdf = os.path.join(OUT_DIR, f"{name}.pdf")
    fig.savefig(png, bbox_inches="tight", dpi=300)
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"[Figure] Saved {name}.png & .pdf", flush=True)


def fig1_architecture_overview(data):
    fig, ax = plt.subplots(figsize=(12.2, 5.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    ax.axis("off")

    def box(x, y, w, h, title, body, fc="#F8FAFC", ec="#334155", tc=C_DARK, lw=1.4):
        p = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.2",
            facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2
        )
        ax.add_patch(p)
        ax.text(x + w / 2, y + h - 2.3, title, ha="center", va="top", fontsize=9.0, fontweight="bold", color=tc, zorder=3)
        ax.text(x + w / 2, y + h / 2 - 1.2, body, ha="center", va="center", fontsize=7.6, color="#334155", linespacing=1.35, zorder=3)

    def arrow(x1, y1, x2, y2, color="#475569"):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.4, shrinkA=2, shrinkB=2), zorder=4)

    ax.text(50, 48.2, "TripSense-FairNet v2: Rotation-Invariant Dual-Stream Fairness & Neuro-Symbolic Architecture",
            ha="center", va="center", fontsize=12.0, fontweight="bold", color=C_DARK)

    # Column 1: Inputs & CLIP
    box(2, 27, 20, 16.5, "Multimodal Inputs",
        "Group Profiles (|G| = 2..5)\nMember Taste History (72% Past)\nCandidate POI + 8-d Context\nCLIP ViT-B/32 (512-d) + Centr.",
        fc="#EFF6FF", ec=C_OURS)
    box(2, 5, 20, 16.5, "Active Bayesian EIG",
        "Cold-Start Preference Probe\nOrthogonal Info Gain Swipes\n12-Card Visual Gallery\n0 -> 6 Swipes Calibration",
        fc="#F0FDF4", ec=C_ECO)

    # Column 2: Dual Streams
    box(27.5, 27, 24.5, 16.5, "Stream 1: Hadamard Cross-Attn",
        "Rotation-Invariant Geo Tokens:\n[cos_u, Δmean, Δmin, coh, bg]\n+ 0.35*Tanh Hadamard Residual\n4-Head Cross-Attn + Soft-Min",
        fc="#F5F3FF", ec=C_MLP)
    box(27.5, 5, 24.5, 16.5, "Stream 2: 15-d Rel. Highway",
        "[cos_{mean,min,max,std}, bg,\n |G|/5, dist, price, pop, rating,\n indoor, hidden, eco, SME]\nResidual MLP + Linear Skip",
        fc="#FFFBEB", ec=C_LGBM)

    # Column 3: Additive Fusion + Multi-Objective Loss
    box(57.5, 16, 19, 27.5, "Additive Logit Fusion\n& Pareto InfoNCE",
        "Softplus Scales s1,s2,s3:\nScore = σ(s1·Attn + s2·Min\n          + s3·Rel + b)\n\nJoint Loss:\n• 20-Neg InfoNCE (τ=0.20)\n• Differentiable Gini + Slate\n• Least-Misery Safety Floor\n• Expected Eco-Exposure",
        fc="#ECFEFF", ec=C_OURS, lw=1.8)

    # Column 4: Multi-XAI & Neuro-Symbolic Output
    mae = data["multi_xai_evaluation"]["integrated_gradients"]["completeness_mae"]
    tp_feas = data["travelplanner_rag_evaluation"]["tripsense_neuro_symbolic_rag"]["budget_feasibility_pct"]
    nash_gain = data["multi_xai_evaluation"]["attention_and_counterfactual_audit"]["nash_counterfactual_recourse"]["mean_nash_welfare_gain_pct"]
    box(81, 27, 17, 16.5, "Multi-Paradigm XAI",
        f"32-Step IG (MAE={mae:.1e})\nComp/Suff + Permutation\nTreeSHAP Concordance\nAttn Budget Protection",
        fc="#FEF2F2", ec=C_AGREE)
    box(81, 5, 17, 16.5, "Nash Veto & Verifier",
        f"Nash Bargaining Recourse\n(Welfare Gain +{nash_gain:.2f}%)\nDeterministic CSP Audit\n(Budget Feas. {tp_feas:.0f}%)",
        fc="#F0FDF4", ec=C_ECO)

    arrow(22.6, 35.2, 27.0, 35.2, C_OURS)
    arrow(22.6, 31.0, 27.0, 14.5, C_LGBM)
    arrow(12.0, 22.1, 12.0, 26.4, C_ECO)
    arrow(52.6, 35.2, 57.0, 32.0, C_MLP)
    arrow(52.6, 13.5, 57.0, 24.0, C_LGBM)
    arrow(77.1, 34.0, 80.5, 35.2, C_AGREE)
    arrow(77.1, 21.0, 80.5, 13.5, C_ECO)

    _save(fig, "fig1_architecture_overview")


def fig2_model_benchmark_and_cd(data):
    comp = data["group_consensus_comparison"]
    items = sorted(comp.items(), key=lambda kv: kv[1]["ndcg10"])
    names = [k for k, _ in items]
    ndcgs = [v["ndcg10"] for _, v in items]
    err_low = [v["ndcg10"] - v["ndcg10_ci95"][0] for _, v in items]
    err_high = [v["ndcg10_ci95"][1] - v["ndcg10"] for _, v in items]

    colors = []
    for n in names:
        if "Ours" in n:
            colors.append(C_OURS)
        elif "LightGBM" in n or "HistGBDT" in n or "Random Forest" in n:
            colors.append(C_LGBM)
        elif "AGREE" in n or "GroupMLP" in n:
            colors.append(C_AGREE)
        else:
            colors.append(C_SLATE)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 4.9), gridspec_kw={"width_ratios": [1.35, 1.0]})

    # Panel A: Horizontal NDCG@10 with 95% Bootstrap CI
    y = np.arange(len(names))
    bars = ax1.barh(y, ndcgs, xerr=[err_low, err_high], color=colors, edgecolor="#1E293B", linewidth=0.6, capsize=3, height=0.68, alpha=0.92)
    ax1.set_yticks(y)
    ax1.set_yticklabels(names, fontweight="medium")
    ax1.set_xlabel("NDCG@10 on Held-Out Sydney Test Split (n = 180 groups, 95% Bootstrap CI)")
    ax1.set_title("(a) Group Ranking Accuracy Comparison (10 Models)")
    ax1.set_xlim(0, 0.68)
    for i, (val, bar) in enumerate(zip(ndcgs, bars)):
        suffix = " (Holm p≤0.0011 vs baselines)" if "Ours" in names[i] else f" (Hit@10={comp[names[i]]['hit10']:.3f})"
        ax1.text(val + err_high[i] + 0.008, bar.get_y() + bar.get_height() / 2,
                 f"{val:.4f}", va="center", ha="left", fontsize=8.0,
                 fontweight="bold" if "Ours" in names[i] else "normal",
                 color=C_OURS if "Ours" in names[i] else "#334155")

    # Panel B: Friedman Average Ranks + Nemenyi Critical Difference
    st = data["statistical_tests"]
    cd = st["nemenyi_cd_alpha05"]
    ranks_sorted = sorted(comp.items(), key=lambda kv: kv[1]["friedman_rank"])
    r_names = [k for k, _ in ranks_sorted]
    r_vals = [v["friedman_rank"] for _, v in ranks_sorted]
    r_cols = [C_OURS if "Ours" in n else (C_LGBM if any(x in n for x in ("LightGBM", "Forest", "Hist")) else (C_AGREE if any(x in n for x in ("AGREE", "MLP")) else C_SLATE)) for n in r_names]

    yr = np.arange(len(r_names))[::-1]
    ax2.hlines(yr, xmin=1.0, xmax=r_vals, color="#CBD5E1", linewidth=1.2, zorder=1)
    ax2.scatter(r_vals, yr, c=r_cols, s=75, edgecolors="#0F172A", linewidth=0.8, zorder=3)
    ax2.axvline(r_vals[0] + cd, color=C_OURS, linestyle=":", linewidth=1.3, label=f"Best + Nemenyi CD ({cd:.2f})")
    ax2.axvspan(r_vals[0], r_vals[0] + cd, color=C_OURS, alpha=0.07)

    # Top CD bar
    ax2.plot([r_vals[0], r_vals[0] + cd], [len(r_names) - 0.15, len(r_names) - 0.15], color=C_DARK, lw=2.0, marker="|", markersize=8)
    ax2.text(r_vals[0] + cd / 2, len(r_names) + 0.12, f"CD = {cd:.2f} (α = 0.05)", ha="center", va="bottom", fontsize=8.0, fontweight="bold")

    ax2.set_yticks(yr)
    ax2.set_yticklabels([f"{n} ({v:.2f})" for n, v in zip(r_names, r_vals)], fontsize=8.2)
    ax2.set_xlim(1.0, 9.0)
    ax2.set_ylim(-0.6, len(r_names) + 0.7)
    ax2.set_xlabel(f"Friedman Average Rank (lower is better; χ² = {st['friedman_chi2']:.1f}, p = {st['friedman_p_value']:.1e})")
    ax2.set_title("(b) Friedman-Nemenyi Post-Hoc Rank Diagram")
    ax2.legend(loc="lower right", frameon=True)

    fig.tight_layout(pad=1.4)
    _save(fig, "fig2_model_benchmark_and_cd")


def fig3_fairness_accuracy_pareto(data):
    comp = data["group_consensus_comparison"]
    pareto = data["pareto_gini_sweep"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.7))

    # Panel A: NDCG@10 vs Gini Index (ideal: top-left: high NDCG@10, low Gini)
    for mname, m in comp.items():
        if "Ours" in mname:
            continue
        marker = "s" if any(k in mname for k in ("LightGBM", "Forest", "Hist")) else ("^" if any(k in mname for k in ("AGREE", "MLP")) else "o")
        col = C_LGBM if marker == "s" else (C_AGREE if marker == "^" else C_SLATE)
        ax1.scatter(m["gini_index"], m["ndcg10"], s=70, color=col, marker=marker, edgecolors=C_DARK, linewidth=0.7, zorder=3)
        dx, dy, ha = 0.0005, 0.005, "left"
        if "LightGBM" in mname:
            dx, dy, ha = -0.0006, -0.015, "right"
        elif "HistGBDT" in mname:
            dx, dy, ha = 0.0005, -0.014, "left"
        elif "Random Forest" in mname:
            dx, dy, ha = 0.0005, 0.005, "left"
        elif "Least-Misery" in mname:
            dx, dy, ha = 0.0006, 0.004, "left"
        elif "Borda" in mname:
            dx, dy, ha = 0.0006, -0.004, "left"
        elif "Average Cosine" in mname:
            dx, dy, ha = -0.0006, 0.010, "right"
        ax1.text(m["gini_index"] + dx, m["ndcg10"] + dy, mname.replace(" (SIGIR'18)", ""), fontsize=7.5, color="#334155", ha=ha)

    px = [p["gini_index"] for p in pareto]
    py = [p["ndcg10"] for p in pareto]
    order = np.argsort(px)
    ax1.plot(np.array(px)[order], np.array(py)[order], color=C_OURS, lw=1.6, linestyle="--", alpha=0.75, label="FairNet v2 λ_gini Sweep")
    label_offsets = {
        0.0: (0.0022, -0.022, "left"),
        0.15: (-0.0024, -0.024, "right"),
        0.3: (0.0000, 0.018, "center"),
        0.65: (0.0024, 0.014, "left"),
        1.0: (-0.0020, 0.016, "right"),
    }
    for p in pareto:
        is_opt = abs(p["lambda_gini"] - 0.3) < 1e-4
        ax1.scatter(p["gini_index"], p["ndcg10"], s=165 if is_opt else 85,
                    color=C_OURS if is_opt else C_SKY, marker="*", edgecolors=C_DARK, linewidth=0.8, zorder=5)
        ox, oy, ha = label_offsets.get(round(p["lambda_gini"], 2), (0.0006, 0.008, "left"))
        ax1.annotate(
            f"λ={p['lambda_gini']:.2f}" + (" (Ours)" if is_opt else ""),
            xy=(p["gini_index"], p["ndcg10"]),
            xytext=(p["gini_index"] + ox, p["ndcg10"] + oy),
            fontsize=7.6,
            fontweight="bold" if is_opt else "normal",
            color=C_OURS if is_opt else "#1E293B",
            ha=ha,
            arrowprops=dict(arrowstyle="-", color="#94A3B8", lw=0.6) if not is_opt else None,
        )

    ax1.set_xlabel("Intra-Group Satisfaction Gini Index (lower = fairer)")
    ax1.set_ylabel("Group Ranking Accuracy (NDCG@10, higher = better)")
    ax1.set_title("(a) Accuracy vs. Fairness Pareto Frontier (Optimal: Top-Left)")
    ax1.set_xlim(0.0565, 0.0815)
    ax1.set_ylim(0.13, 0.595)
    ax1.legend(loc="lower right", frameon=True)

    # Panel B: Learned Models Multi-Metric Comparison (NDCG@10 vs Eco Coverage)
    learned = ["AGREE (SIGIR'18)", "HistGBDT", "Random Forest", "GroupMLP", "LightGBM GBDT", "TripSense-FairNet v2 (Ours)"]
    x = np.arange(len(learned))
    w = 0.36
    vals_ndcg = [comp[k]["ndcg10"] * 100.0 for k in learned]
    vals_eco = [comp[k]["eco_coverage_pct"] for k in learned]

    b1 = ax2.bar(x - w / 2, vals_ndcg, w, label="NDCG@10 (×100)", color=C_OURS, edgecolor=C_DARK, lw=0.6)
    b2 = ax2.bar(x + w / 2, vals_eco, w, label="Top-5 Eco Coverage (%)", color=C_ECO, edgecolor=C_DARK, lw=0.6)
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width() / 2, h + 0.9, f"{h:.1f}", ha="center", va="bottom", fontsize=7.5)

    ax2.set_xticks(x)
    ax2.set_xticklabels(["AGREE", "HistGBDT", "RF", "GroupMLP", "LightGBM", "FairNet v2\n(Ours)"], fontsize=8.2)
    ax2.set_ylabel("Score / Coverage Percentage (%)")
    ax2.set_title("(b) Accuracy–Sustainability Synergy Across Learned Models")
    ax2.set_ylim(0, 65)
    ax2.legend(loc="upper left", frameon=True)

    fig.tight_layout(pad=1.4)
    _save(fig, "fig3_fairness_accuracy_pareto")


def fig4_ablation_and_scaling(data):
    abl = data["ablation_study"]
    scl = data["group_size_scaling"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 4.8), gridspec_kw={"width_ratios": [1.25, 1.0]})

    # Panel A: 7-Variant Component Ablation
    variants = [r["variant"] for r in abl][::-1]
    ndcgs = [r["ndcg10"] for r in abl][::-1]
    deltas = [r["delta_ndcg10"] for r in abl][::-1]
    cols = [C_OURS if v.startswith("Full") else C_AGREE for v in variants]
    y = np.arange(len(variants))
    bars = ax1.barh(y, ndcgs, color=cols, edgecolor=C_DARK, lw=0.6, height=0.62, alpha=0.9)
    ax1.set_yticks(y)
    ax1.set_yticklabels(variants, fontsize=8.4)
    ax1.set_xlabel("Held-Out Sydney NDCG@10")
    ax1.set_title("(a) 7-Variant Component Ablation Study")
    ax1.set_xlim(0, 0.75)
    for bar, v, d in zip(bars, ndcgs, deltas):
        lbl = f"{v:.4f}" if d == 0 else f"{v:.4f} ({d:+.4f})"
        ax1.text(v + 0.008, bar.get_y() + bar.get_height() / 2, lbl,
                 va="center", ha="left", fontsize=7.9, fontweight="bold" if d == 0 else "normal")

    # Panel B: Group Size Scaling |G| in {2, 3, 4, 5}
    gs = [r["group_size"] for r in scl]
    ax2.plot(gs, [r["fairnet_ndcg10"] for r in scl], marker="o", lw=2.2, color=C_OURS, label="TripSense-FairNet v2 (Ours)")
    ax2.plot(gs, [r["lgbm_ndcg10"] for r in scl], marker="s", lw=1.8, linestyle="--", color=C_LGBM, label="LightGBM GBDT")
    ax2.plot(gs, [r["agree_ndcg10"] for r in scl], marker="^", lw=1.8, linestyle=":", color=C_AGREE, label="AGREE (SIGIR'18)")
    for r in scl:
        dy = -0.025 if r["group_size"] == 5 else 0.013
        ax2.text(r["group_size"], r["fairnet_ndcg10"] + dy, f"{r['fairnet_ndcg10']:.3f}", ha="center", fontsize=7.8, fontweight="bold", color=C_OURS)

    ax2.set_xticks(gs)
    ax2.set_xticklabels([f"|G| = {g}\n(n={r['num_groups']})" for g, r in zip(gs, scl)])
    ax2.set_ylabel("NDCG@10 Across Group Sizes")
    ax2.set_title("(b) Scalability Across Group Cardinality |G| = 2..5")
    ax2.set_ylim(0.32, 0.66)
    ax2.legend(loc="lower left", frameon=True)

    fig.tight_layout(pad=1.4)
    _save(fig, "fig4_ablation_and_scaling")


def fig5_cross_city_transfer(data):
    ext = data["external_cross_city_validation"]
    syd = data["group_consensus_comparison"]
    bd = data["bangladesh_5city_pilot"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 4.8), gridspec_kw={"width_ratios": [1.3, 1.0]})

    # Panel A: Zero-Shot Cross-City NDCG@10 (Sydney in-domain + Melbourne/Tokyo/New-York zero-shot)
    cities = ["Sydney\n(In-Domain)", "Melbourne\n(Zero-Shot)", "Tokyo\n(Zero-Shot)", "New-York\n(Zero-Shot)"]
    x = np.arange(len(cities))
    w = 0.18

    def _get(c, k):
        if c == "Sydney":
            map_s = {"Ours": "TripSense-FairNet v2 (Ours)", "LGBM": "LightGBM GBDT", "GroupMLP": "GroupMLP", "AGREE": "AGREE (SIGIR'18)", "AvgCos": "Average Cosine"}
            return syd[map_s[k]]["ndcg10"]
        map_e = {"Ours": "TripSense-FairNet v2 (Zero-Shot)", "LGBM": "LightGBM (Zero-Shot)", "GroupMLP": "GroupMLP (Zero-Shot)", "AGREE": "AGREE (Zero-Shot)", "AvgCos": "Average Cosine"}
        return ext[c]["models"][map_e[k]]["ndcg10"]

    city_keys = ["Sydney", "Melbourne", "Tokyo", "New-York"]
    m_specs = [
        ("Ours", "FairNet v2 (Ours)", C_OURS),
        ("LGBM", "LightGBM GBDT", C_LGBM),
        ("GroupMLP", "GroupMLP", C_MLP),
        ("AGREE", "AGREE (SIGIR'18)", C_AGREE),
        ("AvgCos", "Average Cosine", C_SLATE),
    ]
    offsets = np.linspace(-2 * w, 2 * w, len(m_specs))
    for (mk, ml, mc), off in zip(m_specs, offsets):
        vals = [_get(ck, mk) for ck in city_keys]
        bars = ax1.bar(x + off, vals, w * 0.94, label=ml, color=mc, edgecolor=C_DARK, lw=0.5)
        if mk == "Ours":
            for b, v in zip(bars, vals):
                ax1.text(b.get_x() + b.get_width() / 2 - 0.02, v + 0.012, f"{v:.3f}", ha="center", va="bottom",
                         fontsize=7.1, fontweight="bold", color=C_OURS)
        elif mk == "LGBM":
            for b, v in zip(bars, vals):
                ax1.text(b.get_x() + b.get_width() / 2 + 0.04, v + 0.006, f"{v:.3f}", ha="center", va="bottom",
                         fontsize=6.6, color="#92400E")

    ax1.set_xticks(x)
    ax1.set_xticklabels(cities, fontsize=8.5)
    ax1.set_ylabel("Group Consensus NDCG@10")
    ax1.set_title("(a) External Cross-City Zero-Shot Transfer Validation")
    ax1.set_ylim(0, 0.63)
    ax1.legend(loc="upper right", ncol=2, frameon=True)

    # Panel B: Bangladesh 5-City Pilot Ecological & Equity Deployment Audit
    bd_cities = [r["city"] for r in bd]
    xb = np.arange(len(bd_cities))
    eco_bd = [r["fairnet_eco_score_pct"] for r in bd]
    hg_bd = [r["hidden_gem_exposure_pct"] for r in bd]
    minsat_bd = [r["fairnet_min_sat"] * 100.0 for r in bd]

    wb = 0.26
    ax2.bar(xb - wb, eco_bd, wb, label="Eco (%)", color=C_ECO, edgecolor=C_DARK, lw=0.5)
    ax2.bar(xb, minsat_bd, wb, label="MinSat (×100)", color=C_OURS, edgecolor=C_DARK, lw=0.5)
    ax2.bar(xb + wb, hg_bd, wb, label="Hidden Gem (%)", color=C_LGBM, edgecolor=C_DARK, lw=0.5)
    ax2.set_xticks(xb)
    ax2.set_xticklabels(bd_cities, fontsize=8.3, rotation=12)
    ax2.set_ylabel("Deployment Audit Score (%)")
    ax2.set_title("(b) Bangladesh 5-City Pilot Audit (43 Real POIs)")
    ax2.set_ylim(0, 114)
    ax2.legend(loc="upper center", ncol=3, frameon=True, fontsize=7.4)

    fig.tight_layout(pad=1.4)
    _save(fig, "fig5_cross_city_transfer")


def fig6_multi_xai_faithfulness(data):
    mx = data["multi_xai_evaluation"]
    ig_ranked = mx["integrated_gradients"]["features_ranked"][:10]
    shap_map = {r["feature"]: r["importance_pct"] for r in data["shap_feature_importance"]}
    perm_map = {r["feature"]: r["importance_pct"] for r in mx["permutation_importance"]}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 5.0), gridspec_kw={"width_ratios": [1.35, 1.0]})

    # Panel A: Top-10 Features across IG vs TreeSHAP vs Permutation
    fnames = [r["feature"] for r in ig_ranked][::-1]
    y = np.arange(len(fnames))
    h = 0.26
    v_ig = [r["importance_pct"] for r in ig_ranked][::-1]
    v_sh = [shap_map.get(fn, 0.0) for fn in fnames]
    v_pm = [perm_map.get(fn, 0.0) for fn in fnames]

    ax1.barh(y + h, v_ig, h, label="FairNet v2 IG (%)", color=C_OURS, edgecolor=C_DARK, lw=0.4)
    ax1.barh(y, v_sh, h, label="LightGBM TreeSHAP (%)", color=C_LGBM, edgecolor=C_DARK, lw=0.4)
    ax1.barh(y - h, v_pm, h, label="Permutation NDCG Drop (%)", color=C_ECO, edgecolor=C_DARK, lw=0.4)
    ax1.set_yticks(y)
    ax1.set_yticklabels(fnames, fontsize=8.0)
    ax1.set_xlabel("Normalized Feature Attribution Share (%)")
    conc = mx["cross_xai_concordance"]
    ax1.set_title(f"(a) Multi-Paradigm XAI Attribution (Spearman ρ={conc['ig_vs_treeshap_spearman_rho']:.3f} IG/SHAP)")
    ax1.legend(loc="lower right", frameon=True)

    # Panel B: Perturbation Faithfulness Curves (Comprehensiveness & Sufficiency Gap)
    ig_meta = mx["integrated_gradients"]
    ks = [1, 3, 5, 7]
    comp_vals = [ig_meta["comprehensiveness_curve"][f"k{k}"] for k in ks]
    suff_vals = [ig_meta["sufficiency_curve"][f"k{k}"] for k in ks]

    ax2.plot(ks, comp_vals, marker="o", lw=2.2, color=C_OURS, label="Comprehensiveness ΔP (↑ better)")
    ax2.plot(ks, suff_vals, marker="s", lw=2.2, linestyle="--", color=C_AGREE, label="Sufficiency Gap |ΔP| (↓ tighter)")
    ax2.axhline(ig_meta["random_baseline_comp_k3"], color=C_SLATE, linestyle=":", lw=1.4,
                label=f"Random Drop@k=3 ({ig_meta['random_baseline_comp_k3']:.4f}; {ig_meta['faithfulness_ratio_over_random']:.2f}× Ratio)")
    for k, cv, sv in zip(ks, comp_vals, suff_vals):
        ax2.text(k, cv + 0.0007, f"{cv:.4f}", ha="center", fontsize=7.6, color=C_OURS, fontweight="bold")
        ax2.text(k, sv - 0.0014, f"{sv:.4f}", ha="center", fontsize=7.6, color=C_AGREE)

    ax2.set_xticks(ks)
    ax2.set_xticklabels([f"k = {k}" for k in ks])
    ax2.set_xlabel("Top-k Attributed Features Perturbed (15 total)")
    ax2.set_ylabel("Mean Prediction Shift (Probability)")
    ax2.set_title(f"(b) Quantitative Faithfulness (Axiom 1 MAE={ig_meta['completeness_mae']:.1e})")
    ax2.set_ylim(0, 0.025)
    ax2.legend(loc="upper right", frameon=True)

    fig.tight_layout(pad=1.4)
    _save(fig, "fig6_multi_xai_faithfulness")


def fig7_swipe_and_nash_recourse(data):
    sw = data["active_swipe_learning_curve"]
    audit = data["multi_xai_evaluation"]["attention_and_counterfactual_audit"]
    attn = audit["cross_attention_audit"]
    nash = audit["nash_counterfactual_recourse"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.6))

    # Panel A: Active Bayesian EIG Cold-Start Curve
    ks = [r["swipes"] for r in sw]
    ax1.plot(ks, [r["bayesian_eig_cos"] for r in sw], marker="o", lw=2.2, color=C_OURS, label="Bayesian EIG Active Probe")
    ax1.plot(ks, [r["random_swipe_cos"] for r in sw], marker="s", lw=1.8, linestyle="--", color=C_SLATE, label="Random Card Sampling")
    for r in sw:
        ax1.text(r["swipes"], r["bayesian_eig_cos"] + 0.022, f"{r['bayesian_eig_cos']:.3f}", ha="center", fontsize=7.6, color=C_OURS)
    ax1.set_xticks(ks)
    ax1.set_xlabel("Number of Interactive Visual Card Swipes")
    ax1.set_ylabel("Cosine Alignment with Latent User Taste (n = 120)")
    ax1.set_title("(a) Cold-Start Taste Elicitation Curve")
    ax1.set_ylim(0.25, 1.0)
    ax1.legend(loc="lower right", frameon=True)

    # Panel B: Cross-Attention Budget Protection & Nash Counterfactual Recourse
    cats = [
        "Low-Budget\nAttn", "Uniform\nRef.", "High-Budget\nAttn",
        "MinSat\nBefore", "MinSat\nNash", "Gini×10\nBefore", "Gini×10\nAfter"
    ]
    vals = [
        attn["lowest_budget_member_mean_attn"],
        attn["uniform_weight_expected"],
        attn["highest_budget_member_mean_attn"],
        nash["mean_min_member_sat_before"],
        nash["mean_min_member_sat_after"],
        nash["mean_gini_before"] * 10.0,
        nash["mean_gini_after"] * 10.0,
    ]
    cols = [C_ECO, C_SLATE, C_SKY, C_LGBM, C_OURS, C_AGREE, C_ECO]
    x = np.arange(len(cats))
    bars = ax2.bar(x, vals, color=cols, edgecolor=C_DARK, lw=0.6, width=0.62)
    for b, v in zip(bars, vals):
        ax2.text(b.get_x() + b.get_width() / 2, v + 0.015, f"{v:.3f}", ha="center", va="bottom", fontsize=7.6, fontweight="bold")
    ax2.axvline(2.5, color="#94A3B8", linestyle="--", lw=1.0)
    ax2.set_xticks(x)
    ax2.set_xticklabels(cats, fontsize=7.4)
    ax2.set_ylabel("Weight / Satisfaction / Scaled Inequality")
    ax2.set_title(f"(b) Attention Equity & Nash Recourse (Welfare +{nash['mean_nash_welfare_gain_pct']:.2f}%)")
    ax2.set_ylim(0, 0.78)

    fig.tight_layout(pad=1.4)
    _save(fig, "fig7_swipe_and_nash_recourse")


def fig8_travelplanner_neurosymbolic(data):
    tp = data["travelplanner_rag_evaluation"]
    pub = tp["published_icml2024_zeroshot_final_pass"]
    van = tp["vanilla_llm"]
    ts = tp["tripsense_neuro_symbolic_rag"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.5))

    # Panel A: TravelPlanner 180-Task Verification Comparison
    metrics = ["Entity\nGrounding (%)", "Hard Budget\nFeasibility (%)", "Strict Final\nPass Rate (%)"]
    v_vals = [van["entity_grounding_pct"], van["budget_feasibility_pct"], van["final_pass_rate_pct"]]
    t_vals = [ts["entity_grounding_pct"], ts["budget_feasibility_pct"], ts["final_pass_rate_pct"]]

    x = np.arange(len(metrics))
    w = 0.34
    b1 = ax1.bar(x - w / 2, v_vals, w, label="Vanilla Unconstrained LLM", color=C_AGREE, edgecolor=C_DARK, lw=0.6)
    b2 = ax1.bar(x + w / 2, t_vals, w, label=f"TripSense Neuro-Symbolic ({tp['avg_verify_ms']:.3f} ms)", color=C_ECO, edgecolor=C_DARK, lw=0.6)
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width() / 2, h + 1.5, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.0, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics, fontsize=8.5)
    ax1.set_ylabel("Validation Pass / Grounding Rate (%)")
    ax1.set_title(f"(a) osunlp/TravelPlanner Benchmark (N = {tp['num_tasks']} Tasks)")
    ax1.set_ylim(0, 126)
    ax1.legend(loc="upper center", ncol=1, frameon=True)

    # Panel B: Zero-Shot Final Pass Rate vs Published ICML 2024 Baselines
    models = ["GPT-3.5 Zero-Shot\n(ICML 2024)", "GPT-4 Zero-Shot\n(ICML 2024)", "Vanilla LLM\n(TravelPlanner)", "TripSense RAG +\nVerifier (Ours)"]
    p_vals = [pub["gpt_3_5_pct"], pub["gpt_4_pct"], van["final_pass_rate_pct"], ts["final_pass_rate_pct"]]
    p_cols = [C_SLATE, C_LGBM, C_AGREE, C_OURS]
    xp = np.arange(len(models))
    bp = ax2.bar(xp, p_vals, width=0.55, color=p_cols, edgecolor=C_DARK, lw=0.6)
    for b, v in zip(bp, p_vals):
        ax2.text(b.get_x() + b.get_width() / 2, v + 1.4, f"{v:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    ax2.set_xticks(xp)
    ax2.set_xticklabels(models, fontsize=8.2)
    ax2.set_ylabel("Strict Final Pass Rate (%)")
    ax2.set_title("(b) Final Plan Feasibility vs. Published Baselines")
    ax2.set_ylim(0, 66)

    fig.tight_layout(pad=1.4)
    _save(fig, "fig8_travelplanner_neurosymbolic")


def main():
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    fig1_architecture_overview(data)
    fig2_model_benchmark_and_cd(data)
    fig3_fairness_accuracy_pareto(data)
    fig4_ablation_and_scaling(data)
    fig5_cross_city_transfer(data)
    fig6_multi_xai_faithfulness(data)
    fig7_swipe_and_nash_recourse(data)
    fig8_travelplanner_neurosymbolic(data)
    print(f"[DONE] All 8 Q1 figures generated cleanly in {OUT_DIR}")


if __name__ == "__main__":
    main()
