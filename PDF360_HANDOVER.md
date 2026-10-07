# PDF360 — Handover Document

This document exists to let another LLM (or you) pick up PDF360 development
with full context, without re-deriving decisions already made or re-finding
bugs already found. Read this fully before touching code.

**Attach/upload alongside this document**: `PDF360-complete-4.zip` — the
last fully-verified snapshot of the codebase. Everything in "Verified
Current State" below describes what's inside that zip. Everything in
"Unfinished Work" below is **not** in that zip and needs to be (re)written —
code for it is given inline so it can mostly be copy-pasted rather than
re-designed.

---

## 1. What PDF360 is

Open-source (MIT), self-hostable, all-in-one PDF platform — "Everything
PDF. One Platform." Comparable in feature scope to iLovePDF/Smallpdf/PDF24,
built from a long master-prompt SRS (creation, editing, merge/split,
compression, conversion, OCR, security, forms, batch processing, reading,
organization, collaboration, user + admin dashboards).

**Explicitly out of scope — do not implement, even if the SRS mentions
them** (the project owner ruled these out):
- AI features — `/api/v1/ai/*` exists and returns a clean "not configured"
  501 by design. Do not wire in an LLM provider.
- Email verification / transactional email.
- Payments — `BillingService.change_plan` only records local state, no
  Stripe/Paddle. Do not add a payment provider.

Reasoning for all three is documented in `CONTRIBUTING.md` in the repo.

## 2. Tech stack

- **Backend**: FastAPI (Python), SQLAlchemy 2.0 + Alembic, Pydantic v2,
  PostgreSQL (Neon), Redis + Celery for job processing, JWT auth + RBAC.
- **PDF engine**: PyMuPDF (`pymupdf`, pinned **1.24.11** — see §5 for why
  the version matters), `pypdf`, ReportLab, `pdfplumber`, OCRmyPDF,
  Pillow, LibreOffice headless (document conversions), Poppler.
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind, TanStack
  Query, Axios. Custom design system (ink navy + signal amber, Space
  Grotesk/Inter fonts).
- **Storage**: local filesystem now, behind an interface that's
  S3/R2-swappable (`app/services/storage/factory.py`).

## 3. Repo layout

```
pdf360/
  backend/
    app/
      main.py                  # FastAPI app, all routers registered here
      core/                    # security.py (hashing/JWT), deps.py (auth/permission deps)
      db/                      # session.py, base.py (declarative base + mixins), seed.py
      models/                  # one file per domain; models/__init__.py imports ALL of them
                                #   (required — see the docstring in that file; a model not
                                #   imported there breaks relationship() string lookups)
      schemas/                 # Pydantic request/response models, mirrors routes/ naming
      repositories/            # DB access only, no business logic
      services/                # business logic; routes call these, never DB directly
        pdf_engine/             # the ONLY place that imports PyMuPDF/pypdf/ReportLab —
                                 #   core.py, security.py, editor.py, conversion.py, creation.py
                                 #   every function: raw bytes in, raw bytes out, no DB/storage
      routes/v1/                # thin — parse request, call service, return. No logic here.
      workers/
        celery_app.py           # task module registration list — NEW task modules must be
                                 #   added to `include=[...]` here or Celery never sees them
        tasks/                  # one Celery task per async PDF operation
    alembic/versions/           # migrations — see §6 for current head
    tests/                      # 41 pytest tests, engine-level, run against real generated
                                 #   PDFs/DOCX/images — not mocks. Does NOT cover anything
                                 #   added in the last two sessions (see §8).
  frontend/
    app/(auth)/                 # login, register
    app/(app)/                  # everything behind auth — dashboard, files, editor, settings,
                                 #   admin, tools/{create,organize,convert,secure,forms,ai,batch}
    components/tools/           # ToolCard, FileSelect, JobStatusPanel, PageEditor — shared
                                 #   building blocks every tool page is built from
    hooks/                      # one hook file per domain (useEditor.ts, useBilling.ts, etc.),
                                 #   thin TanStack Query wrappers around apiClient calls
    lib/api/client.ts           # Axios instance, base URL + auth header injection
  LICENSE, CONTRIBUTING.md, README.md
```

### Architecture conventions — follow these, don't improvise new patterns

1. **Routes are thin.** A route parses the request schema, calls one
   service method, returns. If you're writing `if`/business logic in a
   route file, it belongs in `services/` instead.
2. **PDF-library imports are confined to `services/pdf_engine/`.** Every
   function there takes bytes, returns bytes (or a list of bytes, or a
   plain dict for metadata-only reads), and has zero knowledge of
   storage/DB/jobs. This is what makes the engine unit-testable and
   library-swappable. Never `import pymupdf` or `import pypdf` outside
   this package.
3. **Two execution patterns, pick correctly:**
   - **Async/Celery** (`PDFService`, `BatchService`): for anything that
     reads+rewrites a PDF and could be slow — merge, split, compress,
     convert, OCR, encrypt, page operations, signing. Route creates a
     `Job` row, dispatches a Celery task, returns `202` with the job ID;
     the frontend polls `GET /jobs/{id}` (see `JobStatusPanel.tsx`).
   - **Synchronous** (`EditorService`, `CreationService`): for fast,
     single-document operations — annotations, form fields, blank-PDF/
     invoice/certificate generation. Returns the new `File` directly,
     `201`, no polling.
   Don't make something synchronous "because it's simpler" if it does a
   full PDF rewrite — stay consistent with the existing split.
4. **Ownership checks**: `PDFService._assert_owns_all(owner_id,
   [file_id, ...])` for job-based ops; `FileService.get_owned_file(...)`
   for direct reads (download/preview). Both currently check
   `file.owner_id == caller_id` only — **no sharing-aware check exists
   yet**, see §7, item 1, this is the single biggest half-finished piece.
5. **New Celery task modules must be added to `celery_app.py`'s
   `include=[...]` list** or they silently never run (confirmed — this
   bit us once already during this project; don't repeat it).
6. **Alembic migrations**: write a new revision file by hand (don't rely
   on autogenerate against a live DB, since this environment has no live
   Postgres to generate against) matching the exact column style of
   existing migrations — `server_default=sa.text('now()')` on
   created_at/updated_at, no server_default on `id` (SQLAlchemy supplies
   `uuid.uuid4()` client-side). Check the most recent migration file for
   the exact pattern before writing a new one.
7. **Frontend tool pages are long, flat, repetitive files** — one
   `useState` pair per field, one `async function run<Thing>()` per
   operation, one `<ToolCard>` per operation, all in the same page
   component. This is intentional for this project (not every tool needs
   its own component), don't "refactor" it into fragments unless asked.

## 4. How to verify changes (do this after every change, not just at the end)

Backend — this is the single most useful check; it catches wrong
imports, bad relationships, and route wiring mistakes that `py_compile`
cannot (py_compile only checks syntax, not that names actually resolve):

```bash
cd backend
cp .env.example .env
sed -i 's|postgresql://user:password@ep-xxxx.neon.tech/pdf360?sslmode=require|postgresql://user:password@localhost/pdf360|' .env
pip install -r requirements.txt --break-system-packages -q
python3 -c "
from app.main import app
n = sum(1 for r in app.routes if hasattr(r, 'methods'))
print('routes:', n)
"
rm -f .env
```

No live Postgres is needed for this — `app.main` importing successfully
and the route count printing is what matters; it proves every router,
service, model, and schema actually resolves. As of the last verified
state this prints **105**.

For anything in `services/pdf_engine/`, don't stop at import-checking —
**actually run the function against a real generated PDF** before calling
it done. Compiling only catches syntax errors; e.g. a prior pass shipped
`compress_pdf` calling `Document.rewrite_images()`, which doesn't exist
in the pinned PyMuPDF 1.24.11 — this was silent until actually exercised
against a PDF with a real embedded image. Minimal pattern:

```python
import pymupdf
from app.services.pdf_engine import core, creation
pdf = creation.text_to_pdf("Hello world.\n\nSecond paragraph.")
result = core.some_new_function(pdf, ...)
print(len(result))  # sanity: non-trivial byte length, no exception
```

Frontend:

```bash
cd frontend
npm install --no-audit --no-fund
npx tsc --noEmit
```

Must be zero errors before considering frontend work done.
`next build` will fail in a sandboxed environment with no internet access
(it tries to fetch Google Fonts) — that's an environment limitation, not
a code error; don't chase it.

## 5. Known-fixed bugs (don't reintroduce)

- **`compress_pdf` was silently broken.** `Document.rewrite_images()` is
  not available in PyMuPDF 1.24.11 (the pinned version in
  `requirements.txt`). Fixed by manually walking `page.get_images(full=True)`,
  extracting each image via `doc.extract_image(xref)`, recompressing with
  Pillow (resize by the preset's dpi ratio, re-encode as JPEG at the
  preset quality), and writing back with `page.replace_image(xref,
  stream=...)`. If you ever bump the PyMuPDF version, you could revert to
  the one-line `rewrite_images()` call — but verify it actually exists
  in whatever version you pin first.
- **pypdf permission flag names**: `pypdf.constants.UserAccessPermissions`
  has `PRINT`, `EXTRACT`, `MODIFY`, `FILL_FORM_FIELDS` — it does **not**
  have `ANNOT_FORMS` or any `pypdf.generic.UserAccessPermissions` (that
  path doesn't exist at all in this pinned version). Used in
  `security.set_permissions`.
- **Storage API is `storage.build_key(owner_id, filename)` +
  `storage.save(key, io.BytesIO(data))`**, not `storage.write(data,
  suffix=...)` (that method doesn't exist). Grep `_save_bytes` in
  `workers/tasks/conversion_tasks.py` or `_run` in `editor_service.py`
  for the canonical pattern before writing new storage-touching code.

## 6. Current Alembic head

```
fa701903ec9f (initial schema)
  -> b3c9a1e5f210 (page-ops/signature/html-epub job types)
  -> c7d2f4a8e331 (rotate/extract/crop/replace/remove-watermark/bookmarks job types)
```
`c7d2f4a8e331` is HEAD in the verified zip. §7 below describes a further
migration (`d8e5b1c9f442`) that was drafted but never verified/compiled
against the zip — treat its SQL as a starting draft, re-check it
carefully (it was hand-written against the *style* of other migrations,
not against a live DB).

## 7. Unfinished work — start here

This is mid-flight work from the session that produced this handover.
None of it is in the zip. Code is given where it was already written so
it can be dropped in rather than redesigned — but **treat all of it as
unverified**: compile-check, then run `app.main` import check, then
runtime-test the engine-level pieces, same as §4 says for everything
else.

### 7.1 File sharing ("Share Documents" / "Shared Workspace") — biggest gap

No sharing exists at all in the zip — every file is single-owner only,
and `FileService.get_owned_file` / `PDFService._assert_owns_all` both
hard-check `file.owner_id == caller_id` with no concept of a grant.
"Comments" in the zip are similarly owner-only (you can only comment on
your own files), which makes the existing Collaboration feature set
(comments, notifications) effectively unreachable by anyone but the
file's owner — a second user has no way to ever see the file to comment
on it. This is the most consequential remaining gap.

**Design** (drafted, not yet wired into existing ownership checks):

New model `app/models/file_share.py`:
```python
import enum
import uuid

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SharePermission(str, enum.Enum):
    VIEW = "view"
    COMMENT = "comment"
    EDIT = "edit"


class FileShare(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Grants shared_with_id access to file_id at `permission`. VIEW covers
    download/preview/bookmarks-read; COMMENT additionally allows adding
    comments; EDIT additionally allows running PDF operations against the
    file. Direct user-to-user grants only — no public share links in this
    design (that's a separate feature with its own security surface:
    expiry, anonymous access, revocation-by-link)."""
    __tablename__ = "file_shares"
    __table_args__ = (UniqueConstraint("file_id", "shared_with_id", name="uq_file_shares_file_user"),)

    file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"))
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    shared_with_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    permission: Mapped[SharePermission] = mapped_column(Enum(SharePermission, name="share_permission"), nullable=False)

    file: Mapped["File"] = relationship()
```
Register it in `app/models/__init__.py`'s import list (required, see the
docstring in that file — a model not imported there breaks
`relationship()` string-based lookups elsewhere).

Migration `d8e5b1c9f442` (drafted, needs re-verification — write it fresh
by copying the exact column style from
`alembic/versions/c7d2f4a8e331_...py`, which is HEAD in the zip):
creates `file_shares` table (id, created_at, updated_at, file_id,
owner_id, shared_with_id, permission enum `share_permission`, unique
constraint on `(file_id, shared_with_id)`), indexes on `shared_with_id`
and `file_id`; also adds `comments.mentioned_user_ids` JSONB
`NOT NULL DEFAULT '[]'` (see §7.2).

Repository `app/repositories/file_share_repository.py` — CRUD: `get_by_id`,
`get_for_file_and_user`, `list_for_file`, `list_shared_with_user`,
`upsert` (update permission if a share already exists for that pair
rather than erroring), `delete`.

Shared access-level helper, **this is the piece every existing ownership
check needs to start calling** — `app/services/file_access.py`:
```python
import uuid
from sqlalchemy.orm import Session
from app.models.file import File
from app.models.file_share import SharePermission
from app.repositories.file_share_repository import FileShareRepository

_LEVEL = {SharePermission.VIEW: 1, SharePermission.COMMENT: 2, SharePermission.EDIT: 3}

def permission_for(db: Session, *, file: File, user_id: uuid.UUID) -> SharePermission | None:
    """EDIT if they own it, whatever was granted if shared with them, else None."""
    if file.owner_id == user_id:
        return SharePermission.EDIT
    share = FileShareRepository(db).get_for_file_and_user(file.id, user_id)
    return share.permission if share else None

def has_at_least(db: Session, *, file: File, user_id: uuid.UUID, required: SharePermission) -> bool:
    perm = permission_for(db, file=file, user_id=user_id)
    return perm is not None and _LEVEL[perm] >= _LEVEL[required]
```

`ShareService` (`app/services/share_service.py`) — share-by-email (looks
up the target by `UserRepository.get_by_email`, 404s if not found, 422s
if sharing with yourself), `list_shares_for_file`, `revoke_share`,
`list_shared_with_me` (returns `[{"share": ..., "file": ...}]` pairs).
Share creation should fire a `NotificationService.create_for_user(...)`
to the recipient ("A file was shared with you") — `NotificationService`
already exists in `collaboration_service.py`, reuse it, don't duplicate
notification logic.

**Still needed beyond the above** (none of this exists yet, even in
draft form):
1. Pydantic schemas (`ShareCreateRequest{file_id, with_email, permission}`,
   `ShareOut`, `SharedWithMeOut`) and routes — natural home is
   `routes/v1/collaboration.py` (`POST /collaboration/files/{file_id}/share`,
   `GET /collaboration/files/{file_id}/shares`,
   `DELETE /collaboration/shares/{share_id}`,
   `GET /collaboration/shared-with-me`).
2. **Retrofit `FileService.get_owned_file`** to accept callers with at
   least VIEW via `file_access.has_at_least` instead of hard-requiring
   ownership — this unlocks download/preview for shared users. Likely
   needs a rename/new method (`get_accessible_file`) rather than changing
   the existing one's semantics everywhere, since some call sites
   (billing, admin) may genuinely want owner-only.
3. **Retrofit `CommentRepository`/`CommentService`** (`_assert_owns_file`
   in `collaboration_service.py`) to allow COMMENT+ access, not just
   ownership — this is what actually makes Comments usable by anyone but
   the owner.
4. Decide — and this is a real product decision, not just plumbing —
   whether `PDFService._assert_owns_all` (every merge/split/convert/etc.
   job) should accept EDIT-level shares too. Retrofitting that one
   function unlocks true collaborative editing across all ~30 PDF
   operations in one place, since every job-based operation already
   funnels through it. This was not done in the draft — it's the highest
   remaining architectural decision in the project to resolve.
5. Frontend: a "Share" button/modal on the Files page, a "Shared with me"
   view, and surfacing share-permission state in the file list. None of
   this has been started.

### 7.2 Mentions (@mentions in comments)

Smaller, mostly independent of 7.1. `Comment.mentioned_user_ids: Mapped[list]
= mapped_column(JSONB, default=list)` was added to the `Comment` model in
`app/models/activity.py` (draft, part of migration `d8e5b1c9f442` above —
verify the migration syntax before trusting it). Not yet done: parsing
`@email-or-handle` out of comment body text in `CommentService.add_comment`,
resolving each to a user ID, saving them to `mentioned_user_ids`, and
firing a `NotificationService.create_for_user(...)` per mention. No
frontend mention-autocomplete UI exists.

### 7.3 Activity History / Activity Timeline

The `ActivityLog` model (`app/models/activity.py`) existed in the zip but
was **completely unused** — confirmed by grep, zero writes anywhere. Found
during this session and partially fixed: a single-choke-point write was
added to `JobRepository.mark_done` (every job-based PDF operation — merge,
split, compress, convert, OCR, security, page ops, signing — funnels
through this one method, so logging there gives a complete activity feed
for free without touching ~30 call sites individually):

```python
# in JobRepository.mark_done, after the existing commit/refresh:
self.db.add(ActivityLog(
    user_id=job.owner_id, action=f"job.{job.job_type.value}",
    resource_type="job", resource_id=job.id,
    metadata_json={"result": result},
))
self.db.commit()
```
(needs `from app.models.activity import ActivityLog` added to that file's
imports). This is in the conversation but **not in the zip** — redo it.
Not yet done at all: a repository method to list a user's activity, a
service method, a `GET /dashboard/activity` (or similar) route, and
frontend display (the dashboard's "Activity Timeline" from the SRS).
Also not done: logging activity for the *synchronous* operations
(EditorService, CreationService) which don't go through `JobRepository`
at all — those would need their own logging calls added individually,
there's no equivalent single choke point for them.

### 7.4 Admin feature flags

`SystemConfiguration` model exists in the zip (`key`, `value` JSONB,
`description`) but had zero repository/service/route. Drafted this
session (not in zip): `SystemConfigRepository` (in
`repositories/billing_repository.py` — odd location, was appended there
expediently; consider moving to its own file), `AdminService` methods
`list_feature_flags`/`set_feature_flag`/`delete_feature_flag` (each
writes to the audit log via the existing `_write_audit` helper), schemas
`FeatureFlagOut`/`FeatureFlagSetRequest`, routes `GET/PUT
/admin/feature-flags`, `DELETE /admin/feature-flags/{key}` (all behind
the existing `admin:system:manage` permission). None of this was
verified against the zip's actual `app.main` import check — redo and
verify. No frontend UI for it exists.

## 8. Test coverage gap

`backend/tests/` has 41 tests covering the *original* feature set
(merge/split/compress/convert/OCR/security/editor engine functions, run
against real generated PDFs — not mocks, this pattern should be kept).
**Nothing added across the last two sessions has test coverage**: page
organization (delete/insert-blank/duplicate/reorder/page-numbers/
header-footer), signature (sign/verify/permissions), crop/replace-pages/
remove-watermark/bookmarks, underline/strikethrough/whiteout annotations,
the Creation module (blank/text-to-pdf/invoice/certificate/report),
billing/API-keys, admin analytics/audit-log/system-health, or anything in
§7. Given how directly testing caught real bugs twice already in this
project (`rewrite_images`, the permission-flag name), this is a priority,
not a nice-to-have — new PDF-engine code especially should get tests in
the same PR, not after.

## 9. Remaining SRS gaps not yet started at all

- **Reading/viewer features**: zoom, fullscreen, presentation mode, night
  mode, reading progress, thumbnail navigation. The only "preview" that
  exists today is a static rendered-page PNG (used by the redaction
  picker and `PageEditor`) — not an interactive viewer. This needs a
  PDF.js-based viewer component; nothing toward it has been built.
- **Document version history**: the `DocumentVersion` model exists but is
  *deliberately* unused — documented in a comment at the top of
  `editor_service.py`: each edit creates an independent new `File` row
  rather than a linked version of an existing document. This was a
  conscious architectural tradeoff, not an oversight; revisiting it is a
  real design decision (migrate existing File-per-edit data? Keep both
  models?), not a quick fix.
- **Export form data** — arguably already covered: `GET
  /editor/form-fields/{file_id}` returns every field as JSON, which is
  functionally "export form data." No separate dedicated endpoint exists;
  decide if the SRS line item needs more than that before building
  anything new here.

## 10. Quick-start to validate you're working from the right baseline

```bash
unzip PDF360-complete-4.zip
cd pdf360/backend
cp .env.example .env
sed -i 's|postgresql://user:password@ep-xxxx.neon.tech/pdf360?sslmode=require|postgresql://user:password@localhost/pdf360|' .env
pip install -r requirements.txt --break-system-packages -q
python3 -c "from app.main import app; print(sum(1 for r in app.routes if hasattr(r,'methods')))"
# expect: 105
rm -f .env
cd ../frontend
npm install --no-audit --no-fund
npx tsc --noEmit
# expect: no output, exit 0
```
If either check fails before you've changed anything, something about
the environment differs from what's documented here — stop and
reconcile that before building on top of it.
