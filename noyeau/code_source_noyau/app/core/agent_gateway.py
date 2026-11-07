"""
Agent Gateway
=============
Le noyau ne fait JAMAIS confiance directement à un agent tiers. Toute
communication passe par cette passerelle qui :
  1. Injecte le contexte tenant (company_id, tenant_api_key) de façon fiable.
  2. Applique un timeout et un format de réponse standard (enveloppe).
  3. Valide que la réponse de l'agent respecte le contrat (schéma attendu).
  4. Journalise chaque appel pour l'audit.

C'est ce module qui garantit qu'un agent buggé ou malveillant développé par
un programmeur externe ne peut pas casser le reste de la plateforme ni
accéder aux données d'un autre tenant.
"""
import httpx
from datetime import datetime
from sqlalchemy.orm import Session

from ..models import Agent, AgentSubscription, AgentEventLog

AGENT_CALL_TIMEOUT_SECONDS = 10


class AgentContractViolation(Exception):
    """Levée quand un agent ne respecte pas l'enveloppe de réponse standard."""
    pass


def _validate_envelope(payload: dict):
    """
    Toute réponse d'agent DOIT respecter :
    { "status": "ok" | "error", "data": {...} | null, "error": str | null }
    """
    if not isinstance(payload, dict):
        raise AgentContractViolation("La réponse de l'agent n'est pas un objet JSON.")
    if "status" not in payload:
        raise AgentContractViolation("Champ 'status' manquant dans la réponse de l'agent.")
    if payload["status"] not in ("ok", "error"):
        raise AgentContractViolation("Champ 'status' invalide (doit être 'ok' ou 'error').")


async def call_agent(
    db: Session,
    agent: Agent,
    endpoint_path: str,
    method: str = "POST",
    tenant_api_key: str | None = None,
    company_id: str | None = None,
    json_body: dict | None = None,
) -> dict:
    url = agent.base_url.rstrip("/") + "/" + endpoint_path.lstrip("/")

    headers = {
        "X-Platform-Signature": "core-gateway",  # remplacé par une vraie signature HMAC en prod
        "Content-Type": "application/json",
    }
    if tenant_api_key:
        headers["Authorization"] = f"Bearer {tenant_api_key}"
    if company_id:
        headers["X-Tenant-Id"] = company_id

    async with httpx.AsyncClient(timeout=AGENT_CALL_TIMEOUT_SECONDS) as client:
        try:
            response = await client.request(method, url, headers=headers, json=json_body or {})
            response.raise_for_status()
            payload = response.json()
            _validate_envelope(payload)
            return payload
        except httpx.TimeoutException:
            raise AgentContractViolation(f"Timeout : l'agent '{agent.slug}' n'a pas répondu à temps.")
        except httpx.HTTPStatusError as e:
            raise AgentContractViolation(f"L'agent '{agent.slug}' a renvoyé une erreur HTTP {e.response.status_code}.")
        except ValueError:
            raise AgentContractViolation(f"L'agent '{agent.slug}' n'a pas renvoyé de JSON valide.")


async def activate_agent_for_tenant(db: Session, subscription: AgentSubscription):
    agent = subscription.agent
    payload = await call_agent(
        db, agent, agent.activate_endpoint,
        tenant_api_key=subscription.tenant_api_key,
        company_id=subscription.company_id,
        json_body={"config": subscription.config or {}},
    )
    return payload


async def deactivate_agent_for_tenant(db: Session, subscription: AgentSubscription):
    agent = subscription.agent
    payload = await call_agent(
        db, agent, agent.deactivate_endpoint,
        tenant_api_key=subscription.tenant_api_key,
        company_id=subscription.company_id,
    )
    return payload


def record_inbound_event(db: Session, agent_id: str, company_id: str, event: dict):
    """
    Point d'entrée unique où TOUS les agents doivent pousser leurs alertes.
    Voir /webhooks/agent-events dans routers/webhooks.py
    """
    log = AgentEventLog(
        agent_id=agent_id,
        company_id=company_id,
        severity=event.get("severity", "info"),
        event_type=event.get("event_type", "unknown"),
        payload=event.get("data", {}),
        received_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    return log
