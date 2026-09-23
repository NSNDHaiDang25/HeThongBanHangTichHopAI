from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import LoginIn, TokenOut, UserCreate, UserOut, UserUpdate
from app.security import ADMIN_ONLY, create_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/auth/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == data.username.strip()))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Sai tên đăng nhập hoặc mật khẩu")
    if not user.is_active:
        raise HTTPException(403, "Tài khoản đã bị khóa")
    return TokenOut(access_token=create_token(user), user=UserOut.model_validate(user))


@router.post("/auth/logout")
def logout(_: User = Depends(get_current_user)):
    # JWT không lưu phía server: client xóa token là đăng xuất.
    return {"ok": True}


@router.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(ADMIN_ONLY)):
    return db.scalars(select(User).order_by(User.id)).all()


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), _: User = Depends(ADMIN_ONLY)):
    if db.scalar(select(User).where(User.username == data.username)):
        raise HTTPException(400, "Tên đăng nhập đã tồn tại")
    user = User(username=data.username, full_name=data.full_name, role=data.role,
                password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    return user


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db),
                admin: User = Depends(ADMIN_ONLY)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "Không tìm thấy người dùng")
    if user.id == admin.id and (data.role not in (None, "admin") or data.is_active is False):
        raise HTTPException(400, "Không thể tự hạ quyền hoặc khóa chính mình")
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.password:
        user.password_hash = hash_password(data.password)
    db.commit()
    return user
