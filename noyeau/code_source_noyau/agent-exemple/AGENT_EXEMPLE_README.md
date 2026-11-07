
### Agent exemple


### Gabarit de depart pour votre propre agent

Ce dossier n'est pas un agent utile en lui-meme : c'est un squelette minimal mais complet, qui respecte deja AGENT_INTEGRATION_CONTRACT.docx. Copiez-le et remplacez la logique de demonstration par le comportement reel de votre agent.


### Contenu du dossier

main.py — les 5 endpoints obligatoires, plus un exemple d'envoi d'alerte et de reception d'un objet du bus d'echange.

agent.manifest.json — le manifeste a adapter (slug, nom, filiere, equipe...).

Dockerfile — pret a l'emploi pour une stack Python ; a reecrire si vous changez de langage.

requirements.txt — dependances minimales.


### Lancer l'agent exemple en local

pip install -r requirements.txt
uvicorn main:app --port 9000

Variable d'environnement NOYAU_URL : adresse du noyau, utilisee pour l'envoi des alertes (par defaut http://localhost:8000).


### Tester manuellement le scenario de demonstration

Une fois votre entreprise de test inscrite et l'agent exemple souscrit depuis /catalogue, simulez l'arrivee d'une mesure :

curl -X POST "http://localhost:9000/demo/mesure/<tenant_id>?valeur=95"

Si la valeur depasse le seuil configure (80 par defaut), une alerte est automatiquement envoyee au noyau et apparait dans le tableau de bord de l'entreprise (/mon-compte).


### Ce qu'il faut remplacer pour en faire votre agent

La section "LOGIQUE DE DEMONSTRATION" de main.py, par votre propre traitement.

Le contenu de agent.manifest.json.

Les dependances de requirements.txt selon ce dont votre agent a reellement besoin.

Les champs produces/consumes si votre agent echange des objets avec un autre (voir INTER_AGENT_DATA_CONTRACT.docx).
