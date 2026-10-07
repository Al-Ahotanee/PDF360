"""
Editor engine — real PDF annotations and form fields via PyMuPDF, not
image overlays. Annotations added here are genuine PDF objects: they
survive in any PDF viewer, can be edited/removed later, and (for
freetext/highlight) are searchable/selectable — verified by testing that
`page.annots()` reports the correct type and count after each operation.

Coordinates throughout are in PDF points, page-1-indexed, origin top-left
— matching the page-preview endpoint's coordinate transform in
routes/v1/files.py, so the frontend's canvas picker works unchanged for
every tool in the editor (redaction, highlight, freetext, ink, sticky note).
"""
import io

import pymupdf

from app.services.pdf_engine.core import PDFEngineError

_HEX_COLOR_DEFAULT = (1, 0.85, 0.2)  # highlight yellow, as an RGB 0-1 tuple


def _hex_to_rgb01(hex_color: str) -> tuple[float, float, float]:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise PDFEngineError(f"Invalid hex color: {hex_color}")
    try:
        r, g, b = (int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))
    except ValueError as exc:
        raise PDFEngineError(f"Invalid hex color: {hex_color}") from exc
    return (r, g, b)


def add_highlight(file_bytes: bytes, page: int, x0: float, y0: float, x1: float, y1: float, color: str | None = None) -> bytes:
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc
    try:
        if page < 1 or page > len(doc):
            raise PDFEngineError(f"Page {page} out of range.")
        p = doc[page - 1]
        annot = p.add_highlight_annot(pymupdf.Rect(x0, y0, x1, y1))
        annot.set_colors(stroke=_hex_to_rgb01(color) if color else _HEX_COLOR_DEFAULT)
        annot.update()
        return doc.tobytes()
    finally:
        doc.close()


def add_text_box(file_bytes: bytes, page: int, x0: float, y0: float, x1: float, y1: float,
                  text: str, font_size: float = 12, color: str | None = None) -> bytes:
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc
    try:
        if page < 1 or page > len(doc):
            raise PDFEngineError(f"Page {page} out of range.")
        p = doc[page - 1]
        p.add_freetext_annot(
            pymupdf.Rect(x0, y0, x1, y1), text, fontsize=font_size,
            text_color=_hex_to_rgb01(color) if color else (0, 0, 0),
        )
        return doc.tobytes()
    finally:
        doc.close()


def add_sticky_note(file_bytes: bytes, page: int, x: float, y: float, note: str) -> bytes:
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc
    try:
        if page < 1 or page > len(doc):
            raise PDFEngineError(f"Page {page} out of range.")
        p = doc[page - 1]
        annot = p.add_text_annot(pymupdf.Point(x, y), note)
        annot.update()
        return doc.tobytes()
    finally:
        doc.close()


def add_freehand_drawing(file_bytes: bytes, page: int, strokes: list[list[tuple[float, float]]],
                          color: str | None = None, width: float = 2.0) -> bytes:
    """
    strokes: list of strokes, each a list of (x, y) points forming one
    continuous pen stroke — matches how a canvas pointer-drag naturally
    produces points, so the frontend can send raw mouse-move samples with
    no client-side conversion.
    """
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc
    try:
        if page < 1 or page > len(doc):
            raise PDFEngineError(f"Page {page} out of range.")
        if not strokes or any(len(s) < 2 for s in strokes):
            raise PDFEngineError("Each stroke needs at least 2 points.")
        p = doc[page - 1]
        annot = p.add_ink_annot(strokes)
        annot.set_colors(stroke=_hex_to_rgb01(color) if color else (0, 0, 0))
        annot.set_border(width=width)
        annot.update()
        return doc.tobytes()
    finally:
        doc.close()


def add_text_form_field(file_bytes: bytes, page: int, x0: float, y0: float, x1: float, y1: float,
                         field_name: str, default_value: str = "") -> bytes:
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc
    try:
        if page < 1 or page > len(doc):
            raise PDFEngineError(f"Page {page} out of range.")
        p = doc[page - 1]
        widget = pymupdf.Widget()
        widget.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
        widget.field_name = field_name
        widget.field_value = default_value
        widget.rect = pymupdf.Rect(x0, y0, x1, y1)
        p.add_widget(widget)
        return doc.tobytes()
    finally:
        doc.close()


def add_checkbox_form_field(file_bytes: bytes, page: int, x0: float, y0: float, x1: float, y1: float,
                             field_name: str, checked: bool = False) -> bytes:
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc
    try:
        if page < 1 or page > len(doc):
            raise PDFEngineError(f"Page {page} out of range.")
        p = doc[page - 1]
        widget = pymupdf.Widget()
        widget.field_type = pymupdf.PDF_WIDGET_TYPE_CHECKBOX
        widget.field_name = field_name
        widget.field_value = checked
        widget.rect = pymupdf.Rect(x0, y0, x1, y1)
        p.add_widget(widget)
        return doc.tobytes()
    finally:
        doc.close()


def fill_form_fields(file_bytes: bytes, values: dict[str, str | bool]) -> bytes:
    """values: {field_name: new_value} — matches by widget.field_name."""
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc
    try:
        matched = set()
        for p in doc:
            for widget in p.widgets():
                if widget.field_name in values:
                    widget.field_value = values[widget.field_name]
                    widget.update()
                    matched.add(widget.field_name)
        missing = set(values) - matched
        if missing:
            raise PDFEngineError(f"Form fields not found: {sorted(missing)}")
        return doc.tobytes()
    finally:
        doc.close()


def list_form_fields(file_bytes: bytes) -> list[dict]:
    doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    try:
        fields = []
        for page_num, p in enumerate(doc, start=1):
            for widget in p.widgets():
                fields.append({
                    "page": page_num,
                    "field_name": widget.field_name,
                    "field_type": widget.field_type_string,
                    "field_value": widget.field_value,
                })
        return fields
    finally:
        doc.close()


def add_underline(file_bytes: bytes, page: int, x0: float, y0: float, x1: float, y1: float, color: str | None = None) -> bytes:
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc
    try:
        if page < 1 or page > len(doc):
            raise PDFEngineError(f"Page {page} out of range.")
        p = doc[page - 1]
        annot = p.add_underline_annot(pymupdf.Rect(x0, y0, x1, y1))
        annot.set_colors(stroke=_hex_to_rgb01(color) if color else _HEX_COLOR_DEFAULT)
        annot.update()
        return doc.tobytes()
    finally:
        doc.close()


def add_strikethrough(file_bytes: bytes, page: int, x0: float, y0: float, x1: float, y1: float, color: str | None = None) -> bytes:
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc
    try:
        if page < 1 or page > len(doc):
            raise PDFEngineError(f"Page {page} out of range.")
        p = doc[page - 1]
        annot = p.add_strikeout_annot(pymupdf.Rect(x0, y0, x1, y1))
        annot.set_colors(stroke=_hex_to_rgb01(color) if color else (1, 0, 0))
        annot.update()
        return doc.tobytes()
    finally:
        doc.close()


def add_whiteout(file_bytes: bytes, page: int, x0: float, y0: float, x1: float, y1: float) -> bytes:
    """Paints an opaque white rectangle over the given area — cosmetic
    cover-up (the original content is still present underneath in the
    file), unlike `/pdf/redact` which actually deletes the underlying
    content. That distinction matches the SRS listing "Whiteout" and
    "Redaction" as two separate features."""
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc
    try:
        if page < 1 or page > len(doc):
            raise PDFEngineError(f"Page {page} out of range.")
        p = doc[page - 1]
        p.draw_rect(pymupdf.Rect(x0, y0, x1, y1), color=(1, 1, 1), fill=(1, 1, 1), overlay=True)
        return doc.tobytes()
    finally:
        doc.close()
