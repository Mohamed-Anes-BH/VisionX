import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CCCCCC'

# 1. GANTT CHART (Panoramic: 12 x 4.0)
fig, ax = plt.subplots(figsize=(12, 4.2), dpi=250)

tasks = [
    ("N — Documentation & Démo", 19, 2, True),
    ("L — Tests & Recette", 16, 3, True),
    ("K — Intégration Noyau", 13, 3, True),
    ("J — Campagnes & Auto.", 13, 2, False),
    ("H — Réception Commandes", 11, 2, True),
    ("G — Prospects & Scoring", 11, 2, True),
    ("M — Packaging Docker", 9, 1, False),
    ("F — Multi-tenant & Purge", 9, 2, True),
    ("I — Moteur Email SMTP", 6, 2, False),
    ("E — Socle FastAPI", 6, 3, True),
    ("D — Modèle BDD", 4, 2, False),
    ("C — Architecture API", 4, 2, True),
    ("B — Spécifications", 2, 2, True),
    ("A — Cadrage & Contrats", 1, 1, True),
]

y_pos = np.arange(len(tasks))
ax.set_facecolor('#F8FAFC')
ax.grid(axis='x', color='#E2E8F0', linestyle='--', linewidth=0.8, zorder=0)

for i, (name, start, duration, is_crit) in enumerate(tasks):
    color = '#1B365D' if is_crit else '#3B82F6'
    edge = '#0F172A' if is_crit else '#1D4ED8'
    bar = ax.barh(i, duration, left=start, height=0.68, align='center',
                  color=color, edgecolor=edge, linewidth=0.8, zorder=3, alpha=0.92)
    ax.text(start + duration / 2, i, f"{duration}j", 
            ha='center', va='center', color='white', fontweight='bold', fontsize=7.8, zorder=4)

ax.set_yticks(y_pos)
ax.set_yticklabels([t[0] for t in tasks], fontsize=8, fontweight='bold', color='#1E293B')
ax.set_xlabel("Jours ouvrés du projet (J1 à J20)", fontsize=8.5, fontweight='bold', color='#1E293B', labelpad=4)
ax.set_xlim(0.5, 21.5)
ax.set_xticks(range(1, 21))
ax.set_xticklabels([f"J{i}" for i in range(1, 21)], fontsize=7.5)

legend_elements = [
    patches.Patch(facecolor='#1B365D', edgecolor='#0F172A', label='Chemin Critique (MT = 0)'),
    patches.Patch(facecolor='#3B82F6', edgecolor='#1D4ED8', label='Tâches Parallèles (MT > 0)')
]
ax.legend(handles=legend_elements, loc='lower right', framealpha=0.95, facecolor='white', edgecolor='#CBD5E1', fontsize=8)

plt.tight_layout(pad=0.5)
plt.savefig('/home/anes/Documents/VisionX/gantt_chart_visionx.png', dpi=250)
plt.close()
print("Panoramic Gantt chart généré !")

# 2. PERT NETWORK (Panoramic: 13 x 4.0)
fig, ax = plt.subplots(figsize=(13, 3.8), dpi=250)
ax.set_facecolor('#FFFFFF')
ax.set_xlim(0, 22.5)
ax.set_ylim(1.5, 10.5)
ax.axis('off')

nodes = {
    'A': (1.5, 6.0, 'A\nCadrage\n1j', True),
    'B': (3.8, 6.0, 'B\nSpécifs\n2j', True),
    'C': (6.5, 7.6, 'C\nArchit.\n2j', True),
    'D': (6.5, 4.2, 'D\nBDD\n2j', False),
    'E': (9.2, 7.6, 'E\nFastAPI\n3j', True),
    'I': (9.2, 9.6, 'I\nEmail\n2j', False),
    'F': (11.8, 6.0, 'F\nMulti-ten.\n2j', True),
    'M': (11.8, 9.2, 'M\nDocker\n1j', False),
    'G': (14.5, 7.4, 'G\nProsp.\n2j', True),
    'H': (14.5, 4.4, 'H\nCmds\n2j', True),
    'J': (17.2, 9.0, 'J\nCamp.\n2j', False),
    'K': (17.2, 6.0, 'K\nNoyau\n3j', True),
    'L': (19.6, 6.0, 'L\nTests\n3j', True),
    'N': (21.5, 6.0, 'N\nDémo\n2j', True),
}

edges = [
    ('A', 'B', True),
    ('B', 'C', True),
    ('B', 'D', False),
    ('C', 'E', True),
    ('C', 'I', False),
    ('D', 'F', False),
    ('E', 'F', True),
    ('E', 'M', False),
    ('F', 'G', True),
    ('F', 'H', True),
    ('G', 'K', True),
    ('H', 'K', True),
    ('G', 'J', False),
    ('H', 'J', False),
    ('I', 'J', False),
    ('J', 'L', False),
    ('K', 'L', True),
    ('M', 'L', False),
    ('L', 'N', True),
]

for src, dst, is_crit in edges:
    x1, y1, _, _ = nodes[src]
    x2, y2, _, _ = nodes[dst]
    color = '#DC2626' if is_crit else '#94A3B8'
    lw = 2.0 if is_crit else 1.1
    ls = '-' if is_crit else '--'
    
    dx, dy = x2 - x1, y2 - y1
    dist = np.hypot(dx, dy)
    ox, oy = (dx / dist) * 0.75, (dy / dist) * 0.45
    ax.annotate("", xy=(x2 - ox, y2 - oy), xytext=(x1 + ox, y1 + oy),
                arrowprops=dict(arrowstyle="->", color=color, lw=lw, ls=ls,
                                shrinkA=2, shrinkB=2, mutation_scale=10))

for k, (x, y, text, is_crit) in nodes.items():
    fc = '#1B365D' if is_crit else '#F1F5F9'
    tc = '#FFFFFF' if is_crit else '#0F172A'
    ec = '#DC2626' if is_crit else '#64748B'
    lw = 1.8 if is_crit else 1.0
    
    box = patches.FancyBboxPatch((x - 0.65, y - 0.42), 1.3, 0.84,
                                 boxstyle="round,pad=0.06",
                                 facecolor=fc, edgecolor=ec, linewidth=lw, zorder=5)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', color=tc, fontsize=6.8, fontweight='bold', zorder=6)

legend_elements = [
    patches.Patch(facecolor='#1B365D', edgecolor='#DC2626', linewidth=1.5, label='Chemins Critiques A-B-C-E-F-(G/H)-K-L-N (20j, MT=0)'),
    patches.Patch(facecolor='#F1F5F9', edgecolor='#64748B', linewidth=1, label='Activités Flottantes / Chemins Secondaires')
]
ax.legend(handles=legend_elements, loc='lower left', framealpha=0.95, facecolor='white', edgecolor='#CBD5E1', fontsize=7.5)

plt.tight_layout(pad=0.4)
plt.savefig('/home/anes/Documents/VisionX/pert_network_visionx.png', dpi=250)
plt.close()
print("Panoramic PERT network diagram généré !")
