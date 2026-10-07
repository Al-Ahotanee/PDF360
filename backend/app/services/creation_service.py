import io
import uuid

from sqlalchemy.orm import Session

from app.models.file import File
from app.repositories.file_repository import FileRepository
from app.services.pdf_engine import creation
from app.services.storage.factory import get_storage_provider


class CreationService:
    """
    Unlike PDFService/EditorService, these operations have no source file —
    they produce a brand-new PDF from parameters alone. Kept synchronous
    (like EditorService) since ReportLab generation of a single document is
    fast; there's no batch/multi-minute case here to justify a Celery job.
    """

    def __init__(self, db: Session):
        self.db = db
        self.files = FileRepository(db)
        self.storage = get_storage_provider()

    def _save(self, owner_id: uuid.UUID, filename: str, data: bytes) -> File:
        key = self.storage.build_key(str(owner_id), filename)
        size = self.storage.save(key, io.BytesIO(data))
        return self.files.create(
            owner_id=owner_id, original_filename=filename,
            storage_key=key, mime_type="application/pdf", size_bytes=size,
        )

    def create_blank(self, *, owner_id: uuid.UUID, pages: int, page_size: str) -> File:
        data = creation.create_blank_pdf(pages=pages, page_size=page_size)
        return self._save(owner_id, "blank.pdf", data)

    def create_from_text(self, *, owner_id: uuid.UUID, text: str, page_size: str, font_size: int) -> File:
        data = creation.text_to_pdf(text, page_size=page_size, font_size=font_size)
        return self._save(owner_id, "document.pdf", data)

    def create_invoice(self, *, owner_id: uuid.UUID, invoice_data: dict) -> File:
        data = creation.generate_invoice(invoice_data)
        number = invoice_data.get("invoice_number", "invoice")
        return self._save(owner_id, f"invoice_{number}.pdf", data)

    def create_certificate(self, *, owner_id: uuid.UUID, certificate_data: dict) -> File:
        data = creation.generate_certificate(certificate_data)
        return self._save(owner_id, "certificate.pdf", data)

    def create_report(self, *, owner_id: uuid.UUID, report_data: dict) -> File:
        data = creation.generate_report(report_data)
        return self._save(owner_id, "report.pdf", data)
