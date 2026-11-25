"""
Builds a publication-formatted Microsoft Word (.docx) Q1 manuscript
directly from backend/ml/artifacts/q1_benchmark_results.json and docs/q1_figures/*.png.
"""

import os
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
METRICS_PATH = os.path.join(ROOT_DIR, "backend", "ml", "artifacts", "q1_benchmark_results.json")
FIG_DIR = os.path.join(ROOT_DIR, "docs", "q1_figures")
OUT_DOCX = os.path.join(ROOT_DIR, "docs", "TripSense_Q1_Manuscript.docx")


def _add_heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for r in h.runs:
        r.font.name = "Times New Roman"
        r.font.color.rgb = RGBColor(15, 23, 42)
    return h


def _add_table(doc, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = str(h)
        for p in hdr_cells[i].paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(9)
    for row in rows:
        rc = table.add_row().cells
        for i, val in enumerate(row):
            rc[i].text = str(val)
            for p in rc[i].paragraphs:
                for r in p.runs:
                    r.font.size = Pt(9)
    doc.add_paragraph("")


def _add_figure(doc, filename, caption, width_in=6.2):
    fpath = os.path.join(FIG_DIR, filename)
    if os.path.exists(fpath):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(fpath, width=Inches(width_in))
        cp = doc.add_paragraph(caption)
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in cp.runs:
            r.italic = True
            r.font.size = Pt(9)


def main():
    data = json.load(open(METRICS_PATH, "r", encoding="utf-8"))
    comp = data["group_consensus_comparison"]
    st = data["statistical_tests"]
    ms = data["multi_seed_stability"]
    abl = data["ablation_study"]
    ext = data["external_cross_city_validation"]
    bd = data["bangladesh_5city_pilot"]
    mx = data["multi_xai_evaluation"]
    ig = mx["integrated_gradients"]
    conc = mx["cross_xai_concordance"]
    attn = mx["attention_and_counterfactual_audit"]["cross_attention_audit"]
    nash = mx["attention_and_counterfactual_audit"]["nash_counterfactual_recourse"]
    tp = data["travelplanner_rag_evaluation"]

    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)

    title = doc.add_heading(
        "TripSense-FairNet v2: Rotation-Invariant Dual-Stream Consensus, Nash Counterfactual Recourse, and Verifiably Faithful Explainable AI for Sustainable Group Travel Planning",
        level=0,
    )
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    auth = doc.add_paragraph("Sabbir Hossan Sani (sani2305101776@diu.edu.bd)\nDepartment of Software Engineering, Daffodil International University, Dhaka, Bangladesh")
    auth.alignment = WD_ALIGN_PARAGRAPH.CENTER

    _add_heading(doc, "Abstract", level=1)
    ours = comp["TripSense-FairNet v2 (Ours)"]
    lgbm = comp["LightGBM GBDT"]
    doc.add_paragraph(
        f"Group travel planning demands simultaneous optimization of collective ranking relevance, intra-group satisfaction equity, "
        f"low-carbon SME sustainability, deterministic budget feasibility, and auditable explainability. We present TripSense-FairNet v2, "
        f"a {data['num_parameters']:,}-parameter rotation-invariant dual-stream consensus network over isotropic CLIP ViT-B/32 representations. "
        f"Across a zero-leakage chronological Massive-STEPS-Sydney benchmark ({data['datasets']['checkins_loaded']:,} check-ins, "
        f"{data['datasets']['unique_venues']:,} venues, {data['datasets']['total_groups']:,} groups), FairNet v2 achieves "
        f"NDCG@10 = {ours['ndcg10']:.4f} (95% CI [{ours['ndcg10_ci95'][0]:.4f}, {ours['ndcg10_ci95'][1]:.4f}]), "
        f"Hit@10 = {ours['hit10']:.4f}, Gini = {ours['gini_index']:.4f}, and Eco Coverage = {ours['eco_coverage_pct']:.2f}%, "
        f"outperforming LightGBM ({lgbm['ndcg10']:.4f}, Holm-Bonferroni p = {lgbm['holm_p_ndcg10']:.5f}), GroupMLP ({comp['GroupMLP']['ndcg10']:.4f}), "
        f"and AGREE ({comp['AGREE (SIGIR\'18)']['ndcg10']:.4f}; Friedman chi2 = {st['friedman_chi2']:.3f}, p = {st['friedman_p_value']:.3e}). "
        f"In zero-shot transfer without retraining, FairNet v2 outperforms LightGBM in Melbourne ({ext['Melbourne']['models']['TripSense-FairNet v2 (Zero-Shot)']['ndcg10']:.4f} vs. {ext['Melbourne']['models']['LightGBM (Zero-Shot)']['ndcg10']:.4f}) "
        f"and Tokyo ({ext['Tokyo']['models']['TripSense-FairNet v2 (Zero-Shot)']['ndcg10']:.4f} vs. {ext['Tokyo']['models']['LightGBM (Zero-Shot)']['ndcg10']:.4f}) "
        f"and remains competitive in New-York ({ext['New-York']['models']['TripSense-FairNet v2 (Zero-Shot)']['ndcg10']:.4f}, lowest Gini {ext['New-York']['models']['TripSense-FairNet v2 (Zero-Shot)']['gini_index']:.4f}). "
        f"Multi-XAI verification establishes Integrated Gradients Completeness MAE = {ig['completeness_mae']:.1e}, "
        f"{ig['faithfulness_ratio_over_random']:.2f}x Perturbation Comprehensiveness over random masking, "
        f"{attn['lowest_budget_member_mean_attn']:.4f} attention allocation to lowest-budget companions, +{nash['mean_nash_welfare_gain_pct']:.2f}% Nash welfare gain, "
        f"and {tp['tripsense_neuro_symbolic_rag']['budget_feasibility_pct']:.1f}% TravelPlanner hard budget feasibility ({tp['avg_verify_ms']:.3f} ms)."
    )

    _add_heading(doc, "1. Introduction & Architecture", level=1)
    doc.add_paragraph(
        "Group recommender systems must reconcile heterogeneous member tastes and disparate budgets while avoiding popularity concentration at over-visited venues. "
        "TripSense-FairNet v2 removes city-specific coordinate memorization using unsupervised All-but-the-Top CLIP mean-centering, rotation-invariant geometric member tokens, "
        "a bounded low-rank Hadamard semantic residual (0.35*tanh), a 15-d relational highway without input LayerNorm distortion, and Pareto InfoNCE training."
    )
    _add_figure(doc, "fig1_architecture_overview.png", "Figure 1. TripSense-FairNet v2 Dual-Stream, Multi-XAI, and Neuro-Symbolic Architecture.")

    _add_heading(doc, "2. Primary Benchmark Comparison (Massive-STEPS-Sydney)", level=1)
    headers_m = ["Model", "NDCG@5", "NDCG@10 [95% CI]", "Hit@10", "Gini (low)", "MinSat", "Eco (%)", "Rank"]
    rows_m = []
    for k, v in comp.items():
        rows_m.append([
            k, f"{v['ndcg5']:.4f}", f"{v['ndcg10']:.4f} [{v['ndcg10_ci95'][0]:.3f}, {v['ndcg10_ci95'][1]:.3f}]",
            f"{v['hit10']:.4f}", f"{v['gini_index']:.4f}", f"{v['min_member_sat']:.4f}", f"{v['eco_coverage_pct']:.2f}%", f"{v['friedman_rank']:.3f}"
        ])
    _add_table(doc, headers_m, rows_m)
    _add_figure(doc, "fig2_model_benchmark_and_cd.png", "Figure 2. 10-Model Ranking Accuracy and Friedman-Nemenyi Post-Hoc Rank Diagram.")
    doc.add_paragraph(
        f"Across 5 seeds ({ms['seeds']}), FairNet v2 achieves NDCG@10 = {ms['ndcg10_mean']:.4f} ± {ms['ndcg10_std']:.4f} and Gini = {ms['gini_mean']:.4f} ± {ms['gini_std']:.4f}, "
        f"vs. LightGBM ({ms['lgbm']['ndcg10_mean']:.4f} ± {ms['lgbm']['ndcg10_std']:.4f}) and AGREE ({ms['agree']['ndcg10_mean']:.4f} ± {ms['agree']['ndcg10_std']:.4f}). "
        f"Scoring latency is {data['latency_profile']['gpu_ms_per_100_cands']} ms (GPU) and {data['latency_profile']['cpu_ms_per_100_cands']} ms (CPU) per 100 candidates."
    )

    _add_heading(doc, "3. Pareto Trade-Off, Ablation Study & Group Scaling", level=1)
    _add_figure(doc, "fig3_fairness_accuracy_pareto.png", "Figure 3. Accuracy vs. Fairness Pareto Frontier and Eco-Sustainability Synergy.")
    _add_table(doc, ["Variant", "NDCG@10", "Delta NDCG@10", "Hit@10", "Gini", "Eco (%)"], [
        [r["variant"], f"{r['ndcg10']:.4f}", f"{r['delta_ndcg10']:+.4f}", f"{r['hit10']:.4f}", f"{r['gini_index']:.4f}", f"{r['eco_coverage_pct']:.2f}%"]
        for r in abl
    ])
    _add_figure(doc, "fig4_ablation_and_scaling.png", "Figure 4. 7-Variant Component Ablation and Group Cardinality Scaling (|G| = 2..5).")

    _add_heading(doc, "4. Zero-Shot Cross-City Validation & Bangladesh Pilot", level=1)
    rows_c = []
    for cname, cdata in ext.items():
        for mk, mv in cdata["models"].items():
            if mk in ("Average Cosine", "AGREE (Zero-Shot)", "LightGBM (Zero-Shot)", "TripSense-FairNet v2 (Zero-Shot)"):
                rows_c.append([cname, mk, f"{mv['ndcg10']:.4f}", f"{mv['hit10']:.4f}", f"{mv['gini_index']:.4f}", f"{mv['eco_coverage_pct']:.2f}%"])
    _add_table(doc, ["City", "Model", "NDCG@10", "Hit@10", "Gini", "Eco (%)"], rows_c)
    _add_table(doc, ["BD City", "Spots", "FairNet Gini", "AvgCos Gini", "MinSat", "Eco (%)"], [
        [r["city"], r["num_spots"], f"{r['fairnet_gini']:.4f}", f"{r['avg_cos_gini']:.4f}", f"{r['fairnet_min_sat']:.4f}", f"{r['fairnet_eco_score_pct']:.1f}%"]
        for r in bd
    ])
    _add_figure(doc, "fig5_cross_city_transfer.png", "Figure 5. Zero-Shot Transfer Across Melbourne, Tokyo, and New-York & Bangladesh 5-City Pilot.")

    _add_heading(doc, "5. Multi-Paradigm XAI, Active Swipe & Neuro-Symbolic Verification", level=1)
    doc.add_paragraph(
        f"Integrated Gradients satisfies Completeness MAE = {ig['completeness_mae']:.1e} (max {ig['completeness_max']:.1e}). "
        f"Comprehensiveness@k3 = {ig['comprehensiveness_k3']:.4f} ({ig['faithfulness_ratio_over_random']:.2f}x random {ig['random_baseline_comp_k3']:.4f}; AOPC = {ig['aopc_score']:.4f}), "
        f"and Sufficiency Gap tightens from {ig['sufficiency_curve']['k1']:.4f} (k=1) to {ig['sufficiency_curve']['k7']:.4f} (k=7). "
        f"Cross-method Spearman rho = {conc['ig_vs_treeshap_spearman_rho']:.4f} (IG vs. TreeSHAP) and {conc['ig_vs_permutation_spearman_rho']:.4f} (IG vs. Permutation). "
        f"Cross-Attention allocates {attn['lowest_budget_member_mean_attn']:.4f} weight to the lowest-budget member vs. {attn['highest_budget_member_mean_attn']:.4f} to the highest-budget peer. "
        f"Nash Veto Recourse raises MinSat {nash['mean_min_member_sat_before']:.4f} -> {nash['mean_min_member_sat_after']:.4f} and cuts Gini {nash['mean_gini_before']:.4f} -> {nash['mean_gini_after']:.4f} (+{nash['mean_nash_welfare_gain_pct']:.2f}% welfare)."
    )
    _add_figure(doc, "fig6_multi_xai_faithfulness.png", "Figure 6. Multi-Paradigm Attribution Concordance and Perturbation Faithfulness Curves.")
    _add_figure(doc, "fig7_swipe_and_nash_recourse.png", "Figure 7. Cold-Start Bayesian EIG Probing & Nash Bargaining Recourse Equity.")
    _add_figure(doc, "fig8_travelplanner_neurosymbolic.png", "Figure 8. TravelPlanner Neuro-Symbolic Verification vs. ICML 2024 Baselines.")

    doc.save(OUT_DOCX)
    print(f"[DONE] Saved Q1 DOCX manuscript -> {OUT_DOCX}", flush=True)


if __name__ == "__main__":
    main()
