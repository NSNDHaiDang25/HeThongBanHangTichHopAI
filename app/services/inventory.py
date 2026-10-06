"""Nghiệp vụ tồn kho, hóa đơn và phiếu nhập.

Mọi thay đổi tồn kho đi qua `change_stock` để luôn có nhật ký StockMovement (thẻ kho) và
không bao giờ để tồn kho âm. Các hàm ở đây KHÔNG commit; router gọi commit sau khi
toàn bộ nghiệp vụ thành công (một giao dịch duy nhất).

Vòng đời hóa đơn: pending (hóa đơn tạm: chưa thanh toán, chưa trừ kho, còn sửa được)
-> paid (đã thanh toán: trừ kho, tích / dùng điểm; không sửa được nữa) -> cancelled (hoàn kho, hoàn điểm).
Hủy hóa đơn đã thanh toán: thu ngân gửi yêu cầu, chủ cửa hàng duyệt.
"""
from collections import defaultdict
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import (
    Category, Customer, ImportItem, ImportReceipt, Invoice, InvoiceItem, Product, ProductSerial, Promotion,
    StockMovement, Supplier, User, now,
)
from app.schemas import ImportDraftIn, ImportIn, InvoiceIn, InvoicePayIn, NewProductIn
from app.services import loyalty


class BusinessError(Exception):
    """Lỗi nghiệp vụ, router chuyển thành HTTP 400."""


def change_stock(db: Session, product: Product, delta: int, type_: str, ref: str | None,
                 user: User | None, note: str | None = None, at: datetime | None = None) -> None:
    new_stock = product.stock + delta
    if new_stock < 0:
        raise BusinessError(
            f"Sản phẩm '{product.name}' không đủ tồn kho (còn {product.stock}, cần {-delta})"
        )
    product.stock = new_stock
    db.add(StockMovement(
        product_id=product.id, change=delta, stock_after=new_stock, type=type_, ref_code=ref,
        user_id=user.id if user else None, note=note, created_at=at or now(),
    ))


def next_code(db: Session, model, prefix: str, at: datetime) -> str:
    """Mã chứng từ theo ngày: HD2609230001, PN..., TH..., BH..."""
    day = at.strftime("%y%m%d")
    base = f"{prefix}{day}"
    count = db.scalar(select(func.count()).select_from(model).where(model.code.like(f"{base}%"))) or 0
    return f"{base}{count + 1:04d}"


_next_code = next_code  # tên cũ


def _lock_products(db: Session, product_ids) -> dict[int, Product]:
    products = db.scalars(select(Product).where(Product.id.in_(set(product_ids))).with_for_update()).all()
    found = {p.id: p for p in products}
    missing = set(product_ids) - found.keys()
    if missing:
        raise BusinessError(f"Không tìm thấy sản phẩm id {sorted(missing)}")
    return found


# ================================================================ Serial / IMEI
def add_serials(db: Session, product: Product, serials: list[str], import_id: int | None = None,
                note: str | None = None) -> None:
    exists = set(db.scalars(select(ProductSerial.serial).where(ProductSerial.serial.in_(serials))))
    if exists:
        raise BusinessError(f"Serial / IMEI đã có trong hệ thống: {', '.join(sorted(exists))}")
    for s in serials:
        db.add(ProductSerial(product_id=product.id, serial=s, status="in_stock", import_id=import_id, note=note))
    db.flush()


def _check_serial_count(product: Product, serials: list[str] | None, qty: int, action: str) -> list[str]:
    serials = serials or []
    if product.track_serial and len(serials) != qty:
        raise BusinessError(f"Sản phẩm '{product.name}' quản lý theo serial / IMEI: cần {action} đủ {qty} serial "
                            f"(đang có {len(serials)})")
    return serials if product.track_serial else []


def _sell_serials(db: Session, product: Product, serials: list[str], invoice: Invoice, at: datetime) -> None:
    rows = {r.serial: r for r in db.scalars(select(ProductSerial).where(ProductSerial.serial.in_(serials)))}
    for s in serials:
        r = rows.get(s)
        if r is None or r.product_id != product.id:
            raise BusinessError(f"Serial / IMEI '{s}' không thuộc sản phẩm '{product.name}'")
        if r.status != "in_stock":
            raise BusinessError(f"Serial / IMEI '{s}' không còn trong kho")
        r.status, r.invoice_id, r.sold_at = "sold", invoice.id, at


def _release_serials(db: Session, serials: list[str], status: str = "in_stock") -> None:
    for r in db.scalars(select(ProductSerial).where(ProductSerial.serial.in_(serials))):
        r.status = status
        if status == "in_stock":
            r.invoice_id, r.sold_at = None, None


# ================================================================ Hóa đơn: tính tiền
def _compute_discount(subtotal: int, data: InvoiceIn) -> int:
    """Giảm giá tự nhập (₫ hoặc %) của chủ cửa hàng."""
    discount = data.discount
    if data.discount_percent is not None:
        discount = int(subtotal * data.discount_percent / 100 + 0.5)  # làm tròn nửa lên, khớp với giao diện
    if discount > subtotal:
        raise BusinessError("Giảm giá không được lớn hơn tổng tiền hàng")
    return discount


def promotion_discount(p: Promotion, subtotal: int) -> int:
    if p.discount_type == "percent":
        d = int(subtotal * p.value / 100 + 0.5)
        if p.max_discount:
            d = min(d, p.max_discount)
    else:
        d = p.value
    return min(d, subtotal)


def promotion_usage(db: Session, promotion_id: int, exclude_invoice: int | None = None) -> int:
    stmt = select(func.count(Invoice.id)).where(Invoice.promotion_id == promotion_id, Invoice.status == "paid")
    if exclude_invoice:
        stmt = stmt.where(Invoice.id != exclude_invoice)
    return db.scalar(stmt) or 0


def _resolve_promotion(db: Session, data: InvoiceIn, keep_id: int | None) -> Promotion | None:
    if data.promotion_id and data.voucher_code:
        raise BusinessError("Mỗi hóa đơn chỉ áp dụng một chương trình khuyến mãi hoặc một voucher")
    if data.voucher_code:
        code = data.voucher_code.strip().upper()
        p = db.scalar(select(Promotion).where(func.upper(Promotion.code) == code))
        if p is None:
            raise BusinessError(f"Mã voucher '{code}' không tồn tại")
        return p
    if data.promotion_id:
        p = db.get(Promotion, data.promotion_id)
        if p is None:
            raise BusinessError("Chương trình khuyến mãi không tồn tại")
        if p.code and p.id != keep_id:
            raise BusinessError(f"Chương trình '{p.name}' là voucher: hãy nhập mã voucher khách đưa")
        return p
    return None


def check_promotion(db: Session, p: Promotion, subtotal: int, at: datetime, invoice_id: int | None = None) -> None:
    if not p.is_active:
        raise BusinessError(f"Chương trình '{p.name}' đã ngừng áp dụng")
    if not (p.start_date <= at.date() <= p.end_date):
        raise BusinessError(f"Chương trình '{p.name}' chỉ áp dụng từ {p.start_date:%d/%m/%Y} đến {p.end_date:%d/%m/%Y}")
    if subtotal < p.min_subtotal:
        raise BusinessError(f"Chương trình '{p.name}' áp dụng cho đơn từ {p.min_subtotal:,} ₫".replace(",", "."))
    if p.usage_limit and promotion_usage(db, p.id, invoice_id) >= p.usage_limit:
        raise BusinessError(f"Voucher '{p.code or p.name}' đã hết lượt sử dụng")


def _apply_amounts(db: Session, invoice: Invoice, data: InvoiceIn, customer: Customer | None, at: datetime) -> None:
    """Tính các khoản giảm và tổng tiền: hạng thành viên + khuyến mãi / voucher + giảm tay + dùng điểm."""
    subtotal = invoice.subtotal
    tier = loyalty.customer_tier(db, customer)
    tier_discount = int(subtotal * tier.discount_percent / 100 + 0.5) if tier and tier.discount_percent else 0

    keep_id = invoice.promotion_id  # sửa hóa đơn tạm: giữ được chương trình đã chọn trước đó
    promo = _resolve_promotion(db, data, keep_id)
    promo_discount = 0
    if promo:
        check_promotion(db, promo, subtotal, at, invoice.id)
        promo_discount = promotion_discount(promo, subtotal)
    manual = _compute_discount(subtotal, data)

    points_discount = 0
    if data.points_used:
        if customer is None:
            raise BusinessError("Chọn khách hàng để dùng điểm tích lũy")
        if settings.POINT_VALUE <= 0:
            raise BusinessError("Cửa hàng chưa cho phép dùng điểm tích lũy")
        if data.points_used > customer.points:
            raise BusinessError(f"Khách hàng chỉ có {customer.points} điểm")
        points_discount = data.points_used * settings.POINT_VALUE
        remain = subtotal - tier_discount - promo_discount - manual
        limit = max(0, remain) * settings.POINTS_MAX_PERCENT // 100
        if points_discount > limit:
            raise BusinessError(f"Chỉ được dùng điểm tối đa {settings.POINTS_MAX_PERCENT}% giá trị đơn "
                                f"({limit // settings.POINT_VALUE} điểm)")

    discount = tier_discount + promo_discount + manual + points_discount
    if discount > subtotal:
        raise BusinessError("Giảm giá không được lớn hơn tổng tiền hàng")
    invoice.promotion_id = promo.id if promo else None
    invoice.tier_discount, invoice.promo_discount = tier_discount, promo_discount
    invoice.points_used, invoice.points_discount = data.points_used, points_discount
    invoice.discount = discount
    invoice.total = subtotal - discount


def _fill(db: Session, invoice: Invoice, data: InvoiceIn, at: datetime) -> None:
    """Ghi dòng hàng và tiền vào hóa đơn (chưa đụng tới tồn kho)."""
    customer = _get_customer(db, data.customer_id)
    # Gộp các dòng trùng sản phẩm để kiểm tra tồn kho chính xác
    qty_by_product: dict[int, int] = defaultdict(int)
    price_by_product: dict[int, int | None] = {}
    serials_by_product: dict[int, list[str]] = defaultdict(list)
    for item in data.items:
        qty_by_product[item.product_id] += item.quantity
        price_by_product.setdefault(item.product_id, item.unit_price)
        serials_by_product[item.product_id] += item.serials or []

    products = _lock_products(db, qty_by_product.keys())
    subtotal = 0
    for pid, qty in qty_by_product.items():
        product = products[pid]
        if product.status != "active":
            raise BusinessError(f"Sản phẩm '{product.name}' đang ngừng kinh doanh")
        if qty > product.stock:
            raise BusinessError(f"Sản phẩm '{product.name}' không đủ tồn kho (còn {product.stock}, cần {qty})")
        serials = serials_by_product[pid] if product.track_serial else []
        if len(set(serials)) != len(serials) or len(serials) > qty:
            raise BusinessError(f"Danh sách serial / IMEI của '{product.name}' không hợp lệ")
        price = price_by_product[pid] if price_by_product[pid] is not None else product.sale_price
        line_total = price * qty
        subtotal += line_total
        invoice.items.append(InvoiceItem(
            product_id=pid, quantity=qty, unit_price=price, unit_cost=product.cost_price,
            line_total=line_total, serials=serials or None,
        ))
    invoice.customer_id = data.customer_id
    invoice.note = data.note
    invoice.subtotal = subtotal
    _apply_amounts(db, invoice, data, customer, at)


def _apply_payment(invoice: Invoice, data: InvoiceIn | InvoicePayIn) -> None:
    invoice.payment_method = data.payment_method
    invoice.payment_ref = (data.payment_ref or "").strip() or None
    invoice.cash_received = None
    if data.payment_method == "cash" and data.cash_received is not None:
        if data.cash_received < invoice.total:
            raise BusinessError("Tiền khách đưa ít hơn tổng tiền cần thanh toán")
        invoice.cash_received = data.cash_received


def _get_customer(db: Session, customer_id: int | None) -> Customer | None:
    if customer_id is None:
        return None
    c = db.get(Customer, customer_id)
    if c is None:
        raise BusinessError("Khách hàng không tồn tại")
    return c


_check_customer = _get_customer  # tên cũ


def _pay(db: Session, invoice: Invoice, payment: InvoiceIn | InvoicePayIn, user: User, at: datetime) -> None:
    """Thanh toán hóa đơn tạm: trừ kho, bán serial, dùng / tích điểm. Thời điểm bán = lúc thanh toán."""
    if invoice.status != "pending":
        raise BusinessError("Hóa đơn này không ở trạng thái chờ thanh toán")
    invoice.created_at = at
    products = _lock_products(db, [i.product_id for i in invoice.items])
    for item in invoice.items:
        product = products[item.product_id]
        if product.status != "active":
            raise BusinessError(f"Sản phẩm '{product.name}' đang ngừng kinh doanh")
        serials = _check_serial_count(product, item.serials, item.quantity, "chọn")
        change_stock(db, product, -item.quantity, "sale", invoice.code, user, at=at)
        if serials:
            _sell_serials(db, product, serials, invoice, at)
        item.unit_cost = product.cost_price  # giá vốn tại thời điểm bán
    if invoice.promotion_id:
        promo = db.get(Promotion, invoice.promotion_id)
        if promo.usage_limit and promotion_usage(db, promo.id, invoice.id) >= promo.usage_limit:
            raise BusinessError(f"Voucher '{promo.code or promo.name}' đã hết lượt sử dụng")
    customer = _get_customer(db, invoice.customer_id)
    if customer is not None:
        try:
            if invoice.points_used:
                loyalty.change_points(db, customer, -invoice.points_used, "redeem", invoice.code, user,
                                      f"Trừ {invoice.points_discount:,} ₫".replace(",", "."))
            invoice.points_earned = loyalty.earn_for(invoice.total)
            loyalty.change_points(db, customer, invoice.points_earned, "earn", invoice.code, user)
        except loyalty.PointsError as e:
            raise BusinessError(str(e))
    _apply_payment(invoice, payment)
    invoice.status = "paid"
    db.flush()


def create_invoice(db: Session, data: InvoiceIn, user: User, at: datetime | None = None) -> Invoice:
    """Lập hóa đơn. data.pay=True: thanh toán luôn; False: lưu hóa đơn tạm."""
    at = at or now()
    invoice = Invoice(code=next_code(db, Invoice, "HD", at), user_id=user.id, created_at=at, status="pending",
                      payment_method=data.payment_method)
    db.add(invoice)
    _fill(db, invoice, data, at)
    db.flush()
    if data.pay:
        _pay(db, invoice, data, user, at)
    return invoice


def update_invoice(db: Session, invoice: Invoice, data: InvoiceIn, user: User) -> Invoice:
    """Sửa hóa đơn tạm (chưa thanh toán). Hóa đơn đã thanh toán không sửa: hủy (có duyệt) hoặc đổi trả."""
    if invoice.status != "pending":
        raise BusinessError("Chỉ sửa được hóa đơn chưa thanh toán. Hóa đơn đã thanh toán hãy hủy hoặc làm đổi trả")
    invoice.items.clear()
    db.flush()
    at = now()
    _fill(db, invoice, data, at)
    invoice.payment_method = data.payment_method
    db.flush()
    if data.pay:
        _pay(db, invoice, data, user, at)
    return invoice


def pay_invoice(db: Session, invoice: Invoice, data: InvoicePayIn, user: User) -> Invoice:
    if invoice.status != "pending":
        raise BusinessError("Hóa đơn đã thanh toán hoặc đã hủy")
    customer = _get_customer(db, invoice.customer_id)
    if invoice.points_used and (customer is None or customer.points < invoice.points_used):
        raise BusinessError("Khách hàng không còn đủ điểm, hãy sửa lại hóa đơn")
    _pay(db, invoice, data, user, now())
    return invoice


def request_cancel(db: Session, invoice: Invoice, reason: str, user: User) -> Invoice:
    """Thu ngân yêu cầu hủy hóa đơn đã thanh toán, chờ chủ cửa hàng duyệt."""
    if invoice.status != "paid":
        raise BusinessError("Chỉ gửi yêu cầu hủy cho hóa đơn đã thanh toán")
    if invoice.cancel_requested_at:
        raise BusinessError("Hóa đơn đang chờ chủ cửa hàng duyệt hủy")
    if invoice.returns:
        raise BusinessError("Hóa đơn đã có phiếu đổi trả, không thể hủy")
    invoice.cancel_requested_at, invoice.cancel_requested_by, invoice.cancel_reason = now(), user.id, reason
    db.flush()
    return invoice


def reject_cancel(db: Session, invoice: Invoice) -> Invoice:
    if not invoice.cancel_requested_at or invoice.status != "paid":
        raise BusinessError("Hóa đơn không có yêu cầu hủy đang chờ duyệt")
    invoice.cancel_requested_at = invoice.cancel_requested_by = invoice.cancel_reason = None
    db.flush()
    return invoice


def cancel_invoice(db: Session, invoice: Invoice, reason: str, user: User) -> Invoice:
    """Hủy hóa đơn. Hóa đơn tạm: chỉ đổi trạng thái. Đã thanh toán: hoàn kho, trả serial về kho, hoàn điểm."""
    if invoice.status == "cancelled":
        raise BusinessError("Hóa đơn đã bị hủy trước đó")
    if invoice.status == "paid":
        if invoice.returns:
            raise BusinessError("Hóa đơn đã có phiếu đổi trả, không thể hủy")
        products = _lock_products(db, [i.product_id for i in invoice.items])
        for item in invoice.items:
            change_stock(db, products[item.product_id], item.quantity, "cancel", invoice.code, user)
            if item.serials:
                _release_serials(db, item.serials)
        customer = _get_customer(db, invoice.customer_id)
        if customer is not None:
            loyalty.change_points(db, customer, -invoice.points_earned, "revert", invoice.code, user,
                                  "Hủy hóa đơn: trừ điểm đã tích", clamp=True)
            loyalty.change_points(db, customer, invoice.points_used, "revert", invoice.code, user,
                                  "Hủy hóa đơn: hoàn điểm đã dùng")
    invoice.status = "cancelled"
    invoice.cancelled_at = now()
    invoice.cancel_reason = reason
    invoice.cancel_requested_at = None
    db.flush()
    return invoice


# ================================================================ Phiếu nhập
def _resolve_supplier(db: Session, supplier_id: int | None, name: str | None) -> tuple[int | None, str | None]:
    if supplier_id:
        s = db.get(Supplier, supplier_id)
        if s is None:
            raise BusinessError("Nhà cung cấp không tồn tại")
        return s.id, s.name
    name = " ".join((name or "").split()) or None
    if name:  # tên gõ tay trùng nhà cung cấp đã có: gắn luôn vào danh sách
        s = next((x for x in db.scalars(select(Supplier)) if x.name.casefold() == name.casefold()), None)
        if s:
            return s.id, s.name
    return None, name


def _post_import(db: Session, receipt: ImportReceipt, data: ImportIn, user: User, at: datetime) -> None:
    """Ghi dòng hàng của phiếu nhập và cộng kho."""
    receipt.supplier_id, receipt.supplier = _resolve_supplier(db, data.supplier_id, data.supplier)
    receipt.note = data.note
    products = _lock_products(db, [i.product_id for i in data.items if i.product_id is not None])
    created: dict[str, Product] = {}  # cùng một tên mới xuất hiện nhiều dòng => chỉ tạo một sản phẩm
    total = 0
    for item in data.items:
        if item.new_product is not None:
            key = " ".join(item.new_product.name.split()).casefold()
            if key not in created:
                created[key] = _create_product(db, item.new_product, item.unit_cost)
            product = created[key]
        else:
            product = products[item.product_id]
        serials = _check_serial_count(product, item.serials, item.quantity, "nhập")
        change_stock(db, product, item.quantity, "import", receipt.code, user, at=at)
        if serials:
            add_serials(db, product, serials, receipt.id)
        product.cost_price = item.unit_cost  # cập nhật giá nhập gần nhất
        line_total = item.quantity * item.unit_cost
        total += line_total
        receipt.items.append(ImportItem(
            product_id=product.id, quantity=item.quantity, unit_cost=item.unit_cost, line_total=line_total,
            serials=serials or None,
        ))
    receipt.total = total
    receipt.status = "completed"
    receipt.confirmed_at, receipt.confirmed_by = at, user.id


def create_import(db: Session, data: ImportIn, user: User, at: datetime | None = None) -> ImportReceipt:
    at = at or now()
    receipt = ImportReceipt(code=next_code(db, ImportReceipt, "PN", at), user_id=user.id, created_at=at)
    db.add(receipt)
    db.flush()
    _post_import(db, receipt, data, user, at)
    db.flush()
    return receipt


def _draft_items(db: Session, receipt: ImportReceipt, data: ImportDraftIn) -> None:
    products = _lock_products(db, [i.product_id for i in data.items])
    receipt.supplier_id, receipt.supplier = _resolve_supplier(db, data.supplier_id, data.supplier)
    receipt.note = data.note
    total = 0
    for item in data.items:
        product = products[item.product_id]
        serials = item.serials if product.track_serial else None
        if serials and len(serials) > item.quantity:
            raise BusinessError(f"'{product.name}': số serial nhiều hơn số lượng nhập")
        cost = item.unit_cost or 0
        total += cost * item.quantity
        receipt.items.append(ImportItem(product_id=product.id, quantity=item.quantity, unit_cost=cost,
                                        line_total=cost * item.quantity, serials=serials or None))
    receipt.total = total


def create_import_draft(db: Session, data: ImportDraftIn, user: User) -> ImportReceipt:
    at = now()
    receipt = ImportReceipt(code=next_code(db, ImportReceipt, "PN", at), user_id=user.id, created_at=at,
                            status="draft")
    db.add(receipt)
    _draft_items(db, receipt, data)
    db.flush()
    return receipt


def update_import_draft(db: Session, receipt: ImportReceipt, data: ImportDraftIn) -> ImportReceipt:
    if receipt.status != "draft":
        raise BusinessError("Chỉ sửa được phiếu nhập nháp")
    receipt.items.clear()
    db.flush()
    _draft_items(db, receipt, data)
    db.flush()
    return receipt


def confirm_import(db: Session, receipt: ImportReceipt, data: ImportIn, user: User) -> ImportReceipt:
    """Chủ cửa hàng duyệt phiếu nháp (có thể sửa số lượng, giá nhập): cộng kho từ lúc này."""
    if receipt.status != "draft":
        raise BusinessError("Phiếu này không phải phiếu nháp")
    receipt.items.clear()
    db.flush()
    _post_import(db, receipt, data, user, now())
    db.flush()
    return receipt


def cancel_import(db: Session, receipt: ImportReceipt, reason: str, user: User) -> ImportReceipt:
    """Hủy phiếu nhập. Phiếu đã nhập kho: trừ lại tồn kho và xóa serial của phiếu (hàng phải còn trong kho)."""
    if receipt.status == "cancelled":
        raise BusinessError("Phiếu nhập đã bị hủy trước đó")
    if receipt.status == "completed":
        products = _lock_products(db, [i.product_id for i in receipt.items])
        serial_rows = db.scalars(select(ProductSerial).where(ProductSerial.import_id == receipt.id)).all()
        sold = [r.serial for r in serial_rows if r.status != "in_stock"]
        if sold:
            raise BusinessError(f"Không thể hủy: serial đã bán / lỗi: {', '.join(sold[:5])}")
        for item in receipt.items:
            product = products[item.product_id]
            if product.stock < item.quantity:
                raise BusinessError(f"Không thể hủy: '{product.name}' chỉ còn {product.stock} trong kho "
                                    f"(phiếu nhập {item.quantity}), hàng đã bán bớt")
            change_stock(db, product, -item.quantity, "import_cancel", receipt.code, user, note=reason)
        for r in serial_rows:
            db.delete(r)
    receipt.status = "cancelled"
    receipt.cancelled_at, receipt.cancel_reason = now(), reason
    db.flush()
    return receipt


def _new_product_code(db: Session) -> str:
    """Mã tự sinh cho sản phẩm tạo khi nhập hàng: SP0001, SP0002..."""
    nums = [int(c[2:]) for c in db.scalars(select(Product.code).where(Product.code.like("SP%"))) if c[2:].isdigit()]
    return f"SP{max(nums, default=0) + 1:04d}"


def _create_product(db: Session, spec: NewProductIn, unit_cost: int) -> Product:
    """Tạo sản phẩm mới ngay trong phiếu nhập (tồn ban đầu 0, phiếu nhập sẽ cộng tồn)."""
    name = " ".join(spec.name.split())
    if name.casefold() in {n.casefold() for n in db.scalars(select(Product.name))}:
        raise BusinessError(f"Sản phẩm '{name}' đã có trong danh mục, hãy chọn sản phẩm có sẵn thay vì tạo mới")
    code = (spec.code or "").strip().upper() or _new_product_code(db)
    if db.scalar(select(Product.id).where(func.upper(Product.code) == code)):
        raise BusinessError(f"Mã sản phẩm '{code}' đã tồn tại")
    if spec.category_id is not None and db.get(Category, spec.category_id) is None:
        raise BusinessError("Nhóm hàng không tồn tại")
    product = Product(code=code, name=name, category_id=spec.category_id, sale_price=spec.sale_price,
                      cost_price=unit_cost, stock=0, min_stock=spec.min_stock,
                      description=(spec.description or "").strip() or None, status="active")
    db.add(product)
    db.flush()
    return product


def adjust_stock(db: Session, product: Product, new_stock: int, note: str, user: User) -> None:
    delta = new_stock - product.stock
    if delta:
        change_stock(db, product, delta, "adjust", None, user, note=note)
