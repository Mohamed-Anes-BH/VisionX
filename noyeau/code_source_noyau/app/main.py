from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import engine
from .models import Base
from .routers import auth, admin, companies, agents, subscriptions, webhooks, exchange, pages

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Noyau de la plateforme d'agents",
    description=(
        "Noyau commun aux trois filieres du mini-projet (cybersecurite, "
        "automatisation metier, IoT) : inscription des entreprises, catalogue "
        "et souscription aux agents, passerelle d'integration, bus d'echange "
        "de donnees inter-agents, administration."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routes API (JSON), utilisees par les agents et par les pages web ci-dessous
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(companies.router)
app.include_router(agents.router)
app.include_router(subscriptions.router)
app.include_router(webhooks.router)
app.include_router(exchange.router)

# Pages web (HTML), utilisees par les entreprises et l'administrateur
app.include_router(pages.router)


@app.get("/healthz")
def health_check():
    return {"status": "ok"}
