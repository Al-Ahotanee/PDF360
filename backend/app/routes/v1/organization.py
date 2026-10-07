import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.organization import AddTagRequest, FavoriteRequest, FolderCreate, FolderOut, TagCreate, TagOut
from app.schemas.pdf import FileOut
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/organization", tags=["Organization"])


@router.post("/folders", response_model=FolderOut, status_code=201)
def create_folder(data: FolderCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return OrganizationService(db).create_folder(owner_id=user.id, name=data.name, parent_id=data.parent_id)


@router.get("/folders", response_model=list[FolderOut])
def list_folders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return OrganizationService(db).list_folders(user.id)


@router.post("/tags", response_model=TagOut, status_code=201)
def create_tag(data: TagCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return OrganizationService(db).create_tag(owner_id=user.id, name=data.name, color=data.color)


@router.get("/tags", response_model=list[TagOut])
def list_tags(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return OrganizationService(db).list_tags(user.id)


@router.patch("/files/{file_id}/favorite", response_model=FileOut)
def set_favorite(file_id: uuid.UUID, data: FavoriteRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return OrganizationService(db).toggle_favorite(owner_id=user.id, file_id=file_id, is_favorite=data.is_favorite)


@router.post("/files/{file_id}/trash", response_model=FileOut)
def trash_file(file_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return OrganizationService(db).move_to_trash(owner_id=user.id, file_id=file_id)


@router.post("/files/{file_id}/restore", response_model=FileOut)
def restore_file(file_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return OrganizationService(db).restore_from_trash(owner_id=user.id, file_id=file_id)


@router.post("/files/{file_id}/tags", response_model=FileOut)
def add_tag(file_id: uuid.UUID, data: AddTagRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return OrganizationService(db).add_tag_to_file(owner_id=user.id, file_id=file_id, tag_id=data.tag_id)
