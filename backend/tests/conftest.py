"""
Shared fixtures — build real PDFs/images in-memory so engine tests exercise
actual PyMuPDF/pypdf/LibreOffice/Tesseract behavior, not mocks. This
mirrors the manual verification done during development (see
docs/02-architecture.md); persisting it here turns that one-off checking
into a permanent regression suite.
"""
import io

import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def _make_pdf(pages: int = 3, text_prefix: str = "Test Page") -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    for i in range(pages):
        c.drawString(100, 700, f"{text_prefix} {i + 1}")
        c.rect(100, 500, 200, 150, fill=1)
        c.showPage()
    c.save()
    return buf.getvalue()


@pytest.fixture
def make_pdf():
    return _make_pdf


@pytest.fixture
def sample_pdf() -> bytes:
    return _make_pdf(3)


@pytest.fixture
def sample_image() -> bytes:
    from PIL import Image

    img = Image.new("RGB", (200, 200), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
