import hashlib
import hmac
import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import PasswordReset, User, now
from app.schemas import ForgotPasswordIn, LoginIn, ResetPasswordIn, TokenOut, UserCreate, UserOut, UserUpdate
from app.security import ADMIN_ONLY, create_token, get_current_user, hash_password, verify_password
from app.services.mailer import MailError, mail_configured, send_mail

router = APIRouter(prefix="/api", tags=["auth"])

RESET_MAX_ATTEMPTS = 5     # nhập sai quá số lần này thì mã bị hủy
RESET_RESEND_SECONDS = 60  # khoảng cách tối thiểu giữa hai lần gửi mã
RESET_MAX_PER_HOUR = 5     # chống spam hộp thư quản trị


def _code_hash(user_id: int, code: str) -> str:
    return hmac.new(settings.SECRET_KEY.encode(), f"{user_id}:{code}".encode(), hashlib.sha256).hexdigest()


def _mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    return f"{local[:1]}***@{domain}" if domain else "***"


@router.post("/auth/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == data.username.strip()))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Sai tên đăng nhập hoặc mật khẩu")
    if not user.is_active:
        raise HTTPException(403, "Tài khoản đã bị khóa")
    return TokenOut(access_token=create_token(user), user=UserOut.model_validate(user))


@router.post("/auth/forgot-password")
def forgot_password(data: ForgotPasswordIn, db: Session = Depends(get_db)):
    """Quản trị viên quên mật khẩu: gửi mã 6 số tới ADMIN_EMAIL. Tài khoản khác nhờ quản trị viên đặt lại.

    Luôn trả cùng một thông báo (kể cả khi tên đăng nhập không có, không phải quản trị viên, hoặc vừa gửi mã)
    để người ngoài không dò ra được tài khoản quản trị.
    """
    if not (settings.ADMIN_EMAIL and mail_configured()):
        raise HTTPException(503, "Hệ thống chưa cấu hình gửi email đặt lại mật khẩu (ADMIN_EMAIL, RESEND_API_KEY hoặc SMTP)")
    result = {"ok": True, "message": f"Nếu đây là tài khoản quản trị viên, mã xác nhận đã được gửi tới "
                                     f"{_mask_email(settings.ADMIN_EMAIL)}. Mã có hiệu lực {settings.RESET_CODE_MINUTES} phút."}
    user = db.scalar(select(User).where(User.username == data.username.strip()))
    if user is None or user.role != "admin" or not user.is_active:
        return result
    t = now()
    recent = db.scalars(select(PasswordReset).where(PasswordReset.user_id == user.id,
                                                    PasswordReset.created_at > t - timedelta(hours=1))
                        .order_by(PasswordReset.id.desc())).all()
    if recent and ((t - recent[0].created_at).total_seconds() < RESET_RESEND_SECONDS or len(recent) >= RESET_MAX_PER_HOUR):
        return result  # vừa gửi / gửi quá nhiều: mã trước vẫn dùng được
    for old in db.scalars(select(PasswordReset).where(PasswordReset.user_id == user.id, PasswordReset.used.is_(False))):
        old.used = True  # mã mới thay thế mã cũ
    code = f"{secrets.randbelow(10 ** 6):06d}"
    db.add(PasswordReset(user_id=user.id, code_hash=_code_hash(user.id, code),
                         expires_at=t + timedelta(minutes=settings.RESET_CODE_MINUTES)))
    try:
        send_mail(settings.ADMIN_EMAIL, f"[{settings.SHOP_NAME}] Mã đặt lại mật khẩu: {code}",
                  f"Xin chào,\n\nCó yêu cầu đặt lại mật khẩu cho tài khoản quản trị viên \"{user.username}\" "
                  f"trên {settings.SHOP_NAME}.\n\nMã xác nhận: {code}\n\n"
                  f"Mã có hiệu lực {settings.RESET_CODE_MINUTES} phút và chỉ dùng được một lần.\n"
                  "Nếu bạn không yêu cầu, hãy bỏ qua email này, mật khẩu hiện tại vẫn giữ nguyên.")
    except MailError as e:
        db.rollback()  # không lưu mã chưa gửi được, mã cũ vẫn còn hiệu lực
        raise HTTPException(502, f"Không gửi được email: {e}")
    db.commit()
    return result


@router.post("/auth/reset-password")
def reset_password(data: ResetPasswordIn, db: Session = Depends(get_db)):
    invalid = HTTPException(400, "Mã xác nhận không đúng hoặc đã hết hạn")
    user = db.scalar(select(User).where(User.username == data.username.strip()))
    if user is None or user.role != "admin" or not user.is_active:
        raise invalid
    reset = db.scalar(select(PasswordReset).where(PasswordReset.user_id == user.id, PasswordReset.used.is_(False))
                      .order_by(PasswordReset.id.desc()))
    if reset is None or reset.expires_at < now():
        raise invalid
    if not hmac.compare_digest(reset.code_hash, _code_hash(user.id, data.code.strip())):
        reset.attempts += 1
        reset.used = reset.attempts >= RESET_MAX_ATTEMPTS
        db.commit()
        if reset.used:
            raise HTTPException(400, "Nhập sai mã quá nhiều lần, hãy yêu cầu mã mới")
        raise HTTPException(400, f"Mã xác nhận không đúng (còn {RESET_MAX_ATTEMPTS - reset.attempts} lần thử)")
    user.password_hash = hash_password(data.new_password)
    reset.used = True
    db.commit()
    return {"ok": True, "message": "Đã đổi mật khẩu, hãy đăng nhập bằng mật khẩu mới"}


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
