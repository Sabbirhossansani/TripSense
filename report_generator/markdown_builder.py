"""
Markdown Builder for TripSense DIU CSE FYDP Final Report
Outputs docs/TripSense_FYDP_Final_Report.md
"""

import os
from . import front_matter
from . import chapter1
from . import chapter2
from . import chapter3
from . import chapter4
from . import chapter5
from . import chapter6

def format_table(headers, rows):
    col_widths = [len(h) for h in headers]
    for r in rows:
        for i, val in enumerate(r):
            lines = str(val).split("\n")
            max_l = max(len(l) for l in lines) if lines else 0
            if max_l > col_widths[i]:
                col_widths[i] = max_l

    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    separator_line = "|-" + "-|-".join("-" * col_widths[i] for i in range(len(headers))) + "-|"
    
    row_lines = []
    for r in rows:
        clean_row = [str(val).replace("\n", "<br>") for val in r]
        row_lines.append("| " + " | ".join(clean_row[i].ljust(col_widths[i]) for i in range(len(clean_row))) + " |")

    return "\n".join([header_line, separator_line] + row_lines)

def build_markdown(output_path):
    lines = []

    # Front Matter - Cover
    lines.append(f"# {front_matter.PROJECT_TITLE}\n\n")
    lines.append("## FINAL YEAR DESIGN PROJECT REPORT\n\n")
    lines.append("**Submitted in Partial Fulfillment of the Requirements for the Degree of**  \n"
                 "**Bachelor of Science in Computer Science and Engineering**\n\n---\n\n")

    lines.append("### Submitted By:\n")
    for s in front_matter.STUDENTS:
        lines.append(f"- **{s['name']}** (Student ID: {s['id']})  \n  {s['dept']}, {s['inst']}\n")

    lines.append("\n### Supervised By:\n")
    sup = front_matter.SUPERVISORS["supervisor"]
    cosup = front_matter.SUPERVISORS["co_supervisor"]
    lines.append(f"- **{sup['name']}**, {sup['designation']}  \n  {sup['dept']}, {sup['inst']}\n")
    lines.append(f"- **{cosup['name']}**, {cosup['designation']} (Co-Supervisor)  \n  {cosup['dept']}, {cosup['inst']}\n\n")

    lines.append("<p align=\"center\">\n"
                 "  <img src=\"figures/diu_logo.jpeg\" alt=\"Daffodil International University Logo\" width=\"140\"/>\n"
                 "</p>\n\n")

    lines.append(f"**Department of Computer Science and Engineering**  \n"
                 f"**Daffodil International University**, Dhaka, Bangladesh  \n"
                 f"*{front_matter.SUBMISSION_DATE}*\n\n---\n\n")

    # Approval
    lines.append("## APPROVAL\n\n")
    lines.append(front_matter.APPROVAL_TEXT + "\n\n")
    lines.append("### BOARD OF EXAMINERS\n\n")
    for b in front_matter.BOARD_OF_EXAMINERS:
        lines.append(f"- **{b['name']}** ({b['role']})  \n  {b['designation']}, {b['dept']}, {b['inst']}\n")
    lines.append("\n---\n\n")

    # Declaration
    lines.append("## DECLARATION\n\n")
    lines.append(front_matter.DECLARATION_TEXT + "\n\n")
    lines.append("Submitted by:\n")
    for s in front_matter.STUDENTS:
        lines.append(f"- {s['name']} (ID: {s['id']})\n")
    lines.append("\n---\n\n")

    # Acknowledgements
    lines.append("## ACKNOWLEDGEMENTS\n\n")
    for p in front_matter.ACKNOWLEDGEMENTS_TEXT:
        lines.append(p + "\n\n")
    lines.append("---\n\n")

    # Abstract
    lines.append("## ABSTRACT\n\n")
    lines.append(front_matter.ABSTRACT_TEXT + "\n\n")
    lines.append("**Keywords:** Group Recommender Systems, Social Choice Theory, Least-Misery Consensus, "
                 "Gini Inequality Metric, Travelling Salesperson Problem (TSP), 2-Opt Local Search Heuristic, "
                 "Explainable AI (XAI), Dynamic Weather Adaptation, Bangladesh Tourism, Progressive Web Application (PWA).\n\n---\n\n")

    # Table of Contents
    lines.append("## TABLE OF CONTENTS\n\n")
    for item, page in front_matter.TABLE_OF_CONTENTS:
        indent = "&nbsp;&nbsp;&nbsp;&nbsp;" if item.startswith("    ") else ("&nbsp;&nbsp;" if item.startswith("  ") else "")
        lines.append(f"{indent}**{item.strip()}** .................................................... {page}  \n")
    lines.append("\n---\n\n")

    # List of Figures
    lines.append("## LIST OF FIGURES\n\n")
    for fig_id, title, page in front_matter.LIST_OF_FIGURES:
        lines.append(f"- **{fig_id}**: {title} .................... *Page {page}*  \n")
    lines.append("\n---\n\n")

    # List of Tables
    lines.append("## LIST OF TABLES\n\n")
    for tbl_id, title, page in front_matter.LIST_OF_TABLES:
        lines.append(f"- **{tbl_id}**: {title} .................... *Page {page}*  \n")
    lines.append("\n---\n\n")

    # CHAPTER 1
    lines.append(f"# {chapter1.CHAPTER_1_TITLE}\n\n")
    for sec in [chapter1.SECTION_1_1, chapter1.SECTION_1_2, chapter1.SECTION_1_3, chapter1.SECTION_1_4, chapter1.SECTION_1_5, chapter1.SECTION_1_6, chapter1.SECTION_1_7]:
        lines.append(f"## {sec['title']}\n\n")
        for p in sec["paragraphs"]:
            lines.append(p + "\n\n")

    lines.append("\n---\n\n")

    # CHAPTER 2
    lines.append(f"# {chapter2.CHAPTER_2_TITLE}\n\n")
    for sec in [chapter2.SECTION_2_1, chapter2.SECTION_2_2]:
        lines.append(f"## {sec['title']}\n\n")
        for p in sec["paragraphs"]:
            lines.append(p + "\n\n")

    lines.append(f"### {chapter2.TABLE_2_1_DATA['caption']}\n\n")
    lines.append(format_table(chapter2.TABLE_2_1_DATA["headers"], chapter2.TABLE_2_1_DATA["rows"]) + "\n\n")

    lines.append(f"## {chapter2.SECTION_2_3['title']}\n\n")
    for p in chapter2.SECTION_2_3["paragraphs"]:
        lines.append(p + "\n\n")

    lines.append(f"## {chapter2.SECTION_2_4['title']}\n\n")
    for p in chapter2.SECTION_2_4["paragraphs"]:
        lines.append(p + "\n\n")

    lines.append(f"### {chapter2.TABLE_2_2_DATA['caption']}\n\n")
    lines.append(format_table(chapter2.TABLE_2_2_DATA["headers"], chapter2.TABLE_2_2_DATA["rows"]) + "\n\n")

    lines.append(f"### {chapter2.SECTION_2_4_OPEN_ISSUES['title']}\n\n")
    for p in chapter2.SECTION_2_4_OPEN_ISSUES["paragraphs"]:
        lines.append(p + "\n\n")

    lines.append(f"## {chapter2.SECTION_2_5['title']}\n\n")
    for p in chapter2.SECTION_2_5["paragraphs"]:
        lines.append(p + "\n\n")

    lines.append("\n---\n\n")

    # CHAPTER 3
    lines.append(f"# {chapter3.CHAPTER_3_TITLE}\n\n")
    lines.append("## 3.1 Requirements Analysis and Design Specification\n\n")
    for sec in [chapter3.SECTION_3_1_1, chapter3.SECTION_3_1_2]:
        lines.append(f"### {sec['title']}\n\n")
        for p in sec["paragraphs"]:
            lines.append(p + "\n\n")

    lines.append("### 3.1.3 Functional Requirements Specification\n\n")
    lines.append(f"#### {chapter3.TABLE_3_1_FR['caption']}\n\n")
    lines.append(format_table(chapter3.TABLE_3_1_FR["headers"], chapter3.TABLE_3_1_FR["rows"]) + "\n\n")

    lines.append("### 3.1.4 Non-Functional Requirements Specification\n\n")
    lines.append(f"#### {chapter3.TABLE_3_2_NFR['caption']}\n\n")
    lines.append(format_table(chapter3.TABLE_3_2_NFR["headers"], chapter3.TABLE_3_2_NFR["rows"]) + "\n\n")

    lines.append("### 3.1.5 Actors and Principal Use Cases\n\n")
    for uc in chapter3.USE_CASE_SPECS:
        lines.append(f"#### {uc['title']}\n\n")
        lines.append(format_table(uc["headers"], uc["rows"]) + "\n\n")

    lines.append("## 3.2 Detailed Design\n\n")
    lines.append(f"### {chapter3.SECTION_3_2_1['title']}\n\n")
    for p in chapter3.SECTION_3_2_1["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append("![Figure 3.1: TripSense Multi-Tier Decoupled System Architecture](figures/fig3_1_architecture.png)\n\n"
                 "*Figure 3.1: TripSense Multi-Tier Decoupled System Architecture*\n\n")

    lines.append(f"### {chapter3.SECTION_3_2_2['title']}\n\n")
    for p in chapter3.SECTION_3_2_2["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append("![Figure 3.5: Algorithmic Recommendation and 2-Opt TSP Scheduling Flowchart](figures/fig3_5_flowchart.png)\n\n"
                 "*Figure 3.5: Algorithmic Recommendation and 2-Opt TSP Scheduling Flowchart*\n\n")

    lines.append(f"### {chapter3.SECTION_3_2_3['title']}\n\n")
    for p in chapter3.SECTION_3_2_3["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append("![Figure 3.2: TripSense Relational and Document Entity-Relationship Diagram](figures/fig3_2_er_diagram.png)\n\n"
                 "*Figure 3.2: TripSense Relational and Document Entity-Relationship Diagram*\n\n")
    for tbl in [chapter3.TABLE_3_7_DATA, chapter3.TABLE_3_8_DATA, chapter3.TABLE_3_9_DATA]:
        lines.append(f"#### {tbl['caption']}\n\n")
        lines.append(format_table(tbl["headers"], tbl["rows"]) + "\n\n")

    lines.append(f"### {chapter3.SECTION_3_2_4['title']}\n\n")
    for p in chapter3.SECTION_3_2_4["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append("![Figure 3.3: UML Class Diagram: Domain Entities and Algorithmic Services](figures/fig3_3_class_diagram.png)\n\n"
                 "*Figure 3.3: UML Class Diagram: Domain Entities, Algorithmic Services, and Structural Relations*\n\n")
    lines.append("![Figure 3.4: UML Sequence Diagram: Group Plan Synthesis and Weather Adaptation](figures/fig3_4_sequence.png)\n\n"
                 "*Figure 3.4: UML Sequence Diagram: Group Plan Synthesis and Dynamic Weather Adaptation Workflow*\n\n")

    for sec in [chapter3.SECTION_3_2_5, chapter3.SECTION_3_2_6, chapter3.SECTION_3_3]:
        lines.append(f"### {sec['title']}\n\n")
        for p in sec["paragraphs"]:
            lines.append(p + "\n\n")

    lines.append(f"#### {chapter3.TABLE_3_10_DATA['caption']}\n\n")
    lines.append(format_table(chapter3.TABLE_3_10_DATA["headers"], chapter3.TABLE_3_10_DATA["rows"]) + "\n\n")

    lines.append(f"#### {chapter3.TABLE_3_11_DATA['caption']}\n\n")
    lines.append(format_table(chapter3.TABLE_3_11_DATA["headers"], chapter3.TABLE_3_11_DATA["rows"]) + "\n\n")

    lines.append(f"## {chapter3.SECTION_3_4['title']}\n\n")
    for p in chapter3.SECTION_3_4["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append(f"#### {chapter3.TABLE_3_12_DATA['caption']}\n\n")
    lines.append(format_table(chapter3.TABLE_3_12_DATA["headers"], chapter3.TABLE_3_12_DATA["rows"]) + "\n\n")

    lines.append(f"## {chapter3.SECTION_3_5['title']}\n\n")
    for p in chapter3.SECTION_3_5["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append(f"#### {chapter3.TABLE_3_13_DATA['caption']}\n\n")
    lines.append(format_table(chapter3.TABLE_3_13_DATA["headers"], chapter3.TABLE_3_13_DATA["rows"]) + "\n\n")

    lines.append(f"## {chapter3.SECTION_3_6['title']}\n\n")
    for p in chapter3.SECTION_3_6["paragraphs"]:
        lines.append(p + "\n\n")

    lines.append("\n---\n\n")

    # CHAPTER 4
    lines.append(f"# {chapter4.CHAPTER_4_TITLE}\n\n")
    lines.append(f"## {chapter4.SECTION_4_1['title']}\n\n")
    for p in chapter4.SECTION_4_1["paragraphs"]:
        lines.append(p + "\n\n")

    lines.append("## 4.2 Comprehensive Testing and Quality Assurance\n\n")
    
    # 4.2.1 Unit Tests
    lines.append(f"### {chapter4.SECTION_4_2_1['title']}\n\n")
    for p in chapter4.SECTION_4_2_1["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append(f"#### {chapter4.TABLE_4_1_UNIT_TESTS['caption']}\n\n")
    lines.append(format_table(chapter4.TABLE_4_1_UNIT_TESTS["headers"], chapter4.TABLE_4_1_UNIT_TESTS["rows"]) + "\n\n")

    # 4.2.2 Integration Tests
    lines.append(f"### {chapter4.SECTION_4_2_2['title']}\n\n")
    for p in chapter4.SECTION_4_2_2["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append(f"#### {chapter4.TABLE_4_2_INTEGRATION_TESTS['caption']}\n\n")
    lines.append(format_table(chapter4.TABLE_4_2_INTEGRATION_TESTS["headers"], chapter4.TABLE_4_2_INTEGRATION_TESTS["rows"]) + "\n\n")

    # 4.2.3 System Resilience Tests
    lines.append(f"### {chapter4.SECTION_4_2_3['title']}\n\n")
    for p in chapter4.SECTION_4_2_3["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append(f"#### {chapter4.TABLE_4_3_SYSTEM_TESTS['caption']}\n\n")
    lines.append(format_table(chapter4.TABLE_4_3_SYSTEM_TESTS["headers"], chapter4.TABLE_4_3_SYSTEM_TESTS["rows"]) + "\n\n")

    # 4.2.4 UI Black-Box Test Cases
    lines.append("### 4.2.4 User Interface Black-Box Test Cases\n\n")
    lines.append(f"#### {chapter4.TABLE_4_4_UI_TEST_CASES['caption']}\n\n")
    lines.append(format_table(chapter4.TABLE_4_4_UI_TEST_CASES["headers"], chapter4.TABLE_4_4_UI_TEST_CASES["rows"]) + "\n\n")

    # Results & Discussion
    lines.append("## 4.3 Algorithmic Performance Evaluation and Discussion\n\n")
    lines.append(f"### {chapter4.SECTION_4_3_1['title']}\n\n")
    for p in chapter4.SECTION_4_3_1["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append(f"#### {chapter4.TABLE_4_5_SOCIAL_CHOICE['caption']}\n\n")
    lines.append(format_table(chapter4.TABLE_4_5_SOCIAL_CHOICE["headers"], chapter4.TABLE_4_5_SOCIAL_CHOICE["rows"]) + "\n\n")
    lines.append("![Figure 4.2: Group Satisfaction Distribution and Fairness Metric Dashboard](figures/fig4_2_fairness.png)\n\n"
                 "*Figure 4.2: Group Satisfaction Distribution and Fairness Metric Dashboard*\n\n")

    lines.append(f"### {chapter4.SECTION_4_3_2['title']}\n\n")
    for p in chapter4.SECTION_4_3_2["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append(f"#### {chapter4.TABLE_4_6_TRANSIT_BENCHMARK['caption']}\n\n")
    lines.append(format_table(chapter4.TABLE_4_6_TRANSIT_BENCHMARK["headers"], chapter4.TABLE_4_6_TRANSIT_BENCHMARK["rows"]) + "\n\n")
    lines.append("![Figure 4.1: Empirical 2-Opt TSP Route Optimization Benchmark](figures/fig4_1_route_opt.png)\n\n"
                 "*Figure 4.1: Empirical 2-Opt TSP Route Optimization Benchmark (Chittagong Day Tour)*\n\n")

    lines.append(f"### {chapter4.SECTION_4_3_3['title']}\n\n")
    for p in chapter4.SECTION_4_3_3["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append("![Figure 4.3: Dynamic Context-Aware Weather Adaptation Decision Tree](figures/fig4_3_weather_tree.png)\n\n"
                 "*Figure 4.3: Dynamic Context-Aware Weather Adaptation Decision Tree*\n\n")

    lines.append(f"### {chapter4.SECTION_4_3_4['title']}\n\n")
    for p in chapter4.SECTION_4_3_4["paragraphs"]:
        lines.append(p + "\n\n")

    # 4.4 Final System Demonstration with UI Mockup Figures
    lines.append(f"## {chapter4.SECTION_4_4['title']}\n\n")
    for p in chapter4.SECTION_4_4["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append("![Figure 4.4: System Demonstration: Destination Selection and 60-Second Preference Onboarding Quiz](figures/fig4_4_demo_onboarding.png)\n\n"
                 "*Figure 4.4: System Demonstration: Destination Selection and 60-Second Preference Onboarding Quiz*\n\n")
    lines.append("![Figure 4.5: System Demonstration: Consensus Itinerary, Leaflet Map, and Explainability Modal](figures/fig4_5_demo_itinerary.png)\n\n"
                 "*Figure 4.5: System Demonstration: Consensus Itinerary, Leaflet Map, and Explainability Modal*\n\n")
    lines.append("![Figure 4.6: System Demonstration: Dynamic Monsoon Weather Alert and Peer Expense Splitter](figures/fig4_6_demo_weather_expense.png)\n\n"
                 "*Figure 4.6: System Demonstration: Dynamic Monsoon Weather Alert and Peer Expense Splitter*\n\n")

    lines.append(f"## {chapter4.SECTION_4_5['title']}\n\n")
    for p in chapter4.SECTION_4_5["paragraphs"]:
        lines.append(p + "\n\n")

    lines.append("\n---\n\n")

    # CHAPTER 5
    lines.append(f"# {chapter5.CHAPTER_5_TITLE}\n\n")
    lines.append("## 5.1 Compliance with Engineering Standards\n\n")
    for sec in [chapter5.SECTION_5_1_1, chapter5.SECTION_5_1_2, chapter5.SECTION_5_1_3]:
        lines.append(f"### {sec['title']}\n\n")
        for p in sec["paragraphs"]:
            lines.append(p + "\n\n")

    lines.append("## 5.2 Impact on Society, Environment, and Sustainability\n\n")
    for sec in [chapter5.SECTION_5_2_1, chapter5.SECTION_5_2_2, chapter5.SECTION_5_2_3, chapter5.SECTION_5_2_4]:
        lines.append(f"### {sec['title']}\n\n")
        for p in sec["paragraphs"]:
            lines.append(p + "\n\n")

    lines.append(f"## {chapter5.SECTION_5_3['title']}\n\n")
    for p in chapter5.SECTION_5_3["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append(f"#### {chapter5.TABLE_5_1_BUDGET['caption']}\n\n")
    lines.append(format_table(chapter5.TABLE_5_1_BUDGET["headers"], chapter5.TABLE_5_1_BUDGET["rows"]) + "\n\n")

    lines.append("## 5.4 Complex Engineering Problem (BAETE OBE Criteria)\n\n")
    lines.append(f"### {chapter5.SECTION_5_4_1['title']}\n\n")
    for p in chapter5.SECTION_5_4_1["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append(f"#### {chapter5.TABLE_5_2_EP['caption']}\n\n")
    lines.append(format_table(chapter5.TABLE_5_2_EP["headers"], chapter5.TABLE_5_2_EP["rows"]) + "\n\n")
    lines.append(f"#### {chapter5.TABLE_5_3_KP['caption']}\n\n")
    lines.append(format_table(chapter5.TABLE_5_3_KP["headers"], chapter5.TABLE_5_3_KP["rows"]) + "\n\n")

    lines.append(f"### {chapter5.SECTION_5_4_2['title']}\n\n")
    for p in chapter5.SECTION_5_4_2["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append(f"#### {chapter5.TABLE_5_4_EA['caption']}\n\n")
    lines.append(format_table(chapter5.TABLE_5_4_EA["headers"], chapter5.TABLE_5_4_EA["rows"]) + "\n\n")

    lines.append(f"## {chapter5.SECTION_5_5['title']}\n\n")
    for p in chapter5.SECTION_5_5["paragraphs"]:
        lines.append(p + "\n\n")
    lines.append(f"#### {chapter5.TABLE_5_5_PO['caption']}\n\n")
    lines.append(format_table(chapter5.TABLE_5_5_PO["headers"], chapter5.TABLE_5_5_PO["rows"]) + "\n\n")

    lines.append(f"## {chapter5.SECTION_5_6['title']}\n\n")
    for p in chapter5.SECTION_5_6["paragraphs"]:
        lines.append(p + "\n\n")

    lines.append("\n---\n\n")

    # CHAPTER 6
    lines.append(f"# {chapter6.CHAPTER_6_TITLE}\n\n")
    for sec in [chapter6.SECTION_6_1, chapter6.SECTION_6_2, chapter6.SECTION_6_3]:
        lines.append(f"## {sec['title']}\n\n")
        for p in sec["paragraphs"]:
            lines.append(p + "\n\n")

    lines.append("\n---\n\n")

    # REFERENCES
    lines.append("# REFERENCES\n\n")
    for ref in chapter6.REFERENCES_LIST:
        lines.append(f"{ref}\n\n")

    # Write out
    content = "".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Markdown report generated successfully at: {output_path} ({len(content)} characters, ~{len(content.split())} words)")
