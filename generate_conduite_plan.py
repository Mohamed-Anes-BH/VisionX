import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=60, bottom=60, left=90, right=90):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(margin_name)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_borders(cell, top="CBD5E1", bottom="CBD5E1", left="CBD5E1", right="CBD5E1"):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
    for b_name, b_val in borders.items():
        if b_val:
            node = OxmlElement(f'w:{b_name}')
            node.set(qn('w:val'), 'single')
            node.set(qn('w:sz'), '4')
            node.set(qn('w:space'), '0')
            node.set(qn('w:color'), b_val)
            tcBorders.append(node)
        else:
            node = OxmlElement(f'w:{b_name}')
            node.set(qn('w:val'), 'none')
            tcBorders.append(node)
    tcPr.append(tcBorders)

doc = Document()

# Page Margins & Setup
for s in doc.sections:
    s.top_margin = Inches(0.55)
    s.bottom_margin = Inches(0.55)
    s.left_margin = Inches(0.65)
    s.right_margin = Inches(0.65)
    s.page_width = Inches(8.27)  # A4
    s.page_height = Inches(11.69)
    footer = s.footer
    f_p = footer.paragraphs[0]
    f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    f_run = f_p.add_run("ESTIN 2026–2027 | Conduite de Projet | Livrable 3 : Planification — Équipe VisionX")
    f_run.font.name = "Arial"
    f_run.font.size = Pt(8)
    f_run.font.color.rgb = RGBColor(128, 128, 128)

NAVY = RGBColor(27, 54, 93)       # #1B365D (Bleu institutionnel ESTIN)
STEEL = RGBColor(41, 128, 185)    # #2980B9
CHARCOAL = RGBColor(45, 55, 72)   # #2D3748
MUTED = RGBColor(100, 116, 139)   # #64748B
CRITICAL_RED = RGBColor(185, 28, 28)

def add_heading(text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.bold = True
    if level == 1:
        r.font.size = Pt(11)
        r.font.color.rgb = NAVY
    else:
        r.font.size = Pt(9.5)
        r.font.color.rgb = STEEL

def add_body(text, before=0, after=3, indent=0.0):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.left_indent = Inches(indent)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(8.5)
    r.font.color.rgb = CHARCOAL
    return p

# ==============================================================================
# PAGE 1 : PAGE DE GARDE & CADRAGE OFFICIEL DU PROJET
# ==============================================================================
p_rep = doc.add_paragraph()
p_rep.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_rep.paragraph_format.space_before = Pt(0)
p_rep.paragraph_format.space_after = Pt(1)
r_rep = p_rep.add_run("الجمهوريــــــــة الجزائريــــــة الديمقراطيـــــة الشعبيـــــة\nRÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE")
r_rep.font.name = "Arial"
r_rep.font.size = Pt(8)
r_rep.font.bold = True
r_rep.font.color.rgb = MUTED

p_min = doc.add_paragraph()
p_min.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_min.paragraph_format.space_before = Pt(0)
p_min.paragraph_format.space_after = Pt(2)
r_min = p_min.add_run("MINISTÈRE DE L'ENSEIGNEMENT SUPÉRIEUR ET DE LA RECHERCHE SCIENTIFIQUE\nÉCOLE SUPÉRIEURE EN SCIENCES ET TECHNOLOGIES DE L'INFORMATIQUE ET DU NUMÉRIQUE (ESTIN)")
r_min.font.name = "Arial"
r_min.font.size = Pt(8)
r_min.font.bold = True
r_min.font.color.rgb = NAVY

# Title Banner Table
tbl_tit = doc.add_table(rows=1, cols=1)
tbl_tit.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_tit.autofit = False
c_tit = tbl_tit.cell(0, 0)
c_tit.width = Inches(6.97)
set_cell_background(c_tit, "1B365D")
set_cell_margins(c_tit, top=120, bottom=120, left=150, right=150)
p_t = c_tit.paragraphs[0]
p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_t1 = p_t.add_run("MINI-PROJET « CONDUITE DE PROJET » — 2ÈME ANNÉE CS (2026–2027)\n")
r_t1.font.name = "Arial"
r_t1.font.size = Pt(9.5)
r_t1.font.bold = True
r_t1.font.color.rgb = RGBColor(245, 180, 50)

r_t2 = p_t.add_run("LIVRABLE 3 : PLANIFICATION OPÉRATIONNELLE DU PROJET D'ÉQUIPE\n")
r_t2.font.name = "Arial"
r_t2.font.size = Pt(13)
r_t2.font.bold = True
r_t2.font.color.rgb = RGBColor(255, 255, 255)

r_t3 = p_t.add_run("Conception et développement d'un agent logiciel de Marketing Automation\nFilière Automatisation Métier · Date limite : 14 Novembre 2026")
r_t3.font.name = "Arial"
r_t3.font.size = Pt(9)
r_t3.font.color.rgb = RGBColor(220, 235, 252)

doc.add_paragraph().paragraph_format.space_after = Pt(2)

# Team Cartouche Table (Style identifié dans l'exemple de l'étudiant)
tbl_team = doc.add_table(rows=5, cols=2)
tbl_team.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_team.autofit = False
team_widths = [Inches(3.48), Inches(3.49)]
team_info = [
    ("Équipe de réalisation : VisionX", "Chef d'équipe : Bouharizi Mohamed Anes"),
    ("Membres du projet (6 étudiants) :\n1. Bouharizi Mohamed Anes (Chef d'équipe & Lead Tech)\n2. Sebti Iyed (Développeur API & Intégration)\n3. Zouane Akram (Développeur Cœur Métier)",
     "4. Fellah Baha (Développeur Emailing & Campagnes)\n5. Bertil Anis (Responsable Données & Sécurité)\n6. Bahi Adem (Qualité, Recette & Packaging Docker)"),
    ("Filière d'application : Automatisation Métier\nAgent : Marketing Automation (slug: agent-marketing-automation-visionx)",
     "Module : Conduite de Projet — 2ème Année CS\nÉtablissement : ESTIN (Amizour – Béjaïa)"),
    ("Objets du Bus Central d'Échange :\n• Consomme : Commande (endpoint /exchange/notify)\n• Produit : Prospect qualifié (seuil score >= 70)",
     "Calendrier prévisionnel de réalisation :\n• Durée calendaire du projet : 20 jours ouvrés\n• Charge globale d'effort : 36 Jours-Hommes (288 h)"),
    ("Nomenclature officielle du fichier de soumission :\nConduite_PLAN_VisionX.docx (alias Conduite_PLAN_equipe.doc)",
     "Date officielle de remise : Samedi 14 Novembre 2026\nStatut du document : Validé pour exécution")
]

for r_idx, (col1, col2) in enumerate(team_info):
    for c_idx, text in enumerate([col1, col2]):
        c = tbl_team.cell(r_idx, c_idx)
        c.width = team_widths[c_idx]
        set_cell_background(c, "F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
        set_cell_borders(c, top="CBD5E1", bottom="CBD5E1", left="CBD5E1", right="CBD5E1")
        set_cell_margins(c, top=40, bottom=40, left=70, right=70)
        p = c.paragraphs[0]
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(7.8)
        r.font.color.rgb = CHARCOAL
        if ":" in text.split("\n")[0]:
            # make titles slightly bold
            pass

add_heading("1. Synthèse Exécutive et Cadrage du Livrable 3", 1)
add_body(
    "Le présent livrable formalise la planification opérationnelle et détaillée du mini-projet « Conduite de projet » pour l'équipe VisionX. "
    "Faisant suite à la validation de la Charte de Projet (L2), ce document structure l'exécution technique de l'Agent Marketing Automation "
    "en articulant la décomposition hiérarchique des travaux (WBS), l'organisation de l'équipe (OBS) et sa matrice RACI, l'échéancier global "
    "et jalonné, le calcul rigoureux du chemin critique via le réseau PERT, l'ordonnancement temporel par le diagramme de Gantt sur 20 jours ouvrés, "
    "et l'évaluation chiffrée des charges (36 Jours-Hommes) et des coûts (158 400 DA valorisés pour 0 DA déboursé grâce aux logiciels open source)."
)

# ==============================================================================
# PAGE 2 : WBS & DICTIONNAIRE DÉTAILLÉ DES TÂCHES
# ==============================================================================
doc.add_page_break()

add_heading("2. Décomposition des Livrables (WBS) & Dictionnaire Détaillé des Tâches", 1)
add_body(
    "La Work Breakdown Structure (WBS) découpe le projet en 6 lots de travail majeurs (WP1 à WP6), déclinés en 14 activités opérationnelles (A à N). "
    "Chaque tâche possède un responsable clairement identifié, une durée calendaire estimée (en jours), une charge d'effort (en JH), des antécédents "
    "immédiats et un livrable technique auditable."
)

tbl_wbs = doc.add_table(rows=15, cols=7)
tbl_wbs.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_wbs.autofit = False
wbs_widths = [Inches(0.4), Inches(2.2), Inches(1.15), Inches(0.45), Inches(0.45), Inches(0.55), Inches(1.77)]
wbs_headers = ["ID", "Intitulé de l'activité", "Responsable(s)", "Dur.", "Chg.", "Préd.", "Livrable technique vérifiable"]

for c_idx, h in enumerate(wbs_headers):
    c = tbl_wbs.cell(0, c_idx)
    c.width = wbs_widths[c_idx]
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=40, bottom=40, left=30, right=30)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 3, 4, 5] else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(7.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

tasks_wbs_data = [
    ("A", "Cadrage & contrats officiels", "M. Anes", "1 j", "1 JH", "—", "Documents L1 et L2 validés"),
    ("B", "Spécifications fonctionnelles & tech.", "Anes, Iyed, Akram", "2 j", "3 JH", "A", "Dossier de spécifications & Pydantic"),
    ("C", "Conception de l'architecture backend", "Anes, Iyed", "2 j", "2 JH", "B", "Schémas modulaires & routes FastAPI"),
    ("D", "Modélisation de la base de données", "Baha, Anis", "2 j", "2 JH", "B", "Schéma relationnel & DDL SQLite/PG"),
    ("E", "Développement du socle FastAPI", "Iyed", "3 j", "3 JH", "C", "5 endpoints obligatoires & enveloppe"),
    ("F", "Isolation multi-tenant & persistance", "Baha, Adem", "2 j", "3 JH", "D, E", "Middleware tenant & script de purge"),
    ("G", "Gestion prospects & Lead Scoring", "Anis, Baha", "2 j", "3 JH", "F", "Module scoring borné (seuil >= 70)"),
    ("H", "Réception & traitement commandes", "Akram, Iyed", "2 j", "2 JH", "F", "Route /exchange/notify (commandes)"),
    ("I", "Moteur email Jinja2/SMTP modulaire", "Anis, Adem", "2 j", "2 JH", "C", "Templates HTML/texte & service SMTP"),
    ("J", "Automatisations & campagnes marketing", "Anis", "2 j", "2 JH", "G, H, I", "Workflows onboarding & win-back"),
    ("K", "Intégration complète avec le noyau", "Iyed, Akram", "3 j", "3 JH", "G, H", "Publication bus prospect & handshake"),
    ("M", "Conteneurisation Docker autonome", "Adem", "1 j", "1 JH", "E", "Dockerfile fonctionnel (< 100 Mo)"),
    ("L", "Tests fonctionnels, intégration & sécu", "Toute l'équipe", "3 j", "6 JH", "J, K, M", "Suite 15 tests automatisés à 100%"),
    ("N", "Documentation & préparation démo", "Anes, toute équipe", "2 j", "3 JH", "L", "README d'exploitation & support L8")
]

for r_idx, row in enumerate(tasks_wbs_data, start=1):
    bg_col = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
    for c_idx, val in enumerate(row):
        c = tbl_wbs.cell(r_idx, c_idx)
        c.width = wbs_widths[c_idx]
        set_cell_background(c, bg_col)
        set_cell_borders(c, top="E2E8F0", bottom="E2E8F0")
        set_cell_margins(c, top=25, bottom=25, left=30, right=30)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 3, 4, 5] else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(7.2)
        if c_idx == 0:
            r.font.bold = True
            r.font.color.rgb = NAVY
        else:
            r.font.color.rgb = CHARCOAL

add_heading("2.1. Analyse des Dépendances Fonctionnelles Inter-Agents (Filière Métier)", 2)
add_body(
    "Conformément au sujet officiel, l'agent Marketing Automation collabore avec la plateforme par couplage asynchrone sur le bus central :\n"
    "▪ Flux Sortant (Production de 'prospect') : Dès que le score comportemental d'un prospect atteint ou dépasse le seuil (score >= 70), "
    "l'activité G déclenche la publication vers le bus central via POST {NOYAU_URL}/exchange/agent/prospect. L'Agent Commercial consomme ce flux. "
    "Si l'Agent Commercial est indisponible, le noyau conserve l'événement sans bloquer notre agent.\n"
    "▪ Flux Entrant (Consommation de 'commande') : L'activité H écoute les notifications POST /exchange/notify transmises par le noyau "
    "lorsque l'Agent Facturation/Vente valide une commande ('confirmee' ou 'annulee'). VisionX déclenche immédiatement la campagne réactive J.\n"
    "▪ Indépendance Garantie : Grâce au simulateur autonome d'échanges (simulateur_marche_marketing.py), VisionX a validé l'intégralité de sa "
    "logique d'échange en local, garantissant une autonomie totale vis-à-vis des retards éventuels des autres équipes (Règle 4 de cloisonnement)."
)

# ==============================================================================
# PAGE 3 : OBS & MATRICE RACI CONSOLIDÉE
# ==============================================================================
doc.add_page_break()

add_heading("3. Organisation de l'Équipe (OBS) & Matrice RACI Consolidée", 1)
add_body(
    "L'Organizational Breakdown Structure (OBS) formalise la spécialisation des 6 membres de l'équipe VisionX. La matrice RACI garantit une "
    "gouvernance claire où chaque lot possède un responsable unique (Accountable) et des réalisateurs qualifiés (Responsible)."
)

tbl_obs = doc.add_table(rows=7, cols=4)
tbl_obs.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_obs.autofit = False
obs_widths = [Inches(1.8), Inches(1.8), Inches(2.2), Inches(1.17)]
obs_headers = ["Membre de l'équipe", "Rôle principal (OBS)", "Responsabilités directes & Lots", "Disponibilité"]

for c_idx, h in enumerate(obs_headers):
    c = tbl_obs.cell(0, c_idx)
    c.width = obs_widths[c_idx]
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=40, bottom=40, left=40, right=40)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 3 else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(7.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

obs_data = [
    ("Bouharizi Mohamed Anes", "Chef d'équipe & Lead Tech", "Pilotage global, cadrage A, architecture C, doc N, jalons", "6 JH (48 h)"),
    ("Sebti Iyed", "Développeur API & Intégration", "Socle FastAPI E, conformité 5 routes, intégration noyau K", "7 JH (56 h)"),
    ("Zouane Akram", "Développeur Cœur Métier", "Spécifications B, traitement commandes H, règles métier", "5 JH (40 h)"),
    ("Fellah Baha", "Développeur Emailing & Campagnes", "Modélisation base D, moteur Jinja2/SMTP I, campagnes J", "6 JH (48 h)"),
    ("Bertil Anis", "Responsable Données & Sécurité", "Multi-tenant F, purge atomique, lead scoring G", "6 JH (48 h)"),
    ("Bahi Adem", "Responsable Qualité & Packaging", "Packaging Docker M, banc de 15 tests pytest L, recette", "6 JH (48 h)")
]

for r_idx, row in enumerate(obs_data, start=1):
    bg_col = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
    for c_idx, val in enumerate(row):
        c = tbl_obs.cell(r_idx, c_idx)
        c.width = obs_widths[c_idx]
        set_cell_background(c, bg_col)
        set_cell_borders(c, top="E2E8F0", bottom="E2E8F0")
        set_cell_margins(c, top=25, bottom=25, left=40, right=40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 3 else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(7.2)
        if c_idx == 0:
            r.font.bold = True
        r.font.color.rgb = CHARCOAL

add_heading("3.1. Matrice RACI Consolidée du Projet", 2)

tbl_raci = doc.add_table(rows=7, cols=7)
tbl_raci.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_raci.autofit = False
raci_widths = [Inches(2.17), Inches(0.8), Inches(0.8), Inches(0.8), Inches(0.8), Inches(0.8), Inches(0.8)]
raci_headers = ["Lot de travail (WBS)", "M. Anes", "S. Iyed", "Z. Akram", "F. Baha", "B. Anis", "B. Adem"]

for c_idx, h in enumerate(raci_headers):
    c = tbl_raci.cell(0, c_idx)
    c.width = raci_widths[c_idx]
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=40, bottom=40, left=40, right=40)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(7.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

raci_data = [
    ("WP1 : Cadrage & Spécifications (A, B)", "A / R", "R", "R", "C", "C", "I"),
    ("WP2 : Socle Backend & Persistance (C, D, E, F)", "C", "A / R", "I", "R", "R", "R"),
    ("WP3 : Moteur Métier & Scoring (G, H)", "I", "C", "R", "C", "A / R", "I"),
    ("WP4 : Emailing & Campagnes (I, J)", "I", "R", "A / R", "R", "R", "C"),
    ("WP5 : Intégration Noyau & Bus (K)", "C", "A / R", "R", "I", "C", "I"),
    ("WP6 : Assurance Qualité & Packaging (M, L, N)", "A", "C", "I", "I", "C", "A / R")
]

for r_idx, row in enumerate(raci_data, start=1):
    bg_col = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
    for c_idx, val in enumerate(row):
        c = tbl_raci.cell(r_idx, c_idx)
        c.width = raci_widths[c_idx]
        set_cell_background(c, bg_col)
        set_cell_borders(c, top="E2E8F0", bottom="E2E8F0")
        set_cell_margins(c, top=25, bottom=25, left=40, right=40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(7.5)
        if "A" in val:
            r.font.bold = True
            r.font.color.rgb = NAVY
        else:
            r.font.color.rgb = CHARCOAL

add_heading("3.2. Modalités de Coordination et Règles d'Équipe", 2)
add_body(
    "▪ Réunions hebdomadaires obligatoires (tenues chaque mardi avec rédaction et archivage du PV de réunion formel).\n"
    "▪ Gestion de configuration et revues de code systématiques (pull requests sur le dépôt GitHub privé avec validation par 2 relecteurs).\n"
    "▪ Règle absolue de non-régression : chaque commit doit passer à 100 % les 15 tests automatisés de conformité avant fusion."
)

# ==============================================================================
# PAGE 4 : RÉSEAU PERT & CHEMIN CRITIQUE
# ==============================================================================
doc.add_page_break()

add_heading("4. Réseau PERT & Calcul Analytique du Chemin Critique", 1)
add_body(
    "Le réseau PERT (Program Evaluation and Review Technique) modélise l'ordonnancement mathématique des 14 activités du projet. "
    "Il permet de déterminer les dates de début et fin au plus tôt (Early Start/Finish), au plus tard (Late Start/Finish), ainsi que les "
    "marges totales (MT) et libres (ML), identifiant avec certitude les tâches critiques dont tout retard impacterait la livraison finale."
)

tbl_pert = doc.add_table(rows=15, cols=9)
tbl_pert.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_pert.autofit = False
p_widths = [Inches(0.4), Inches(1.8), Inches(0.45), Inches(0.45), Inches(0.45), Inches(0.45), Inches(0.45), Inches(0.55), Inches(1.77)]
p_headers = ["ID", "Activité", "Dur.", "ES", "EF", "LS", "LF", "Marge T.", "Statut & Criticité"]

for c_idx, h in enumerate(p_headers):
    c = tbl_pert.cell(0, c_idx)
    c.width = p_widths[c_idx]
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=40, bottom=40, left=30, right=30)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2, 3, 4, 5, 6, 7] else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(7.2)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

pert_data = [
    ("A", "Cadrage & contrats", "1 j", "0", "1", "0", "1", "0 j", "CRITIQUE (Chemin principal)"),
    ("B", "Spécifications fonctionnelles", "2 j", "1", "3", "1", "3", "0 j", "CRITIQUE (Chemin principal)"),
    ("C", "Conception architecture", "2 j", "3", "5", "3", "5", "0 j", "CRITIQUE (Chemin principal)"),
    ("D", "Modélisation base de données", "2 j", "3", "5", "6", "8", "3 j", "Non critique (Marge libre = 3 j)"),
    ("E", "Socle FastAPI", "3 j", "5", "8", "5", "8", "0 j", "CRITIQUE (Chemin principal)"),
    ("F", "Multi-tenant & persistance", "2 j", "8", "10", "8", "10", "0 j", "CRITIQUE (Chemin principal)"),
    ("G", "Prospects & Lead Scoring", "2 j", "10", "12", "10", "12", "0 j", "CRITIQUE (Branche jumelle 1)"),
    ("H", "Traitement des commandes", "2 j", "10", "12", "10", "12", "0 j", "CRITIQUE (Branche jumelle 2)"),
    ("I", "Moteur email Jinja2/SMTP", "2 j", "5", "7", "11", "13", "6 j", "Non critique (Marge libre = 5 j)"),
    ("J", "Campagnes marketing", "2 j", "12", "14", "13", "15", "1 j", "Non critique (Marge libre = 1 j)"),
    ("K", "Intégration noyau & bus", "3 j", "12", "15", "12", "15", "0 j", "CRITIQUE (Convergence bus)"),
    ("M", "Conteneurisation Docker", "1 j", "8", "9", "14", "15", "6 j", "Non critique (Marge libre = 6 j)"),
    ("L", "Tests fonctionnels & sécurité", "3 j", "15", "18", "15", "18", "0 j", "CRITIQUE (Recette globale)"),
    ("N", "Documentation & démo", "2 j", "18", "20", "18", "20", "0 j", "CRITIQUE (Clôture projet)")
]

for r_idx, row in enumerate(pert_data, start=1):
    is_crit = "CRITIQUE" in row[8]
    bg_col = "FEF2F2" if is_crit else ("F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
    for c_idx, val in enumerate(row):
        c = tbl_pert.cell(r_idx, c_idx)
        c.width = p_widths[c_idx]
        set_cell_background(c, bg_col)
        set_cell_borders(c, top="E2E8F0", bottom="E2E8F0")
        set_cell_margins(c, top=25, bottom=25, left=30, right=30)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2, 3, 4, 5, 6, 7] else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(7.2)
        if is_crit:
            r.font.bold = True
            r.font.color.rgb = CRITICAL_RED if c_idx in [0, 7, 8] else CHARCOAL
        else:
            r.font.color.rgb = CHARCOAL

add_heading("4.1. Analyse Approfondie du Chemin Critique", 2)
add_body(
    "▪ Équation des Chemins Critiques : Deux branches jumelles critiques déterminent la durée minimale du projet (20 jours ouvrés) :\n"
    "    Chemin 1 : A (1j) → B (2j) → C (2j) → E (3j) → F (2j) → G (2j) → K (3j) → L (3j) → N (2j) = 20 jours ouvrés.\n"
    "    Chemin 2 : A (1j) → B (2j) → C (2j) → E (3j) → F (2j) → H (2j) → K (3j) → L (3j) → N (2j) = 20 jours ouvrés.\n"
    "▪ Conséquence Managériale : Toute journée de retard sur l'une de ces 10 tâches décale directement la date de livraison finale (T6/T8).\n"
    "▪ Marges de Manœuvre : Tâche D (+3j de marge), Tâche I (+6j), Tâche M (+6j), Tâche J (+1j). Ces marges permettent d'absorber des aléas."
)

# ==============================================================================
# PAGE 5 : ÉCHÉANCIER GLOBAL & DIAGRAMME DE GANTT
# ==============================================================================
doc.add_page_break()

add_heading("5. Échéancier Global (Jalons) & Diagramme de Gantt Détaillé (J1 à J20)", 1)
add_body(
    "Le diagramme de Gantt ci-dessous traduit le réseau PERT en un calendrier opérationnel sur 20 jours ouvrés. "
    "Il illustre la synchronisation des tâches parallèles et les points d'étape formels (jalons de validation J1 à J6)."
)

tbl_gantt = doc.add_table(rows=15, cols=22)
tbl_gantt.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_gantt.autofit = False

g_widths = [Inches(1.5), Inches(0.8)] + [Inches(0.233)] * 20
g_headers = ["Activité", "Pilote"] + [f"J{i}" for i in range(1, 21)]

for c_idx, h in enumerate(g_headers):
    c = tbl_gantt.cell(0, c_idx)
    c.width = g_widths[c_idx]
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=30, bottom=30, left=10, right=10)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx >= 1 else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(6.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

gantt_schedule = [
    ("A : Cadrage contrats", "Anes", 1, 1, True),
    ("B : Spécifications", "Anes", 2, 3, True),
    ("C : Architecture", "Iyed", 4, 5, True),
    ("D : Modèle BDD", "Baha", 4, 5, False),
    ("E : Socle FastAPI", "Iyed", 6, 8, True),
    ("I : Email SMTP", "Anis", 6, 7, False),
    ("F : Multi-tenant", "Baha", 9, 10, True),
    ("M : Dockerisation", "Adem", 9, 9, False),
    ("G : Prospects & Score", "Anis", 11, 12, True),
    ("H : Commandes", "Akram", 11, 12, True),
    ("J : Campagnes", "Anis", 13, 14, False),
    ("K : Intégration noyau", "Iyed", 13, 15, True),
    ("L : Tests & Recette", "Adem", 16, 18, True),
    ("N : Doc & Démo", "Anes", 19, 20, True),
]

for r_idx, (t_name, t_lead, start_d, end_d, is_crit) in enumerate(gantt_schedule, start=1):
    c_name = tbl_gantt.cell(r_idx, 0)
    c_name.width = g_widths[0]
    set_cell_background(c_name, "F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
    set_cell_margins(c_name, top=20, bottom=20, left=30, right=30)
    p = c_name.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(t_name)
    r.font.name = "Arial"
    r.font.size = Pt(6.8)
    r.font.bold = is_crit
    r.font.color.rgb = CRITICAL_RED if is_crit else CHARCOAL

    c_lead = tbl_gantt.cell(r_idx, 1)
    c_lead.width = g_widths[1]
    set_cell_background(c_lead, "F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
    set_cell_margins(c_lead, top=20, bottom=20, left=10, right=10)
    p2 = c_lead.paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_before = Pt(1)
    p2.paragraph_format.space_after = Pt(1)
    r2 = p2.add_run(t_lead)
    r2.font.name = "Arial"
    r2.font.size = Pt(6.8)
    r2.font.color.rgb = MUTED

    for day in range(1, 21):
        cell_d = tbl_gantt.cell(r_idx, day + 1)
        cell_d.width = g_widths[day + 1]
        set_cell_margins(cell_d, top=15, bottom=15, left=5, right=5)
        p_d = cell_d.paragraphs[0]
        p_d.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_d.paragraph_format.space_before = Pt(1)
        p_d.paragraph_format.space_after = Pt(1)
        
        if start_d <= day <= end_d:
            bar_color = "DC2626" if is_crit else "2563EB"
            set_cell_background(cell_d, bar_color)
            r_bar = p_d.add_run("■")
            r_bar.font.name = "Arial"
            r_bar.font.size = Pt(6)
            r_bar.font.color.rgb = RGBColor(255, 255, 255)
        else:
            bg_empty = "F1F5F9" if day in [5, 10, 15, 20] else ("FFFFFF" if r_idx % 2 == 0 else "F8FAFC")
            set_cell_background(cell_d, bg_empty)
            set_cell_borders(cell_d, top="E2E8F0", bottom="E2E8F0")

add_body(
    "Légende : [■ Rouge] = Tâches sur le Chemin Critique (marge nulle). [■ Bleu] = Tâches parallèles non critiques.\n"
    "Jalons : J1 (Fin J5 : Conception) · J2 (Fin J10 : Socle API) · J3 (Fin J14 : Moteur Métier) · J4 (Fin J15 : Intégration Noyau) · J5 (Fin J18 : Recette) · J6 (Fin J20 : Clôture).",
    before=4, after=4
)

add_heading("5.1. Matrice des Jalons de Contrôle Officiels", 2)
tbl_jalons = doc.add_table(rows=7, cols=5)
tbl_jalons.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_jalons.autofit = False
jal_widths = [Inches(0.6), Inches(1.8), Inches(0.8), Inches(1.97), Inches(1.8)]
jal_headers = ["Jalon", "Intitulé du Jalon", "Échéance", "Critère de validation opérationnel", "Livrable formel"]

for c_idx, h in enumerate(jal_headers):
    c = tbl_jalons.cell(0, c_idx)
    c.width = jal_widths[c_idx]
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=40, bottom=40, left=40, right=40)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2] else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(7.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

jalons_data = [
    ("J1", "Conception & Architecture", "Fin J5", "Validation schémas DDL et signature des endpoints", "Livrable L2 (Charte)"),
    ("J2", "Socle API & Multi-tenant", "Fin J10", "5 routes obligatoires opérationnelles + purge vérifiée", "Socle testé en local"),
    ("J3", "Moteur Métier & Campagnes", "Fin J14", "Scoring prospect >= 70 actif + traitement commandes", "Modules G, H, J prêts"),
    ("J4", "Intégration Noyau & Bus", "Fin J15", "Publication/réception fluides via /exchange/...", "Livrable L3 (PV Lancement)"),
    ("J5", "Recette Qualité & Conformité", "Fin J18", "15/15 tests automatisés validés à 100 %, 0 faille", "Livrable L4 (Planning)"),
    ("J6", "Déploiement & Soutenance", "Fin J20", "Image Docker livrée sur GitHub privé, démo prête", "Livrables L5 à L8")
]

for r_idx, (j_id, j_nom, j_ech, j_crit, j_liv) in enumerate(jalons_data, start=1):
    bg_col = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
    for c_idx, val in enumerate([j_id, j_nom, j_ech, j_crit, j_liv]):
        c = tbl_jalons.cell(r_idx, c_idx)
        c.width = jal_widths[c_idx]
        set_cell_background(c, bg_col)
        set_cell_borders(c, top="CBD5E1", bottom="CBD5E1")
        set_cell_margins(c, top=25, bottom=25, left=40, right=40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2] else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(7.2)
        if c_idx == 0:
            r.font.bold = True
            r.font.color.rgb = NAVY
        else:
            r.font.color.rgb = CHARCOAL

# ==============================================================================
# PAGE 6 : ESTIMATION DES COÛTS ET DES EFFORTS
# ==============================================================================
doc.add_page_break()

add_heading("6. Estimation Globale et Détaillée des Coûts et des Efforts", 1)
add_body(
    "L'évaluation distingue rigoureusement la durée calendaire du projet (20 jours ouvrés) de la charge totale de travail humain requise "
    "(36 Jours-Hommes, soit 288 heures réparties sur les 6 élèves-ingénieurs). Cette estimation reflète l'effort cumulé de conception, "
    "développement, tests et rédaction des livrables."
)

tbl_chg = doc.add_table(rows=8, cols=5)
tbl_chg.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_chg.autofit = False
chg_widths = [Inches(1.8), Inches(2.0), Inches(0.9), Inches(1.0), Inches(1.27)]
chg_headers = ["Membre de l'équipe", "Domaines d'intervention principaux", "Charge (JH)", "Charge (h)", "Part d'effort"]

for c_idx, h in enumerate(chg_headers):
    c = tbl_chg.cell(0, c_idx)
    c.width = chg_widths[c_idx]
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=40, bottom=40, left=30, right=30)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx >= 2 else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(7.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

chg_data = [
    ("Mohamed Anes Bouharizi", "Coordination, cadrage A, specs B, architecture C, doc N", "6 JH", "48 h", "16.7 %"),
    ("Sebti Iyed", "Specs B, backend FastAPI E, intégration noyau K", "7 JH", "56 h", "19.4 %"),
    ("Zouane Akram", "Specs B, traitement commandes H, intégration noyau K", "5 JH", "40 h", "13.9 %"),
    ("Fellah Baha", "Modélisation base D, isolation multi-tenant F, tests L", "6 JH", "48 h", "16.7 %"),
    ("Bertil Anis", "Lead scoring G, moteur emailing I, campagnes marketing J", "6 JH", "48 h", "16.7 %"),
    ("Bahi Adem", "Multi-tenant F, conteneurisation Docker M, banc de tests L", "6 JH", "48 h", "16.7 %"),
    ("TOTAL CONSOLIDÉ", "Ensemble des 14 activités du projet VisionX", "36 JH", "288 h", "100.0 %")
]

for r_idx, (m_nom, m_dom, m_chg, m_h, m_pct) in enumerate(chg_data, start=1):
    is_tot = (r_idx == 7)
    bg_col = "1B365D" if is_tot else ("F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
    for c_idx, val in enumerate([m_nom, m_dom, m_chg, m_h, m_pct]):
        c = tbl_chg.cell(r_idx, c_idx)
        c.width = chg_widths[c_idx]
        set_cell_background(c, bg_col)
        set_cell_borders(c, top="CBD5E1", bottom="CBD5E1")
        set_cell_margins(c, top=25, bottom=25, left=30, right=30)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx >= 2 else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(7.5)
        if is_tot:
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
        else:
            r.font.bold = (c_idx == 0)
            r.font.color.rgb = CHARCOAL

add_heading("6.1. Budget Prévisionnel et Analyse Financière du Projet", 2)
add_body(
    "Le modèle économique retenu s'appuie exclusivement sur des outils et frameworks Open Source / FOSS libres de droits. "
    "Le débours réel en trésorerie pour l'ESTIN et pour l'équipe est de **0 DA**, tout en intégrant une valorisation académique théorique "
    "de la main-d'œuvre qualifiée fournie par les élèves-ingénieurs :"
)

tbl_bud = doc.add_table(rows=6, cols=4)
tbl_bud.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_bud.autofit = False
bud_widths = [Inches(1.8), Inches(2.6), Inches(1.3), Inches(1.27)]
bud_headers = ["Catégorie de coût", "Description des ressources mobilisées", "Base de valorisation", "Montant valorisé"]

for c_idx, h in enumerate(bud_headers):
    c = tbl_bud.cell(0, c_idx)
    c.width = bud_widths[c_idx]
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=40, bottom=40, left=40, right=40)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx >= 2 else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(7.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

bud_data = [
    ("Logiciels & Frameworks", "Python 3.10+, FastAPI, SQLite/PG, Jinja2, MailHog, Git", "Licences MIT / BSD / FOSS", "0 DA (Débours réel 0)"),
    ("Infrastructure & Serveurs", "Docker Engine, environnements locaux étudiants, git privé", "Postes de travail & ESTIN", "0 DA (Débours réel 0)"),
    ("Main-d'œuvre intellectuelle", "Prestation d'ingénierie des 6 étudiants VisionX (36 JH)", "36 JH × 4 000 DA/JH", "144 000 DA (Valorisé)"),
    ("Réserve pour imprévus (10%)", "Marge de sécurité technique & recette (+10 %)", "10 % du coût main-d'œuvre", "14 400 DA (Réserve)"),
    ("COÛT TOTAL DU PROJET", "Budget complet valorisé (Débours effectif décaissé = 0 DA)", "Formule standard L3/L4", "158 400 DA (Valorisé)")
]

for r_idx, (b_cat, b_desc, b_base, b_mnt) in enumerate(bud_data, start=1):
    is_tot = (r_idx == 5)
    bg_col = "1B365D" if is_tot else ("F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
    for c_idx, val in enumerate([b_cat, b_desc, b_base, b_mnt]):
        c = tbl_bud.cell(r_idx, c_idx)
        c.width = bud_widths[c_idx]
        set_cell_background(c, bg_col)
        set_cell_borders(c, top="CBD5E1", bottom="CBD5E1")
        set_cell_margins(c, top=25, bottom=25, left=40, right=40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx >= 2 else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(7.5)
        if is_tot:
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
        else:
            r.font.bold = (c_idx == 0)
            r.font.color.rgb = CHARCOAL

# ==============================================================================
# PAGE 7 : GESTION DES RISQUES & PILOTAGE PAR LES KPIS
# ==============================================================================
doc.add_page_break()

add_heading("7. Plan de Gestion des Risques de Planification & Pilotage par les KPIs", 1)
add_body(
    "Pour maîtriser les aléas susceptibles de compromettre le respect de l'échéancier et du chemin critique, l'équipe applique une gestion "
    "proactive des risques combinée à un tableau de bord d'indicateurs de performance (KPIs) audité chaque semaine."
)

tbl_risk = doc.add_table(rows=6, cols=6)
tbl_risk.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_risk.autofit = False
risk_widths = [Inches(0.5), Inches(1.8), Inches(0.5), Inches(0.5), Inches(0.7), Inches(2.97)]
risk_headers = ["ID", "Risque identifié", "P", "G", "Criticité", "Plan de prévention & parade opérationnelle"]

for c_idx, h in enumerate(risk_headers):
    c = tbl_risk.cell(0, c_idx)
    c.width = risk_widths[c_idx]
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=40, bottom=40, left=30, right=30)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2, 3, 4] else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(7.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

risks_plan_data = [
    ("RP1", "Dérive du chemin critique sur K (Intégration noyau)", "3", "4", "12 Élevée", 
     "Prévention : Utilisation du simulateur autonome en local. Parade : Mobilisation d'un binôme (Iyed + Akram) pour l'intégration."),
    ("RP2", "Retard de l'agent producteur de commande tiers", "3", "4", "12 Élevée", 
     "Prévention : Découplage strict via le bus et double lecture. Parade : Injection d'événements factices conformes au contrat."),
    ("RP3", "Non-respect de l'isolation multi-tenant / purge", "2", "4", "8 Moyenne", 
     "Prévention : Clés étrangères composites obligatoires. Parade : Banc de 15 tests automatisés avec blocage Git si 1 test échoue."),
    ("RP4", "Indisponibilité ponctuelle d'un membre", "2", "3", "6 Moyenne", 
     "Prévention : Binômage défini dans l'OBS/RACI. Parade : Reprise immédiate des tâches grâce à la documentation du code."),
    ("RP5", "Défaut de packaging Docker lors du test sur machine propre", "2", "3", "6 Moyenne", 
     "Prévention : Image multi-stage testée dès J9. Parade : Script de vérification automatisé de démarrage à froid.")
]

for r_idx, row in enumerate(risks_plan_data, start=1):
    bg_col = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
    for c_idx, val in enumerate(row):
        c = tbl_risk.cell(r_idx, c_idx)
        c.width = risk_widths[c_idx]
        set_cell_background(c, bg_col)
        set_cell_borders(c, top="E2E8F0", bottom="E2E8F0")
        set_cell_margins(c, top=25, bottom=25, left=30, right=30)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2, 3, 4] else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(7.2)
        if c_idx == 4:
            r.font.bold = True
            r.font.color.rgb = CRITICAL_RED if "Élevée" in val else NAVY
        else:
            r.font.color.rgb = CHARCOAL

add_heading("7.1. Tableau de Bord des Indicateurs Clés de Performance (KPIs)", 2)
add_body(
    "▪ SPI (Schedule Performance Index) = EV / PV : Mesure l'efficacité temporelle. Valeur cible maintenue : SPI >= 1.0 (zéro dérive).\n"
    "▪ Taux d'Exécution des Tests de Conformité = (Tests validés / 15) × 100 : Maintenu en permanence à 100 % (15/15 tests réussis).\n"
    "▪ Vélocité Réelle vs Prévue : Suivi hebdomadaire de la consommation des Jours-Hommes par rapport aux 36 JH alloués.\n"
    "▪ Taux d'Étanchéité Multi-tenant : Audit automatique après purge garantissant 0 enregistrement résiduel pour un tenant désactivé."
)

# ==============================================================================
# PAGE 8 : VALIDATION DU PLAN DE PROJET & SIGNATURES OFFICIELLES
# ==============================================================================
doc.add_page_break()

add_heading("8. Approbation, Validation du Plan de Projet & Signatures Officielles", 1)
add_body(
    "Le présent document de Planification Opérationnelle (Livrable 3 / Livrable L4) constitue le référentiel contractuel d'exécution de "
    "l'équipe VisionX. Il engage l'ensemble des membres sur les durées, les charges, les dépendances et les critères d'acceptation définis.\n\n"
    "Toute modification substantielle impactant le chemin critique fera l'objet d'un avenant validé collégialement en réunion de projet hebdomadaire.\n\n"
    "Fait à Amizour (ESTIN), le 07 Novembre 2026. Par leurs signatures ci-dessous, les membres approuvent et valident formellement ce plan :"
)

tbl_sign = doc.add_table(rows=4, cols=2)
tbl_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_sign.autofit = False
sign_widths = [Inches(3.48), Inches(3.49)]

sign_members = [
    ("Mohamed Anes Bouharizi\nChef d'équipe & Lead Tech Backend\n[Signature validée / Lu et approuvé]",
     "Sebti Iyed\nDéveloppeur API & Intégration Noyau\n[Signature validée / Lu et approuvé]"),
    ("Zouane Akram\nDéveloppeur Cœur Métier & Scoring\n[Signature validée / Lu et approuvé]",
     "Fellah Baha\nDéveloppeur Emailing & Campagnes\n[Signature validée / Lu et approuvé]"),
    ("Bertil Anis\nResponsable Données, Multi-tenant & Sécurité\n[Signature validée / Lu et approuvé]",
     "Bahi Adem\nResponsable Qualité, Recette & Docker\n[Signature validée / Lu et approuvé]")
]

for r_idx, (sig_l, sig_r) in enumerate(sign_members):
    for c_idx, sig_text in enumerate([sig_l, sig_r]):
        cell = tbl_sign.cell(r_idx, c_idx)
        cell.width = sign_widths[c_idx]
        set_cell_background(cell, "F8FAFC")
        set_cell_borders(cell, top="CBD5E1", bottom="CBD5E1", left="CBD5E1", right="CBD5E1")
        set_cell_margins(cell, top=60, bottom=60, left=90, right=90)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        
        lines = sig_text.split("\n")
        r_name = p.add_run(lines[0] + "\n")
        r_name.font.name = "Arial"
        r_name.font.size = Pt(8.5)
        r_name.font.bold = True
        r_name.font.color.rgb = NAVY
        
        r_role = p.add_run(lines[1] + "\n")
        r_role.font.name = "Arial"
        r_role.font.size = Pt(8)
        r_role.font.color.rgb = STEEL
        
        r_mention = p.add_run(lines[2])
        r_mention.font.name = "Arial"
        r_mention.font.size = Pt(7.5)
        r_mention.font.italic = True
        r_mention.font.color.rgb = RGBColor(46, 125, 50)

# Save file with both names as required by the guidelines
output_docx_1 = "/home/anes/Documents/VisionX/Conduite_PLAN_VisionX.docx"
output_docx_2 = "/home/anes/Documents/VisionX/Conduite_PLAN_equipe.docx"

doc.save(output_docx_1)
doc.save(output_docx_2)
print("Fichiers Word générés avec succès :")
print(" -", output_docx_1)
print(" -", output_docx_2)
