from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, utc_now

class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="tenant_admin")
    tenant_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True)
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now)

    __table_args__ = (
        CheckConstraint("role IN ('superadmin', 'tenant_admin')", name="chk_admin_role"),
    )

class AdminSession(Base):
    __tablename__ = "admin_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    token_hash: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    csrf_token_hash: Mapped[str] = mapped_column(String, nullable=False)
    admin_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("admin_users.id", ondelete="CASCADE"), nullable=False)
    tenant_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    revoked: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    expires_at: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now)

    __table_args__ = (
        Index("idx_admin_sessions_token", "token_hash", "revoked", "expires_at"),
    )
