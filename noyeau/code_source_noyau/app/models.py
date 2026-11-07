"""
Modeles de donnees du noyau commun.

Le noyau est partage par les trois filieres du mini-projet (cybersecurite,
automatisation metier, IoT). Chaque entreprise inscrite est un tenant
(Company), isole des autres. Un agent est developpe et deploye separement
par une equipe etudiante ; le noyau ne connait de lui que ce qui est
decrit dans son manifeste et enregistre ici.

Deux mecanismes de communication agent -> reste de la plateforme sont
disponibles, et un agent est libre de n'utiliser que celui dont il a
besoin :
  - le webhook d'alertes (AgentEventLog), pour signaler un evenement
    ponctuel (une alerte de securite, une mesure hors seuil, etc.) ;
  - le bus d'echange (ExchangeObject), pour publier ou consommer un objet
    metier partage avec un autre agent de la meme entreprise (une
    commande, un niveau de stock...). Utilise surtout en filiere
    automatisation metier, mais rien n'empeche un agent IoT de s'en
    servir s'il produit une donnee reutilisable par un autre agent.
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, Enum, Text, Integer, JSON, Numeric
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


def gen_uuid():
    return str(uuid.uuid4())


class Role(str, enum.Enum):
    PLATFORM_ADMIN = "platform_admin"   # administrateur de la plateforme (enseignant)
    COMPANY_ADMIN = "company_admin"     # administrateur d'une entreprise inscrite
    COMPANY_USER = "company_user"       # utilisateur simple d'une entreprise


class Filiere(str, enum.Enum):
    CYBERSECURITE = "cybersecurite"
    AUTOMATISATION_METIER = "automatisation_metier"
    IOT = "iot"


class SubscriptionStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class AgentStatus(str, enum.Enum):
    DRAFT = "draft"             # en cours de developpement par l'equipe
    IN_REVIEW = "in_review"     # soumis, en attente de verification par l'enseignant
    CERTIFIED = "certified"     # verifie conforme au contrat, pret a publier
    PUBLISHED = "published"     # visible et souscriptible dans le catalogue
    DEPRECATED = "deprecated"
    SUSPENDED = "suspended"     # retire temporairement (non-conformite, incident)


class Company(Base):
    """Une entreprise inscrite sur la plateforme : un tenant."""
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    siret_or_reg_number = Column(String(64), nullable=True)
    sector = Column(String(128), nullable=True)
    park_size = Column(String(32), nullable=True)  # "petit", "moyen", "grand"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="company")
    subscriptions = relationship("AgentSubscription", back_populates="company")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(Role), nullable=False, default=Role.COMPANY_USER)
    company_id = Column(UUID(as_uuid=False), ForeignKey("companies.id"), nullable=True)
    # company_id reste NULL pour un platform_admin, qui n'appartient a aucune entreprise
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="users")


class Agent(Base):
    """
    Une entree du catalogue. Chaque agent est developpe par une equipe
    etudiante, independamment du noyau, et doit respecter le contrat
    d'integration pour y figurer.
    """
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    slug = Column(String(64), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    version = Column(String(32), nullable=False, default="1.0.0")
    description = Column(Text)
    filiere = Column(Enum(Filiere), nullable=False)
    category = Column(String(64))  # categorie libre au sein de la filiere (ex: "stock", "ids", "capteur")
    developer_email = Column(String(255), nullable=False)
    team_name = Column(String(128), nullable=True)  # nom de l'equipe etudiante, pour le suivi pedagogique

    # Endpoints du contrat d'integration (voir AGENT_INTEGRATION_CONTRACT.docx)
    base_url = Column(String(512), nullable=False)
    health_endpoint = Column(String(255), default="/health")
    activate_endpoint = Column(String(255), default="/tenant/activate")
    deactivate_endpoint = Column(String(255), default="/tenant/deactivate")
    status_endpoint = Column(String(255), default="/tenant/{tenant_id}/status")
    webhook_receiver_endpoint = Column(String(255), default="/webhook")
    manifest = Column(JSON, nullable=False)  # copie du agent.manifest.json soumis

    pricing_model = Column(String(32), default="flat_monthly")
    price = Column(Numeric(10, 2), default=0)

    # Declaration de collaboration inter-agents, facultative : un agent qui
    # n'utilise que le webhook d'alertes laisse ces deux listes vides.
    produces = Column(JSON, default=list)
    consumes = Column(JSON, default=list)
    exchange_notify_endpoint = Column(String(255), default="/exchange/notify")

    status = Column(Enum(AgentStatus), default=AgentStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subscriptions = relationship("AgentSubscription", back_populates="agent")


class AgentSubscription(Base):
    """Souscription d'une entreprise a un agent du catalogue."""
    __tablename__ = "agent_subscriptions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id = Column(UUID(as_uuid=False), ForeignKey("companies.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id"), nullable=False)

    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.PENDING)
    tenant_api_key = Column(String(255), nullable=False)  # cle remise a l'agent pour ce couple (tenant, agent)
    config = Column(JSON, default=dict)
    activated_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="subscriptions")
    agent = relationship("Agent", back_populates="subscriptions")


class AgentEventLog(Base):
    """
    Journal des evenements remontes par les agents via le webhook standard
    (alertes, notifications). Utilise par l'administrateur pour la
    supervision, et par chaque entreprise pour consulter ses propres
    evenements.
    """
    __tablename__ = "agent_event_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id"), nullable=False)
    company_id = Column(UUID(as_uuid=False), ForeignKey("companies.id"), nullable=False)
    severity = Column(String(16))  # info | low | medium | high | critical
    event_type = Column(String(64))
    payload = Column(JSON)
    received_at = Column(DateTime, default=datetime.utcnow)


class ProducerType(str, enum.Enum):
    AGENT = "agent"
    HUMAN = "human"


class ExchangeObject(Base):
    """
    Un objet metier partage (commande, stock_level, mesure_capteur...)
    pour un tenant donne. Peut etre ecrit soit par un agent (via la cle
    tenant_api_key), soit par un utilisateur de l'entreprise depuis son
    tableau de bord : les deux ecrivent dans la meme table, ce qui permet
    a un agent consommateur de recevoir la donnee de facon identique
    quelle que soit son origine.
    """
    __tablename__ = "exchange_objects"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id = Column(UUID(as_uuid=False), ForeignKey("companies.id"), nullable=False)
    object_type = Column(String(64), nullable=False)
    external_id = Column(String(128), nullable=False)  # cle metier (ex: numero de commande)
    payload = Column(JSON, nullable=False)
    version = Column(Integer, default=1)

    produced_by_type = Column(Enum(ProducerType), nullable=False)
    produced_by_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id"), nullable=True)
    produced_by_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UsageRecord(Base):
    """Mesures d'usage remontees par un agent facture a l'usage (facultatif pour le mini-projet)."""
    __tablename__ = "usage_records"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    subscription_id = Column(UUID(as_uuid=False), ForeignKey("agent_subscriptions.id"), nullable=False)
    metric_name = Column(String(64))
    quantity = Column(Integer, default=0)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
