import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
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

def set_cell_borders(cell, top="CCCCCC", bottom="CCCCCC", left=None, right=None):
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

# Page Margins
sections = doc.sections
for s in sections:
    s.top_margin = Inches(0.6)
    s.bottom_margin = Inches(0.6)
    s.left_margin = Inches(0.7)
    s.right_margin = Inches(0.7)
    s.page_width = Inches(8.27)  # A4
    s.page_height = Inches(11.69)
    # Header & Footer
    footer = s.footer
    f_p = footer.paragraphs[0]
    f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    f_run = f_p.add_run("VisionX | Livrable L3 — PV de Réunion de Lancement | Module Conduite de Projet ESTIN")
    f_run.font.name = "Arial"
    f_run.font.size = Pt(8)
    f_run.font.color.rgb = RGBColor(128, 128, 128)

PRIMARY_COLOR = RGBColor(24, 76, 120)    # Bleu marine
SECONDARY_COLOR = RGBColor(41, 128, 185) # Bleu roi
TEXT_COLOR = RGBColor(40, 40, 40)

def add_header_banner():
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(0)
    p_inst.paragraph_format.space_after = Pt(2)
    r_inst = p_inst.add_run("ÉCOLE SUPÉRIEURE EN SCIENCES ET TECHNOLOGIES DE L'INFORMATIQUE ET DU NUMÉRIQUE (ESTIN)")
    r_inst.font.name = "Arial"
    r_inst.font.size = Pt(8.5)
    r_inst.font.bold = True
    r_inst.font.color.rgb = RGBColor(100, 100, 100)

    p_mod = doc.add_paragraph()
    p_mod.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_mod.paragraph_format.space_before = Pt(0)
    p_mod.paragraph_format.space_after = Pt(8)
    r_mod = p_mod.add_run("2ème Année CS — Module Conduite de Projet (2026–2027) | Enseignant : Dr. Noyau / Équipe Pédagogique")
    r_mod.font.name = "Arial"
    r_mod.font.size = Pt(8)
    r_mod.font.color.rgb = RGBColor(120, 120, 120)

    # Title box table
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    c = tbl.cell(0, 0)
    c.width = Inches(6.87)
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=140, bottom=140, left=180, right=180)
    
    tp = c.paragraphs[0]
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tr1 = tp.add_run("LIVRABLE L3 — PROCÈS-VERBAL DE RÉUNION DE LANCEMENT\n")
    tr1.font.name = "Arial"
    tr1.font.size = Pt(13)
    tr1.font.bold = True
    tr1.font.color.rgb = RGBColor(255, 255, 255)
    
    tr2 = tp.add_run("Kick-off Meeting & Engagement Collectif sur le Contrat d'Intégration\n")
    tr2.font.name = "Arial"
    tr2.font.size = Pt(10.5)
    tr2.font.color.rgb = RGBColor(220, 235, 252)

    tr3 = tp.add_run("Équipe VisionX · Agent Marketing Automation (Filière Métier)")
    tr3.font.name = "Arial"
    tr3.font.size = Pt(9.5)
    tr3.font.bold = True
    tr3.font.color.rgb = RGBColor(245, 180, 50)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

add_header_banner()

# Meta table
tbl_meta = doc.add_table(rows=3, cols=2)
tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_meta.autofit = False
meta_widths = [Inches(3.43), Inches(3.44)]
meta_data = [
    ("Date & Heure : Samedi 07 Novembre 2026, 14h00 – 16h30", "Lieu : Salle de projet / Visioconférence ESTIN"),
    ("Projet : VisionX — Agent Marketing Automation", "Slug Agent : agent-marketing-automation-visionx"),
    ("Présidence de séance : Mohamed Anes Bouharizi", "Secrétariat de séance : Sebti Iyed & Bahi Adem")
]
for r_idx, row in enumerate(meta_data):
    for c_idx, val in enumerate(row):
        cell = tbl_meta.cell(r_idx, c_idx)
        cell.width = meta_widths[c_idx]
        set_cell_background(cell, "F4F6F9" if r_idx % 2 == 0 else "FFFFFF")
        set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True if ":" in val else False
        r.font.color.rgb = TEXT_COLOR

def add_heading(text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.bold = True
    if level == 1:
        r.font.size = Pt(11)
        r.font.color.rgb = PRIMARY_COLOR
    else:
        r.font.size = Pt(9.5)
        r.font.color.rgb = SECONDARY_COLOR

add_heading("1. Ordre du Jour & Contexte de la Réunion", 1)
p_ctx = doc.add_paragraph()
p_ctx.paragraph_format.space_before = Pt(0)
p_ctx.paragraph_format.space_after = Pt(4)
p_ctx.paragraph_format.line_spacing = 1.15
r_ctx = p_ctx.add_run(
    "Faisant suite à la validation du Document d'Orientation (L1) et de la Charte de Projet (L2), l'ensemble des six membres "
    "de l'équipe VisionX s'est réuni en séance plénière pour officialiser le lancement des travaux de réalisation de l'Agent Marketing Automation. "
    "L'ordre du jour portait sur : (1) La validation collective du périmètre fonctionnel et contractuel, (2) L'attribution formelle des rôles et "
    "responsabilités (OBS/RACI), (3) Le verrouillage des choix d'architecture technique, et (4) La signature solennelle de l'engagement d'équipe "
    "garantissant la stricte conformité aux contrats d'intégration fournis par l'enseignant."
)
r_ctx.font.name = "Arial"
r_ctx.font.size = Pt(8.5)
r_ctx.font.color.rgb = TEXT_COLOR

add_heading("2. Attribution Formelle des Rôles & Responsabilités (OBS)", 1)
tbl_roles = doc.add_table(rows=7, cols=3)
tbl_roles.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_roles.autofit = False
col_widths = [Inches(1.8), Inches(2.2), Inches(2.87)]

headers = ["Membre de l'équipe", "Rôle principal (OBS)", "Périmètre de responsabilité directe"]
for c_idx, h in enumerate(headers):
    c = tbl_roles.cell(0, c_idx)
    c.width = col_widths[c_idx]
    set_cell_background(c, "1B365D")
    set_cell_margins(c, top=80, bottom=80, left=100, right=100)
    p = c.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(8.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

members = [
    ("Mohamed Anes Bouharizi", "Chef de Projet & Lead Tech", "Pilotage global, respect des jalons T1 à T9, architecture FastAPI, packaging Docker."),
    ("Sebti Iyed", "Architecte Intégration Noyau", "Conformité des 5 endpoints obligatoires, cycle de vie tenant, publication/consommation du bus."),
    ("Zouane Akram", "Lead Algorithme & Scoring", "Moteur de qualification prospect (score >= 70), déclenchement automatique de publication."),
    ("Fellah Baha", "Lead Emailing & Scénarios", "Moteur de campagnes réactives (bienvenue, relance post-commande, win-back), templates Jinja2."),
    ("Bertil Anis", "Responsable Sécurité & Données", "Isolation multi-tenant stricte par schéma/tenant_id, procédure et validation de purge intégrale."),
    ("Bahi Adem", "Lead QA, Conformité & Recette", "Banc de tests unitaires/intégration (15 tests validés), conformité enveloppe {status, data, error}.")
]

for r_idx, (m_nom, m_role, m_desc) in enumerate(members, start=1):
    bg_col = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
    for c_idx, val in enumerate([m_nom, m_role, m_desc]):
        c = tbl_roles.cell(r_idx, c_idx)
        c.width = col_widths[c_idx]
        set_cell_background(c, bg_col)
        set_cell_borders(c, top="E2E8F0", bottom="E2E8F0")
        set_cell_margins(c, top=50, bottom=50, left=80, right=80)
        p = c.paragraphs[0]
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(8)
        if c_idx == 0:
            r.font.bold = True
        r.font.color.rgb = TEXT_COLOR

add_heading("3. Décisions Techniques et Opérationnelles Actées", 1)
decisions = [
    ("Framework Backend :", " Adoption définitive de Python 3.10+ avec FastAPI et Pydantic v2 pour des performances asynchrones optimales et une validation native des payloads."),
    ("Échanges avec le Noyau :", " Publication sur POST {NOYAU_URL}/exchange/agent/prospect (score >= 70) et consommation sur POST /exchange/notify (commandes)."),
    ("Enveloppe Contractuelle :", " Respect absolu et systématique du format {'status': 'ok'|'error', 'data': {...}|null, 'error': msg|null} sur les 5 routes obligatoires."),
    ("Sécurité & Purge :", " Cloisonnement étanche des données par X-Tenant-Id. Purge immédiate et irréversible à la réception de POST /tenant/deactivate."),
    ("Arbitrage Mautic :", " Abandon validé de l'infrastructure lourde Mautic au profit d'un micro-moteur natif léger Jinja2/SMTP consommant moins de 150 Mo de RAM.")
]
for tit, desc in decisions:
    p_dec = doc.add_paragraph()
    p_dec.paragraph_format.space_before = Pt(1)
    p_dec.paragraph_format.space_after = Pt(2)
    p_dec.paragraph_format.left_indent = Inches(0.2)
    p_dec.paragraph_format.line_spacing = 1.15
    r_bullet = p_dec.add_run("▪ ")
    r_bullet.font.bold = True
    r_bullet.font.color.rgb = SECONDARY_COLOR
    r_t = p_dec.add_run(tit)
    r_t.font.name = "Arial"
    r_t.font.size = Pt(8.5)
    r_t.font.bold = True
    r_t.font.color.rgb = PRIMARY_COLOR
    r_d = p_dec.add_run(desc)
    r_d.font.name = "Arial"
    r_d.font.size = Pt(8.5)
    r_d.font.color.rgb = TEXT_COLOR

# Page break to keep signatures and engagement cleanly on Page 2
doc.add_page_break()

add_heading("4. Engagement Collectif sur le Contrat d'Intégration & les Règles du Projet", 1)
p_eng_box = doc.add_paragraph()
p_eng_box.paragraph_format.space_before = Pt(2)
p_eng_box.paragraph_format.space_after = Pt(6)
p_eng_box.paragraph_format.line_spacing = 1.15

r_eng_pre = p_eng_box.add_run(
    "Les soussignés, membres de l'équipe VisionX, attestent avoir pris connaissance intégrale des documents contractuels "
    "fournis par l'enseignant et s'engagent formellement sur l'honneur à respecter les clauses suivantes durant l'intégralité du cycle de vie du projet :\n"
)
r_eng_pre.font.name = "Arial"
r_eng_pre.font.size = Pt(8.5)
r_eng_pre.font.color.rgb = TEXT_COLOR

clauses = [
    ("Conformité Stricte au Contrat d'Intégration (AGENT_INTEGRATION_CONTRACT.doc) : ", 
     "Implémenter sans déviation les 5 endpoints obligatoires (/health, /tenant/activate, /tenant/deactivate, /tenant/{id}/status, /config-schema), "
     "l'authentification par clé API Bearer, la validation du header X-Tenant-Id, et l'enveloppe de réponse standardisée."),
    
    ("Conformité au Registre de Données Partagées (INTER_AGENT_DATA_CONTRACT.doc) : ", 
     "Publier l'objet prospect avec les champs exacts (id_prospect, nom, email, score_interet, statut) et consommer rigoureusement "
     "l'objet commande (numero_commande, date_commande, client, lignes, montant_total_ht, statut) sans altération structurelle."),
    
    ("Règle Fondamentale de Cloisonnement du Code (Section 4 du Sujet) : ", 
     "Interdiction absolue et totale de consulter, copier, référencer ou appeler directement le code source d'une autre équipe. "
     "Toute collaboration et échange inter-agents s'opèrent EXCLUSIVEMENT par l'intermédiaire du bus d'événements du noyau central. "
     "L'équipe reconnaît que tout manquement à cette règle entraîne des sanctions immédiates pour violation d'intégrité académique."),
    
    ("Exigences Techniques de Déploiement & Traçabilité (Sections 5 et 6) : ", 
     "Fournir un conteneur Docker autonome et testé, un fichier agent.manifest.json valide, un README d'exploitation complet, "
     "et assurer une traçabilité rigoureuse via des commits fréquents et explicites sur le dépôt GitHub privé officiel."),
    
    ("Solidarité et Responsabilité d'Équipe : ", 
     "Assurer l'entraide technique interne, la transparence sur l'avancement, la tenue des revues de code, et la garantie "
     "que l'agent sera 100 % opérationnel lors de la phase d'assemblage en direct (Jalon T6 / Démonstration T8).")
]

for cl_t, cl_d in clauses:
    p_cl = doc.add_paragraph()
    p_cl.paragraph_format.space_before = Pt(1)
    p_cl.paragraph_format.space_after = Pt(3)
    p_cl.paragraph_format.left_indent = Inches(0.2)
    p_cl.paragraph_format.line_spacing = 1.15
    r_check = p_cl.add_run("✔ ")
    r_check.font.bold = True
    r_check.font.color.rgb = SECONDARY_COLOR
    r_t = p_cl.add_run(cl_t)
    r_t.font.name = "Arial"
    r_t.font.size = Pt(8.5)
    r_t.font.bold = True
    r_t.font.color.rgb = PRIMARY_COLOR
    r_d = p_cl.add_run(cl_d)
    r_d.font.name = "Arial"
    r_d.font.size = Pt(8.5)
    r_d.font.color.rgb = TEXT_COLOR

add_heading("5. Échéancier Immédiat & Préparation du Jalon T5 (Livrable L4)", 1)
p_ech = doc.add_paragraph()
p_ech.paragraph_format.space_before = Pt(2)
p_ech.paragraph_format.space_after = Pt(6)
p_ech.paragraph_format.line_spacing = 1.15
r_ech = p_ech.add_run(
    "À l'issue de cette réunion de lancement, l'équipe entame immédiatement la phase de planification opérationnelle détaillée "
    "(Livrable L4 — METIER_PLAN_AgentMarketing.docx, 5 à 6 pages avant le Jalon T5). Les livrables prioritaires de cette phase comprennent : "
    "le réseau PERT calculant le chemin critique, le diagramme de Gantt avec affectation précise des ressources, l'évaluation chiffrée "
    "des charges en jours-hommes (JH), et la formalisation du plan de recette d'intégration continue."
)
r_ech.font.name = "Arial"
r_ech.font.size = Pt(8.5)
r_ech.font.color.rgb = TEXT_COLOR

add_heading("6. Signatures et Approbation des Membres de l'Équipe VisionX", 1)
p_sig_note = doc.add_paragraph()
p_sig_note.paragraph_format.space_before = Pt(1)
p_sig_note.paragraph_format.space_after = Pt(4)
r_sn = p_sig_note.add_run("Fait à Amizour (ESTIN), le 07 Novembre 2026. Par leurs signatures ci-dessous, les membres s'engagent solidairement :")
r_sn.font.name = "Arial"
r_sn.font.size = Pt(8.5)
r_sn.font.italic = True
r_sn.font.color.rgb = TEXT_COLOR

tbl_sig = doc.add_table(rows=4, cols=2)
tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_sig.autofit = False
sig_widths = [Inches(3.43), Inches(3.44)]

signers = [
    ("Mohamed Anes Bouharizi\nChef de Projet & Lead Tech\n[Signature validée / Lu et approuvé]", 
     "Sebti Iyed\nArchitecte Intégration Noyau\n[Signature validée / Lu et approuvé]"),
    ("Zouane Akram\nLead Scoring & Qualification\n[Signature validée / Lu et approuvé]", 
     "Fellah Baha\nLead Emailing & Templates\n[Signature validée / Lu et approuvé]"),
    ("Bertil Anis\nResp. Sécurité, Données & Purge\n[Signature validée / Lu et approuvé]", 
     "Bahi Adem\nLead QA, Conformité & Recette\n[Signature validée / Lu et approuvé]")
]

for r_idx, (sig_l, sig_r) in enumerate(signers):
    for c_idx, sig_text in enumerate([sig_l, sig_r]):
        cell = tbl_sig.cell(r_idx, c_idx)
        cell.width = sig_widths[c_idx]
        set_cell_background(cell, "F8FAFC")
        set_cell_borders(cell, top="CBD5E1", bottom="CBD5E1", left="CBD5E1", right="CBD5E1")
        set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        
        lines = sig_text.split("\n")
        r_name = p.add_run(lines[0] + "\n")
        r_name.font.name = "Arial"
        r_name.font.size = Pt(8.5)
        r_name.font.bold = True
        r_name.font.color.rgb = PRIMARY_COLOR
        
        r_role = p.add_run(lines[1] + "\n")
        r_role.font.name = "Arial"
        r_role.font.size = Pt(8)
        r_role.font.color.rgb = SECONDARY_COLOR
        
        r_mention = p.add_run(lines[2])
        r_mention.font.name = "Arial"
        r_mention.font.size = Pt(7.5)
        r_mention.font.italic = True
        r_mention.font.color.rgb = RGBColor(100, 150, 100)

doc.save("/home/anes/Documents/VisionX/METIER_PVLancement_AgentMarketing.docx")
print("METIER_PVLancement_AgentMarketing.docx généré avec succès !")
