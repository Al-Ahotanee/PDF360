# Contributing to PDF360

PDF360 is open source (MIT license) — issues, PRs, and forks are welcome.

## Out of scope for this project

To keep the project simple to self-host and free of external-vendor
dependencies, the following are **intentionally not implemented** and PRs
adding them will likely be declined unless discussed in an issue first:

- **AI features** — the `/api/v1/ai/*` endpoints exist as a clean interface
  (summarize/ask/translate/keywords/suggest-title) but return a "not
  configured" response rather than calling any LLM provider. Wiring one in
  is a legitimate self-hosting choice, but it's a per-deployment decision
  (which provider, API key management, cost) rather than something the
  project should hard-code.
- **Email verification / transactional email** — `User.is_verified` exists
  as a field but nothing sends or checks a verification email. Self-hosters
  who need this are expected to put PDF360 behind their own auth/identity
  layer (e.g. an OAuth proxy) rather than the project shipping its own
  SMTP/provider integration.
- **Payments** — the billing/subscription/API-key models and endpoints
  exist so premium-tier UI has something real to read from, but
  `BillingService.change_plan` only ever records local state; no payment
  provider (Stripe, Paddle, etc.) is wired in, and none is planned. PDF360
  is free/open-source software — there is no paid tier to unlock in this
  codebase itself; the billing scaffolding is there only for anyone who
  forks this to run a hosted commercial version.

## Local setup

See the root `README.md` "Getting started" section.

## Pull requests

- Keep changes scoped — one feature/fix per PR.
- Match the existing layering: `routes/` are thin, business logic lives in
  `services/`, DB access lives in `repositories/`.
- Add or update tests under `backend/tests/` for any engine-level change
  (`services/pdf_engine/*`).
- Run `alembic revision --autogenerate` for any model change and commit the
  generated migration.
- Frontend: run `npx tsc --noEmit` before submitting; there is no CI type
  check bypass.

## Reporting issues

Please include: what you ran, what you expected, what happened, and
(for PDF-processing bugs) a minimal PDF that reproduces it if you're able
to share one.
