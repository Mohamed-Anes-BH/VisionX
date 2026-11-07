from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Agent, AgentStatus, Filiere

router = APIRouter(prefix="/agents", tags=["Catalogue Agents"])


class AgentManifestSubmission(BaseModel):
    """
    Donnees envoyees par une equipe etudiante pour enregistrer son agent.
    Doit correspondre au fichier agent.manifest.json decrit dans
    AGENT_INTEGRATION_CONTRACT.docx.
    """
    slug: str
    name: str
    version: str
    description: str
    filiere: Filiere
    category: str
    developer_email: str
    team_name: str | None = None
    base_url: str
    pricing_model: str = "flat_monthly"
    price: float = 0
    manifest: dict
    # Declaration de collaboration inter-agents, facultative (voir INTER_AGENT_DATA_CONTRACT.docx)
    produces: list[str] = []
    consumes: list[str] = []


@router.get("/catalog")
def public_catalog(filiere: Filiere | None = None, db: Session = Depends(get_db)):
    """Catalogue visible par les entreprises : uniquement les agents publies, filtrables par filiere."""
    query = db.query(Agent).filter(Agent.status == AgentStatus.PUBLISHED)
    if filiere:
        query = query.filter(Agent.filiere == filiere)
    return query.all()


@router.post("/submit")
def submit_agent(payload: AgentManifestSubmission, db: Session = Depends(get_db)):
    """
    Soumission d'un agent par une equipe etudiante. L'agent entre en
    statut IN_REVIEW et attend la verification de l'enseignant avant
    d'apparaitre dans le catalogue (voir /admin).
    """
    existing = db.query(Agent).filter(Agent.slug == payload.slug).first()
    if existing:
        raise HTTPException(400, "Un agent avec ce slug existe deja. Incrementez la version.")

    agent = Agent(
        slug=payload.slug,
        name=payload.name,
        version=payload.version,
        description=payload.description,
        filiere=payload.filiere,
        category=payload.category,
        developer_email=payload.developer_email,
        team_name=payload.team_name,
        base_url=payload.base_url,
        pricing_model=payload.pricing_model,
        price=payload.price,
        manifest=payload.manifest,
        produces=payload.produces,
        consumes=payload.consumes,
        status=AgentStatus.IN_REVIEW,
    )
    db.add(agent)
    db.commit()
    return {"message": "Agent soumis pour revue", "agent_id": str(agent.id), "status": agent.status.value}
