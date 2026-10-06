import hashlib
import hmac
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User

ALGORITHM = "HS256"
BCRYPT_ROUNDS = 12  # mỗi lần băm ~0,2 giây: đủ chậm để chống dò mật khẩu, đăng nhập vẫn nhanh
_PBKDF2_ROUNDS = 200_000  # chỉ để kiểm tra mật khẩu băm theo cách cũ (trước khi dùng bcrypt)
bearer = HTTPBearer(auto_error=False)


def _password_bytes(password: str) -> bytes:
    # bcrypt chỉ dùng 72 byte đầu (bcrypt 5 báo lỗi nếu dài hơn), cắt sẵn để lúc băm và lúc kiểm tra giống nhau
    return password.encode()[:72]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt(BCRYPT_ROUNDS)).decode()


def verify_password(password: str, stored: str) -> bool:
    if stored.startswith("pbkdf2$"):
        return _verify_pbkdf2(password, stored)
    try:
        return bcrypt.checkpw(_password_bytes(password), stored.encode())
    except ValueError:  # chuỗi băm hỏng
        return False


def needs_rehash(stored: str) -> bool:
    """Mật khẩu còn băm theo cách cũ: băm lại bằng bcrypt ở lần đăng nhập thành công kế tiếp."""
    return stored.startswith("pbkdf2$")


def _verify_pbkdf2(password: str, stored: str) -> bool:
    try:
        _, salt, digest = stored.split("$")
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _PBKDF2_ROUNDS).hex()
    return hmac.compare_digest(check, digest)


def create_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user.id), "role": user.role, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(status.HTTP_401_UNAUTHORIZED, "Chưa đăng nhập hoặc phiên đã hết hạn")
    if creds is None:
        raise unauthorized
    try:
        payload = jwt.decode(creds.credentials, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise unauthorized
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise unauthorized
    return user


def require_roles(*roles: str):
    """Dependency kiểm tra vai trò. Các vai trò độc lập, không kế thừa nhau: chỉ vai trò được liệt kê mới được vào
    (quản trị viên không tự động có quyền bán hàng / xem doanh thu, chủ cửa hàng không quản trị tài khoản)."""
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Bạn không có quyền thực hiện chức năng này")
        return user
    return checker


# Nhóm quyền dùng chung
ALL_STAFF = require_roles("owner", "staff")  # nghiệp vụ bán hàng: thu ngân và chủ cửa hàng
MANAGERS = require_roles("owner")            # chỉ chủ cửa hàng
ADMIN_ONLY = require_roles("admin")          # quản trị hệ thống
ANY_ROLE = require_roles("admin", "owner", "staff")
