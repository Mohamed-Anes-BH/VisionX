from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, Numeric, String, Integer, Text, ForeignKey, UniqueConstraint, CheckConstraint, Index

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

class Base(DeclarativeBase):
    pass
