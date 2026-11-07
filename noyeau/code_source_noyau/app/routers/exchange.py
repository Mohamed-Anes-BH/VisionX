"""
Endpoints du bus d'échange inter-agents / humain.
Voir app/core/exchange_bus.py pour la logique, et
INTER_AGENT_DATA_CONTRACT.docx pour le registre des types d'objets standard
(commande, stock_level, expedition, facture, ticket_support, prospect...).
"""
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ExchangeObject, ProducerType, AgentSubscription, User
from ..core.exchange_bus import publish_exchange_object
from ..core.security import get_current_user, require_same_company_or_admin

router = APIRouter(tags=["Bus d'échange"])


class ExchangePublishPayload(BaseModel):
    external_id: str
    payload: dict


# ────────────────────────────────────────────────────────────────
# Point d'entrée AGENT (authentifié par tenant_api_key)
# ────────────────────────────────────────────────────────────────

@router.post("/exchange/agent/{object_type}")
async def agent_publish_object(
    object_type: str,
    body: ExchangePublishPayload,
    authorization: str = Header(None),
    x_tenant_id: str = Header(None, alias="X-Tenant-Id"),
    db: Session = Depends(get_db),
):
    """Un agent publie ou met à jour un objet métier partagé pour son tenant."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "En-tête Authorization manquant")
    tenant_api_key = authorization.replace("Bearer ", "")

    subscription = db.query(AgentSubscription).filter(
        AgentSubscription.tenant_api_key == tenant_api_key,
        AgentSubscription.company_id == x_tenant_id,
    ).first()
    if not subscription:
        raise HTTPException(403, "Clé API tenant invalide pour cette entreprise")

    if object_type not in (subscription.agent.produces or []):
        raise HTTPException(
            400,
            f"L'agent '{subscription.agent.slug}' ne déclare pas produire le type '{object_type}' "
            f"dans son manifeste (champ 'produces')."
        )

    obj = await publish_exchange_object(
        db, company_id=x_tenant_id, object_type=object_type,
        external_id=body.external_id, payload=body.payload,
        produced_by_type=ProducerType.AGENT,
        produced_by_agent_id=subscription.agent_id,
    )
    return {"status": "ok", "data": {"id": str(obj.id), "version": obj.version}, "error": None}


@router.get("/exchange/agent/{object_type}")
def agent_read_objects(
    object_type: str,
    authorization: str = Header(None),
    x_tenant_id: str = Header(None, alias="X-Tenant-Id"),
    db: Session = Depends(get_db),
):
    """Un agent peut aussi tirer (pull) l'état courant d'un type d'objet, en plus des notifications push."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "En-tête Authorization manquant")
    tenant_api_key = authorization.replace("Bearer ", "")

    subscription = db.query(AgentSubscription).filter(
        AgentSubscription.tenant_api_key == tenant_api_key,
        AgentSubscription.company_id == x_tenant_id,
    ).first()
    if not subscription:
        raise HTTPException(403, "Clé API tenant invalide pour cette entreprise")

    objects = db.query(ExchangeObject).filter(
        ExchangeObject.company_id == x_tenant_id,
        ExchangeObject.object_type == object_type,
    ).all()
    return {"status": "ok", "data": [
        {"external_id": o.external_id, "version": o.version, "payload": o.payload} for o in objects
    ], "error": None}


# ────────────────────────────────────────────────────────────────
# Point d'entrée ENTREPRISE / HUMAIN (authentifié par compte utilisateur,
# utilisé par le tableau de bord). Permet à un employé (ex: responsable
# stock) d'alimenter ou de consulter le même flux qu'un agent, même sans
# agent souscrit pour cette tâche.
# ────────────────────────────────────────────────────────────────

@router.post("/companies/{company_id}/exchange/{object_type}")
async def human_publish_object(
    company_id: str,
    object_type: str,
    body: ExchangePublishPayload,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_same_company_or_admin),
):
    obj = await publish_exchange_object(
        db, company_id=company_id, object_type=object_type,
        external_id=body.external_id, payload=body.payload,
        produced_by_type=ProducerType.HUMAN,
        produced_by_user_id=user.id,
    )
    return {"id": str(obj.id), "version": obj.version}


@router.get("/companies/{company_id}/exchange/{object_type}")
def human_read_objects(
    company_id: str,
    object_type: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_same_company_or_admin),
):
    """Utilisé par le tableau de bord entreprise pour afficher un flux (ex: niveaux de stock actuels)."""
    objects = db.query(ExchangeObject).filter(
        ExchangeObject.company_id == company_id,
        ExchangeObject.object_type == object_type,
    ).all()
    return [
        {
            "external_id": o.external_id,
            "version": o.version,
            "payload": o.payload,
            "produced_by": o.produced_by_type.value,
            "updated_at": o.updated_at,
        }
        for o in objects
    ]
