# Agent Marketing Automation — Équipe VisionX

**Filière :** Automatisation Métier  
**Agent :** `agent-marketing-automation-visionx`  
**Équipe :** VisionX (Chef d'équipe : Mohamed Anes Bouharizi)  
**École :** ESTIN (2ème Année CS 2026–2027)  

---

## 📋 Rôle de l'Agent dans la Plateforme Commune
* **PRODUIT :** `prospect` (Publié sur le bus d'échange du noyau via `POST /exchange/agent/prospect` lorsque `score_interet >= seuil`).
* **CONSOMME :** `commande` (Reçu via le webhook `POST /exchange/notify` lors de la publication d'une commande par l'Agent Commercial).

---

## 🚀 Démarrage Rapide en Local

### 1. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 2. Lancement de l'agent
```bash
uvicorn main:app --port 9000 --reload
```
L'agent sera accessible sur `http://localhost:9000`.  
La documentation interactive OpenAPI / Swagger est disponible sur `http://localhost:9000/docs`.

---

## 🔗 Endpoints Conformes aux Contrats du Noyau

| Méthode | Route | Rôle |
|---|---|---|
| `GET` | `/health` | Uptime et état de santé de l'agent |
| `POST` | `/tenant/activate` | Activation d'une entreprise avec configuration initiale |
| `POST` | `/tenant/deactivate` | Résiliation et purge immédiate des données du tenant |
| `GET` | `/tenant/{id}/status` | État d'exécution et compteurs (prospects, commandes) |
| `GET` | `/config-schema` | JSON Schema des options configurables |
| `POST` | `/exchange/notify` | Webhook de réception des objets `commande` du bus |
| `POST` | `/marketing/prospects` | Création et qualification automatique de leads |
| `GET` | `/marketing/prospects` | Consultation des prospects du tenant |

Toutes les réponses respectent strictement l'enveloppe imposée :
```json
{
  "status": "ok" | "error",
  "data": { ... } | null,
  "error": null | "message"
}
```

---

## 🐳 Déploiement Docker
```bash
docker build -t visionx-marketing-agent .
docker run -p 9000:9000 -e NOYAU_URL=http://localhost:8000 visionx-marketing-agent
```

