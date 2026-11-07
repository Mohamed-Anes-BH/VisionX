"""
Agent exemple.

Ce fichier n'est pas un agent "utile" en soi : c'est un gabarit minimal,
qui respecte le contrat d'integration du noyau, et qui sert de point de
depart pour chaque equipe. Les 6 routes ci-dessous sont celles exigees
par AGENT_INTEGRATION_CONTRACT.docx ; tout le reste (la logique metier
reelle de votre agent) est a ecrire a la place du code de demonstration
que vous trouverez dans la section "LOGIQUE DE DEMONSTRATION" plus bas.

Pour lancer cet agent en local :
    pip install -r requirements.txt
    uvicorn main:app --port 9000

Il faudra ensuite le soumettre au noyau avec le fichier agent.manifest.json
fourni a cote de ce main.py (voir DEVELOPER_INSTRUCTIONS.docx, etape 10).
"""
import os
import time
import httpx
from fastapi import FastAPI, Header, HTTPException

app = FastAPI(title="Agent exemple")

# Stockage en memoire, par tenant. Pour un vrai agent, remplacez ceci par
# une vraie base de donnees (SQLite suffit largement pour ce mini-projet).
etat_par_tenant: dict[str, dict] = {}

demarre_le = time.time()

NOYAU_URL = os.getenv("NOYAU_URL", "http://localhost:8000")


# ---------------------------------------------------------------------
# Les 5 routes obligatoires du contrat
# ---------------------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "data": {"uptime_seconds": int(time.time() - demarre_le)},
        "error": None,
    }


@app.post("/tenant/activate")
def activate(body: dict, authorization: str = Header(None), x_tenant_id: str = Header(None, alias="X-Tenant-Id")):
    if not x_tenant_id:
        raise HTTPException(400, "X-Tenant-Id manquant")

    config = body.get("config", {})
    etat_par_tenant[x_tenant_id] = {
        "tenant_api_key": authorization.replace("Bearer ", "") if authorization else None,
        "config": config,
        "seuil_alerte": config.get("seuil_alerte", 80),
        "derniere_mesure": None,
    }
    return {"status": "ok", "data": {"activated": True}, "error": None}


@app.post("/tenant/deactivate")
def deactivate(x_tenant_id: str = Header(None, alias="X-Tenant-Id")):
    etat_par_tenant.pop(x_tenant_id, None)
    return {"status": "ok", "data": {"deactivated": True, "data_purged": True}, "error": None}


@app.get("/tenant/{tenant_id}/status")
def tenant_status(tenant_id: str):
    tenant = etat_par_tenant.get(tenant_id)
    if not tenant:
        raise HTTPException(404, "Tenant non active")
    return {
        "status": "ok",
        "data": {"state": "running", "derniere_mesure": tenant["derniere_mesure"]},
        "error": None,
    }


@app.get("/config-schema")
def config_schema():
    """
    Decrit les champs que l'entreprise peut renseigner a l'activation.
    Le noyau utilise ce schema pour generer le formulaire de configuration
    (dans une version future ; pour ce mini-projet, la config par defaut
    suffit).
    """
    return {
        "status": "ok",
        "data": {
            "type": "object",
            "properties": {
                "seuil_alerte": {
                    "type": "number",
                    "description": "Valeur au-dela de laquelle une alerte est envoyee",
                    "default": 80,
                }
            },
        },
        "error": None,
    }


# ---------------------------------------------------------------------
# Route facultative : a implementer uniquement si votre agent CONSOMME
# des objets du bus d'echange (champ "consumes" non vide dans votre
# manifeste). Sinon, vous pouvez supprimer cette fonction.
# ---------------------------------------------------------------------

@app.post("/exchange/notify")
def exchange_notify(body: dict, x_tenant_id: str = Header(None, alias="X-Tenant-Id")):
    # body contient : object_type, external_id, version, payload
    # Exemple : un agent de stock recevrait ici une "commande" publiee
    # par l'agent commercial, et deciderait quoi en faire.
    return {"status": "ok", "data": {"processed": True}, "error": None}


# ---------------------------------------------------------------------
# LOGIQUE DE DEMONSTRATION
#
# Ce qui suit n'est pas exige par le contrat : c'est un exemple concret
# pour montrer comment un agent envoie une alerte au noyau, et comment il
# peut, s'il le souhaite, publier un objet sur le bus d'echange. Une
# equipe de la filiere IoT pourrait remplacer "mesure" par une vraie
# lecture de capteur ; une equipe de la filiere cybersecurite par le
# resultat d'un scan ; etc.
# ---------------------------------------------------------------------

@app.post("/demo/mesure/{tenant_id}")
async def demo_recevoir_mesure(tenant_id: str, valeur: float):
    """
    Point d'entree de demonstration, appele ici manuellement (par exemple
    avec curl) pour simuler l'arrivee d'une mesure. Un vrai agent IoT
    appellerait ce genre de logique depuis une boucle de lecture de
    capteur, pas depuis une route HTTP exposee publiquement.
    """
    tenant = etat_par_tenant.get(tenant_id)
    if not tenant:
        raise HTTPException(404, "Tenant non active")

    tenant["derniere_mesure"] = valeur

    if valeur > tenant["seuil_alerte"]:
        await _envoyer_alerte(tenant_id, tenant["tenant_api_key"], valeur)

    return {"status": "ok", "data": {"recue": True}, "error": None}


async def _envoyer_alerte(tenant_id: str, tenant_api_key: str, valeur: float):
    """Exemple d'appel au webhook d'alertes du noyau."""
    async with httpx.AsyncClient(timeout=5) as client:
        await client.post(
            f"{NOYAU_URL}/webhooks/agent-events",
            headers={
                "Authorization": f"Bearer {tenant_api_key}",
                "X-Tenant-Id": tenant_id,
            },
            json={
                "event_type": "seuil_depasse",
                "severity": "medium",
                "data": {"valeur": valeur},
            },
        )
