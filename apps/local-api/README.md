# Local API (FastAPI sidecar)

Runs locally alongside the desktop app, backed by SQLite. Source of truth when offline.

## Architecture

Hexagonal (ports & adapters), fully typed:

```
cadence_local_api/
├── domain/          # ports (ABCs) — no framework dependency
├── application/     # use cases, orchestrate domain ports
├── infrastructure/  # adapters (SQLite, ...)
├── api/             # FastAPI routes + dependency wiring
└── app.py           # composition root (FastAPI app factory)
```

## Tooling

- [uv](https://docs.astral.sh/uv/) for dependencies and running the app
- [ty](https://github.com/astral-sh/ty) for static type checking

## Run

```
uv run uvicorn main:app --port 8756
```

## Type check

```
uv run ty check
```
