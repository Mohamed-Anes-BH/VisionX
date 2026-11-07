from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Agent, AgentStatus, AgentSubscription, SubscriptionStatus
from ..core.security import generate_tenant_api_key
from ..core.agent_gateway import activate_agent_for_tenant, deactivate_agent_for_tenant, AgentContractViolation

router = APIRouter(prefix="/subscriptions", tags=["Souscriptions"])


class SubscribeRequest(BaseModel):
    company_id: str
    agent_slug: str
    config: dict = {}


@router.post("")
async def subscribe_to_agent(payload: SubscribeRequest, db: Session = Depends(get_db)):
    """
    Une entreprise souscrit à un agent : c'est ici que la mécanique
    "paie et active" se déclenche (le paiement réel est délégué à un
    fournisseur de paiement, non détaillé ici).
    """
    agent = db.query(Agent).filter(
        Agent.slug == payload.agent_slug, Agent.status == AgentStatus.PUBLISHED
    ).first()
    if not agent:
        raise HTTPException(404, "Agent introuvable ou non publié")

    subscription = AgentSubscription(
        company_id=payload.company_id,
        agent_id=agent.id,
        status=SubscriptionStatus.PENDING,
        tenant_api_key=generate_tenant_api_key(),
        config=payload.config,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    # TODO PRODUCTION : déclencher le paiement (Stripe, virement, etc.) avant activation réelle.

    try:
        await activate_agent_for_tenant(db, subscription)
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.activated_at = datetime.utcnow()
        db.commit()
    except AgentContractViolation as e:
        subscription.status = SubscriptionStatus.SUSPENDED
        db.commit()
        raise HTTPException(502, f"L'agent n'a pas pu être activé : {str(e)}")

    return {
        "subscription_id": str(subscription.id),
        "status": subscription.status.value,
        "message": f"Agent '{agent.name}' activé pour votre entreprise",
    }


@router.post("/{subscription_id}/cancel")
async def cancel_subscription(subscription_id: str, db: Session = Depends(get_db)):
    subscription = db.query(AgentSubscription).get(subscription_id)
    if not subscription:
        raise HTTPException(404, "Souscription introuvable")

    try:
        await deactivate_agent_for_tenant(db, subscription)
    except AgentContractViolation:
        pass  # on désactive côté plateforme même si l'agent ne répond plus

    subscription.status = SubscriptionStatus.CANCELLED
    subscription.cancelled_at = datetime.utcnow()
    db.commit()
    return {"message": "Souscription annulée"}


@router.get("/company/{company_id}")
def list_company_subscriptions(company_id: str, db: Session = Depends(get_db)):
    return db.query(AgentSubscription).filter(AgentSubscription.company_id == company_id).all()
