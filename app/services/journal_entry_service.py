from collections import defaultdict
from datetime import datetime
from uuid import UUID

from sqlakeyset import BadBookmark
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.error import (
    DuplicateExternalRef,
    InvalidCursor,
    InvalidDateRange,
    JournalEntryNotFound,
    PostingAccountNotFound,
    PostingCurrencyMismatch,
    UnbalancedEntry,
)
from app.models.enums import NormalBalance
from app.models.journal_entry import JournalEntry
from app.repositories.account_repository import find_accounts_by_ids
from app.repositories.journal_entry_repository import (
    build_journal_entry_search,
    find_journal_entries_page,
    find_journal_entry_by_id,
    insert_journal_entry,
)
from app.schemas.journal_entry import JournalEntryCreate, PostingCreate


def create_journal_entry(db: Session, tenant_id: UUID, entry: JournalEntryCreate) -> JournalEntry:
    check_entry_is_balanced(entry.postings)
    check_posting_accounts(db, tenant_id, entry.postings)
    try:
        created = insert_journal_entry(db, tenant_id, entry)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        if "uq_journal_entries_tenant_external_ref" in str(error.orig):
            raise DuplicateExternalRef(
                f"External reference {entry.external_ref} already exists"
            ) from error
        raise
    return created


def get_journal_entry(db: Session, tenant_id: UUID, entry_id: UUID) -> JournalEntry:
    entry = find_journal_entry_by_id(db, tenant_id, entry_id)
    if entry is None:
        raise JournalEntryNotFound(f"Journal entry {entry_id} not found")
    return entry


def search_journal_entries(
    db: Session,
    tenant_id: UUID,
    account_id: UUID | None,
    external_ref: str | None,
    effective_from: datetime | None,
    effective_to: datetime | None,
    limit: int,
    cursor: str | None,
) -> tuple[list[JournalEntry], str | None]:
    if effective_from and effective_to and effective_from >= effective_to:
        raise InvalidDateRange("'from' must be earlier than 'to'")
    statement = build_journal_entry_search(
        tenant_id, account_id, external_ref, effective_from, effective_to
    )
    try:
        return find_journal_entries_page(db, statement, limit, cursor)
    except BadBookmark as error:
        raise InvalidCursor("Cursor is not valid; use next_cursor from a previous page") from error


# every currency in the entry must have equal debit and credit totals
def check_entry_is_balanced(postings: list[PostingCreate]) -> None:
    totals: dict[str, dict[NormalBalance, int]] = defaultdict(
        lambda: {NormalBalance.DEBIT: 0, NormalBalance.CREDIT: 0}
    )
    for posting in postings:
        totals[posting.currency][posting.direction] += int(posting.amount)
    imbalances = [
        {
            "currency": currency,
            "debits": str(total[NormalBalance.DEBIT]),
            "credits": str(total[NormalBalance.CREDIT]),
        }
        for currency, total in totals.items()
        if total[NormalBalance.DEBIT] != total[NormalBalance.CREDIT]
    ]
    if imbalances:
        raise UnbalancedEntry("Debits must equal credits in every currency", imbalances=imbalances)


# every posting account must belong to the tenant and use the posting's currency
def check_posting_accounts(db: Session, tenant_id: UUID, postings: list[PostingCreate]) -> None:
    account_ids = {posting.account_id for posting in postings}
    accounts = {account.id: account for account in find_accounts_by_ids(db, tenant_id, account_ids)}
    missing = account_ids - accounts.keys()
    if missing:
        raise PostingAccountNotFound(
            "These accounts do not exist", account_ids=sorted(str(id_) for id_ in missing)
        )
    mismatched = sorted(
        {str(p.account_id) for p in postings if p.currency != accounts[p.account_id].currency}
    )
    if mismatched:
        raise PostingCurrencyMismatch(
            "Posting currency must match the account currency", account_ids=mismatched
        )
