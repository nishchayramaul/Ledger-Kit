from collections import defaultdict
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.error import PostingAccountNotFound, PostingCurrencyMismatch, UnbalancedEntry
from app.models.enums import NormalBalance
from app.models.journal_entry import JournalEntry
from app.repositories.account_repository import find_accounts_by_ids
from app.repositories.journal_entry_repository import insert_journal_entry
from app.schemas.journal_entry import JournalEntryCreate, PostingCreate


def create_journal_entry(db: Session, tenant_id: UUID, entry: JournalEntryCreate) -> JournalEntry:
    check_entry_is_balanced(entry.postings)
    check_posting_accounts(db, tenant_id, entry.postings)
    created = insert_journal_entry(db, tenant_id, entry)
    db.commit()
    return created


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
