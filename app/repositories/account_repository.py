from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.schemas.account import AccountCreate


def insert_account(db: Session, tenant_id: UUID, account: AccountCreate) -> Account:
    statement = (
        insert(Account)
        .values(
            tenant_id=tenant_id,
            code=account.code,
            name=account.name,
            type=account.type.value,
            currency=account.currency,
            overdraft_policy=account.overdraft_policy.value,
            overdraft_limit_minor=int(account.overdraft_limit) if account.overdraft_limit else None,
            external_ref=account.external_ref,
        )
        .returning(Account)
    )
    return db.scalars(statement).one()


def find_account_by_id(db: Session, tenant_id: UUID, account_id: UUID) -> Account | None:
    statement = select(Account).where(Account.tenant_id == tenant_id, Account.id == account_id)
    return db.scalars(statement).one_or_none()


def find_accounts_by_ids(db: Session, tenant_id: UUID, account_ids: set[UUID]) -> list[Account]:
    statement = select(Account).where(Account.tenant_id == tenant_id, Account.id.in_(account_ids))
    return list(db.scalars(statement))
