from fastapi import APIRouter, Depends,Response
from sqlalchemy.orm import Session

from app.schemas.journal_entry import JournalEntryCreate
from app.db.session import get_db

router = APIRouter(
    tags=["Journal Entries"],
    prefix = 'api/v1'
)


@router.post("/entries", status_code=201 , response_model=dict)
async  def post_entries(entry: JournalEntryCreate,
                        db: Session = Depends(get_db),
                        response: Response,
                        tenant_id : Depends(get_current_tenant_id)):
