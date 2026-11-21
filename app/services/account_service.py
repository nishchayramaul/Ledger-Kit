from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.error import AccountNotFound, DuplicateAccountCode, DuplicateExternalRef
from app.models.account import Account
from app.repositories.account_repository import find_account_by_id, insert_account
from app.schemas.account import AccountCreate


def create_account(db: Session, tenant_id: UUID, account: AccountCreate) -> Account:
    try:
        created = insert_account(db, tenant_id, account)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        if "uq_accounts_tenant_code" in str(error.orig):
            raise DuplicateAccountCode(f"Account code {account.code} already exists") from error
        if "uq_accounts_tenant_external_ref" in str(error.orig):
            raise DuplicateExternalRef(
                f"External reference {account.external_ref} already exists"
            ) from error
        raise
    return created


def get_account(db: Session, tenant_id: UUID, account_id: UUID) -> Account:
    account = find_account_by_id(db, tenant_id, account_id)
    if account is None:
        raise AccountNotFound(f"Account {account_id} not found")
    return account
