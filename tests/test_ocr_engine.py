import io

import pytest

from app.services.pdf_engine import ocr as ocr_engine
from app.services.pdf_engine.conversion import html_to_pdf, pdf_to_txt
from app.services.pdf_engine.core import PDFEngineError


@pytest.fixture
def rendered_text_image() -> bytes:
    """A synthetic 'scanned document' — real text rendered as pixels, no PDF text layer."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (800, 200), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), "PDF360 OCR TEST DOCUMENT", fill="black")
    draw.text((50, 100), "Invoice Number: INV-2026-00042", fill="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_ocr_recognizes_real_text(rendered_text_image):
    """
    The core correctness test for OCR: render known text into an image,
    OCR it, and confirm the exact recognized string comes back — proves
    actual text recognition, not just that the command exits 0.
    """
    searchable_pdf = ocr_engine.ocr_image_to_pdf(rendered_text_image, languages=["english"])
    assert searchable_pdf[:4] == b"%PDF"

    extracted = pdf_to_txt(searchable_pdf)
    assert "INV-2026-00042" in extracted


def test_ocr_skip_text_preserves_existing_content():
    text_pdf = html_to_pdf("<html><body><p>Already has text.</p></body></html>")
    result = ocr_engine.ocr_pdf(text_pdf, languages=["english"], force=False)
    assert "Already has text." in pdf_to_txt(result)


def test_ocr_unsupported_language_raises():
    text_pdf = html_to_pdf("<html><body><p>Text.</p></body></html>")
    with pytest.raises(PDFEngineError):
        ocr_engine.ocr_pdf(text_pdf, languages=["klingon"])
