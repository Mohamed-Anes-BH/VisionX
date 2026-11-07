RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE
MINISTÈRE DE L'ENSEIGNEMENT SUPÉRIEUR ET DE LA RECHERCHE SCIENTIFIQUE
ÉCOLE SUPÉRIEURE EN SCIENCES ET TECHNOLOGIES DE L'INFORMATIQUE ET DU NUMÉRIQUE (ESTIN)
Mini-projet « Conduite de Projet » — 2ème Année CS (2026–2027)


### LIVRABLE L1 : DOCUMENT D'ORIENTATION (DO)

Agent d'Automatisation Métier — Marketing Automation (VisionX)


### 1. Agent Choisi et Périmètre Fonctionnel

Dans le cadre du mini-projet de Conduite de Projet, l'équipe VisionX conçoit et développe l'agent Marketing Automation (filière Automatisation Métier, section 2.2 du cahier des charges). Cet agent autonome a pour mission d'optimiser et d'automatiser les actions marketing des entreprises clientes (multi-tenant) : qualification et scoring de prospects, génération de campagnes de communication ciblées (emailing/notifications), et fidélisation post-achat.


### 2. Objectifs et Justification du Choix

• Objectif opérationnel : Fournir un service autonome sous Docker capable de : (1) qualifier des leads et publier l'objet métier prospect sur le bus d'échange du noyau ; (2) consommer via notification l'objet métier commande pour déclencher des scénarios d'onboarding, de relance ou de fidélisation ; (3) respecter strictement l'API et l'isolation des données par tenant.
• Justification : Le marketing est le point de départ de l'entonnoir de vente (générateur de prospects pour l'agent Commercial) et le point d'atterrissage final après commande. Il offre une forte valeur ajoutée en ingénierie multi-agents car il sollicite à la fois la publication et la consommation d'objets métier via le bus commun.


### 3. Méthodologie de Conduite de Projet

L'équipe adopte une démarche Agile / Scrum adaptée rythmée par les 8 jalons contractuels (T1 à T8) : sprints courts de 1 à 2 semaines, réunions hebdomadaires formalisées par des comptes-rendus, et suivi rigoureux sur le dépôt privé GitHub attribué par l'enseignant. Le code source est structuré en couches étanches (API/Contrat, Logique Métier, Données) conformément aux règles de cloisonnement inter-équipes imposées.


### 4. Plan Prévisionnel et Jalons des Livrables


### 5. Sources Contractuelles et Choix Techniques

• Documents contractuels : Conformité stricte à AGENT_INTEGRATION_CONTRACT.docx v1.0 (5 routes obligatoires /health, /tenant/activate, /tenant/deactivate, /tenant/{id}/status, /config-schema + enveloppe standard {status, data, error}) et à INTER_AGENT_DATA_CONTRACT.docx.
• Objets partagés déclarés : PRODUIT = prospect (external_id, nom, email, score_interet, statut) | CONSOMME = commande (numero_commande, date, client, lignes, montant, statut).
• Stack technique retenue : Langage Python (imposé par le guide), framework FastAPI (haute performance, validation automatique Pydantic, aligné sur l'agent-exemple fourni), base de données SQLite/PostgreSQL avec isolation par tenant_id, templates email Jinja2, conteneurisation Docker.


### 6. Risques Identifiés et Mesures Préventives

1. Risque de dépendance inter-agents (Modéré) : Si l'agent Commercial n'est pas déployé ou actif, l'agent Marketing ne recevrait pas de commandes réelles. Parade : Exploiter le principe à double lecture du noyau : injection de commandes manuelles via le tableau de bord noyau ou un mock local de test.
2. Risque de non-conformité contractuelle (Critique) : Non-respect du format de réponse {status, data, error} entraînant la suspension par le noyau. Parade : Création d'un middleware FastAPI imposant systématiquement l'enveloppe standard et tests automatisés pré-soumission.
3. Risque d'étanchéité multi-tenant (Élevé) : Mélange accidentel de données entre deux entreprises clientes. Parade : Filtrage obligatoire par X-Tenant-Id sur toutes les requêtes en base de données et tests de purge lors de /tenant/deactivate.
