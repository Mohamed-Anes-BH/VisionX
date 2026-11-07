from typing import Optional, List
from sqlalchemy import String, Integer, Text, ForeignKey, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, utc_now

class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    html_body: Mapped[str] = mapped_column(Text, nullable=False)
    text_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now)

    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_email_templates_tenant_id"),
        UniqueConstraint("tenant_id", "name", name="uq_email_templates_tenant_name"),
    )

class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, default="marketing")
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")
    template_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("email_templates.id", ondelete="RESTRICT"), nullable=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now)

    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_campaigns_tenant_id"),
        CheckConstraint("category IN ('marketing', 'transactional')", name="chk_campaign_category"),
        CheckConstraint("status IN ('active', 'paused')", name="chk_campaign_status"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="campaigns")
    template: Mapped[Optional["EmailTemplate"]] = relationship("EmailTemplate")
    dispatches: Mapped[List["CampaignDispatch"]] = relationship("CampaignDispatch", back_populates="campaign", cascade="all, delete-orphan")

class CampaignDispatch(Base):
    __tablename__ = "campaign_dispatches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    campaign_id: Mapped[int] = mapped_column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    prospect_id: Mapped[int] = mapped_column(Integer, ForeignKey("prospects.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, default="marketing")
    idempotency_key: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="PENDING")
    skip_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now)

    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_dispatches_tenant_id"),
        UniqueConstraint("tenant_id", "idempotency_key", name="uq_dispatches_idemp"),
        CheckConstraint("category IN ('marketing', 'transactional')", name="chk_dispatch_category"),
        CheckConstraint("status IN ('PENDING', 'SENT', 'FAILED', 'SKIPPED')", name="chk_dispatch_status"),
        Index("idx_dispatches_cooldown", "tenant_id", "prospect_id", "campaign_id", "created_at"),
    )

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="dispatches")
    logs: Mapped[List["CampaignLog"]] = relationship("CampaignLog", back_populates="dispatch", cascade="all, delete-orphan")

class CampaignLog(Base):
    __tablename__ = "campaign_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    dispatch_id: Mapped[int] = mapped_column(Integer, ForeignKey("campaign_dispatches.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    message_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sent_at: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now)

    dispatch: Mapped["CampaignDispatch"] = relationship("CampaignDispatch", back_populates="logs")
