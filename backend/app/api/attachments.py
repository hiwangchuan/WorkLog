from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import AppError, ok
from app.models import Attachment, OvertimeLog, Project, Task, User, WorkLog
from app.schemas import AttachmentOut, AttachmentUpdate
from app.utils.serializers import dump, dump_list

router = APIRouter(prefix="/attachments", tags=["attachments"])

RELATED_TYPES = {"work_log", "task", "overtime", "project"}


def _safe_name(file_name: str | None) -> str:
    name = Path(file_name or "attachment").name.strip()
    return name or "attachment"


def _ensure_related_access(db: Session, related_type: str, related_id: int, user: User) -> None:
    if related_type not in RELATED_TYPES:
        raise AppError("附件关联类型不支持")
    if related_type == "work_log":
        exists = db.query(WorkLog.id).filter(WorkLog.id == related_id, WorkLog.user_id == user.id).first()
    elif related_type == "task":
        exists = (
            db.query(Task.id)
            .filter(Task.id == related_id, or_(Task.creator_id == user.id, Task.assignee_id == user.id))
            .first()
        )
    elif related_type == "overtime":
        exists = db.query(OvertimeLog.id).filter(OvertimeLog.id == related_id, OvertimeLog.user_id == user.id).first()
    else:
        exists = db.query(Project.id).filter(Project.id == related_id, Project.owner_id == user.id).first()
    if not exists:
        raise AppError("关联数据不存在或无权访问", status_code=404)


def _attachment_for_user(db: Session, attachment_id: int, user: User) -> Attachment:
    attachment = db.get(Attachment, attachment_id)
    if not attachment:
        raise AppError("附件不存在", status_code=404)
    _ensure_related_access(db, attachment.related_type, attachment.related_id, user)
    return attachment


@router.get("")
def list_attachments(
    related_type: str,
    related_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_related_access(db, related_type, related_id, current_user)
    items = (
        db.query(Attachment)
        .filter(Attachment.related_type == related_type, Attachment.related_id == related_id)
        .order_by(Attachment.created_at.desc(), Attachment.id.desc())
        .all()
    )
    return ok(dump_list(AttachmentOut, items))


@router.post("")
async def upload_attachment(
    related_type: str = Form(...),
    related_id: int = Form(...),
    summary: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_related_access(db, related_type, related_id, current_user)
    file_name = _safe_name(file.filename)
    suffix = Path(file_name).suffix
    storage_dir = Path(settings.upload_dir) / related_type / str(related_id)
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_path = storage_dir / f"{uuid4().hex}{suffix}"
    max_size = settings.max_upload_size_mb * 1024 * 1024
    size = 0
    try:
        with storage_path.open("wb") as target:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > max_size:
                    raise AppError(f"附件大小不能超过 {settings.max_upload_size_mb}MB")
                target.write(chunk)
    except Exception:
        storage_path.unlink(missing_ok=True)
        raise
    attachment = Attachment(
        related_type=related_type,
        related_id=related_id,
        file_name=file_name,
        file_url="",
        storage_path=str(storage_path),
        mime_type=file.content_type,
        file_size=size,
        summary=summary.strip() if isinstance(summary, str) and summary.strip() else None,
        uploader_id=current_user.id,
    )
    db.add(attachment)
    db.flush()
    attachment.file_url = f"/api/attachments/{attachment.id}/download"
    db.commit()
    db.refresh(attachment)
    return ok(dump(AttachmentOut, attachment))


@router.put("/{attachment_id}")
def update_attachment(
    attachment_id: int,
    payload: AttachmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attachment = _attachment_for_user(db, attachment_id, current_user)
    attachment.summary = payload.summary.strip() if isinstance(payload.summary, str) and payload.summary.strip() else None
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return ok(dump(AttachmentOut, attachment))


@router.get("/{attachment_id}/download")
def download_attachment(attachment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    attachment = _attachment_for_user(db, attachment_id, current_user)
    if not attachment.storage_path:
        raise AppError("附件文件不存在", status_code=404)
    path = Path(attachment.storage_path)
    if not path.exists() or not path.is_file():
        raise AppError("附件文件不存在", status_code=404)
    return FileResponse(path, media_type=attachment.mime_type or "application/octet-stream", filename=attachment.file_name)


@router.delete("/{attachment_id}")
def delete_attachment(attachment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    attachment = _attachment_for_user(db, attachment_id, current_user)
    storage_path = Path(attachment.storage_path) if attachment.storage_path else None
    db.delete(attachment)
    db.commit()
    if storage_path:
        storage_path.unlink(missing_ok=True)
    return ok({"deleted": True})
