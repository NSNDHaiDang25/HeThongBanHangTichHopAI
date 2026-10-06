"""Gửi email: qua Resend (HTTPS) nếu có RESEND_API_KEY, ngược lại qua SMTP (mặc định Gmail).

Render gói miễn phí chặn kết nối ra cổng SMTP (25/465/587), nên khi deploy ở đó phải dùng Resend.
Resend chưa xác minh tên miền chỉ gửi được tới chính email đăng ký tài khoản Resend.
"""
import base64
import logging
import smtplib
from email.message import EmailMessage

import httpx

from app.config import settings

logger = logging.getLogger("mail")
RESEND_URL = "https://api.resend.com/emails"


class MailError(Exception):
    """Không gửi được email (chưa cấu hình, sai mật khẩu, mạng lỗi...)."""


def mail_configured() -> bool:
    return bool(settings.RESEND_API_KEY or (settings.SMTP_USER and settings.SMTP_PASSWORD))


Attachment = tuple[str, bytes, str]  # (tên file, nội dung, kiểu MIME)


def send_mail(to: str, subject: str, text: str, attachments: list[Attachment] | None = None) -> None:
    if settings.RESEND_API_KEY:
        _send_resend(to, subject, text, attachments or [])
    elif settings.SMTP_USER and settings.SMTP_PASSWORD:
        _send_smtp(to, subject, text, attachments or [])
    else:
        raise MailError("Chưa cấu hình gửi email (RESEND_API_KEY hoặc SMTP_USER / SMTP_PASSWORD)")


def _send_resend(to: str, subject: str, text: str, attachments: list[Attachment]) -> None:
    sender = settings.MAIL_FROM or f"{settings.SHOP_NAME} <onboarding@resend.dev>"
    payload = {"from": sender, "to": [to], "subject": subject, "text": text}
    if attachments:
        payload["attachments"] = [{"filename": name, "content": base64.b64encode(data).decode()}
                                  for name, data, _ in attachments]
    try:
        resp = httpx.post(RESEND_URL, headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
                          json=payload, timeout=30)
    except httpx.HTTPError as e:
        logger.warning("Resend lỗi kết nối: %s", e)
        raise MailError(f"Không kết nối được Resend: {e.__class__.__name__}")
    if resp.status_code >= 300:
        try:
            msg = resp.json().get("message") or resp.text
        except ValueError:
            msg = resp.text
        logger.warning("Resend từ chối gửi (%s): %s", resp.status_code, msg)
        raise MailError(f"Resend từ chối gửi ({resp.status_code}): {msg[:200]}")


def _send_smtp(to: str, subject: str, text: str, attachments: list[Attachment]) -> None:
    msg = EmailMessage()
    msg["From"] = settings.MAIL_FROM or f"{settings.SHOP_NAME} <{settings.SMTP_USER}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(text)
    for name, data, mime in attachments:
        maintype, _, subtype = mime.partition("/")
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=name)
    try:
        if settings.SMTP_PORT == 465:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as s:
                s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                s.send_message(msg)
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as s:
                s.starttls()
                s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                s.send_message(msg)
    except smtplib.SMTPAuthenticationError:
        logger.warning("SMTP từ chối đăng nhập với %s", settings.SMTP_USER)
        raise MailError("Gmail từ chối đăng nhập: kiểm tra SMTP_USER và mật khẩu ứng dụng (App Password)")
    except (smtplib.SMTPException, OSError) as e:
        logger.warning("SMTP lỗi: %s", e)
        raise MailError(f"Không gửi được email qua SMTP: {e.__class__.__name__}")
