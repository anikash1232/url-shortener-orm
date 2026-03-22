"""Integration tests for LinkService against a real PostgreSQL database."""

import pytest
from sqlmodel import Session

from models import LinkModel
from services import LinkService


@pytest.mark.integration
def test_list_links_empty(db_session: Session) -> None:
    """Returns an empty list when no links exist."""
    svc = LinkService(db_session)
    assert svc.list_links() == []


@pytest.mark.integration
def test_list_links_returns_all(db_session: Session) -> None:
    """Returns all persisted links."""
    svc = LinkService(db_session)
    svc.create("unc", "https://www.unc.edu")
    svc.create("comp423", "https://comp423-26s.github.io")

    results = svc.list_links()

    slugs = {lnk.slug for lnk in results}
    assert slugs == {"unc", "comp423"}


@pytest.mark.integration
def test_create_link_returns_model(db_session: Session) -> None:
    """Creating a link returns a LinkModel with correct fields and hits=0."""
    svc = LinkService(db_session)
    result = svc.create("comp423", "https://comp423-26s.github.io")

    assert isinstance(result, LinkModel)
    assert result.slug == "comp423"
    assert result.target == "https://comp423-26s.github.io"
    assert result.hits == 0


@pytest.mark.integration
def test_create_duplicate_slug_raises(db_session: Session) -> None:
    """Creating a link with a duplicate slug raises ValueError."""
    svc = LinkService(db_session)
    svc.create("comp423", "https://comp423-26s.github.io")

    with pytest.raises(ValueError, match="already taken"):
        svc.create("comp423", "https://other.example.com/path")


@pytest.mark.integration
def test_get_link_increments_hits(db_session: Session) -> None:
    """Getting a link increments its hit counter."""
    svc = LinkService(db_session)
    svc.create("comp423", "https://comp423-26s.github.io")

    result = svc.get("comp423")

    assert result is not None
    assert result.hits == 1

    result2 = svc.get("comp423")
    assert result2 is not None
    assert result2.hits == 2


@pytest.mark.integration
def test_get_link_not_found_returns_none(db_session: Session) -> None:
    """Getting a non-existent slug returns None."""
    svc = LinkService(db_session)
    assert svc.get("missing") is None
