
### Noyau de la plateforme


### Presentation generale et prise en main


### Objet de ce document

Ce document decrit le noyau commun aux trois filieres du mini-projet (cybersecurite, automatisation metier, IoT). Le noyau est fourni par l'enseignant et ne doit pas etre modifie par les equipes etudiantes : il contient tout ce qui est necessaire pour faire fonctionner la plateforme, a l'exception des agents eux-memes, qui sont le livrable de chaque equipe.


### Ce que contient le noyau

L'inscription et l'authentification des entreprises clientes (multi-tenant).

Un catalogue d'agents, avec soumission, verification et publication par l'administrateur.

La souscription d'une entreprise a un ou plusieurs agents, avec activation reelle aupres de l'agent.

Une passerelle d'integration (agent gateway) qui controle que chaque agent respecte le contrat.

Un bus d'echange de donnees inter-agents, utilisable par les agents qui en ont besoin.

Trois interfaces web : inscription/catalogue pour les entreprises, tableau de bord entreprise, et back-office pour l'administrateur (l'enseignant).

Un agent exemple, a utiliser comme point de depart pour developper votre propre agent.


### Ce que le noyau NE contient PAS

Le noyau ne contient aucune logique metier d'agent. C'est volontaire : chaque equipe developpe son agent comme un service independant, qui ne communique avec le noyau qu'a travers les regles decrites dans AGENT_INTEGRATION_CONTRACT.docx.


### Installation

pip install -r requirements.txt
export DATABASE_URL="postgresql+psycopg2://saas_user:saas_pass@localhost:5432/plateforme_agents"
export JWT_SECRET_KEY="une-cle-longue-et-aleatoire"
uvicorn app.main:app --reload --port 8000

Au premier lancement, creez le compte administrateur (l'enseignant) avec le script fourni :


### python scripts/create_admin.py

La documentation interactive de l'API est accessible sur http://localhost:8000/docs. Les pages web sont accessibles sur http://localhost:8000/ (accueil), /inscription, /connexion, /catalogue, /mon-compte et /admin.


### Organisation du code

app/
  main.py              point d'entree de l'application
  database.py          connexion a la base de donnees
  models.py            tables (Company, User, Agent, AgentSubscription, ...)
  core/
    security.py        authentification (JWT, cookies, mots de passe)
    agent_gateway.py    appels sortants du noyau vers un agent
    exchange_bus.py     bus d'echange de donnees inter-agents
  routers/
    auth.py, companies.py, agents.py, subscriptions.py, admin.py,
    webhooks.py, exchange.py      routes API (JSON)
    pages.py                      pages web (HTML)
  templates/            pages HTML (Jinja2)
  static/               feuille de style
scripts/
  create_admin.py       creation du compte administrateur
agent-exemple/
  main.py, agent.manifest.json, Dockerfile, requirements.txt


### Le parcours d'un agent, de la soumission a la publication

1. L'equipe developpe son agent en suivant AGENT_INTEGRATION_CONTRACT.docx et DEVELOPER_INSTRUCTIONS.docx.

2. Elle le soumet avec POST /agents/submit (voir DEVELOPER_INSTRUCTIONS.docx). L'agent entre en statut "soumis".

3. L'administrateur verifie sa conformite depuis la page /admin, puis le certifie et le publie.

4. L'agent apparait dans le catalogue (/catalogue) et peut etre souscrit par une entreprise.

5. A la souscription, le noyau appelle automatiquement l'agent pour l'activer. Si l'agent ne repond pas correctement (voir l'enveloppe de reponse standard du contrat), la souscription reste en erreur plutot que de planter la plateforme.


### Documents associes

AGENT_INTEGRATION_CONTRACT.docx — le contrat technique que chaque agent doit respecter.

INTER_AGENT_DATA_CONTRACT.docx — le registre des objets partages pour les agents qui collaborent entre eux.

DEVELOPER_INSTRUCTIONS.docx — le guide pas-a-pas pour developper et soumettre un agent.

GUIDE_GITHUB_NOYAU.docx — comment publier ce noyau sur GitHub et organiser les depots des equipes.
