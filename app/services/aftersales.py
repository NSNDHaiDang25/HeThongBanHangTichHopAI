"""Hậu mãi: đổi trả hàng và bảo hành (thu ngân và chủ cửa hàng đều làm được).

Đổi trả: chỉ nhận trong RETURN_HOURS giờ kể từ lúc thanh toán (tham số kinh doanh). Tiền hoàn của mỗi dòng
chia theo tỉ lệ giảm giá của hóa đơn; trả hết hàng thì hoàn đúng số tiền khách đã trả. Hàng còn tốt nhập lại kho,
hàng lỗi không nhập lại (serial chuyển sang "lỗi"). Điểm đã tích của phần hàng trả bị trừ lại.
"Đổi hàng" = làm phiếu trả rồi lập hóa đơn mới cho món khách lấy.

Bảo hành: hạn bảo hành = ngày mua + số tháng bảo hành của sản phẩm. Tra theo mã hóa đơn hoặc serial / IMEI.
"""
import calendar
from collections import defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.models import (Customer, Invoice, InvoiceItem, Product, ProductSerial, ReturnItem, ReturnReceipt,
                        User, WarrantyTicket, now)
from app.schemas import ReturnIn, WarrantyIn, WarrantyUpdate
from app.services import loyalty
from app.services.inventory import BusinessError, _lock_products, _release_serials, change_stock, next_code

WARRANTY_STATUS = {"received": "Đã tiếp nhận", "processing": "Đang xử lý", "done": "Đã trả khách",
                   "rejected": "Từ chối bảo hành"}


def add_months(d: date, months: int) -> date:
    m = d.month - 1 + months
    y, m = d.year + m // 12, m % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def warranty_until(invoice: Invoice, product: Product) -> date | None:
    if not product.warranty_months:
        return None
    return add_months(invoice.created_at.date(), product.warranty_months)


def return_deadline(invoice: Invoice) -> datetime:
    return invoice.created_at + timedelta(hours=settings.RETURN_HOURS)


def find_invoice(db: Session, code: str) -> Invoice:
    inv = db.scalar(select(Invoice).options(selectinload(Invoice.items).selectinload(InvoiceItem.product),
                                            selectinload(Invoice.returns).selectinload(ReturnReceipt.items))
                    .where(func.upper(Invoice.code) == code.strip().upper()))
    if inv is None:
        raise BusinessError(f"Không tìm thấy hóa đơn '{code.strip()}'")
    return inv


def _returned(inv: Invoice) -> tuple[dict[int, int], set[str]]:
    qty: dict[int, int] = defaultdict(int)
    serials: set[str] = set()
    for r in inv.returns:
        for it in r.items:
            qty[it.product_id] += it.quantity
            serials |= set(it.serials or [])
    return qty, serials


def invoice_lookup(db: Session, inv: Invoice) -> dict:
    """Thông tin hóa đơn cho màn hình đổi trả / bảo hành: còn trả được bao nhiêu, còn bảo hành tới khi nào.
    Không có giá vốn: thu ngân dùng được."""
    returned_qty, returned_serials = _returned(inv)
    deadline = return_deadline(inv)
    t = now()
    can_return = inv.status == "paid" and not inv.cancel_requested_at and settings.RETURN_HOURS > 0 and t <= deadline
    why = None
    if inv.status != "paid":
        why = "Hóa đơn chưa thanh toán hoặc đã hủy"
    elif inv.cancel_requested_at:
        why = "Hóa đơn đang chờ duyệt hủy"
    elif settings.RETURN_HOURS <= 0:
        why = "Cửa hàng không nhận đổi trả"
    elif t > deadline:
        why = f"Đã quá thời hạn đổi trả {settings.RETURN_HOURS} giờ (hạn chót {deadline:%H:%M %d/%m/%Y})"
    ratio = inv.total / inv.subtotal if inv.subtotal else 0
    items = []
    for it in inv.items:
        p = it.product
        until = warranty_until(inv, p) if inv.status == "paid" else None
        items.append({
            "product_id": p.id, "product_code": p.code, "product_name": p.name, "image_url": p.image_url,
            "quantity": it.quantity, "unit_price": it.unit_price, "line_total": it.line_total,
            "returned": returned_qty[p.id], "returnable": max(0, it.quantity - returned_qty[p.id]),
            "unit_refund": round(it.unit_price * ratio), "track_serial": p.track_serial,
            "serials": it.serials or [], "returnable_serials": [s for s in it.serials or [] if s not in returned_serials],
            "warranty_months": p.warranty_months, "warranty_until": until,
            "in_warranty": bool(until and t.date() <= until),
        })
    return {
        "id": inv.id, "code": inv.code, "status": inv.status, "created_at": inv.created_at,
        "customer_id": inv.customer_id, "customer_name": inv.customer.name if inv.customer else "Khách lẻ",
        "customer_phone": inv.customer.phone if inv.customer else None,
        "subtotal": inv.subtotal, "discount": inv.discount, "total": inv.total,
        "refunded": sum(r.refund_total for r in inv.returns),
        "return_deadline": deadline, "can_return": can_return, "cannot_return_reason": why,
        "return_hours": settings.RETURN_HOURS, "items": items,
        "returns": [{"id": r.id, "code": r.code, "created_at": r.created_at, "refund_total": r.refund_total}
                    for r in inv.returns],
    }


def create_return(db: Session, data: ReturnIn, user: User) -> ReturnReceipt:
    inv = db.get(Invoice, data.invoice_id)
    if inv is None:
        raise BusinessError("Không tìm thấy hóa đơn")
    info = invoice_lookup(db, inv)
    if not info["can_return"]:
        raise BusinessError(info["cannot_return_reason"])
    by_product = {it["product_id"]: it for it in info["items"]}
    sold_items = {it.product_id: it for it in inv.items}
    at = now()
    receipt = ReturnReceipt(code=next_code(db, ReturnReceipt, "TH", at), invoice_id=inv.id, user_id=user.id,
                            created_at=at, reason=data.reason, note=data.note)
    db.add(receipt)
    products = _lock_products(db, [i.product_id for i in data.items])
    seen: set[int] = set()
    ratio = inv.total / inv.subtotal if inv.subtotal else 0
    refund = 0
    for item in data.items:
        line = by_product.get(item.product_id)
        if line is None:
            raise BusinessError("Sản phẩm không có trong hóa đơn")
        if item.product_id in seen:
            raise BusinessError(f"'{line['product_name']}' bị lặp, gộp thành một dòng")
        seen.add(item.product_id)
        if item.quantity > line["returnable"]:
            raise BusinessError(f"'{line['product_name']}' chỉ còn trả được {line['returnable']}")
        product = products[item.product_id]
        serials = []
        if line["serials"]:  # hàng bán theo serial: chỉ đúng các máy đã bán trong hóa đơn
            serials = item.serials or []
            if len(serials) != item.quantity or not set(serials) <= set(line["returnable_serials"]):
                raise BusinessError(f"'{product.name}': chọn đúng {item.quantity} serial / IMEI đã bán trong hóa đơn")
        sold = sold_items[item.product_id]
        line_refund = round(sold.unit_price * item.quantity * ratio)
        refund += line_refund
        if item.restock:
            change_stock(db, product, item.quantity, "return", receipt.code, user, note=data.reason, at=at)
        if serials:
            _release_serials(db, serials, "in_stock" if item.restock else "defective")
        receipt.items.append(ReturnItem(product_id=product.id, quantity=item.quantity, unit_price=sold.unit_price,
                                        unit_cost=sold.unit_cost, refund=line_refund, restock=item.restock,
                                        serials=serials or None))
    previous = info["refunded"]
    all_back = all(by_product[pid]["returnable"] == next((i.quantity for i in data.items if i.product_id == pid), 0)
                   for pid in by_product)
    if all_back or previous + refund > inv.total:
        refund = inv.total - previous  # trả hết hàng: hoàn đúng số tiền khách đã trả, không lệch do làm tròn
    receipt.refund_total = refund
    customer = db.get(Customer, inv.customer_id) if inv.customer_id else None
    if customer is not None and inv.points_earned:
        earlier = sum(r.points_reverted for r in inv.returns if r.id != receipt.id)
        share = inv.points_earned - earlier if all_back else round(inv.points_earned * refund / inv.total) if inv.total else 0
        receipt.points_reverted = loyalty.change_points(db, customer, -max(0, share), "revert", receipt.code, user,
                                                        "Trả hàng: trừ điểm đã tích", clamp=True) * -1
    db.flush()
    return receipt


def return_out(r: ReturnReceipt) -> dict:
    inv = r.invoice
    return {
        "id": r.id, "code": r.code, "created_at": r.created_at, "invoice_id": inv.id, "invoice_code": inv.code,
        "customer_name": inv.customer.name if inv.customer else "Khách lẻ", "user_name": r.user.full_name,
        "reason": r.reason, "note": r.note, "refund_total": r.refund_total, "points_reverted": r.points_reverted,
        "items": [{"product_id": it.product_id, "product_code": it.product.code, "product_name": it.product.name,
                   "image_url": it.product.image_url, "quantity": it.quantity, "unit_price": it.unit_price,
                   "refund": it.refund, "restock": it.restock, "serials": it.serials or []} for it in r.items],
    }


# ================================================================ Bảo hành
def serial_lookup(db: Session, serial: str) -> dict:
    r = db.scalar(select(ProductSerial).where(func.upper(ProductSerial.serial) == serial.strip().upper()))
    if r is None:
        raise BusinessError(f"Không tìm thấy serial / IMEI '{serial.strip()}'")
    p = r.product
    out = {"serial": r.serial, "status": r.status, "product_id": p.id, "product_code": p.code,
           "product_name": p.name, "warranty_months": p.warranty_months, "invoice_id": None, "invoice_code": None,
           "sold_at": r.sold_at, "warranty_until": None, "in_warranty": False, "customer_name": None}
    inv = r.invoice
    if inv is not None and inv.status == "paid" and r.status == "sold":
        until = warranty_until(inv, p)
        out.update(invoice_id=inv.id, invoice_code=inv.code, warranty_until=until,
                   in_warranty=bool(until and now().date() <= until),
                   customer_name=inv.customer.name if inv.customer else "Khách lẻ")
    return out


def create_ticket(db: Session, data: WarrantyIn, user: User) -> WarrantyTicket:
    product = db.get(Product, data.product_id)
    if product is None:
        raise BusinessError("Không tìm thấy sản phẩm")
    serial = (data.serial or "").strip().upper() or None
    inv = db.get(Invoice, data.invoice_id) if data.invoice_id else None
    if data.invoice_id and inv is None:
        raise BusinessError("Không tìm thấy hóa đơn")
    if inv is None and serial:  # khách chỉ có máy: tìm hóa đơn theo serial
        found = db.scalar(select(ProductSerial).where(ProductSerial.serial == serial))
        if found and found.status == "sold" and found.product_id == product.id:
            inv = found.invoice
    until = None
    if inv is not None:
        if inv.status != "paid":
            raise BusinessError("Hóa đơn chưa thanh toán hoặc đã hủy")
        item = next((it for it in inv.items if it.product_id == product.id), None)
        if item is None:
            raise BusinessError(f"Hóa đơn {inv.code} không có sản phẩm '{product.name}'")
        if serial and item.serials and serial not in item.serials:
            raise BusinessError(f"Serial / IMEI '{serial}' không thuộc hóa đơn {inv.code}")
        until = warranty_until(inv, product)
    name = (data.customer_name or "").strip() or ((inv.customer.name if inv.customer else "Khách lẻ") if inv else "")
    if not name:
        raise BusinessError("Khách không có hóa đơn: nhập tên khách hàng")
    phone = (data.customer_phone or "").strip() or (inv.customer.phone if inv and inv.customer else None)
    at = now()
    t = WarrantyTicket(code=next_code(db, WarrantyTicket, "BH", at), invoice_id=inv.id if inv else None,
                       product_id=product.id, customer_name=name, customer_phone=phone, serial=serial,
                       issue=data.issue.strip(), warranty_until=until, in_warranty=bool(until and at.date() <= until),
                       status="received", user_id=user.id, created_at=at, updated_at=at,
                       history=[{"time": at.isoformat(), "status": "received", "user": user.full_name,
                                 "note": "Tiếp nhận: " + data.issue.strip()}])
    db.add(t)
    db.flush()
    return t


def update_ticket(db: Session, t: WarrantyTicket, data: WarrantyUpdate, user: User) -> WarrantyTicket:
    if t.status in ("done", "rejected"):
        raise BusinessError("Phiếu bảo hành đã đóng, không cập nhật được")
    if data.status == t.status and not (data.note or "").strip():
        raise BusinessError("Nhập nội dung tiến độ hoặc đổi trạng thái")
    at = now()
    t.status = data.status
    if data.note:
        t.result = data.note.strip()
    t.updated_at = at
    if data.status in ("done", "rejected"):
        t.completed_at = at
    t.history = [*(t.history or []), {"time": at.isoformat(), "status": data.status, "user": user.full_name,
                                      "note": (data.note or "").strip() or None}]
    db.flush()
    return t


def ticket_out(t: WarrantyTicket) -> dict:
    return {
        "id": t.id, "code": t.code, "created_at": t.created_at, "updated_at": t.updated_at,
        "completed_at": t.completed_at, "status": t.status, "status_label": WARRANTY_STATUS.get(t.status, t.status),
        "invoice_id": t.invoice_id, "invoice_code": t.invoice.code if t.invoice else None,
        "product_id": t.product_id, "product_code": t.product.code, "product_name": t.product.name,
        "image_url": t.product.image_url, "customer_name": t.customer_name, "customer_phone": t.customer_phone,
        "serial": t.serial, "issue": t.issue, "result": t.result, "warranty_until": t.warranty_until,
        "in_warranty": t.in_warranty, "user_name": t.user.full_name, "history": t.history or [],
    }
