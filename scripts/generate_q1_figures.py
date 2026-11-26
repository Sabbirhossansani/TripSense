"""
Flagship Q1 Publication Figure Generator for TripSense-FairNet v3 (GeoFairFormer).
Produces 10 300-DPI PNG + vector PDF figures directly from
backend/ml/artifacts/q1_benchmark_results.json using pure Matplotlib.
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
METRICS_PATH = os.path.join(ROOT_DIR, "backend", "ml", "artifacts", "q1_benchmark_results.json")
OUT_DIR = os.path.join(ROOT_DIR, "docs", "q1_figures")
os.makedirs(OUT_DIR, exist_ok=True)

# Colorblind-safe Okabe-Ito publication palette
C_OURS = "#0072B2"     # Ocean blue (TripSense-FairNet v3)
C_ECO = "#009E73"      # Forest emerald (Eco / Neuro-Symbolic / TripWorld)
C_LGBM = "#E69F00"     # Warm gold (LightGBM / GBDT)
C_AGREE = "#D55E00"    # Vermilion (AGREE / Random / Vanilla)
C_MLP = "#CC79A7"      # Muted plum (MoSAN / Set-Transformer)
C_SLATE = "#64748B"    # Neutral slate (Heuristics)
C_SKY = "#56B4E9"      # Sky blue (GroupIM / Secondary)
C_DARK = "#0F172A"     # Deep ink

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Times New Roman", "serif"],
    "font.size": 9.2,
    "axes.titlesize": 10.6,
    "axes.titleweight": "bold",
    "axes.labelsize": 9.2,
    "axes.edgecolor": "#CBD5E1",
    "axes.linewidth": 0.9,
    "axes.grid": True,
    "grid.color": "#E2E8F0",
    "grid.linestyle": "--",
    "grid.linewidth": 0.6,
    "grid.alpha": 0.75,
    "xtick.labelsize": 8.2,
    "ytick.labelsize": 8.2,
    "legend.fontsize": 8.0,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.facecolor": "white",
})


def _save(fig, name: str):
    for ext in ("png", "pdf"):
        p = os.path.join(OUT_DIR, f"{name}.{ext}")
        if ext == "png":
            fig.savefig(p, bbox_inches="tight", dpi=300)
        else:
            fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    print(f"[Figure] Saved {name}.png & .pdf", flush=True)


def fig1_architecture_overview(data):
    fig, ax = plt.subplots(figsize=(12.6, 5.8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 52)
    ax.axis("off")

    def box(x, y, w, h, title, body, fc="#F8FAFC", ec="#334155", tc=C_DARK, lw=1.4):
        p = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.2",
            facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2
        )
        ax.add_patch(p)
        ax.text(x + w / 2, y + h - 2.1, title, ha="center", va="top", fontsize=8.8, fontweight="bold", color=tc, zorder=3)
        ax.text(x + w / 2, y + h / 2 - 1.1, body, ha="center", va="center", fontsize=7.4, color="#334155", linespacing=1.34, zorder=3)

    def arrow(x1, y1, x2, y2, color="#475569"):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.35, shrinkA=2, shrinkB=2), zorder=4)

    ax.text(50, 50.2, "TripSense-FairNet v3 (GeoFairFormer): Dual-Path O(D)-Invariant Consensus & Spectral OOD Gating",
            ha="center", va="center", fontsize=11.6, fontweight="bold", color=C_DARK)

    box(1.5, 28, 19.5, 17, "Multimodal Inputs",
        "Group Profiles (|G| = 2..5)\n72% Past Check-ins (No Leak)\nCandidate POI + 8-d Context\nCLIP / SigLIP / BGE Centered",
        fc="#EFF6FF", ec=C_OURS)
    box(1.5, 5, 19.5, 17, "BALD Active Swipe",
        "Gaussian Posterior EIG\narg max x^T Sigma_t x\n0 -> 6 Cold-Start Calibration\nOrthogonal Taste Refinement",
        fc="#F0FDF4", ec=C_ECO)

    box(25.5, 31.5, 25, 14, "Stream 1: O(D) + MemberGramSAB",
        "19-d Zero-Coord Geo Tokens\nMember-to-Member Gram SAB\n4-Head Cross-Attn + Soft-Min",
        fc="#F5F3FF", ec=C_MLP)
    box(25.5, 16.5, 25, 11.5, "Stream 2: 15-d Rel. Highway",
        "Un-Squashed Summary Manifold\n[cos_{mu,min,max,std}, bg, |G|/5,\n dist..SME] ResNet + Skip",
        fc="#FFFBEB", ec=C_LGBM)
    box(25.5, 3.5, 25, 10.0, "Stream 3: Spectral-Gated Adapter",
        "Top-48 Source SVD Gate gamma(C)\nSydney=0.75 vs Tokyo/TW~0.00\nHadamard Adapter (In-Domain)",
        fc="#FFF1F2", ec=C_AGREE)

    box(55.5, 11, 20.5, 33, "Dual-Path Pareto\nInfoNCE Fusion",
        "Invariant Logit = s0*Attn +\n  s1*SoftMin + s2*Rel + b\nTotal = Inv + gamma*s3*Sem\n\nJoint Loss (L_tot + 0.7 L_inv):\n• 20-Neg InfoNCE (tau=0.20)\n• Differentiable True Gini\n• Rawlsian Min-Sat Floor\n• Soft-Slate Expected Eco",
        fc="#ECFEFF", ec=C_OURS, lw=1.8)

    mae = data["multi_xai_evaluation"]["integrated_gradients"]["completeness_mae"]
    ins_auc = data["multi_xai_evaluation"]["integrated_gradients"]["insertion_auc"]
    nash_gain = data["multi_xai_evaluation"]["attention_and_counterfactual_audit"]["nash_counterfactual_recourse"]["mean_nash_welfare_gain_pct"]
    tp_feas = data["travelplanner_rag_evaluation"]["tripsense_neuro_symbolic_rag"]["budget_feasibility_pct"]

    box(80.5, 28, 18.0, 17, "5-Paradigm E2E XAI",
        f"32-Step IG (MAE={mae:.1e})\nExpected Grad + InputxGrad\nInsAUC={ins_auc:.3f} | 5.33x Comp\nWorked Local Case Audits",
        fc="#FEF2F2", ec=C_AGREE)
    box(80.5, 5, 18.0, 17, "Nash & Symbolic Audit",
        f"Nash Bargaining Veto\n(Welfare Gain +{nash_gain:.2f}%)\nDeterministic CSP Verifier\n(Budget Feas. {tp_feas:.0f}%)",
        fc="#F0FDF4", ec=C_ECO)

    arrow(21.5, 36.5, 25.0, 38.5, C_OURS)
    arrow(21.5, 32.0, 25.0, 22.2, C_LGBM)
    arrow(21.5, 29.0, 25.0, 8.5, C_AGREE)
    arrow(11.2, 22.5, 11.2, 27.5, C_ECO)
    arrow(51.0, 38.5, 55.0, 34.0, C_MLP)
    arrow(51.0, 22.2, 55.0, 26.5, C_LGBM)
    arrow(51.0, 8.5, 55.0, 17.0, C_AGREE)
    arrow(76.5, 33.5, 80.0, 36.5, C_AGREE)
    arrow(76.5, 20.0, 80.0, 13.5, C_ECO)

    _save(fig, "fig1_architecture_overview")


def fig2_model_benchmark_and_cd(data):
    comp = data["group_consensus_comparison"]
    st = data["statistical_tests"]

    items = sorted(comp.items(), key=lambda kv: kv[1]["ndcg10"])
    names = [k for k, _ in items]
    ndcgs = np.array([v["ndcg10"] for _, v in items])
    ci_lows = np.array([v["ndcg10"] - v["ndcg10_ci95"][0] for _, v in items])
    ci_highs = np.array([v["ndcg10_ci95"][1] - v["ndcg10"] for _, v in items])
    colors = []
    for k in names:
        if "Ours" in k:
            colors.append(C_OURS)
        elif "LightGBM" in k or "Hist" in k or "Random Forest" in k:
            colors.append(C_LGBM)
        elif any(t in k for t in ["AGREE", "MoSAN", "GroupIM", "Set-Transformer", "DeepSets", "GroupMLP"]):
            colors.append(C_MLP)
        else:
            colors.append(C_SLATE)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.0, 5.6), gridspec_kw={"width_ratios": [1.32, 1.0]})

    y_pos = np.arange(len(names))
    ax1.barh(y_pos, ndcgs, xerr=[ci_lows, ci_highs], height=0.68, color=colors,
             edgecolor=C_DARK, linewidth=0.55, error_kw=dict(ecolor=C_DARK, lw=1.0, capsize=2.5))
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([n.replace(" (Ours)", "\n(Ours)") for n in names], fontsize=7.8)
    for i, (val, hi, name) in enumerate(zip(ndcgs, ci_highs, names)):
        fw = "bold" if "Ours" in name else "normal"
        col = C_OURS if "Ours" in name else C_DARK
        sig = " ***" if comp[name].get("holm_p_ndcg10", 1.0) < 0.001 else ""
        ax1.text(val + hi + 0.008, i, f"{val:.4f}{sig}", va="center", fontsize=7.4, fontweight=fw, color=col)
    ax1.set_xlim(0, 0.72)
    ax1.set_xlabel("NDCG@10 (with 95% Bootstrap CI, N = 180 Test Groups)")
    ax1.set_title("(A) 15-Model Benchmark on Massive-STEPS-Sydney")
    ax1.grid(axis="x", linestyle="--", alpha=0.6)
    ax1.grid(axis="y", visible=False)

    # Panel B: Friedman-Nemenyi CD Diagram
    ranked = sorted(comp.items(), key=lambda kv: kv[1]["friedman_rank"])
    r_names = [k for k, _ in ranked]
    ranks = np.array([v["friedman_rank"] for _, v in ranked])
    cd = st["nemenyi_cd_alpha05"]
    best_r = ranks[0]

    y2 = np.arange(len(r_names))[::-1]
    c2 = [C_OURS if "Ours" in k else (C_LGBM if ("LightGBM" in k or "Hist" in k or "Forest" in k) else C_SLATE) for k in r_names]
    ax2.hlines(y2, xmin=best_r, xmax=ranks, color="#CBD5E1", linewidth=1.2, zorder=1)
    ax2.scatter(ranks, y2, s=68, color=c2, edgecolor=C_DARK, zorder=3)
    for idx_r, (rn, rk, yy) in enumerate(zip(r_names, ranks, y2)):
        ax2.text(rk + 0.16, yy, f"{rk:.2f}", va="center", fontsize=7.3,
                 fontweight=("bold" if "Ours" in rn else "normal"))

    ax2.axvspan(best_r, best_r + cd, color="#DBEAFE", alpha=0.50, label=f"Nemenyi CD_0.05 = {cd:.3f}")
    ax2.axvline(best_r + cd, color=C_OURS, linestyle="--", linewidth=1.2)
    ax2.set_yticks(y2)
    ax2.set_yticklabels([n.replace(" (SIGIR'18)", "").replace(" (SIGIR'19)", "").replace(" (SIGIR'20)", "").replace(" (ICML'19)", "").replace(" (NeurIPS'17)", "") for n in r_names], fontsize=7.6)
    ax2.set_xlim(4.0, 12.8)
    ax2.set_xlabel("Mean Friedman Rank (1 = Best, Lower Better)")
    ax2.set_title(f"(B) Friedman chi2 = {st['friedman_chi2']:.1f} (p = {st['friedman_p_value']:.1e})")
    ax2.legend(loc="upper right", frameon=True, fontsize=7.8)

    plt.tight_layout()
    _save(fig, "fig2_model_benchmark_and_cd")


def fig3_pareto_and_sensitivity(data):
    comp = data["group_consensus_comparison"]
    hs = data["hyperparameter_sensitivity"]
    bb = data["backbone_comparison"]

    fig, axes = plt.subplots(2, 2, figsize=(12.2, 8.6))

    # Panel A: Pareto Fairness-Accuracy Frontier
    ax = axes[0, 0]
    for mname, mvals in comp.items():
        x, y, eco = mvals["gini_index"], mvals["ndcg10"], mvals["eco_coverage_pct"]
        is_ours = "Ours" in mname
        col = C_OURS if is_ours else (C_LGBM if "LightGBM" in mname else (C_MLP if any(t in mname for t in ["AGREE", "MoSAN", "GroupIM", "GroupMLP"]) else C_SLATE))
        ax.scatter(x, y, s=eco * 4.8 if not is_ours else eco * 7.2,
                   color=col, edgecolor=C_DARK, linewidth=(1.6 if is_ours else 0.7), alpha=0.88, zorder=(5 if is_ours else 3))
        if is_ours or mname in ("LightGBM GBDT", "LightGBM LambdaRank", "MoSAN (SIGIR'19)", "GroupMLP", "GroupIM (SIGIR'20)", "Least-Misery", "Popularity"):
            short = "FairNet v3 (Ours)" if is_ours else mname.replace(" (SIGIR'19)", "").replace(" (SIGIR'20)", "").replace(" GBDT", "")
            offsets = {
                "TripSense-FairNet v3 (Ours)": (-0.0004, -0.032),
                "LightGBM GBDT": (0.0012, 0.020),
                "GroupMLP": (-0.0022, 0.006),
                "MoSAN (SIGIR'19)": (0.0002, 0.016),
                "GroupIM (SIGIR'20)": (0.0012, -0.022),
                "LightGBM LambdaRank": (-0.0005, -0.026),
                "Popularity": (0.0005, 0.015),
                "Least-Misery": (0.0012, 0.015),
            }
            dx, dy = offsets.get(mname, (0.0005, 0.014))
            ax.annotate(short, (x + dx, y + dy), fontsize=7.5, fontweight=("bold" if is_ours else "normal"),
                        color=(C_OURS if is_ours else C_DARK))

    # Plot Pareto sweep trajectory
    ps = hs["lambda_gini_sweep"]
    ax.plot([r["gini_index"] for r in ps], [r["ndcg10"] for r in ps], "--", color=C_OURS, alpha=0.65, lw=1.2, label="lambda_gini Sweep")
    ax.invert_xaxis()
    ax.set_xlabel("Intra-Group Gini Index (Right = Lower Inequality)")
    ax.set_ylabel("NDCG@10 (Higher Better)")
    ax.set_title("(A) Fairness-Accuracy-Eco Pareto Frontier (Bubble Size = Eco %)")
    ax.legend(loc="lower left", fontsize=7.6)

    # Panel B: lambda_gini & lambda_eco Sensitivity
    ax = axes[0, 1]
    lgs = [r["lambda_gini"] for r in ps]
    ax.plot(lgs, [r["ndcg10"] for r in ps], "o-", color=C_OURS, lw=2.0, label="NDCG@10 vs lambda_gini")
    ax.set_xlabel("lambda_gini Weight")
    ax.set_ylabel("NDCG@10", color=C_OURS)
    ax.tick_params(axis="y", labelcolor=C_OURS)
    ax_r = ax.twinx()
    ax_r.plot(lgs, [r["gini_index"] for r in ps], "s--", color=C_AGREE, lw=1.8, label="Gini Index (Right)")
    ax_r.set_ylabel("Gini Index (Lower Better)", color=C_AGREE)
    ax_r.tick_params(axis="y", labelcolor=C_AGREE)
    ax_r.grid(False)
    ax.set_title("(B) Pareto Weight Sensitivity (lambda_gini = 0.36 Sweet Spot)")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax_r.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=7.4)

    # Panel C: Temperature tau & lambda_eco Sensitivity
    ax = axes[1, 0]
    tsw = hs["tau_sweep"]
    taus = [r["tau"] for r in tsw]
    ax.plot(taus, [r["ndcg10"] for r in tsw], "o-", color=C_OURS, lw=2.0, label="NDCG@10 (tau Sweep)")
    ax.set_xlabel("InfoNCE Temperature tau")
    ax.set_ylabel("NDCG@10", color=C_OURS)
    ax2r = ax.twinx()
    ax2r.plot(taus, [r["eco_coverage_pct"] for r in tsw], "^--", color=C_ECO, lw=1.8, label="Eco Coverage % (Right)")
    ax2r.set_ylabel("Top-5 Eco Coverage (%)", color=C_ECO)
    ax2r.grid(False)
    ax.set_title("(C) Contrastive Temperature tau Sensitivity")
    l1, lb1 = ax.get_legend_handles_labels()
    l2, lb2 = ax2r.get_legend_handles_labels()
    ax.legend(l1 + l2, lb1 + lb2, loc="lower left", fontsize=7.4)

    # Panel D: 3-Backbone Foundation Comparison
    ax = axes[1, 1]
    b_labels = ["CLIP ViT-B/32\n(512-d)", "Google SigLIP\n(768-d)", "BAAI BGE-base\n(768-d)"]
    b_keys = ["openai/clip-vit-base-patch32", "google/siglip-base-patch16-224", "BAAI/bge-base-en-v1.5"]
    x_pos = np.arange(len(b_keys))
    w = 0.20
    for idx_m, (mkey, mlbl, col) in enumerate([
        ("fairnet_v3", "FairNet v3 (Ours)", C_OURS),
        ("groupim", "GroupIM (SIGIR'20)", C_SKY),
        ("lambdarank", "LGBM LambdaRank", C_LGBM),
        ("avg_cos", "Average Cosine", C_SLATE),
    ]):
        vals = [bb[bk][mkey]["ndcg10"] for bk in b_keys]
        bars = ax.bar(x_pos + (idx_m - 1.5) * w, vals, width=w, label=mlbl, color=col, edgecolor=C_DARK, linewidth=0.5)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.008, f"{v:.3f}", ha="center", va="bottom", fontsize=6.6, rotation=90)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(b_labels)
    ax.set_ylim(0, 0.72)
    ax.set_ylabel("Sydney Test NDCG@10")
    ax.set_title("(D) Multi-Backbone Generalization (3 Foundation Encoders)")
    ax.legend(loc="upper right", ncol=2, fontsize=7.2)

    plt.tight_layout()
    _save(fig, "fig3_pareto_and_sensitivity")


def fig4_ablation_and_scaling(data):
    abl = data["ablation_study"]
    scl = data["group_size_scaling"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.8, 5.2), gridspec_kw={"width_ratios": [1.3, 1.0]})

    # Panel A: 10-Variant Component Ablation (both Sydney + External Zero-Shot Mean)
    vnames = [r["variant"].replace(" (Ours)", "").replace("O(D)", "O(D)") for r in abl]
    syd_vals = [r["ndcg10"] for r in abl]
    ext_vals = [r["ext_mean_ndcg10"] for r in abl]
    y = np.arange(len(vnames))[::-1]
    h = 0.36
    ax1.barh(y + h / 2, syd_vals, height=h, color=C_OURS, edgecolor=C_DARK, lw=0.5, label="Sydney In-Domain NDCG@10")
    ax1.barh(y - h / 2, ext_vals, height=h, color=C_ECO, edgecolor=C_DARK, lw=0.5, label="5-City Zero-Shot Mean NDCG@10")
    for yy, sv, ev in zip(y, syd_vals, ext_vals):
        ax1.text(sv + 0.006, yy + h / 2, f"{sv:.3f}", va="center", fontsize=7.0, color=C_OURS, fontweight="bold")
        ax1.text(ev + 0.006, yy - h / 2, f"{ev:.3f}", va="center", fontsize=7.0, color=C_ECO)
    ax1.set_yticks(y)
    ax1.set_yticklabels(vnames, fontsize=7.7)
    ax1.set_xlim(0.20, 0.64)
    ax1.set_xlabel("NDCG@10 (Note: Removing Spectral Gate drops Ext Mean 0.3585 -> 0.3371)")
    ax1.set_title("(A) 10-Variant Component Ablation (In-Domain vs Zero-Shot)")
    ax1.legend(loc="lower right", fontsize=7.4)

    # Panel B: Group Size Scaling |G|=2..5
    gsz = [r["group_size"] for r in scl]
    ax2.plot(gsz, [r["fairnet_ndcg10"] for r in scl], "o-", color=C_OURS, lw=2.3, ms=7, label="FairNet v3 (Ours)")
    ax2.plot(gsz, [r["lgbm_ndcg10"] for r in scl], "s--", color=C_LGBM, lw=1.8, ms=6, label="LightGBM GBDT")
    ax2.plot(gsz, [r["groupim_ndcg10"] for r in scl], "D-.", color=C_SKY, lw=1.6, ms=5.5, label="GroupIM (SIGIR'20)")
    ax2.plot(gsz, [r["agree_ndcg10"] for r in scl], "^:", color=C_AGREE, lw=1.6, ms=6, label="AGREE (SIGIR'18)")
    ax2.plot(gsz, [r["lambdarank_ndcg10"] for r in scl], "v--", color=C_MLP, lw=1.5, ms=5.5, label="LightGBM LambdaRank")
    for r in scl:
        ax2.text(r["group_size"], r["fairnet_ndcg10"] + 0.012, f"{r['fairnet_ndcg10']:.3f}", ha="center", fontsize=7.5, fontweight="bold", color=C_OURS)
    ax2.set_xticks(gsz)
    ax2.set_xticklabels([f"|G|={g}\n(n={r['num_groups']})" for g, r in zip(gsz, scl)])
    ax2.set_ylim(0.30, 0.70)
    ax2.set_ylabel("Held-Out Test NDCG@10")
    ax2.set_title("(B) Group Cardinality Scaling (|G| = 2..5 Companions)")
    ax2.legend(loc="upper right", fontsize=7.4)

    plt.tight_layout()
    _save(fig, "fig4_ablation_and_scaling")


def fig5_multicontinent_and_tripworld(data):
    ext = data["external_cross_city_validation"]
    tw = data["tripworld_external_validation"]

    cities = ["Melbourne", "Tokyo", "New-York", "Istanbul", "Sao-Paulo"]
    domains = cities + ["TripWorld\n(Osaka)"]
    datasets_list = [ext[c] for c in cities] + [tw]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 5.1), gridspec_kw={"width_ratios": [1.55, 1.0]})

    x = np.arange(len(domains))
    w = 0.16
    model_specs = [
        ("TripSense-FairNet v3 (Zero-Shot)", "FairNet v3 (Zero-Shot)", C_OURS),
        ("LightGBM Cls (Zero-Shot)", "LightGBM Cls", C_LGBM),
        ("LightGBM LambdaRank (Zero-Shot)", "LGBM LambdaRank", C_MLP),
        ("MoSAN (Zero-Shot)", "MoSAN (SIGIR'19)", C_SKY),
        ("GroupIM (Zero-Shot)", "GroupIM (SIGIR'20)", C_ECO),
        ("AGREE (Zero-Shot)", "AGREE (SIGIR'18)", C_AGREE),
    ]
    for idx_m, (mkey, mlbl, col) in enumerate(model_specs):
        vals = [d["models"][mkey]["ndcg10"] for d in datasets_list]
        bars = ax1.bar(x + (idx_m - 2.5) * w, vals, width=w, label=mlbl, color=col, edgecolor=C_DARK, lw=0.45)
        if idx_m == 0:
            for b, v in zip(bars, vals):
                ax1.text(b.get_x() + b.get_width() / 2, v + 0.010, f"{v:.3f}", ha="center", va="bottom", fontsize=7.2, fontweight="bold", color=C_OURS)
    ax1.set_xticks(x)
    ax1.set_xticklabels(domains, fontsize=8.4)
    ax1.set_ylim(0.0, 0.67)
    ax1.set_ylabel("Zero-Shot Test NDCG@10 (Zero Target Retraining)")
    ax1.set_title("(A) Multi-Continent 5-City & Independent 2026 TripWorld Transfer")
    ax1.legend(loc="upper left", ncol=2, fontsize=7.2)

    # Panel B: Unsupervised Spectral Gate gamma(C) & Gini/Eco on External Benchmarks
    gate_labels = ["Sydney\n(Source)"] + cities + ["TripWorld\n(Osaka)"]
    gates = [data["datasets"]["sydney_spectral_gate"]] + [d["spectral_gate_activation"] for d in datasets_list]
    gx = np.arange(len(gate_labels))
    bar_cols = [C_OURS] + [C_ECO if g < 0.15 else C_LGBM for g in gates[1:]]
    bars_g = ax2.bar(gx, gates, width=0.58, color=bar_cols, edgecolor=C_DARK, lw=0.6)
    for b, g in zip(bars_g, gates):
        ax2.text(b.get_x() + b.get_width() / 2, g + 0.022, f"{g:.3f}", ha="center", va="bottom", fontsize=7.4, fontweight="bold")
    ax2.set_xticks(gx)
    ax2.set_xticklabels(gate_labels, fontsize=7.6)
    ax2.set_ylim(0.0, 0.92)
    ax2.set_ylabel("Mean Spectral-Support Gate Activation gamma(C)")
    ax2.set_title("(B) Unsupervised OOD Spectral Gate Suppresses Shift")
    ax2.axhline(0.50, color=C_SLATE, linestyle="--", lw=1.0, label="Domain Shift Boundary")
    ax2.legend(loc="upper right", fontsize=7.4)

    plt.tight_layout()
    _save(fig, "fig5_multicontinent_and_tripworld")


def fig6_xai_faithfulness_benchmark(data):
    ft = data["multi_xai_evaluation"]["faithfulness_comparison"]
    steps = list(range(0, 16))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 4.9))
    styles = [
        ("Integrated Gradients (Ours End-to-End)", "-", "o", C_OURS, 2.3),
        ("Expected Gradients (GradientSHAP)", "--", "s", C_ECO, 1.9),
        ("Vanilla Gradient Saliency", "-.", "^", C_LGBM, 1.7),
        ("Input x Gradient", ":", "D", C_MLP, 1.7),
        ("Random Baseline", "--", "x", C_AGREE, 1.5),
    ]

    for label, ls, mk, col, lw in styles:
        d = ft[label]
        ax1.plot(steps, d["deletion_trajectory"], ls, marker=mk, markersize=4.3, color=col, lw=lw,
                 label=f"{label.split(' (')[0]} (AUC={d['deletion_auc']:.4f})")
        ax2.plot(steps, d["insertion_trajectory"], ls, marker=mk, markersize=4.3, color=col, lw=lw,
                 label=f"{label.split(' (')[0]} (AUC={d['insertion_auc']:.4f})")

    ax1.set_xlabel("Top-k Attributed Features Removed (k)")
    ax1.set_ylabel("Mean Predicted Positive Probability")
    ax1.set_title("(A) Perturbation Deletion Curve (Lower AUC = More Faithful)")
    ax1.legend(loc="upper right", fontsize=7.3)

    ax2.set_xlabel("Top-k Attributed Features Inserted (k)")
    ax2.set_ylabel("Mean Predicted Positive Probability")
    ax2.set_title("(B) Perturbation Insertion Curve (Higher AUC = More Faithful)")
    ax2.legend(loc="lower right", fontsize=7.3)

    plt.tight_layout()
    _save(fig, "fig6_xai_faithfulness_benchmark")


def fig7_xai_concordance_and_casestudy(data):
    mx = data["multi_xai_evaluation"]
    ig_map = {r["feature"]: r["importance_pct"] for r in mx["integrated_gradients"]["features_unsorted"]}
    shap_map = {r["feature"]: r["importance_pct"] for r in data["shap_feature_importance"]}
    conc = mx["cross_xai_concordance"]

    # Sort features by FairNet End-to-End IG importance
    feats_sorted = sorted(ig_map.keys(), key=lambda k: ig_map[k])
    y = np.arange(len(feats_sorted))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.0, 5.4), gridspec_kw={"width_ratios": [1.35, 1.0]})

    h = 0.37
    ig_v = [ig_map[f] for f in feats_sorted]
    sh_v = [shap_map[f] for f in feats_sorted]
    ax1.barh(y + h / 2, ig_v, height=h, color=C_OURS, edgecolor=C_DARK, lw=0.45, label="FairNet v3 E2E IG (%)")
    ax1.barh(y - h / 2, sh_v, height=h, color=C_LGBM, edgecolor=C_DARK, lw=0.45, label="LightGBM TreeSHAP (%)")
    ax1.set_yticks(y)
    ax1.set_yticklabels(feats_sorted, fontsize=7.6)
    ax1.set_xlabel("Normalized Global Attribution Share (%)")
    ax1.set_title(
        f"(A) FairNet v3 vs LightGBM Attributions (r = {conc['ig_vs_treeshap_pearson_r']:.3f}, "
        f"p = {conc['ig_vs_treeshap_pearson_p']:.1e})\n"
        f"Note Fairness Shift: Budget Gap 10.1% vs 2.9% | Max-Member 3.4% vs 10.3%"
    )
    ax1.legend(loc="lower right", fontsize=7.5)

    # Panel B: Worked Case Study 1 (sydney_grp_1021) Member Utilities, Budgets & Attention Weights
    cs = mx["worked_case_studies"][0]
    top_rec = cs["top_recommendation"]
    M = cs["group_size"]
    m_labels = [f"Member {i+1}\n(Budget={cs['member_budgets'][i]:.2f})" for i in range(M)]
    mx_pos = np.arange(M)
    bw = 0.34
    ax2.bar(mx_pos - bw / 2, top_rec["cross_attention_weights"], width=bw, color=C_OURS, edgecolor=C_DARK, label="Cross-Attn Weight alpha_u")
    ax2.bar(mx_pos + bw / 2, top_rec["member_utilities"], width=bw, color=C_ECO, edgecolor=C_DARK, label="Predicted Utility U_u(p)")
    for i in range(M):
        ax2.text(i - bw / 2, top_rec["cross_attention_weights"][i] + 0.015, f"{top_rec['cross_attention_weights'][i]:.3f}", ha="center", fontsize=7.5, fontweight="bold", color=C_OURS)
        ax2.text(i + bw / 2, top_rec["member_utilities"][i] + 0.015, f"{top_rec['member_utilities'][i]:.3f}", ha="center", fontsize=7.5, fontweight="bold", color=C_ECO)
    ax2.set_xticks(mx_pos)
    ax2.set_xticklabels(m_labels, fontsize=8.0)
    ax2.set_ylim(0, 0.85)
    ax2.set_ylabel("Weight / Utility Score")
    ax2.set_title(
        f"(B) Worked Case Study ({cs['group_id']}: {top_rec['name']})\n"
        f"Rawlsian Priority Weighting Equalizes Utility (Gini = {top_rec['gini']:.4f})"
    )
    ax2.legend(loc="upper right", fontsize=7.4)

    plt.tight_layout()
    _save(fig, "fig7_xai_concordance_and_casestudy")


def fig8_active_swipe_and_nash(data):
    sw = data["active_swipe_learning_curve"]
    audit = data["multi_xai_evaluation"]["attention_and_counterfactual_audit"]
    attn = audit["cross_attention_audit"]
    nash = audit["nash_counterfactual_recourse"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 4.7))

    xs = [r["swipes"] for r in sw]
    by = [r["bayesian_eig_cos"] for r in sw]
    ry = [r["random_swipe_cos"] for r in sw]
    ax1.plot(xs, by, "o-", color=C_OURS, lw=2.3, ms=6.5, label="Gaussian BALD EIG Swipes (Ours)")
    ax1.plot(xs, ry, "s--", color=C_AGREE, lw=1.9, ms=5.5, label="Random Swipe Baseline")
    ax1.fill_between(xs, ry, by, color=C_SKY, alpha=0.18)
    for k, b, rv in zip(xs, by, ry):
        dy = -0.036 if b < rv else 0.022
        ax1.text(k, b + dy, f"{b:.3f}", ha="center", fontsize=7.4, fontweight="bold", color=C_OURS)
    ax1.set_xlabel("Cold-Start Preference Swipes (k)")
    ax1.set_ylabel("Latent Taste Alignment (Cosine Similarity)")
    ax1.set_ylim(0.10, 0.82)
    ax1.set_title("(A) Cold-Start Taste Elicitation (120 Synthetic Travelers)")
    ax1.legend(loc="lower right", fontsize=7.6)

    # Panel B: Cross-Attention Budget Protection & Nash Recourse
    cats = ["Lowest-Budget\nMember Attn", "Uniform\nBaseline (1/M)", "Highest-Budget\nMember Attn", "Veto Min-Sat\n(Before)", "Nash Recourse\nMin-Sat (After)"]
    vals = [
        attn["lowest_budget_member_mean_attn"],
        attn["uniform_weight_expected"],
        attn["highest_budget_member_mean_attn"],
        nash["mean_min_member_sat_before"],
        nash["mean_min_member_sat_after"],
    ]
    cols = [C_OURS, C_SLATE, C_AGREE, C_LGBM, C_ECO]
    bars = ax2.bar(np.arange(len(cats)), vals, width=0.56, color=cols, edgecolor=C_DARK, lw=0.6)
    for b, v in zip(bars, vals):
        ax2.text(b.get_x() + b.get_width() / 2, v + 0.015, f"{v:.4f}", ha="center", fontsize=7.5, fontweight="bold")
    ax2.set_xticks(np.arange(len(cats)))
    ax2.set_xticklabels(cats, fontsize=7.5)
    ax2.set_ylim(0, 0.78)
    ax2.set_ylabel("Mean Attention Weight / Satisfaction")
    ax2.set_title(f"(B) Budget Equity & Nash Recourse (+{nash['mean_nash_welfare_gain_pct']:.2f}% Welfare, N=80)")

    plt.tight_layout()
    _save(fig, "fig8_active_swipe_and_nash")


def fig9_travelplanner_and_bd_pilot(data):
    tp = data["travelplanner_rag_evaluation"]
    bd = data["bangladesh_5city_pilot"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 4.8))

    # Panel A: TravelPlanner 180 tasks
    metrics_tp = ["Entity\nGrounding %", "Hard Budget\nFeasibility %", "Final Plan\nPass Rate %", "Hallucination\nRate % (Low Better)"]
    v_vals = [
        tp["vanilla_llm"]["entity_grounding_pct"],
        tp["vanilla_llm"]["budget_feasibility_pct"],
        tp["vanilla_llm"]["final_pass_rate_pct"],
        tp["vanilla_llm"]["hallucination_rate_pct"],
    ]
    o_vals = [
        tp["tripsense_neuro_symbolic_rag"]["entity_grounding_pct"],
        tp["tripsense_neuro_symbolic_rag"]["budget_feasibility_pct"],
        tp["tripsense_neuro_symbolic_rag"]["final_pass_rate_pct"],
        tp["tripsense_neuro_symbolic_rag"]["hallucination_rate_pct"],
    ]
    x = np.arange(len(metrics_tp))
    w = 0.34
    b1 = ax1.bar(x - w / 2, v_vals, width=w, color=C_AGREE, edgecolor=C_DARK, label="Unconstrained Baseline")
    b2 = ax1.bar(x + w / 2, o_vals, width=w, color=C_ECO, edgecolor=C_DARK, label="TripSense Neuro-Symbolic Verifier")
    for b, v in zip(b1, v_vals):
        ax1.text(b.get_x() + b.get_width() / 2, v + 1.8, f"{v:.1f}%", ha="center", fontsize=7.3)
    for b, v in zip(b2, o_vals):
        ax1.text(b.get_x() + b.get_width() / 2, v + 1.8, f"{v:.1f}%", ha="center", fontsize=7.3, fontweight="bold", color=C_ECO)
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics_tp, fontsize=7.8)
    ax1.set_ylim(0, 114)
    ax1.set_ylabel("Percentage (%) across 180 Tasks")
    ax1.set_title(f"(A) TravelPlanner Verification (Verify Time = {tp['avg_verify_ms']:.3f} ms/task)")
    ax1.legend(loc="upper right", fontsize=7.3)

    # Panel B: Bangladesh 5-City Eco & Gini Pilot
    cnames = [r["city"] for r in bd]
    cx = np.arange(len(cnames))
    eco_v = [r["fairnet_eco_score_pct"] for r in bd]
    ginis = [r["fairnet_gini"] for r in bd]
    bars_e = ax2.bar(cx, eco_v, width=0.46, color=C_ECO, edgecolor=C_DARK, alpha=0.88, label="Mean Top-5 Eco Score (%)")
    for b, v in zip(bars_e, eco_v):
        ax2.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.1f}%", ha="center", fontsize=7.4, fontweight="bold", color=C_ECO)
    ax2.set_xticks(cx)
    ax2.set_xticklabels(cnames, fontsize=8.0)
    ax2.set_ylim(0, 106)
    ax2.set_ylabel("Mean Eco Score (%)", color=C_ECO)

    ax2_r = ax2.twinx()
    ax2_r.plot(cx, ginis, "o-", color=C_OURS, lw=2.0, ms=6.5, label="FairNet v3 Gini (Right)")
    ax2_r.set_ylabel("Group Gini Inequality (Lower Better)", color=C_OURS)
    ax2_r.set_ylim(0.0, 0.12)
    ax2_r.grid(False)
    ax2.set_title("(B) Field Pilot Audit Across 5 Bangladeshi Destinations")
    l1, lb1 = ax2.get_legend_handles_labels()
    l2, lb2 = ax2_r.get_legend_handles_labels()
    ax2.legend(l1 + l2, lb1 + lb2, loc="lower left", fontsize=7.3)

    plt.tight_layout()
    _save(fig, "fig9_travelplanner_and_bd_pilot")


def fig10_training_and_latency(data):
    hist = data["fairnet_training"]["history"]
    ms = data["multi_seed_stability"]
    comp = data["group_consensus_comparison"]
    lat = data["latency_profile"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 4.8))

    # Panel A: Training Convergence
    eps = [h["epoch"] for h in hist]
    ax1.plot(eps, [h["val_ndcg10"] for h in hist], "o-", color=C_OURS, lw=2.1, ms=4.5, label="Val NDCG@10 (Left)")
    ax1.plot(eps, [h["val_min_sat"] for h in hist], "s--", color=C_ECO, lw=1.7, ms=4.0, label="Val MinSat (Left)")
    ax1.set_xlabel("Training Epoch")
    ax1.set_ylabel("Validation NDCG@10 / MinSat")
    ax1_r = ax1.twinx()
    ax1_r.plot(eps, [h["train_loss"] for h in hist], "^:", color=C_AGREE, lw=1.8, ms=4.2, label="Dual-Path Pareto Loss (Right)")
    ax1_r.set_ylabel("Training Loss", color=C_AGREE)
    ax1_r.grid(False)
    ax1.set_title(f"(A) FairNet v3 Convergence (Best Val = {data['fairnet_training']['best_val_ndcg10']:.4f})")
    l1, lb1 = ax1.get_legend_handles_labels()
    l2, lb2 = ax1_r.get_legend_handles_labels()
    ax1.legend(l1 + l2, lb1 + lb2, loc="center right", fontsize=7.3)

    # Panel B: 5-Seed Stability Comparison across Top 5 Models
    models_ms = ["fairnet_v3", "lgbm", "groupim", "agree", "lambdarank"]
    labels_ms = ["FairNet v3\n(Ours)", "LightGBM\nGBDT", "GroupIM\n(SIGIR'20)", "AGREE\n(SIGIR'18)", "LGBM\nLambdaRank"]
    cols_ms = [C_OURS, C_LGBM, C_SKY, C_AGREE, C_MLP]
    means = [ms[m]["ndcg10_mean"] for m in models_ms]
    stds = [ms[m]["ndcg10_std"] for m in models_ms]
    g_means = [ms[m]["gini_index_mean"] for m in models_ms]

    mx = np.arange(len(models_ms))
    bars_m = ax2.bar(mx, means, yerr=stds, capsize=4, width=0.52, color=cols_ms, edgecolor=C_DARK, lw=0.6)
    for b, mval, sval, gval in zip(bars_m, means, stds, g_means):
        ax2.text(b.get_x() + b.get_width() / 2, mval + sval + 0.010, f"{mval:.3f}\n(G={gval:.3f})", ha="center", va="bottom", fontsize=7.1, fontweight="bold")
    ax2.set_xticks(mx)
    ax2.set_xticklabels(labels_ms, fontsize=7.8)
    ax2.set_ylim(0.32, 0.62)
    ax2.set_ylabel("5-Seed Mean Test NDCG@10 (± Std)")
    ax2.set_title(f"(B) 5-Seed Stability & Runtime ({lat['gpu_ms_per_100_cands']}ms GPU / {lat['cpu_ms_per_100_cands']}ms CPU)")

    plt.tight_layout()
    _save(fig, "fig10_training_and_latency")


def main():
    data = json.load(open(METRICS_PATH, "r", encoding="utf-8"))
    fig1_architecture_overview(data)
    fig2_model_benchmark_and_cd(data)
    fig3_pareto_and_sensitivity(data)
    fig4_ablation_and_scaling(data)
    fig5_multicontinent_and_tripworld(data)
    fig6_xai_faithfulness_benchmark(data)
    fig7_xai_concordance_and_casestudy(data)
    fig8_active_swipe_and_nash(data)
    fig9_travelplanner_and_bd_pilot(data)
    fig10_training_and_latency(data)
    print(f"[DONE] All 10 vector PDF + 300-DPI PNG figures saved to {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
