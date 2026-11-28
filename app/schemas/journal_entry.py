from typing import Annotated
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StringConstraints

from app.models.enums import NormalBalance
from app.schemas.money import CurrencyCode, MinorUnits, PositiveMinorUnits

MIN_POSTINGS_PER_ENTRY = 2


class PostingCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: UUID
    direction: NormalBalance
    amount: PositiveMinorUnits
    currency: CurrencyCode


class JournalEntryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    description: Annotated[str, StringConstraints(min_length=1, max_length=500)]
    external_ref: Annotated[str, StringConstraints(min_length=1, max_length=128)] | None = None
    effective_at: AwareDatetime
    postings: list[PostingCreate] = Field(min_length=MIN_POSTINGS_PER_ENTRY)


class PostingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    line_number: int
    account_id: UUID
    direction: NormalBalance
    amount: MinorUnits = Field(validation_alias="amount_minor")
    currency: str


class EntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    description: str
    external_ref: str | None
    effective_at: AwareDatetime
    recorded_at: AwareDatetime
    postings: list[PostingResponse]


class EntryPage(BaseModel):
    data: list[EntryResponse]
    next_cursor: str | None
