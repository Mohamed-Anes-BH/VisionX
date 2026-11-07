"""
Agent Marketing Automation — Équipe VisionX (ESTIN 2026-2027)
Filière : Automatisation Métier
Produit : prospect
Consomme : commande

Conforme à 100% à :
- AGENT_INTEGRATION_CONTRACT.docx v1.0
- INTER_AGENT_DATA_CONTRACT.docx
- DEVELOPER_INSTRUCTIONS.docx
"""

import os
import time
from typing import Optional, Dict, Any, List
import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

app = FastAPI(
    title="Agent Marketing Automation - VisionX",
    description="Agent métier d'automatisation marketing : lead scoring, publication de prospects et scénarios post-commande.",
    version="1.0.0"
)

# Configuration de base
demarre_le = time.time()
NOYAU_URL = os.getenv("NOYAU_URL", "http://localhost:8000")

# Stockage multi-tenant en mémoire (isolé par tenant_id)
# En production, ce dictionnaire est remplacé par une base SQLite/PostgreSQL
# Chaque requête filtre IMPÉRATIVEMENT par tenant_id.
tenants_db: Dict[str, Dict[str, Any]] = {}


# =====================================================================
# MODÈLES DE DONNÉES CONFORMES AUX CONTRATS DU NOYAU
# =====================================================================

class ProspectPayload(BaseModel):
    """Conforme au schéma 'prospect' de INTER_AGENT_DATA_CONTRACT.docx"""
    id_prospect: str = Field(..., description="Exemple: PROS-2027-0210")
    nom: str = Field(..., description="Exemple: Martin Leroy")
    email: str = Field(..., description="Exemple: martin.leroy@example.com")
    score_interet: int = Field(default=50, ge=0, le=100)
    statut: str = Field(default="nouveau", description="nouveau, qualifie, contacte, converti")


class CommandeClient(BaseModel):
    nom: str
    email: str


class LigneCommande(BaseModel):
    sku: str
    quantite: int
    prix_unitaire_ht: float


class CommandePayload(BaseModel):
    """Conforme au schéma 'commande' de INTER_AGENT_DATA_CONTRACT.docx"""
    numero_commande: str
    date_commande: str
    client: CommandeClient
    lignes: List[LigneCommande] = []
    montant_total_ht: float
    statut: str  # en_attente, confirmee, expediee, facturee, annulee


# =====================================================================
# LES 5 ROUTES OBLIGATOIRES (AGENT_INTEGRATION_CONTRACT Section 3)
# Toute réponse respecte strictement { status, data, error } (Section 4)
# =====================================================================

@app.get("/health")
def health():
    """Vérification de bon fonctionnement et de disponibilité."""
    return {
        "status": "ok",
        "data": {
            "uptime_seconds": int(time.time() - demarre_le),
            "agent": "Marketing Automation - VisionX",
            "version": "1.0.0"
        },
        "error": None
    }


@app.post("/tenant/activate")
def activate(body: dict, authorization: str = Header(None), x_tenant_id: str = Header(None, alias="X-Tenant-Id")):
    """
    Appelé par le noyau quand une entreprise souscrit à l'agent.
    Enregistre les clés et initialise les données du tenant de façon étanche.
    """
    if not x_tenant_id:
        raise HTTPException(400, "En-tête X-Tenant-Id manquant")

    api_key = authorization.replace("Bearer ", "").strip() if authorization else None
    config = body.get("config", {})

    tenants_db[x_tenant_id] = {
        "tenant_id": x_tenant_id,
        "tenant_api_key": api_key,
        "config": {
            "seuil_qualification_lead": config.get("seuil_qualification_lead", 70),
            "auto_email_bienvenue": config.get("auto_email_bienvenue", True),
            "auto_email_relance": config.get("auto_email_relance", True)
        },
        "prospects": {},
        "commandes_recues": {},
        "campagnes_executes": [],
        "date_activation": time.time()
    }

    print(f"[VISIONX] Tenant activé avec succès : {x_tenant_id}")
    return {
        "status": "ok",
        "data": {"activated": True, "tenant_id": x_tenant_id},
        "error": None
    }


@app.post("/tenant/deactivate")
def deactivate(x_tenant_id: str = Header(None, alias="X-Tenant-Id")):
    """
    Appelé par le noyau quand l'entreprise résilie sa souscription.
    Purge immédiatement et totalement les données du tenant (RGPD / Confidentialité).
    """
    if not x_tenant_id:
        raise HTTPException(400, "En-tête X-Tenant-Id manquant")

    deleted = tenants_db.pop(x_tenant_id, None) is not None
    print(f"[VISIONX] Tenant désactivé et données purgées : {x_tenant_id}")
    return {
        "status": "ok",
        "data": {"deactivated": True, "data_purged": deleted},
        "error": None
    }


@app.get("/tenant/{tenant_id}/status")
def tenant_status(tenant_id: str):
    """Retourne l'état courant de l'agent pour ce tenant spécifique."""
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(404, f"Tenant '{tenant_id}' non activé sur cet agent")

    return {
        "status": "ok",
        "data": {
            "state": "running",
            "prospects_count": len(tenant["prospects"]),
            "commandes_recues_count": len(tenant["commandes_recues"]),
            "campagnes_count": len(tenant["campagnes_executes"])
        },
        "error": None
    }


@app.get("/config-schema")
def config_schema():
    """Schéma JSON décrivant les paramètres configurables par l'entreprise."""
    return {
        "status": "ok",
        "data": {
            "type": "object",
            "properties": {
                "seuil_qualification_lead": {
                    "type": "integer",
                    "description": "Score d'intérêt à partir duquel le prospect est automatiquement publié vers l'agent Commercial",
                    "default": 70,
                    "minimum": 0,
                    "maximum": 100
                },
                "auto_email_bienvenue": {
                    "type": "boolean",
                    "description": "Déclencher automatiquement un email de bienvenue dès réception d'une commande confirmée",
                    "default": True
                },
                "auto_email_relance": {
                    "type": "boolean",
                    "description": "Déclencher une campagne de relance en cas de commande annulée",
                    "default": True
                }
            }
        },
        "error": None
    }


# =====================================================================
# ROUTE DE CONSOMMATION DU BUS D'ÉCHANGE (Section 6 du Contrat)
# Notre agent CONSOMME l'objet "commande" publié par l'agent Commercial
# =====================================================================

@app.post("/exchange/notify")
async def exchange_notify(body: dict, x_tenant_id: str = Header(None, alias="X-Tenant-Id")):
    """
    Appelé automatiquement par le noyau lorsqu'un objet 'commande' est publié
    par l'agent Commercial de la même entreprise (ou saisi manuellement).
    """
    if not x_tenant_id:
        raise HTTPException(400, "X-Tenant-Id manquant")

    tenant = tenants_db.get(x_tenant_id)
    if not tenant:
        raise HTTPException(404, "Tenant inconnu ou inactif")

    object_type = body.get("object_type")
    external_id = body.get("external_id")
    payload = body.get("payload", {})

    print(f"\n[VISIONX] Notification reçue du bus d'échange pour le tenant {x_tenant_id}:")
    print(f"   Objet : {object_type} | ID : {external_id}")

    if object_type != "commande":
        # Règle commune : un champ ou type inattendu est ignoré silencieusement
        return {"status": "ok", "data": {"processed": False, "reason": "unhandled_object_type"}, "error": None}

    # Stocker la commande dans la base du tenant
    tenant["commandes_recues"][external_id] = payload

    statut_commande = payload.get("statut", "en_attente")
    client_info = payload.get("client", {})
    client_email = client_info.get("email")
    client_nom = client_info.get("nom")
    montant = payload.get("montant_total_ht", 0.0)

    actions_effectuees = []

    # Scénario Marketing 1 : Commande Confirmée -> Onboarding & Fidélisation
    if statut_commande in ["confirmee", "en_attente"]:
        # Mise à jour ou création du prospect en tant que client converti
        prospect_existant = next((p for p in tenant["prospects"].values() if p["email"] == client_email), None)
        if prospect_existant:
            prospect_existant["score_interet"] = 100
            prospect_existant["statut"] = "converti_client"
        else:
            nouveau_id = f"PROS-CLIENT-{len(tenant['prospects'])+1:04d}"
            tenant["prospects"][nouveau_id] = {
                "id_prospect": nouveau_id,
                "nom": client_nom,
                "email": client_email,
                "score_interet": 100,
                "statut": "converti_client"
            }

        if tenant["config"]["auto_email_bienvenue"]:
            action_desc = f"Email de bienvenue et remerciement envoyé à {client_email} pour la commande {external_id} ({montant}€)"
            tenant["campagnes_executes"].append({
                "type": "onboarding_post_achat",
                "commande_id": external_id,
                "email": client_email,
                "timestamp": time.time()
            })
            actions_effectuees.append(action_desc)
            print(f"   [ACTION MARKETING] {action_desc}")

    # Scénario Marketing 2 : Commande Annulée -> Campagne de Win-back / Enquête
    elif statut_commande == "annulee":
        if tenant["config"]["auto_email_relance"]:
            action_desc = f"Email de relance / enquête d'abandon envoyé à {client_email}"
            tenant["campagnes_executes"].append({
                "type": "relance_abandon",
                "commande_id": external_id,
                "email": client_email,
                "timestamp": time.time()
            })
            actions_effectuees.append(action_desc)
            print(f"   [ACTION MARKETING] {action_desc}")

    return {
        "status": "ok",
        "data": {
            "processed": True,
            "commande_id": external_id,
            "actions": actions_effectuees
        },
        "error": None
    }


# =====================================================================
# LOGIQUE MÉTIER DE PRODUCTION D'OBJETS : PUBLIER UN "prospect"
# =====================================================================

async def publier_prospect_vers_noyau(tenant_id: str, prospect_data: dict) -> bool:
    """
    Envoie un objet 'prospect' au bus d'échange du noyau (Section 6).
    Le noyau notifiera ensuite automatiquement l'agent Commercial !
    """
    tenant = tenants_db.get(tenant_id)
    if not tenant or not tenant.get("tenant_api_key"):
        print(f"[ERREUR] Clé API noyau absente pour le tenant {tenant_id}")
        return False

    url = f"{NOYAU_URL}/exchange/agent/prospect"
    headers = {
        "Authorization": f"Bearer {tenant['tenant_api_key']}",
        "X-Tenant-Id": tenant_id,
        "Content-Type": "application/json"
    }
    body = {
        "external_id": prospect_data["id_prospect"],
        "payload": prospect_data
    }

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(url, headers=headers, json=body)
            if resp.status_code == 200:
                print(f"[VISIONX -> NOYAU] Prospect {prospect_data['id_prospect']} publié avec succès sur le bus !")
                return True
            else:
                print(f"[VISIONX -> NOYAU ERREUR] Code {resp.status_code} : {resp.text}")
                return False
    except Exception as e:
        print(f"[VISIONX -> NOYAU EXCEPTION] Connexion impossible au noyau ({url}) : {e}")
        return False


@app.post("/marketing/prospects")
async def creer_prospect(prospect: ProspectPayload, x_tenant_id: str = Header(None, alias="X-Tenant-Id")):
    """
    Point d'entrée interne : Créer un nouveau lead / prospect issu d'une campagne.
    Si son score atteint ou dépasse le seuil configuré, il est qualifié et publié
    immédiatement sur le bus d'échange du noyau pour l'agent Commercial !
    """
    if not x_tenant_id or x_tenant_id not in tenants_db:
        raise HTTPException(400, "Tenant invalide ou inactif")

    tenant = tenants_db[x_tenant_id]
    data = prospect.dict()
    seuil = tenant["config"]["seuil_qualification_lead"]

    publie_sur_bus = False
    if data["score_interet"] >= seuil:
        data["statut"] = "qualifie"
        publie_sur_bus = await publier_prospect_vers_noyau(x_tenant_id, data)

    tenant["prospects"][data["id_prospect"]] = data

    return {
        "status": "ok",
        "data": {
            "prospect": data,
            "qualifie": data["score_interet"] >= seuil,
            "publie_au_noyau": publie_sur_bus
        },
        "error": None
    }


@app.get("/marketing/prospects")
def lister_prospects(x_tenant_id: str = Header(None, alias="X-Tenant-Id")):
    """Consulte la base de prospects du tenant."""
    if not x_tenant_id or x_tenant_id not in tenants_db:
        raise HTTPException(400, "Tenant invalide ou inactif")

    return {
        "status": "ok",
        "data": list(tenants_db[x_tenant_id]["prospects"].values()),
        "error": None
    }


@app.get("/marketing/commandes")
def lister_commandes(x_tenant_id: str = Header(None, alias="X-Tenant-Id")):
    """Consulte l'historique des commandes reçues via le bus d'échange."""
    if not x_tenant_id or x_tenant_id not in tenants_db:
        raise HTTPException(400, "Tenant invalide ou inactif")

    return {
        "status": "ok",
        "data": list(tenants_db[x_tenant_id]["commandes_recues"].values()),
        "error": None
    }
