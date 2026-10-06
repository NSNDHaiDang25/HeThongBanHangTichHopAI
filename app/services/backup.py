"""Sao lưu và khôi phục dữ liệu (quản trị viên).

SQLite: bản sao lưu là chính file CSDL, chụp bằng backup API của SQLite nên vẫn nhất quán khi hệ thống đang chạy.
Khôi phục: kiểm tra file tải lên đúng là CSDL của SalesAI rồi chép đè toàn bộ vào CSDL đang dùng.
CSDL khác (PostgreSQL, MySQL): sao lưu ra JSON để lưu trữ; khôi phục dùng công cụ của hệ quản trị CSDL đó.
"""
import json
import sqlite3
import tempfile
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from app.database import Base, ensure_schema

REQUIRED_TABLES = {"users", "products", "invoices", "invoice_items", "customers", "stock_movements"}
MAX_RESTORE_BYTES = 200 * 1024 * 1024


class BackupError(Exception):
    pass


def is_sqlite(engine: Engine) -> bool:
    return engine.url.get_backend_name() == "sqlite"


def _driver_connection(engine: Engine):
    raw = engine.raw_connection()
    return raw, raw.driver_connection


def backup_bytes(engine: Engine) -> tuple[bytes, str]:
    """Trả về (nội dung, đuôi file)."""
    if is_sqlite(engine):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "backup.db"
            raw, src = _driver_connection(engine)
            try:
                dst = sqlite3.connect(path)
                with dst:
                    src.backup(dst)
                dst.close()
            finally:
                raw.close()
            return path.read_bytes(), "db"
    data = {}
    with engine.connect() as conn:
        for table in Base.metadata.sorted_tables:
            data[table.name] = [dict(r._mapping) for r in conn.execute(select(table))]
    default = lambda v: v.isoformat() if isinstance(v, (date, datetime)) else str(v)  # noqa: E731
    return json.dumps({"format": "salesai-backup", "tables": data}, ensure_ascii=False, default=default).encode(), "json"


def restore_sqlite(engine: Engine, content: bytes) -> dict:
    """Chép đè CSDL đang dùng bằng file sao lưu. Trả về số dòng một vài bảng chính để báo lại."""
    if not is_sqlite(engine):
        raise BackupError("Khôi phục trên giao diện chỉ hỗ trợ CSDL SQLite. Với PostgreSQL / MySQL hãy dùng công cụ của CSDL")
    if not content.startswith(b"SQLite format 3\x00"):
        raise BackupError("File không phải bản sao lưu SQLite (.db) của hệ thống")
    if len(content) > MAX_RESTORE_BYTES:
        raise BackupError("File sao lưu quá lớn")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "restore.db"
        path.write_bytes(content)
        src = sqlite3.connect(path)
        try:
            tables = {r[0] for r in src.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            missing = REQUIRED_TABLES - tables
            if missing:
                raise BackupError(f"File sao lưu thiếu bảng: {', '.join(sorted(missing))}")
            if src.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise BackupError("File sao lưu bị hỏng")
            if not src.execute("SELECT COUNT(*) FROM users WHERE role='admin' AND is_active").fetchone()[0]:
                raise BackupError("File sao lưu không có tài khoản quản trị viên nào đang hoạt động")
            counts = {t: src.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                      for t in ("users", "products", "customers", "invoices")}
            raw, dst = _driver_connection(engine)
            try:
                src.backup(dst)
            finally:
                raw.close()
        except sqlite3.DatabaseError as e:
            raise BackupError(f"Không đọc được file sao lưu: {e}")
        finally:
            src.close()
    if not isinstance(engine.pool, StaticPool):  # StaticPool (CSDL trong bộ nhớ khi test) chỉ có một kết nối
        engine.dispose()  # bỏ các kết nối cũ đang giữ trong pool
    ensure_schema(engine)  # bản sao lưu từ phiên bản cũ: bổ sung bảng / cột mới
    return counts
