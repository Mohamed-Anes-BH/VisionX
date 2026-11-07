# 🚀 Équipe VisionX — Tâche 1 (Version Finale Stabilisée V1.1)
**Mini-Projet « Conduite de Projet » — 2ème Année CS (ESTIN 2026–2027)**  
**Filière :** Automatisation Métier (Section 2.2)  
**Agent Choisi :** **Marketing Automation** (`agent-marketing-automation-visionx`)  
**Équipe :** VisionX (Bouharizi Mohamed Anes - Chef d'équipe, Sebti Iyed, Zouane Akram, Fellah Baha, Bertil Anis, Bahi Adem)  

---

## 🎯 1. Clôture Formelle des 5 Corrections de la Tâche 1

### Correction 1 — Règles Contractuelles vs Choix d'Équipe VisionX
Afin de ne baser la Charte L2 sur aucune ambiguïté, voici la distinction stricte entre les exigences imposées par l'enseignant et les choix fonctionnels propres à VisionX :

| Composant | Règle Contractuelle (Imposée par l'enseignant) | Choix d'Équipe VisionX |
|---|---|---|
| **Schéma de `prospect`** | Format strict `INTER_AGENT_DATA_CONTRACT` : `id_prospect`, `nom`, `email`, `score_interet`, `statut`. | Calcul dynamique du `score_interet` (0-100) par un algorithme pondéré d'engagement. |
| **Seuil de Qualification** | Non fixé par le noyau (libre à l'agent). | Fixé à **70 points** par défaut, configurable par chaque entreprise via `/config-schema`. |
| **Schéma de `commande`** | Format strict `INTER_AGENT_DATA_CONTRACT` : `numero_commande`, `date_commande`, `client`, `lignes`, `montant_total_ht`, `statut`. | Traitement marketing différencié : onboarding si statut `confirmee`, relance win-back si `annulee`. |
| **Format des Réponses** | Enveloppe unique imposée : `{"status": "ok"\|"error", "data": ..., "error": ...}`. | Implémentée via un middleware FastAPI pour garantir zéro violation de contrat. |
| **Authentification** | Transmission obligatoire par le noyau de `X-Tenant-Id` et `Authorization: Bearer <key>`. | Vérification stricte et rejet immédiat (HTTP 400) si l'en-tête `X-Tenant-Id` est manquant. |

---

### Correction 2 — Cartographie Complète et Tripartite des Endpoints

Pour une clarté totale, les endpoints ne sont plus confondus mais séparés en 4 catégories distinctes :

#### 1. Endpoints Obligatoires Imposés par le Noyau (5 routes de base)
* `GET /health` : Vérification de la disponibilité et de l'uptime du service.
* `POST /tenant/activate` : Initialisation et souscription d'une entreprise avec configuration.
* `POST /tenant/deactivate` : Résiliation et purge immédiate des données du tenant.
* `GET /tenant/{tenant_id}/status` : État d'exécution et compteurs du tenant.
* `GET /config-schema` : Schéma JSON des paramètres personnalisables par l'entreprise.

#### 2. Endpoint Conditionnel de Consommation du Bus
* `POST /exchange/notify` : **Obligatoire uniquement parce que VisionX déclare consommer l'objet `commande`** dans son manifeste (`consumes: ["commande"]`). Le noyau l'appelle automatiquement dès qu'une commande est émise sur la plateforme.

#### 3. Endpoints Internes Supplémentaires Développés par VisionX
* `POST /marketing/prospects` : Création et scoring d'un prospect en local. Déclenche automatiquement l'appel sortant vers le noyau si le score $\ge 70$.
* `GET /marketing/prospects` : Consultation de la base de prospects du tenant.
* `GET /marketing/commandes` : Consultation de l'historique des commandes traitées par l'agent.

#### 4. Appels Sortants Effectués par VisionX vers le Noyau
* `POST {NOYAU_URL}/exchange/agent/prospect` : Publication d'un prospect qualifié sur le bus partagé (avec `Authorization: Bearer <key>` et `X-Tenant-Id`).
* `POST {NOYAU_URL}/webhooks/agent-events` : Envoi d'alertes ou d'événements opérationnels vers le tableau de bord noyau.

---

### Correction 3 — Procédure Définitive de Purge des Données Multi-Tenant

Conformément à la section 3 du contrat d'intégration (*"Doit supprimer ou anonymiser les donnees du tenant concerne"*), VisionX implémente la procédure de purge suivante lors de l'appel à `POST /tenant/deactivate` :
1. **Interruption des Traitements Actifs :** Révocation immédiate de la clé d'API locale du tenant et annulation des envois d'emails en file d'attente pour ce `tenant_id`.
2. **Suppression en Cascade :** Suppression définitive dans la base de données de :
   * L'ensemble des prospects rattachés au tenant (`prospects[tenant_id]`).
   * L'historique des commandes reçues (`commandes_recues[tenant_id]`).
   * Les journaux de campagnes et statistiques (`campagnes_executes[tenant_id]`).
   * La configuration et les jetons d'accès (`tenant_api_key`).
3. **Garantie d'Étanchéité Inter-Tenants :** La suppression utilise exclusivement une clause stricte `WHERE tenant_id = :id`. Aucune donnée d'un autre tenant n'est impactée.
4. **Preuve de Purge :** Tout appel ultérieur à `GET /tenant/{tenant_id}/status` retourne immédiatement une erreur **HTTP 404 (Tenant non activé)**, validé par test automatisé.

---

### Correction 4 — Décision Technologique Définitive

* **Langage & Framework :** **Python 3.10+ avec FastAPI**. Justification : imposé pour la cohérence du projet (DEVELOPER_INSTRUCTIONS), haute performance asynchrone, validation stricte Pydantic native et alignement sur `agent-exemple`.
* **Client HTTP :** **httpx** en mode asynchrone pour les appels sortants vers le noyau sans blocage d'I/O.
* **Persistance :** **SQLite en mode WAL (Write-Ahead Logging)** pour le développement local et les tests ; compatible **PostgreSQL** pour le déploiement multi-tenant en conteneur.
* **Moteur d'Emailing :** **Templates Jinja2** couplés à un connecteur SMTP standard (compatible Postfix local ou mock MailHog).
* **Abandon formel de Mautic complet :** L'intégration d'un serveur Mautic complet (PHP/MySQL) a été formellement écartée : trop lourd (> 1.5 Go de RAM), architecture redondante et incompatible avec l'exigence d'un agent micro-service léger (< 256 Mo de RAM imposé dans le manifeste). Notre moteur Python FastAPI embarqué réalise 100% des fonctions requises avec une empreinte minimale.

---

### Correction 5 — Preuves d'Exécution et Journal des Tests de Validation

Une suite de **15 tests automatisés (positifs et négatifs)** a été exécutée avec **100% de succès**. Le journal d'audit complet est consigné dans :  
📁 **`tests/preuves_validation_v1.1.json`**

#### Extrait du Journal d'Audit :
* ✅ **TEST-01 (`GET /health`) :** HTTP 200 en 19.78ms | Enveloppe `{status: "ok", data: {uptime_seconds: ...}, error: null}` conforme.
* ✅ **TEST-02 (`GET /config-schema`) :** HTTP 200 en 4.16ms | JSON Schema validé.
* ✅ **TEST-03 (`POST /tenant/activate`) :** HTTP 200 en 8.59ms | Tenant `ENT-ESTIN-01` activé avec seuil 75.
* ✅ **TEST-05 (Sécurité : sans `X-Tenant-Id`) :** HTTP 400 en 6.99ms | Rejet immédiat conforme.
* ✅ **TEST-06 (Sécurité : tenant inconnu) :** HTTP 404 en 14.51ms | Accès refusé conforme.
* ✅ **TEST-09 (Métier : commande confirmée) :** HTTP 200 en 5.68ms | Déclenchement de l'onboarding et conversion client.
* ✅ **TEST-10 (Métier : commande annulée) :** HTTP 200 en 4.76ms | Déclenchement de la relance win-back.
* ✅ **TEST-11 (Bus : objet non géré) :** HTTP 200 en 5.66ms | Ignoré silencieusement conformément au contrat.
* ✅ **TEST-12 (Métier : prospect qualifié) :** HTTP 200 en 83.87ms | Score 85 $\ge$ seuil 75 $\rightarrow$ publication vers le noyau.
* ✅ **TEST-14 (`POST /tenant/deactivate`) :** HTTP 200 en 4.35ms | Purge complète des données exécutée.
* ✅ **TEST-15 (Audit post-purge) :** HTTP 404 en 3.73ms | Vérification de l'inaccessibilité absolue des données purgées.

---

## 🏁 Conclusion de la Tâche 1
La **Tâche 1 (Version V1.1)** est définitivement stabilisée, documentée et prouvée par des tests reproductibles. Le projet passe officiellement à la **Tâche 2 (Livrable L2 — Charte de Projet)**.
