import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me-please-use-a-long-random-string")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'sales.db'}")

    # Bỏ cả dấu ngoặc kép / đơn: dán key kèm ngoặc vào Environment trên Render là lỗi hay gặp (Google trả 401)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip().strip("\"'").strip()
    # Quản trị viên tắt AI (trên màn hình Cấu hình hệ thống): mọi chức năng AI chạy chế độ dự phòng
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "true").strip().lower() not in ("0", "false", "no", "off")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    # Model dự phòng, dùng lần lượt khi model chính hết lượt / quá tải (mỗi model có hạn mức riêng).
    # Xếp model mạnh trước để câu trả lời vẫn tốt khi phải đổi model; bản lite để cuối cùng.
    GEMINI_FALLBACK_MODELS: list[str] = [m.strip() for m in os.getenv(
        "GEMINI_FALLBACK_MODELS",
        "gemini-3.8-flash,gemini-3.7-flash,gemini-3.5-flash,gemini-3.5-flash-lite").split(",") if m.strip()]
    # Mức suy nghĩ của Gemini trước khi trả lời: minimal (nhanh nhất) | low | medium | high (chậm, kỹ nhất).
    # Để trống = theo mặc định của model (thường là high, chậm hơn nhiều).
    AI_THINKING_LEVEL: str = os.getenv("AI_THINKING_LEVEL", "minimal").strip().lower()
    AI_TIMEOUT_SECONDS: float = float(os.getenv("AI_TIMEOUT_SECONDS", "30"))
    AI_MAX_RETRIES: int = int(os.getenv("AI_MAX_RETRIES", "2"))
    ADVISOR_PROMPT_VERSION: str = os.getenv("ADVISOR_PROMPT_VERSION", "v3")

    # ---- Tham số kinh doanh (chủ cửa hàng chỉnh trên màn hình Tham số kinh doanh, ghi đè giá trị ở đây)
    SHOP_NAME: str = os.getenv("SHOP_NAME", "Cửa hàng SalesAI")
    SHOP_ADDRESS: str = os.getenv("SHOP_ADDRESS", "")
    SHOP_PHONE: str = os.getenv("SHOP_PHONE", "")
    POINTS_EARN_AMOUNT: int = int(os.getenv("POINTS_EARN_AMOUNT", "100000"))  # mỗi 100.000 ₫ thanh toán = 1 điểm
    POINT_VALUE: int = int(os.getenv("POINT_VALUE", "1000"))                  # 1 điểm = 1.000 ₫ khi dùng điểm
    POINTS_MAX_PERCENT: int = int(os.getenv("POINTS_MAX_PERCENT", "50"))       # dùng điểm tối đa 50% giá trị đơn
    RETURN_HOURS: int = int(os.getenv("RETURN_HOURS", "24"))                   # nhận đổi trả trong 24 giờ sau khi mua
    # Tài khoản nhận chuyển khoản (VietQR). BIN ngân hàng: https://api.vietqr.io/v2/banks
    VIETQR_BANK_BIN: str = os.getenv("VIETQR_BANK_BIN", "970436")
    VIETQR_BANK_NAME: str = os.getenv("VIETQR_BANK_NAME", "Vietcombank")
    VIETQR_ACCOUNT_NO: str = os.getenv("VIETQR_ACCOUNT_NO", "0123456789")
    VIETQR_ACCOUNT_NAME: str = os.getenv("VIETQR_ACCOUNT_NAME", "CUA HANG SALESAI")

    # Quản trị viên quên mật khẩu: mã xác nhận gửi tới ADMIN_EMAIL.
    # Gửi qua Resend (HTTPS) nếu có RESEND_API_KEY, ngược lại qua SMTP (Gmail + mật khẩu ứng dụng).
    # Render gói miễn phí chặn cổng SMTP nên khi deploy ở đó phải dùng Resend.
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "").strip()
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "").strip()
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "").strip()
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "").replace(" ", "")  # Google hiển thị mật khẩu ứng dụng có dấu cách
    MAIL_FROM: str = os.getenv("MAIL_FROM", "").strip()  # trống: Resend dùng onboarding@resend.dev, SMTP dùng SMTP_USER
    RESET_CODE_MINUTES: int = int(os.getenv("RESET_CODE_MINUTES", "10"))

    PROMPTS_DIR: Path = BASE_DIR / "prompts"
    STATIC_DIR: Path = BASE_DIR / "static"
    LOG_DIR: Path = BASE_DIR / "logs"
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"


settings = Settings()

# Đường dẫn SQLite tương đối được tính theo thư mục gốc dự án, không theo thư mục đang chạy lệnh
if settings.DATABASE_URL.startswith("sqlite:///./"):
    settings.DATABASE_URL = "sqlite:///" + str(BASE_DIR / settings.DATABASE_URL[len("sqlite:///./"):])
