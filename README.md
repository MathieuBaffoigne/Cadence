# Cadence

Admin toolkit for small French businesses — an offline-first desktop app that syncs to the cloud when connected.

Built as a complement to existing point-of-sale tools, not a replacement: Cadence focuses on the administrative side that POS software usually ignores.

## v1 scope

Built and validated with a real local business (a flower shop) as first user.

- **Team planning** — staff scheduling under constraints (availability, seasonal peaks like Valentine's Day or Mother's Day)
- **Invoicing & quotes** — quote-to-invoice workflow for event orders, status tracking, French legal invoice requirements
- **CSV / Excel import-export** — accounting-ready exports, client/catalog imports

Single business per deployment for v1 — no multi-tenant account management yet (see Roadmap).

## Architecture

Offline-first: the desktop app works with zero network connection, then syncs when online.

```
apps/desktop/       Tauri shell (Rust), packaged app (Windows/Mac)
apps/frontend/      Angular UI, shared by the desktop shell
apps/local-api/     FastAPI sidecar, runs locally, talks to SQLite
services/cloud-api/ FastAPI + PostgreSQL, sync endpoint, deployed on AWS
infra/terraform/    AWS infrastructure as code
```

Local SQLite is the source of truth offline. Each record carries an `updated_at`; when the app reconnects, it pushes local changes and pulls remote ones, resolving conflicts last-write-wins.

Both FastAPI services (`local-api`, `cloud-api`) follow a hexagonal architecture (ports & adapters): a framework-free `domain` layer (ABCs as ports), `application` use cases, and `infrastructure`/`api` adapters. Fully typed — Python type hints checked with `ty`, TypeScript in strict mode. The desktop shell (`apps/desktop/src-tauri`) is Rust: it spawns and owns the `local-api` sidecar process for the lifetime of the app.

## Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) ![uv](https://img.shields.io/badge/uv-DE5FE9?style=flat-square&logo=uv&logoColor=white) ![Angular](https://img.shields.io/badge/Angular-DD0031?style=flat-square&logo=angular&logoColor=white) ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white) ![Rust](https://img.shields.io/badge/Rust-000000?style=flat-square&logo=rust&logoColor=white) ![Tauri](https://img.shields.io/badge/Tauri-24C8DB?style=flat-square&logo=tauri&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) ![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazonwebservices&logoColor=white) ![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=flat-square&logo=terraform&logoColor=white)

## Testing

TDD going forward: for each issue, write the failing test first (domain/application logic, not framework glue), then the code that makes it pass.

| App | Runner | Command |
|---|---|---|
| `apps/local-api` | pytest | `uv run pytest` |
| `services/cloud-api` | pytest | `uv run pytest` |
| `apps/frontend` | Vitest (via Angular CLI) | `npx ng test --watch=false` |
| `apps/desktop` | `cargo test` | `cd apps/desktop/src-tauri && cargo test` |

The hexagonal architecture is what makes this practical: `application` use cases are tested against fake ports (in-memory test doubles for `domain` ABCs), no FastAPI or SQLite involved. Adapters (`infrastructure`, the Rust `LocalApiSidecar`) get their own focused tests — SQLite adapters against a real temp database, the sidecar's process/network lifecycle against a real (but disposable, in-test) TCP server rather than a mock.

## Roadmap

- Multi-tenant SaaS: one cloud deployment serving multiple businesses, with accounts and billing
- Expand beyond the flower shop use case to other small commerce verticals

## Status

Early scaffolding — see [Issues](../../issues) and the [Project board](../../projects) for current progress.

> [!NOTE]
> Built with [Claude Code](https://claude.com/claude-code) as a daily pair-programming tool — AI drafts, I review.
