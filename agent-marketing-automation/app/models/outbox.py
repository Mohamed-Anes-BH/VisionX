from typing import Optional
from sqlalchemy import String, Integer, Text, ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, utc_now

class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="PENDING")
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    locked_until: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    next_retry_at: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now)
    published_at: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    __table_args__ = (
        CheckConstraint("status IN ('PENDING', 'PROCESSING', 'PUBLISHED', 'FAILED')", name="chk_outbox_status"),
        Index("idx_outbox_queue", "status", "locked_until", "next_retry_at"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="outbox_events")

class EmailSuppression(Base):
    __tablename__ = "email_suppressions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now)

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_suppressions_tenant_email"),
        CheckConstraint("reason IN ('opt_out', 'hard_bounce', 'complaint', 'manual')", name="chk_suppression_reason"),
        Index("idx_suppressions_check", "tenant_id", "email"),
    )

class TenantPurgeAudit(Base):
    __tablename__ = "tenant_purge_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_hash: Mapped[str] = mapped_column(String, nullable=False)
    purged_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now)
    records_deleted: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    executed_by: Mapped[str] = mapped_column(String, nullable=False)
