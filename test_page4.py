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

def set_cell_margins(cell, top=15, bottom=15, left=25, right=25):
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
r = p.add_run("8. Diagramme de Gantt Prévisionnel (Calendrier sur 20 Jours Ouvrés)")
r.font.name = "Arial"
r.font.size = Pt(10)
r.font.bold = True
r.font.color.rgb = RGBColor(27, 54, 93)

p2 = doc.add_paragraph()
p2.paragraph_format.space_before = Pt(0)
p2.paragraph_format.space_after = Pt(3)
p2.paragraph_format.line_spacing = 1.0
r2 = p2.add_run("Le diagramme de Gantt convertit l'ordonnancement PERT en un calendrier opérationnel. Les barres foncées indiquent les tâches critiques.")
r2.font.name = "Arial"
r2.font.size = Pt(8)

p_img = doc.add_paragraph()
p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_img.paragraph_format.space_before = Pt(0)
p_img.paragraph_format.space_after = Pt(3)
run_img = p_img.add_run()
run_img.add_picture('/home/anes/Documents/VisionX/gantt_chart_visionx.png', width=Inches(6.8), height=Inches(2.1))

# Table
tbl = doc.add_table(rows=15, cols=5)
tbl.autofit = False
date_widths = [Inches(0.45), Inches(2.7), Inches(1.15), Inches(1.15), Inches(1.72)]
headers = ["ID", "Activité", "Début au plus tôt", "Fin au plus tôt", "Responsables mobilisés"]

for c_idx, h in enumerate(headers):
    c = tbl.cell(0, c_idx)
    c.width = date_widths[c_idx]
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=20, bottom=20, left=20, right=20)
    p = c.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2, 3] else WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(6.8)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

date_data = [
    ("A", "Cadrage & validation des contrats", "J1 (08h00)", "J1 (17h00)", "M. Anes Bouharizi"),
    ("B", "Spécifications fonctionnelles & techniques", "J2 (08h00)", "J3 (17h00)", "M. Anes, S. Iyed, Z. Akram"),
    ("C", "Conception de l'architecture logicielle", "J4 (08h00)", "J5 (17h00)", "M. Anes, S. Iyed"),
    ("D", "Modélisation de la base de données", "J4 (08h00)", "J5 (17h00)", "F. Baha"),
    ("E", "Développement du socle FastAPI", "J6 (08h00)", "J8 (17h00)", "S. Iyed"),
    ("I", "Micro-moteur email Jinja2 / SMTP", "J6 (08h00)", "J7 (17h00)", "B. Anis, B. Adem"),
    ("F", "Isolation multi-tenant & persistance", "J9 (08h00)", "J10 (17h00)", "F. Baha, B. Adem"),
    ("M", "Packaging Docker & configuration", "J9 (08h00)", "J9 (17h00)", "B. Adem"),
    ("G", "Gestion prospects & Lead Scoring", "J11 (08h00)", "J12 (17h00)", "B. Anis, F. Baha"),
    ("H", "Réception & traitement des commandes", "J11 (08h00)", "J12 (17h00)", "Z. Akram, S. Iyed"),
    ("J", "Automatisations & campagnes marketing", "J13 (08h00)", "J14 (17h00)", "B. Anis"),
    ("K", "Intégration & échanges avec le noyau", "J13 (08h00)", "J15 (17h00)", "S. Iyed, Z. Akram"),
    ("L", "Tests de conformité, intégration & sécurité", "J16 (08h00)", "J18 (17h00)", "Toute l'équipe VisionX"),
    ("N", "Documentation finale & préparation démo", "J19 (08h00)", "J20 (17h00)", "M. Anes, toute l'équipe")
]

for r_idx, (d_id, d_nom, d_deb, d_fin, d_resp) in enumerate(date_data, start=1):
    bg_col = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
    for c_idx, val in enumerate([d_id, d_nom, d_deb, d_fin, d_resp]):
        c = tbl.cell(r_idx, c_idx)
        c.width = date_widths[c_idx]
        set_cell_background(c, bg_col)
        set_cell_margins(c, top=15, bottom=15, left=20, right=20)
        p = c.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2, 3] else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(6.5)
        if c_idx == 0:
            r.font.bold = True
        r.font.color.rgb = RGBColor(30, 41, 59)

p_liss = doc.add_paragraph()
p_liss.paragraph_format.space_before = Pt(2)
p_liss.paragraph_format.space_after = Pt(0)
p_liss.paragraph_format.line_spacing = 1.05
r_l = p_liss.add_run(
    "Stratégie de lissage : Parallélisation systématique (D//C, I//E, G//H). Équilibrage optimal de la charge sans heures supplémentaires."
)
r_l.font.name = "Arial"
r_l.font.size = Pt(7.2)
r_l.font.bold = True
r_l.font.color.rgb = RGBColor(27, 54, 93)

doc.save("/home/anes/Documents/VisionX/test_page4.docx")
