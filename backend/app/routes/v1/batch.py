from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.batch import (
    BatchCompressRequest,
    BatchConvertRequest,
    BatchEncryptRequest,
    BatchJobOut,
    BatchMergeRequest,
    BatchOCRRequest,
    BatchSplitRequest,
    BatchWatermarkRequest,
)
from app.services.batch_service import BatchService

router = APIRouter(prefix="/batch", tags=["Batch Processing"])


@router.post("/merge", response_model=BatchJobOut, status_code=202)
def batch_merge(data: BatchMergeRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return BatchJobOut(job_ids=BatchService(db).batch_merge(owner_id=user.id, groups=data.groups))


@router.post("/split", response_model=BatchJobOut, status_code=202)
def batch_split(data: BatchSplitRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return BatchJobOut(job_ids=BatchService(db).batch_split(owner_id=user.id, file_ids=data.file_ids, page_ranges=data.page_ranges))


@router.post("/compress", response_model=BatchJobOut, status_code=202)
def batch_compress(data: BatchCompressRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return BatchJobOut(job_ids=BatchService(db).batch_compress(owner_id=user.id, file_ids=data.file_ids, quality=data.quality))


@router.post("/convert", response_model=BatchJobOut, status_code=202)
def batch_convert(data: BatchConvertRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return BatchJobOut(job_ids=BatchService(db).batch_convert(owner_id=user.id, file_ids=data.file_ids, target_format=data.target_format))


@router.post("/ocr", response_model=BatchJobOut, status_code=202)
def batch_ocr(data: BatchOCRRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return BatchJobOut(job_ids=BatchService(db).batch_ocr(owner_id=user.id, file_ids=data.file_ids, languages=data.languages))


@router.post("/watermark", response_model=BatchJobOut, status_code=202)
def batch_watermark(data: BatchWatermarkRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return BatchJobOut(job_ids=BatchService(db).batch_watermark(owner_id=user.id, file_ids=data.file_ids, text=data.text, opacity=data.opacity))


@router.post("/encrypt", response_model=BatchJobOut, status_code=202)
def batch_encrypt(data: BatchEncryptRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return BatchJobOut(job_ids=BatchService(db).batch_encrypt(owner_id=user.id, file_ids=data.file_ids, user_password=data.user_password))
