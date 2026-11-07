"""
Pages web du noyau.

Ce fichier ne contient pas de nouvelle logique metier : il reutilise les
memes modeles et les memes fonctions de securite que les routes API
(voir routers/companies.py, routers/subscriptions.py, routers/admin.py).
Il s'agit simplement de la couche de presentation, pour que l'enseignant
et les entreprises n'aient pas a passer par l'API brute pour utiliser la
plateforme au quotidien.

Convention : une page qui echoue une verification (pas connecte, mauvais
role) redirige vers la page de connexion plutot que de renvoyer une
erreur JSON, puisque l'utilisateur est ici un humain dans un navigateur.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Company, User, Role, Agent, AgentStatus, Filiere,
    AgentSubscription, SubscriptionStatus, AgentEventLog,
)
from ..core.security import (
    hash_password, verify_password, create_access_token,
    get_user_from_cookie, generate_tenant_api_key, COOKIE_NAME,
)
from ..core.agent_gateway import activate_agent_for_tenant, AgentContractViolation

router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory="app/templates")


def set_auth_cookie(response: RedirectResponse, user: User) -> None:
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    response.set_cookie(COOKIE_NAME, token, httponly=True, max_age=60 * 60 * 8)


# ---------------------------------------------------------------------
# Accueil
# ---------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_cookie(request, db)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


# ---------------------------------------------------------------------
# Inscription d'une entreprise
# ---------------------------------------------------------------------

@router.get("/inscription", response_class=HTMLResponse)
def inscription_form(request: Request):
    return templates.TemplateResponse("inscription.html", {"request": request, "erreur": None})


@router.post("/inscription")
def inscription_submit(
    request: Request,
    company_name: str = Form(...),
    sector: str = Form(""),
    park_size: str = Form("moyen"),
    admin_full_name: str = Form(...),
    admin_email: str = Form(...),
    admin_password: str = Form(...),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.email == admin_email).first():
        return templates.TemplateResponse(
            "inscription.html",
            {"request": request, "erreur": "Cet email est deja utilise."},
            status_code=400,
        )

    company = Company(name=company_name, sector=sector, park_size=park_size)
    db.add(company)
    db.flush()

    user = User(
        email=admin_email,
        hashed_password=hash_password(admin_password),
        full_name=admin_full_name,
        role=Role.COMPANY_ADMIN,
        company_id=company.id,
    )
    db.add(user)
    db.commit()

    response = RedirectResponse("/catalogue", status_code=303)
    set_auth_cookie(response, user)
    return response


# ---------------------------------------------------------------------
# Connexion / deconnexion
# ---------------------------------------------------------------------

@router.get("/connexion", response_class=HTMLResponse)
def connexion_form(request: Request):
    return templates.TemplateResponse("connexion.html", {"request": request, "erreur": None})


@router.post("/connexion")
def connexion_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "connexion.html",
            {"request": request, "erreur": "Email ou mot de passe incorrect."},
            status_code=401,
        )

    destination = "/admin" if user.role == Role.PLATFORM_ADMIN else "/catalogue"
    response = RedirectResponse(destination, status_code=303)
    set_auth_cookie(response, user)
    return response


@router.get("/deconnexion")
def deconnexion():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response


# ---------------------------------------------------------------------
# Catalogue et souscription (cote entreprise)
# ---------------------------------------------------------------------

@router.get("/catalogue", response_class=HTMLResponse)
def catalogue(request: Request, filiere: str | None = None, db: Session = Depends(get_db)):
    user = get_user_from_cookie(request, db)
    if not user or user.role == Role.PLATFORM_ADMIN:
        return RedirectResponse("/connexion", status_code=303)

    query = db.query(Agent).filter(Agent.status == AgentStatus.PUBLISHED)
    if filiere:
        query = query.filter(Agent.filiere == filiere)
    agents = query.order_by(Agent.filiere, Agent.name).all()

    deja_souscrits = {
        s.agent_id for s in user.company.subscriptions if s.status == SubscriptionStatus.ACTIVE
    }

    return templates.TemplateResponse("catalogue.html", {
        "request": request, "user": user, "agents": agents,
        "filieres": list(Filiere), "filiere_active": filiere,
        "deja_souscrits": deja_souscrits,
    })


@router.post("/catalogue/souscrire/{agent_slug}")
async def souscrire(agent_slug: str, request: Request, db: Session = Depends(get_db)):
    user = get_user_from_cookie(request, db)
    if not user or user.role == Role.PLATFORM_ADMIN:
        return RedirectResponse("/connexion", status_code=303)

    agent = db.query(Agent).filter(Agent.slug == agent_slug, Agent.status == AgentStatus.PUBLISHED).first()
    if not agent:
        return RedirectResponse("/catalogue", status_code=303)

    subscription = AgentSubscription(
        company_id=user.company_id,
        agent_id=agent.id,
        status=SubscriptionStatus.PENDING,
        tenant_api_key=generate_tenant_api_key(),
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    try:
        await activate_agent_for_tenant(db, subscription)
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.activated_at = datetime.utcnow()
        db.commit()
    except AgentContractViolation:
        # L'agent n'a pas repondu correctement a l'activation : la
        # souscription reste visible, en erreur, dans le tableau de bord.
        subscription.status = SubscriptionStatus.SUSPENDED
        db.commit()

    return RedirectResponse("/mon-compte", status_code=303)


# ---------------------------------------------------------------------
# Tableau de bord entreprise
# ---------------------------------------------------------------------

@router.get("/mon-compte", response_class=HTMLResponse)
def mon_compte(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_cookie(request, db)
    if not user or user.role == Role.PLATFORM_ADMIN:
        return RedirectResponse("/connexion", status_code=303)

    subscriptions = db.query(AgentSubscription).filter(
        AgentSubscription.company_id == user.company_id
    ).order_by(AgentSubscription.created_at.desc()).all()

    evenements = db.query(AgentEventLog).filter(
        AgentEventLog.company_id == user.company_id
    ).order_by(AgentEventLog.received_at.desc()).limit(20).all()

    return templates.TemplateResponse("mon_compte.html", {
        "request": request, "user": user, "subscriptions": subscriptions, "evenements": evenements,
    })


# ---------------------------------------------------------------------
# Administration de la plateforme (enseignant)
# ---------------------------------------------------------------------

@router.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_cookie(request, db)
    if not user or user.role != Role.PLATFORM_ADMIN:
        return RedirectResponse("/connexion", status_code=303)

    agents = db.query(Agent).order_by(Agent.status, Agent.filiere, Agent.name).all()
    companies = db.query(Company).order_by(Company.created_at.desc()).all()
    evenements = db.query(AgentEventLog).order_by(AgentEventLog.received_at.desc()).limit(30).all()

    return templates.TemplateResponse("admin.html", {
        "request": request, "user": user, "agents": agents,
        "companies": companies, "evenements": evenements,
        "AgentStatus": AgentStatus,
    })


@router.post("/admin/agents/{agent_id}/certifier")
def admin_certifier(agent_id: str, request: Request, db: Session = Depends(get_db)):
    user = get_user_from_cookie(request, db)
    if not user or user.role != Role.PLATFORM_ADMIN:
        return RedirectResponse("/connexion", status_code=303)
    agent = db.query(Agent).get(agent_id)
    if agent:
        agent.status = AgentStatus.CERTIFIED
        db.commit()
    return RedirectResponse("/admin", status_code=303)


@router.post("/admin/agents/{agent_id}/publier")
def admin_publier(agent_id: str, request: Request, db: Session = Depends(get_db)):
    user = get_user_from_cookie(request, db)
    if not user or user.role != Role.PLATFORM_ADMIN:
        return RedirectResponse("/connexion", status_code=303)
    agent = db.query(Agent).get(agent_id)
    if agent and agent.status == AgentStatus.CERTIFIED:
        agent.status = AgentStatus.PUBLISHED
        db.commit()
    return RedirectResponse("/admin", status_code=303)


@router.post("/admin/agents/{agent_id}/suspendre")
def admin_suspendre(agent_id: str, request: Request, db: Session = Depends(get_db)):
    user = get_user_from_cookie(request, db)
    if not user or user.role != Role.PLATFORM_ADMIN:
        return RedirectResponse("/connexion", status_code=303)
    agent = db.query(Agent).get(agent_id)
    if agent:
        agent.status = AgentStatus.SUSPENDED
        db.commit()
    return RedirectResponse("/admin", status_code=303)


@router.post("/admin/companies/{company_id}/suspendre")
def admin_suspendre_entreprise(company_id: str, request: Request, db: Session = Depends(get_db)):
    user = get_user_from_cookie(request, db)
    if not user or user.role != Role.PLATFORM_ADMIN:
        return RedirectResponse("/connexion", status_code=303)
    company = db.query(Company).get(company_id)
    if company:
        company.is_active = False
        db.commit()
    return RedirectResponse("/admin", status_code=303)
