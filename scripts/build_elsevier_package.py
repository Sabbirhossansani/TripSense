"""
Compiles the authentic Elsevier 2-Column PDF (elsarticle 5p,times,twocolumn) via Tectonic,
renders page verification thumbnails via PyMuPDF (fitz), generates all mandatory Elsevier
ESWA companion files (Highlights <= 85 chars, separate Title Page, Anonymous Review .tex,
Declaration of Competing Interest, compiled .bbl), and packages a verified self-contained
Elsevier LaTeX submission ZIP archive:
  - docs/TripSense_Elsevier_2Col_Manuscript.pdf
  - docs/TripSense_Elsevier_Submission.zip
"""

import os
import re
import sys
import shutil
import zipfile
import tempfile
import subprocess
from docx import Document
from docx.shared import Pt
import fitz  # PyMuPDF

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
FIG_DIR = os.path.join(DOCS_DIR, "q1_figures")
MAIN_TEX_NAME = "TripSense_Elsevier_2Col_Manuscript.tex"
MAIN_TEX_PATH = os.path.join(DOCS_DIR, MAIN_TEX_NAME)
BIB_PATH = os.path.join(DOCS_DIR, "references.bib")
OUT_PDF = os.path.join(DOCS_DIR, "TripSense_Elsevier_2Col_Manuscript.pdf")
OUT_ZIP = os.path.join(DOCS_DIR, "TripSense_Elsevier_Submission.zip")

TECTONIC_EXE = os.environ.get(
    "TECTONIC_EXE",
    r"C:\Users\Sani\.gemini\antigravity\brain\9f8c7f4c-c898-41fb-bcb2-db843d3d4d3a\scratch\tectonic\tectonic.exe",
)
PREVIEW_DIR = r"C:\Users\Sani\.gemini\antigravity\brain\9f8c7f4c-c898-41fb-bcb2-db843d3d4d3a\scratch\pdf_pages"

# Elsevier ESWA mandatory Highlights: 3-5 bullets, strictly <= 85 chars each incl. spaces
HIGHLIGHTS = [
    "Rotation-invariant FairNet v2 eliminates cross-city embedding overfitting.",
    "Achieves 0.5394 NDCG@10 on Sydney, beating 9 baselines (Friedman p < 1e-104).",
    "Transfers zero-shot to Melbourne and Tokyo with top eco coverage (49.9-66.5%).",
    "Verifies IG Completeness (MAE 3e-6) and 3.43x perturbation faithfulness.",
    "Nash recourse boosts welfare +6.25% with 100% TravelPlanner budget feasibility.",
]


def _verify_highlights():
    for idx, line in enumerate(HIGHLIGHTS, 1):
        n = len(line)
        print(f"  [Highlight {idx}] ({n:2d}/85 chars) {line}", flush=True)
        assert n <= 85, f"Highlight {idx} exceeds Elsevier 85-char limit ({n} chars)!"


def _write_docx_lines(path: str, title: str, paragraphs):
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)
    doc.add_heading(title, level=1)
    for item in paragraphs:
        if isinstance(item, tuple) and item[0] == "bullet":
            doc.add_paragraph(item[1], style="List Bullet")
        elif isinstance(item, tuple) and item[0] == "heading":
            doc.add_heading(item[1], level=2)
        else:
            doc.add_paragraph(str(item))
    doc.save(path)


def _make_anonymous_tex(src_tex: str) -> str:
    """Creates a clean double-blind ESWA review version removing identifying metadata."""
    anon = src_tex
    anon = anon.replace(
        r"\author[diu]{Sabbir Hossan Sani\corref{cor1}}",
        r"\author[anon]{Anonymous Author(s)}",
    )
    anon = re.sub(r"\\ead\{[^}]+\}\n?", "", anon)
    anon = re.sub(r"\\cortext\[cor1\]\{[^}]+\}\n?", "", anon)
    anon = re.sub(
        r"\\affiliation\[diu\]\{.*?country=\{Bangladesh\}\}",
        r"\\affiliation[anon]{organization={Anonymized for Double-Blind Peer Review}}",
        anon,
        flags=re.S,
    )
    anon = re.sub(
        r"\\section\*\{CRediT Authorship Contribution Statement\}.*?\\section\*\{Declaration of Competing Interest\}",
        r"\\section*{Declaration of Competing Interest}",
        anon,
        flags=re.S,
    )
    anon = anon.replace(
        r"\url{https://github.com/Sabbirhossansani/TripSense}",
        r"[Anonymized Repository URL Available Upon Acceptance]",
    )
    return anon


def _compile_with_tectonic(workdir: str, tex_file: str, keep_intermediates: bool = True):
    cmd = [TECTONIC_EXE, "-X", "compile", tex_file]
    if keep_intermediates:
        cmd.append("--keep-intermediates")
    print(f"[Tectonic] Running: {' '.join(cmd)} (cwd={workdir})", flush=True)
    res = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.stdout:
        print(res.stdout[-1500:], flush=True)
    if res.returncode != 0:
        print(res.stderr[-2500:], flush=True)
        raise RuntimeError(f"Tectonic compilation failed for {tex_file} (exit {res.returncode})")
    return res


def main():
    assert os.path.exists(TECTONIC_EXE), f"Tectonic not found at {TECTONIC_EXE}"
    assert os.path.exists(MAIN_TEX_PATH), f"Main .tex not found at {MAIN_TEX_PATH}"
    _verify_highlights()

    # 1. Build inside a clean staging directory so we generate clean .pdf + .bbl without cluttering docs/
    stage_dir = tempfile.mkdtemp(prefix="tripsense_elsevier_")
    try:
        shutil.copy2(MAIN_TEX_PATH, os.path.join(stage_dir, MAIN_TEX_NAME))
        shutil.copy2(BIB_PATH, os.path.join(stage_dir, "references.bib"))
        shutil.copytree(FIG_DIR, os.path.join(stage_dir, "q1_figures"))

        # Compile main camera-ready 2-column Elsevier PDF + .bbl
        _compile_with_tectonic(stage_dir, MAIN_TEX_NAME, keep_intermediates=True)

        compiled_pdf = os.path.join(stage_dir, MAIN_TEX_NAME.replace(".tex", ".pdf"))
        compiled_bbl = os.path.join(stage_dir, MAIN_TEX_NAME.replace(".tex", ".bbl"))
        assert os.path.exists(compiled_pdf), "Compiled PDF missing!"
        assert os.path.exists(compiled_bbl), "Compiled .bbl missing!"

        # Check PDF page count and unresolved references
        doc_pdf = fitz.open(compiled_pdf)
        num_pages = len(doc_pdf)
        full_text = "\n".join(page.get_text("text") for page in doc_pdf)
        unresolved = re.findall(r"\[\?\]|\?\?", full_text)
        print(f"[Verify PDF] Pages: {num_pages} | Unresolved citations/refs: {len(unresolved)}", flush=True)
        if unresolved:
            raise RuntimeError(f"Unresolved LaTeX references found in PDF: {unresolved[:10]}")

        # Render every page to PNG in scratch/pdf_pages for visual inspection
        os.makedirs(PREVIEW_DIR, exist_ok=True)
        for old in os.listdir(PREVIEW_DIR):
            os.remove(os.path.join(PREVIEW_DIR, old))
        for pno in range(num_pages):
            pix = doc_pdf[pno].get_pixmap(dpi=165)
            pix.save(os.path.join(PREVIEW_DIR, f"page_{pno + 1:02d}.png"))
        doc_pdf.close()
        print(f"[Verify PDF] Rendered {num_pages} page PNG previews -> {PREVIEW_DIR}", flush=True)

        # Copy final compiled PDF and .bbl into docs/
        shutil.copy2(compiled_pdf, OUT_PDF)

        # 2. Generate Elsevier ESWA companion submission files inside zip_stage
        zip_stage = tempfile.mkdtemp(prefix="tripsense_elsevier_zip_")
        try:
            # Core LaTeX & BibTeX files
            src_tex = open(MAIN_TEX_PATH, "r", encoding="utf-8").read()
            shutil.copy2(MAIN_TEX_PATH, os.path.join(zip_stage, MAIN_TEX_NAME))
            shutil.copy2(compiled_bbl, os.path.join(zip_stage, MAIN_TEX_NAME.replace(".tex", ".bbl")))
            shutil.copy2(BIB_PATH, os.path.join(zip_stage, "references.bib"))
            shutil.copy2(compiled_pdf, os.path.join(zip_stage, "TripSense_Elsevier_2Col_Manuscript.pdf"))

            # Double-blind Anonymous Review version (+ compile check!)
            anon_name = "TripSense_Elsevier_Anonymous_Review.tex"
            anon_tex = _make_anonymous_tex(src_tex)
            with open(os.path.join(zip_stage, anon_name), "w", encoding="utf-8") as f:
                f.write(anon_tex)

            # Copy all figures (vector PDF + 300-DPI PNG)
            shutil.copytree(FIG_DIR, os.path.join(zip_stage, "q1_figures"))

            # Verify anonymous version also compiles cleanly and keep its .bbl too
            _compile_with_tectonic(zip_stage, anon_name, keep_intermediates=True)
            # Clean auxiliary build clutter (.aux, .log, .out, .fls, .blg) while keeping .bbl & .pdf
            for ext in (".aux", ".log", ".out", ".blg", ".toc", ".fdb_latexmk", ".synctex.gz"):
                for fname in list(os.listdir(zip_stage)):
                    if fname.endswith(ext):
                        os.remove(os.path.join(zip_stage, fname))

            # Separate Highlights (.txt + .docx)
            with open(os.path.join(zip_stage, "Highlights.txt"), "w", encoding="utf-8") as f:
                f.write("Highlights (Elsevier ESWA Submission — <= 85 characters per bullet)\n\n")
                for h in HIGHLIGHTS:
                    f.write(f"- {h}\n")
            _write_docx_lines(
                os.path.join(zip_stage, "Highlights.docx"),
                "Highlights",
                [("bullet", h) for h in HIGHLIGHTS],
            )

            # Separate Title Page (.tex + .docx) for Double-Blind Submission
            title_page_tex = r"""\documentclass[12pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{hyperref}
\begin{document}
\begin{center}
{\Large\bfseries TripSense-FairNet v2: Rotation-Invariant Dual-Stream Consensus, Nash Counterfactual Recourse, and Verifiably Faithful Explainable AI for Sustainable Group Travel Planning}\\[1.2em]
{\large Sabbir Hossan Sani$^{*}$}\\[0.5em]
Department of Software Engineering, Daffodil International University, Dhaka, Bangladesh\\[0.3em]
$^{*}$Corresponding author email: \texttt{sani2305101776@diu.edu.bd}
\end{center}
\vspace{1.5em}
\noindent\textbf{CRediT Authorship Contribution Statement:} \textbf{Sabbir Hossan Sani:} Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing -- original draft, Writing -- review \& editing, Visualization.\\[0.8em]
\noindent\textbf{Declaration of Competing Interest:} The author declares that there are no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.\\[0.8em]
\noindent\textbf{Funding:} This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.\\[0.8em]
\noindent\textbf{Data and Code Availability:} Source code, deterministic evaluation scripts, and artifacts are hosted at \url{https://github.com/Sabbirhossansani/TripSense}.
\end{document}
"""
            with open(os.path.join(zip_stage, "Title_Page.tex"), "w", encoding="utf-8") as f:
                f.write(title_page_tex)
            _write_docx_lines(
                os.path.join(zip_stage, "Title_Page.docx"),
                "Title Page — Expert Systems with Applications",
                [
                    "Manuscript Title: TripSense-FairNet v2: Rotation-Invariant Dual-Stream Consensus, Nash Counterfactual Recourse, and Verifiably Faithful Explainable AI for Sustainable Group Travel Planning",
                    "Author: Sabbir Hossan Sani (Corresponding Author)",
                    "Affiliation: Department of Software Engineering, Daffodil International University, Dhaka, Bangladesh",
                    "Corresponding Email: sani2305101776@diu.edu.bd",
                    ("heading", "CRediT Authorship Contribution Statement"),
                    "Sabbir Hossan Sani: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing - original draft, Writing - review & editing, Visualization.",
                    ("heading", "Declaration of Competing Interest"),
                    "The author declares that there are no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.",
                    ("heading", "Funding"),
                    "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.",
                    ("heading", "Data and Code Availability"),
                    "All code, deterministic evaluation harnesses, figure generators, and benchmark artifacts are available at https://github.com/Sabbirhossansani/TripSense.",
                ],
            )

            # Declaration of Interests text file
            with open(os.path.join(zip_stage, "Declaration_of_Interests.txt"), "w", encoding="utf-8") as f:
                f.write(
                    "Declaration of Competing Interest\n"
                    "=================================\n\n"
                    "The author (Sabbir Hossan Sani) declares that there are no known competing financial\n"
                    "interests or personal relationships that could have appeared to influence the work\n"
                    "reported in the manuscript titled:\n"
                    "\"TripSense-FairNet v2: Rotation-Invariant Dual-Stream Consensus, Nash Counterfactual\n"
                    "Recourse, and Verifiably Faithful Explainable AI for Sustainable Group Travel Planning\".\n"
                )

            # Submission Instructions README
            with open(os.path.join(zip_stage, "README_ELSEVIER_SUBMISSION.txt"), "w", encoding="utf-8") as f:
                f.write(
                    "TripSense-FairNet v2 — Elsevier LaTeX Submission Package (elsarticle 5p Two-Column)\n"
                    "==================================================================================\n\n"
                    "Contents:\n"
                    "1. TripSense_Elsevier_2Col_Manuscript.tex  : Full camera-ready 2-column Elsevier LaTeX source\n"
                    "2. TripSense_Elsevier_2Col_Manuscript.bbl  : Pre-compiled BibTeX bibliography (for Editorial Manager)\n"
                    "3. TripSense_Elsevier_2Col_Manuscript.pdf  : Compiled 2-column Elsevier journal PDF\n"
                    "4. TripSense_Elsevier_Anonymous_Review.tex : Double-blind anonymized manuscript for ESWA review\n"
                    "5. TripSense_Elsevier_Anonymous_Review.bbl : Pre-compiled bibliography for anonymized review\n"
                    "6. TripSense_Elsevier_Anonymous_Review.pdf : Compiled anonymized 2-column PDF\n"
                    "7. references.bib                          : Complete 26-entry BibTeX database\n"
                    "8. Title_Page.tex & Title_Page.docx        : Separate Elsevier Title Page (author, CRediT, COI)\n"
                    "9. Highlights.txt & Highlights.docx        : 5 mandatory ESWA Highlights (all <= 85 characters)\n"
                    "10. Declaration_of_Interests.txt           : Signed Conflict of Interest statement\n"
                    "11. q1_figures/*.pdf & *.png               : All 8 publication figures (vector PDF + 300-DPI PNG)\n\n"
                    "Compilation Command (Overleaf / TeX Live / MiKTeX):\n"
                    "  pdflatex TripSense_Elsevier_2Col_Manuscript.tex\n"
                    "  bibtex   TripSense_Elsevier_2Col_Manuscript\n"
                    "  pdflatex TripSense_Elsevier_2Col_Manuscript.tex\n"
                    "  pdflatex TripSense_Elsevier_2Col_Manuscript.tex\n"
                )

            # Create ZIP archive cleanly
            if os.path.exists(OUT_ZIP):
                os.remove(OUT_ZIP)
            with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
                for root, _, files in os.walk(zip_stage):
                    for fn in sorted(files):
                        full_p = os.path.join(root, fn)
                        arc_p = os.path.relpath(full_p, zip_stage).replace("\\", "/")
                        zf.write(full_p, arc_p)

            # 3. Round-Trip Verification: Extract ZIP into fresh temp dir and recompile from scratch!
            verify_dir = tempfile.mkdtemp(prefix="tripsense_zip_verify_")
            try:
                with zipfile.ZipFile(OUT_ZIP, "r") as zf:
                    names = zf.namelist()
                    zf.extractall(verify_dir)
                # Remove prebuilt pdf in verify_dir and compile fresh directly from extracted .tex
                os.remove(os.path.join(verify_dir, "TripSense_Elsevier_2Col_Manuscript.pdf"))
                _compile_with_tectonic(verify_dir, MAIN_TEX_NAME, keep_intermediates=False)
                rebuilt = os.path.join(verify_dir, "TripSense_Elsevier_2Col_Manuscript.pdf")
                assert os.path.exists(rebuilt) and os.path.getsize(rebuilt) > 100_000
                print(f"[ZIP Verified] Standalone extraction + fresh compile SUCCEEDED ({len(names)} files in ZIP)!", flush=True)
                print(f"[OUTPUT PDF] {OUT_PDF} ({os.path.getsize(OUT_PDF)/1024:.1f} KB, {num_pages} pages)", flush=True)
                print(f"[OUTPUT ZIP] {OUT_ZIP} ({os.path.getsize(OUT_ZIP)/1024:.1f} KB)", flush=True)
            finally:
                shutil.rmtree(verify_dir, ignore_errors=True)
        finally:
            shutil.rmtree(zip_stage, ignore_errors=True)
    finally:
        shutil.rmtree(stage_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
