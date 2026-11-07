from typing import Optional, List
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, ForeignKey, ForeignKeyConstraint, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, utc_now

class Prospect(Base):
    __tablename__ = "prospects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    nom: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    score_raw: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    status: Mapped[str] = mapped_column(String, nullable=False, default="NEW")
    last_activity_at: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now)
    updated_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now, onupdate=utc_now)

    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_prospects_tenant_id"),
        UniqueConstraint("tenant_id", "email", name="uq_prospects_tenant_email"),
        CheckConstraint("score_raw BETWEEN 0.00 AND 100.00", name="chk_score_raw_range"),
        CheckConstraint("status IN ('NEW', 'ENGAGED', 'NURTURING', 'QUALIFIED', 'CONVERTED', 'UNSUBSCRIBED')", name="chk_prospect_status"),
        Index("idx_prospects_lookup", "tenant_id", "email"),
        Index("idx_prospects_status", "tenant_id", "status"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="prospects")
    activities: Mapped[List["Activity"]] = relationship(
        "Activity", 
        back_populates="prospect", 
        cascade="all, delete-orphan",
        primaryjoin="and_(Prospect.tenant_id==foreign(Activity.tenant_id), Prospect.id==foreign(Activity.prospect_id))"
    )

class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    prospect_id: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    points: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    idempotency_key: Mapped[str] = mapped_column(String, nullable=False)
    occurred_at: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now)

    __table_args__ = (
        UniqueConstraint("tenant_id", "idempotency_key", name="uq_activities_tenant_idemp"),
        ForeignKeyConstraint(
            ["tenant_id", "prospect_id"],
            ["prospects.tenant_id", "prospects.id"],
            name="fk_activities_prospect_composite",
            ondelete="CASCADE"
        ),
        Index("idx_activities_timeline", "tenant_id", "prospect_id", "occurred_at"),
    )

    prospect: Mapped["Prospect"] = relationship(
        "Prospect", 
        back_populates="activities",
        primaryjoin="and_(Prospect.tenant_id==Activity.tenant_id, Prospect.id==Activity.prospect_id)"
    )
