from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Customer, Invoice, User
from app.schemas import CustomerIn, CustomerOut
from app.security import ALL_STAFF, MANAGERS

router = APIRouter(prefix="/api/customers", tags=["customers"])


def _stats(db: Session, customer_id: int) -> dict:
    count, spent, last = db.execute(
        select(func.count(Invoice.id), func.coalesce(func.sum(Invoice.total), 0), func.max(Invoice.created_at))
        .where(Invoice.customer_id == customer_id, Invoice.status == "paid")
    ).one()
    return {"invoice_count": count, "total_spent": int(spent), "last_purchase": last}


@router.get("")
def list_customers(q: str | None = None, group: str | None = None,
                   page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=200),
                   db: Session = Depends(get_db), _: User = Depends(ALL_STAFF)):
    stmt = select(Customer)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Customer.name.ilike(like), Customer.phone.ilike(like), Customer.code.ilike(like)))
    if group:
        stmt = stmt.where(Customer.group == group)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(Customer.id.desc()).offset((page - 1) * size).limit(size)).all()
    return {"total": total, "items": [
        {**CustomerOut.model_validate(c).model_dump(), **_stats(db, c.id)} for c in rows
    ]}


@router.get("/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db), _: User = Depends(ALL_STAFF)):
    c = db.get(Customer, customer_id)
    if c is None:
        raise HTTPException(404, "Không tìm thấy khách hàng")
    history = db.scalars(select(Invoice).where(Invoice.customer_id == customer_id)
                         .order_by(Invoice.created_at.desc()).limit(50)).all()
    return {**CustomerOut.model_validate(c).model_dump(), **_stats(db, c.id), "invoices": [
        {"id": i.id, "code": i.code, "created_at": i.created_at, "total": i.total, "status": i.status,
         "items": ", ".join(f"{it.product.name} x{it.quantity}" for it in i.items)}
        for i in history
    ]}


def _next_customer_code(db: Session) -> str:
    last = db.scalar(select(func.max(Customer.id))) or 0
    return f"KH{last + 1:04d}"


@router.post("", status_code=201)
def create_customer(data: CustomerIn, db: Session = Depends(get_db), _: User = Depends(ALL_STAFF)):
    if data.phone and db.scalar(select(Customer).where(Customer.phone == data.phone)):
        raise HTTPException(400, "Số điện thoại đã được đăng ký cho khách hàng khác")
    values = data.model_dump()
    values["code"] = values["code"] or _next_customer_code(db)
    c = Customer(**values)
    db.add(c)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, "Mã khách hàng đã tồn tại")
    return CustomerOut.model_validate(c)


@router.put("/{customer_id}")
def update_customer(customer_id: int, data: CustomerIn, db: Session = Depends(get_db),
                    _: User = Depends(ALL_STAFF)):
    c = db.get(Customer, customer_id)
    if c is None:
        raise HTTPException(404, "Không tìm thấy khách hàng")
    if data.phone and db.scalar(select(Customer).where(Customer.phone == data.phone, Customer.id != customer_id)):
        raise HTTPException(400, "Số điện thoại đã được đăng ký cho khách hàng khác")
    for k, v in data.model_dump(exclude={"code"} if not data.code else set()).items():
        setattr(c, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, "Mã khách hàng đã tồn tại")
    return CustomerOut.model_validate(c)


@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    c = db.get(Customer, customer_id)
    if c is None:
        raise HTTPException(404, "Không tìm thấy khách hàng")
    if db.scalar(select(func.count(Invoice.id)).where(Invoice.customer_id == customer_id)):
        raise HTTPException(400, "Khách hàng đã có hóa đơn, không thể xóa")
    db.delete(c)
    db.commit()
    return {"ok": True}
