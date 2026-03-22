"""End-to-end tests for route handlers against a real database."""

from collections.abc import Iterator

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from db import get_session
from main import app


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    """Provide a TestClient wired to a clean test database session."""

    def override_get_session() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_follow_link_redirects(client: TestClient) -> None:
    """Redirects when a matching slug exists."""
    client.post("/links", json={"slug": "comp423", "target": "https://comp423-26s.github.io"})

    response = client.get("/comp423", follow_redirects=False)

    assert response.status_code is status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == "https://comp423-26s.github.io"


@pytest.mark.integration
def test_follow_link_returns_404(client: TestClient) -> None:
    """Returns 404 when the slug is missing."""
    response = client.get("/missing", follow_redirects=False)

    assert response.status_code is status.HTTP_404_NOT_FOUND
    assert response.text == "Not Found"


@pytest.mark.integration
def test_create_and_list_links_e2e(client: TestClient) -> None:
    """Creates a link and then lists it through the public API."""
    create_response = client.post(
        "/links",
        json={
            "slug": "comp423",
            "target": "https://github.com/comp423-26s",
        },
    )
    list_response = client.get("/links")

    assert create_response.status_code is status.HTTP_200_OK
    assert create_response.json() == {
        "slug": "comp423",
        "target": "https://github.com/comp423-26s",
        "hits": 0,
    }
    assert list_response.status_code is status.HTTP_200_OK
    assert list_response.json() == [
        {
            "slug": "comp423",
            "target": "https://github.com/comp423-26s",
            "hits": 0,
        }
    ]
