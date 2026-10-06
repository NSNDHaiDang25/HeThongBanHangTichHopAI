"""Quản trị hệ thống (chỉ quản trị viên): cấu hình kỹ thuật và AI, sao lưu / khôi phục, nhật ký hệ thống.
Tham số kinh doanh (chủ cửa hàng) cũng ở đây vì dùng chung cơ chế lưu cấu hình.

Quản trị viên không xem được doanh thu, giá vốn: nhật ký gọi AI chỉ hiện thời điểm, chức năng, model, kết quả,
không hiện nội dung câu hỏi / câu trả lời (có thể chứa số liệu kinh doanh).
"""
import json
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import AuditLog, Customer, Invoice, Product, User
from app.schemas import SettingsUpdate
from app.security import ADMIN_ONLY, MANAGERS
from app.services import backup, system_config
from app.services.audit import ACTIONS, audit
from app.services.mailer import mail_configured
from app.services.reports import parse_range

router = APIRouter(prefix="/api", tags=["admin"])


def _engine(db: Session):
    return db.get_bind()


def _save(db: Session, user: User, group: str, data: SettingsUpdate) -> dict:
    try:
        changed = system_config.update(db, user, group, data.values)
    except ValueError as e:
        db.rollback()
        raise HTTPException(400, str(e))
    db.commit()
    return {"ok": True, "changed": changed, "params": system_config.snapshot(group)}


@router.get("/admin/settings")
def get_settings(db: Session = Depends(get_db), _: User = Depends(ADMIN_ONLY)):
    key = settings.GEMINI_API_KEY
    return {
        "params": system_config.snapshot("tech"),
        "info": {
            "database": _engine(db).url.get_backend_name(),
            "gemini_key": f"{key[:4]}...{key[-4:]}" if len(key) > 12 else ("đã cấu hình" if key else None),
            "mail": mail_configured(), "admin_email": settings.ADMIN_EMAIL or None,
            "version": "2.0.0",
        },
    }


@router.put("/admin/settings")
def put_settings(data: SettingsUpdate, db: Session = Depends(get_db), user: User = Depends(ADMIN_ONLY)):
    return _save(db, user, "tech", data)


@router.get("/business-settings")
def get_business(_: User = Depends(MANAGERS)):
    return {"params": system_config.snapshot("business")}


@router.put("/business-settings")
def put_business(data: SettingsUpdate, db: Session = Depends(get_db), user: User = Depends(MANAGERS)):
    return _save(db, user, "business", data)


# ---------------- Sao lưu / khôi phục ----------------
@router.get("/admin/backup/info")
def backup_info(db: Session = Depends(get_db), _: User = Depends(ADMIN_ONLY)):
    last = db.scalar(select(AuditLog).where(AuditLog.action == "backup").order_by(AuditLog.id.desc()))
    last_restore = db.scalar(select(AuditLog).where(AuditLog.action == "restore").order_by(AuditLog.id.desc()))
    engine = _engine(db)
    return {
        "database": engine.url.get_backend_name(), "can_restore": backup.is_sqlite(engine),
        "last_backup": {"at": last.created_at, "by": last.username} if last else None,
        "last_restore": {"at": last_restore.created_at, "by": last_restore.username} if last_restore else None,
        "counts": {"users": db.scalar(select(func.count(User.id))), "products": db.scalar(select(func.count(Product.id))),
                   "customers": db.scalar(select(func.count(Customer.id))),
                   "invoices": db.scalar(select(func.count(Invoice.id)))},
    }


@router.get("/admin/backup")
def download_backup(db: Session = Depends(get_db), user: User = Depends(ADMIN_ONLY)):
    db.commit()  # kết thúc giao dịch đọc đang mở trước khi chụp CSDL
    content, ext = backup.backup_bytes(_engine(db))
    name = f"salesai_backup_{datetime.now():%Y%m%d_%H%M%S}.{ext}"
    audit(db, user, "backup", f"{name} ({len(content) // 1024} KB)")
    db.commit()
    media = "application/x-sqlite3" if ext == "db" else "application/json"
    return Response(content, media_type=media, headers={"Content-Disposition": f'attachment; filename="{name}"'})


@router.post("/admin/restore")
def restore_backup(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(ADMIN_ONLY)):
    """Khôi phục toàn bộ dữ liệu từ file sao lưu .db. Dữ liệu hiện tại bị thay thế hoàn toàn."""
    content = file.file.read(backup.MAX_RESTORE_BYTES + 1)
    username = user.username
    db.rollback()  # nhả khóa đọc của phiên hiện tại để chép đè CSDL
    try:
        counts = backup.restore_sqlite(_engine(db), content)
    except backup.BackupError as e:
        raise HTTPException(400, str(e))
    db.expire_all()
    system_config.reload(db)  # tham số đã lưu trong bản sao lưu
    audit(db, None, "restore", f"Từ file {file.filename}: {counts['products']} sản phẩm, {counts['customers']} khách, "
                               f"{counts['invoices']} hóa đơn", username=username)
    db.commit()
    return {"ok": True, "counts": counts,
            "message": "Đã khôi phục dữ liệu. Mọi người cần đăng nhập lại nếu tài khoản trong bản sao lưu khác hiện tại."}


# ---------------- Nhật ký hệ thống ----------------
@router.get("/admin/audit-logs")
def audit_logs(q: str | None = None, action: str | None = None, date_from: str | None = None,
               date_to: str | None = None, page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=200),
               db: Session = Depends(get_db), _: User = Depends(ADMIN_ONLY)):
    stmt = select(AuditLog)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(AuditLog.username.ilike(like), AuditLog.detail.ilike(like)))
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if date_from or date_to:
        start, end = parse_range(date_from, date_to)
        stmt = stmt.where(AuditLog.created_at >= start, AuditLog.created_at < end)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(AuditLog.id.desc()).offset((page - 1) * size).limit(size)).all()
    return {"total": total, "actions": ACTIONS, "items": [
        {"id": r.id, "created_at": r.created_at, "username": r.username, "action": r.action,
         "action_label": ACTIONS.get(r.action, r.action), "detail": r.detail} for r in rows]}


@router.get("/admin/ai-logs")
def ai_logs(limit: int = Query(200, ge=1, le=1000), _: User = Depends(ADMIN_ONLY)):
    """Nhật ký gọi AI (logs/ai_calls.jsonl), mới nhất trước. Bỏ nội dung câu hỏi / trả lời."""
    path = settings.LOG_DIR / "ai_calls.jsonl"
    if not path.exists():
        return {"items": [], "summary": {}}
    with open(path, "rb") as f:
        f.seek(0, 2)
        f.seek(max(0, f.tell() - 512 * 1024))  # chỉ đọc phần cuối file
        lines = f.read().decode("utf-8", "ignore").splitlines()
    items = []
    for line in reversed(lines):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        items.append({k: r.get(k) for k in ("time", "feature", "model", "status", "latency_ms")})
        if len(items) >= limit:
            break
    ok = [x for x in items if x["status"] == "ok"]
    summary = {"calls": len(items), "ok": len(ok), "errors": len(items) - len(ok),
               "avg_latency_ms": round(sum(x["latency_ms"] or 0 for x in ok) / len(ok)) if ok else None}
    return {"items": items, "summary": summary}
