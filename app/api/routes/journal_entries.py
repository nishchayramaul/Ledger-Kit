from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_tenant_id
from app.db.session import get_db
from app.models.journal_entry import JournalEntry
from app.schemas.journal_entry import EntryResponse, JournalEntryCreate
from app.services.journal_entry_service import create_journal_entry

router = APIRouter(prefix="/api/v1/entries", tags=["journal entries"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=EntryResponse)
def post_entry(
    entry: JournalEntryCreate,
    db: Annotated[Session, Depends(get_db)],
    tenant_id: Annotated[UUID, Depends(get_current_tenant_id)],
) -> JournalEntry:
    return create_journal_entry(db, tenant_id, entry)
