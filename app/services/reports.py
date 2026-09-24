"""Truy vấn thống kê doanh thu, tồn kho, sản phẩm bán chạy / bán chậm.

Chỉ tính hóa đơn trạng thái `paid` (hóa đơn đã hủy không tính doanh thu).
Nhóm theo ngày/tháng làm ở Python để chạy giống nhau trên SQLite, MySQL, PostgreSQL.
"""
from collections import OrderedDict
from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Category, Customer, Invoice, InvoiceItem, Product, now


def parse_range(date_from: str | date | None, date_to: str | date | None,
                default_days: int = 30) -> tuple[datetime, datetime]:
    """Trả về [start, end) theo ngày. Mặc định: 30 ngày gần nhất tính cả hôm nay."""
    def to_date(v):
        if v is None or v == "":
            return None
        return v if isinstance(v, date) else date.fromisoformat(v)

    d_to = to_date(date_to) or now().date()
    d_from = to_date(date_from) or d_to - timedelta(days=default_days - 1)
    if d_from > d_to:
        d_from, d_to = d_to, d_from
    return datetime.combine(d_from, time.min), datetime.combine(d_to + timedelta(days=1), time.min)


def _paid_in(start: datetime, end: datetime):
    return (Invoice.status == "paid", Invoice.created_at >= start, Invoice.created_at < end)


def revenue_total(db: Session, start: datetime, end: datetime) -> dict:
    row = db.execute(
        select(func.count(Invoice.id), func.coalesce(func.sum(Invoice.total), 0),
               func.coalesce(func.sum(Invoice.discount), 0))
        .where(*_paid_in(start, end))
    ).one()
    cost = db.scalar(
        select(func.coalesce(func.sum(InvoiceItem.unit_cost * InvoiceItem.quantity), 0))
        .join(Invoice).where(*_paid_in(start, end))
    )
    return {
        "invoice_count": row[0], "revenue": int(row[1]), "discount": int(row[2]),
        "cost": int(cost), "gross_profit": int(row[1]) - int(cost),
    }


def revenue_by_day(db: Session, start: datetime, end: datetime) -> list[dict]:
    buckets: OrderedDict[str, dict] = OrderedDict()
    d = start.date()
    while d < end.date():
        buckets[d.isoformat()] = {"date": d.isoformat(), "revenue": 0, "invoice_count": 0}
        d += timedelta(days=1)
    for created_at, total in db.execute(
        select(Invoice.created_at, Invoice.total).where(*_paid_in(start, end))
    ):
        b = buckets[created_at.date().isoformat()]
        b["revenue"] += total
        b["invoice_count"] += 1
    return list(buckets.values())


def revenue_by_month(db: Session, year: int) -> list[dict]:
    start, end = datetime(year, 1, 1), datetime(year + 1, 1, 1)
    months = [{"month": f"{year}-{m:02d}", "revenue": 0, "invoice_count": 0} for m in range(1, 13)]
    for created_at, total in db.execute(
        select(Invoice.created_at, Invoice.total).where(*_paid_in(start, end))
    ):
        months[created_at.month - 1]["revenue"] += total
        months[created_at.month - 1]["invoice_count"] += 1
    return months


def revenue_by_category(db: Session, start: datetime, end: datetime) -> list[dict]:
    rows = db.execute(
        select(func.coalesce(Category.name, "Chưa phân nhóm"),
               func.sum(InvoiceItem.quantity), func.sum(InvoiceItem.line_total))
        .select_from(InvoiceItem).join(Invoice).join(Product)
        .outerjoin(Category, Product.category_id == Category.id)
        .where(*_paid_in(start, end))
        .group_by(Category.name)
        .order_by(func.sum(InvoiceItem.line_total).desc())
    ).all()
    return [{"category": r[0], "quantity": int(r[1]), "revenue": int(r[2])} for r in rows]


def top_products(db: Session, start: datetime, end: datetime, limit: int = 10) -> list[dict]:
    rows = db.execute(
        select(Product.code, Product.name, Product.stock,
               func.sum(InvoiceItem.quantity).label("qty"), func.sum(InvoiceItem.line_total))
        .select_from(InvoiceItem).join(Invoice).join(Product)
        .where(*_paid_in(start, end))
        .group_by(Product.id)
        .order_by(func.sum(InvoiceItem.quantity).desc(), func.sum(InvoiceItem.line_total).desc())
        .limit(limit)
    ).all()
    return [{"code": r[0], "name": r[1], "stock": r[2], "quantity": int(r[3]), "revenue": int(r[4])}
            for r in rows]


def slow_products(db: Session, start: datetime, end: datetime, limit: int = 10) -> list[dict]:
    """Sản phẩm đang kinh doanh, còn tồn nhưng bán ít nhất trong kỳ (kể cả bán 0)."""
    sold = (
        select(InvoiceItem.product_id, func.sum(InvoiceItem.quantity).label("qty"))
        .join(Invoice).where(*_paid_in(start, end))
        .group_by(InvoiceItem.product_id).subquery()
    )
    rows = db.execute(
        select(Product.code, Product.name, Product.stock, func.coalesce(sold.c.qty, 0))
        .outerjoin(sold, sold.c.product_id == Product.id)
        .where(Product.status == "active", Product.stock > 0)
        .order_by(func.coalesce(sold.c.qty, 0).asc(), Product.stock.desc())
        .limit(limit)
    ).all()
    return [{"code": r[0], "name": r[1], "stock": r[2], "quantity": int(r[3])} for r in rows]


def low_stock(db: Session) -> list[dict]:
    rows = db.scalars(
        select(Product).where(Product.status == "active", Product.stock <= Product.min_stock)
        .order_by(Product.stock)
    ).all()
    return [{"code": p.code, "name": p.name, "stock": p.stock, "min_stock": p.min_stock} for p in rows]


def dashboard(db: Session) -> dict:
    today = now().date()
    t_start, t_end = parse_range(today, today)
    m_start = datetime(today.year, today.month, 1)
    last30_start, last30_end = parse_range(None, None, 30)
    return {
        "today": revenue_total(db, t_start, t_end),
        "month": revenue_total(db, m_start, t_end),
        "customer_count": db.scalar(select(func.count(Customer.id))),
        "product_count": db.scalar(select(func.count(Product.id)).where(Product.status == "active")),
        "low_stock": low_stock(db),
        "daily_30": revenue_by_day(db, last30_start, last30_end),
        "top_products_30": top_products(db, last30_start, last30_end, 5),
    }


def ai_data_context(db: Session, start: datetime, end: datetime) -> dict:
    """Gói dữ liệu tổng hợp gửi cho AI. Chỉ số liệu kinh doanh, KHÔNG có thông tin cá nhân khách hàng."""
    period_days = (end - start).days
    prev_start = start - timedelta(days=period_days)
    return {
        "period": {"from": start.date().isoformat(), "to": (end - timedelta(days=1)).date().isoformat(),
                   "days": period_days},
        "summary": revenue_total(db, start, end),
        "previous_period_summary": revenue_total(db, prev_start, start),
        "revenue_by_category": revenue_by_category(db, start, end),
        "top_products": top_products(db, start, end, 10),
        "slow_products": slow_products(db, start, end, 10),
        "low_stock": low_stock(db),
        "revenue_by_day": [d for d in revenue_by_day(db, start, end) if d["invoice_count"]],
    }
