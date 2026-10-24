import re
from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import create_app
from app.middleware.middleware import REQUEST_ID_HEADER


class FakeSession:
    def execute(self, *args: object, **kwargs: object) -> None:
        return None


def build_client() -> TestClient:
    app = create_app()

    def override_get_db() -> Iterator[FakeSession]:
        yield FakeSession()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_generates_request_id_when_client_sends_none() -> None:
    client = build_client()

    first = client.get("/health").headers[REQUEST_ID_HEADER]
    second = client.get("/health").headers[REQUEST_ID_HEADER]

    assert re.fullmatch(r"[0-9a-f]{32}", first)
    assert first != second


def test_reuses_valid_request_id_sent_by_client() -> None:
    client_request_id = uuid4().hex

    response = build_client().get("/health", headers={REQUEST_ID_HEADER: client_request_id})

    assert response.headers[REQUEST_ID_HEADER] == client_request_id


@pytest.mark.parametrize("unsafe_id", ["<script>", "a" * 65, "paylite-881"])
def test_replaces_request_id_that_is_not_a_uuid(unsafe_id: str) -> None:
    response = build_client().get("/health", headers={REQUEST_ID_HEADER: unsafe_id})

    assert response.headers[REQUEST_ID_HEADER] != unsafe_id
