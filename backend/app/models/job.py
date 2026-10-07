import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class JobType(str, enum.Enum):
    MERGE = "merge"
    SPLIT = "split"
    COMPRESS = "compress"
    CONVERT_TO_PDF = "convert_to_pdf"
    CONVERT_FROM_PDF = "convert_from_pdf"
    OCR = "ocr"
    EDIT = "edit"
    FORM_FILL = "form_fill"
    WATERMARK = "watermark"
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    REDACT = "redact"
    METADATA = "metadata"
    AI_SUMMARY = "ai_summary"
    AI_QA = "ai_qa"
    AI_TRANSLATE = "ai_translate"
    AI_EXTRACT = "ai_extract"
    DELETE_PAGES = "delete_pages"
    INSERT_BLANK_PAGE = "insert_blank_page"
    DUPLICATE_PAGE = "duplicate_page"
    REORDER_PAGES = "reorder_pages"
    PAGE_NUMBERS = "page_numbers"
    HEADER_FOOTER = "header_footer"
    SIGN = "sign"
    PDF_TO_HTML = "pdf_to_html"
    PDF_TO_EPUB = "pdf_to_epub"
    PERMISSIONS = "permissions"
    ROTATE = "rotate"
    EXTRACT = "extract"
    CROP = "crop"
    REPLACE_PAGES = "replace_pages"
    REMOVE_WATERMARK = "remove_watermark"
    BOOKMARKS = "bookmarks"


class Job(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Every PDF/OCR/AI operation — regardless of how fast it actually
    completes — is represented as a Job. The API always responds to an
    operation request with a job_id; the client polls (or listens on a
    websocket, added later) for status. This keeps one code path for
    "instant" and "slow" operations instead of two.

    `input_params` and `result` are JSONB so each JobType can store whatever
    shape it needs (e.g. compress stores {quality: "high"}, merge stores
    {source_file_ids: [...]}) without new columns per job type.
    """
    __tablename__ = "jobs"

    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    job_type: Mapped[JobType] = mapped_column(Enum(JobType, name="job_type"), nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"), default=JobStatus.QUEUED, nullable=False
    )

    input_params: Mapped[dict] = mapped_column(JSONB, default=dict)
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
