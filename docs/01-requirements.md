# PDF360 — Requirements Analysis (Phase 1)

## Vision
An enterprise-grade, all-in-one PDF platform (create, edit, convert, merge,
split, compress, OCR, secure, collaborate, AI-assist) — comparable to and
eventually exceeding iLovePDF, Smallpdf, PDF24, Adobe Acrobat Online, Sejda.

## User types
Guest, Registered User, Premium User, Admin, Super Admin — enforced via
RBAC (roles → permissions → route-level checks), not just UI hiding.

## Non-functional requirements
- Large file support via chunked upload/download
- All non-trivial PDF operations run as async background jobs (Celery),
  never block the request thread
- Horizontally scalable: stateless API, storage abstracted from day one
  (local now, S3/R2-ready)
- Audit logging on admin and security-sensitive actions
- Dark/light mode, accessibility-compliant, responsive UI

## Out of scope for this phase
Payment provider integration, virus-scan engine choice, and specific AI
provider are deferred — stubbed interfaces are in place so they can be
filled in without touching calling code.

## Full feature list
See the original master prompt (`docs/00-master-prompt.md`) for the
complete feature inventory across Creation, Editing, Merge & Split,
Compression, Conversion, OCR, Security, Forms, Reading, Organization,
Batch Processing, AI, Collaboration, User Dashboard, and Admin Dashboard.
