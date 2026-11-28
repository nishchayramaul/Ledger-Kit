from datetime import datetime
from typing import Any
from uuid import UUID

from sqlakeyset import select_page
from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.models.journal_entry import JournalEntry, Posting
from app.schemas.journal_entry import JournalEntryCreate


def insert_journal_entry(db: Session, tenant_id: UUID, entry: JournalEntryCreate) -> JournalEntry:
    journal_entry = JournalEntry(
        tenant_id=tenant_id,
        description=entry.description,
        external_ref=entry.external_ref,
        effective_at=entry.effective_at,
        postings=[
            Posting(
                tenant_id=tenant_id,
                line_number=line_number,
                account_id=posting.account_id,
                direction=posting.direction.value,
                amount_minor=int(posting.amount),
                currency=posting.currency,
            )
            for line_number, posting in enumerate(entry.postings, start=1)
        ],
    )
    db.add(journal_entry)
    db.flush()
    return journal_entry


def find_journal_entry_by_id(db: Session, tenant_id: UUID, entry_id: UUID) -> JournalEntry | None:
    statement = (
        select(JournalEntry)
        .options(selectinload(JournalEntry.postings))
        .where(JournalEntry.tenant_id == tenant_id, JournalEntry.id == entry_id)
    )
    return db.scalars(statement).one_or_none()


def build_journal_entry_search(
    tenant_id: UUID,
    account_id: UUID | None,
    external_ref: str | None,
    effective_from: datetime | None,
    effective_to: datetime | None,
) -> Select[Any]:
    statement = (
        select(JournalEntry)
        .options(selectinload(JournalEntry.postings))
        .where(JournalEntry.tenant_id == tenant_id)
        .order_by(JournalEntry.effective_at.desc(), JournalEntry.id.desc())
    )
    if account_id is not None:
        statement = statement.where(JournalEntry.postings.any(Posting.account_id == account_id))
    if external_ref is not None:
        statement = statement.where(JournalEntry.external_ref == external_ref)
    if effective_from is not None:
        statement = statement.where(JournalEntry.effective_at >= effective_from)
    if effective_to is not None:
        statement = statement.where(JournalEntry.effective_at < effective_to)
    return statement


# returns one page of entries and the cursor for the next page (None on the last page)
def find_journal_entries_page(
    db: Session, statement: Select[Any], limit: int, cursor: str | None
) -> tuple[list[JournalEntry], str | None]:
    page = select_page(db, statement, per_page=limit, page=cursor)
    next_cursor = page.paging.bookmark_next if page.paging.has_next else None
    return [row[0] for row in page], next_cursor
