import re
from collections.abc import Iterator

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

    assert re.fullmatch(r"req_[0-9a-f]{32}", first)
    assert first != second


def test_reuses_request_id_sent_by_client() -> None:
    response = build_client().get("/health", headers={REQUEST_ID_HEADER: "paylite-881"})

    assert response.headers[REQUEST_ID_HEADER] == "paylite-881"
