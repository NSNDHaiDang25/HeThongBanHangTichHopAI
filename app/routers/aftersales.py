"""Đổi trả hàng và bảo hành: thu ngân và chủ cửa hàng.

Tra hóa đơn ở đây theo đúng mã (khách mang hóa đơn / quét mã QR in trên hóa đơn), nên thu ngân tra được cả
hóa đơn do người khác lập; danh sách hóa đơn vẫn chỉ hiện hóa đơn của mình.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.models import Invoice, ReturnReceipt, User, WarrantyTicket
from app.schemas import ReturnIn, WarrantyIn, WarrantyUpdate
from app.security import ALL_STAFF
from app.services import aftersales
from app.services.inventory import BusinessError
from app.services.reports import parse_range

router = APIRouter(prefix="/api", tags=["aftersales"])


def _bad(e: BusinessError):
    return HTTPException(400, str(e))


@router.get("/aftersales/invoice")
def lookup_invoice(code: str, db: Session = Depends(get_db), _: User = Depends(ALL_STAFF)):
    try:
        return aftersales.invoice_lookup(db, aftersales.find_invoice(db, code))
    except BusinessError as e:
        raise HTTPException(404, str(e))


@router.get("/aftersales/serial")
def lookup_serial(serial: str, db: Session = Depends(get_db), _: User = Depends(ALL_STAFF)):
    """Tra bảo hành theo serial / IMEI."""
    try:
        return aftersales.serial_lookup(db, serial)
    except BusinessError as e:
        raise HTTPException(404, str(e))


# ---------------- Đổi trả ----------------
@router.get("/returns")
def list_returns(q: str | None = None, date_from: str | None = None, date_to: str | None = None,
                 page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=200),
                 db: Session = Depends(get_db), _: User = Depends(ALL_STAFF)):
    stmt = select(ReturnReceipt).join(Invoice, ReturnReceipt.invoice_id == Invoice.id)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(ReturnReceipt.code.ilike(like), Invoice.code.ilike(like)))
    if date_from or date_to:
        start, end = parse_range(date_from, date_to)
        stmt = stmt.where(ReturnReceipt.created_at >= start, ReturnReceipt.created_at < end)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.options(joinedload(ReturnReceipt.user), selectinload(ReturnReceipt.items),
                                   joinedload(ReturnReceipt.invoice).joinedload(Invoice.customer))
                      .order_by(ReturnReceipt.id.desc()).offset((page - 1) * size).limit(size)).unique().all()
    return {"total": total, "items": [aftersales.return_out(r) for r in rows]}


@router.get("/returns/{return_id}")
def get_return(return_id: int, db: Session = Depends(get_db), _: User = Depends(ALL_STAFF)):
    r = db.get(ReturnReceipt, return_id)
    if r is None:
        raise HTTPException(404, "Không tìm thấy phiếu đổi trả")
    return aftersales.return_out(r)


@router.post("/returns", status_code=201)
def create_return(data: ReturnIn, db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    try:
        r = aftersales.create_return(db, data, user)
        db.commit()
    except BusinessError as e:
        db.rollback()
        raise _bad(e)
    return aftersales.return_out(r)


# ---------------- Bảo hành ----------------
@router.get("/warranty")
def list_tickets(q: str | None = None, status: str | None = Query(None, pattern="^(received|processing|done|rejected|open)$"),
                 page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=200),
                 db: Session = Depends(get_db), _: User = Depends(ALL_STAFF)):
    stmt = select(WarrantyTicket)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(WarrantyTicket.code.ilike(like), WarrantyTicket.customer_name.ilike(like),
                              WarrantyTicket.customer_phone.ilike(like), WarrantyTicket.serial.ilike(like)))
    if status == "open":
        stmt = stmt.where(WarrantyTicket.status.in_(("received", "processing")))
    elif status:
        stmt = stmt.where(WarrantyTicket.status == status)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.options(joinedload(WarrantyTicket.product), joinedload(WarrantyTicket.invoice),
                                   joinedload(WarrantyTicket.user))
                      .order_by(WarrantyTicket.id.desc()).offset((page - 1) * size).limit(size)).unique().all()
    return {"total": total, "items": [aftersales.ticket_out(t) for t in rows]}


@router.get("/warranty/{ticket_id}")
def get_ticket(ticket_id: int, db: Session = Depends(get_db), _: User = Depends(ALL_STAFF)):
    t = db.get(WarrantyTicket, ticket_id)
    if t is None:
        raise HTTPException(404, "Không tìm thấy phiếu bảo hành")
    return aftersales.ticket_out(t)


@router.post("/warranty", status_code=201)
def create_ticket(data: WarrantyIn, db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    try:
        t = aftersales.create_ticket(db, data, user)
        db.commit()
    except BusinessError as e:
        db.rollback()
        raise _bad(e)
    return aftersales.ticket_out(t)


@router.put("/warranty/{ticket_id}")
def update_ticket(ticket_id: int, data: WarrantyUpdate, db: Session = Depends(get_db),
                  user: User = Depends(ALL_STAFF)):
    t = db.get(WarrantyTicket, ticket_id)
    if t is None:
        raise HTTPException(404, "Không tìm thấy phiếu bảo hành")
    try:
        aftersales.update_ticket(db, t, data, user)
        db.commit()
    except BusinessError as e:
        db.rollback()
        raise _bad(e)
    return aftersales.ticket_out(t)
