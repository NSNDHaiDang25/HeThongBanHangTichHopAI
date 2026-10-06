"""Tham số chỉnh trên giao diện: lưu bảng system_settings, ghi đè giá trị đọc từ .env (app/config.py).

Hai nhóm tách theo vai trò, không ai sửa được nhóm của người kia:
- tech (quản trị viên): cấu hình kỹ thuật và AI.
- business (chủ cửa hàng): thông tin cửa hàng, tài khoản nhận tiền, điểm tích lũy, thời hạn đổi trả.
API key Gemini, mật khẩu email, SECRET_KEY không chỉnh trên giao diện: chỉ đặt trong .env.
"""
import json
import re
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import SystemSetting, User, now
from app.services.audit import audit


@dataclass(frozen=True)
class Param:
    key: str
    label: str
    kind: str  # str | int | float | bool | list | choice
    help: str = ""
    choices: tuple[str, ...] = ()
    lo: float | None = None
    hi: float | None = None
    max_len: int = 150
    pattern: str | None = None  # biểu thức chính quy cho kiểu str


TECH = [
    Param("AI_ENABLED", "Bật trợ lý AI (Gemini)", "bool", "Tắt: mọi chức năng AI chạy chế độ dự phòng theo từ khóa"),
    Param("GEMINI_MODEL", "Model chính", "str", "VD: gemini-3.6-flash", max_len=60, pattern=r"[A-Za-z0-9._-]+"),
    Param("GEMINI_FALLBACK_MODELS", "Model dự phòng", "list",
          "Dùng lần lượt khi model chính hết lượt / quá tải, cách nhau dấu phẩy"),
    Param("AI_THINKING_LEVEL", "Mức suy nghĩ của AI", "choice", "minimal nhanh nhất, high kỹ nhất nhưng chậm",
          choices=("", "minimal", "low", "medium", "high")),
    Param("AI_TIMEOUT_SECONDS", "Thời gian chờ AI tối đa (giây)", "float", lo=5, hi=120),
    Param("AI_MAX_RETRIES", "Số lần thử lại khi AI lỗi", "int", lo=0, hi=5),
    Param("ADVISOR_PROMPT_VERSION", "Phiên bản prompt chatbot tư vấn", "choice", choices=("v1", "v2", "v3")),
    Param("ACCESS_TOKEN_EXPIRE_MINUTES", "Phiên đăng nhập hết hạn sau (phút)", "int", lo=15, hi=1440),
    Param("RESET_CODE_MINUTES", "Mã đặt lại mật khẩu có hiệu lực (phút)", "int", lo=5, hi=60),
]

BUSINESS = [
    Param("SHOP_NAME", "Tên cửa hàng", "str", "In trên hóa đơn", max_len=100),
    Param("SHOP_ADDRESS", "Địa chỉ cửa hàng", "str", "In trên hóa đơn", max_len=200),
    Param("SHOP_PHONE", "Số điện thoại cửa hàng", "str", "In trên hóa đơn", max_len=20, pattern=r"[0-9 .+-]*"),
    Param("POINTS_EARN_AMOUNT", "Số tiền thanh toán để được 1 điểm (₫)", "int", "0 = tắt tích điểm", lo=0, hi=100_000_000),
    Param("POINT_VALUE", "Giá trị 1 điểm khi dùng điểm (₫)", "int", "0 = không cho dùng điểm", lo=0, hi=1_000_000),
    Param("POINTS_MAX_PERCENT", "Dùng điểm tối đa (% giá trị đơn)", "int", lo=0, hi=100),
    Param("RETURN_HOURS", "Thời hạn đổi trả (giờ kể từ lúc mua)", "int", "0 = không nhận đổi trả", lo=0, hi=720),
    Param("VIETQR_BANK_BIN", "Mã BIN ngân hàng nhận tiền", "str", "VD: Vietcombank 970436, MB 970422",
          max_len=6, pattern=r"\d{6}"),
    Param("VIETQR_BANK_NAME", "Tên ngân hàng", "str", max_len=50),
    Param("VIETQR_ACCOUNT_NO", "Số tài khoản nhận tiền", "str", max_len=30, pattern=r"\d{4,30}"),
    Param("VIETQR_ACCOUNT_NAME", "Chủ tài khoản", "str", "Viết hoa không dấu", max_len=60),
]

GROUPS = {"tech": TECH, "business": BUSINESS}
PARAMS = {p.key: p for p in TECH + BUSINESS}
AI_KEYS = {"AI_ENABLED", "GEMINI_MODEL", "GEMINI_FALLBACK_MODELS", "AI_THINKING_LEVEL", "AI_TIMEOUT_SECONDS",
           "AI_MAX_RETRIES"}
_ENV_DEFAULTS = {k: getattr(settings, k) for k in PARAMS}  # giá trị từ .env, để hiện "mặc định"


def parse(p: Param, raw):
    """Chuẩn hóa và kiểm tra giá trị người dùng nhập. Sai thì ValueError kèm câu báo lỗi tiếng Việt."""
    if p.kind == "bool":
        if isinstance(raw, str):
            return raw.strip().lower() in ("1", "true", "yes", "on")
        return bool(raw)
    if p.kind in ("int", "float"):
        try:
            v = int(raw) if p.kind == "int" else float(raw)
        except (TypeError, ValueError):
            raise ValueError(f"{p.label}: phải là số")
        if (p.lo is not None and v < p.lo) or (p.hi is not None and v > p.hi):
            raise ValueError(f"{p.label}: phải từ {p.lo:g} đến {p.hi:g}")
        return v
    if p.kind == "list":
        items = raw if isinstance(raw, list) else str(raw or "").split(",")
        items = [str(x).strip() for x in items if str(x).strip()]
        if any(not re.fullmatch(r"[A-Za-z0-9._-]{1,60}", x) for x in items):
            raise ValueError(f"{p.label}: tên model chỉ gồm chữ, số và . _ -")
        return items
    v = " ".join(str(raw if raw is not None else "").split())
    if p.kind == "choice":
        if v not in p.choices:
            raise ValueError(f"{p.label}: chỉ nhận {', '.join(c or '(mặc định của model)' for c in p.choices)}")
        return v
    if len(v) > p.max_len:
        raise ValueError(f"{p.label}: tối đa {p.max_len} ký tự")
    if p.pattern and v and not re.fullmatch(p.pattern, v):
        raise ValueError(f"{p.label}: không hợp lệ")
    if not v and p.key in ("SHOP_NAME", "GEMINI_MODEL", "VIETQR_BANK_BIN", "VIETQR_ACCOUNT_NO", "VIETQR_ACCOUNT_NAME"):
        raise ValueError(f"{p.label}: không được để trống")
    return v


def load(db: Session) -> None:
    """Nạp các giá trị đã lưu vào settings (lúc khởi động và sau khi khôi phục dữ liệu). Giá trị hỏng thì bỏ qua."""
    for row in db.scalars(select(SystemSetting)):
        p = PARAMS.get(row.key)
        if p is None:
            continue
        try:
            setattr(settings, p.key, parse(p, json.loads(row.value)))
        except (ValueError, TypeError):
            continue


def reload(db: Session) -> None:
    """Sau khi khôi phục dữ liệu: về giá trị .env rồi nạp tham số lưu trong bản sao lưu."""
    for k, v in _ENV_DEFAULTS.items():
        setattr(settings, k, v)
    load(db)
    from app.ai.client import reset_ai_client
    reset_ai_client()


def snapshot(group: str) -> list[dict]:
    return [{"key": p.key, "label": p.label, "kind": p.kind, "help": p.help, "choices": list(p.choices),
             "min": p.lo, "max": p.hi, "value": getattr(settings, p.key), "default": _ENV_DEFAULTS[p.key]}
            for p in GROUPS[group]]


def update(db: Session, user: User, group: str, values: dict) -> list[str]:
    """Lưu các tham số thuộc nhóm `group`. Trả về danh sách khóa đã đổi. Không commit."""
    allowed = {p.key: p for p in GROUPS[group]}
    unknown = [k for k in values if k not in allowed]
    if unknown:
        raise ValueError(f"Không được sửa tham số: {', '.join(unknown)}")
    parsed = {k: parse(allowed[k], v) for k, v in values.items()}  # kiểm tra hết rồi mới lưu
    changed = [k for k, v in parsed.items() if getattr(settings, k) != v]
    for k in changed:
        row = db.get(SystemSetting, k)
        if row is None:
            row = SystemSetting(key=k, value="")
            db.add(row)
        row.value = json.dumps(parsed[k], ensure_ascii=False)
        row.updated_at, row.updated_by = now(), user.id
        setattr(settings, k, parsed[k])
    if changed:
        audit(db, user, "settings_update" if group == "tech" else "business_update",
              ", ".join(f"{allowed[k].label}" for k in changed))
    if AI_KEYS & set(changed):
        from app.ai.client import reset_ai_client
        reset_ai_client()  # tạo lại client AI để dùng model / thời gian chờ mới
    return changed
