import hashlib
import hmac
import logging
import secrets
from datetime import timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import EmailLog, PasswordReset, User, now
from app.schemas import (AdminResetPasswordIn, ChangePasswordIn, ForgotPasswordIn, LoginIn, RegisterIn,
                         ResetPasswordIn, TokenOut, UserCreate, UserOut, UserUpdate)
from app.security import (ADMIN_ONLY, create_token, get_current_user, hash_password, needs_rehash, revoke_token,
                          verify_password)
from app.services import app_settings, audit
from app.services.mailer import MailError, mail_configured, send_mail

router = APIRouter(prefix="/api", tags=["auth"])

RESET_MAX_ATTEMPTS = 5     # nhập sai quá số lần này thì mã bị hủy
RESET_RESEND_SECONDS = 60  # khoảng cách tối thiểu giữa hai lần gửi mã
RESET_MAX_PER_HOUR = 5     # chống spam hộp thư quản trị
REGISTER_MAX_PENDING = 20  # chống spam đăng ký: quá số tài khoản chờ duyệt thì tạm ngừng nhận đăng ký mới

log = logging.getLogger(__name__)


def _code_hash(user_id: int, code: str) -> str:
    return hmac.new(settings.SECRET_KEY.encode(), f"{user_id}:{code}".encode(), hashlib.sha256).hexdigest()


def _mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    return f"{local[:1]}***@{domain}" if domain else "***"


@router.post("/auth/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    """FR-AUT-01..04: sai tên hoặc sai mật khẩu đều trả cùng một thông báo; sai liên tiếp quá số lần thì khóa tạm."""
    invalid = HTTPException(401, "Sai tên đăng nhập hoặc mật khẩu")
    user = db.scalar(select(User).where(User.username == data.username.strip()))
    if user is None:
        audit.log(db, None, "LOGIN_FAILED", "users", None, new={"username": data.username.strip()[:50]})
        db.commit()
        raise invalid
    t = now()
    if user.locked_until and user.locked_until > t:
        minutes = max(1, int((user.locked_until - t).total_seconds() // 60) + 1)
        raise HTTPException(423, f"Tài khoản tạm khóa do đăng nhập sai nhiều lần. Thử lại sau {minutes} phút")
    if not verify_password(data.password, user.password_hash):
        cfg = app_settings.get_many(db, ["login_max_fail", "login_lock_minutes"])
        user.failed_login_count = (user.failed_login_count or 0) + 1
        audit.log(db, user, "LOGIN_FAILED", "users", user.id, new={"failed_login_count": user.failed_login_count})
        if user.failed_login_count >= cfg["login_max_fail"]:
            user.locked_until = t + timedelta(minutes=cfg["login_lock_minutes"])
            user.failed_login_count = 0
            audit.log(db, user, "ACCOUNT_LOCKED", "users", user.id, new={"locked_until": user.locked_until})
            db.commit()
            raise HTTPException(423, f"Sai mật khẩu {cfg['login_max_fail']} lần liên tiếp, tài khoản bị khóa "
                                     f"{cfg['login_lock_minutes']} phút")
        db.commit()
        raise invalid
    if user.pending:
        raise HTTPException(403, "Tài khoản đang chờ quản trị viên duyệt. Vui lòng thử lại sau khi được duyệt!")
    if not user.is_active:
        raise HTTPException(403, "Tài khoản đã bị khóa")
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(data.password)
    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = t
    db.commit()
    token = create_token(user, app_settings.get(db, "jwt_expire_hours"))
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/auth/change-password")
def change_password(data: ChangePasswordIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """FR-AUT-07: đổi mật khẩu khi biết mật khẩu cũ. Cũng dùng cho lần đăng nhập đầu (FR-USR-02)."""
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(400, "Mật khẩu hiện tại không đúng")
    if data.old_password == data.new_password:
        raise HTTPException(400, "Mật khẩu mới phải khác mật khẩu hiện tại")
    user.password_hash = hash_password(data.new_password)
    user.must_change_password = False
    audit.log(db, user, "PASSWORD_CHANGE", "users", user.id)
    db.commit()
    return {"ok": True, "message": "Đã đổi mật khẩu"}


@router.post("/auth/forgot-password")
def forgot_password(data: ForgotPasswordIn, db: Session = Depends(get_db)):
    """FR-AUT-06: gửi mã 6 số tới email của tài khoản; quản trị viên chưa khai báo email thì gửi tới ADMIN_EMAIL.
    Tài khoản không có email nhờ quản trị viên đặt lại.

    Luôn trả cùng một thông báo (kể cả khi tên đăng nhập không có, không có email, hoặc vừa gửi mã)
    để người ngoài không dò ra được tài khoản.
    """
    if not (settings.ADMIN_EMAIL and mail_configured()):
        raise HTTPException(503, "Hệ thống chưa cấu hình gửi email đặt lại mật khẩu (ADMIN_EMAIL, RESEND_API_KEY hoặc SMTP)")
    result = {"ok": True, "message": f"Nếu đây là tài khoản quản trị viên, mã xác nhận đã được gửi tới "
                                     f"{_mask_email(settings.ADMIN_EMAIL)}. Mã có hiệu lực {settings.RESET_CODE_MINUTES} phút."}
    user = db.scalar(select(User).where(User.username == data.username.strip()))
    target = (user.email or (settings.ADMIN_EMAIL if user.role == "admin" else None)) if user else None
    if user is None or not target or not user.is_active:
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
        send_mail(target, f"[{settings.SHOP_NAME}] Mã đặt lại mật khẩu: {code}",
                  f"Xin chào,\n\nCó yêu cầu đặt lại mật khẩu cho tài khoản \"{user.username}\" "
                  f"trên {settings.SHOP_NAME}.\n\nMã xác nhận: {code}\n\n"
                  f"Mã có hiệu lực {settings.RESET_CODE_MINUTES} phút và chỉ dùng được một lần.\n"
                  "Nếu bạn không yêu cầu, hãy bỏ qua email này, mật khẩu hiện tại vẫn giữ nguyên.")
    except MailError as e:
        db.rollback()  # không lưu mã chưa gửi được, mã cũ vẫn còn hiệu lực
        db.add(EmailLog(to_email=target, subject="Mã đặt lại mật khẩu", mail_type="reset_password", status="failed",
                        error_message=str(e)))
        db.commit()
        raise HTTPException(502, f"Không gửi được email: {e}")
    db.add(EmailLog(to_email=target, subject="Mã đặt lại mật khẩu", mail_type="reset_password", status="sent"))
    db.commit()
    return result


@router.post("/auth/reset-password")
def reset_password(data: ResetPasswordIn, db: Session = Depends(get_db)):
    invalid = HTTPException(400, "Mã xác nhận không đúng hoặc đã hết hạn")
    user = db.scalar(select(User).where(User.username == data.username.strip()))
    if user is None or not user.is_active:
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
    user.must_change_password = False
    user.locked_until = None
    user.failed_login_count = 0
    reset.used = True
    db.commit()
    return {"ok": True, "message": "Đã đổi mật khẩu, hãy đăng nhập bằng mật khẩu mới"}


def _notify_new_account(username: str, full_name: str) -> None:
    """Báo quản trị viên qua email có tài khoản mới chờ duyệt (nếu đã cấu hình gửi mail). Lỗi gửi mail không chặn đăng ký."""
    if not (settings.ADMIN_EMAIL and mail_configured()):
        return
    try:
        send_mail(settings.ADMIN_EMAIL, f"[{settings.SHOP_NAME}] Tài khoản mới chờ duyệt: {username}",
                  f"{full_name} vừa tạo tài khoản \"{username}\" trên {settings.SHOP_NAME}.\n\n"
                  "Đăng nhập bằng tài khoản quản trị viên, vào menu Người dùng để duyệt hoặc từ chối.")
    except MailError as e:
        log.warning("Không gửi được email báo tài khoản mới: %s", e)


@router.post("/auth/register", status_code=201)
def register(data: RegisterIn, background: BackgroundTasks, db: Session = Depends(get_db)):
    """Tự tạo tài khoản ở màn hình đăng nhập.

    Tài khoản mới là nhân viên bán hàng và bị khóa cho tới khi quản trị viên duyệt: quản trị viên vẫn là người cấp quyền
    (UC002), người lạ tự đăng ký trên bản chạy công khai không xem được dữ liệu cửa hàng.
    """
    if db.scalar(select(User).where(func.lower(User.username) == data.username.lower())):
        raise HTTPException(400, "Tên đăng nhập đã được sử dụng")
    if db.scalar(select(func.count(User.id)).where(User.pending.is_(True))) >= REGISTER_MAX_PENDING:
        raise HTTPException(429, "Đang có quá nhiều tài khoản chờ duyệt, vui lòng liên hệ quản trị viên")
    user = User(username=data.username, full_name=data.full_name, role="staff", is_active=False, pending=True,
                password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    background.add_task(_notify_new_account, user.username, user.full_name)
    return {"ok": True, "message": "Đã gửi yêu cầu tạo tài khoản. Bạn đăng nhập được sau khi quản trị viên duyệt."}


@router.post("/auth/logout")
def logout(request: Request, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """FR-AUT-05: thu hồi token đang dùng, token này bị từ chối ở mọi endpoint kể cả khi chưa hết hạn."""
    revoke_token(db, request.state.token_payload)
    db.commit()
    return {"ok": True}


@router.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(ADMIN_ONLY)):
    return db.scalars(select(User).order_by(User.id)).all()


def _user_snapshot(u: User) -> dict:
    return {"full_name": u.full_name, "role": u.role, "is_active": u.is_active, "email": u.email, "phone": u.phone}


def _active_admins(db: Session) -> int:
    return db.scalar(select(func.count(User.id)).where(User.role == "admin", User.is_active.is_(True))) or 0


def _check_unique_email(db: Session, email: str | None, user_id: int | None = None) -> None:
    if email and db.scalar(select(User.id).where(func.lower(User.email) == email.lower(), User.id != (user_id or 0))):
        raise HTTPException(400, "Email đã được dùng cho tài khoản khác")


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), admin: User = Depends(ADMIN_ONLY)):
    """FR-USR-01, 02: quản trị viên tạo tài khoản với mật khẩu tạm, người dùng phải đổi ở lần đăng nhập đầu."""
    if db.scalar(select(User).where(func.lower(User.username) == data.username.lower())):
        raise HTTPException(400, "Tên đăng nhập đã tồn tại")
    _check_unique_email(db, data.email)
    user = User(username=data.username, full_name=data.full_name, role=data.role, email=data.email, phone=data.phone,
                password_hash=hash_password(data.password), must_change_password=True)
    db.add(user)
    db.flush()
    audit.log(db, admin, "USER_CREATE", "users", user.id, new=_user_snapshot(user))
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
    # FR-USR-04: luôn còn ít nhất một quản trị viên đang hoạt động
    if user.role == "admin" and user.is_active and (data.role not in (None, "admin") or data.is_active is False) \
            and _active_admins(db) <= 1:
        raise HTTPException(400, "Không thể khóa hoặc hạ vai trò quản trị viên cuối cùng")
    before = _user_snapshot(user)
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.role is not None:
        user.role = data.role
    if data.email is not None or "email" in data.model_fields_set:
        _check_unique_email(db, data.email, user.id)
        user.email = data.email
    if data.phone is not None or "phone" in data.model_fields_set:
        user.phone = data.phone
    if data.is_active is not None:
        user.is_active = data.is_active
        if data.is_active:
            user.pending = False  # mở khóa tài khoản chờ duyệt = duyệt
    if data.unlock:
        user.locked_until = None
        user.failed_login_count = 0
    if data.password:
        user.password_hash = hash_password(data.password)
        user.must_change_password = True
    after = _user_snapshot(user)
    if before != after:
        action = "ROLE_CHANGE" if before["role"] != after["role"] else "USER_UPDATE"
        audit.log(db, admin, action, "users", user.id, old=before, new=after)
    db.commit()
    return user


@router.post("/users/{user_id}/reset-password")
def admin_reset_password(user_id: int, data: AdminResetPasswordIn, db: Session = Depends(get_db),
                         admin: User = Depends(ADMIN_ONLY)):
    """FR-USR-03: quản trị viên đặt mật khẩu tạm, người dùng phải đổi khi đăng nhập lại."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "Không tìm thấy người dùng")
    user.password_hash = hash_password(data.new_password)
    user.must_change_password = True
    user.locked_until = None
    user.failed_login_count = 0
    audit.log(db, admin, "PASSWORD_RESET", "users", user.id)
    db.commit()
    return {"ok": True, "message": f"Đã đặt mật khẩu tạm cho {user.username}"}


@router.delete("/users/{user_id}")
def reject_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(ADMIN_ONLY)):
    """Từ chối yêu cầu tạo tài khoản. Tài khoản đã được duyệt thì chỉ khóa, không xóa, để giữ lịch sử hóa đơn."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "Không tìm thấy người dùng")
    if not user.pending:
        raise HTTPException(400, "Chỉ xóa được tài khoản đang chờ duyệt. Tài khoản đã dùng hãy khóa lại")
    db.delete(user)
    db.commit()
    return {"ok": True, "message": f"Đã từ chối tài khoản {user.username}"}
