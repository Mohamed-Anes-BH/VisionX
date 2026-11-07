tasks = {
    'A': {'name': 'Cadrage et contrats', 'dur': 1, 'preds': []},
    'B': {'name': 'Spécifications fonctionnelles & tech', 'dur': 2, 'preds': ['A']},
    'C': {'name': "Conception de l'architecture", 'dur': 2, 'preds': ['B']},
    'D': {'name': 'Modélisation base de données', 'dur': 2, 'preds': ['B']},
    'E': {'name': 'Développement socle FastAPI', 'dur': 3, 'preds': ['C']},
    'F': {'name': 'Isolation multi-tenant & persistance', 'dur': 2, 'preds': ['D', 'E']},
    'G': {'name': 'Gestion prospects & Lead Scoring', 'dur': 2, 'preds': ['F']},
    'H': {'name': 'Réception & traitement commandes', 'dur': 2, 'preds': ['F']},
    'I': {'name': 'Moteur email Jinja2/SMTP', 'dur': 2, 'preds': ['C']},
    'J': {'name': 'Automatisations & campagnes marketing', 'dur': 2, 'preds': ['G', 'H', 'I']},
    'K': {'name': 'Intégration avec le noyau', 'dur': 3, 'preds': ['G', 'H']},
    'M': {'name': 'Conteneurisation Docker', 'dur': 1, 'preds': ['E']},
    'L': {'name': 'Tests fonctionnels, intégration & sécu', 'dur': 3, 'preds': ['J', 'K', 'M']},
    'N': {'name': 'Documentation & préparation démo', 'dur': 2, 'preds': ['L']},
}

# Forward pass (Earliest times)
# Start project at Day 0 (or Day 1)
# Let's use 0-indexed for calculation, so Day 1 means [0, 1]
es = {}
ef = {}

for t in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M', 'L', 'N']:
    preds = tasks[t]['preds']
    if not preds:
        es[t] = 0
    else:
        es[t] = max(ef[p] for p in preds)
    ef[t] = es[t] + tasks[t]['dur']

project_duration = ef['N']
print(f"Project Duration: {project_duration} days")

# Backward pass (Latest times)
lf = {}
ls = {}

for t in reversed(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M', 'L', 'N']):
    # Find successors
    succs = [s for s, data in tasks.items() if t in data['preds']]
    if not succs:
        lf[t] = project_duration
    else:
        lf[t] = min(ls[s] for s in succs)
    ls[t] = lf[t] - tasks[t]['dur']

# Slack
total_slack = {}
free_slack = {}
for t in tasks:
    total_slack[t] = ls[t] - es[t]
    succs = [s for s, data in tasks.items() if t in data['preds']]
    if not succs:
        free_slack[t] = project_duration - ef[t]
    else:
        free_slack[t] = min(es[s] for s in succs) - ef[t]

print(f"{'Tâche':<5} | {'Durée':<5} | {'ES':<4} | {'EF':<4} | {'LS':<4} | {'LF':<4} | {'Marge Totale':<12} | {'Marge Libre':<11} | {'Critique?'}")
print("-" * 80)
for t in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M', 'L', 'N']:
    crit = "OUI (CRITIQUE)" if total_slack[t] == 0 else "Non"
    # Show 1-indexed days: ES+1 to EF
    print(f"{t:<5} | {tasks[t]['dur']:<5} | {es[t]:<4} | {ef[t]:<4} | {ls[t]:<4} | {lf[t]:<4} | {total_slack[t]:<12} | {free_slack[t]:<11} | {crit}")

