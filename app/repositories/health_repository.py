from sqlalchemy import text
from sqlalchemy.orm import Session


def ping_database(db: Session, timeout_ms: int) -> None:
    db.execute(
        text("SELECT set_config('statement_timeout', :timeout, true)"),
        {"timeout": str(timeout_ms)},
    )
    db.execute(text("SELECT 1"))
