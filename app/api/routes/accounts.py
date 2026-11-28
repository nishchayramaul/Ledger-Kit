from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_tenant_id
from app.db.session import get_db
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountResponse
from app.services.account_service import create_account, get_account

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
def post_account(
    account: AccountCreate,
    db: Annotated[Session, Depends(get_db)],
    tenant_id: Annotated[UUID, Depends(get_current_tenant_id)],
) -> Account:
    return create_account(db, tenant_id, account)


@router.get("/{account_id}", response_model=AccountResponse)
def get_account_by_id(
    account_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    tenant_id: Annotated[UUID, Depends(get_current_tenant_id)],
) -> Account:
    return get_account(db, tenant_id, account_id)
