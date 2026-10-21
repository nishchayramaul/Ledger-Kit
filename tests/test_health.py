from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.core.config import Settings
from app.db.session import get_db
from app.main import create_app


class FakeSession:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.statements: list[str] = []

    def execute(self, statement: Any, params: Any = None) -> None:
        if self.error is not None:
            raise self.error
        self.statements.append(str(statement))


def build_client(session: FakeSession) -> TestClient:
    app = create_app()

    def override_get_db() -> Iterator[FakeSession]:
        yield session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_health_returns_ok_when_database_answers() -> None:
    session = FakeSession()

    response = build_client(session).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "ok"}
    assert session.statements[-1] == "SELECT 1"


def test_health_returns_503_when_database_is_unreachable() -> None:
    error = OperationalError("SELECT 1", {}, Exception("connection refused"))

    response = build_client(FakeSession(error=error)).get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "db": "unreachable"}


def test_health_is_not_served_under_api_prefix() -> None:
    response = build_client(FakeSession()).get("/api/v1/health")

    assert response.status_code == 404


@pytest.mark.parametrize(
    "raw_url",
    [
        "postgresql://u:p@db.example.com/ledger",
        "postgres://u:p@db.example.com/ledger",
        "postgresql+psycopg://u:p@db.example.com/ledger",
    ],
)
def test_plain_postgres_urls_use_psycopg_driver(raw_url: str) -> None:
    settings = Settings(app_env="test", app_db_url=raw_url)

    assert str(settings.app_db_url).startswith("postgresql+psycopg://")
