"""
Conversion engine — the only place that shells out to LibreOffice/Poppler
or does format transcoding. Like pdf_engine/core.py, every function takes
and returns raw bytes so it has no knowledge of storage, jobs, or the DB.

Office format conversions (Word/Excel/PowerPoint <-> PDF) go through
LibreOffice headless, since it's the only reliable way to preserve
formatting fidelity without a commercial SDK. This means the deployment
environment must have `soffice` on PATH — documented in docs/03-deployment.md.
"""
import io
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from app.services.pdf_engine.core import PDFEngineError

_OFFICE_TIMEOUT_SECONDS = 120


def _run_soffice_convert(input_bytes: bytes, input_suffix: str, output_ext: str) -> bytes:
    """
    Runs `soffice --headless --convert-to <ext>` in an isolated temp dir.
    LibreOffice writes the output as <original_stem>.<output_ext> in the
    same directory, so we locate it by extension rather than guessing a name.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        input_path = Path(tmp_dir) / f"input{input_suffix}"
        input_path.write_bytes(input_bytes)

        result = subprocess.run(
            [
                "soffice", "--headless", "--norestore",
                "--convert-to", output_ext,
                "--outdir", tmp_dir,
                str(input_path),
            ],
            capture_output=True,
            timeout=_OFFICE_TIMEOUT_SECONDS,
        )
        if result.returncode != 0:
            raise PDFEngineError(f"LibreOffice conversion failed: {result.stderr.decode(errors='replace')}")

        output_path = Path(tmp_dir) / f"input.{output_ext}"
        if not output_path.exists():
            raise PDFEngineError("LibreOffice did not produce an output file.")
        return output_path.read_bytes()


def office_to_pdf(file_bytes: bytes, source_suffix: str) -> bytes:
    """source_suffix e.g. '.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt'."""
    return _run_soffice_convert(file_bytes, source_suffix, "pdf")


def pdf_to_docx(file_bytes: bytes) -> bytes:
    """
    LibreOffice headless cannot reliably export PDF->DOCX (it opens PDFs as
    a Draw/graphics document, not editable text, and the export filter
    rejects it) — confirmed by direct testing, not assumed. Instead we
    extract text per page with PyMuPDF and rebuild a Word document with
    python-docx. This loses original layout/fonts (a fundamental limit of
    "PDF to Word" without a commercial layout-reconstruction engine — no
    PDF tool fully solves this either) but produces a real, editable,
    correctly-ordered text document.
    """
    import pymupdf
    from docx import Document as DocxDocument

    try:
        src = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc

    try:
        out_doc = DocxDocument()
        for i, page in enumerate(src):
            text = page.get_text()
            for para in text.split("\n"):
                if para.strip():
                    out_doc.add_paragraph(para)
            if i < len(src) - 1:
                out_doc.add_page_break()
        buf = io.BytesIO()
        out_doc.save(buf)
        return buf.getvalue()
    finally:
        src.close()


def pdf_to_pptx(file_bytes: bytes) -> bytes:
    """
    Renders each PDF page to a high-resolution image and places it as a
    full-slide picture. This is the approach that preserves visual fidelity
    (the thing PPT export is usually wanted for — keeping the deck
    "looking right") since PDFs don't carry reconstructable slide/shape
    data the way a native PPTX does.
    """
    from pptx import Presentation
    from pptx.util import Emu

    page_images = pdf_to_images(file_bytes, fmt="png", dpi=150)
    if not page_images:
        raise PDFEngineError("PDF has no pages to convert.")

    prs = Presentation()
    prs.slide_width = Emu(12192000)   # 16:9 widescreen, 13.33in
    prs.slide_height = Emu(6858000)
    blank_layout = prs.slide_layouts[6]

    for img_bytes in page_images:
        slide = prs.slides.add_slide(blank_layout)
        slide.shapes.add_picture(
            io.BytesIO(img_bytes), 0, 0, width=prs.slide_width, height=prs.slide_height
        )

    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()


def pdf_to_xlsx(file_bytes: bytes) -> bytes:
    """
    Extracts detected tables via pdfplumber and writes one worksheet per
    table found. If a PDF has no detectable tables, raises PDFEngineError
    rather than silently producing an empty workbook — the caller/route
    surfaces this as a clear "no tables found" error to the user.

    Known limitation (confirmed by testing, not theoretical): pdfplumber's
    default detection strategy relies on visible ruling lines. A PDF whose
    tables are laid out with whitespace/alignment only, no drawn borders,
    will not be detected. If this turns out to matter in practice, switch
    to `extract_tables(table_settings={"vertical_strategy": "text",
    "horizontal_strategy": "text"})` for line-less tables — noted here
    rather than silently guessing which strategy the AI table-extraction
    feature (Phase 13) should use.
    """
    import pdfplumber
    from openpyxl import Workbook

    wb = Workbook()
    wb.remove(wb.active)  # remove default blank sheet
    table_count = 0

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                for t_idx, table in enumerate(tables, start=1):
                    table_count += 1
                    sheet_name = f"Page{page_num}_Table{t_idx}"[:31]  # Excel sheet name limit
                    ws = wb.create_sheet(title=sheet_name)
                    for row in table:
                        ws.append([cell if cell is not None else "" for cell in row])
    except Exception as exc:
        raise PDFEngineError(f"Failed to extract tables: {exc}") from exc

    if table_count == 0:
        raise PDFEngineError("No tables were detected in this PDF.")

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def images_to_pdf(image_bytes_list: list[bytes]) -> bytes:
    if not image_bytes_list:
        raise PDFEngineError("At least one image is required.")
    images = []
    for img_bytes in image_bytes_list:
        try:
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            images.append(img)
        except Exception as exc:
            raise PDFEngineError(f"Failed to read image: {exc}") from exc

    output = io.BytesIO()
    images[0].save(output, format="PDF", save_all=True, append_images=images[1:])
    return output.getvalue()


def pdf_to_images(file_bytes: bytes, fmt: str = "png", dpi: int = 150) -> list[bytes]:
    """Renders each page to an image using PyMuPDF (no external process needed)."""
    import pymupdf

    fmt = fmt.lower()
    if fmt not in ("png", "jpg", "jpeg"):
        raise PDFEngineError(f"Unsupported image format: {fmt}")

    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc

    try:
        zoom = dpi / 72
        matrix = pymupdf.Matrix(zoom, zoom)
        results = []
        for page in doc:
            pix = page.get_pixmap(matrix=matrix)
            results.append(pix.tobytes(fmt if fmt != "jpg" else "jpeg"))
        return results
    finally:
        doc.close()


def html_to_pdf(html: str) -> bytes:
    return _run_soffice_convert(html.encode("utf-8"), ".html", "pdf")


def markdown_to_pdf(markdown_text: str) -> bytes:
    """
    Converts Markdown -> HTML -> PDF. A minimal, dependency-free Markdown
    subset (headings, bold/italic, lists, paragraphs) is handled here;
    swap in `markdown` or `mistune` if richer syntax is needed later.
    """
    import html as html_lib
    import re

    lines = markdown_text.splitlines()
    html_parts = ["<html><body style='font-family: sans-serif; padding: 40px;'>"]
    in_list = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            continue
        heading_match = re.match(r"^(#{1,6})\s+(.*)", stripped)
        if heading_match:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            level = len(heading_match.group(1))
            html_parts.append(f"<h{level}>{html_lib.escape(heading_match.group(2))}</h{level}>")
            continue
        if stripped.startswith(("- ", "* ")):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{html_lib.escape(stripped[2:])}</li>")
            continue
        if in_list:
            html_parts.append("</ul>")
            in_list = False
        text = html_lib.escape(stripped)
        text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
        html_parts.append(f"<p>{text}</p>")
    if in_list:
        html_parts.append("</ul>")
    html_parts.append("</body></html>")
    return html_to_pdf("".join(html_parts))


def pdf_to_txt(file_bytes: bytes) -> str:
    import pymupdf

    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc
    try:
        return "\n\n".join(page.get_text() for page in doc)
    finally:
        doc.close()


def pdf_to_html(file_bytes: bytes) -> str:
    """Per-page HTML export preserving basic layout, via PyMuPDF's built-in converter."""
    import pymupdf

    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc
    try:
        parts = ["<html><head><meta charset='utf-8'></head><body>"]
        for i, page in enumerate(doc):
            parts.append(f"<!-- page {i + 1} -->")
            parts.append(page.get_text("html"))
        parts.append("</body></html>")
        return "".join(parts)
    finally:
        doc.close()


def pdf_to_epub(file_bytes: bytes, title: str = "Untitled") -> bytes:
    """
    Minimal but valid EPUB3 (one XHTML chapter per PDF page, no image
    extraction) built by hand — avoids adding a new heavyweight dependency
    (e.g. Calibre/ebooklib) for a single conversion target.
    """
    import io
    import zipfile
    import html as html_lib

    import pymupdf

    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFEngineError(f"Failed to open PDF: {exc}") from exc

    try:
        chapters = []
        for i, page in enumerate(doc, start=1):
            text = html_lib.escape(page.get_text()).replace("\n", "<br/>")
            chapters.append(
                f"<?xml version='1.0' encoding='utf-8'?>"
                f"<html xmlns='http://www.w3.org/1999/xhtml'><head><title>Page {i}</title></head>"
                f"<body><h2>Page {i}</h2><p>{text}</p></body></html>"
            )
    finally:
        doc.close()

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
        zf.writestr("META-INF/container.xml", (
            "<?xml version='1.0'?><container version='1.0' "
            "xmlns='urn:oasis:names:tc:opendocument:xmlns:container'>"
            "<rootfiles><rootfile full-path='OEBPS/content.opf' "
            "media-type='application/oebps-package+xml'/></rootfiles></container>"
        ))
        manifest_items = "".join(
            f"<item id='ch{i}' href='chapter{i}.xhtml' media-type='application/xhtml+xml'/>"
            for i in range(1, len(chapters) + 1)
        )
        spine_items = "".join(f"<itemref idref='ch{i}'/>" for i in range(1, len(chapters) + 1))
        zf.writestr("OEBPS/content.opf", (
            "<?xml version='1.0' encoding='utf-8'?>"
            "<package xmlns='http://www.idpf.org/2007/opf' version='3.0' unique-identifier='bookid'>"
            f"<metadata xmlns:dc='http://purl.org/dc/elements/1.1/'>"
            f"<dc:title>{html_lib.escape(title)}</dc:title>"
            "<dc:language>en</dc:language>"
            "<dc:identifier id='bookid'>urn:uuid:pdf360-export</dc:identifier>"
            "</metadata>"
            f"<manifest>{manifest_items}</manifest>"
            f"<spine>{spine_items}</spine>"
            "</package>"
        ))
        for i, chapter_html in enumerate(chapters, start=1):
            zf.writestr(f"OEBPS/chapter{i}.xhtml", chapter_html)
    return buf.getvalue()
