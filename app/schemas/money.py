from typing import Annotated

from pydantic import BaseModel, PlainSerializer, StringConstraints, WithJsonSchema
from pydantic.types import Strict

POSITIVE_MINOR_UNITS_PATTERN = r"^[1-9][0-9]{0,17}$"
CURRENCY_CODE_PATTERN = r"^[A-Z]{3}$"

PositiveMinorUnits = Annotated[str, StringConstraints(pattern=POSITIVE_MINOR_UNITS_PATTERN)]

MinorUnits = Annotated[
    int,
    Strict(),
    PlainSerializer(str, return_type=str),
    WithJsonSchema({"type": "string", "pattern": "^-?[0-9]+$", "examples": ["-5000"]}),
]

CurrencyCode = Annotated[str, StringConstraints(pattern=CURRENCY_CODE_PATTERN)]


class Money(BaseModel):
    amount: MinorUnits
    currency: CurrencyCode
