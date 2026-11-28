from typing import Any

from fastapi_problem.error import (
    ConflictProblem,
    NotFoundProblem,
    ServerProblem,
    UnprocessableProblem,
)


# replaces the message of any unexpected exception so internals never reach the client
class UnexpectedError(ServerProblem):
    title = "Internal Server Error"

    def __init__(self, detail: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            "An unexpected error occurred. Quote the request id when reporting it.", **kwargs
        )


class TenantNotConfigured(ServerProblem):
    status = 503
    title = "Tenant not configured"


class AccountNotFound(NotFoundProblem):
    title = "Account not found"


class DuplicateAccountCode(ConflictProblem):
    title = "Account code already exists"


class DuplicateExternalRef(ConflictProblem):
    title = "External reference already exists"


class UnbalancedEntry(UnprocessableProblem):
    title = "Entry is not balanced"


class PostingAccountNotFound(UnprocessableProblem):
    title = "Posting account not found"


class PostingCurrencyMismatch(UnprocessableProblem):
    title = "Posting currency does not match its account"


class JournalEntryNotFound(NotFoundProblem):
    title = "Journal entry not found"


class InvalidCursor(UnprocessableProblem):
    title = "Invalid cursor"


class InvalidDateRange(UnprocessableProblem):
    title = "Invalid date range"
