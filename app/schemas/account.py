from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationInfo,
    field_validator,
)

from app.core.config import get_settings
from app.models.enums import AccountType, NormalBalance, OverdraftPolicy
from app.schemas.money import CurrencyCode, MinorUnits, PositiveMinorUnits

ACCOUNT_CODE_PATTERN = r"^[A-Z][A-Z0-9_]*$"


class AccountCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    code: Annotated[str, StringConstraints(pattern=ACCOUNT_CODE_PATTERN, max_length=64)]
    name: Annotated[str, StringConstraints(min_length=1, max_length=200)]
    type: AccountType
    currency: CurrencyCode
    overdraft_policy: OverdraftPolicy = OverdraftPolicy.DISALLOW
    overdraft_limit: PositiveMinorUnits | None = Field(default=None, validate_default=True)
    external_ref: Annotated[str, StringConstraints(min_length=1, max_length=128)] | None = None

    # only currencies listed in APP_SUPPORTED_CURRENCIES can be used
    @field_validator("currency")
    @classmethod
    def check_currency_is_supported(cls, currency: str) -> str:
        supported = get_settings().app_supported_currencies
        if currency not in supported:
            raise ValueError(f"unsupported currency, use one of {', '.join(supported)}")
        return currency

    # an overdraft limit is required for the 'limit' policy and forbidden for the others
    @field_validator("overdraft_limit")
    @classmethod
    def check_overdraft_limit_matches_policy(
        cls, limit: str | None, info: ValidationInfo
    ) -> str | None:
        policy = info.data.get("overdraft_policy")
        if policy is None:
            return limit
        if policy == OverdraftPolicy.LIMIT and limit is None:
            raise ValueError("required when overdraft_policy is 'limit'")
        if policy != OverdraftPolicy.LIMIT and limit is not None:
            raise ValueError("only allowed when overdraft_policy is 'limit'")
        return limit


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    type: AccountType
    currency: str
    normal_balance: NormalBalance
    overdraft_policy: OverdraftPolicy
    overdraft_limit: MinorUnits | None = Field(validation_alias="overdraft_limit_minor")
    external_ref: str | None
    created_at: datetime
    updated_at: datetime
