from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import AppError
from app.core.security import decode_access_token
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppError("请先登录", code=40101, status_code=401)
    subject = decode_access_token(credentials.credentials)
    if subject is None:
        raise AppError("登录已失效，请重新登录", code=40102, status_code=401)
    user = db.get(User, int(subject))
    if not user or user.status != "active":
        raise AppError("用户不存在或已禁用", code=40103, status_code=401)
    return user
