"""
Docx Builder for TripSense DIU CSE FYDP Final Report
Outputs docs/TripSense_FYDP_Final_Report.docx
Strictly follows DIU CSE FYDP Report Guidelines v2.1 with Century typography,
professional tables, embedded high-resolution figures, multi-section pagination,
and full academic prose.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION_START
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

from . import front_matter
from . import chapter1
from . import chapter2
from . import chapter3
from . import chapter4
from . import chapter5
from . import chapter6

# Colors
COLOR_NAVY = RGBColor(30, 58, 138)       # #1E3A8A
COLOR_DARK = RGBColor(15, 23, 42)        # #0F172A
COLOR_SLATE = RGBColor(71, 85, 105)      # #475569
COLOR_BODY = RGBColor(30, 41, 59)        # #1E293B

HEX_NAVY = "1E3A8A"
HEX_ZEBRA = "F8FAFC"
HEX_BORDER = "CBD5E1"

def set_cell_background(cell, hex_color):
    """Sets background shading of a table cell."""
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    """Sets cell padding (in twips: 20 twips = 1 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(margin_name)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
    """Sets clean subtle borders on a table."""
    tblPr = table._tbl.tblPr
    borders_xml = f'''
    <w:tblBorders {nsdecls("w")}>
        <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
        <w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
        <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
        <w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
        <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
        <w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
    </w:tblBorders>
    '''
    tblPr.append(parse_xml(borders_xml))

def apply_section_margins(section):
    """Applies standard DIU CSE thesis margins."""
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.15)  # 1.15 in for left binding margin
    section.right_margin = Inches(1.0)
    section.header_distance = Inches(0.5)
    section.footer_distance = Inches(0.5)

def apply_default_typography(doc):
    """Configures default Century styles."""
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Century'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = COLOR_BODY
    style_normal.paragraph_format.line_spacing = 1.15
    style_normal.paragraph_format.space_after = Pt(6)
    style_normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

def add_paragraph(doc, text, bold_prefix=None, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6):
    """Adds a body paragraph with Century font."""
    p = doc.add_paragraph()
    p.paragraph_format.alignment = align
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(space_after)
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = 'Century'
        r_pre.font.size = Pt(11)
        r_pre.font.color.rgb = COLOR_DARK

    r = p.add_run(text)
    r.font.name = 'Century'
    r.font.size = Pt(11)
    r.font.color.rgb = COLOR_BODY
    return p

def add_section_heading(doc, text, level=2):
    """Adds a section heading with Century font and DIU styling."""
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    
    if level == 1:
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(10)
        r = p.add_run(text)
        r.font.name = 'Century'
        r.font.size = Pt(18)
        r.font.bold = True
        r.font.color.rgb = COLOR_NAVY
    elif level == 2:
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.font.name = 'Century'
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = COLOR_NAVY
    elif level == 3:
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.font.name = 'Century'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = COLOR_DARK
    else:
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(text)
        r.font.name = 'Century'
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = COLOR_SLATE
    return p

def add_table(doc, caption, headers, rows, col_widths=None):
    """Creates a professional styled table with navy headers, repeating headers, and no row split."""
    # Caption above table
    p_cap = doc.add_paragraph()
    p_cap.paragraph_format.space_before = Pt(12)
    p_cap.paragraph_format.space_after = Pt(4)
    p_cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_cap.paragraph_format.keep_with_next = True
    r_cap = p_cap.add_run(caption)
    r_cap.font.name = 'Century'
    r_cap.font.size = Pt(10)
    r_cap.font.bold = True
    r_cap.font.color.rgb = COLOR_NAVY

    # Add Table
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, color=HEX_BORDER, sz="4")

    # Repeat Header on Page Breaks (w:tblHeader)
    trPr_hdr = tbl.rows[0]._tr.get_or_add_trPr()
    trPr_hdr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

    # Format Header Row
    hdr_cells = tbl.rows[0].cells
    for i, h_text in enumerate(headers):
        hdr_cells[i].text = h_text
        set_cell_background(hdr_cells[i], HEX_NAVY)
        set_cell_margins(hdr_cells[i], top=130, bottom=130, left=140, right=140)
        hdr_cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        for p in hdr_cells[i].paragraphs:
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            for run in p.runs:
                run.font.name = 'Century'
                run.font.size = Pt(9.5)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

    # Format Data Rows
    for r_idx, row_data in enumerate(rows):
        row = tbl.rows[r_idx + 1]
        # Prevent row split across pages (w:cantSplit)
        trPr_row = row._tr.get_or_add_trPr()
        trPr_row.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

        row_cells = row.cells
        bg_color = HEX_ZEBRA if (r_idx % 2 == 1) else "FFFFFF"
        for c_idx, cell_value in enumerate(row_data):
            row_cells[c_idx].text = str(cell_value)
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=90, bottom=90, left=120, right=120)
            row_cells[c_idx].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for p in row_cells[c_idx].paragraphs:
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.05
                txt = cell_value.strip() if isinstance(cell_value, str) else str(cell_value)
                if len(txt) <= 8 or txt in ["PASS", "FAIL", "Option A", "Option B", "Yes", "No", "✓"]:
                    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for run in p.runs:
                    run.font.name = 'Century'
                    run.font.size = Pt(9)
                    if txt == "PASS":
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(22, 101, 52)
                    elif txt == "FAIL":
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(185, 28, 28)
                    else:
                        run.font.color.rgb = COLOR_BODY

    # Set explicit column widths if provided
    if col_widths:
        for row in tbl.rows:
            for idx, width in enumerate(col_widths):
                if idx < len(row.cells):
                    row.cells[idx].width = width

    # Add space after table
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(4)
    p_after.paragraph_format.space_after = Pt(8)

def add_figure(doc, image_path, caption, width_inches=5.8):
    """Embeds an image centered with a caption below."""
    if not os.path.exists(image_path):
        print(f"Warning: Figure image not found at {image_path}")
        return

    p_img = doc.add_paragraph()
    p_img.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(12)
    p_img.paragraph_format.space_after = Pt(4)
    p_img.paragraph_format.keep_with_next = True
    
    r_img = p_img.add_run()
    r_img.add_picture(image_path, width=Inches(width_inches))

    p_cap = doc.add_paragraph()
    p_cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(12)
    
    r_cap = p_cap.add_run(caption)
    r_cap.font.name = 'Century'
    r_cap.font.size = Pt(10)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_SLATE

def build_cover_page(doc, figures_dir):
    """Constructs the official DIU CSE FYDP Cover / Title Page with embedded DIU logo."""
    p_top = doc.add_paragraph()
    p_top.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_top.paragraph_format.space_before = Pt(16)
    p_top.paragraph_format.space_after = Pt(10)

    r_title = p_top.add_run(front_matter.PROJECT_TITLE)
    r_title.font.name = 'Century'
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_NAVY

    p_by = doc.add_paragraph()
    p_by.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_by.paragraph_format.space_after = Pt(6)
    r_by = p_by.add_run("By")
    r_by.font.name = 'Century'
    r_by.font.size = Pt(12)
    r_by.font.italic = True

    p_stud = doc.add_paragraph()
    p_stud.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_stud.paragraph_format.space_after = Pt(14)
    for s in front_matter.STUDENTS:
        r_name = p_stud.add_run(f"{s['name']}\nID: {s['id']}\n")
        r_name.font.name = 'Century'
        r_name.font.size = Pt(11.5)
        r_name.font.bold = True

    p_rep = doc.add_paragraph()
    p_rep.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rep.paragraph_format.space_after = Pt(4)
    r_rep = p_rep.add_run("FINAL YEAR DESIGN PROJECT REPORT")
    r_rep.font.name = 'Century'
    r_rep.font.size = Pt(13)
    r_rep.font.bold = True
    r_rep.font.color.rgb = COLOR_DARK

    p_fulfill = doc.add_paragraph()
    p_fulfill.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fulfill.paragraph_format.space_after = Pt(16)
    r_ful = p_fulfill.add_run("This Report Presented in Partial Fulfillment of the Requirements for the Degree of\nBachelor of Science in Computer Science and Engineering")
    r_ful.font.name = 'Century'
    r_ful.font.size = Pt(10.5)
    r_ful.font.italic = True

    # Supervisors Box
    p_sup = doc.add_paragraph()
    p_sup.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_sup.paragraph_format.space_after = Pt(2)
    r_sup_lbl = p_sup.add_run("Supervised by:\n")
    r_sup_lbl.font.name = 'Century'
    r_sup_lbl.font.size = Pt(10.5)
    r_sup_lbl.font.bold = True
    r_sup_lbl.font.color.rgb = COLOR_NAVY
    
    sup = front_matter.SUPERVISORS["supervisor"]
    r_sup = p_sup.add_run(f"{sup['name']}\n{sup['designation']}\n{sup['dept']}\n{sup['inst']}\n\n")
    r_sup.font.name = 'Century'
    r_sup.font.size = Pt(10.5)

    r_cosup_lbl = p_sup.add_run("Co-Supervised by:\n")
    r_cosup_lbl.font.name = 'Century'
    r_cosup_lbl.font.size = Pt(10.5)
    r_cosup_lbl.font.bold = True
    r_cosup_lbl.font.color.rgb = COLOR_NAVY

    cosup = front_matter.SUPERVISORS["co_supervisor"]
    r_cosup = p_sup.add_run(f"{cosup['name']}\n{cosup['designation']}\n{cosup['dept']}\n{cosup['inst']}\n")
    r_cosup.font.name = 'Century'
    r_cosup.font.size = Pt(10.5)

    # University Logo (Official DIU Logo)
    logo_path = os.path.join(figures_dir, "diu_logo.jpeg")
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(14)
        p_logo.paragraph_format.space_after = Pt(8)
        r_logo = p_logo.add_run()
        r_logo.add_picture(logo_path, width=Inches(1.2))

    # University Footer
    p_inst = doc.add_paragraph()
    p_inst.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(4)
    p_inst.paragraph_format.space_after = Pt(0)
    r_inst = p_inst.add_run(f"Department of Computer Science and Engineering\nDAFFODIL INTERNATIONAL UNIVERSITY\nDhaka, Bangladesh\n{front_matter.SUBMISSION_DATE}")
    r_inst.font.name = 'Century'
    r_inst.font.size = Pt(11.5)
    r_inst.font.bold = True
    r_inst.font.color.rgb = COLOR_NAVY

def build_approval_page(doc):
    """Constructs the official Board of Examiners Approval Page."""
    add_section_heading(doc, "APPROVAL", level=1)
    add_paragraph(doc, front_matter.APPROVAL_TEXT, space_after=18)

    add_section_heading(doc, "BOARD OF EXAMINERS", level=2)
    
    tbl = doc.add_table(rows=len(front_matter.BOARD_OF_EXAMINERS), cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, color="FFFFFF", sz="0") # invisible borders for signature layout

    for idx, b in enumerate(front_matter.BOARD_OF_EXAMINERS):
        c_left = tbl.cell(idx, 0)
        c_right = tbl.cell(idx, 1)
        c_left.width = Inches(4.3)
        c_right.width = Inches(1.9)
        
        p = c_left.paragraphs[0]
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.line_spacing = 1.15
        
        r1 = p.add_run(f"{b['name']}\n")
        r1.font.name = 'Century'
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        
        r2 = p.add_run(f"{b['designation']}, {b['dept']}\n{b['inst']}")
        r2.font.name = 'Century'
        r2.font.size = Pt(9.5)
        
        p_r = c_right.paragraphs[0]
        p_r.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_r.paragraph_format.space_after = Pt(12)
        r_role = p_r.add_run(f"{b['role']}\n\n___________________\nSignature")
        r_role.font.name = 'Century'
        r_role.font.size = Pt(9.5)
        r_role.font.bold = True
        r_role.font.color.rgb = COLOR_NAVY

    doc.add_page_break()

def build_declaration_page(doc):
    """Constructs the formal Declaration of Authorship Page."""
    add_section_heading(doc, "DECLARATION", level=1)
    add_paragraph(doc, front_matter.DECLARATION_TEXT, space_after=20)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run("Submitted by:\n")
    r_sub.font.name = 'Century'
    r_sub.font.size = Pt(11)
    r_sub.font.bold = True
    r_sub.font.color.rgb = COLOR_NAVY

    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, color="FFFFFF", sz="0")

    for idx, s in enumerate(front_matter.STUDENTS):
        cell = tbl.cell(0, idx)
        cell.width = Inches(3.1)
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(f"___________________________\nSignature\n\n{s['name']}\nStudent ID: {s['id']}\n{s['dept']}\n{s['inst']}")
        r.font.name = 'Century'
        r.font.size = Pt(10)

    doc.add_page_break()

def build_acknowledgements_page(doc):
    """Constructs Acknowledgements Page."""
    add_section_heading(doc, "ACKNOWLEDGEMENTS", level=1)
    for p_text in front_matter.ACKNOWLEDGEMENTS_TEXT:
        add_paragraph(doc, p_text, space_after=8)
    doc.add_page_break()

def build_abstract_page(doc):
    """Constructs Abstract Page."""
    add_section_heading(doc, "ABSTRACT", level=1)
    add_paragraph(doc, front_matter.ABSTRACT_TEXT, space_after=12)
    
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(12)
    p_kw.paragraph_format.space_after = Pt(12)
    r_lbl = p_kw.add_run("Keywords: ")
    r_lbl.font.name = 'Century'
    r_lbl.font.size = Pt(10.5)
    r_lbl.font.bold = True
    r_lbl.font.color.rgb = COLOR_NAVY
    
    r_vals = p_kw.add_run("Group Recommender Systems, Social Choice Theory, Least-Misery Consensus, "
                          "Gini Inequality Metric, Travelling Salesperson Problem (TSP), 2-Opt Local Search Heuristic, "
                          "Explainable AI (XAI), Dynamic Weather Adaptation, Bangladesh Tourism, Progressive Web Application (PWA).")
    r_vals.font.name = 'Century'
    r_vals.font.size = Pt(10.5)
    r_vals.font.italic = True
    
    doc.add_page_break()

def build_table_of_contents(doc):
    """Constructs Table of Contents outline."""
    add_section_heading(doc, "TABLE OF CONTENTS", level=1)
    
    tbl = doc.add_table(rows=len(front_matter.TABLE_OF_CONTENTS), cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, color="FFFFFF", sz="0")

    for idx, (title, page) in enumerate(front_matter.TABLE_OF_CONTENTS):
        c_title = tbl.cell(idx, 0)
        c_page = tbl.cell(idx, 1)
        c_title.width = Inches(5.4)
        c_page.width = Inches(0.8)
        
        p_t = c_title.paragraphs[0]
        p_t.paragraph_format.space_after = Pt(2)
        r_t = p_t.add_run(title)
        r_t.font.name = 'Century'
        r_t.font.size = Pt(10)
        if title.startswith("CHAPTER") or title in ["APPROVAL", "DECLARATION", "ACKNOWLEDGEMENTS", "ABSTRACT", "LIST OF FIGURES", "LIST OF TABLES", "REFERENCES"]:
            r_t.font.bold = True
            r_t.font.color.rgb = COLOR_NAVY
        else:
            r_t.font.color.rgb = COLOR_BODY

        p_p = c_page.paragraphs[0]
        p_p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_p.paragraph_format.space_after = Pt(2)
        r_p = p_p.add_run(str(page))
        r_p.font.name = 'Century'
        r_p.font.size = Pt(10)
        r_p.font.bold = title.startswith("CHAPTER")
        r_p.font.color.rgb = COLOR_SLATE

    doc.add_page_break()

def build_list_of_figures(doc):
    """Constructs List of Figures."""
    add_section_heading(doc, "LIST OF FIGURES", level=1)
    
    tbl = doc.add_table(rows=len(front_matter.LIST_OF_FIGURES), cols=3)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, color="FFFFFF", sz="0")

    for idx, (fig_no, fig_title, page) in enumerate(front_matter.LIST_OF_FIGURES):
        c_no = tbl.cell(idx, 0)
        c_title = tbl.cell(idx, 1)
        c_page = tbl.cell(idx, 2)
        c_no.width = Inches(1.1)
        c_title.width = Inches(4.3)
        c_page.width = Inches(0.8)
        
        p_no = c_no.paragraphs[0]
        p_no.paragraph_format.space_after = Pt(2)
        r_no = p_no.add_run(fig_no)
        r_no.font.name = 'Century'
        r_no.font.size = Pt(10)
        r_no.font.bold = True
        r_no.font.color.rgb = COLOR_NAVY

        p_t = c_title.paragraphs[0]
        p_t.paragraph_format.space_after = Pt(2)
        r_t = p_t.add_run(fig_title)
        r_t.font.name = 'Century'
        r_t.font.size = Pt(10)
        r_t.font.color.rgb = COLOR_BODY

        p_p = c_page.paragraphs[0]
        p_p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_p.paragraph_format.space_after = Pt(2)
        r_p = p_p.add_run(str(page))
        r_p.font.name = 'Century'
        r_p.font.size = Pt(10)
        r_p.font.color.rgb = COLOR_SLATE

    doc.add_page_break()

def build_list_of_tables(doc):
    """Constructs List of Tables."""
    add_section_heading(doc, "LIST OF TABLES", level=1)
    
    tbl = doc.add_table(rows=len(front_matter.LIST_OF_TABLES), cols=3)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, color="FFFFFF", sz="0")

    for idx, (tbl_no, tbl_title, page) in enumerate(front_matter.LIST_OF_TABLES):
        c_no = tbl.cell(idx, 0)
        c_title = tbl.cell(idx, 1)
        c_page = tbl.cell(idx, 2)
        c_no.width = Inches(1.1)
        c_title.width = Inches(4.3)
        c_page.width = Inches(0.8)
        
        p_no = c_no.paragraphs[0]
        p_no.paragraph_format.space_after = Pt(2)
        r_no = p_no.add_run(tbl_no)
        r_no.font.name = 'Century'
        r_no.font.size = Pt(10)
        r_no.font.bold = True
        r_no.font.color.rgb = COLOR_NAVY

        p_t = c_title.paragraphs[0]
        p_t.paragraph_format.space_after = Pt(2)
        r_t = p_t.add_run(tbl_title)
        r_t.font.name = 'Century'
        r_t.font.size = Pt(10)
        r_t.font.color.rgb = COLOR_BODY

        p_p = c_page.paragraphs[0]
        p_p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_p.paragraph_format.space_after = Pt(2)
        r_p = p_p.add_run(str(page))
        r_p.font.name = 'Century'
        r_p.font.size = Pt(10)
        r_p.font.color.rgb = COLOR_SLATE

def set_section_page_numbering(section, start=1, fmt="decimal"):
    """Sets or replaces the w:pgNumType element for a section."""
    sectPr = section._sectPr
    for node in sectPr.xpath('./w:pgNumType'):
        sectPr.remove(node)
    pgNumType = OxmlElement('w:pgNumType')
    pgNumType.set(qn('w:start'), str(start))
    pgNumType.set(qn('w:fmt'), fmt)
    sectPr.append(pgNumType)

def build_full_docx_report(output_path, figures_dir):
    """Orchestrates generation of the comprehensive DIU CSE FYDP Word Document with multi-section layout."""
    doc = docx.Document()
    apply_default_typography(doc)

    # -------------------------------------------------------------
    # SECTION 0: COVER PAGE (No headers/footers, DifferentFirstPage)
    # -------------------------------------------------------------
    sec_cover = doc.sections[0]
    apply_section_margins(sec_cover)
    sec_cover.different_first_page_header_footer = True
    print("Building Official Cover Page...")
    build_cover_page(doc, figures_dir)

    # -------------------------------------------------------------
    # SECTION 1: PRELIMINARY FRONT-MATTER (Roman numerals: ii, iii...)
    # -------------------------------------------------------------
    print("Building Preliminary Front-Matter Pages (Roman Numerals)...")
    sec_front = doc.add_section(WD_SECTION_START.NEW_PAGE)
    apply_section_margins(sec_front)
    sec_front.header.is_linked_to_previous = False
    sec_front.footer.is_linked_to_previous = False

    # Roman numeral page numbering starting at 2 (Cover is unnumbered page i)
    set_section_page_numbering(sec_front, start=2, fmt='lowerRoman')

    # Centered Roman numeral footer
    p_ff = sec_front.footer.paragraphs[0]
    p_ff.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ff = p_ff.add_run()
    r_ff.font.name = 'Century'
    r_ff.font.size = Pt(10)
    r_ff.font.color.rgb = COLOR_SLATE
    r_ff._r.append(parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>'))

    build_approval_page(doc)
    build_declaration_page(doc)
    build_acknowledgements_page(doc)
    build_abstract_page(doc)
    build_table_of_contents(doc)
    build_list_of_figures(doc)
    build_list_of_tables(doc)

    # -------------------------------------------------------------
    # SECTION 2: MAIN REPORT BODY (Arabic numerals: 1, 2, 3...)
    # -------------------------------------------------------------
    print("Building Main Report Body (Arabic Numerals)...")
    sec_body = doc.add_section(WD_SECTION_START.NEW_PAGE)
    apply_section_margins(sec_body)
    sec_body.header.is_linked_to_previous = False
    sec_body.footer.is_linked_to_previous = False

    # Decimal page numbering starting at 1
    set_section_page_numbering(sec_body, start=1, fmt='decimal')

    # Running header on body
    p_head = sec_body.header.paragraphs[0]
    p_head.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_head.paragraph_format.space_after = Pt(4)
    r_head = p_head.add_run("TripSense: Final Year Design Project Report | Daffodil International University")
    r_head.font.name = 'Century'
    r_head.font.size = Pt(8.5)
    r_head.font.color.rgb = COLOR_SLATE
    r_head.font.italic = True
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="4" w:space="2" w:color="{HEX_BORDER}"/></w:pBdr>')
    p_head._p.get_or_add_pPr().append(pBdr)

    # Running footer: "Page X of Y"
    p_fb = sec_body.footer.paragraphs[0]
    p_fb.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_fb = p_fb.add_run("Page ")
    r_fb.font.name = 'Century'
    r_fb.font.size = Pt(9.5)
    r_fb.font.color.rgb = COLOR_SLATE
    r_fb_p = p_fb.add_run()
    r_fb_p.font.name = 'Century'
    r_fb_p.font.size = Pt(9.5)
    r_fb_p.font.color.rgb = COLOR_SLATE
    r_fb_p._r.append(parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>'))
    r_fb_of = p_fb.add_run(" of ")
    r_fb_of.font.name = 'Century'
    r_fb_of.font.size = Pt(9.5)
    r_fb_of.font.color.rgb = COLOR_SLATE
    r_fb_np = p_fb.add_run()
    r_fb_np.font.name = 'Century'
    r_fb_np.font.size = Pt(9.5)
    r_fb_np.font.color.rgb = COLOR_SLATE
    r_fb_np._r.append(parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="NUMPAGES"/>'))

    # CHAPTER 1
    print("Building Chapter 1: Introduction...")
    add_section_heading(doc, chapter1.CHAPTER_1_TITLE, level=1)
    for sec in [chapter1.SECTION_1_1, chapter1.SECTION_1_2, chapter1.SECTION_1_3, chapter1.SECTION_1_4, chapter1.SECTION_1_5, chapter1.SECTION_1_6, chapter1.SECTION_1_7]:
        add_section_heading(doc, sec["title"], level=2)
        for p in sec["paragraphs"]:
            add_paragraph(doc, p)
    doc.add_page_break()

    # CHAPTER 2
    print("Building Chapter 2: Background and Literature Review...")
    add_section_heading(doc, chapter2.CHAPTER_2_TITLE, level=1)
    for sec in [chapter2.SECTION_2_1, chapter2.SECTION_2_2]:
        add_section_heading(doc, sec["title"], level=2)
        for p in sec["paragraphs"]:
            add_paragraph(doc, p)

    # Table 2.1 Literature Review
    add_table(doc, chapter2.TABLE_2_1_DATA["caption"], chapter2.TABLE_2_1_DATA["headers"], chapter2.TABLE_2_1_DATA["rows"])

    # Similar Apps
    add_section_heading(doc, chapter2.SECTION_2_3["title"], level=2)
    for p in chapter2.SECTION_2_3["paragraphs"]:
        add_paragraph(doc, p)

    # Gap Analysis
    add_section_heading(doc, chapter2.SECTION_2_4["title"], level=2)
    for p in chapter2.SECTION_2_4["paragraphs"]:
        add_paragraph(doc, p)

    # Table 2.2 Feature Comparison Matrix
    add_table(doc, chapter2.TABLE_2_2_DATA["caption"], chapter2.TABLE_2_2_DATA["headers"], chapter2.TABLE_2_2_DATA["rows"])

    add_section_heading(doc, chapter2.SECTION_2_4_OPEN_ISSUES["title"], level=3)
    for p in chapter2.SECTION_2_4_OPEN_ISSUES["paragraphs"]:
        add_paragraph(doc, p)

    add_section_heading(doc, chapter2.SECTION_2_5["title"], level=2)
    for p in chapter2.SECTION_2_5["paragraphs"]:
        add_paragraph(doc, p)
    doc.add_page_break()

    # CHAPTER 3
    print("Building Chapter 3: Design and Methodology...")
    add_section_heading(doc, chapter3.CHAPTER_3_TITLE, level=1)
    add_section_heading(doc, "3.1 Requirements Analysis and Design Specification", level=2)
    for sec in [chapter3.SECTION_3_1_1, chapter3.SECTION_3_1_2]:
        add_section_heading(doc, sec["title"], level=3)
        for p in sec["paragraphs"]:
            add_paragraph(doc, p)

    # Table 3.1 Functional Requirements
    add_section_heading(doc, "3.1.3 Functional Requirements Specification", level=3)
    add_table(doc, chapter3.TABLE_3_1_FR["caption"], chapter3.TABLE_3_1_FR["headers"], chapter3.TABLE_3_1_FR["rows"])

    # Table 3.2 Non-Functional Requirements
    add_section_heading(doc, "3.1.4 Non-Functional Requirements Specification", level=3)
    add_table(doc, chapter3.TABLE_3_2_NFR["caption"], chapter3.TABLE_3_2_NFR["headers"], chapter3.TABLE_3_2_NFR["rows"])

    # Use Case Specifications
    add_section_heading(doc, "3.1.5 Actors and Principal Use Cases", level=3)
    for uc in chapter3.USE_CASE_SPECS:
        add_table(doc, uc["title"], uc["headers"], uc["rows"], col_widths=[Inches(1.8), Inches(4.4)])

    # Detailed Design
    add_section_heading(doc, "3.2 Detailed Design", level=2)
    add_section_heading(doc, chapter3.SECTION_3_2_1["title"], level=3)
    for p in chapter3.SECTION_3_2_1["paragraphs"]:
        add_paragraph(doc, p)
    add_figure(doc, os.path.join(figures_dir, "fig3_1_architecture.png"), "Figure 3.1: TripSense Multi-Tier Decoupled System Architecture", width_inches=6.0)

    add_section_heading(doc, chapter3.SECTION_3_2_2["title"], level=3)
    for p in chapter3.SECTION_3_2_2["paragraphs"]:
        add_paragraph(doc, p)
    add_figure(doc, os.path.join(figures_dir, "fig3_5_flowchart.png"), "Figure 3.5: Algorithmic Recommendation and 2-Opt TSP Scheduling Flowchart", width_inches=5.8)

    add_section_heading(doc, chapter3.SECTION_3_2_3["title"], level=3)
    for p in chapter3.SECTION_3_2_3["paragraphs"]:
        add_paragraph(doc, p)
    add_figure(doc, os.path.join(figures_dir, "fig3_2_er_diagram.png"), "Figure 3.2: TripSense Relational and Document Entity-Relationship Diagram", width_inches=6.0)
    
    # Data Dictionaries
    for tbl in [chapter3.TABLE_3_7_DATA, chapter3.TABLE_3_8_DATA, chapter3.TABLE_3_9_DATA]:
        add_table(doc, tbl["caption"], tbl["headers"], tbl["rows"])

    # Section 3.2.4 with Class Diagram and Sequence Diagram
    add_section_heading(doc, chapter3.SECTION_3_2_4["title"], level=3)
    for p in chapter3.SECTION_3_2_4["paragraphs"]:
        add_paragraph(doc, p)
    add_figure(doc, os.path.join(figures_dir, "fig3_3_class_diagram.png"), "Figure 3.3: UML Class Diagram: Domain Entities, Algorithmic Services, and Structural Relations", width_inches=6.1)
    add_figure(doc, os.path.join(figures_dir, "fig3_4_sequence.png"), "Figure 3.4: UML Sequence Diagram: Group Plan Synthesis and Dynamic Weather Adaptation Workflow", width_inches=6.0)

    for sec in [chapter3.SECTION_3_2_5, chapter3.SECTION_3_2_6, chapter3.SECTION_3_3]:
        add_section_heading(doc, sec["title"], level=3 if not sec["title"].startswith("3.3") else 2)
        for p in sec["paragraphs"]:
            add_paragraph(doc, p)

    # Tables 3.10 and 3.11 (Timeline & Gantt)
    add_table(doc, chapter3.TABLE_3_10_DATA["caption"], chapter3.TABLE_3_10_DATA["headers"], chapter3.TABLE_3_10_DATA["rows"])
    add_table(doc, chapter3.TABLE_3_11_DATA["caption"], chapter3.TABLE_3_11_DATA["headers"], chapter3.TABLE_3_11_DATA["rows"])

    # Task Allocation
    add_section_heading(doc, chapter3.SECTION_3_4["title"], level=2)
    for p in chapter3.SECTION_3_4["paragraphs"]:
        add_paragraph(doc, p)
    add_table(doc, chapter3.TABLE_3_12_DATA["caption"], chapter3.TABLE_3_12_DATA["headers"], chapter3.TABLE_3_12_DATA["rows"])

    # Risk Mitigation
    add_section_heading(doc, chapter3.SECTION_3_5["title"], level=2)
    for p in chapter3.SECTION_3_5["paragraphs"]:
        add_paragraph(doc, p)
    add_table(doc, chapter3.TABLE_3_13_DATA["caption"], chapter3.TABLE_3_13_DATA["headers"], chapter3.TABLE_3_13_DATA["rows"])

    add_section_heading(doc, chapter3.SECTION_3_6["title"], level=2)
    for p in chapter3.SECTION_3_6["paragraphs"]:
        add_paragraph(doc, p)
    doc.add_page_break()

    # CHAPTER 4
    print("Building Chapter 4: Implementation and Results...")
    add_section_heading(doc, chapter4.CHAPTER_4_TITLE, level=1)
    add_section_heading(doc, chapter4.SECTION_4_1["title"], level=2)
    for p in chapter4.SECTION_4_1["paragraphs"]:
        add_paragraph(doc, p)

    add_section_heading(doc, "4.2 Comprehensive Testing and Quality Assurance", level=2)
    
    # 4.2.1 Unit Tests
    add_section_heading(doc, chapter4.SECTION_4_2_1["title"], level=3)
    for p in chapter4.SECTION_4_2_1["paragraphs"]:
        add_paragraph(doc, p)
    add_table(doc, chapter4.TABLE_4_1_UNIT_TESTS["caption"], chapter4.TABLE_4_1_UNIT_TESTS["headers"], chapter4.TABLE_4_1_UNIT_TESTS["rows"])

    # 4.2.2 Integration Tests
    add_section_heading(doc, chapter4.SECTION_4_2_2["title"], level=3)
    for p in chapter4.SECTION_4_2_2["paragraphs"]:
        add_paragraph(doc, p)
    add_table(doc, chapter4.TABLE_4_2_INTEGRATION_TESTS["caption"], chapter4.TABLE_4_2_INTEGRATION_TESTS["headers"], chapter4.TABLE_4_2_INTEGRATION_TESTS["rows"])

    # 4.2.3 System Resilience Tests
    add_section_heading(doc, chapter4.SECTION_4_2_3["title"], level=3)
    for p in chapter4.SECTION_4_2_3["paragraphs"]:
        add_paragraph(doc, p)
    add_table(doc, chapter4.TABLE_4_3_SYSTEM_TESTS["caption"], chapter4.TABLE_4_3_SYSTEM_TESTS["headers"], chapter4.TABLE_4_3_SYSTEM_TESTS["rows"])

    # 4.2.4 UI Black-Box Test Cases
    add_section_heading(doc, "4.2.4 User Interface Black-Box Test Cases", level=3)
    add_table(doc, chapter4.TABLE_4_4_UI_TEST_CASES["caption"], chapter4.TABLE_4_4_UI_TEST_CASES["headers"], chapter4.TABLE_4_4_UI_TEST_CASES["rows"])

    # Results & Discussion
    add_section_heading(doc, "4.3 Algorithmic Performance Evaluation and Discussion", level=2)
    add_section_heading(doc, chapter4.SECTION_4_3_1["title"], level=3)
    for p in chapter4.SECTION_4_3_1["paragraphs"]:
        add_paragraph(doc, p)
    add_table(doc, chapter4.TABLE_4_5_SOCIAL_CHOICE["caption"], chapter4.TABLE_4_5_SOCIAL_CHOICE["headers"], chapter4.TABLE_4_5_SOCIAL_CHOICE["rows"])
    add_figure(doc, os.path.join(figures_dir, "fig4_2_fairness.png"), "Figure 4.2: Group Satisfaction Distribution and Fairness Metric Dashboard", width_inches=5.8)

    add_section_heading(doc, chapter4.SECTION_4_3_2["title"], level=3)
    for p in chapter4.SECTION_4_3_2["paragraphs"]:
        add_paragraph(doc, p)
    add_table(doc, chapter4.TABLE_4_6_TRANSIT_BENCHMARK["caption"], chapter4.TABLE_4_6_TRANSIT_BENCHMARK["headers"], chapter4.TABLE_4_6_TRANSIT_BENCHMARK["rows"])
    add_figure(doc, os.path.join(figures_dir, "fig4_1_route_opt.png"), "Figure 4.1: Empirical 2-Opt TSP Route Optimization Benchmark (Chittagong Day Tour)", width_inches=5.8)

    add_section_heading(doc, chapter4.SECTION_4_3_3["title"], level=3)
    for p in chapter4.SECTION_4_3_3["paragraphs"]:
        add_paragraph(doc, p)
    add_figure(doc, os.path.join(figures_dir, "fig4_3_weather_tree.png"), "Figure 4.3: Dynamic Context-Aware Weather Adaptation Decision Tree", width_inches=5.8)

    add_section_heading(doc, chapter4.SECTION_4_3_4["title"], level=3)
    for p in chapter4.SECTION_4_3_4["paragraphs"]:
        add_paragraph(doc, p)

    # 4.4 Final System Demonstration with UI Mockup Figures
    add_section_heading(doc, chapter4.SECTION_4_4["title"], level=2)
    for p in chapter4.SECTION_4_4["paragraphs"]:
        add_paragraph(doc, p)
    add_figure(doc, os.path.join(figures_dir, "fig4_4_demo_onboarding.png"), "Figure 4.4: System Demonstration: Destination Selection and 60-Second Preference Onboarding Quiz", width_inches=6.0)
    add_figure(doc, os.path.join(figures_dir, "fig4_5_demo_itinerary.png"), "Figure 4.5: System Demonstration: Consensus Itinerary, Leaflet Map, and Explainability Modal", width_inches=6.0)
    add_figure(doc, os.path.join(figures_dir, "fig4_6_demo_weather_expense.png"), "Figure 4.6: System Demonstration: Dynamic Monsoon Weather Alert and Peer Expense Splitter", width_inches=6.0)

    add_section_heading(doc, chapter4.SECTION_4_5["title"], level=2)
    for p in chapter4.SECTION_4_5["paragraphs"]:
        add_paragraph(doc, p)
    doc.add_page_break()

    # CHAPTER 5
    print("Building Chapter 5: Engineering Standards and Design Challenges...")
    add_section_heading(doc, chapter5.CHAPTER_5_TITLE, level=1)
    add_section_heading(doc, "5.1 Compliance with Engineering Standards", level=2)
    for sec in [chapter5.SECTION_5_1_1, chapter5.SECTION_5_1_2, chapter5.SECTION_5_1_3]:
        add_section_heading(doc, sec["title"], level=3)
        for p in sec["paragraphs"]:
            add_paragraph(doc, p)

    add_section_heading(doc, "5.2 Impact on Society, Environment, and Sustainability", level=2)
    for sec in [chapter5.SECTION_5_2_1, chapter5.SECTION_5_2_2, chapter5.SECTION_5_2_3, chapter5.SECTION_5_2_4]:
        add_section_heading(doc, sec["title"], level=3)
        for p in sec["paragraphs"]:
            add_paragraph(doc, p)

    add_section_heading(doc, chapter5.SECTION_5_3["title"], level=2)
    for p in chapter5.SECTION_5_3["paragraphs"]:
        add_paragraph(doc, p)
    add_table(doc, chapter5.TABLE_5_1_BUDGET["caption"], chapter5.TABLE_5_1_BUDGET["headers"], chapter5.TABLE_5_1_BUDGET["rows"])

    add_section_heading(doc, "5.4 Complex Engineering Problem (BAETE OBE Criteria)", level=2)
    add_section_heading(doc, chapter5.SECTION_5_4_1["title"], level=3)
    for p in chapter5.SECTION_5_4_1["paragraphs"]:
        add_paragraph(doc, p)
    add_table(doc, chapter5.TABLE_5_2_EP["caption"], chapter5.TABLE_5_2_EP["headers"], chapter5.TABLE_5_2_EP["rows"])
    add_table(doc, chapter5.TABLE_5_3_KP["caption"], chapter5.TABLE_5_3_KP["headers"], chapter5.TABLE_5_3_KP["rows"])

    add_section_heading(doc, chapter5.SECTION_5_4_2["title"], level=3)
    for p in chapter5.SECTION_5_4_2["paragraphs"]:
        add_paragraph(doc, p)
    add_table(doc, chapter5.TABLE_5_4_EA["caption"], chapter5.TABLE_5_4_EA["headers"], chapter5.TABLE_5_4_EA["rows"])

    add_section_heading(doc, chapter5.SECTION_5_5["title"], level=2)
    for p in chapter5.SECTION_5_5["paragraphs"]:
        add_paragraph(doc, p)
    add_table(doc, chapter5.TABLE_5_5_PO["caption"], chapter5.TABLE_5_5_PO["headers"], chapter5.TABLE_5_5_PO["rows"])

    add_section_heading(doc, chapter5.SECTION_5_6["title"], level=2)
    for p in chapter5.SECTION_5_6["paragraphs"]:
        add_paragraph(doc, p)
    doc.add_page_break()

    # CHAPTER 6
    print("Building Chapter 6: Conclusion...")
    add_section_heading(doc, chapter6.CHAPTER_6_TITLE, level=1)
    for sec in [chapter6.SECTION_6_1, chapter6.SECTION_6_2, chapter6.SECTION_6_3]:
        add_section_heading(doc, sec["title"], level=2)
        for p in sec["paragraphs"]:
            add_paragraph(doc, p)
    doc.add_page_break()

    # REFERENCES
    print("Building References...")
    add_section_heading(doc, "REFERENCES", level=1)
    for ref_str in chapter6.REFERENCES_LIST:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.first_line_indent = Inches(-0.4)
        p_ref.paragraph_format.space_after = Pt(6)
        p_ref.paragraph_format.line_spacing = 1.15
        r = p_ref.add_run(ref_str)
        r.font.name = 'Century'
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_BODY

    # Save Document
    doc.save(output_path)
    print(f"Word document saved successfully at: {output_path} (Size: {os.path.getsize(output_path)} bytes)")
