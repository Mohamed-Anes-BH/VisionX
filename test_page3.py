import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

doc = Document()
s = doc.sections[0]
s.top_margin = Inches(0.4)
s.bottom_margin = Inches(0.4)
s.left_margin = Inches(0.55)
s.right_margin = Inches(0.55)
s.page_width = Inches(8.27)
s.page_height = Inches(11.69)

def set_cell_margins(cell, top=20, bottom=20, left=30, right=30):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

# Heading
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(2)
r = p.add_run("6. Réseau PERT & Analyse Mathématique de l'Ordonnancement")
r.font.name = "Arial"
r.font.size = Pt(10)
r.font.bold = True
r.font.color.rgb = RGBColor(27, 54, 93)

p2 = doc.add_paragraph()
p2.paragraph_format.space_before = Pt(0)
p2.paragraph_format.space_after = Pt(3)
p2.paragraph_format.line_spacing = 1.0
r2 = p2.add_run("Le graphe PERT ci-dessous modélise le réseau de dépendances du projet VisionX. Il met en évidence la durée minimale théorique (20 jours ouvrés).")
r2.font.name = "Arial"
r2.font.size = Pt(8)

p_img = doc.add_paragraph()
p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_img.paragraph_format.space_before = Pt(0)
p_img.paragraph_format.space_after = Pt(3)
run_img = p_img.add_run()
run_img.add_picture('/home/anes/Documents/VisionX/pert_network_visionx.png', width=Inches(6.8), height=Inches(1.95))

# Table
tbl = doc.add_table(rows=15, cols=9)
tbl.autofit = False
pert_widths = [Inches(0.4), Inches(0.45), Inches(0.8), Inches(0.65), Inches(0.65), Inches(0.65), Inches(0.65), Inches(1.3), Inches(1.4)]
headers = ["ID", "Dur.", "Pred.", "DTO", "FTO", "DTA", "FTA", "Marges (MT / ML)", "Statut"]

for c_idx, h in enumerate(headers):
    c = tbl.cell(0, c_idx)
    c.width = pert_widths[c_idx]
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=20, bottom=20, left=20, right=20)
    p = c.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(6.8)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

pert_calc_data = [
    ("A", "1 j", "—", "J1", "J1", "J1", "J1", "MT = 0 | ML = 0", "CRITIQUE"),
    ("B", "2 j", "A", "J2", "J3", "J2", "J3", "MT = 0 | ML = 0", "CRITIQUE"),
    ("C", "2 j", "B", "J4", "J5", "J4", "J5", "MT = 0 | ML = 0", "CRITIQUE"),
    ("D", "2 j", "B", "J4", "J5", "J7", "J8", "MT = 3 | ML = 3", "Flottante"),
    ("E", "3 j", "C", "J6", "J8", "J6", "J8", "MT = 0 | ML = 0", "CRITIQUE"),
    ("F", "2 j", "D, E", "J9", "J10", "J9", "J10", "MT = 0 | ML = 0", "CRITIQUE"),
    ("G", "2 j", "F", "J11", "J12", "J11", "J12", "MT = 0 | ML = 0", "CRITIQUE"),
    ("H", "2 j", "F", "J11", "J12", "J11", "J12", "MT = 0 | ML = 0", "CRITIQUE"),
    ("I", "2 j", "C", "J6", "J7", "J11", "J12", "MT = 5 | ML = 5", "Flottante"),
    ("J", "2 j", "G, H, I", "J13", "J14", "J14", "J15", "MT = 1 | ML = 1", "Flottante"),
    ("K", "3 j", "G, H", "J13", "J15", "J13", "J15", "MT = 0 | ML = 0", "CRITIQUE"),
    ("M", "1 j", "E", "J9", "J9", "J15", "J15", "MT = 6 | ML = 6", "Flottante"),
    ("L", "3 j", "J, K, M", "J16", "J18", "J16", "J18", "MT = 0 | ML = 0", "CRITIQUE"),
    ("N", "2 j", "L", "J19", "J20", "J19", "J20", "MT = 0 | ML = 0", "CRITIQUE")
]

for r_idx, row in enumerate(pert_calc_data, start=1):
    is_crit = (row[8] == "CRITIQUE")
    bg_col = "FEF2F2" if is_crit else ("F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
    for c_idx, val in enumerate(row):
        c = tbl.cell(r_idx, c_idx)
        c.width = pert_widths[c_idx]
        set_cell_background(c, bg_col)
        set_cell_margins(c, top=15, bottom=15, left=20, right=20)
        p = c.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(6.5)
        if is_crit:
            r.font.bold = True
            r.font.color.rgb = RGBColor(180, 20, 20) if c_idx == 8 else RGBColor(30, 41, 59)

p_cp = doc.add_paragraph()
p_cp.paragraph_format.space_before = Pt(2)
p_cp.paragraph_format.space_after = Pt(0)
p_cp.paragraph_format.line_spacing = 1.05
r_cp = p_cp.add_run(
    "Chemins Critiques (MT=0) : A→B→C→E→F→G→K→L→N (20j) et A→B→C→E→F→H→K→L→N (20j). Tout retard sur ces 8 activités reporte l'échéance finale."
)
r_cp.font.name = "Arial"
r_cp.font.size = Pt(7.2)
r_cp.font.bold = True
r_cp.font.color.rgb = RGBColor(180, 20, 20)

doc.save("/home/anes/Documents/VisionX/test_page3.docx")
