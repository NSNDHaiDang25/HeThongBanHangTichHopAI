from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.models import Customer, ImportReceipt, Invoice, InvoiceItem, User
from app.schemas import ImportIn, InvoiceCancelIn, InvoiceIn
from app.security import ALL_STAFF, MANAGERS
from app.services import inventory
from app.services.inventory import BusinessError
from app.services.reports import parse_range

router = APIRouter(prefix="/api", tags=["invoices"])


def invoice_out(inv: Invoice, with_items: bool = True) -> dict:
    data = {
        "id": inv.id, "code": inv.code, "customer_id": inv.customer_id,
        "customer_name": inv.customer.name if inv.customer else "Khách lẻ",
        "customer_phone": inv.customer.phone if inv.customer else None,
        "user_name": inv.user.full_name, "created_at": inv.created_at,
        "subtotal": inv.subtotal, "discount": inv.discount, "total": inv.total,
        "payment_method": inv.payment_method, "cash_received": inv.cash_received,
        "change": inv.cash_received - inv.total if inv.cash_received is not None else None,
        "payment_ref": inv.payment_ref, "status": inv.status, "note": inv.note,
        "cancelled_at": inv.cancelled_at, "cancel_reason": inv.cancel_reason,
    }
    if with_items:
        data["items"] = [{
            "product_id": it.product_id, "product_code": it.product.code, "product_name": it.product.name,
            "image_url": it.product.image_url, "quantity": it.quantity, "unit_price": it.unit_price, "line_total": it.line_total,
        } for it in inv.items]
    return data


def invoice_query(user: User, q: str | None, status: str | None, date_from: str | None,
                  date_to: str | None, payment_method: str | None, customer_id: int | None):
    stmt = select(Invoice)
    if user.role == "staff":
        stmt = stmt.where(Invoice.user_id == user.id)  # nhân viên chỉ xem hóa đơn mình lập
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.outerjoin(Customer).where(
            or_(Invoice.code.ilike(like), Customer.name.ilike(like), Customer.phone.ilike(like)))
    if status:
        stmt = stmt.where(Invoice.status == status)
    if payment_method:
        stmt = stmt.where(Invoice.payment_method == payment_method)
    if customer_id:
        stmt = stmt.where(Invoice.customer_id == customer_id)
    if date_from or date_to:
        start, end = parse_range(date_from, date_to)
        stmt = stmt.where(Invoice.created_at >= start, Invoice.created_at < end)
    return stmt


@router.get("/invoices")
def list_invoices(q: str | None = None, status: str | None = Query(None, pattern="^(paid|cancelled)$"),
                  date_from: str | None = None, date_to: str | None = None,
                  payment_method: str | None = None, customer_id: int | None = None,
                  page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=200),
                  db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    stmt = invoice_query(user, q, status, date_from, date_to, payment_method, customer_id)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    sum_total = db.scalar(select(func.coalesce(func.sum(Invoice.total), 0)).where(
        Invoice.id.in_(stmt.with_only_columns(Invoice.id).where(Invoice.status == "paid"))))
    stmt = stmt.options(joinedload(Invoice.customer), joinedload(Invoice.user))
    rows = db.scalars(stmt.order_by(Invoice.created_at.desc(), Invoice.id.desc())
                      .offset((page - 1) * size).limit(size)).unique().all()
    return {"total": total, "sum_paid": int(sum_total), "items": [invoice_out(i, False) for i in rows]}


def _get_invoice(db: Session, invoice_id: int, user: User) -> Invoice:
    inv = db.scalar(select(Invoice).options(selectinload(Invoice.items).joinedload(InvoiceItem.product))
                    .where(Invoice.id == invoice_id))
    if inv is None or (user.role == "staff" and inv.user_id != user.id):
        raise HTTPException(404, "Không tìm thấy hóa đơn")
    return inv


@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int, db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    return invoice_out(_get_invoice(db, invoice_id, user))


@router.post("/invoices", status_code=201)
def create_invoice(data: InvoiceIn, db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    if user.role == "staff":
        for item in data.items:
            item.unit_price = None  # nhân viên không được tự đặt giá, luôn dùng giá bán niêm yết
    try:
        inv = inventory.create_invoice(db, data, user)
        db.commit()
    except BusinessError as e:
        db.rollback()
        raise HTTPException(400, str(e))
    return invoice_out(_get_invoice(db, inv.id, user))


@router.put("/invoices/{invoice_id}")
def update_invoice(invoice_id: int, data: InvoiceIn, db: Session = Depends(get_db),
                   user: User = Depends(MANAGERS)):
    inv = _get_invoice(db, invoice_id, user)
    try:
        inventory.update_invoice(db, inv, data, user)
        db.commit()
    except BusinessError as e:
        db.rollback()
        raise HTTPException(400, str(e))
    db.expire_all()
    return invoice_out(_get_invoice(db, invoice_id, user))


@router.post("/invoices/{invoice_id}/cancel")
def cancel_invoice(invoice_id: int, data: InvoiceCancelIn, db: Session = Depends(get_db),
                   user: User = Depends(MANAGERS)):
    inv = _get_invoice(db, invoice_id, user)
    try:
        inventory.cancel_invoice(db, inv, data.reason, user)
        db.commit()
    except BusinessError as e:
        db.rollback()
        raise HTTPException(400, str(e))
    return invoice_out(inv)


# ---------------- Phiếu nhập ----------------
def import_out(r: ImportReceipt, with_items: bool = True) -> dict:
    data = {"id": r.id, "code": r.code, "supplier": r.supplier, "note": r.note, "total": r.total,
            "created_at": r.created_at, "user_name": r.user.full_name, "item_count": len(r.items)}
    if with_items:
        data["items"] = [{"product_id": it.product_id, "product_code": it.product.code,
                          "product_name": it.product.name, "quantity": it.quantity,
                          "unit_cost": it.unit_cost, "line_total": it.line_total} for it in r.items]
    return data


@router.get("/imports")
def list_imports(date_from: str | None = None, date_to: str | None = None, q: str | None = None,
                 page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=200),
                 db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    stmt = select(ImportReceipt).options(joinedload(ImportReceipt.user), selectinload(ImportReceipt.items))
    if date_from or date_to:
        start, end = parse_range(date_from, date_to)
        stmt = stmt.where(ImportReceipt.created_at >= start, ImportReceipt.created_at < end)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(ImportReceipt.code.ilike(like), ImportReceipt.supplier.ilike(like)))
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(ImportReceipt.created_at.desc(), ImportReceipt.id.desc())
                      .offset((page - 1) * size).limit(size)).unique().all()
    return {"total": total, "items": [import_out(r, False) for r in rows]}


@router.get("/imports/{receipt_id}")
def get_import(receipt_id: int, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    r = db.get(ImportReceipt, receipt_id)
    if r is None:
        raise HTTPException(404, "Không tìm thấy phiếu nhập")
    return import_out(r)


@router.post("/imports", status_code=201)
def create_import(data: ImportIn, db: Session = Depends(get_db), user: User = Depends(MANAGERS)):
    try:
        r = inventory.create_import(db, data, user)
        db.commit()
    except BusinessError as e:
        db.rollback()
        raise HTTPException(400, str(e))
    return import_out(r)
