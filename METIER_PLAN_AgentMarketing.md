# Livrable L4 — Plan de Projet & Planification Opérationnelle
**Module « Conduite de Projet » — 2ème Année CS (ESTIN 2026–2027)**  
**Équipe VisionX — Filière Métier : Agent Marketing Automation (`agent-marketing-automation-visionx`)**  
**Échéance : Avant Jalon T5 | Volume officiel : 6 pages calibrées**

---

## 1. Présentation de la Planification, Hypothèses et Ressources

### 1.1. Introduction et Objectifs
Faisant suite à la validation de la Charte de Projet (L2) et du Procès-Verbal de Lancement (L3), ce document opérationnalise la démarche de conduite de projet. Il traduit les exigences techniques et contractuelles du sujet ESTIN en un ordonnancement temporel maîtrisé sur **20 jours ouvrés** et **36 Jours-Hommes (JH)**.

### 1.2. Hypothèses Structurantes
- **Base calendaire :** 20 jours ouvrés (J1 à J20).
- **Ressources :** 6 élèves-ingénieurs mobilisés en parallèle (Mohamed Anes Bouharizi, Sebti Iyed, Zouane Akram, Fellah Baha, Bertil Anis, Bahi Adem).
- **Découplage strict (Règle 4) :** Aucun travail n'est subordonné au code d'une autre équipe. Les échanges avec l'Agent Commercial (consommateur de `prospect`) et l'Agent Facturation (producteur de `commande`) s'opèrent exclusivement via le bus d'événements du noyau central et sont simulés localement avec un simulateur autonome (`simulateur_marche_marketing.py`).

### 1.3. Matrice OBS / RACI Consolidée

| Lot de travail (WBS) | M. Anes (CP) | S. Iyed (Arch) | Z. Akram (Lead) | F. Baha (Dev) | B. Anis (Dev) | B. Adem (QA) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **WP1 : Cadrage & Spécifications** | **A / R** | R | R | C | C | I |
| **WP2 : Socle Backend & Multi-tenant** | C | **A / R** | I | R | C | R |
| **WP3 : Moteur Métier (Prospect & Scoring)** | I | C | C | R | **A / R** | I |
| **WP4 : Moteur Événementiel (Commandes & Email)** | I | R | **A / R** | I | R | R |
| **WP5 : Intégration Noyau & Bus d'Échange** | C | **A / R** | R | I | C | I |
| **WP6 : Assurance Qualité, Tests & Déploiement** | A | C | I | I | C | **A / R** |

*Légende RACI : A = Accountable (Responsable unique) | R = Responsible (Réalisateur) | C = Consulted (Consulté) | I = Informed (Informé)*

---

## 2. Décomposition des Tâches, Durées et Dépendances

| ID | Intitulé de l'activité | Responsable(s) | Durée | Charge | Préd. | Livrable technique vérifiable |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **A** | Cadrage et validation des contrats | Anes | 1 j | 1 JH | — | Documents L1 & L2 validés |
| **B** | Spécifications fonctionnelles & tech | Anes, Iyed, Akram | 2 j | 3 JH | A | Dossier d'API & schémas Pydantic |
| **C** | Conception architecture backend | Anes, Iyed | 2 j | 2 JH | B | Architecture modulaire & routes |
| **D** | Modélisation base de données | Baha | 2 j | 2 JH | B | DDL SQLite (WAL) & PostgreSQL |
| **E** | Développement socle FastAPI | Iyed | 3 j | 3 JH | C | 5 routes obligatoires & enveloppe |
| **F** | Isolation multi-tenant & persistance | Baha, Adem | 2 j | 3 JH | D, E | Middleware tenant & script de purge |
| **G** | Gestion prospects & Lead Scoring | Anis, Baha | 2 j | 3 JH | F | Module de qualification (score >= 70) |
| **H** | Réception & traitement commandes | Akram, Iyed | 2 j | 2 JH | F | Route `/exchange/notify` (commandes) |
| **I** | Moteur email Jinja2/SMTP modulaire | Anis, Adem | 2 j | 2 JH | C | Templates HTML & service SMTP |
| **J** | Automatisations & campagnes marketing | Anis | 2 j | 2 JH | G, H, I | Scénarios onboarding & win-back |
| **K** | Intégration complète avec le noyau | Iyed, Akram | 3 j | 3 JH | G, H | Publication bus prospect & handshake |
| **M** | Conteneurisation Docker autonome | Adem | 1 j | 1 JH | E | Dockerfile optimisé & compose |
| **L** | Tests fonctionnels, intégration & sécu | Toute l'équipe | 3 j | 6 JH | J, K, M | Suite de 15 tests pytest à 100% |
| **N** | Documentation & préparation démo | Anes, toute équipe | 2 j | 3 JH | L | README d'exploitation & support démo |

### 2.1. Analyse des Dépendances Fonctionnelles Inter-Agents
- **Publication `prospect` :** Déclenchée par l'activité G dès que `score >= 70` vers `POST {NOYAU_URL}/exchange/agent/prospect`. Consommée par l'Agent Commercial.
- **Consommation `commande` :** Reçue par l'activité H sur `POST /exchange/notify` émise par l'Agent Facturation/Vente. Déclenche la tâche J (campagnes email réactives).
- **Résilience :** Grâce au simulateur autonome d'échanges, VisionX peut exécuter et valider 100 % de son périmètre même en l'absence des autres équipes.

---

## 3. Réseau PERT et Chemin Critique

### 3.1. Tableau Analytique CPM / PERT

| ID | Activité | Durée | ES (Début Tôt) | EF (Fin Tôt) | LS (Début Tard) | LF (Fin Tard) | Marge Totale | Statut & Criticité |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **A** | Cadrage & contrats | 1 j | 0 | 1 | 0 | 1 | **0 j** | **CRITIQUE (Chemin principal)** |
| **B** | Spécifications fonctionnelles | 2 j | 1 | 3 | 1 | 3 | **0 j** | **CRITIQUE (Chemin principal)** |
| **C** | Conception architecture | 2 j | 3 | 5 | 3 | 5 | **0 j** | **CRITIQUE (Chemin principal)** |
| **D** | Modélisation base de données | 2 j | 3 | 5 | 6 | 8 | **3 j** | Non critique (Marge libre = 3 j) |
| **E** | Socle FastAPI | 3 j | 5 | 8 | 5 | 8 | **0 j** | **CRITIQUE (Chemin principal)** |
| **F** | Multi-tenant & persistance | 2 j | 8 | 10 | 8 | 10 | **0 j** | **CRITIQUE (Chemin principal)** |
| **G** | Prospects & Lead Scoring | 2 j | 10 | 12 | 10 | 12 | **0 j** | **CRITIQUE (Branche jumelle 1)** |
| **H** | Traitement des commandes | 2 j | 10 | 12 | 10 | 12 | **0 j** | **CRITIQUE (Branche jumelle 2)** |
| **I** | Moteur email Jinja2/SMTP | 2 j | 5 | 7 | 11 | 13 | **6 j** | Non critique (Marge libre = 5 j) |
| **J** | Campagnes marketing | 2 j | 12 | 14 | 13 | 15 | **1 j** | Non critique (Marge libre = 1 j) |
| **K** | Intégration noyau & bus | 3 j | 12 | 15 | 12 | 15 | **0 j** | **CRITIQUE (Convergence bus)** |
| **M** | Conteneurisation Docker | 1 j | 8 | 9 | 14 | 15 | **6 j** | Non critique (Marge libre = 6 j) |
| **L** | Tests fonctionnels & sécurité | 3 j | 15 | 18 | 15 | 18 | **0 j** | **CRITIQUE (Recette globale)** |
| **N** | Documentation & démo | 2 j | 18 | 20 | 18 | 20 | **0 j** | **CRITIQUE (Clôture projet)** |

### 3.2. Analyse du Chemin Critique
- **Double Chemin Critique (20 jours ouvrés) :**
  $$\text{Chemin 1} : A(1) \to B(2) \to C(2) \to E(3) \to F(2) \to G(2) \to K(3) \to L(3) \to N(2) = 20\text{ jours}$$
  $$\text{Chemin 2} : A(1) \to B(2) \to C(2) \to E(3) \to F(2) \to H(2) \to K(3) \to L(3) \to N(2) = 20\text{ jours}$$
- **Tolérance zéro retard :** Toute dérive d'une journée sur l'une de ces 10 tâches décale directement la date de livraison finale.
- **Tâches à marge :** Tâche D (+3j), Tâche I (+6j), Tâche M (+6j), Tâche J (+1j).

---

## 4. Diagramme de Gantt Prévisionnel (J1 à J20)

```
Activité             Pilote  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20
---------------------------------------------------------------------------------------
A : Cadrage contrats Anes   [■] .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
B : Spécifications   Anes    . [■  ■] .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
C : Architecture     Iyed    .  .  . [■  ■] .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
D : Modèle BDD       Baha    .  .  . [░  ░] .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
E : Socle FastAPI    Iyed    .  .  .  .  . [■  ■  ■] .  .  .  .  .  .  .  .  .  .  .  .
I : Email SMTP       Anis    .  .  .  .  . [░  ░] .  .  .  .  .  .  .  .  .  .  .  .  .
F : Multi-tenant     Baha    .  .  .  .  .  .  .  . [■  ■] .  .  .  .  .  .  .  .  .  .
M : Dockerisation    Adem    .  .  .  .  .  .  .  . [░] .  .  .  .  .  .  .  .  .  .  .
G : Prospects & ScoreAnis    .  .  .  .  .  .  .  .  .  . [■  ■] .  .  .  .  .  .  .  .
H : Commandes        Akram   .  .  .  .  .  .  .  .  .  . [■  ■] .  .  .  .  .  .  .  .
J : Campagnes        Anis    .  .  .  .  .  .  .  .  .  .  .  . [░  ░] .  .  .  .  .  .
K : Intégration noyauIyed    .  .  .  .  .  .  .  .  .  .  .  . [■  ■  ■] .  .  .  .  .
L : Tests & Recette  Adem    .  .  .  .  .  .  .  .  .  .  .  .  .  .  . [■  ■  ■] .  .
N : Doc & Démo       Anes    .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . [■  ■]
---------------------------------------------------------------------------------------
[■] = Tâche critique (MT = 0) | [░] = Tâche parallèle avec marge
Jalons : J1 (Fin J5) -> J2 (Fin J10) -> J3 (Fin J14) -> J4 (Fin J15) -> J5 (Fin J18) -> J6 (Fin J20)
```

---

## 5. Estimation des Charges en Jours-Hommes et Budget

### 5.1. Ventilation de la Charge de Travail (36 JH)

| Membre de l'équipe | Périmètre d'action principal | Charge cible | Part d'effort |
| :--- | :--- | :---: | :---: |
| **Mohamed Anes Bouharizi** | Coordination globale, A, B, C, doc N | 6 JH | 16.7 % |
| **Sebti Iyed** | B, socle FastAPI E, intégration noyau K | 7 JH | 19.4 % |
| **Zouane Akram** | B, gestion commandes H, intégration noyau K | 5 JH | 13.9 % |
| **Fellah Baha** | Modèle BDD D, isolation multi-tenant F, tests L | 6 JH | 16.7 % |
| **Bertil Anis** | Lead scoring G, service email I, campagnes J | 6 JH | 16.7 % |
| **Bahi Adem** | Multi-tenant F, Docker M, banc de tests L | 6 JH | 16.7 % |
| **TOTAL CONSOLIDÉ** | **Ensemble des 14 activités du projet** | **36 JH** | **100.0 %** |

### 5.2. Budget Prévisionnel Consolidé

| Catégorie budgétaire | Description des ressources | Base de valorisation | Montant valorisé |
| :--- | :--- | :--- | :---: |
| **Logiciels & Frameworks** | Python, FastAPI, SQLite, Pydantic, Jinja2, MailHog | Licences FOSS / Open Source | 0 DA |
| **Infrastructure & Serveurs** | Docker Engine, environnements locaux, git privé | Postes de travail & ESTIN | 0 DA |
| **Main-d'œuvre intellectuelle** | Prestation des 6 élèves-ingénieurs VisionX | 36 JH × 4 000 DA/JH | 144 000 DA |
| **Réserve pour imprévus (10%)** | Marge de sécurité technique & recette | 10 % de la main-d'œuvre | 14 400 DA |
| **COÛT TOTAL DU PROJET** | **Budget valorisé (Débours effectif décaissé = 0 DA)** | — | **158 400 DA** |

---

## 6. Jalons de Contrôle, Gouvernance et Validation

### 6.1. Matrice des Jalons de Contrôle

| Jalon | Intitulé | Date cible | Critère d'acceptation | Livrable officiel |
| :---: | :--- | :---: | :--- | :--- |
| **J1** | Conception & Architecture | Fin J5 | DDL validé, routes et schémas figés | Livrable L2 (Charte) |
| **J2** | Socle API & Multi-tenant | Fin J10 | 5 endpoints opérationnels, purge testée | Socle testé local |
| **J3** | Métier & Campagnes | Fin J14 | Scoring >= 70 et handler commandes prêts | Modules G, H, J prêts |
| **J4** | Intégration Noyau & Bus | Fin J15 | Publication/réception fluides via `/exchange/...` | Livrable L3 (PV Lancement) |
| **J5** | Recette & Conformité | Fin J18 | 15/15 tests validés avec 100 % de succès | Livrable L4 (Planification) |
| **J6** | Déploiement & Clôture | Fin J20 | Image Docker livrée sur GitHub, démo prête | Livrables L5, L6, L7, L8 |

### 6.2. Tableau de Bord KPI
- **SPI (Schedule Performance Index) = EV / PV :** Maintenu $\ge 1.0$.
- **Taux de Succès des Tests :** Maintenu à **100 %** (15/15 tests validés, 0 régression).
- **Consommation des Jours-Hommes :** Suivi régulier de l'effort réel vs les 36 JH prévus.
- **Étanchéité Multi-tenant :** 0 fuite inter-tenant et vérification de la purge immédiate.

---
