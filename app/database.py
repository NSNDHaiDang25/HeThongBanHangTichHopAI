from pathlib import Path

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


def make_engine(url: str, **kwargs):
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        db_path = url.replace("sqlite:///", "", 1)
        if db_path and db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(url, connect_args=connect_args, **kwargs)
    if url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _fk_on(dbapi_conn, _):
            dbapi_conn.execute("PRAGMA foreign_keys=ON")
    return engine


engine = make_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


# Cột được thêm sau phiên bản đầu. create_all() không sửa bảng đã có nên bổ sung bằng ALTER TABLE,
# giúp CSDL cũ vẫn chạy mà không phải xóa dữ liệu.
ADDED_COLUMNS = {
    "users": {"pending": "BOOLEAN NOT NULL DEFAULT FALSE", "email": "VARCHAR(100)"},
    "products": {"image_url": "VARCHAR(255)", "warranty_months": "INTEGER NOT NULL DEFAULT 0",
                 "track_serial": "BOOLEAN NOT NULL DEFAULT FALSE"},
    "customers": {"points": "INTEGER NOT NULL DEFAULT 0"},
    "invoices": {"cash_received": "INTEGER", "payment_ref": "VARCHAR(50)", "promotion_id": "INTEGER",
                 "cancel_requested_at": "TIMESTAMP", "cancel_requested_by": "INTEGER",
                 "tier_discount": "INTEGER NOT NULL DEFAULT 0", "promo_discount": "INTEGER NOT NULL DEFAULT 0",
                 "points_used": "INTEGER NOT NULL DEFAULT 0", "points_discount": "INTEGER NOT NULL DEFAULT 0",
                 "points_earned": "INTEGER NOT NULL DEFAULT 0"},
    "invoice_items": {"serials": "JSON"},
    "import_receipts": {"supplier_id": "INTEGER", "status": "VARCHAR(20) NOT NULL DEFAULT 'completed'",
                        "confirmed_at": "TIMESTAMP", "confirmed_by": "INTEGER", "cancelled_at": "TIMESTAMP",
                        "cancel_reason": "VARCHAR(255)"},
    "import_items": {"serials": "JSON"},
}


def ensure_schema(bind) -> None:
    Base.metadata.create_all(bind)
    inspector = inspect(bind)
    with bind.begin() as conn:
        for table, columns in ADDED_COLUMNS.items():
            existing = {c["name"] for c in inspector.get_columns(table)}
            for name, ddl in columns.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
