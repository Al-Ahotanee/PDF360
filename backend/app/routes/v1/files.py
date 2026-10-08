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
    import logging
    logger = logging.getLogger("pdf360.api")
    service = FileService(db)
    try:
        file = service.upload(
            owner_id=user.id,
            filename=upload.filename or "uploaded_file.pdf",
            mime_type=upload.content_type or "application/pdf",
            file_obj=upload.file,
        )
        return file
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error uploading file '{upload.filename}': {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process upload: {str(exc)}")



@router.get("", response_model=list[FileOut])
def list_files(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return FileService(db).list_for_owner(user.id)
    except Exception as e:
        import logging
        logging.getLogger("pdf360.api").error(f"Error listing files for user {user.id}: {e}", exc_info=True)
        return []


@router.get("/{file_id}/download")
def download_file(file_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = FileService(db)
    file = service.get_accessible_file(file_id=file_id, user_id=user.id)
    try:
        content = service.read_bytes(file)
    except Exception as e:
        import logging
        logging.getLogger("pdf360.api").error(f"Failed to read file {file_id} ({file.storage_key}): {e}", exc_info=True)
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="File content could not be retrieved from storage.")

    return StreamingResponse(
        io.BytesIO(content),
        media_type=file.mime_type or "application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{file.original_filename}"',
            "Content-Length": str(len(content)),
        },
    )


@router.get("/{file_id}/page-count")
def get_page_count_endpoint(file_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = FileService(db)
    file = service.get_accessible_file(file_id=file_id, user_id=user.id)
    from app.services.pdf_engine.core import get_page_count, PDFEngineError

    try:
        content = service.read_bytes(file)
    except Exception as e:
        import logging
        logging.getLogger("pdf360.api").warning(f"File {file_id} ({file.storage_key}) content not found: {e}")
        raise HTTPException(status_code=404, detail="File content could not be retrieved from storage.")

    try:
        return {"page_count": get_page_count(content)}
    except PDFEngineError as pe:
        raise HTTPException(status_code=400, detail=str(pe))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Failed to calculate page count. Document may be corrupt.")


@router.get("/{file_id}/preview/{page_number}")
def preview_page(file_id: uuid.UUID, page_number: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Renders one page as a PNG — used by the redaction picker UI so the
    person can click-drag a box on an actual rendered page rather than
    guessing PDF point coordinates blind.
    """
    service = FileService(db)
    file = service.get_accessible_file(file_id=file_id, user_id=user.id)
    from app.services.pdf_engine.conversion import pdf_to_images
    from app.services.pdf_engine.core import PDFEngineError

    try:
        content = service.read_bytes(file)
    except Exception as e:
        import logging
        logging.getLogger("pdf360.api").warning(f"File {file_id} preview content not found: {e}")
        raise HTTPException(status_code=404, detail="File content could not be retrieved from storage.")

    try:
        images = pdf_to_images(content, fmt="png", dpi=100)
    except Exception as pe:
        raise HTTPException(status_code=400, detail=f"Failed to render PDF preview: {pe}")

    if page_number < 1 or page_number > len(images):
        raise HTTPException(status_code=404, detail=f"Page {page_number} out of range (document has {len(images)} pages).")

    return StreamingResponse(
        io.BytesIO(images[page_number - 1]),
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400, stale-while-revalidate=604800"},
    )
