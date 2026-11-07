# Livrable L3 — Procès-Verbal de Réunion de Lancement (Kick-off Meeting)
**Module « Conduite de Projet » — 2ème Année CS (ESTIN 2026–2027)**  
**Équipe VisionX — Filière Automatisation Métier : Agent Marketing Automation**

---

### Informations Générales de Séance
- **Date & Heure :** Samedi 07 Novembre 2026, de 14h00 à 16h30
- **Lieu :** Salle de projet / Visioconférence d'équipe ESTIN
- **Projet :** Conception et développement de l'Agent Marketing Automation (`agent-marketing-automation-visionx`)
- **Présidence de séance :** Mohamed Anes Bouharizi (Chef de projet)
- **Secrétariat de séance :** Sebti Iyed & Bahi Adem
- **Participants présents (100 %) :**
  1. Mohamed Anes Bouharizi
  2. Sebti Iyed
  3. Zouane Akram
  4. Fellah Baha
  5. Bertil Anis
  6. Bahi Adem

---

### 1. Ordre du Jour & Contexte
Faisant suite à la validation du Document d'Orientation (L1) et de la Charte de Projet (L2), l'équipe VisionX s'est réunie au complet pour officialiser le lancement opérationnel des travaux. L'ordre du jour portait sur :
1. La confirmation collective du périmètre fonctionnel et des objectifs métier de l'agent.
2. L'attribution nominative et l'acceptation formelle des rôles et responsabilités (OBS / RACI).
3. Le verrouillage des décisions d'architecture technique (FastAPI, persistance multi-tenant, micro-moteur Jinja2/SMTP).
4. La formalisation et la signature de **l'engagement d'équipe** garantissant le respect strict des contrats d'intégration fournis par l'enseignant (`AGENT_INTEGRATION_CONTRACT.doc` et `INTER_AGENT_DATA_CONTRACT.doc`) ainsi que de la règle absolue de cloisonnement de code inter-équipes.

---

### 2. Attribution des Rôles & Responsabilités (OBS)

| Membre de l'équipe | Rôle principal (OBS) | Périmètre d'action & Livrables sous sa responsabilité |
| :--- | :--- | :--- |
| **Mohamed Anes Bouharizi** | Chef de Projet & Lead Tech Backend | Pilotage général, calendrier (T1 à T9), architecture FastAPI asynchrone, packaging Dockerfile. |
| **Sebti Iyed** | Architecte Intégration Noyau | Implémentation des 5 routes obligatoires, cycle de vie tenant, publication/consommation du bus. |
| **Zouane Akram** | Lead Scoring & Moteur Décisionnel | Algorithme de scoring d'intérêt prospect (seuil >= 70), automatisation du déclenchement des publications. |
| **Fellah Baha** | Lead Emailing & Scénarios Marketing | Scénarios réactifs (bienvenue prospect, confirmation/relance commande), moteur de templates Jinja2. |
| **Bertil Anis** | Responsable Multi-tenant, Données & Sécurité | Cloisonnement strict des données par `tenant_id`, procédure automatisée de purge immédiate et irréversible. |
| **Bahi Adem** | Lead QA, Conformité & Recette | Banc de tests automatisés (15 tests de conformité validés), vérification systématique de l'enveloppe `{status, data, error}`. |

---

### 3. Décisions Techniques et Opérationnelles Clés
- **Stack Backend retenue :** Python 3.10+ avec FastAPI et Pydantic v2. Choix justifié par l'asynchronisme natif, la légèreté (< 150 Mo de RAM vs contrainte 256 Mo) et la validation automatique des schémas JSON.
- **Remplacement de l'outil lourd Mautic :** L'équipe a validé à l'unanimité le remplacement d'une instance complète Mautic par un micro-moteur modulaire Jinja2 couplé au protocole SMTP standard, assurant une conformité parfaite tout en restant dans les limites de ressources prescrites.
- **Échanges avec le Noyau central :**
  - **Sortant (Publication) :** Publication d'objets `prospect` sur `POST {NOYAU_URL}/exchange/agent/prospect` avec en-têtes `Authorization: Bearer <api_key>` et `X-Tenant-Id`.
  - **Entrant (Consommation) :** Traitement des notifications d'objets `commande` reçues sur l'endpoint dédié de l'agent `POST /exchange/notify`.
- **Enveloppe obligatoire :** Chaque endpoint retourne strictement sans exception `{"status": "ok"|"error", "data": {...}|null, "error": msg|null}`.

---

### 4. Engagement Collectif sur le Contrat d'Intégration & les Règles du Projet
Les six membres de l'équipe VisionX s'engagent solennellement sur l'honneur à respecter les clauses non négociables suivantes :
1. **Respect absolu du Contrat d'Intégration (`AGENT_INTEGRATION_CONTRACT.doc`) :** Implémenter fidèlement les 5 endpoints obligatoires (`/health`, `/tenant/activate`, `/tenant/deactivate`, `/tenant/{id}/status`, `/config-schema`) et le format d'enveloppe standard.
2. **Respect du Registre des Objets Métier (`INTER_AGENT_DATA_CONTRACT.doc`) :** Publier et consommer les objets métier (`prospect` et `commande`) en parfaite conformité de types et de nommage des champs.
3. **Cloisonnement total du code source (Section 4 du Sujet) :** Interdiction stricte de consulter, copier ou invoquer directement le code source d'une autre équipe. Tout couplage s'effectue obligatoirement via le bus centralisé du noyau.
4. **Qualité logicielle et traçabilité :** Packaging sous conteneur Docker fonctionnel, historique Git propre et commits réguliers sur le dépôt privé assigné.

---

### 5. Prochaines Échéances
- **Jalon T5 (Livrable L4) :** Rédaction de la Planification détaillée (`METIER_PLAN_AgentMarketing.docx`, 5 à 6 pages avec PERT, Gantt, OBS/RACI et évaluation budgétaire/charges).
- **Jalon T6 (Livrable L5) :** Déploiement du conteneur et soumission du manifeste `agent.manifest.json` pour la phase d'assemblage live sur le noyau enseignant.

---

### 6. Signatures des Membres de l'Équipe VisionX

| Membre | Rôle | Mention & Approbation |
| :--- | :--- | :--- |
| **Mohamed Anes Bouharizi** | Chef de Projet & Lead Tech | *Lu et approuvé — Engagement validé* |
| **Sebti Iyed** | Architecte Intégration Noyau | *Lu et approuvé — Engagement validé* |
| **Zouane Akram** | Lead Scoring & Décisionnel | *Lu et approuvé — Engagement validé* |
| **Fellah Baha** | Lead Emailing & Scénarios | *Lu et approuvé — Engagement validé* |
| **Bertil Anis** | Resp. Multi-tenant & Données | *Lu et approuvé — Engagement validé* |
| **Bahi Adem** | Lead QA & Recette | *Lu et approuvé — Engagement validé* |
