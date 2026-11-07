"""
Point d'entrée UNIQUE et STANDARDISÉ que tous les agents (quel que soit
le programmeur qui les a développés) doivent utiliser pour remonter des
alertes/événements vers le noyau. Voir AGENT_INTEGRATION_CONTRACT.docx,
section "Webhook sortant (Agent -> Noyau)".
"""
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AgentSubscription
from ..core.agent_gateway import record_inbound_event

router = APIRouter(prefix="/webhooks", tags=["Webhooks Agents"])


class AgentEventPayload(BaseModel):
    event_type: str          # ex: "commande_traitee", "ticket_ouvert", "stock_faible"
    severity: str = "info"   # info | low | medium | high | critical
    data: dict = {}


@router.post("/agent-events")
def receive_agent_event(
    payload: AgentEventPayload,
    authorization: str = Header(None),
    x_tenant_id: str = Header(None, alias="X-Tenant-Id"),
    db: Session = Depends(get_db),
):
    """
    Un agent appelle CET endpoint (jamais directement la base de données du
    noyau) pour signaler un événement métier (alerte, incident, notification) concernant un tenant donné.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "En-tête Authorization manquant")
    tenant_api_key = authorization.replace("Bearer ", "")

    subscription = db.query(AgentSubscription).filter(
        AgentSubscription.tenant_api_key == tenant_api_key,
        AgentSubscription.company_id == x_tenant_id,
    ).first()
    if not subscription:
        raise HTTPException(403, "Clé API tenant invalide pour cette entreprise")

    log = record_inbound_event(
        db,
        agent_id=subscription.agent_id,
        company_id=subscription.company_id,
        event=payload.dict(),
    )
    return {"status": "ok", "data": {"event_id": str(log.id)}, "error": None}
