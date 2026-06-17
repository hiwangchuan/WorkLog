from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import ok
from app.models import SystemSetting, User
from app.schemas import SettingUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
def get_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(SystemSetting).filter(SystemSetting.user_id == current_user.id, SystemSetting.key == "ai_desensitization_default").first()
    return ok(
        {
            "app_name": settings.app_name,
            "ai_desensitization_default": (row.value == "true") if row else settings.ai_desensitization_default,
            "upload_driver": settings.upload_driver,
            "max_upload_size_mb": settings.max_upload_size_mb,
        }
    )


@router.put("")
def update_settings(payload: SettingUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(SystemSetting).filter(SystemSetting.user_id == current_user.id, SystemSetting.key == "ai_desensitization_default").first()
    if not row:
        row = SystemSetting(user_id=current_user.id, key="ai_desensitization_default", value=str(payload.ai_desensitization_default).lower())
    else:
        row.value = str(payload.ai_desensitization_default).lower()
    db.add(row)
    db.commit()
    return ok({"saved": True})
