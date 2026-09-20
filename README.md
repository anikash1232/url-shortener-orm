# URL Shortener

A URL shortening service in Python — FastAPI routes over an ORM-backed store, wired
together with dependency injection.

## What it does

Create a short link, list existing links, and follow a short code through to its
destination. Links persist in a relational database through an ORM layer rather than being
held in memory.

```
POST /links          create a shortened link
GET  /links          list all links
GET  /{code}         follow a short code to its target
```

## Architecture

```
main.py                   FastAPI application
db.py                     engine and session management
models/link.py            LinkModel - the ORM model and API schema
routes/router.py          HTTP endpoints
services/link_service.py  business logic
services/link_service_di.py  the injectable dependency
util/reset_db.py          schema teardown and recreation for development
```

Routes declare what they need rather than constructing it:

```python
def read_links(link_svc: LinkServiceDI) -> list[LinkModel]:
```

`LinkServiceDI` is an annotated dependency type, so FastAPI resolves and supplies the
service at request time. The route never imports a database session or instantiates a
service — which is what makes the handlers testable in isolation, with a substitute service
injected in place of the real one.

Separating `routes` from `services` from `models` means the HTTP layer holds no business
logic and the service layer knows nothing about HTTP.

## Running it

```bash
uv sync
uv run python -m src.util.reset_db
uv run fastapi dev src/main.py
```

Interactive API docs at `http://localhost:8000/docs`.
