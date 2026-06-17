from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import AppError, ok
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas import AuthToken, LoginRequest, PasswordChange, UserCreate, UserOut
from app.utils.serializers import dump

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    duplicate_filters = [User.username == payload.username]
    if payload.email:
        duplicate_filters.append(User.email == payload.email)
    exists = db.query(User).filter(or_(*duplicate_filters)).first()
    if exists:
        raise AppError("用户名或邮箱已存在")
    user = User(
        username=payload.username,
        email=payload.email,
        nickname=payload.nickname,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = create_access_token(user.id)
    return ok(AuthToken(access_token=access_token, user=UserOut.model_validate(user)).model_dump(mode="json"))


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(or_(User.username == payload.username, User.email == payload.username)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise AppError("用户名或密码错误", code=40002, status_code=401)
    if user.status != "active":
        raise AppError("用户已被禁用", code=40003, status_code=403)
    access_token = create_access_token(user.id)
    return ok(AuthToken(access_token=access_token, user=UserOut.model_validate(user)).model_dump(mode="json"))


@router.post("/logout")
def logout():
    return ok({"logged_out": True})


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return ok(dump(UserOut, current_user))


@router.put("/password")
def change_password(payload: PasswordChange, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.old_password, current_user.password_hash):
        raise AppError("原密码不正确")
    current_user.password_hash = hash_password(payload.new_password)
    db.add(current_user)
    db.commit()
    return ok({"changed": True})
