# PDF360 — Architecture (Phase 2)

## High-level flow
```
Client (Next.js) → REST API (FastAPI) → Service layer → {PDF engine, DB, Redis/Celery workers, Storage}
                                       ↳ Auth middleware (JWT + RBAC) on every route
Workers (Celery) → pull jobs → run PDF/OCR/AI ops → write result + update job status
```

## Backend layering
`routes/` (thin controllers, no business logic) → `services/` (business
logic, orchestration) → `repositories/` (all DB queries) → `models/`
(SQLAlchemy ORM). `schemas/` (Pydantic) sit at the API boundary only —
they never leak into services or repositories.

## Frontend layering
`app/` (routes, App Router) → `components/` (presentational) → `hooks/`
(TanStack Query wrappers around API calls) → `lib/api/` (Axios client +
interceptors) → `types/` (shared TS types, generated from backend schemas
later).

## Key decisions
1. **PDF engine boundary** — all PyMuPDF/pypdf/ReportLab/etc. calls live
   behind a single `pdf_engine` service layer (Phase 9). Route handlers
   never import a PDF library directly. This is what makes swapping or
   upgrading a library later a one-file change.
2. **Uniform job model** — every PDF operation (even sub-second ones)
   creates a job record with status queued/processing/done/failed. One
   consistent client pattern: submit → poll/websocket → result. No
   separate "fast path" vs "slow path" code.
3. **Storage abstraction** — `StorageProvider` interface with
   `LocalStorageProvider` now, `S3StorageProvider` later. Services never
   touch the filesystem directly.
4. **RBAC** — permissions are fine-grained strings (`files:delete`,
   `admin:users:manage`) attached to roles via a join table. Route-level
   checks use a `require_permission()` dependency factory. Adding a
   permission to a role is a data change, not a deploy.
5. **AI features** — provider-agnostic; `AI_PROVIDER`/`ANTHROPIC_API_KEY`
   are currently unset/stubbed. Real AI endpoints get built once a
   provider is confirmed.

## Monorepo layout
```
pdf360/
  backend/   FastAPI app, Alembic migrations, Celery workers
  frontend/  Next.js app
  docs/      Architecture, database, API, deployment docs
```
