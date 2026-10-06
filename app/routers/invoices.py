from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.config import settings
from app.database import get_db
from app.models import Customer, ImportReceipt, Invoice, InvoiceItem, User
from app.schemas import (CancelRejectIn, ImportCancelIn, ImportDraftIn, ImportIn, InvoiceCancelIn, InvoiceEmailIn,
                         InvoiceIn, InvoicePayIn)
from app.security import ALL_STAFF, MANAGERS
from app.services import export, inventory
from app.services.audit import audit
from app.services.inventory import BusinessError
from app.services.mailer import MailError, mail_configured, send_mail
from app.services.qr import qr_svg
from app.services.reports import parse_range

router = APIRouter(prefix="/api", tags=["invoices"])
PAY_VI = {"cash": "Tiền mặt", "transfer": "Chuyển khoản", "card": "Quẹt thẻ", "qr": "Quét mã QR"}


def invoice_out(inv: Invoice, with_items: bool = True) -> dict:
    data = {
        "id": inv.id, "code": inv.code, "customer_id": inv.customer_id,
        "customer_name": inv.customer.name if inv.customer else "Khách lẻ",
        "customer_phone": inv.customer.phone if inv.customer else None,
        "customer_email": inv.customer.email if inv.customer else None,
        "user_id": inv.user_id, "user_name": inv.user.full_name, "created_at": inv.created_at,
        "subtotal": inv.subtotal, "discount": inv.discount, "total": inv.total,
        "tier_discount": inv.tier_discount, "promo_discount": inv.promo_discount,
        "points_used": inv.points_used, "points_discount": inv.points_discount, "points_earned": inv.points_earned,
        "manual_discount": inv.discount - inv.tier_discount - inv.promo_discount - inv.points_discount,
        "promotion_id": inv.promotion_id, "promotion_name": inv.promotion.name if inv.promotion else None,
        "voucher_code": inv.promotion.code if inv.promotion else None,
        "payment_method": inv.payment_method, "cash_received": inv.cash_received,
        "change": inv.cash_received - inv.total if inv.cash_received is not None else None,
        "payment_ref": inv.payment_ref, "status": inv.status, "note": inv.note,
        "cancelled_at": inv.cancelled_at, "cancel_reason": inv.cancel_reason,
        "cancel_requested_at": inv.cancel_requested_at,
        "cancel_requested_by": inv.requester.full_name if inv.requester else None,
    }
    if with_items:
        data["items"] = [{
            "product_id": it.product_id, "product_code": it.product.code, "product_name": it.product.name,
            "image_url": it.product.image_url, "quantity": it.quantity, "unit_price": it.unit_price,
            "line_total": it.line_total, "serials": it.serials or [], "track_serial": it.product.track_serial,
            "warranty_months": it.product.warranty_months,
        } for it in inv.items]
        data["returns"] = [{"id": r.id, "code": r.code, "created_at": r.created_at, "refund_total": r.refund_total}
                           for r in inv.returns]
        data["refunded"] = sum(r.refund_total for r in inv.returns)
        data["code_qr"] = qr_svg(inv.code)  # in trên hóa đơn: quét mã để tra hóa đơn khi đổi trả / bảo hành
    return data


def invoice_query(user: User, q: str | None, status: str | None, date_from: str | None,
                  date_to: str | None, payment_method: str | None, customer_id: int | None,
                  cancel_pending: bool = False):
    stmt = select(Invoice)
    if user.role != "owner":
        stmt = stmt.where(Invoice.user_id == user.id)  # thu ngân chỉ xem hóa đơn mình lập
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.outerjoin(Customer).where(
            or_(Invoice.code.ilike(like), Customer.name.ilike(like), Customer.phone.ilike(like)))
    if status:
        stmt = stmt.where(Invoice.status == status)
    if cancel_pending:
        stmt = stmt.where(Invoice.cancel_requested_at.is_not(None), Invoice.status == "paid")
    if payment_method:
        stmt = stmt.where(Invoice.payment_method == payment_method)
    if customer_id:
        stmt = stmt.where(Invoice.customer_id == customer_id)
    if date_from or date_to:
        start, end = parse_range(date_from, date_to)
        stmt = stmt.where(Invoice.created_at >= start, Invoice.created_at < end)
    return stmt


@router.get("/invoices")
def list_invoices(q: str | None = None, status: str | None = Query(None, pattern="^(pending|paid|cancelled)$"),
                  cancel_pending: bool = False,
                  date_from: str | None = None, date_to: str | None = None,
                  payment_method: str | None = None, customer_id: int | None = None,
                  page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=200),
                  db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    stmt = invoice_query(user, q, status, date_from, date_to, payment_method, customer_id, cancel_pending)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    sum_total = db.scalar(select(func.coalesce(func.sum(Invoice.total), 0)).where(
        Invoice.id.in_(stmt.with_only_columns(Invoice.id).where(Invoice.status == "paid"))))
    stmt = stmt.options(joinedload(Invoice.customer), joinedload(Invoice.user), joinedload(Invoice.promotion),
                        joinedload(Invoice.requester))
    rows = db.scalars(stmt.order_by(Invoice.created_at.desc(), Invoice.id.desc())
                      .offset((page - 1) * size).limit(size)).unique().all()
    return {"total": total, "sum_paid": int(sum_total), "items": [invoice_out(i, False) for i in rows]}


@router.get("/invoices/pending-count")
def pending_counts(db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    """Số việc đang chờ, hiện cạnh menu: hóa đơn tạm (của mình / cả cửa hàng), yêu cầu hủy, phiếu nhập nháp."""
    held = select(func.count(Invoice.id)).where(Invoice.status == "pending")
    if user.role != "owner":
        held = held.where(Invoice.user_id == user.id)
    out = {"held_invoices": db.scalar(held) or 0}
    if user.role == "owner":
        out["cancel_requests"] = db.scalar(select(func.count(Invoice.id)).where(
            Invoice.status == "paid", Invoice.cancel_requested_at.is_not(None))) or 0
        out["draft_imports"] = db.scalar(select(func.count(ImportReceipt.id)).where(
            ImportReceipt.status == "draft")) or 0
    return out


def _get_invoice(db: Session, invoice_id: int, user: User) -> Invoice:
    inv = db.scalar(select(Invoice).options(selectinload(Invoice.items).joinedload(InvoiceItem.product))
                    .where(Invoice.id == invoice_id))
    if inv is None or (user.role != "owner" and inv.user_id != user.id):
        raise HTTPException(404, "Không tìm thấy hóa đơn")
    return inv


def _run(db: Session, fn, *args):
    try:
        result = fn(*args)
        db.commit()
        return result
    except BusinessError as e:
        db.rollback()
        raise HTTPException(400, str(e))


def _staff_limits(data: InvoiceIn, user: User) -> None:
    """Thu ngân không tự đặt giá, không tự giảm giá: chỉ áp dụng khuyến mãi / voucher / hạng / điểm."""
    if user.role == "owner":
        return
    for item in data.items:
        item.unit_price = None  # luôn dùng giá bán niêm yết
    if data.discount or data.discount_percent:
        raise HTTPException(403, "Thu ngân không được tự giảm giá, hãy áp dụng chương trình khuyến mãi hoặc voucher")


@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int, db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    return invoice_out(_get_invoice(db, invoice_id, user))


@router.post("/invoices", status_code=201)
def create_invoice(data: InvoiceIn, db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    _staff_limits(data, user)
    inv = _run(db, inventory.create_invoice, db, data, user)
    return invoice_out(_get_invoice(db, inv.id, user))


@router.put("/invoices/{invoice_id}")
def update_invoice(invoice_id: int, data: InvoiceIn, db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    """Sửa hóa đơn tạm (chưa thanh toán); data.pay=True thì thanh toán luôn sau khi sửa."""
    _staff_limits(data, user)
    inv = _get_invoice(db, invoice_id, user)
    _run(db, inventory.update_invoice, db, inv, data, user)
    db.expire_all()
    return invoice_out(_get_invoice(db, invoice_id, user))


@router.post("/invoices/{invoice_id}/pay")
def pay_invoice(invoice_id: int, data: InvoicePayIn, db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    inv = _get_invoice(db, invoice_id, user)
    _run(db, inventory.pay_invoice, db, inv, data, user)
    db.expire_all()
    return invoice_out(_get_invoice(db, invoice_id, user))


@router.post("/invoices/{invoice_id}/cancel")
def cancel_invoice(invoice_id: int, data: InvoiceCancelIn, db: Session = Depends(get_db),
                   user: User = Depends(ALL_STAFF)):
    """Hủy hóa đơn. Hóa đơn tạm: người lập hoặc chủ cửa hàng hủy ngay.
    Hóa đơn đã thanh toán: chỉ chủ cửa hàng (duyệt luôn yêu cầu hủy nếu có); thu ngân dùng /cancel-request."""
    inv = _get_invoice(db, invoice_id, user)
    if inv.status == "paid" and user.role != "owner":
        raise HTTPException(403, "Hóa đơn đã thanh toán: thu ngân gửi yêu cầu hủy để chủ cửa hàng duyệt")
    was_paid, requested = inv.status == "paid", inv.cancel_requested_at is not None
    inventory_fn = inventory.cancel_invoice
    if was_paid:
        detail = f"{inv.code}: {data.reason}" + (" (duyệt yêu cầu của thu ngân)" if requested else "")
        audit(db, user, "invoice_cancel", detail)
    _run(db, inventory_fn, db, inv, data.reason, user)
    db.expire_all()
    return invoice_out(_get_invoice(db, invoice_id, user))


@router.post("/invoices/{invoice_id}/cancel-request")
def request_cancel(invoice_id: int, data: InvoiceCancelIn, db: Session = Depends(get_db),
                   user: User = Depends(ALL_STAFF)):
    inv = _get_invoice(db, invoice_id, user)
    audit(db, user, "invoice_cancel_request", f"{inv.code}: {data.reason}")
    _run(db, inventory.request_cancel, db, inv, data.reason, user)
    return invoice_out(_get_invoice(db, invoice_id, user))


@router.post("/invoices/{invoice_id}/cancel-reject")
def reject_cancel(invoice_id: int, data: CancelRejectIn, db: Session = Depends(get_db),
                  user: User = Depends(MANAGERS)):
    inv = _get_invoice(db, invoice_id, user)
    audit(db, user, "invoice_cancel_reject", f"{inv.code}" + (f": {data.note}" if data.note else ""))
    _run(db, inventory.reject_cancel, db, inv)
    return invoice_out(_get_invoice(db, invoice_id, user))


def _pdf(inv: dict) -> bytes:
    v = export.vnd
    info = [["Thời gian", inv["created_at"].strftime("%H:%M %d/%m/%Y")], ["Khách hàng", inv["customer_name"]],
            ["Thu ngân", inv["user_name"]], ["Thanh toán", PAY_VI.get(inv["payment_method"], inv["payment_method"])]]
    if inv["payment_ref"]:
        info.append(["Mã giao dịch", inv["payment_ref"]])
    items = [[i["product_name"] + (f" (Serial: {', '.join(i['serials'])})" if i["serials"] else ""),
              i["quantity"], v(i["unit_price"]), v(i["line_total"])] for i in inv["items"]]
    totals = [["Tạm tính", v(inv["subtotal"])]]
    for key, label in (("tier_discount", "Giảm hạng thành viên"), ("promo_discount", "Khuyến mãi / voucher"),
                       ("manual_discount", "Giảm giá"), ("points_discount", f"Dùng {inv['points_used']} điểm")):
        if inv[key]:
            totals.append([label, "-" + v(inv[key])])
    totals.append(["TỔNG CỘNG", v(inv["total"]) + " đ"])
    if inv["cash_received"] is not None:
        totals += [["Khách đưa", v(inv["cash_received"])], ["Tiền thừa", v(inv["change"])]]
    if inv["points_earned"]:
        totals.append(["Điểm tích lũy được cộng", inv["points_earned"]])
    status = {"pending": "CHƯA THANH TOÁN", "cancelled": "ĐÃ HỦY", "paid": ""}[inv["status"]]
    shop = " · ".join(x for x in (settings.SHOP_NAME, settings.SHOP_ADDRESS, settings.SHOP_PHONE) if x)
    return export.to_pdf(f"HÓA ĐƠN BÁN HÀNG {inv['code']}", shop + (f" · {status}" if status else ""), [
        ("Thông tin", ["Mục", "Nội dung"], info, [1, 3]),
        ("Sản phẩm", ["Sản phẩm", "SL", "Đơn giá", "Thành tiền"], items, [5, 0.8, 1.6, 1.8]),
        ("Thanh toán", ["Khoản", "Số tiền"], totals, [3, 1.5]),
    ])


@router.get("/invoices/{invoice_id}/pdf")
def invoice_pdf(invoice_id: int, db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    inv = invoice_out(_get_invoice(db, invoice_id, user))
    return Response(_pdf(inv), media_type=export.MEDIA["pdf"],
                    headers={"Content-Disposition": f'attachment; filename="hoa_don_{inv["code"]}.pdf"'})


@router.post("/invoices/{invoice_id}/email")
def email_invoice(invoice_id: int, data: InvoiceEmailIn, db: Session = Depends(get_db),
                  user: User = Depends(ALL_STAFF)):
    """Gửi hóa đơn (kèm file PDF) tới email khách hàng."""
    inv = invoice_out(_get_invoice(db, invoice_id, user))
    to = data.to or inv["customer_email"]
    if not to:
        raise HTTPException(400, "Khách hàng chưa có email, hãy nhập địa chỉ email nhận hóa đơn")
    if not mail_configured():
        raise HTTPException(503, "Hệ thống chưa cấu hình gửi email (RESEND_API_KEY hoặc SMTP)")
    lines = [f"Cảm ơn quý khách đã mua hàng tại {settings.SHOP_NAME}!", "",
             f"Hóa đơn {inv['code']} - {inv['created_at']:%H:%M %d/%m/%Y}", ""]
    lines += [f"- {i['product_name']} x{i['quantity']}: {export.vnd(i['line_total'])} đ" for i in inv["items"]]
    lines += ["", f"Giảm giá: {export.vnd(inv['discount'])} đ", f"Tổng cộng: {export.vnd(inv['total'])} đ",
              "", "Hóa đơn chi tiết đính kèm file PDF."]
    try:
        send_mail(to, f"[{settings.SHOP_NAME}] Hóa đơn {inv['code']}", "\n".join(lines),
                  attachments=[(f"hoa_don_{inv['code']}.pdf", _pdf(inv), "application/pdf")])
    except MailError as e:
        raise HTTPException(502, f"Không gửi được email: {e}")
    return {"ok": True, "message": f"Đã gửi hóa đơn tới {to}"}


# ---------------- Phiếu nhập ----------------
def import_out(r: ImportReceipt, user: User, with_items: bool = True) -> dict:
    # Thu ngân không xem giá nhập, trừ phiếu nháp do chính mình ghi (giá theo phiếu giao hàng)
    show_cost = user.role == "owner" or (r.status == "draft" and r.user_id == user.id)
    data = {"id": r.id, "code": r.code, "status": r.status, "supplier_id": r.supplier_id, "supplier": r.supplier,
            "note": r.note, "total": r.total if show_cost else None, "created_at": r.created_at,
            "user_id": r.user_id, "user_name": r.user.full_name, "item_count": len(r.items),
            "confirmed_at": r.confirmed_at, "confirmed_by": r.confirmer.full_name if r.confirmer else None,
            "cancelled_at": r.cancelled_at, "cancel_reason": r.cancel_reason}
    if with_items:
        data["items"] = [{"product_id": it.product_id, "product_code": it.product.code,
                          "product_name": it.product.name, "image_url": it.product.image_url,
                          "track_serial": it.product.track_serial, "quantity": it.quantity,
                          "unit_cost": it.unit_cost if show_cost else None,
                          "line_total": it.line_total if show_cost else None, "serials": it.serials or []}
                         for it in r.items]
    return data


def _get_import(db: Session, receipt_id: int, user: User) -> ImportReceipt:
    r = db.get(ImportReceipt, receipt_id)
    if r is None or (user.role != "owner" and r.user_id != user.id):
        raise HTTPException(404, "Không tìm thấy phiếu nhập")
    return r


@router.get("/imports")
def list_imports(date_from: str | None = None, date_to: str | None = None, q: str | None = None,
                 status: str | None = Query(None, pattern="^(draft|completed|cancelled)$"),
                 page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=200),
                 db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    stmt = select(ImportReceipt).options(joinedload(ImportReceipt.user), joinedload(ImportReceipt.confirmer),
                                         selectinload(ImportReceipt.items))
    if user.role != "owner":
        stmt = stmt.where(ImportReceipt.user_id == user.id)  # thu ngân chỉ xem phiếu nháp mình lập
    if status:
        stmt = stmt.where(ImportReceipt.status == status)
    if date_from or date_to:
        start, end = parse_range(date_from, date_to)
        stmt = stmt.where(ImportReceipt.created_at >= start, ImportReceipt.created_at < end)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(ImportReceipt.code.ilike(like), ImportReceipt.supplier.ilike(like)))
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(ImportReceipt.created_at.desc(), ImportReceipt.id.desc())
                      .offset((page - 1) * size).limit(size)).unique().all()
    return {"total": total, "items": [import_out(r, user, False) for r in rows]}


@router.get("/imports/{receipt_id}")
def get_import(receipt_id: int, db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    return import_out(_get_import(db, receipt_id, user), user)


@router.post("/imports", status_code=201)
def create_import(data: ImportIn, db: Session = Depends(get_db), user: User = Depends(MANAGERS)):
    """Chủ cửa hàng lập phiếu nhập: cộng kho ngay."""
    r = _run(db, inventory.create_import, db, data, user)
    return import_out(r, user)


@router.post("/imports/drafts", status_code=201)
def create_import_draft(data: ImportDraftIn, db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    """Phiếu nhập nháp (thu ngân ghi nhận hàng về): chưa cộng kho, chờ chủ cửa hàng xác nhận."""
    r = _run(db, inventory.create_import_draft, db, data, user)
    return import_out(r, user)


@router.put("/imports/{receipt_id}")
def update_import_draft(receipt_id: int, data: ImportDraftIn, db: Session = Depends(get_db),
                        user: User = Depends(ALL_STAFF)):
    r = _get_import(db, receipt_id, user)
    _run(db, inventory.update_import_draft, db, r, data)
    return import_out(r, user)


@router.post("/imports/{receipt_id}/confirm")
def confirm_import(receipt_id: int, data: ImportIn, db: Session = Depends(get_db), user: User = Depends(MANAGERS)):
    r = _get_import(db, receipt_id, user)
    audit(db, user, "import_confirm", f"{r.code} (lập bởi {r.user.full_name})")
    _run(db, inventory.confirm_import, db, r, data, user)
    return import_out(r, user)


@router.post("/imports/{receipt_id}/cancel")
def cancel_import(receipt_id: int, data: ImportCancelIn, db: Session = Depends(get_db),
                  user: User = Depends(ALL_STAFF)):
    """Hủy phiếu nhập: phiếu nháp thì người lập hoặc chủ cửa hàng hủy; phiếu đã nhập kho chỉ chủ cửa hàng (trừ lại kho)."""
    r = _get_import(db, receipt_id, user)
    if r.status != "draft" and user.role != "owner":
        raise HTTPException(403, "Chỉ chủ cửa hàng hủy được phiếu đã nhập kho")
    if r.status == "completed":
        audit(db, user, "import_cancel", f"{r.code}: {data.reason}")
    _run(db, inventory.cancel_import, db, r, data.reason, user)
    return import_out(r, user)
