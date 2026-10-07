import io

import pypdf
import pytest

from app.services.pdf_engine import editor
from app.services.pdf_engine.core import PDFEngineError


def _find_annot(pdf_bytes: bytes, subtype: str):
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    for a in reader.pages[0].get("/Annots") or []:
        obj = a.get_object()
        if obj.get("/Subtype") == subtype:
            return obj
    return None


# Verification here deliberately uses pypdf's structural reading, not
# PyMuPDF's own Annot.type property — confirmed during development that
# PyMuPDF 1.28.0 in this environment unreliably re-reads annotation
# objects it just created (intermittent "annotation not bound to any
# page" errors and one reproducible segfault), while `qpdf --check` and
# pypdf both confirm the actual PDF output is structurally valid every
# time. pypdf is the reliable verification tool for this suite.


def test_add_highlight(sample_pdf):
    result = editor.add_highlight(sample_pdf, 1, 50, 50, 300, 100, color="#FFD700")
    assert _find_annot(result, "/Highlight") is not None


def test_add_text_box(sample_pdf):
    result = editor.add_text_box(sample_pdf, 1, 50, 150, 300, 200, "Reviewer comment", font_size=14)
    obj = _find_annot(result, "/FreeText")
    assert obj is not None
    assert obj["/Contents"] == "Reviewer comment"


def test_add_sticky_note(sample_pdf):
    result = editor.add_sticky_note(sample_pdf, 1, 400, 50, "Check this figure")
    obj = _find_annot(result, "/Text")
    assert obj is not None
    assert obj["/Contents"] == "Check this figure"


def test_add_freehand_drawing(sample_pdf):
    strokes = [[(60, 300), (80, 320), (100, 300), (120, 330)]]
    result = editor.add_freehand_drawing(sample_pdf, 1, strokes, color="#FF0000", width=3)
    assert _find_annot(result, "/Ink") is not None


def test_freehand_drawing_requires_min_points(sample_pdf):
    with pytest.raises(PDFEngineError):
        editor.add_freehand_drawing(sample_pdf, 1, [[(10, 10)]])


def test_annotation_out_of_range_page_raises(sample_pdf):
    with pytest.raises(PDFEngineError):
        editor.add_highlight(sample_pdf, 99, 0, 0, 10, 10)


def test_invalid_hex_color_raises(sample_pdf):
    with pytest.raises(PDFEngineError):
        editor.add_highlight(sample_pdf, 1, 0, 0, 10, 10, color="not-a-color")


def test_form_field_lifecycle(sample_pdf):
    with_field = editor.add_text_form_field(sample_pdf, 1, 50, 300, 250, 330, "full_name")
    fields = editor.list_form_fields(with_field)
    assert len(fields) == 1
    assert fields[0]["field_name"] == "full_name"

    with_checkbox = editor.add_checkbox_form_field(with_field, 1, 50, 350, 70, 370, "agree_terms")
    fields = editor.list_form_fields(with_checkbox)
    assert len(fields) == 2

    filled = editor.fill_form_fields(with_checkbox, {"full_name": "Shafiu Ibrahim", "agree_terms": True})
    fields = editor.list_form_fields(filled)
    name_field = next(f for f in fields if f["field_name"] == "full_name")
    assert name_field["field_value"] == "Shafiu Ibrahim"


def test_fill_unknown_field_raises(sample_pdf):
    with_field = editor.add_text_form_field(sample_pdf, 1, 50, 300, 250, 330, "full_name")
    with pytest.raises(PDFEngineError):
        editor.fill_form_fields(with_field, {"nonexistent_field": "x"})
