"""Nghiệp vụ tồn kho, hóa đơn và phiếu nhập.

Mọi thay đổi tồn kho đi qua `change_stock` để luôn có nhật ký StockMovement và
không bao giờ để tồn kho âm. Các hàm ở đây KHÔNG commit; router gọi commit sau khi
toàn bộ nghiệp vụ thành công (một giao dịch duy nhất).
"""
from collections import defaultdict
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import set_committed_value

from app.models import (
    Category, Customer, ImportItem, ImportReceipt, Invoice, InvoiceItem, Product, StockMovement, User, now,
)
from app.schemas import ImportIn, InvoiceIn, NewProductIn


class BusinessError(Exception):
    """Lỗi nghiệp vụ, router chuyển thành HTTP 400."""


def change_stock(db: Session, product: Product, delta: int, type_: str, ref: str | None,
                 user: User | None, note: str | None = None, at: datetime | None = None) -> None:
    """FR-STK-06: trừ tồn bằng một câu UPDATE có điều kiện stock >= số cần trừ rồi kiểm tra số dòng bị ảnh hưởng,
    không đọc tồn rồi mới ghi lại, nên hai quầy cùng bán chiếc cuối cùng thì chỉ một quầy thành công."""
    stmt = update(Product).where(Product.id == product.id).values(stock=Product.stock + delta)
    if delta < 0:
        stmt = stmt.where(Product.stock >= -delta)
    result = db.execute(stmt.execution_options(synchronize_session=False))
    if result.rowcount != 1:
        current = db.scalar(select(Product.stock).where(Product.id == product.id))
        raise BusinessError(f"Sản phẩm '{product.name}' không đủ tồn kho (còn {current}, cần {-delta})")
    new_stock = db.scalar(select(Product.stock).where(Product.id == product.id))
    set_committed_value(product, "stock", new_stock)
    db.add(StockMovement(
        product_id=product.id, change=delta, stock_after=new_stock, type=type_, ref_code=ref,
        user_id=user.id if user else None, note=note, created_at=at or now(),
    ))


def _next_code(db: Session, model, prefix: str, at: datetime) -> str:
    day = at.strftime("%y%m%d")
    base = f"{prefix}{day}"
    count = db.scalar(select(func.count()).select_from(model).where(model.code.like(f"{base}%"))) or 0
    return f"{base}{count + 1:04d}"


def _lock_products(db: Session, product_ids) -> dict[int, Product]:
    products = db.scalars(select(Product).where(Product.id.in_(set(product_ids))).with_for_update()).all()
    found = {p.id: p for p in products}
    missing = set(product_ids) - found.keys()
    if missing:
        raise BusinessError(f"Không tìm thấy sản phẩm id {sorted(missing)}")
    return found


def _compute_discount(subtotal: int, data: InvoiceIn) -> int:
    discount = data.discount
    if data.discount_percent is not None:
        discount = int(subtotal * data.discount_percent / 100 + 0.5)  # làm tròn nửa lên, khớp với giao diện
    if discount > subtotal:
        raise BusinessError("Giảm giá không được lớn hơn tổng tiền hàng")
    return discount


def _apply_items(db: Session, invoice: Invoice, data: InvoiceIn, user: User,
                 move_type: str, at: datetime) -> None:
    # Gộp các dòng trùng sản phẩm để kiểm tra tồn kho chính xác
    qty_by_product: dict[int, int] = defaultdict(int)
    price_by_product: dict[int, int | None] = {}
    for item in data.items:
        qty_by_product[item.product_id] += item.quantity
        price_by_product.setdefault(item.product_id, item.unit_price)

    products = _lock_products(db, qty_by_product.keys())
    subtotal = 0
    for pid, qty in qty_by_product.items():
        product = products[pid]
        if product.status != "active":
            raise BusinessError(f"Sản phẩm '{product.name}' đang ngừng kinh doanh")
        price = price_by_product[pid] if price_by_product[pid] is not None else product.sale_price
        change_stock(db, product, -qty, move_type, invoice.code, user, at=at)
        line_total = price * qty
        subtotal += line_total
        invoice.items.append(InvoiceItem(
            product_id=pid, quantity=qty, unit_price=price, unit_cost=product.cost_price,
            line_total=line_total,
        ))
    invoice.subtotal = subtotal
    invoice.discount = _compute_discount(subtotal, data)
    invoice.total = subtotal - invoice.discount


def _restore_items(db: Session, invoice: Invoice, user: User, move_type: str) -> None:
    products = _lock_products(db, [i.product_id for i in invoice.items])
    for item in invoice.items:
        change_stock(db, products[item.product_id], item.quantity, move_type, invoice.code, user)


def _apply_payment(invoice: Invoice, data: InvoiceIn) -> None:
    invoice.payment_method = data.payment_method
    invoice.payment_ref = (data.payment_ref or "").strip() or None
    invoice.cash_received = None
    if data.payment_method == "cash" and data.cash_received is not None:
        if data.cash_received < invoice.total:
            raise BusinessError("Tiền khách đưa ít hơn tổng tiền cần thanh toán")
        invoice.cash_received = data.cash_received


def _check_customer(db: Session, customer_id: int | None) -> None:
    if customer_id is not None and db.get(Customer, customer_id) is None:
        raise BusinessError("Khách hàng không tồn tại")


def create_invoice(db: Session, data: InvoiceIn, user: User, at: datetime | None = None) -> Invoice:
    at = at or now()
    _check_customer(db, data.customer_id)
    invoice = Invoice(
        code=_next_code(db, Invoice, "HD", at), customer_id=data.customer_id, user_id=user.id,
        created_at=at, note=data.note, status="paid",
    )
    db.add(invoice)
    _apply_items(db, invoice, data, user, "sale", at)
    _apply_payment(invoice, data)
    db.flush()
    return invoice


def update_invoice(db: Session, invoice: Invoice, data: InvoiceIn, user: User) -> Invoice:
    """Sửa hóa đơn: hoàn tồn kho theo dòng cũ, sau đó trừ theo dòng mới.

    Nếu dòng mới không đủ hàng, BusinessError được ném ra và router rollback
    => tồn kho giữ nguyên như trước khi sửa.
    """
    if invoice.status == "cancelled":
        raise BusinessError("Không thể sửa hóa đơn đã hủy")
    _check_customer(db, data.customer_id)
    _restore_items(db, invoice, user, "edit")
    invoice.items.clear()
    db.flush()
    invoice.customer_id = data.customer_id
    invoice.note = data.note
    _apply_items(db, invoice, data, user, "edit", now())
    _apply_payment(invoice, data)
    db.flush()
    return invoice


def cancel_invoice(db: Session, invoice: Invoice, reason: str, user: User) -> Invoice:
    if invoice.status == "cancelled":
        raise BusinessError("Hóa đơn đã bị hủy trước đó")
    _restore_items(db, invoice, user, "cancel")
    invoice.status = "cancelled"
    invoice.cancelled_at = now()
    invoice.cancel_reason = reason
    db.flush()
    return invoice


def create_import(db: Session, data: ImportIn, user: User, at: datetime | None = None) -> ImportReceipt:
    """Phiếu nhập kiểu cũ (/api/imports): lập và xác nhận nhập kho ngay, nhà cung cấp chỉ ghi tên."""
    from app.schemas import PurchaseItemIn, PurchaseOrderIn
    from app.services import purchasing
    po = PurchaseOrderIn(supplier_id=data.supplier_id, supplier_name=data.supplier, note=data.note, confirm=True,
                         items=[PurchaseItemIn(product_id=i.product_id, new_product=i.new_product, quantity=i.quantity,
                                               unit_cost=i.unit_cost, serials=i.serials) for i in data.items])
    return purchasing.create(db, po, user, at, require_supplier=False)


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
    cat = db.get(Category, spec.category_id) if spec.category_id else None
    product = Product(code=code, name=name, category_id=spec.category_id, sale_price=spec.sale_price,
                      cost_price=unit_cost, stock=0, min_stock=spec.min_stock, track_serial=spec.track_serial,
                      vat_rate=cat.default_vat_rate if cat else 10,
                      warranty_months=cat.default_warranty_months if cat else 12,
                      description=(spec.description or "").strip() or None, status="active")
    db.add(product)
    db.flush()
    return product


def adjust_stock(db: Session, product: Product, new_stock: int, note: str, user: User) -> None:
    """FR-STK-04: kiểm kê, điều chỉnh tồn kèm lý do. Hàng theo serial thì tồn đi theo serial (BR-18)."""
    if product.track_serial:
        raise BusinessError("Sản phẩm quản lý theo serial: tồn kho thay đổi qua phiếu nhập, bán hàng, đổi trả "
                            "hoặc đổi trạng thái serial")
    delta = new_stock - product.stock
    if delta:
        old = product.stock
        change_stock(db, product, delta, "adjust", None, user, note=note)
        from app.services import audit
        audit.log(db, user, "STOCK_ADJUST", "products", product.id, old={"stock": old},
                  new={"stock": new_stock, "note": note})
