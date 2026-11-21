import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.main import create_app
from tests.conftest import TEST_TENANT_ID

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# integration tests need a dedicated database; they wipe tables, so never point this at real data
@pytest.fixture(scope="session")
def migrated_database() -> None:
    test_database_url = os.environ.get("TEST_DATABASE_URL")
    if not test_database_url:
        if os.environ.get("CI"):
            pytest.fail("TEST_DATABASE_URL must be set in CI")
        pytest.skip("TEST_DATABASE_URL is not set")
    if test_database_url == dotenv_values(PROJECT_ROOT / ".env").get("APP_DB_URL"):
        pytest.fail("TEST_DATABASE_URL must not be the database from .env")

    alembic_config = Config(str(PROJECT_ROOT / "alembic.ini"))
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")
    with SessionLocal() as session:
        session.execute(
            text("INSERT INTO tenants (id, name) VALUES (:id, 'Test tenant')"),
            {"id": TEST_TENANT_ID},
        )
        session.commit()


@pytest.fixture
def db_session(migrated_database: None) -> Iterator[Session]:
    with SessionLocal() as session:
        session.execute(text("TRUNCATE postings, journal_entries, accounts"))
        session.execute(text("DELETE FROM tenants WHERE id <> :id"), {"id": TEST_TENANT_ID})
        session.commit()
        yield session


@pytest.fixture
def client(db_session: Session) -> TestClient:
    return TestClient(create_app())
