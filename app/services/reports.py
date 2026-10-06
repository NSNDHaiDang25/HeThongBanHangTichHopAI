"""Truy vấn thống kê doanh thu, tồn kho, thẻ kho, sản phẩm bán chạy / bán chậm.

Chỉ tính hóa đơn trạng thái `paid` (hóa đơn tạm và hóa đơn đã hủy không tính doanh thu).
Hàng khách trả (phiếu đổi trả) được trừ vào kỳ có phiếu trả: doanh thu trừ tiền hoàn, giá vốn trừ phần hàng
nhập lại kho, số lượng bán trừ số lượng trả.
Nhóm theo ngày/tháng làm ở Python để chạy giống nhau trên SQLite, MySQL, PostgreSQL.
"""
from collections import OrderedDict, defaultdict
from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (Category, Customer, Invoice, InvoiceItem, Product, ReturnItem, ReturnReceipt,
                        StockMovement, now)

MOVE_VI = {"import": "Nhập hàng", "sale": "Bán hàng", "cancel": "Hủy hóa đơn", "edit": "Sửa hóa đơn",
           "adjust": "Kiểm kho", "return": "Khách trả hàng", "import_cancel": "Hủy phiếu nhập"}


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


def _returns_in(start: datetime, end: datetime):
    return (ReturnReceipt.created_at >= start, ReturnReceipt.created_at < end)


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
    ret_count, refunds = db.execute(select(func.count(ReturnReceipt.id), func.coalesce(func.sum(ReturnReceipt.refund_total), 0))
                                    .where(*_returns_in(start, end))).one()
    returned_cost = db.scalar(
        select(func.coalesce(func.sum(ReturnItem.unit_cost * ReturnItem.quantity), 0))
        .join(ReturnReceipt).where(ReturnItem.restock.is_(True), *_returns_in(start, end))
    )
    revenue = int(row[1]) - int(refunds)
    cost = int(cost) - int(returned_cost)
    return {
        "invoice_count": row[0], "gross_sales": int(row[1]), "refunds": int(refunds), "return_count": ret_count,
        "revenue": revenue, "discount": int(row[2]), "cost": cost, "gross_profit": revenue - cost,
    }


def _refunds_by_date(db: Session, start: datetime, end: datetime):
    return db.execute(select(ReturnReceipt.created_at, ReturnReceipt.refund_total).where(*_returns_in(start, end)))


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
    for created_at, refund in _refunds_by_date(db, start, end):
        buckets[created_at.date().isoformat()]["revenue"] -= refund
    return list(buckets.values())


def revenue_by_month(db: Session, year: int) -> list[dict]:
    start, end = datetime(year, 1, 1), datetime(year + 1, 1, 1)
    months = [{"month": f"{year}-{m:02d}", "revenue": 0, "invoice_count": 0} for m in range(1, 13)]
    for created_at, total in db.execute(
        select(Invoice.created_at, Invoice.total).where(*_paid_in(start, end))
    ):
        months[created_at.month - 1]["revenue"] += total
        months[created_at.month - 1]["invoice_count"] += 1
    for created_at, refund in _refunds_by_date(db, start, end):
        months[created_at.month - 1]["revenue"] -= refund
    return months


def _returned_by_product(db: Session, start: datetime, end: datetime) -> dict[int, tuple[int, int]]:
    """product_id -> (số lượng trả, giá trị trả theo đơn giá hóa đơn) trong kỳ."""
    return {pid: (int(q), int(v)) for pid, q, v in db.execute(
        select(ReturnItem.product_id, func.sum(ReturnItem.quantity), func.sum(ReturnItem.unit_price * ReturnItem.quantity))
        .join(ReturnReceipt).where(*_returns_in(start, end)).group_by(ReturnItem.product_id))}


def revenue_by_category(db: Session, start: datetime, end: datetime) -> list[dict]:
    """Doanh thu theo nhóm hàng (theo đơn giá, chưa chia giảm giá hóa đơn), đã trừ hàng trả."""
    cat_name = func.coalesce(Category.name, "Chưa phân nhóm")
    rows = db.execute(
        select(cat_name, func.sum(InvoiceItem.quantity), func.sum(InvoiceItem.line_total))
        .select_from(InvoiceItem).join(Invoice).join(Product)
        .outerjoin(Category, Product.category_id == Category.id)
        .where(*_paid_in(start, end))
        .group_by(Category.name)
    ).all()
    out: dict[str, list[int]] = {r[0]: [int(r[1]), int(r[2])] for r in rows}
    returned = _returned_by_product(db, start, end)
    if returned:
        cats = dict(db.execute(select(Product.id, cat_name).outerjoin(Category, Product.category_id == Category.id)
                               .where(Product.id.in_(returned))).all())
        for pid, (q, v) in returned.items():
            c = out.setdefault(cats[pid], [0, 0])
            c[0] -= q
            c[1] -= v
    rows = [{"category": k, "quantity": q, "revenue": v} for k, (q, v) in out.items() if q > 0 or v > 0]
    return sorted(rows, key=lambda r: -r["revenue"])


def _net_sold(db: Session, start: datetime, end: datetime) -> dict[int, tuple[int, int]]:
    """product_id -> (số lượng bán thực, doanh thu thực) trong kỳ, đã trừ hàng trả."""
    out = {pid: [int(q), int(v)] for pid, q, v in db.execute(
        select(InvoiceItem.product_id, func.sum(InvoiceItem.quantity), func.sum(InvoiceItem.line_total))
        .join(Invoice).where(*_paid_in(start, end)).group_by(InvoiceItem.product_id))}
    for pid, (q, v) in _returned_by_product(db, start, end).items():
        o = out.setdefault(pid, [0, 0])
        o[0] -= q
        o[1] -= v
    return {pid: (q, v) for pid, (q, v) in out.items()}


def top_products(db: Session, start: datetime, end: datetime, limit: int = 10) -> list[dict]:
    sold = {pid: qv for pid, qv in _net_sold(db, start, end).items() if qv[0] > 0}
    products = {p.id: p for p in db.scalars(select(Product).where(Product.id.in_(sold)))}
    ranked = sorted(sold.items(), key=lambda x: (-x[1][0], -x[1][1], products[x[0]].code))[:limit]
    return [{"code": products[pid].code, "name": products[pid].name, "stock": products[pid].stock,
             "quantity": q, "revenue": v} for pid, (q, v) in ranked]


def slow_products(db: Session, start: datetime, end: datetime, limit: int = 10) -> list[dict]:
    """Sản phẩm đang kinh doanh, còn tồn nhưng bán ít nhất trong kỳ (kể cả bán 0)."""
    sold = _net_sold(db, start, end)
    products = db.scalars(select(Product).where(Product.status == "active", Product.stock > 0)).all()
    ranked = sorted(products, key=lambda p: (max(0, sold.get(p.id, (0, 0))[0]), -p.stock, p.code))[:limit]
    return [{"code": p.code, "name": p.name, "stock": p.stock, "quantity": max(0, sold.get(p.id, (0, 0))[0])}
            for p in ranked]


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


def inventory_report(db: Session, category_id: int | None = None, stock: str | None = None) -> dict:
    """Báo cáo tồn kho hiện tại: số lượng, giá trị tồn theo giá vốn / giá bán, theo nhóm hàng."""
    stmt = select(Product).where(Product.status == "active")
    if category_id:
        stmt = stmt.where(Product.category_id == category_id)
    products = db.scalars(stmt.order_by(Product.code)).all()
    cats = dict(db.execute(select(Category.id, Category.name)).all())
    by_cat: dict[str, dict] = defaultdict(lambda: {"products": 0, "units": 0, "value_at_cost": 0, "value_at_price": 0})
    for p in products:
        c = by_cat[cats.get(p.category_id, "Chưa phân nhóm")]
        c["products"] += 1
        c["units"] += p.stock
        c["value_at_cost"] += p.stock * p.cost_price
        c["value_at_price"] += p.stock * p.sale_price
    state = lambda p: "out" if p.stock <= 0 else "low" if p.stock <= p.min_stock else "ok"  # noqa: E731
    items = [{"id": p.id, "code": p.code, "name": p.name, "image_url": p.image_url,
              "category_name": cats.get(p.category_id), "stock": p.stock, "min_stock": p.min_stock,
              "cost_price": p.cost_price, "sale_price": p.sale_price, "value_at_cost": p.stock * p.cost_price,
              "value_at_price": p.stock * p.sale_price, "state": state(p)}
             for p in products if not stock or state(p) == stock]
    return {
        "summary": {"products": len(products), "units": sum(p.stock for p in products),
                    "value_at_cost": sum(p.stock * p.cost_price for p in products),
                    "value_at_price": sum(p.stock * p.sale_price for p in products),
                    "low": sum(state(p) == "low" for p in products), "out": sum(state(p) == "out" for p in products)},
        "by_category": sorted(({"category": k, **v} for k, v in by_cat.items()), key=lambda r: -r["value_at_cost"]),
        "items": items,
    }


def stock_card(db: Session, product: Product, start: datetime, end: datetime) -> dict:
    """Thẻ kho một sản phẩm trong kỳ: tồn đầu kỳ, từng lần nhập / xuất, tổng nhập, tổng xuất, tồn cuối kỳ."""
    before = db.scalar(select(StockMovement).where(StockMovement.product_id == product.id,
                                                   StockMovement.created_at < start)
                       .order_by(StockMovement.created_at.desc(), StockMovement.id.desc()))
    opening = before.stock_after if before else 0
    moves = db.scalars(select(StockMovement).where(StockMovement.product_id == product.id,
                                                   StockMovement.created_at >= start, StockMovement.created_at < end)
                       .order_by(StockMovement.created_at, StockMovement.id)).all()
    return {
        "product": {"id": product.id, "code": product.code, "name": product.name, "stock": product.stock,
                    "image_url": product.image_url},
        "period": {"from": start.date().isoformat(), "to": (end - timedelta(days=1)).date().isoformat()},
        "opening": opening,
        "total_in": sum(m.change for m in moves if m.change > 0),
        "total_out": -sum(m.change for m in moves if m.change < 0),
        "closing": moves[-1].stock_after if moves else opening,
        "movements": [{"created_at": m.created_at, "type": m.type, "type_label": MOVE_VI.get(m.type, m.type),
                       "ref_code": m.ref_code, "change": m.change, "stock_after": m.stock_after, "note": m.note}
                      for m in moves],
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
