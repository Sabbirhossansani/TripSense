<p align="center">
  <img src="assets/tripsense-banner.svg" alt="TripSense — Neural Group Travel Consensus & Sustainable Expedition Engine" width="100%" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-121715?style=for-the-badge&logo=python&logoColor=F7F4EE" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/PyTorch-GeoFairFormer_v3-D94E28?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch GeoFairFormer v3" />
  <img src="https://img.shields.io/badge/Backbones-CLIP_%7C_SigLIP_%7C_BGE-1F4B3E?style=for-the-badge" alt="CLIP SigLIP BGE" />
  <img src="https://img.shields.io/badge/Transfer-5_Continents_%2B_TripWorld-121715?style=for-the-badge" alt="5 Continents + TripWorld" />
  <img src="https://img.shields.io/badge/XAI-5--Paradigm_E2E_%2B_Nash-1F4B3E?style=for-the-badge" alt="5-Paradigm E2E XAI" />
</p>

<p align="center">
  <a href="https://vercel.com/new/clone?repository-url=https://github.com/Sabbirhossansani/TripSense">
    <img src="https://vercel.com/button" alt="Deploy to Vercel" />
  </a>
</p>

# TripSense-FairNet v3 (GeoFairFormer) — Spectral-Gated $O(D)$-Invariant Group Travel Consensus & Verifiable XAI Platform

**Author:** [Sabbirhossansani](https://github.com/Sabbirhossansani) (`sani2305101776@diu.edu.bd`) — Department of Software Engineering, Daffodil International University

**Research Manuscripts, Elsevier Package & Defense Kit:**
- [Elsevier 2-Column Journal PDF (`elsarticle final,5p,twocolumn`, 12 pages)](docs/TripSense_Elsevier_2Col_Manuscript.pdf) • [Elsevier Submission LaTeX ZIP (`.tex`, `.bbl`, `.bib`, Anonymous Review, Highlights, Title Page, 10 Vector Figures)](docs/TripSense_Elsevier_Submission.zip)
- [Elsevier 2-Column LaTeX Source](docs/TripSense_Elsevier_2Col_Manuscript.tex) • [BibTeX References (`45` Entries)](docs/references.bib)
- [Q1 Journal Manuscript (Markdown)](docs/TripSense_Q1_Manuscript.md) • [Word (.docx) with All 10 Figures](docs/TripSense_Q1_Manuscript.docx) • [Thesis Defense & Reviewer Q&A Guide](docs/Thesis_Defense_Prep_Guide.md)
- [Publication Figures (300-DPI PNG & Vector PDF)](docs/q1_figures/)

---

## Key Innovations (`TripSense-FairNet v3 / GeoFairFormer`)

**TripSense-FairNet v3** (`109,612` parameters) solves the **Out-of-Town & Cross-City Sustainable Group Travel Trilemma** without target-city retraining:

1. **Dual-Path Spectral-Gated Architecture:** Separates a strictly orthogonal-invariant consensus backbone (**Stream 1**: `19-d` geometric tokens + `MemberGramSAB` + 4-head Cross-Attention + Rawlsian Soft-Min; **Stream 2**: `15-d` Relational Highway) from an additive semantic Hadamard adapter (**Stream 3**) modulated by an **unsupervised top-48 SVD Spectral-Support OOD Gate** $\gamma(\mathcal{C})$ ($\gamma = 0.7545$ in Sydney vs. $0.0004\text{--}0.0926$ across distant linguistic manifolds).
2. **Multi-Objective Dual-Path Pareto InfoNCE:** Jointly optimizes 20-negative InfoNCE ($\tau=0.20$), differentiable Gini dispersion, Soft-Slate Rawlsian floor protection, and Eco-Exposure regularization (`5.03 ms` GPU / `7.24 ms` CPU per 100 candidates).
3. **End-to-End 5-Paradigm Faithful XAI & Nash Recourse:** Reconstructs complete model attributions (`MAE = 3.3e-5`), leading Expected Gradients, Input×Gradient, Vanilla Saliency, and Random masking across all 5 faithfulness metrics (`Comp@3 = 0.0719`, `5.33×` random, `InsAUC = 0.6075`, `DelAUC = 0.5482`), alongside `+6.39%` Nash counterfactual recourse welfare gains and `100.0%` *TravelPlanner* hard budget feasibility (`0.898 ms/task`).

---

## Empirical Q1 Benchmark Results

Executed deterministically on **CUDA (`NVIDIA GeForce RTX 3050 6GB Laptop GPU`, `2205.05s` full experimental suite)** across zero-leakage chronological splits of `CRUISEResearchGroup/Massive-STEPS` (`Sydney`: `29,900` check-ins, `8,189` venues, `1,200` groups -> `840` train / `180` val / `180` test; `Melbourne`, `Tokyo`, `New-York`, `Istanbul`, `São Paulo`: `160` zero-shot test groups each), the independent 2026 `CRUISEResearchGroup/TripWorld` out-of-town benchmark (`Osaka`, `419,254` check-in/hometown rows, `77,500` POIs, `200` test groups), `osunlp/TravelPlanner` (`180` tasks), and a 5-city Bangladesh pilot (`43` regional POIs).

### 1. Primary 15-Model Comparison (`Massive-STEPS-Sydney`, `180` Test Groups)

| Model / Strategy | NDCG@5 ↑ | NDCG@10 [95% CI] ↑ | Hit@10 ↑ | MRR@10 ↑ | Gini ↓ | MinSat ↑ | Eco Cov. ↑ | Rank ↓ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Popularity | `0.2487` | `0.3006 [0.264, 0.337]` | `73.89%` | `0.3945` | `0.0696` | `38.21%` | `32.00%` | `10.331` |
| Average Cosine | `0.1952` | `0.2437 [0.210, 0.280]` | `66.67%` | `0.3366` | `0.0808` | `45.97%` | **`63.44%`** | `10.650` |
| Least-Misery | `0.1574` | `0.1946 [0.165, 0.228]` | `58.89%` | `0.2687` | **`0.0635`** | `45.92%` | `60.11%` | `11.622` |
| Borda Count | `0.1835` | `0.2215 [0.191, 0.255]` | `62.78%` | `0.3079` | `0.0708` | **`46.31%`** | `60.67%` | `11.053` |
| DeepSets (NeurIPS'17) | `0.3248` | `0.4066 [0.366, 0.448]` | `86.67%` | `0.4769` | `0.0668` | `39.16%` | `39.00%` | `7.878` |
| AGREE (SIGIR'18) | `0.3234` | `0.4089 [0.368, 0.452]` | `86.11%` | `0.4815` | `0.0712` | `38.15%` | `31.89%` | `7.861` |
| MoSAN (SIGIR'19) | `0.3680` | `0.4508 [0.412, 0.489]` | `90.00%` | `0.5100` | `0.0652` | `40.39%` | `40.00%` | `6.550` |
| Set-Transformer (ICML'19) | `0.3390` | `0.4145 [0.376, 0.452]` | `88.89%` | `0.4836` | `0.0677` | `40.20%` | **`42.44%`** | `7.636` |
| GroupIM (SIGIR'20) | `0.3290` | `0.4257 [0.388, 0.466]` | `90.56%` | `0.4735` | `0.0724` | `39.45%` | `38.56%` | `7.464` |
| GroupMLP | `0.3744` | `0.4538 [0.415, 0.492]` | **`92.22%`** | `0.5202` | `0.0705` | `40.60%` | `36.11%` | `6.375` |
| Random Forest | `0.3874` | `0.4493 [0.410, 0.488]` | `88.89%` | `0.5483` | `0.0697` | `41.66%` | `32.11%` | `6.514` |
| HistGBDT | `0.3758` | `0.4549 [0.417, 0.497]` | `87.22%` | `0.5425` | `0.0723` | `41.61%` | `38.89%` | `6.744` |
| LightGBM GBDT | `0.3899` | `0.4649 [0.425, 0.504]` | `89.44%` | `0.5641` | `0.0703` | `41.63%` | `36.00%` | `6.272` |
| LightGBM LambdaRank | `0.3242` | `0.3830 [0.342, 0.423]` | `82.22%` | `0.5399` | `0.0727` | `41.10%` | `32.44%` | `8.256` |
| **TripSense-FairNet v3 (Ours)** | **`0.4955`** | **`0.5567 [0.512, 0.596]`** | `91.67%` | **`0.6844`** | **`0.0642`** | **`41.87%`** | `40.67%` | **`4.794`** |

- **Friedman & Holm-Bonferroni:** $\chi^2 = 558.316$ ($p = 3.894 \times 10^{-110}$, Nemenyi $\text{CD}_{0.05} = 1.599$); Holm-Bonferroni $p < 0.0001$ across all 14 baselines.
- **Multi-Backbone & 5-Seed Stability:** Leads `GroupIM` and `LambdaRank` across `CLIP` (`0.5567`), `Google SigLIP` (`0.5183`, `93.33%` Hit@10), and `BAAI BGE-base` (`0.4880`, `45.67%` Eco); 5-seed mean `0.5145 ± 0.0241` (`Gini 0.0651 ± 0.0012`).

### 2. Zero-Shot 5-Continent Transfer & 2026 *TripWorld* Out-of-Town Validation

| Unseen City / Dataset | AGREE (ZS) | MoSAN (ZS) | GroupIM (ZS) | LightGBM Cls (ZS) | LambdaRank (ZS) | FairNet v3 (ZS) NDCG@10 | FairNet Gini ↓ | FairNet Eco ↑ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Melbourne** (`2,522` POIs) | `0.2362` | `0.2348` | `0.2261` | `0.3146` | `0.3034` | **`0.3203`** | `0.0641` | **`53.75%`** |
| **Tokyo** (`1,183` POIs) | `0.3190` | `0.2746` | `0.2903` | `0.2921` | `0.3344` | **`0.3366`** | `0.0728` | `61.12%` |
| **New-York** (`9,572` POIs) | `0.2410` | `0.2390` | `0.2432` | `0.3130` | `0.2944` | **`0.3358`** | **`0.0637`** | `48.62%` |
| **Istanbul** (`5,880` POIs) | `0.3518` | `0.3635` | `0.3264` | `0.3596` | **`0.4311`** | **`0.3873`** *(Best Neural/Cls)* | `0.0872` | `34.62%` |
| **São Paulo** (`7,808` POIs) | `0.3869` | `0.3544` | `0.3533` | `0.3826` | `0.3995` | **`0.4126`** | `0.0772` | `45.50%` |
| ***TripWorld*-Osaka** (`77,500` POIs) | `0.4918` | `0.4909` | `0.4587` | `0.4926` | `0.4778` | **`0.5891`** (`MRR 0.7703`) | `0.0589` | `48.00%` |

### 3. 10-Variant Ablation, 5-Paradigm XAI & *TravelPlanner* Verification

- **Ablations:** Removing Spectral OOD Gate lifts Sydney `+0.0099` (`0.5666`) while collapsing 5-city external mean `0.3585 -> 0.3371` (`-0.0214`); removing Hadamard drops Sydney `-0.1678`, Cross-Attention `-0.0547`, MemberGramSAB `-0.0336`, InfoNCE `-0.1347`, CLIP semantics `-0.2161`.
- **5-Paradigm E2E XAI ($N=240$):** IG **Comp@3 = `0.0719`** (`5.33×` random `0.0135`), **Suff@3 = `0.0272`**, **AOPC = `0.0658`**, **InsAUC = `0.6075`**, **DelAUC = `0.5482`**, **Completeness MAE = `3.3e-5`**, IG vs. ExpectedGrad $\rho = 0.9750$ ($p = 7.14\times 10^{-10}$).
- **`osunlp/TravelPlanner` (`180` Tasks, `0.898 ms`/task):** `100.0%` Hard Budget Feasibility • `53.3%` Strict Final Pass Rate vs. `16.1%` (Vanilla LLM) and `0.6% / 4.4%` (GPT-3.5 / GPT-4).

---

## Publication Figures (`300 DPI`)

<p align="center">
  <img src="docs/q1_figures/fig2_model_benchmark_and_cd.png" alt="15-Model Benchmark and Friedman-Nemenyi CD Diagram" width="49%" />
  <img src="docs/q1_figures/fig5_multicontinent_and_tripworld.png" alt="5-Continent Zero-Shot Transfer and 2026 TripWorld-Osaka Validation" width="49%" />
</p>
<p align="center">
  <img src="docs/q1_figures/fig6_xai_faithfulness_benchmark.png" alt="End-to-End 5-Paradigm XAI Deletion and Insertion Faithfulness Curves" width="49%" />
  <img src="docs/q1_figures/fig9_travelplanner_and_bd_pilot.png" alt="TravelPlanner Neuro-Symbolic Verification and Bangladesh 5-City Pilot" width="49%" />
</p>

---

## Local Development, Reproduction & Testing

```bash
# 1. Reproduce complete Q1 multi-backbone, 5-seed, ablation, TripWorld, and Multi-XAI benchmarks
python -u backend/ml/train_fairnet.py

# 2. Regenerate all 10 300-DPI Q1 figures, Word manuscript & Elsevier submission ZIP
python scripts/generate_q1_figures.py
python scripts/build_q1_docx.py
python scripts/build_elsevier_package.py

# 3. Sync offline demo catalog & rebuild frontend showcase
python scripts/sync_frontend_demo_data.py
cd frontend && npm install && npm run lint && npm run build && cd ..

# 4. Run all 5 automated test suites
python backend/test_backend.py
python test_phase2_fixes.py
python test_phase2_integration.py
python test_user_journey_e2e.py
python test_blueprint_b_ml.py
```

---

## Citation

```bibtex
@article{sani2026tripsense,
  author  = {Sani, Sabbir Hossan},
  title   = {TripSense-FairNet v3 (GeoFairFormer): Spectral-Gated O(D)-Invariant Consensus, End-to-End Faithful Explainable AI, and Nash Counterfactual Recourse for Sustainable Group Travel Planning},
  journal = {Expert Systems with Applications (Preprint)},
  year    = {2026},
  url     = {https://github.com/Sabbirhossansani/TripSense}
}
```
