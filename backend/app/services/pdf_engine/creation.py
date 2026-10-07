"""
PDF creation from scratch — the SRS's "PDF Creation" section covers this
separately from "Conversion" (Word/HTML/Markdown -> PDF, which already
exist in conversion.py). This module uses ReportLab directly rather than
shelling out to LibreOffice, since these are programmatic layouts (a
blank page, wrapped text, a table) rather than rendering an existing
document format.
"""
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, LETTER, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.services.pdf_engine.core import PDFEngineError

_PAGE_SIZES = {"letter": LETTER, "a4": A4}


def create_blank_pdf(pages: int = 1, page_size: str = "letter") -> bytes:
    if pages < 1:
        raise PDFEngineError("pages must be at least 1.")
    size = _PAGE_SIZES.get(page_size.lower())
    if size is None:
        raise PDFEngineError(f"Unknown page_size: {page_size}. Use 'letter' or 'a4'.")

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=size)
    for _ in range(pages):
        c.showPage()
    c.save()
    return buf.getvalue()


def text_to_pdf(text: str, page_size: str = "letter", font_size: int = 11) -> bytes:
    """Plain text -> PDF with word-wrap and automatic pagination —
    distinct from `conversion.markdown_to_pdf`, which interprets Markdown
    syntax; this treats the input as literal text."""
    size = _PAGE_SIZES.get(page_size.lower())
    if size is None:
        raise PDFEngineError(f"Unknown page_size: {page_size}. Use 'letter' or 'a4'.")

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle("body", parent=styles["Normal"], fontSize=font_size, leading=font_size * 1.4)

    import html as html_lib
    paragraphs = [
        Paragraph(html_lib.escape(p).replace("\n", "<br/>"), body_style)
        for p in text.split("\n\n")
        if p.strip()
    ] or [Paragraph("", body_style)]

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=size, topMargin=0.75 * inch, bottomMargin=0.75 * inch,
                             leftMargin=0.75 * inch, rightMargin=0.75 * inch)
    flowables = []
    for p in paragraphs:
        flowables.append(p)
        flowables.append(Spacer(1, 10))
    doc.build(flowables)
    return buf.getvalue()


def generate_invoice(data: dict) -> bytes:
    """
    `data` shape:
    {
      "invoice_number": str, "date": str, "due_date": str | None,
      "from": {"name": str, "address": str | None},
      "to": {"name": str, "address": str | None},
      "line_items": [{"description": str, "quantity": number, "unit_price": number}],
      "notes": str | None, "currency": str  # e.g. "USD"
    }
    """
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=LETTER, topMargin=0.75 * inch, bottomMargin=0.75 * inch,
                                 leftMargin=0.75 * inch, rightMargin=0.75 * inch)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("title", parent=styles["Title"], alignment=0)
        flowables = [Paragraph("INVOICE", title_style), Spacer(1, 4)]

        meta_rows = [["Invoice #", data.get("invoice_number", "")], ["Date", data.get("date", "")]]
        if data.get("due_date"):
            meta_rows.append(["Due", data["due_date"]])
        flowables.append(Table(meta_rows, colWidths=[80, 200], style=TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 9), ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
        ])))
        flowables.append(Spacer(1, 16))

        frm, to = data.get("from", {}), data.get("to", {})
        addr_rows = [[
            Paragraph(f"<b>From</b><br/>{frm.get('name', '')}<br/>{frm.get('address', '') or ''}", styles["Normal"]),
            Paragraph(f"<b>Bill To</b><br/>{to.get('name', '')}<br/>{to.get('address', '') or ''}", styles["Normal"]),
        ]]
        flowables.append(Table(addr_rows, colWidths=[240, 240]))
        flowables.append(Spacer(1, 20))

        currency = data.get("currency", "USD")
        items = data.get("line_items", [])
        item_rows = [["Description", "Qty", "Unit Price", "Amount"]]
        total = 0.0
        for item in items:
            qty = float(item.get("quantity", 1))
            price = float(item.get("unit_price", 0))
            amount = qty * price
            total += amount
            item_rows.append([item.get("description", ""), str(qty), f"{currency} {price:,.2f}", f"{currency} {amount:,.2f}"])
        item_rows.append(["", "", "Total", f"{currency} {total:,.2f}"])

        table = Table(item_rows, colWidths=[240, 60, 100, 100])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -2), 0.5, colors.HexColor("#dddddd")),
            ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ]))
        flowables.append(table)

        if data.get("notes"):
            flowables.append(Spacer(1, 20))
            flowables.append(Paragraph(f"<b>Notes</b><br/>{data['notes']}", styles["Normal"]))

        doc.build(flowables)
        return buf.getvalue()
    except PDFEngineError:
        raise
    except Exception as exc:
        raise PDFEngineError(f"Failed to generate invoice: {exc}") from exc


def generate_certificate(data: dict) -> bytes:
    """
    `data` shape: {"recipient": str, "title": str, "body": str, "date": str,
                    "signer": str | None, "signer_title": str | None}
    """
    try:
        buf = io.BytesIO()
        size = landscape(LETTER)
        c = canvas.Canvas(buf, pagesize=size)
        width, height = size

        c.setStrokeColor(colors.HexColor("#c9a227"))
        c.setLineWidth(3)
        c.rect(30, 30, width - 60, height - 60)
        c.setLineWidth(1)
        c.rect(40, 40, width - 80, height - 80)

        c.setFont("Helvetica-Bold", 30)
        c.setFillColor(colors.HexColor("#1a1a2e"))
        c.drawCentredString(width / 2, height - 130, data.get("title", "Certificate of Achievement"))

        c.setFont("Helvetica", 14)
        c.setFillColor(colors.grey)
        c.drawCentredString(width / 2, height - 165, "This certificate is proudly presented to")

        c.setFont("Helvetica-Bold", 26)
        c.setFillColor(colors.HexColor("#c9a227"))
        c.drawCentredString(width / 2, height - 210, data.get("recipient", ""))

        c.setFont("Helvetica", 13)
        c.setFillColor(colors.HexColor("#333333"))
        body = data.get("body", "")
        c.drawCentredString(width / 2, height - 250, body[:120])

        c.setFont("Helvetica", 11)
        c.setFillColor(colors.grey)
        c.drawCentredString(width / 2, 100, data.get("date", ""))

        if data.get("signer"):
            c.line(width / 2 - 100, 80, width / 2 + 100, 80)
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.black)
            c.drawCentredString(width / 2, 65, data["signer"])
            if data.get("signer_title"):
                c.setFont("Helvetica", 9)
                c.setFillColor(colors.grey)
                c.drawCentredString(width / 2, 52, data["signer_title"])

        c.save()
        return buf.getvalue()
    except Exception as exc:
        raise PDFEngineError(f"Failed to generate certificate: {exc}") from exc


def generate_report(data: dict) -> bytes:
    """
    `data` shape: {"title": str, "subtitle": str | None,
                    "sections": [{"heading": str, "body": str}]}
    """
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=LETTER, topMargin=1 * inch, bottomMargin=1 * inch,
                                 leftMargin=1 * inch, rightMargin=1 * inch)
        styles = getSampleStyleSheet()
        flowables = [Paragraph(data.get("title", "Report"), styles["Title"])]
        if data.get("subtitle"):
            flowables.append(Paragraph(data["subtitle"], styles["Italic"]))
        flowables.append(Spacer(1, 20))

        for section in data.get("sections", []):
            flowables.append(Paragraph(section.get("heading", ""), styles["Heading2"]))
            flowables.append(Spacer(1, 6))
            flowables.append(Paragraph(section.get("body", "").replace("\n", "<br/>"), styles["Normal"]))
            flowables.append(Spacer(1, 16))

        doc.build(flowables)
        return buf.getvalue()
    except Exception as exc:
        raise PDFEngineError(f"Failed to generate report: {exc}") from exc
