import pytest

from app.services.pdf_engine import security as sec
from app.services.pdf_engine.conversion import html_to_pdf, pdf_to_txt
from app.services.pdf_engine.core import PDFEngineError


@pytest.fixture
def confidential_pdf() -> bytes:
    return html_to_pdf(
        "<html><body style='padding:40px'><h1>Confidential Report</h1>"
        "<p>SSN: 123-45-6789. Public info stays here.</p></body></html>"
    )


def test_encrypt_decrypt_round_trip(confidential_pdf):
    encrypted = sec.encrypt_pdf(confidential_pdf, user_password="secret123")
    assert sec.is_encrypted(encrypted)

    decrypted = sec.decrypt_pdf(encrypted, "secret123")
    assert not sec.is_encrypted(decrypted)
    assert "Confidential Report" in pdf_to_txt(decrypted)


def test_decrypt_wrong_password_raises(confidential_pdf):
    encrypted = sec.encrypt_pdf(confidential_pdf, user_password="secret123")
    with pytest.raises(PDFEngineError):
        sec.decrypt_pdf(encrypted, "wrongpassword")


def test_encrypt_requires_password(confidential_pdf):
    with pytest.raises(PDFEngineError):
        sec.encrypt_pdf(confidential_pdf, user_password="")


def test_watermark_preserves_original_content(confidential_pdf):
    watermarked = sec.add_watermark(confidential_pdf, "CONFIDENTIAL - PDF360")
    text = pdf_to_txt(watermarked)
    assert "CONFIDENTIAL" in text
    assert "Confidential Report" in text


def test_metadata_round_trip(confidential_pdf):
    tagged = sec.set_metadata(confidential_pdf, {"Title": "PDF360 Test Doc", "Author": "Test"})
    meta = sec.get_metadata(tagged)
    assert meta.get("Title") == "PDF360 Test Doc"

    cleared = sec.remove_metadata(tagged)
    assert not sec.get_metadata(cleared).get("Title")


def test_redaction_genuinely_removes_content(confidential_pdf):
    """
    The core correctness test for redaction: locate the SSN's real
    coordinates, redact that box, and confirm it's gone from extracted
    text (not just visually covered) while surrounding content survives.
    """
    import pymupdf

    doc = pymupdf.open(stream=confidential_pdf, filetype="pdf")
    hits = doc[0].search_for("123-45-6789")
    doc.close()
    assert hits, "test setup: SSN text must be locatable"

    rect = hits[0]
    redacted = sec.redact_areas(
        confidential_pdf,
        [{"page": 1, "x0": rect.x0, "y0": rect.y0, "x1": rect.x1, "y1": rect.y1}],
    )
    after_text = pdf_to_txt(redacted)
    assert "123-45-6789" not in after_text
    assert "Confidential Report" in after_text
    assert "Public info stays here" in after_text
