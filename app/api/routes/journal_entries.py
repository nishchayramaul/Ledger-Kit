from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from pydantic import AwareDatetime
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_tenant_id
from app.db.session import get_db
from app.models.journal_entry import JournalEntry
from app.schemas.journal_entry import EntryPage, EntryResponse, JournalEntryCreate
from app.services.journal_entry_service import (
    create_journal_entry,
    get_journal_entry,
    search_journal_entries,
)

router = APIRouter(prefix="/api/v1/entries", tags=["journal entries"])

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100


@router.post("", status_code=status.HTTP_201_CREATED, response_model=EntryResponse)
def post_entry(
    entry: JournalEntryCreate,
    db: Annotated[Session, Depends(get_db)],
    tenant_id: Annotated[UUID, Depends(get_current_tenant_id)],
) -> JournalEntry:
    return create_journal_entry(db, tenant_id, entry)


@router.get("/{entry_id}", response_model=EntryResponse)
def get_entry_by_id(
    entry_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    tenant_id: Annotated[UUID, Depends(get_current_tenant_id)],
) -> JournalEntry:
    return get_journal_entry(db, tenant_id, entry_id)


@router.get("", response_model=EntryPage)
def list_entries(
    db: Annotated[Session, Depends(get_db)],
    tenant_id: Annotated[UUID, Depends(get_current_tenant_id)],
    account_id: UUID | None = None,
    external_ref: Annotated[str | None, Query(max_length=128)] = None,
    effective_from: Annotated[AwareDatetime | None, Query(alias="from")] = None,
    effective_to: Annotated[AwareDatetime | None, Query(alias="to")] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    cursor: str | None = None,
) -> dict[str, object]:
    entries, next_cursor = search_journal_entries(
        db, tenant_id, account_id, external_ref, effective_from, effective_to, limit, cursor
    )
    return {"data": entries, "next_cursor": next_cursor}
