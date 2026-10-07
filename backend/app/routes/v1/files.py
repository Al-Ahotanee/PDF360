import io
import uuid

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.pdf import FileOut
from app.services.file_service import FileService

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload", response_model=FileOut, status_code=201)
async def upload_file(
    upload: UploadFile,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = FileService(db)
    file = service.upload(
        owner_id=user.id,
        filename=upload.filename,
        mime_type=upload.content_type or "application/octet-stream",
        file_obj=upload.file,
    )
    return file


@router.get("", response_model=list[FileOut])
def list_files(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return FileService(db).list_for_owner(user.id)


@router.get("/{file_id}/download")
def download_file(file_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = FileService(db)
    file = service.get_owned_file(file_id=file_id, owner_id=user.id)
    stream = service.storage.open_stream(file.storage_key)
    return StreamingResponse(
        stream,
        media_type=file.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{file.original_filename}"'},
    )


@router.get("/{file_id}/page-count")
def get_page_count_endpoint(file_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = FileService(db)
    file = service.get_owned_file(file_id=file_id, owner_id=user.id)
    from app.services.pdf_engine.core import get_page_count

    return {"page_count": get_page_count(service.read_bytes(file))}


@router.get("/{file_id}/preview/{page_number}")
def preview_page(file_id: uuid.UUID, page_number: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Renders one page as a PNG — used by the redaction picker UI so the
    person can click-drag a box on an actual rendered page rather than
    guessing PDF point coordinates blind.
    """
    service = FileService(db)
    file = service.get_owned_file(file_id=file_id, owner_id=user.id)
    from app.services.pdf_engine.conversion import pdf_to_images
    from app.services.pdf_engine.core import PDFEngineError

    images = pdf_to_images(service.read_bytes(file), fmt="png", dpi=100)
    if page_number < 1 or page_number > len(images):
        raise PDFEngineError(f"Page {page_number} out of range (document has {len(images)} pages).")
    return StreamingResponse(io.BytesIO(images[page_number - 1]), media_type="image/png")
