"""
Exchange Bus — Bus d'échange de données inter-agents ET humain.
================================================================
Cœur de la collaboration entre agents d'une même entreprise (ex: l'agent
Commercial produit une "commande", l'agent Stock la consomme et publie un
"mouvement_stock", l'agent Logistique consomme ce mouvement pour produire
une "expedition").

Principe : le noyau ne met JAMAIS deux agents en relation directe. Tout
passe par une table d'objets métier partagés (ExchangeObject), avec deux
points d'entrée en écriture qui alimentent la même donnée :
  - un point d'entrée "agent" (routers/exchange.py, section agent),
    authentifié par la tenant_api_key de l'agent producteur ;
  - un point d'entrée "humain" (routers/exchange.py, section entreprise),
    authentifié par le compte utilisateur de l'entreprise, utilisé par le
    tableau de bord. Cela permet à un employé de l'entreprise (ex. le
    responsable stock) d'alimenter ou de consulter le même flux qu'un
    agent, même si l'entreprise n'a pas souscrit à un agent pour cette
    tâche précise.

Quand un objet est publié ou mis à jour, le noyau notifie automatiquement
(push HTTP) tous les agents ACTIFS du même tenant qui déclarent consommer
ce type d'objet dans leur manifeste (`Agent.consumes`).
"""
from datetime import datetime
from sqlalchemy.orm import Session

from ..models import ExchangeObject, ProducerType, Agent, AgentSubscription, SubscriptionStatus
from .agent_gateway import call_agent, AgentContractViolation


async def publish_exchange_object(
    db: Session,
    company_id: str,
    object_type: str,
    external_id: str,
    payload: dict,
    produced_by_type: ProducerType,
    produced_by_agent_id: str | None = None,
    produced_by_user_id: str | None = None,
) -> ExchangeObject:
    """
    Crée ou met à jour (par external_id) un objet métier partagé, puis
    notifie tous les agents consommateurs actifs de ce tenant.
    """
    existing = db.query(ExchangeObject).filter(
        ExchangeObject.company_id == company_id,
        ExchangeObject.object_type == object_type,
        ExchangeObject.external_id == external_id,
    ).first()

    if existing:
        existing.payload = payload
        existing.version += 1
        existing.updated_at = datetime.utcnow()
        existing.produced_by_type = produced_by_type
        existing.produced_by_agent_id = produced_by_agent_id
        existing.produced_by_user_id = produced_by_user_id
        obj = existing
    else:
        obj = ExchangeObject(
            company_id=company_id,
            object_type=object_type,
            external_id=external_id,
            payload=payload,
            produced_by_type=produced_by_type,
            produced_by_agent_id=produced_by_agent_id,
            produced_by_user_id=produced_by_user_id,
        )
        db.add(obj)

    db.commit()
    db.refresh(obj)

    await _notify_consumers(db, company_id, object_type, obj, exclude_agent_id=produced_by_agent_id)
    return obj


async def _notify_consumers(
    db: Session, company_id: str, object_type: str, obj: ExchangeObject, exclude_agent_id: str | None
):
    """
    Pousse une notification aux agents actifs du tenant qui déclarent
    consommer ce type d'objet, à l'exception de l'agent producteur
    lui-même (pour éviter les boucles).
    """
    subscriptions = db.query(AgentSubscription).filter(
        AgentSubscription.company_id == company_id,
        AgentSubscription.status == SubscriptionStatus.ACTIVE,
    ).all()

    for sub in subscriptions:
        agent: Agent = sub.agent
        if agent.id == exclude_agent_id:
            continue
        if object_type not in (agent.consumes or []):
            continue

        try:
            await call_agent(
                db, agent, agent.exchange_notify_endpoint,
                tenant_api_key=sub.tenant_api_key,
                company_id=company_id,
                json_body={
                    "object_type": object_type,
                    "external_id": obj.external_id,
                    "version": obj.version,
                    "payload": obj.payload,
                },
            )
        except AgentContractViolation:
            # Un agent consommateur indisponible ne doit jamais bloquer
            # la publication de l'objet pour les autres. À journaliser
            # en production (table de dead-letter / retry).
            continue
