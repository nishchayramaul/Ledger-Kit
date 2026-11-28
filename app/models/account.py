from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CHAR,
    BigInteger,
    Computed,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

NORMAL_BALANCE_EXPRESSION = "CASE WHEN type IN ('asset', 'expense') THEN 'debit' ELSE 'credit' END"

# models  of accounts table to capture account information for transactions


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_accounts_tenant_code"),
        UniqueConstraint("tenant_id", "external_ref", name="uq_accounts_tenant_external_ref"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    code: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(Text)
    currency: Mapped[str] = mapped_column(CHAR(3))
    normal_balance: Mapped[str] = mapped_column(
        Text, Computed(NORMAL_BALANCE_EXPRESSION, persisted=True)
    )
    overdraft_policy: Mapped[str] = mapped_column(Text, server_default=text("'disallow'"))
    overdraft_limit_minor: Mapped[int | None] = mapped_column(BigInteger)
    external_ref: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
