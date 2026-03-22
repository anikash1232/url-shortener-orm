"""Link service utilities."""

from sqlmodel import Session, select

from entities.link import Link
from models.link import LinkModel


class LinkService:
    """Business logic around shortened links."""

    def __init__(self, session: Session):
        self._session = session

    def list_links(self) -> list[LinkModel]:
        """Return a list of all stored links."""
        links = self._session.exec(select(Link)).all()
        return [
            LinkModel(slug=lnk.slug, target=lnk.target, hits=lnk.hits) for lnk in links
        ]

    def get(self, slug: str) -> LinkModel | None:
        """Retrieve a link by slug and increment its hit counter."""
        link = self._session.get(Link, slug)
        if link is None:
            return None
        link.hits += 1
        self._session.add(link)
        self._session.commit()
        self._session.refresh(link)
        return LinkModel(slug=link.slug, target=link.target, hits=link.hits)

    def create(self, slug: str, target: str) -> LinkModel:
        """Create and persist a new shortened link.

        Raises:
            ValueError: If the provided slug is already taken.
        """
        existing = self._session.get(Link, slug)
        if existing is not None:
            raise ValueError(f"Slug `{slug}` already taken.")
        link = Link(slug=slug, target=target)
        self._session.add(link)
        self._session.commit()
        self._session.refresh(link)
        return LinkModel(slug=link.slug, target=link.target, hits=link.hits)
