from pydantic import BaseModel, Field


class CreateBlankRequest(BaseModel):
    pages: int = 1
    page_size: str = "letter"  # letter | a4


class CreateFromTextRequest(BaseModel):
    text: str
    page_size: str = "letter"
    font_size: int = 11


class InvoiceParty(BaseModel):
    name: str
    address: str | None = None


class InvoiceLineItem(BaseModel):
    description: str
    quantity: float = 1
    unit_price: float = 0


class CreateInvoiceRequest(BaseModel):
    invoice_number: str
    date: str
    due_date: str | None = None
    from_: InvoiceParty = Field(alias="from")
    to: InvoiceParty
    line_items: list[InvoiceLineItem]
    notes: str | None = None
    currency: str = "USD"

    model_config = {"populate_by_name": True}


class CreateCertificateRequest(BaseModel):
    recipient: str
    title: str = "Certificate of Achievement"
    body: str = ""
    date: str
    signer: str | None = None
    signer_title: str | None = None


class ReportSection(BaseModel):
    heading: str
    body: str = ""


class CreateReportRequest(BaseModel):
    title: str
    subtitle: str | None = None
    sections: list[ReportSection]
