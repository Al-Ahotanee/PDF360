# PDF360

**Everything PDF. One Platform.**

Open-source (MIT), all-in-one PDF platform — creation, editing, merge/split,
compression, conversion, OCR, security, forms, batch processing,
collaboration, and full user/admin dashboards.

## Status

✅ **Feature-complete for initial release.** This build includes:

- **Backend** (FastAPI, 89 API routes): JWT auth + RBAC, file upload/
  storage (local now, S3/R2-ready), the full PDF engine (merge, split,
  extract, rotate, compress, delete/insert/duplicate/reorder pages, page
  numbering, header/footer), conversion engine (Office↔PDF, images↔PDF,
  Markdown/HTML↔PDF, PDF→text/EPUB), OCR engine, security engine (encrypt/
  decrypt, watermark, metadata, true redaction, visible e-signature +
  verification, permission restrictions), editor engine (highlight/
  freetext/sticky-note/freehand annotations, form fields — real PDF
  annotation objects via PyMuPDF, not image overlays), batch processing,
  organization (folders/tags/favorites/trash), collaboration (notifications/
  comments), dashboard stats, admin (RBAC-protected user/role management,
  audit log, system health, usage analytics), and a billing/API-key
  scaffold (see "Out of scope" below).
- **Frontend** (Next.js 14 App Router): dashboard, file manager with
  drag-and-drop upload, a full annotation editor (highlight/draw/text/
  sticky-note tools on a real rendered page), tool pages for every
  operation above (organize/convert/secure/forms/batch), a redaction
  coordinate picker, settings (profile/billing/API keys), and an admin
  panel with analytics/audit log. Custom design system (ink navy + signal
  amber, Space Grotesk/Inter).
- **Tests**: 41 pytest tests covering every PDF/conversion/OCR/security/
  editor engine function, run against real generated PDFs/DOCX/images —
  not mocks. (The page-organization, signature, and billing additions
  don't yet have dedicated tests — see `CONTRIBUTING.md` if you'd like to
  add them.)
- **Deployment**: Dockerfiles for both services, `docker-compose.yml`
  (Postgres/Redis/backend/worker/frontend), GitHub Actions CI.

**Out of scope by design** (see `CONTRIBUTING.md` for the reasoning):
AI features (`/api/v1/ai/*` returns a clear "not configured" response —
no LLM provider is wired in), email verification / transactional email,
and payment processing (the billing/subscription endpoints record state
locally only — no Stripe/Paddle integration, and none is planned since
this is free/open-source software with no paid tier to unlock).

**Known scope boundary:** there's a redaction coordinate picker and a
full annotation editor (highlight/draw/text/sticky-note), but no
general-purpose drag-and-resize form-field designer in the UI yet — form
fields can be created via the API (`/editor/form-fields/*`) and filled
via the Forms tool page, but the frontend doesn't expose a visual field
placer for arbitrary coordinates. Everything else from the original
feature list has at least a working implementation.

See `docs/02-architecture.md` for the full list of design decisions made
along the way, several of which came from bugs found by testing against
real running infrastructure rather than assumed to work.

## System dependencies (not installed via pip)

The conversion and OCR engines shell out to external binaries — confirmed
working versions during development are noted:

- **LibreOffice** (`soffice` on PATH) — Office↔PDF conversion. v7.x+
- **Tesseract OCR** (`tesseract` on PATH) — text recognition. v5.3+
  Install additional language packs as needed. Most are available via
  apt (e.g. `tesseract-ocr-fra` for French, `tesseract-ocr-ara` for
  Arabic) — but **confirmed by checking apt's package list directly**,
  Hausa has no `tesseract-ocr-hau` package despite being a supported
  Tesseract language. Download `hau.traineddata` from the
  [tesseract-ocr/tessdata](https://github.com/tesseract-ocr/tessdata)
  repo and place it in Tesseract's `tessdata` directory instead — this
  matters given the Jigawa/Katsina/Gombe/Kano target audience.
- **Ghostscript** (`gs` on PATH) — used internally by ocrmypdf. v10.x+

On Windows: install LibreOffice and Tesseract from their official
installers and add their install directories to PATH; Ghostscript from
ghostscript.com. On the eventual Linux deployment target:
`apt-get install libreoffice tesseract-ocr ghostscript`.

**Known limitation, confirmed by testing:** LibreOffice headless cannot
reliably convert PDF→DOCX/PPTX (it opens PDFs as a Draw/graphics document,
not editable text). PDF→DOCX and PDF→PPTX instead use text-extraction and
image-rendering reconstruction respectively (see
`app/services/pdf_engine/conversion.py` docstrings) — this is a real
constraint of PDF's format, not unique to this codebase; no PDF tool
fully reconstructs original Word/PowerPoint layout from a PDF.

## Getting started (local, Windows-friendly)

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env         # then fill in DATABASE_URL (Neon), SECRET_KEY
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
python -m app.db.seed          # creates default roles/permissions
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/api/docs

### Frontend
```bash
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```
App: http://localhost:3000

### Redis + Celery (for background jobs, needed from Phase 9 onward)
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

## Project structure
```
pdf360/
  backend/
    app/
      core/         config, security, deps (auth/RBAC guards)
      db/           session, base, seed
      models/       SQLAlchemy models
      schemas/      Pydantic request/response models
      repositories/ DB query layer
      services/     business logic
      routes/v1/    API route handlers
      workers/      Celery app + tasks
    alembic/         migrations
  frontend/
    app/             Next.js routes
    components/       UI components
    hooks/           TanStack Query hooks
    lib/api/         Axios client, providers
    types/           shared TypeScript types
  docs/              requirements, architecture, database, API, deployment
```

## Cloud Deployment (Render Blueprint + Neon PostgreSQL)

PDF360 includes a production-ready Infrastructure as Code blueprint (`render.yaml`) for 1-click deployment on [Render](https://render.com):

1. Connect your repository to Render -> Create a new **Blueprint**.
2. Supply your free [Neon PostgreSQL](https://neon.tech) connection string (`DATABASE_URL`).
3. Render automatically provisions the FastAPI API, Next.js frontend, Celery worker, and Redis queue.
4. See [`docs/03-deployment-render-neon.md`](docs/03-deployment-render-neon.md) for full instructions, including Cloudflare R2 / AWS S3 cloud storage setup.

