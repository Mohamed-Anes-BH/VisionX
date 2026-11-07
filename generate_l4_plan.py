import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
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

def set_cell_borders(cell, top="CBD5E1", bottom="CBD5E1", left=None, right=None):
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

# Configure page geometry (A4, 0.65" margins)
for s in doc.sections:
    s.top_margin = Inches(0.55)
    s.bottom_margin = Inches(0.55)
    s.left_margin = Inches(0.65)
    s.right_margin = Inches(0.65)
    s.page_width = Inches(8.27)
    s.page_height = Inches(11.69)
    footer = s.footer
    f_p = footer.paragraphs[0]
    f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    f_run = f_p.add_run("VisionX | Livrable L4 — Planification Opérationnelle (WBS, PERT, Gantt) | ESTIN 2026–2027")
    f_run.font.name = "Arial"
    f_run.font.size = Pt(8)
    f_run.font.color.rgb = RGBColor(128, 128, 128)

NAVY = RGBColor(27, 54, 93)      # #1B365D
STEEL = RGBColor(41, 128, 185)   # #2980B9
CHARCOAL = RGBColor(45, 55, 72)  # #2D3748
MUTED = RGBColor(100, 116, 139)  # #64748B
CRITICAL_RED = RGBColor(185, 28, 28)

def add_header_banner():
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(0)
    p_inst.paragraph_format.space_after = Pt(1)
    r_inst = p_inst.add_run("ÉCOLE SUPÉRIEURE EN SCIENCES ET TECHNOLOGIES DE L'INFORMATIQUE ET DU NUMÉRIQUE (ESTIN)")
    r_inst.font.name = "Arial"
    r_inst.font.size = Pt(8.5)
    r_inst.font.bold = True
    r_inst.font.color.rgb = MUTED

    p_mod = doc.add_paragraph()
    p_mod.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_mod.paragraph_format.space_before = Pt(0)
    p_mod.paragraph_format.space_after = Pt(6)
    r_mod = p_mod.add_run("2ème Année CS — Module Conduite de Projet (2026–2027) | Filière Métier : Agent Marketing Automation")
    r_mod.font.name = "Arial"
    r_mod.font.size = Pt(8)
    r_mod.font.color.rgb = MUTED

    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    c = tbl.cell(0, 0)
    c.width = Inches(6.97)
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=120, bottom=120, left=160, right=160)
    
    tp = c.paragraphs[0]
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tr1 = tp.add_run("LIVRABLE L4 — PLAN DE PROJET & PLANIFICATION OPÉRATIONNELLE\n")
    tr1.font.name = "Arial"
    tr1.font.size = Pt(12)
    tr1.font.bold = True
    tr1.font.color.rgb = RGBColor(255, 255, 255)
    
    tr2 = tp.add_run("WBS/OBS/RACI, Réseau PERT, Chemin Critique, Diagramme de Gantt & Estimation Budgétaire (36 JH)\n")
    tr2.font.name = "Arial"
    tr2.font.size = Pt(9.5)
    tr2.font.color.rgb = RGBColor(220, 235, 252)

    tr3 = tp.add_run("Équipe VisionX · Identifiant Agent : agent-marketing-automation-visionx · Jalon T5")
    tr3.font.name = "Arial"
    tr3.font.size = Pt(8.5)
    tr3.font.bold = True
    tr3.font.color.rgb = RGBColor(245, 180, 50)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_heading(text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.bold = True
    if level == 1:
        r.font.size = Pt(10.5)
        r.font.color.rgb = NAVY
    else:
        r.font.size = Pt(9)
        r.font.color.rgb = STEEL

def add_body_paragraph(text, before=0, after=3, indent=0.0):
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
# PAGE 1 : Présentation de la Planification, Hypothèses et Ressources
# ==============================================================================
add_header_banner()

# Meta summary
tbl_meta = doc.add_table(rows=2, cols=2)
tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_meta.autofit = False
meta_data = [
    ("Projet : VisionX — Agent Marketing Automation", "Équipe : 6 étudiants (Bouharizi, Sebti, Zouane, Fellah, Bertil, Bahi)"),
    ("Durée calendaire prévisionnelle : 20 jours ouvrés", "Charge totale prévisionnelle : 36 Jours-Hommes (JH)")
]
for r_idx, row in enumerate(meta_data):
    for c_idx, val in enumerate(row):
        c = tbl_meta.cell(r_idx, c_idx)
        c.width = Inches(3.48)
        set_cell_background(c, "F8FAFC" if r_idx % 2 == 0 else "FFFFFF")
        set_cell_margins(c, top=40, bottom=40, left=80, right=80)
        p = c.paragraphs[0]
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(8)
        r.font.color.rgb = CHARCOAL

add_heading("1.1. Introduction et Objectifs du Document de Planification (L4)", 1)
add_body_paragraph(
    "Le présent document constitue le Livrable L4 officiel de l'équipe VisionX. Il fait suite à la validation de la Charte de Projet (L2) "
    "et du Procès-Verbal de Lancement (L3). L'objectif est d'opérationnaliser la démarche de conduite de projet en traduisant les objectifs "
    "fonctionnels et techniques en un ordonnancement temporel rigoureux. La planification structure l'enchaînement logique des 14 activités "
    "du projet, identifie les contraintes de précédence, optimise l'allocation des 6 ressources humaines, calcule les marges de sécurité via le "
    "réseau PERT, et formalise le budget prévisionnel ainsi que les jalons de contrôle jusqu'à la livraison finale (Jalon T6 / T8)."
)

add_heading("1.2. Hypothèses de Planification & Cadre Temporel", 1)
add_body_paragraph(
    "La modélisation du planning repose sur un ensemble d'hypothèses réalistes adaptées aux exigences académiques de l'ESTIN :\n"
    "▪ Base de temps : Le projet est calibré sur une durée calendaire de 20 jours ouvrés (notés J1 à J20), hors week-ends.\n"
    "▪ Régime de travail : Équipe de 6 élèves-ingénieurs mobilisés en parallèle, représentant une capacité totale cible de 36 Jours-Hommes (JH).\n"
    "▪ Découplage technique : Conformément à la Règle 4 du sujet (cloisonnement de code), aucun travail n'est subordonné au code source "
    "d'autres équipes. Les dépendances avec l'Agent Commercial (consommateur de prospects) et l'Agent Facturation (producteur de commandes) "
    "sont découplées par le bus d'échange du noyau central et simulées localement en phase de test via des mocks conformes aux contrats."
)

add_heading("1.3. Rappel de l'OBS (Organisation) & Matrice RACI Consolidée", 1)
add_body_paragraph(
    "L'équipe VisionX applique une gouvernance distribuée où chaque lot de travail possède un pilote unique (Accountable) assisté par des "
    "contributeurs spécialisés (Responsible, Consulted, Informed) :"
)

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
    ("WP1 : Cadrage & Spécifications", "A / R", "R", "R", "C", "C", "I"),
    ("WP2 : Socle Backend & Multi-tenant", "C", "A / R", "I", "R", "C", "R"),
    ("WP3 : Moteur Métier (Prospect & Lead Scoring)", "I", "C", "C", "R", "A / R", "I"),
    ("WP4 : Moteur Événementiel (Commandes & Emailing)", "I", "R", "A / R", "I", "R", "R"),
    ("WP5 : Intégration Noyau & Bus d'Échange", "C", "A / R", "R", "I", "C", "I"),
    ("WP6 : Assurance Qualité, Tests & Déploiement", "A", "C", "I", "I", "C", "A / R")
]
for r_idx, row in enumerate(raci_data, start=1):
    bg_col = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
    for c_idx, val in enumerate(row):
        c = tbl_raci.cell(r_idx, c_idx)
        c.width = raci_widths[c_idx]
        set_cell_background(c, bg_col)
        set_cell_borders(c, top="E2E8F0", bottom="E2E8F0")
        set_cell_margins(c, top=30, bottom=30, left=40, right=40)
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

# ==============================================================================
# PAGE 2 : Liste des Tâches, Durées et Dépendances
# ==============================================================================
doc.add_page_break()

add_heading("2. Décomposition des Tâches, Durées et Matrice des Dépendances", 1)
add_body_paragraph(
    "Le projet est décomposé en 14 activités élémentaires (A à N) couvrant l'ensemble du cycle de développement de l'agent. "
    "Chaque tâche possède un responsable clairement identifié, une durée calendaire estimée (en jours), une charge d'effort (en JH), "
    "des antécédents immédiats (prédécesseurs) et un livrable technique vérifiable."
)

tbl_tasks = doc.add_table(rows=15, cols=7)
tbl_tasks.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_tasks.autofit = False
t_widths = [Inches(0.4), Inches(2.2), Inches(1.2), Inches(0.5), Inches(0.5), Inches(0.6), Inches(1.57)]
t_headers = ["ID", "Intitulé de l'activité", "Responsable(s)", "Dur.", "Chg.", "Préd.", "Livrable technique associé"]

for c_idx, h in enumerate(t_headers):
    c = tbl_tasks.cell(0, c_idx)
    c.width = t_widths[c_idx]
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=40, bottom=40, left=40, right=40)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 3, 4, 5] else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(7.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

tasks_list = [
    ("A", "Cadrage et validation des contrats", "Anes", "1 j", "1 JH", "—", "Documents L1 & L2 validés"),
    ("B", "Spécifications fonctionnelles et tech.", "Anes, Iyed, Akram", "2 j", "3 JH", "A", "Dossier de specs d'API & schémas"),
    ("C", "Conception de l'architecture backend", "Anes, Iyed", "2 j", "2 JH", "B", "Schémas UML & routes FastAPI"),
    ("D", "Modélisation de la base de données", "Baha", "2 j", "2 JH", "B", "Schéma relationnel & DDL SQLite/PG"),
    ("E", "Développement du socle FastAPI", "Iyed", "3 j", "3 JH", "C", "5 endpoints obligatoires & enveloppe"),
    ("F", "Isolation multi-tenant et persistance", "Baha, Adem", "2 j", "3 JH", "D, E", "Middleware tenant & script purge"),
    ("G", "Gestion prospects et Lead Scoring", "Anis, Baha", "2 j", "3 JH", "F", "Module scoring (seuil >= 70)"),
    ("H", "Réception et traitement commandes", "Akram, Iyed", "2 j", "2 JH", "F", "Handler /exchange/notify (commandes)"),
    ("I", "Moteur email Jinja2/SMTP modulaire", "Anis, Adem", "2 j", "2 JH", "C", "Service SMTP & templates HTML/texte"),
    ("J", "Automatisations et campagnes marketing", "Anis", "2 j", "2 JH", "G, H, I", "Workflows onboarding & win-back"),
    ("K", "Intégration complète avec le noyau", "Iyed, Akram", "3 j", "3 JH", "G, H", "Publication bus prospect & handshake"),
    ("M", "Conteneurisation et config. Docker", "Adem", "1 j", "1 JH", "E", "Dockerfile autonome & compose"),
    ("L", "Tests fonctionnels, intégration et sécu", "Toute l'équipe", "3 j", "6 JH", "J, K, M", "Suite 15 tests pytest validée"),
    ("N", "Documentation et préparation démo", "Anes, toute équipe", "2 j", "3 JH", "L", "README d'exploitation & support démo")
]

for r_idx, (t_id, t_name, t_resp, t_dur, t_chg, t_pred, t_liv) in enumerate(tasks_list, start=1):
    bg_col = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
    vals = [t_id, t_name, t_resp, t_dur, t_chg, t_pred, t_liv]
    for c_idx, val in enumerate(vals):
        c = tbl_tasks.cell(r_idx, c_idx)
        c.width = t_widths[c_idx]
        set_cell_background(c, bg_col)
        set_cell_borders(c, top="E2E8F0", bottom="E2E8F0")
        set_cell_margins(c, top=25, bottom=25, left=40, right=40)
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
add_body_paragraph(
    "Conformément à la section 3 du sujet d'examen, la filière Métier repose sur un mécanisme de publication/consommation asynchrone :\n"
    "▪ Dépendance Sortante (Production de 'prospect') : Lorsque l'activité G évalue un prospect avec un score >= 70, l'agent publie "
    "l'objet vers le bus via POST {NOYAU_URL}/exchange/agent/prospect. L'Agent Commercial consomme ce flux pour alimenter son pipeline. "
    "Si l'Agent Commercial n'est pas encore souscrit ou indisponible, le noyau conserve l'événement sans bloquer notre agent.\n"
    "▪ Dépendance Entrante (Consommation de 'commande') : L'activité H écoute les notifications POST /exchange/notify transmises par "
    "le noyau lorsque l'Agent Facturation émet une commande confirmée ou annulée. VisionX réagit en déclenchant la campagne J appropriée.\n"
    "▪ Garantie d'Indépendance : Grâce au simulateur autonome (simulateur_marche_marketing.py), VisionX a validé l'ensemble de ses "
    "échanges en local, garantissant une étanchéité totale vis-à-vis du calendrier d'avancement des autres équipes."
)

# ==============================================================================
# PAGE 3 : Réseau PERT et Calcul du Chemin Critique
# ==============================================================================
doc.add_page_break()

add_heading("3. Réseau PERT et Calcul Analytique du Chemin Critique", 1)
add_body_paragraph(
    "La méthode PERT (Program Evaluation and Review Technique) permet de modéliser le réseau des dépendances, de calculer les dates au "
    "plus tôt (Early Start/Finish), les dates au plus tard (Late Start/Finish), les marges libres et totales, et d'isoler le chemin critique "
    "qui détermine la durée incompressible minimale du projet."
)

add_heading("3.1. Tableau Analytique des Dates et des Marges (Algorithme CPM/PERT)", 2)

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
    ("G", "Prospects & Lead Scoring", "2 j", "10", "12", "10", "12", "0 j", "CRITIQUE (Branche parallèle 1)"),
    ("H", "Traitement des commandes", "2 j", "10", "12", "10", "12", "0 j", "CRITIQUE (Branche parallèle 2)"),
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

add_heading("3.2. Analyse Approfondie du Chemin Critique & Stratégie de Pilotage", 2)
add_body_paragraph(
    "▪ Équation du Chemin Critique : Le projet présente deux branches jumelles critiques d'une durée identique de 20 jours ouvrés :\n"
    "    Chemin 1 : A (1j) → B (2j) → C (2j) → E (3j) → F (2j) → G (2j) → K (3j) → L (3j) → N (2j) = 20 jours.\n"
    "    Chemin 2 : A (1j) → B (2j) → C (2j) → E (3j) → F (2j) → H (2j) → K (3j) → L (3j) → N (2j) = 20 jours.\n"
    "▪ Signification Opérationnelle : Les tâches situées sur ces deux chemins possèdent une marge totale strictement nulle (MT = 0). "
    "Tout retard d'une seule journée sur l'une de ces 10 tâches décale mécaniquement la date de livraison finale du projet. "
    "Le Chef de Projet appliquera un suivi quotidien sur les lots E (FastAPI), F (Multi-tenant), G/H (Métier) et K (Intégration noyau).\n"
    "▪ Exploitation des Marges (Flexibilité) :\n"
    "    - Tâche D (Base de données) : Dispose de 3 jours de marge. Peut démarrer entre J4 et J7 sans impacter F.\n"
    "    - Tâche I (Emailing SMTP) : Dispose de 6 jours de marge totale. Peut s'exécuter sereinement en tâche de fond.\n"
    "    - Tâche M (Dockerisation) : Dispose de 6 jours de marge. Programmée dès que E est prêt, garantissant zéro stress avant L.\n"
    "    - Tâche J (Campagnes) : Dispose de 1 jour de marge par rapport au début des tests globaux L (qui attend la fin de K à J15)."
)

# ==============================================================================
# PAGE 4 : Diagramme de Gantt Prévisionnel
# ==============================================================================
doc.add_page_break()

add_heading("4. Diagramme de Gantt Prévisionnel & Calendrier d'Exécution (J1 à J20)", 1)
add_body_paragraph(
    "Le diagramme de Gantt ci-dessous traduit l'ordonnancement PERT en un calendrier opérationnel sur 20 jours ouvrés. "
    "Il met en évidence la synchronisation des tâches parallèles et les passages de témoins critiques entre développeurs."
)

# Gantt Table (22 cols: Task, Resp, J1..J20)
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

# Gantt task schedule (1-indexed start day, end day, is_critical)
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
            # Active task day
            bar_color = "DC2626" if is_crit else "2563EB"  # Rouge vif si critique, Bleu royal si parallèle
            set_cell_background(cell_d, bar_color)
            r_bar = p_d.add_run("■")
            r_bar.font.name = "Arial"
            r_bar.font.size = Pt(6)
            r_bar.font.color.rgb = RGBColor(255, 255, 255)
        else:
            bg_empty = "F1F5F9" if day in [5, 10, 15, 20] else ("FFFFFF" if r_idx % 2 == 0 else "F8FAFC")
            set_cell_background(cell_d, bg_empty)
            set_cell_borders(cell_d, top="E2E8F0", bottom="E2E8F0")

add_body_paragraph(
    "Légende du Gantt : [■ Rouge] = Tâches sur le Chemin Critique (zéro marge). [■ Bleu] = Tâches parallèles non critiques (avec marge).\n"
    "Jalons clés : Jalon 1 (Conception validée à J5), Jalon 2 (Socle API à J10), Jalon 3 (Métier prêt à J14), Jalon 4 (Intégration validée à J15), Jalon 5 (Recette à J18), Jalon 6 (Livraison à J20).",
    before=4, after=4
)

add_heading("4.1. Lissage et Régulation de la Charge Humaine", 2)
add_body_paragraph(
    "L'inspection du diagramme de Gantt démontre un équilibre rigoureux de l'effort : le parallélisme n'excède jamais 3 chantiers "
    "simultanés (ex: J4-J5 avec C et D ; J6-J7 avec E et I ; J11-J12 avec G et H ; J13-J14 avec J et K). Aucun membre n'est sollicité "
    "à plus de 100 % de son temps sur un jour donné, ce qui supprime tout risque de goulot d'étranglement ou de burn-out individuel."
)

# ==============================================================================
# PAGE 5 : Estimation des Charges et Budget Prévisionnel
# ==============================================================================
doc.add_page_break()

add_heading("5. Estimation des Charges en Jours-Hommes (JH) et Modélisation Budgétaire", 1)
add_body_paragraph(
    "Une distinction méthodologique essentielle est opérée entre la durée calendaire du projet (20 jours ouvrés) et la charge de travail "
    "humain globale (36 Jours-Hommes cumulés). La charge représente l'effort effectif de conception, développement, test et documentation."
)

add_heading("5.1. Répartition Nominative de la Charge de Travail (36 JH)", 2)

tbl_chg = doc.add_table(rows=8, cols=4)
tbl_chg.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_chg.autofit = False
chg_widths = [Inches(1.8), Inches(2.2), Inches(1.0), Inches(1.97)]
chg_headers = ["Membre de l'équipe", "Domaines d'intervention principaux", "Charge cible", "Pourcentage d'effort"]

for c_idx, h in enumerate(chg_headers):
    c = tbl_chg.cell(0, c_idx)
    c.width = chg_widths[c_idx]
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

chg_data = [
    ("Mohamed Anes Bouharizi", "Coordination, cadrage A, specs B, architecture C, doc N", "6 JH", "16.7 %"),
    ("Sebti Iyed", "Specs B, backend FastAPI E, intégration noyau K", "7 JH", "19.4 %"),
    ("Zouane Akram", "Specs B, traitement commandes H, intégration noyau K", "5 JH", "13.9 %"),
    ("Fellah Baha", "Modélisation base D, isolation multi-tenant F, tests L", "6 JH", "16.7 %"),
    ("Bertil Anis", "Lead scoring G, moteur emailing I, campagnes marketing J", "6 JH", "16.7 %"),
    ("Bahi Adem", "Multi-tenant F, conteneurisation Docker M, banc de tests L", "6 JH", "16.7 %"),
    ("TOTAL CONSOLIDÉ", "Ensemble des 14 activités du projet VisionX", "36 JH", "100.0 %")
]

for r_idx, (m_nom, m_dom, m_chg, m_pct) in enumerate(chg_data, start=1):
    is_tot = (r_idx == 7)
    bg_col = "1E293B" if is_tot else ("F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
    for c_idx, val in enumerate([m_nom, m_dom, m_chg, m_pct]):
        c = tbl_chg.cell(r_idx, c_idx)
        c.width = chg_widths[c_idx]
        set_cell_background(c, "1B365D" if is_tot else bg_col)
        set_cell_borders(c, top="CBD5E1", bottom="CBD5E1")
        set_cell_margins(c, top=30, bottom=30, left=40, right=40)
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

add_heading("5.2. Budget Prévisionnel et Analyse des Coûts", 2)
add_body_paragraph(
    "Le modèle économique du projet VisionX tire parti des technologies Open Source libres de droits, réduisant les coûts réels décaissés "
    "à zéro dinar tout en permettant une valorisation financière académique rigoureuse de la prestation intellectuelle fournie."
)

tbl_bud = doc.add_table(rows=6, cols=4)
tbl_bud.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_bud.autofit = False
bud_widths = [Inches(1.8), Inches(2.6), Inches(1.3), Inches(1.27)]
bud_headers = ["Catégorie de coût", "Description des ressources mobilisées", "Base de calcul", "Montant valorisé"]

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
    ("Logiciels & Frameworks", "Python 3.10+, FastAPI, SQLite, Pydantic, Jinja2, MailHog", "Licences MIT / BSD / FOSS", "0 DA (Débours réel 0)"),
    ("Infrastructure & Serveurs", "Docker Engine, environnements locaux étudiants, git privé", "Ressources locales & ESTIN", "0 DA (Débours réel 0)"),
    ("Main-d'œuvre intellectuelle", "Prestation d'ingénierie des 6 étudiants de VisionX (36 JH)", "36 JH × 4 000 DA/JH", "144 000 DA (Valorisé)"),
    ("Réserve pour imprévus (10%)", "Marge de sécurité technique & aléas de recette (+10 %)", "10 % du coût main-d'œuvre", "14 400 DA (Réserve)"),
    ("COÛT TOTAL DU PROJET", "Budget complet valorisé (Débours effectif décaissé = 0 DA)", "Formule standard L4", "158 400 DA (Valorisé)")
]

for r_idx, (b_cat, b_desc, b_base, b_mnt) in enumerate(bud_data, start=1):
    is_tot = (r_idx == 5)
    bg_col = "1B365D" if is_tot else ("F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
    for c_idx, val in enumerate([b_cat, b_desc, b_base, b_mnt]):
        c = tbl_bud.cell(r_idx, c_idx)
        c.width = bud_widths[c_idx]
        set_cell_background(c, bg_col)
        set_cell_borders(c, top="CBD5E1", bottom="CBD5E1")
        set_cell_margins(c, top=30, bottom=30, left=40, right=40)
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
# PAGE 6 : Jalons, Suivi et Validation du Planning
# ==============================================================================
doc.add_page_break()

add_heading("6. Jalons de Contrôle, Gouvernance et Validation du Planning", 1)
add_body_paragraph(
    "Pour garantir le respect strict des échéances jusqu'au jalon final d'évaluation (T8 / Soutenance T9), l'équipe VisionX instaure "
    "un protocole de gouvernance jalonné, un tableau de bord d'indicateurs clés de performance (KPI) et une gestion active des risques."
)

add_heading("6.1. Matrice des Jalons de Contrôle Officiels", 2)

tbl_jal = doc.add_table(rows=7, cols=5)
tbl_jal.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_jal.autofit = False
j_widths = [Inches(0.6), Inches(1.8), Inches(0.8), Inches(1.97), Inches(1.8)]
j_headers = ["Jalon", "Intitulé du Jalon", "Échéance", "Critère de validation opérationnel", "Livrable formel"]

for c_idx, h in enumerate(j_headers):
    c = tbl_jal.cell(0, c_idx)
    c.width = j_widths[c_idx]
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

jal_data = [
    ("J1", "Conception & Architecture", "Fin J5", "Validation schémas DDL et signature des endpoints", "Livrable L2 (Charte)"),
    ("J2", "Socle API & Multi-tenant", "Fin J10", "5 routes obligatoires opérationnelles + purge vérifiée", "Socle testé en local"),
    ("J3", "Moteur Métier & Campagnes", "Fin J14", "Scoring prospect >= 70 actif + traitement commandes", "Modules G, H, J prêts"),
    ("J4", "Intégration Noyau & Bus", "Fin J15", "Publication/réception fluides via /exchange/...", "Livrable L3 (PV Lancement)"),
    ("J5", "Recette Qualité & Conformité", "Fin J18", "15/15 tests automatisés validés à 100 %, 0 faille", "Livrable L4 (Planning)"),
    ("J6", "Déploiement & Soutenance", "Fin J20", "Image Docker livrée sur GitHub privé, démo prête", "Livrables L5, L6, L7, L8")
]

for r_idx, (j_id, j_nom, j_ech, j_crit, j_liv) in enumerate(jal_data, start=1):
    bg_col = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
    for c_idx, val in enumerate([j_id, j_nom, j_ech, j_crit, j_liv]):
        c = tbl_jal.cell(r_idx, c_idx)
        c.width = j_widths[c_idx]
        set_cell_background(c, bg_col)
        set_cell_borders(c, top="CBD5E1", bottom="CBD5E1")
        set_cell_margins(c, top=30, bottom=30, left=40, right=40)
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

add_heading("6.2. Indicateurs Clés de Pilotage (Tableau de Bord KPI)", 2)
add_body_paragraph(
    "Le Chef de Projet assure un contrôle hebdomadaire à l'aide de 4 indicateurs quantitatifs clés :\n"
    "▪ SPI (Schedule Performance Index) = EV / PV : Mesure du respect des délais (objectif SPI >= 1.0).\n"
    "▪ Taux d'Exécution des Tests = (Tests Validés / 15) × 100 : Maintenu en permanence à 100 % (zéro régression tolérée).\n"
    "▪ Reste à Faire (Burn-down) : Suivi des Jours-Hommes résiduels par rapport aux 36 JH prévus.\n"
    "▪ Taux d'Étanchéité Multi-tenant : Vérification par script d'audit qu'aucune trace résiduelle n'existe après désactivation."
)

add_heading("6.3. Approbation et Engagement Formel de l'Équipe", 2)
add_body_paragraph(
    "Le présent Plan de Projet (Livrable L4) est déclaré officiel et opposable. Il engage l'ensemble de l'équipe VisionX dans "
    "sa trajectoire de livraison. Toute modification substantielle du chemin critique fera l'objet d'un avenant soumis en réunion d'équipe.",
    after=6
)

tbl_app = doc.add_table(rows=2, cols=3)
tbl_app.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_app.autofit = False
app_widths = [Inches(2.32), Inches(2.32), Inches(2.33)]
app_data = [
    ("Élaboré par :", "Vérifié par :", "Approuvé pour exécution :"),
    ("Mohamed Anes Bouharizi\nChef de Projet & Lead Tech\nDate : 07/11/2026\n[Signé électroniquement]",
     "Sebti Iyed & Bahi Adem\nArchitecture & Assurance Qualité\nDate : 07/11/2026\n[Signé électroniquement]",
     "L'Équipe VisionX au complet\nValidation collégiale L4\nDate : 07/11/2026\n[Signé électroniquement]")
]
for r_idx, row in enumerate(app_data):
    for c_idx, val in enumerate(row):
        c = tbl_app.cell(r_idx, c_idx)
        c.width = app_widths[c_idx]
        set_cell_background(c, "1B365D" if r_idx == 0 else "F8FAFC")
        set_cell_margins(c, top=30, bottom=30, left=40, right=40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if r_idx == 1 else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(7.2)
        if r_idx == 0:
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
        else:
            r.font.color.rgb = CHARCOAL

doc.save("/home/anes/Documents/VisionX/METIER_PLAN_AgentMarketing.docx")
print("METIER_PLAN_AgentMarketing.docx généré avec succès !")
