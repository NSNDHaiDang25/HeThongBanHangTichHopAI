"""Khuyến mãi, voucher (chủ cửa hàng quản lý; thu ngân xem chương trình đang chạy để áp dụng khi bán)
và nhà cung cấp (chủ cửa hàng quản lý; thu ngân xem danh sách để lập phiếu nhập nháp)."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ImportReceipt, Invoice, Promotion, Supplier, User, now
from app.schemas import PromotionIn, PromotionOut, SupplierIn, SupplierOut
from app.security import ALL_STAFF, MANAGERS
from app.services.inventory import promotion_discount, promotion_usage

router = APIRouter(prefix="/api", tags=["promotions"])


def promo_out(db: Session, p: Promotion) -> dict:
    today = now().date()
    used = promotion_usage(db, p.id)
    running = p.is_active and p.start_date <= today <= p.end_date and not (p.usage_limit and used >= p.usage_limit)
    return {**PromotionOut.model_validate(p).model_dump(), "used_count": used, "running": running,
            "state": "Đang chạy" if running else "Tạm dừng" if not p.is_active else
            "Chưa bắt đầu" if today < p.start_date else "Hết lượt" if p.usage_limit and used >= p.usage_limit else "Đã kết thúc"}


@router.get("/promotions")
def list_promotions(q: str | None = None, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    stmt = select(Promotion)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Promotion.name.ilike(like), Promotion.code.ilike(like)))
    return [promo_out(db, p) for p in db.scalars(stmt.order_by(Promotion.end_date.desc(), Promotion.id.desc()))]


@router.get("/promotions/active")
def active_promotions(db: Session = Depends(get_db), _: User = Depends(ALL_STAFF)):
    """Chương trình không cần mã đang chạy hôm nay: thu ngân chọn trong danh sách khi bán. Voucher phải nhập mã."""
    today = now().date()
    rows = db.scalars(select(Promotion).where(Promotion.is_active.is_(True), Promotion.code.is_(None),
                                              Promotion.start_date <= today, Promotion.end_date >= today)
                      .order_by(Promotion.min_subtotal, Promotion.id))
    return [p for p in (promo_out(db, x) for x in rows) if p["running"]]


@router.get("/promotions/voucher/{code}")
def check_voucher(code: str, subtotal: int = Query(0, ge=0), db: Session = Depends(get_db),
                  _: User = Depends(ALL_STAFF)):
    """Kiểm tra mã voucher khách đưa: còn hạn, còn lượt, đơn đủ điều kiện chưa và được giảm bao nhiêu."""
    p = db.scalar(select(Promotion).where(func.upper(Promotion.code) == code.strip().upper()))
    if p is None:
        raise HTTPException(404, f"Mã voucher '{code.strip().upper()}' không tồn tại")
    out = promo_out(db, p)
    if not out["running"]:
        raise HTTPException(400, f"Voucher '{p.code}' không dùng được: {out['state'].lower()}")
    out["eligible"] = subtotal >= p.min_subtotal
    out["discount"] = promotion_discount(p, subtotal) if out["eligible"] else 0
    return out


def _save_promotion(db: Session, p: Promotion, data: PromotionIn) -> dict:
    for k, v in data.model_dump().items():
        setattr(p, k, v)
    p.name = " ".join(p.name.split())
    db.add(p)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, f"Mã voucher '{data.code}' đã được dùng cho chương trình khác")
    return promo_out(db, p)


@router.post("/promotions", status_code=201)
def create_promotion(data: PromotionIn, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    return _save_promotion(db, Promotion(), data)


@router.put("/promotions/{promotion_id}")
def update_promotion(promotion_id: int, data: PromotionIn, db: Session = Depends(get_db),
                     _: User = Depends(MANAGERS)):
    p = db.get(Promotion, promotion_id)
    if p is None:
        raise HTTPException(404, "Không tìm thấy chương trình khuyến mãi")
    return _save_promotion(db, p, data)


@router.delete("/promotions/{promotion_id}")
def delete_promotion(promotion_id: int, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    p = db.get(Promotion, promotion_id)
    if p is None:
        raise HTTPException(404, "Không tìm thấy chương trình khuyến mãi")
    if db.scalar(select(func.count(Invoice.id)).where(Invoice.promotion_id == p.id)):
        p.is_active = False  # đã áp dụng cho hóa đơn: chỉ tạm dừng để giữ lịch sử
        db.commit()
        return {"ok": True, "message": "Chương trình đã áp dụng cho hóa đơn nên chuyển sang tạm dừng"}
    db.delete(p)
    db.commit()
    return {"ok": True, "message": "Đã xóa chương trình khuyến mãi"}


# ---------------- Nhà cung cấp ----------------
def supplier_out(db: Session, s: Supplier, with_stats: bool = False) -> dict:
    data = SupplierOut.model_validate(s).model_dump()
    if with_stats:
        n, last = db.execute(select(func.count(ImportReceipt.id), func.max(ImportReceipt.created_at))
                             .where(ImportReceipt.supplier_id == s.id, ImportReceipt.status == "completed")).one()
        data.update(import_count=n, last_import=last)
    return data


@router.get("/suppliers")
def list_suppliers(q: str | None = None, active_only: bool = False, db: Session = Depends(get_db),
                   user: User = Depends(ALL_STAFF)):
    stmt = select(Supplier)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Supplier.name.ilike(like), Supplier.code.ilike(like), Supplier.phone.ilike(like)))
    if active_only or user.role != "owner":
        stmt = stmt.where(Supplier.is_active.is_(True))
    return [supplier_out(db, s, user.role == "owner") for s in db.scalars(stmt.order_by(Supplier.name))]


def _save_supplier(db: Session, s: Supplier, data: SupplierIn) -> dict:
    for k, v in data.model_dump().items():
        setattr(s, k, v)
    if not s.code:
        last = db.scalar(select(func.max(Supplier.id))) or 0
        s.code = f"NCC{last + 1:03d}"
    db.add(s)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, "Tên nhà cung cấp đã tồn tại")
    return supplier_out(db, s, True)


@router.post("/suppliers", status_code=201)
def create_supplier(data: SupplierIn, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    return _save_supplier(db, Supplier(), data)


@router.put("/suppliers/{supplier_id}")
def update_supplier(supplier_id: int, data: SupplierIn, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    s = db.get(Supplier, supplier_id)
    if s is None:
        raise HTTPException(404, "Không tìm thấy nhà cung cấp")
    return _save_supplier(db, s, data)


@router.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    s = db.get(Supplier, supplier_id)
    if s is None:
        raise HTTPException(404, "Không tìm thấy nhà cung cấp")
    if db.scalar(select(func.count(ImportReceipt.id)).where(ImportReceipt.supplier_id == s.id)):
        s.is_active = False
        db.commit()
        return {"ok": True, "message": "Nhà cung cấp đã có phiếu nhập nên chuyển sang ngừng giao dịch"}
    db.delete(s)
    db.commit()
    return {"ok": True, "message": "Đã xóa nhà cung cấp"}
