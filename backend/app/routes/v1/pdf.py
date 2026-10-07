import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.pdf import (
    BookmarkItem,
    BookmarksSetRequest,
    CompressRequest,
    ConvertFromPDFRequest,
    ConvertToPDFRequest,
    CropRequest,
    DecryptRequest,
    DeletePagesRequest,
    DuplicatePageRequest,
    EncryptRequest,
    ExtractRequest,
    FileOut,
    HeaderFooterRequest,
    InsertBlankPageRequest,
    JobOut,
    MergeRequest,
    MetadataRemoveRequest,
    MetadataSetRequest,
    OCRRequest,
    PageNumbersRequest,
    PermissionsRequest,
    RedactRequest,
    RemoveWatermarkRequest,
    ReorderPagesRequest,
    ReplacePagesRequest,
    RotateRequest,
    SignRequest,
    SplitRequest,
    VerifySignatureResponse,
    WatermarkRequest,
)
from app.services.pdf_service import PDFService

router = APIRouter(prefix="/pdf", tags=["PDF Operations"])


@router.post("/merge", response_model=JobOut, status_code=202)
def merge(data: MergeRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = PDFService(db).merge(owner_id=user.id, file_ids=data.file_ids)
    return job


@router.post("/split", response_model=JobOut, status_code=202)
def split(data: SplitRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = PDFService(db).split(owner_id=user.id, file_id=data.file_id, page_ranges=data.page_ranges)
    return job


@router.post("/compress", response_model=JobOut, status_code=202)
def compress(data: CompressRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = PDFService(db).compress(
        owner_id=user.id, file_id=data.file_id, quality=data.quality,
        custom_dpi_target=data.custom_dpi_target, custom_quality=data.custom_quality,
    )
    return job


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).get_owned_job(job_id=job_id, owner_id=user.id)


@router.post("/convert-to-pdf", response_model=JobOut, status_code=202)
def convert_to_pdf(data: ConvertToPDFRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).convert_to_pdf(owner_id=user.id, file_id=data.file_id)


@router.post("/convert-from-pdf", response_model=JobOut, status_code=202)
def convert_from_pdf(data: ConvertFromPDFRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).convert_from_pdf(owner_id=user.id, file_id=data.file_id, target_format=data.target_format)


@router.post("/ocr", response_model=JobOut, status_code=202)
def ocr(data: OCRRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).ocr(owner_id=user.id, file_id=data.file_id, languages=data.languages, force=data.force)


@router.post("/encrypt", response_model=JobOut, status_code=202)
def encrypt(data: EncryptRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).encrypt(
        owner_id=user.id, file_id=data.file_id, user_password=data.user_password,
        owner_password=data.owner_password, allow_printing=data.allow_printing, allow_copying=data.allow_copying,
    )


@router.post("/decrypt", response_model=JobOut, status_code=202)
def decrypt(data: DecryptRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).decrypt(owner_id=user.id, file_id=data.file_id, password=data.password)


@router.post("/watermark", response_model=JobOut, status_code=202)
def watermark(data: WatermarkRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).watermark(owner_id=user.id, file_id=data.file_id, text=data.text, opacity=data.opacity)


@router.post("/redact", response_model=JobOut, status_code=202)
def redact(data: RedactRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).redact(
        owner_id=user.id, file_id=data.file_id,
        redactions=[r.model_dump() for r in data.redactions],
    )


@router.post("/metadata/set", response_model=JobOut, status_code=202)
def set_metadata(data: MetadataSetRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).set_metadata(owner_id=user.id, file_id=data.file_id, metadata=data.metadata)


@router.post("/metadata/remove", response_model=JobOut, status_code=202)
def remove_metadata(data: MetadataRemoveRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).remove_metadata(owner_id=user.id, file_id=data.file_id)


@router.get("/metadata/{file_id}")
def get_metadata(file_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).get_metadata(owner_id=user.id, file_id=file_id)


@router.post("/pages/delete", response_model=JobOut, status_code=202)
def delete_pages(data: DeletePagesRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).delete_pages(owner_id=user.id, file_id=data.file_id, page_numbers=data.page_numbers)


@router.post("/pages/insert-blank", response_model=JobOut, status_code=202)
def insert_blank_page(data: InsertBlankPageRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).insert_blank_page(owner_id=user.id, file_id=data.file_id, position=data.position)


@router.post("/pages/duplicate", response_model=JobOut, status_code=202)
def duplicate_page(data: DuplicatePageRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).duplicate_page(owner_id=user.id, file_id=data.file_id, page_number=data.page_number)


@router.post("/pages/reorder", response_model=JobOut, status_code=202)
def reorder_pages(data: ReorderPagesRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).reorder_pages(owner_id=user.id, file_id=data.file_id, new_order=data.new_order)


@router.post("/pages/numbers", response_model=JobOut, status_code=202)
def add_page_numbers(data: PageNumbersRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).add_page_numbers(
        owner_id=user.id, file_id=data.file_id, position=data.position, start_at=data.start_at, fmt=data.format,
    )


@router.post("/pages/header-footer", response_model=JobOut, status_code=202)
def add_header_footer(data: HeaderFooterRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).add_header_footer(
        owner_id=user.id, file_id=data.file_id, header_text=data.header_text, footer_text=data.footer_text,
    )


@router.post("/sign", response_model=JobOut, status_code=202)
def sign(data: SignRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).sign(
        owner_id=user.id, file_id=data.file_id, signer_name=data.signer_name,
        page=data.page, x=data.x, y=data.y, reason=data.reason,
    )


@router.get("/sign/{file_id}/verify", response_model=VerifySignatureResponse)
def verify_signature(file_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).verify_signature(owner_id=user.id, file_id=file_id)


@router.post("/permissions", response_model=JobOut, status_code=202)
def set_permissions(data: PermissionsRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).set_permissions(
        owner_id=user.id, file_id=data.file_id, allow_printing=data.allow_printing,
        allow_copying=data.allow_copying, allow_editing=data.allow_editing, allow_annotations=data.allow_annotations,
    )


@router.post("/rotate", response_model=JobOut, status_code=202)
def rotate(data: RotateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).rotate(owner_id=user.id, file_id=data.file_id, page_numbers=data.page_numbers, degrees=data.degrees)


@router.post("/extract", response_model=JobOut, status_code=202)
def extract(data: ExtractRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).extract(owner_id=user.id, file_id=data.file_id, page_numbers=data.page_numbers)


@router.post("/crop", response_model=JobOut, status_code=202)
def crop(data: CropRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).crop(
        owner_id=user.id, file_id=data.file_id, margins=data.margins.model_dump(), page_numbers=data.page_numbers,
    )


@router.post("/replace-pages", response_model=JobOut, status_code=202)
def replace_pages(data: ReplacePagesRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).replace_pages(
        owner_id=user.id, file_id=data.file_id,
        replacement_file_id=data.replacement_file_id, page_numbers=data.page_numbers,
    )


@router.post("/watermark/remove", response_model=JobOut, status_code=202)
def remove_watermark(data: RemoveWatermarkRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).remove_watermark(owner_id=user.id, file_id=data.file_id, text=data.text)


@router.get("/bookmarks/{file_id}", response_model=list[BookmarkItem])
def get_bookmarks(file_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).get_bookmarks(owner_id=user.id, file_id=file_id)


@router.post("/bookmarks", response_model=FileOut)
def set_bookmarks(data: BookmarksSetRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return PDFService(db).set_bookmarks(
        owner_id=user.id, file_id=data.file_id, bookmarks=[b.model_dump() for b in data.bookmarks],
    )
