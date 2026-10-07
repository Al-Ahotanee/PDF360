import uuid
from datetime import datetime

from pydantic import BaseModel


class FileOut(BaseModel):
    id: uuid.UUID
    original_filename: str
    mime_type: str
    size_bytes: int
    is_favorite: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class JobOut(BaseModel):
    id: uuid.UUID
    job_type: str
    status: str
    result: dict | None
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MergeRequest(BaseModel):
    file_ids: list[uuid.UUID]


class SplitRequest(BaseModel):
    file_id: uuid.UUID
    page_ranges: list[tuple[int, int]]


class CompressRequest(BaseModel):
    file_id: uuid.UUID
    quality: str = "medium"  # low | medium | high | custom
    custom_dpi_target: int | None = None  # required when quality == "custom"
    custom_quality: int | None = None  # required when quality == "custom" (1-95 JPEG quality)


class ConvertToPDFRequest(BaseModel):
    file_id: uuid.UUID


class ConvertFromPDFRequest(BaseModel):
    file_id: uuid.UUID
    target_format: str  # docx | pptx | xlsx | png | jpg | txt


class OCRRequest(BaseModel):
    file_id: uuid.UUID
    languages: list[str] = ["english"]
    force: bool = False


class EncryptRequest(BaseModel):
    file_id: uuid.UUID
    user_password: str
    owner_password: str | None = None
    allow_printing: bool = True
    allow_copying: bool = True


class DecryptRequest(BaseModel):
    file_id: uuid.UUID
    password: str


class WatermarkRequest(BaseModel):
    file_id: uuid.UUID
    text: str
    opacity: float = 0.3


class RedactBox(BaseModel):
    page: int
    x0: float
    y0: float
    x1: float
    y1: float


class RedactRequest(BaseModel):
    file_id: uuid.UUID
    redactions: list[RedactBox]


class MetadataSetRequest(BaseModel):
    file_id: uuid.UUID
    metadata: dict[str, str]


class MetadataRemoveRequest(BaseModel):
    file_id: uuid.UUID


class DeletePagesRequest(BaseModel):
    file_id: uuid.UUID
    page_numbers: list[int]


class InsertBlankPageRequest(BaseModel):
    file_id: uuid.UUID
    position: int


class DuplicatePageRequest(BaseModel):
    file_id: uuid.UUID
    page_number: int


class ReorderPagesRequest(BaseModel):
    file_id: uuid.UUID
    new_order: list[int]


class PageNumbersRequest(BaseModel):
    file_id: uuid.UUID
    position: str = "bottom-center"  # bottom-center | bottom-left | bottom-right | top-center | top-left | top-right
    start_at: int = 1
    format: str = "{n}"  # "{n}" or "Page {n} of {total}"


class HeaderFooterRequest(BaseModel):
    file_id: uuid.UUID
    header_text: str | None = None
    footer_text: str | None = None


class SignRequest(BaseModel):
    file_id: uuid.UUID
    signer_name: str
    page: int = 1
    x: float = 350
    y: float = 700
    reason: str | None = None


class VerifySignatureResponse(BaseModel):
    is_signed: bool
    signer: str | None = None
    reason: str | None = None
    timestamp: str | None = None
    pre_sign_sha256: str | None = None


class PermissionsRequest(BaseModel):
    file_id: uuid.UUID
    allow_printing: bool = True
    allow_copying: bool = True
    allow_editing: bool = True
    allow_annotations: bool = True


class RotateRequest(BaseModel):
    file_id: uuid.UUID
    page_numbers: list[int]
    degrees: int  # multiple of 90


class ExtractRequest(BaseModel):
    file_id: uuid.UUID
    page_numbers: list[int]


class CropMargins(BaseModel):
    left: float = 0
    top: float = 0
    right: float = 0
    bottom: float = 0


class CropRequest(BaseModel):
    file_id: uuid.UUID
    margins: CropMargins
    page_numbers: list[int] | None = None  # None = every page


class ReplacePagesRequest(BaseModel):
    file_id: uuid.UUID
    replacement_file_id: uuid.UUID
    page_numbers: list[int]


class RemoveWatermarkRequest(BaseModel):
    file_id: uuid.UUID
    text: str


class BookmarkItem(BaseModel):
    level: int
    title: str
    page: int


class BookmarksSetRequest(BaseModel):
    file_id: uuid.UUID
    bookmarks: list[BookmarkItem]
