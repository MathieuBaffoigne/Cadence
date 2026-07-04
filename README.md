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
apps/desktop/       Electron shell (packaged app, Windows/Mac)
apps/frontend/      Angular UI, shared by the Electron shell
apps/local-api/     FastAPI sidecar, runs locally, talks to SQLite
services/cloud-api/ FastAPI + PostgreSQL, sync endpoint, deployed on AWS
infra/terraform/    AWS infrastructure as code
```

Local SQLite is the source of truth offline. Each record carries an `updated_at`; when the app reconnects, it pushes local changes and pulls remote ones, resolving conflicts last-write-wins.

## Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) ![Angular](https://img.shields.io/badge/Angular-DD0031?style=flat-square&logo=angular&logoColor=white) ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white) ![Electron](https://img.shields.io/badge/Electron-191970?style=flat-square&logo=electron&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) ![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazonwebservices&logoColor=white) ![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=flat-square&logo=terraform&logoColor=white)

## Roadmap

- Multi-tenant SaaS: one cloud deployment serving multiple businesses, with accounts and billing
- Expand beyond the flower shop use case to other small commerce verticals

## Status

Early scaffolding — see [Issues](../../issues) and the [Project board](../../projects) for current progress.

> [!NOTE]
> Built with [Claude Code](https://claude.com/claude-code) as a daily pair-programming tool — AI drafts, I review.
