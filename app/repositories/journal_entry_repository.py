from uuid import UUID

from sqlalchemy.orm import Session

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
                account_id=posting.account_id,
                direction=posting.direction.value,
                amount_minor=int(posting.amount),
                currency=posting.currency,
            )
            for posting in entry.postings
        ],
    )
    db.add(journal_entry)
    db.flush()
    return journal_entry
