from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Company, User, Role
from ..core.security import hash_password, create_access_token

router = APIRouter(prefix="/companies", tags=["Entreprises"])


class CompanySignupRequest(BaseModel):
    company_name: str
    sector: str | None = None
    park_size: str | None = None  # "petit" | "moyen" | "grand"
    admin_email: EmailStr
    admin_password: str
    admin_full_name: str


@router.post("/signup")
def signup_company(payload: CompanySignupRequest, db: Session = Depends(get_db)):
    """
    Inscription d'une nouvelle entreprise cliente. Crée le tenant (Company)
    et son premier utilisateur, avec le rôle COMPANY_ADMIN.
    Aucun agent n'est activé à ce stade : l'entreprise choisira ensuite
    les agents à souscrire dans le catalogue.
    """
    company = Company(
        name=payload.company_name,
        sector=payload.sector,
        park_size=payload.park_size,
    )
    db.add(company)
    db.flush()  # récupère company.id avant le commit final

    admin_user = User(
        email=payload.admin_email,
        hashed_password=hash_password(payload.admin_password),
        full_name=payload.admin_full_name,
        role=Role.COMPANY_ADMIN,
        company_id=company.id,
    )
    db.add(admin_user)
    db.commit()

    token = create_access_token({"sub": str(admin_user.id), "role": admin_user.role.value})
    return {
        "message": "Entreprise créée avec succès",
        "company_id": str(company.id),
        "access_token": token,
    }


@router.get("/{company_id}/dashboard-summary")
def dashboard_summary(company_id: str, db: Session = Depends(get_db)):
    """Résumé pour la page d'accueil du compte entreprise : agents actifs, alertes récentes..."""
    company = db.query(Company).get(company_id)
    active_subs = [s for s in company.subscriptions if s.status.value == "active"]
    return {
        "company_name": company.name,
        "active_agents_count": len(active_subs),
        "active_agents": [s.agent.name for s in active_subs],
    }
