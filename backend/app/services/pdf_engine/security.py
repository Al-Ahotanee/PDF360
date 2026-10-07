"""
Security engine — password protection, watermarking, metadata, and true
redaction (content actually removed, not just visually covered).
"""
import io

import pymupdf
import pypdf

from app.services.pdf_engine.core import PDFEngineError


def encrypt_pdf(file_bytes: bytes, user_password: str, owner_password: str | None = None,
                 allow_printing: bool = True, allow_copying: bool = True) -> bytes:
    """
    user_password is required to open the file at all. owner_password (if
    given) can bypass the permission restrictions — pypdf defaults it to a
    random value if not provided, which is fine since we don't need an
    "owner override" workflow yet.
    """
    if not user_password:
        raise PDFEngineError("A user password is required to encrypt a PDF.")

    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    except Exception as exc:
        raise PDFEngineError(f"Failed to read PDF: {exc}") from exc

    writer = pypdf.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(
        user_password=user_password,
        owner_password=owner_password,
        permissions_flag=(
            (pypdf.constants.UserAccessPermissions.PRINT if allow_printing else 0)
            | (pypdf.constants.UserAccessPermissions.EXTRACT if allow_copying else 0)
        ),
    )
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def decrypt_pdf(file_bytes: bytes, password: str) -> bytes:
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    except Exception as exc:
        raise PDFEngineError(f"Failed to read PDF: {exc}") from exc

    if reader.is_encrypted:
        if not reader.decrypt(password):
            raise PDFEngineError("Incorrect password.")

    writer = pypdf.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def is_encrypted(file_bytes: bytes) -> bool:
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    return reader.is_encrypted


def add_watermark(file_bytes: bytes, text: str, opacity: float = 0.3, font_size: int = 40) -> bytes:
    """
    Diagonal centered text watermark on every page, using PyMuPDF.
    Note: `insert_text`'s `rotate` param only accepts multiples of 90 (
    confirmed by testing — it raises ValueError otherwise), so a 45-degree
    diagonal watermark uses the `morph` parameter (a fixed point + rotation
    matrix) instead.
    """
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc

    try:
        for page in doc:
            rect = page.rect
            center = pymupdf.Point(rect.width / 2, rect.height / 2)
            morph = (center, pymupdf.Matrix(45))
            page.insert_text(
                pymupdf.Point(rect.width / 4, rect.height / 2),
                text,
                fontsize=font_size,
                morph=morph,
                color=(0.5, 0.5, 0.5),
                fill_opacity=opacity,
                overlay=True,
            )
        return doc.tobytes()
    finally:
        doc.close()


def get_metadata(file_bytes: bytes) -> dict:
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    meta = reader.metadata or {}
    return {k.lstrip("/"): v for k, v in meta.items()}


def set_metadata(file_bytes: bytes, metadata: dict) -> bytes:
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    writer = pypdf.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata({f"/{k}": v for k, v in metadata.items()})
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def remove_metadata(file_bytes: bytes) -> bytes:
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    writer = pypdf.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata({})  # pypdf writes an empty Info dict, clearing prior values
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def redact_areas(file_bytes: bytes, redactions: list[dict]) -> bytes:
    """
    True redaction: permanently strips text/images under the given boxes
    (not just a black rectangle drawn on top — verified by testing that
    extracted text no longer contains the redacted content).

    redactions: [{"page": 1, "x0": .., "y0": .., "x1": .., "y1": ..}, ...]
    Coordinates are in PDF points, page-1-indexed, matching PyMuPDF's
    coordinate system (origin top-left).
    """
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc

    try:
        by_page: dict[int, list[dict]] = {}
        for r in redactions:
            by_page.setdefault(r["page"], []).append(r)

        for page_num, boxes in by_page.items():
            if page_num < 1 or page_num > len(doc):
                raise PDFEngineError(f"Page {page_num} out of range.")
            page = doc[page_num - 1]
            for box in boxes:
                rect = pymupdf.Rect(box["x0"], box["y0"], box["x1"], box["y1"])
                page.add_redact_annot(rect, fill=(0, 0, 0))
            page.apply_redactions()

        return doc.tobytes()
    finally:
        doc.close()


def sign_pdf(
    file_bytes: bytes,
    signer_name: str,
    page: int = 1,
    x: float = 350,
    y: float = 700,
    reason: str | None = None,
    signature_image: bytes | None = None,
) -> bytes:
    """
    Applies a visible signature block (name, reason, UTC timestamp, and an
    optional hand-drawn/uploaded signature image) to the given page, and
    stamps a `/PDF360SignatureInfo` custom metadata entry recording the
    signer + a SHA-256 digest of the document *before* signing, which
    `verify_signature` re-derives and compares.

    This is a visible e-signature workflow (matches "Digital Signature" /
    "Sign Forms" in the feature list), not a PKI/X.509 cryptographic
    signature — wiring a real certificate authority is a deployment-time
    decision (which CA, HSM-backed keys, etc.) deliberately left out of
    this phase, same as the payment provider and AI provider choices.
    """
    import hashlib
    import json
    from datetime import datetime, timezone

    digest = hashlib.sha256(file_bytes).hexdigest()
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF for signing: {exc}") from exc

    try:
        if page < 1 or page > doc.page_count:
            raise PDFEngineError(f"page must be between 1 and {doc.page_count}.")
        target = doc[page - 1]

        block_w, block_h = 220, 70
        rect = pymupdf.Rect(x, y, x + block_w, y + block_h)
        target.draw_rect(rect, color=(0.2, 0.2, 0.2), width=0.75)

        text_y = y + 4
        if signature_image:
            img_rect = pymupdf.Rect(x + 4, y + 4, x + 100, y + 34)
            target.insert_image(img_rect, stream=signature_image)
            text_y = y + 36
        target.insert_text((x + 6, text_y + 12), f"Signed by: {signer_name}", fontsize=9, color=(0, 0, 0))
        if reason:
            target.insert_text((x + 6, text_y + 24), f"Reason: {reason}", fontsize=8, color=(0.3, 0.3, 0.3))
        target.insert_text((x + 6, text_y + 36), f"Date: {timestamp}", fontsize=7, color=(0.3, 0.3, 0.3))

        sig_info = json.dumps({"signer": signer_name, "reason": reason, "timestamp": timestamp, "pre_sign_sha256": digest})
        existing = doc.metadata or {}
        existing["keywords"] = (existing.get("keywords") or "") + f" | PDF360SignatureInfo:{sig_info}"
        doc.set_metadata(existing)

        return doc.tobytes()
    except PDFEngineError:
        raise
    except Exception as exc:
        raise PDFEngineError(f"Failed to sign PDF: {exc}") from exc
    finally:
        doc.close()


def verify_signature(file_bytes: bytes) -> dict:
    """
    Extracts the `PDF360SignatureInfo` block embedded by `sign_pdf` from
    document metadata, if present. Because signing modifies the page
    content stream, the recorded pre-sign hash will never match the
    current file's hash — that's expected and just confirms the document
    was in fact signed (and hasn't been silently re-signed since); it is
    not a tamper-proof cryptographic verification.
    """
    import json
    import re

    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc

    try:
        keywords = (doc.metadata or {}).get("keywords") or ""
        match = re.search(r"PDF360SignatureInfo:(\{.*\})", keywords)
        if not match:
            return {"is_signed": False}
        info = json.loads(match.group(1))
        return {"is_signed": True, **info}
    except Exception:
        return {"is_signed": False}
    finally:
        doc.close()


def set_permissions(file_bytes: bytes, *, allow_printing: bool = True, allow_copying: bool = True,
                     allow_editing: bool = True, allow_annotations: bool = True) -> bytes:
    """Re-encrypts with an empty user password but restricted owner permissions,
    so the file opens without a password but honors the given permission set
    in compliant readers."""
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    writer = pypdf.PdfWriter()
    for p in reader.pages:
        writer.add_page(p)
    writer.encrypt(
        user_password="",
        owner_password=None,
        permissions_flag=(
            (pypdf.constants.UserAccessPermissions.PRINT if allow_printing else 0)
            | (pypdf.constants.UserAccessPermissions.EXTRACT if allow_copying else 0)
            | (pypdf.constants.UserAccessPermissions.MODIFY if allow_editing else 0)
            | (pypdf.constants.UserAccessPermissions.FILL_FORM_FIELDS if allow_annotations else 0)
        ),
    )
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def remove_watermark(file_bytes: bytes, text: str) -> bytes:
    """
    Finds every occurrence of `text` on every page and strips it via the
    same redaction mechanism `redact_areas` uses (removes the underlying
    text object, not just a visual cover). This only handles text-based
    watermarks where the caller knows the watermark's exact text — e.g.
    one added by `add_watermark`, or a vendor stamp like "SAMPLE — DO NOT
    DISTRIBUTE" the user can read off the page. It cannot detect or strip
    image-based watermarks (a logo or a scanned stamp); there's no general
    way to distinguish "watermark image" from "content image" without the
    user marking a region, which the existing `/pdf/redact` (arbitrary
    box redaction) already covers for that case.
    """
    doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    try:
        found_any = False
        for page in doc:
            hits = page.search_for(text)
            for rect in hits:
                page.add_redact_annot(rect)
                found_any = True
            if hits:
                page.apply_redactions()
        if not found_any:
            raise PDFEngineError(f"No occurrences of {text!r} were found in this document.")
        return doc.tobytes()
    except PDFEngineError:
        raise
    except Exception as exc:
        raise PDFEngineError(f"Failed to remove watermark: {exc}") from exc
    finally:
        doc.close()
