"""
Endpoints réservés au(x) administrateur(s) de la plateforme (Role.PLATFORM_ADMIN).
C'est le back-office : validation des agents soumis par les programmeurs,
gestion des entreprises, supervision globale.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Agent, AgentStatus, Company, AgentEventLog, Role
from ..core.security import require_role

router = APIRouter(prefix="/admin", tags=["Admin Plateforme"])


@router.get("/companies")
def list_companies(db: Session = Depends(get_db), _=Depends(require_role(Role.PLATFORM_ADMIN))):
    return db.query(Company).all()


@router.patch("/companies/{company_id}/suspend")
def suspend_company(company_id: str, db: Session = Depends(get_db), _=Depends(require_role(Role.PLATFORM_ADMIN))):
    company = db.query(Company).get(company_id)
    if not company:
        raise HTTPException(404, "Entreprise introuvable")
    company.is_active = False
    db.commit()
    return {"message": "Entreprise suspendue"}


@router.get("/agents")
def list_all_agents(db: Session = Depends(get_db), _=Depends(require_role(Role.PLATFORM_ADMIN))):
    """Vue globale de tous les agents, quel que soit leur statut (draft, in_review, published...)."""
    return db.query(Agent).all()


@router.get("/agents/pending-review")
def list_pending_agents(db: Session = Depends(get_db), _=Depends(require_role(Role.PLATFORM_ADMIN))):
    """
    File d'attente des agents soumis par les programmeurs externes et en attente
    de certification manuelle avant publication sur le catalogue.
    """
    return db.query(Agent).filter(Agent.status == AgentStatus.IN_REVIEW).all()


@router.post("/agents/{agent_id}/certify")
def certify_agent(agent_id: str, db: Session = Depends(get_db), _=Depends(require_role(Role.PLATFORM_ADMIN))):
    """
    Passe un agent de IN_REVIEW à CERTIFIED après vérification manuelle/automatisée
    du respect du contrat d'intégration (voir AGENT_INTEGRATION_CONTRACT.docx,
    section "Checklist de certification").
    """
    agent = db.query(Agent).get(agent_id)
    if not agent:
        raise HTTPException(404, "Agent introuvable")
    agent.status = AgentStatus.CERTIFIED
    db.commit()
    return {"message": f"Agent '{agent.name}' certifié. Il peut maintenant être publié."}


@router.post("/agents/{agent_id}/publish")
def publish_agent(agent_id: str, db: Session = Depends(get_db), _=Depends(require_role(Role.PLATFORM_ADMIN))):
    agent = db.query(Agent).get(agent_id)
    if not agent:
        raise HTTPException(404, "Agent introuvable")
    if agent.status != AgentStatus.CERTIFIED:
        raise HTTPException(400, "L'agent doit être certifié avant publication")
    agent.status = AgentStatus.PUBLISHED
    db.commit()
    return {"message": f"Agent '{agent.name}' publié sur le catalogue"}


@router.post("/agents/{agent_id}/suspend")
def suspend_agent(agent_id: str, db: Session = Depends(get_db), _=Depends(require_role(Role.PLATFORM_ADMIN))):
    """Retrait d'urgence d'un agent (ex: faille de sécurité découverte)."""
    agent = db.query(Agent).get(agent_id)
    if not agent:
        raise HTTPException(404, "Agent introuvable")
    agent.status = AgentStatus.SUSPENDED
    db.commit()
    return {"message": f"Agent '{agent.name}' suspendu"}


@router.get("/events")
def global_event_feed(
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_role(Role.PLATFORM_ADMIN)),
):
    """Flux global de tous les événements remontés par tous les agents, tous tenants confondus."""
    return db.query(AgentEventLog).order_by(AgentEventLog.received_at.desc()).limit(limit).all()
