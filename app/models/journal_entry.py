from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CHAR,
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "external_ref", name="uq_journal_entries_tenant_external_ref"
        ),
        Index("ix_journal_entries_tenant_effective_at_id", "tenant_id", "effective_at", "id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    description: Mapped[str] = mapped_column(String(500))
    external_ref: Mapped[str | None] = mapped_column(String(128))
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    postings: Mapped[list["Posting"]] = relationship(order_by="Posting.line_number")


class Posting(Base):
    __tablename__ = "postings"
    __table_args__ = (
        UniqueConstraint("entry_id", "line_number", name="uq_postings_entry_line_number"),
        Index("ix_postings_entry_id", "entry_id"),
        Index("ix_postings_account_id", "account_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    entry_id: Mapped[UUID] = mapped_column(ForeignKey("journal_entries.id"))
    line_number: Mapped[int] = mapped_column(SmallInteger)
    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"))
    direction: Mapped[str] = mapped_column(Text)
    amount_minor: Mapped[int] = mapped_column(BigInteger)
    currency: Mapped[str] = mapped_column(CHAR(3))
