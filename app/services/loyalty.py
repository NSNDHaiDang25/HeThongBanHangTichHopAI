"""Khách hàng thân thiết: hạng thành viên theo tổng chi tiêu và điểm tích lũy.

- Tổng chi tiêu = tổng tiền hóa đơn đã thanh toán trừ tiền đã hoàn khi trả hàng.
- Hạng = hạng cao nhất có "chi tiêu tối thiểu" <= tổng chi tiêu; hạng cho giảm giá tự động khi mua.
- Điểm: thanh toán mỗi POINTS_EARN_AMOUNT ₫ được 1 điểm; dùng điểm trừ tiền POINT_VALUE ₫ / điểm.
Mọi thay đổi điểm ghi vào point_transactions để tra lại được. Các hàm ở đây không commit.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Customer, CustomerTier, Invoice, PointTransaction, ReturnReceipt, User, now

POINT_TYPES = {"earn": "Tích điểm", "redeem": "Dùng điểm", "revert": "Hoàn / trừ điểm", "adjust": "Điều chỉnh"}


class PointsError(Exception):
    pass


def spent_by(db: Session, customer_ids: list[int]) -> dict[int, int]:
    """Tổng chi tiêu thực (đã trừ tiền hoàn trả hàng) của nhiều khách một lần."""
    if not customer_ids:
        return {}
    paid = dict(db.execute(select(Invoice.customer_id, func.sum(Invoice.total))
                           .where(Invoice.status == "paid", Invoice.customer_id.in_(customer_ids))
                           .group_by(Invoice.customer_id)).all())
    refunds = dict(db.execute(select(Invoice.customer_id, func.sum(ReturnReceipt.refund_total))
                              .join(Invoice, ReturnReceipt.invoice_id == Invoice.id)
                              .where(Invoice.status == "paid", Invoice.customer_id.in_(customer_ids))
                              .group_by(Invoice.customer_id)).all())
    return {cid: int(paid.get(cid) or 0) - int(refunds.get(cid) or 0) for cid in customer_ids}


def all_tiers(db: Session) -> list[CustomerTier]:
    return list(db.scalars(select(CustomerTier).order_by(CustomerTier.min_spent, CustomerTier.id)))


def tier_for(tiers: list[CustomerTier], spent: int) -> CustomerTier | None:
    reached = [t for t in tiers if t.min_spent <= spent]
    return reached[-1] if reached else None


def customer_tier(db: Session, customer: Customer | None) -> CustomerTier | None:
    if customer is None:
        return None
    return tier_for(all_tiers(db), spent_by(db, [customer.id])[customer.id])


def tier_dict(t: CustomerTier | None) -> dict | None:
    return {"id": t.id, "name": t.name, "discount_percent": t.discount_percent} if t else None


def earn_for(total: int) -> int:
    rate = settings.POINTS_EARN_AMOUNT
    return total // rate if rate > 0 and total > 0 else 0


def change_points(db: Session, customer: Customer, delta: int, type_: str, ref: str | None, user: User | None,
                  note: str | None = None, clamp: bool = False) -> int:
    """Cộng / trừ điểm, ghi lịch sử. clamp=True: trừ tối đa bằng số điểm đang có (khi hoàn điểm đã tích)."""
    if clamp and customer.points + delta < 0:
        delta = -customer.points
    if delta == 0:
        return 0
    if customer.points + delta < 0:
        raise PointsError(f"Khách hàng chỉ còn {customer.points} điểm")
    customer.points += delta
    db.add(PointTransaction(customer_id=customer.id, change=delta, balance_after=customer.points, type=type_,
                            ref_code=ref, note=note, user_id=user.id if user else None, created_at=now()))
    return delta
