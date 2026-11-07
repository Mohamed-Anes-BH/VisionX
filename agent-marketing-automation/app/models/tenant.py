from typing import Optional, List
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, utc_now

class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")
    api_key_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now)

    __table_args__ = (
        CheckConstraint("status IN ('active', 'deactivating', 'deactivated')", name="chk_tenant_status"),
    )

    config: Mapped["TenantConfig"] = relationship("TenantConfig", back_populates="tenant", cascade="all, delete-orphan", uselist=False)
    prospects: Mapped[List["Prospect"]] = relationship("Prospect", back_populates="tenant", cascade="all, delete-orphan")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="tenant", cascade="all, delete-orphan")
    campaigns: Mapped[List["Campaign"]] = relationship("Campaign", back_populates="tenant", cascade="all, delete-orphan")
    outbox_events: Mapped[List["OutboxEvent"]] = relationship("OutboxEvent", back_populates="tenant", cascade="all, delete-orphan")

class TenantConfig(Base):
    __tablename__ = "tenant_configs"

    tenant_id: Mapped[str] = mapped_column(String, ForeignKey("tenants.id", ondelete="CASCADE"), primary_key=True)
    qualification_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=70)
    score_half_life_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    campaign_cooldown_days: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    marketing_global_cooldown_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=48)
    max_emails_weekly: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    daily_quota: Mapped[int] = mapped_column(Integer, nullable=False, default=500)

    __table_args__ = (
        CheckConstraint("qualification_threshold BETWEEN 0 AND 100", name="chk_qual_threshold"),
        CheckConstraint("score_half_life_days > 0", name="chk_half_life"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="config")
