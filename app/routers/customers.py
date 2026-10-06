from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Customer, CustomerTier, Invoice, PointTransaction, User
from app.schemas import CustomerIn, CustomerOut, PointsAdjustIn, TierIn
from app.security import ALL_STAFF, MANAGERS
from app.services import loyalty
from app.services.audit import audit

router = APIRouter(prefix="/api", tags=["customers"])


def _stats(db: Session, ids: list[int]) -> dict[int, dict]:
    """Số hóa đơn, tổng chi tiêu thực (trừ tiền hoàn trả hàng), lần mua gần nhất, hạng thành viên."""
    rows = {cid: (n, last) for cid, n, last in db.execute(
        select(Invoice.customer_id, func.count(Invoice.id), func.max(Invoice.created_at))
        .where(Invoice.customer_id.in_(ids), Invoice.status == "paid").group_by(Invoice.customer_id))}
    spent = loyalty.spent_by(db, ids)
    tiers = loyalty.all_tiers(db)
    out = {}
    for cid in ids:
        n, last = rows.get(cid, (0, None))
        out[cid] = {"invoice_count": n, "total_spent": spent.get(cid, 0), "last_purchase": last,
                    "tier": loyalty.tier_dict(loyalty.tier_for(tiers, spent.get(cid, 0)))}
    return out


@router.get("/customers")
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
    stats = _stats(db, [c.id for c in rows])
    return {"total": total, "items": [{**CustomerOut.model_validate(c).model_dump(), **stats[c.id]} for c in rows]}


@router.get("/customers/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db), _: User = Depends(ALL_STAFF)):
    c = db.get(Customer, customer_id)
    if c is None:
        raise HTTPException(404, "Không tìm thấy khách hàng")
    history = db.scalars(select(Invoice).where(Invoice.customer_id == customer_id, Invoice.status != "pending")
                         .order_by(Invoice.created_at.desc()).limit(50)).all()
    points = db.scalars(select(PointTransaction).where(PointTransaction.customer_id == customer_id)
                        .order_by(PointTransaction.id.desc()).limit(30)).all()
    return {**CustomerOut.model_validate(c).model_dump(), **_stats(db, [c.id])[c.id], "invoices": [
        {"id": i.id, "code": i.code, "created_at": i.created_at, "total": i.total, "status": i.status,
         "refunded": sum(r.refund_total for r in i.returns),
         "items": ", ".join(f"{it.product.name} x{it.quantity}" for it in i.items)}
        for i in history
    ], "point_history": [
        {"created_at": p.created_at, "change": p.change, "balance_after": p.balance_after,
         "type": loyalty.POINT_TYPES.get(p.type, p.type), "ref_code": p.ref_code, "note": p.note} for p in points
    ]}


def _next_customer_code(db: Session) -> str:
    last = db.scalar(select(func.max(Customer.id))) or 0
    return f"KH{last + 1:04d}"


@router.post("/customers", status_code=201)
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


@router.put("/customers/{customer_id}")
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


@router.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    c = db.get(Customer, customer_id)
    if c is None:
        raise HTTPException(404, "Không tìm thấy khách hàng")
    if db.scalar(select(func.count(Invoice.id)).where(Invoice.customer_id == customer_id)):
        raise HTTPException(400, "Khách hàng đã có hóa đơn, không thể xóa")
    db.query(PointTransaction).filter(PointTransaction.customer_id == customer_id).delete()
    db.delete(c)
    db.commit()
    return {"ok": True}


@router.post("/customers/{customer_id}/points")
def adjust_points(customer_id: int, data: PointsAdjustIn, db: Session = Depends(get_db),
                  user: User = Depends(MANAGERS)):
    """Chủ cửa hàng điều chỉnh điểm tích lũy (tặng điểm, sửa sai sót...), bắt buộc ghi lý do."""
    c = db.get(Customer, customer_id)
    if c is None:
        raise HTTPException(404, "Không tìm thấy khách hàng")
    try:
        loyalty.change_points(db, c, data.change, "adjust", None, user, data.note)
    except loyalty.PointsError as e:
        raise HTTPException(400, str(e))
    audit(db, user, "points_adjust", f"{c.code}: {data.change:+d} điểm ({data.note})")
    db.commit()
    return {"ok": True, "points": c.points}


# ---------------- Hạng thành viên ----------------
def _tier_out(t: CustomerTier) -> dict:
    return {"id": t.id, "name": t.name, "min_spent": t.min_spent, "discount_percent": t.discount_percent,
            "note": t.note}


@router.get("/tiers")
def list_tiers(db: Session = Depends(get_db), _: User = Depends(ALL_STAFF)):
    return [_tier_out(t) for t in loyalty.all_tiers(db)]


def _save_tier(db: Session, t: CustomerTier, data: TierIn) -> dict:
    name = " ".join(data.name.split())
    dup = db.scalar(select(CustomerTier).where(func.lower(CustomerTier.name) == name.lower(), CustomerTier.id != t.id))
    if dup:
        raise HTTPException(400, "Tên hạng đã tồn tại")
    t.name, t.min_spent, t.discount_percent, t.note = name, data.min_spent, data.discount_percent, data.note
    db.add(t)
    db.commit()
    return _tier_out(t)


@router.post("/tiers", status_code=201)
def create_tier(data: TierIn, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    return _save_tier(db, CustomerTier(), data)


@router.put("/tiers/{tier_id}")
def update_tier(tier_id: int, data: TierIn, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    t = db.get(CustomerTier, tier_id)
    if t is None:
        raise HTTPException(404, "Không tìm thấy hạng")
    return _save_tier(db, t, data)


@router.delete("/tiers/{tier_id}")
def delete_tier(tier_id: int, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    t = db.get(CustomerTier, tier_id)
    if t is None:
        raise HTTPException(404, "Không tìm thấy hạng")
    db.delete(t)
    db.commit()
    return {"ok": True}
