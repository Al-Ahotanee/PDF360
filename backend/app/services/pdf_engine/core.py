"""
PDF engine — the ONLY place in the codebase that imports PyMuPDF/pypdf/
ReportLab directly. Routes and services call these functions; they never
touch a PDF library themselves. This is what makes it possible to later
swap PyMuPDF for another engine, or add a faster compression backend,
by editing this one module.

Every function takes and returns raw bytes (or a list of byte-strings for
split), so this module has zero knowledge of storage, jobs, or the DB —
it is pure PDF transformation logic and is easy to unit test in isolation.
"""
import io

import pypdf
import pymupdf  # PyMuPDF
from PIL import Image


class PDFEngineError(Exception):
    """Raised for invalid input (corrupt PDF, bad page range, etc.)."""


def merge_pdfs(file_bytes_list: list[bytes]) -> bytes:
    if len(file_bytes_list) < 2:
        raise PDFEngineError("Merge requires at least 2 files.")

    writer = pypdf.PdfWriter()
    try:
        for file_bytes in file_bytes_list:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                writer.add_page(page)
    except Exception as exc:  # pypdf raises various error types for malformed PDFs
        raise PDFEngineError(f"Failed to merge PDFs: {exc}") from exc

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def split_pdf(file_bytes: bytes, page_ranges: list[tuple[int, int]]) -> list[bytes]:
    """
    page_ranges: list of (start, end) tuples, 1-indexed, inclusive —
    e.g. [(1, 3), (4, 6)] splits a 6-page doc into two 3-page files.
    """
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    except Exception as exc:
        raise PDFEngineError(f"Failed to read PDF: {exc}") from exc

    total_pages = len(reader.pages)
    results: list[bytes] = []

    for start, end in page_ranges:
        if start < 1 or end > total_pages or start > end:
            raise PDFEngineError(f"Invalid page range ({start}, {end}) for a {total_pages}-page document.")
        writer = pypdf.PdfWriter()
        for page_num in range(start - 1, end):
            writer.add_page(reader.pages[page_num])
        buf = io.BytesIO()
        writer.write(buf)
        results.append(buf.getvalue())

    return results


def split_every_page(file_bytes: bytes) -> list[bytes]:
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    total_pages = len(reader.pages)
    return split_pdf(file_bytes, [(i, i) for i in range(1, total_pages + 1)])


def extract_pages(file_bytes: bytes, page_numbers: list[int]) -> bytes:
    """page_numbers: 1-indexed page numbers to keep, in the given order."""
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    except Exception as exc:
        raise PDFEngineError(f"Failed to read PDF: {exc}") from exc

    total_pages = len(reader.pages)
    writer = pypdf.PdfWriter()
    for page_num in page_numbers:
        if page_num < 1 or page_num > total_pages:
            raise PDFEngineError(f"Page {page_num} out of range (document has {total_pages} pages).")
        writer.add_page(reader.pages[page_num - 1])

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


# Compression quality presets. `rewrite_images` recompresses embedded images
# in place (down-sampling DPI and re-encoding at the given JPEG quality);
# `tobytes(garbage=..., deflate=...)` then strips unused objects and
# deflates streams for the structural savings on top.
_COMPRESSION_PRESETS = {
    "low": {"garbage": 1, "deflate": True, "dpi_threshold": 200, "dpi_target": 150, "quality": 85},
    "medium": {"garbage": 3, "deflate": True, "dpi_threshold": 150, "dpi_target": 120, "quality": 60},
    "high": {"garbage": 4, "deflate": True, "dpi_threshold": 110, "dpi_target": 96, "quality": 35},
}


def compress_pdf(
    file_bytes: bytes,
    quality: str = "medium",
    *,
    custom_dpi_target: int | None = None,
    custom_quality: int | None = None,
) -> bytes:
    """`quality="custom"` uses `custom_dpi_target`/`custom_quality` directly
    instead of a preset — lets the UI expose a slider instead of three fixed
    buttons, per the SRS's "Custom compression" requirement."""
    if quality == "custom":
        if custom_dpi_target is None or custom_quality is None:
            raise PDFEngineError("custom_dpi_target and custom_quality are required for quality='custom'.")
        preset = {
            "garbage": 4, "deflate": True,
            "dpi_threshold": max(custom_dpi_target, 72), "dpi_target": custom_dpi_target,
            "quality": custom_quality,
        }
    elif quality in _COMPRESSION_PRESETS:
        preset = _COMPRESSION_PRESETS[quality]
    else:
        raise PDFEngineError(f"Unknown compression quality: {quality}")

    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF for compression: {exc}") from exc

    try:
        # `Document.rewrite_images()` (a one-line bulk API) isn't present in
        # the pinned PyMuPDF version (confirmed by testing — it raises
        # AttributeError), so each image is walked and recompressed by hand
        # via Pillow instead: extract -> optionally downscale -> re-encode
        # as JPEG at the preset quality -> write back with `replace_image`.
        scale = min(1.0, preset["dpi_target"] / max(preset["dpi_threshold"], 1))
        seen_xrefs: set[int] = set()
        for page in doc:
            for img_info in page.get_images(full=True):
                xref = img_info[0]
                if xref in seen_xrefs:
                    continue  # same image referenced by multiple pages
                seen_xrefs.add(xref)
                try:
                    extracted = doc.extract_image(xref)
                except Exception:
                    continue  # not a recompressible raster image (e.g. a mask or vector form)
                try:
                    pil_image = Image.open(io.BytesIO(extracted["image"]))
                    if pil_image.mode in ("RGBA", "P", "LA"):
                        pil_image = pil_image.convert("RGB")
                    if scale < 1.0:
                        w, h = pil_image.size
                        pil_image = pil_image.resize(
                            (max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS,
                        )
                    out = io.BytesIO()
                    pil_image.save(out, format="JPEG", quality=preset["quality"], optimize=True)
                    page.replace_image(xref, stream=out.getvalue())
                except Exception:
                    continue  # leave this one image as-is rather than fail the whole document
        return doc.tobytes(garbage=preset["garbage"], deflate=preset["deflate"], clean=True)
    finally:
        doc.close()


def rotate_pages(file_bytes: bytes, page_numbers: list[int], degrees: int) -> bytes:
    if degrees not in (90, 180, 270, -90, -180, -270):
        raise PDFEngineError("Rotation must be a multiple of 90 degrees.")

    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    writer = pypdf.PdfWriter()
    page_set = set(page_numbers)
    for i, page in enumerate(reader.pages, start=1):
        if i in page_set:
            page.rotate(degrees)
        writer.add_page(page)

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def get_page_count(file_bytes: bytes) -> int:
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        return len(reader.pages)
    except Exception as exc:
        raise PDFEngineError(f"Failed to read PDF: {exc}") from exc


def delete_pages(file_bytes: bytes, page_numbers: list[int]) -> bytes:
    """1-indexed page numbers to remove."""
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    total = len(reader.pages)
    remove_set = set(page_numbers)
    if not remove_set - set(range(1, total + 1)) == set():
        raise PDFEngineError(f"Page numbers out of range 1-{total}.")
    if len(remove_set) >= total:
        raise PDFEngineError("Cannot delete every page in the document.")

    writer = pypdf.PdfWriter()
    for i, page in enumerate(reader.pages, start=1):
        if i not in remove_set:
            writer.add_page(page)

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def insert_blank_page(file_bytes: bytes, position: int, width: float = 612, height: float = 792) -> bytes:
    """Insert a blank page at 1-indexed `position` (page becomes the new page at that index)."""
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    total = len(reader.pages)
    if position < 1 or position > total + 1:
        raise PDFEngineError(f"position must be between 1 and {total + 1}.")

    writer = pypdf.PdfWriter()
    for i, page in enumerate(reader.pages, start=1):
        if i == position:
            writer.add_blank_page(width=width, height=height)
        writer.add_page(page)
    if position == total + 1:
        writer.add_blank_page(width=width, height=height)

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def duplicate_page(file_bytes: bytes, page_number: int) -> bytes:
    """1-indexed. The duplicate is inserted immediately after the source page."""
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    total = len(reader.pages)
    if page_number < 1 or page_number > total:
        raise PDFEngineError(f"page_number must be between 1 and {total}.")

    writer = pypdf.PdfWriter()
    for i, page in enumerate(reader.pages, start=1):
        writer.add_page(page)
        if i == page_number:
            writer.add_page(page)

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def reorder_pages(file_bytes: bytes, new_order: list[int]) -> bytes:
    """`new_order` is a 1-indexed permutation of every page in the document,
    e.g. [3, 1, 2] on a 3-page doc moves page 3 to the front."""
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    total = len(reader.pages)
    if sorted(new_order) != list(range(1, total + 1)):
        raise PDFEngineError(f"new_order must be a permutation of 1-{total}.")

    writer = pypdf.PdfWriter()
    for i in new_order:
        writer.add_page(reader.pages[i - 1])

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def add_page_numbers(
    file_bytes: bytes,
    position: str = "bottom-center",
    start_at: int = 1,
    font_size: float = 10,
    fmt: str = "{n}",
) -> bytes:
    """`fmt` may use {n} for the page number and {total} for the page count."""
    doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    try:
        total = doc.page_count
        margin = 24
        for idx, page in enumerate(doc):
            n = start_at + idx
            label = fmt.format(n=n, total=total)
            rect = page.rect
            text_width = pymupdf.get_text_length(label, fontsize=font_size)
            if "left" in position:
                x = rect.x0 + margin
            elif "right" in position:
                x = rect.x1 - margin - text_width
            else:
                x = (rect.x0 + rect.x1) / 2 - text_width / 2
            y = rect.y1 - margin if "bottom" in position else rect.y0 + margin
            page.insert_text((x, y), label, fontsize=font_size, color=(0, 0, 0))
        return doc.tobytes()
    except Exception as exc:
        raise PDFEngineError(f"Failed to add page numbers: {exc}") from exc
    finally:
        doc.close()


def add_header_footer(
    file_bytes: bytes,
    header_text: str | None = None,
    footer_text: str | None = None,
    font_size: float = 9,
) -> bytes:
    doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    try:
        margin = 24
        for page in doc:
            rect = page.rect
            if header_text:
                page.insert_text((rect.x0 + margin, rect.y0 + margin), header_text,
                                  fontsize=font_size, color=(0.35, 0.35, 0.35))
            if footer_text:
                page.insert_text((rect.x0 + margin, rect.y1 - margin), footer_text,
                                  fontsize=font_size, color=(0.35, 0.35, 0.35))
        return doc.tobytes()
    except Exception as exc:
        raise PDFEngineError(f"Failed to add header/footer: {exc}") from exc
    finally:
        doc.close()


def crop_pages(
    file_bytes: bytes,
    margins: dict,
    page_numbers: list[int] | None = None,
) -> bytes:
    """`margins` = {"left": pt, "top": pt, "right": pt, "bottom": pt} trimmed
    inward from each page's existing box. `page_numbers` is 1-indexed;
    None means every page."""
    doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    try:
        target_pages = set(page_numbers) if page_numbers else set(range(1, doc.page_count + 1))
        left = margins.get("left", 0)
        top = margins.get("top", 0)
        right = margins.get("right", 0)
        bottom = margins.get("bottom", 0)
        for i, page in enumerate(doc, start=1):
            if i not in target_pages:
                continue
            rect = page.rect
            new_rect = pymupdf.Rect(rect.x0 + left, rect.y0 + top, rect.x1 - right, rect.y1 - bottom)
            if new_rect.is_empty or new_rect.width <= 0 or new_rect.height <= 0:
                raise PDFEngineError(f"Crop margins leave no visible area on page {i}.")
            page.set_cropbox(new_rect)
        return doc.tobytes()
    except PDFEngineError:
        raise
    except Exception as exc:
        raise PDFEngineError(f"Failed to crop pages: {exc}") from exc
    finally:
        doc.close()


def replace_pages(file_bytes: bytes, replacement_bytes: bytes, page_numbers: list[int]) -> bytes:
    """Replaces each 1-indexed page in `page_numbers` with the corresponding
    page (by position) from `replacement_bytes` — i.e. `page_numbers[0]` is
    replaced by page 1 of the replacement document, `page_numbers[1]` by
    page 2, and so on."""
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    replacement_reader = pypdf.PdfReader(io.BytesIO(replacement_bytes))
    total = len(reader.pages)

    if len(page_numbers) > len(replacement_reader.pages):
        raise PDFEngineError("The replacement document has fewer pages than page numbers given.")
    if any(p < 1 or p > total for p in page_numbers):
        raise PDFEngineError(f"Page numbers must be between 1 and {total}.")

    replace_map = {page_numbers[i]: replacement_reader.pages[i] for i in range(len(page_numbers))}
    writer = pypdf.PdfWriter()
    for i, page in enumerate(reader.pages, start=1):
        writer.add_page(replace_map.get(i, page))

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def get_bookmarks(file_bytes: bytes) -> list[dict]:
    """Returns the PDF's outline/table-of-contents as a flat list of
    {level, title, page} entries (1-indexed pages), matching PyMuPDF's
    `get_toc()` shape."""
    doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    try:
        return [{"level": lvl, "title": title, "page": page} for lvl, title, page in doc.get_toc()]
    finally:
        doc.close()


def set_bookmarks(file_bytes: bytes, bookmarks: list[dict]) -> bytes:
    """Replaces the PDF's outline/table-of-contents wholesale.
    `bookmarks` is a list of {level, title, page} (1-indexed pages)."""
    doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    try:
        toc = [[b["level"], b["title"], b["page"]] for b in bookmarks]
        doc.set_toc(toc)
        return doc.tobytes()
    except Exception as exc:
        raise PDFEngineError(f"Failed to set bookmarks: {exc}") from exc
    finally:
        doc.close()
