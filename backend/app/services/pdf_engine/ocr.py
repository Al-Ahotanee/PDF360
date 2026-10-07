"""
OCR engine — wraps ocrmypdf (which itself wraps Tesseract + Ghostscript).
Like conversion.py, this is the only module that shells out for OCR;
routes/services never call ocrmypdf or tesseract directly.

Deployment requirement: `ocrmypdf`, `tesseract`, and `ghostscript` must be
installed on PATH. Confirmed working versions during development:
ocrmypdf 17.8, tesseract 5.3, ghostscript 10.02.
"""
import subprocess
import tempfile
from pathlib import Path

from app.services.pdf_engine.core import PDFEngineError

_OCR_TIMEOUT_SECONDS = 300

# ISO 639-2 codes ocrmypdf/tesseract expect, mapped from friendly names —
# extend as more language packs are installed on the deployment image.
SUPPORTED_LANGUAGES = {
    "english": "eng",
    "french": "fra",
    "spanish": "spa",
    "arabic": "ara",
    "hausa": "hau",
}


def ocr_pdf(file_bytes: bytes, languages: list[str] | None = None, force: bool = False) -> bytes:
    """
    Runs OCR and returns a searchable PDF (original page images preserved,
    an invisible text layer added). `languages` are friendly names from
    SUPPORTED_LANGUAGES (e.g. ["english", "hausa"]); defaults to English.

    `force`=True re-OCRs pages that already have text (ocrmypdf's
    --force-ocr) — needed when a PDF has a broken/garbage existing text
    layer, common with poorly-scanned documents.
    """
    lang_codes = [SUPPORTED_LANGUAGES[l.lower()] for l in (languages or ["english"]) if l.lower() in SUPPORTED_LANGUAGES]
    if not lang_codes:
        raise PDFEngineError(f"No supported OCR languages in: {languages}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        input_path = Path(tmp_dir) / "input.pdf"
        output_path = Path(tmp_dir) / "output.pdf"
        input_path.write_bytes(file_bytes)

        cmd = [
            "ocrmypdf",
            "--language", "+".join(lang_codes),
            "--output-type", "pdf",
            "--skip-text" if not force else "--force-ocr",
            str(input_path),
            str(output_path),
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=_OCR_TIMEOUT_SECONDS)

        # ocrmypdf exit code 6 = "already has text, nothing to do" when
        # --skip-text is set and every page already has a text layer —
        # treat this as success and return the (unchanged) input.
        if result.returncode == 6:
            return file_bytes
        if result.returncode != 0:
            raise PDFEngineError(f"OCR failed: {result.stderr.decode(errors='replace')}")
        if not output_path.exists():
            raise PDFEngineError("OCR did not produce an output file.")
        return output_path.read_bytes()


def ocr_image_to_pdf(image_bytes: bytes, languages: list[str] | None = None) -> bytes:
    """OCRs a standalone image (receipt, photo of a document) into a searchable PDF."""
    from app.services.pdf_engine.conversion import images_to_pdf

    pdf_bytes = images_to_pdf([image_bytes])
    return ocr_pdf(pdf_bytes, languages=languages, force=True)
