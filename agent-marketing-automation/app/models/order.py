from typing import Optional, List
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, Text, ForeignKey, ForeignKeyConstraint, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, utc_now

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    numero_commande: Mapped[str] = mapped_column(String, nullable=False)
    client_email: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    montant_total_ht: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    received_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now)
    updated_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now)

    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_orders_tenant_id"),
        UniqueConstraint("tenant_id", "numero_commande", name="uq_orders_tenant_numero"),
        Index("idx_orders_lookup", "tenant_id", "numero_commande"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="orders")
    events: Mapped[List["OrderEvent"]] = relationship("OrderEvent", back_populates="order", cascade="all, delete-orphan")

class OrderEvent(Base):
    __tablename__ = "order_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    numero_commande: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default=utc_now)

    __table_args__ = (
        UniqueConstraint("tenant_id", "idempotency_key", name="uq_order_events_idemp"),
        Index("idx_order_events_history", "tenant_id", "order_id", "occurred_at"),
    )

    order: Mapped["Order"] = relationship("Order", back_populates="events")
