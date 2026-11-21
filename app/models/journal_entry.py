from datetime import datetime
from uuid import UUID

from sqlalchemy import CHAR, BigInteger, DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    description: Mapped[str] = mapped_column(String(500))
    external_ref: Mapped[str | None] = mapped_column(String(128))
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    postings: Mapped[list["Posting"]] = relationship()


class Posting(Base):
    __tablename__ = "postings"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))
    entry_id: Mapped[UUID] = mapped_column(ForeignKey("journal_entries.id"))
    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"))
    direction: Mapped[str] = mapped_column(Text)
    amount_minor: Mapped[int] = mapped_column(BigInteger)
    currency: Mapped[str] = mapped_column(CHAR(3))
