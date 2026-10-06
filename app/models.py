"""Mô hình dữ liệu. Tiền tệ lưu dạng số nguyên (VND) để tránh sai số dấu phẩy động."""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Ba vai trò độc lập, không kế thừa quyền của nhau:
# admin = quản trị hệ thống (tài khoản, cấu hình kỹ thuật / AI, sao lưu, nhật ký; không bán hàng, không xem giá vốn
#         và doanh thu), staff = thu ngân, owner = chủ cửa hàng (nghiệp vụ của thu ngân + hàng hóa, giá, khuyến mãi,
#         nhà cung cấp, nhập hàng, tồn kho, báo cáo, duyệt hủy hóa đơn, toàn bộ AI).
ROLES = ("admin", "owner", "staff")
PAYMENT_METHODS = ("cash", "transfer", "card", "qr")  # qr = khách quét VietQR
CUSTOMER_GROUPS = ("regular", "vip", "wholesale")
# pending = hóa đơn tạm (chưa thanh toán, chưa trừ kho, còn sửa được) | paid = đã thanh toán | cancelled = đã hủy
INVOICE_STATUSES = ("pending", "paid", "cancelled")


# Giờ cửa hàng: Việt Nam UTC+7 (không đổi giờ mùa hè). Không dùng giờ hệ thống vì máy chủ deploy
# (Render, Docker) chạy theo UTC: phiếu tạo lúc 10:41 sẽ bị lưu thành 03:41, sau 17:00 còn sai cả ngày.
SHOP_TZ = timezone(timedelta(hours=7), "ICT")


def now() -> datetime:
    """Giờ Việt Nam hiện tại, không kèm múi giờ (cùng dạng dữ liệu đã lưu). Ngày hôm nay: now().date()."""
    return datetime.now(SHOP_TZ).replace(tzinfo=None, microsecond=0)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(100))  # nhận mã đặt lại mật khẩu
    password_hash: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20), default="staff")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Tự đăng ký ở màn hình đăng nhập: bị khóa và chờ quản trị viên duyệt (phân biệt với tài khoản bị khóa thường)
    pending: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class PasswordReset(Base):
    """Mã đặt lại mật khẩu gửi qua email. Chỉ lưu mã đã băm, mã gốc chỉ có trong email."""
    __tablename__ = "password_resets"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    code_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    sale_price: Mapped[int] = mapped_column(Integer, default=0)
    cost_price: Mapped[int] = mapped_column(Integer, default=0)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    min_stock: Mapped[int] = mapped_column(Integer, default=5)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | inactive
    warranty_months: Mapped[int] = mapped_column(Integer, default=0)  # 0 = không bảo hành
    # Quản lý theo từng máy (serial / IMEI): nhập kho phải ghi serial, bán phải chọn đúng serial
    track_serial: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)
    category: Mapped[Category | None] = relationship(back_populates="products")


class ProductSerial(Base):
    """Từng máy của sản phẩm quản lý theo serial / IMEI."""
    __tablename__ = "product_serials"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    serial: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    # in_stock = trong kho | sold = đã bán | defective = hàng lỗi (khách trả, không bán lại)
    status: Mapped[str] = mapped_column(String(20), default="in_stock", index=True)
    import_id: Mapped[int | None] = mapped_column(ForeignKey("import_receipts.id"))
    invoice_id: Mapped[int | None] = mapped_column(ForeignKey("invoices.id"))  # lần bán gần nhất
    sold_at: Mapped[datetime | None] = mapped_column(DateTime)
    note: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    product: Mapped[Product] = relationship()
    invoice: Mapped["Invoice | None"] = relationship()


class CustomerTier(Base):
    """Hạng thành viên: đạt tổng chi tiêu tối thiểu thì lên hạng, được giảm giá tự động khi mua."""
    __tablename__ = "customer_tiers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    min_spent: Mapped[int] = mapped_column(Integer, default=0)
    discount_percent: Mapped[int] = mapped_column(Integer, default=0)  # 0-50
    note: Mapped[str | None] = mapped_column(String(255))


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    phone: Mapped[str | None] = mapped_column(String(20), index=True)
    email: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(String(255))
    group: Mapped[str] = mapped_column(String(20), default="regular")
    note: Mapped[str | None] = mapped_column(String(255))
    points: Mapped[int] = mapped_column(Integer, default=0)  # điểm tích lũy hiện có
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="customer")


class PointTransaction(Base):
    """Lịch sử điểm tích lũy: tích điểm, dùng điểm, hoàn điểm khi hủy / trả hàng, chủ cửa hàng điều chỉnh."""
    __tablename__ = "point_transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    change: Mapped[int] = mapped_column(Integer)
    balance_after: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String(20))  # earn | redeem | revert | adjust
    ref_code: Mapped[str | None] = mapped_column(String(30))
    note: Mapped[str | None] = mapped_column(String(255))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)


class Promotion(Base):
    """Chương trình khuyến mãi / voucher theo đơn hàng do chủ cửa hàng tạo.

    Không có mã: thu ngân chọn trong danh sách. Có mã (voucher): khách đưa mã, thu ngân nhập đúng mã mới áp dụng được.
    """
    __tablename__ = "promotions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    code: Mapped[str | None] = mapped_column(String(30), unique=True, index=True)  # mã voucher
    discount_type: Mapped[str] = mapped_column(String(10), default="percent")  # percent | amount
    value: Mapped[int] = mapped_column(Integer)  # phần trăm (1-100) hoặc số tiền giảm
    max_discount: Mapped[int | None] = mapped_column(Integer)  # giảm tối đa (với loại phần trăm)
    min_subtotal: Mapped[int] = mapped_column(Integer, default=0)  # giá trị đơn tối thiểu
    usage_limit: Mapped[int | None] = mapped_column(Integer)  # số lần dùng tối đa (voucher), trống = không giới hạn
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    note: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # Thời điểm bán: lúc thanh toán (hóa đơn tạm được cập nhật lại khi thanh toán)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)
    subtotal: Mapped[int] = mapped_column(Integer, default=0)
    discount: Mapped[int] = mapped_column(Integer, default=0)  # tổng mọi khoản giảm bên dưới
    total: Mapped[int] = mapped_column(Integer, default=0)
    # Chi tiết giảm giá: hạng thành viên, khuyến mãi / voucher, dùng điểm (phần còn lại là giảm tay của chủ cửa hàng)
    tier_discount: Mapped[int] = mapped_column(Integer, default=0)
    promo_discount: Mapped[int] = mapped_column(Integer, default=0)
    points_used: Mapped[int] = mapped_column(Integer, default=0)
    points_discount: Mapped[int] = mapped_column(Integer, default=0)
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    payment_method: Mapped[str] = mapped_column(String(20), default="cash")
    cash_received: Mapped[int | None] = mapped_column(Integer)  # tiền khách đưa (tiền mặt)
    payment_ref: Mapped[str | None] = mapped_column(String(50))  # nội dung CK / mã giao dịch POS
    status: Mapped[str] = mapped_column(String(20), default="paid", index=True)  # pending | paid | cancelled
    note: Mapped[str | None] = mapped_column(String(255))
    promotion_id: Mapped[int | None] = mapped_column(ForeignKey("promotions.id"))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime)
    cancel_reason: Mapped[str | None] = mapped_column(String(255))  # lý do hủy (cả khi đang chờ duyệt)
    # Thu ngân gửi yêu cầu hủy, chủ cửa hàng duyệt: khác None = đang chờ duyệt
    cancel_requested_at: Mapped[datetime | None] = mapped_column(DateTime)
    cancel_requested_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    customer: Mapped[Customer | None] = relationship(back_populates="invoices")
    user: Mapped[User] = relationship(foreign_keys=[user_id])
    requester: Mapped[User | None] = relationship(foreign_keys=[cancel_requested_by])
    promotion: Mapped[Promotion | None] = relationship()
    items: Mapped[list["InvoiceItem"]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan"
    )
    returns: Mapped[list["ReturnReceipt"]] = relationship(back_populates="invoice", order_by="ReturnReceipt.id")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[int] = mapped_column(Integer)
    unit_cost: Mapped[int] = mapped_column(Integer, default=0)  # giá vốn tại thời điểm bán, dùng tính lãi gộp
    line_total: Mapped[int] = mapped_column(Integer)
    serials: Mapped[list | None] = mapped_column(JSON)  # serial / IMEI đã bán (sản phẩm quản lý theo serial)
    invoice: Mapped[Invoice] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()


class Supplier(Base):
    __tablename__ = "suppliers"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(String(255))
    note: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class ImportReceipt(Base):
    __tablename__ = "import_receipts"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    supplier: Mapped[str | None] = mapped_column(String(150))  # tên nhà cung cấp tại thời điểm nhập
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"))
    # draft = phiếu nháp (chưa cộng kho, chờ chủ cửa hàng xác nhận) | completed = đã nhập kho | cancelled = đã hủy
    status: Mapped[str] = mapped_column(String(20), default="completed", index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime)
    confirmed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime)
    cancel_reason: Mapped[str | None] = mapped_column(String(255))
    total: Mapped[int] = mapped_column(Integer, default=0)
    note: Mapped[str | None] = mapped_column(String(255))
    user: Mapped[User] = relationship(foreign_keys=[user_id])
    confirmer: Mapped[User | None] = relationship(foreign_keys=[confirmed_by])
    items: Mapped[list["ImportItem"]] = relationship(
        back_populates="receipt", cascade="all, delete-orphan"
    )


class ImportItem(Base):
    __tablename__ = "import_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    receipt_id: Mapped[int] = mapped_column(ForeignKey("import_receipts.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_cost: Mapped[int] = mapped_column(Integer)
    line_total: Mapped[int] = mapped_column(Integer)
    serials: Mapped[list | None] = mapped_column(JSON)
    receipt: Mapped[ImportReceipt] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()


class StockMovement(Base):
    """Nhật ký nhập - xuất - tồn (thẻ kho): mọi thay đổi tồn kho đều ghi lại tại đây."""
    __tablename__ = "stock_movements"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    change: Mapped[int] = mapped_column(Integer)  # dương = nhập, âm = xuất
    stock_after: Mapped[int] = mapped_column(Integer)
    # import | sale | cancel | edit | adjust | return | import_cancel
    type: Mapped[str] = mapped_column(String(20))
    ref_code: Mapped[str | None] = mapped_column(String(30))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    note: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)
    product: Mapped[Product] = relationship()


class ReturnReceipt(Base):
    """Phiếu đổi trả: khách trả lại hàng của một hóa đơn, cửa hàng hoàn tiền (đổi hàng = trả hàng + lập hóa đơn mới)."""
    __tablename__ = "return_receipts"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)
    reason: Mapped[str] = mapped_column(String(255))
    refund_total: Mapped[int] = mapped_column(Integer, default=0)
    points_reverted: Mapped[int] = mapped_column(Integer, default=0)  # điểm đã tích của phần hàng trả, bị trừ lại
    note: Mapped[str | None] = mapped_column(String(255))
    invoice: Mapped[Invoice] = relationship(back_populates="returns")
    user: Mapped[User] = relationship()
    items: Mapped[list["ReturnItem"]] = relationship(back_populates="receipt", cascade="all, delete-orphan")


class ReturnItem(Base):
    __tablename__ = "return_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    return_id: Mapped[int] = mapped_column(ForeignKey("return_receipts.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[int] = mapped_column(Integer)  # đơn giá trên hóa đơn (chưa trừ giảm giá)
    unit_cost: Mapped[int] = mapped_column(Integer, default=0)  # giá vốn lúc bán: hàng về kho thì trừ lại giá vốn
    refund: Mapped[int] = mapped_column(Integer)  # tiền hoàn cả dòng (đã chia phần giảm giá của hóa đơn)
    restock: Mapped[bool] = mapped_column(Boolean, default=True)  # False = hàng lỗi, không nhập lại kho
    serials: Mapped[list | None] = mapped_column(JSON)
    receipt: Mapped[ReturnReceipt] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()


class WarrantyTicket(Base):
    """Phiếu tiếp nhận bảo hành."""
    __tablename__ = "warranty_tickets"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    invoice_id: Mapped[int | None] = mapped_column(ForeignKey("invoices.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    customer_name: Mapped[str] = mapped_column(String(100))
    customer_phone: Mapped[str | None] = mapped_column(String(20))
    serial: Mapped[str | None] = mapped_column(String(100))  # số serial / IMEI
    issue: Mapped[str] = mapped_column(String(500))  # tình trạng lỗi khách báo
    warranty_until: Mapped[date | None] = mapped_column(Date)
    in_warranty: Mapped[bool] = mapped_column(Boolean, default=False)
    # received = đã tiếp nhận | processing = đang xử lý | done = đã trả khách | rejected = từ chối bảo hành
    status: Mapped[str] = mapped_column(String(20), default="received", index=True)
    result: Mapped[str | None] = mapped_column(String(500))  # kết quả xử lý / tiến độ mới nhất
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    history: Mapped[list | None] = mapped_column(JSON)  # tiến độ: [{time, status, note, user}]
    invoice: Mapped[Invoice | None] = relationship()
    product: Mapped[Product] = relationship()
    user: Mapped[User] = relationship()


class AuditLog(Base):
    """Nhật ký hệ thống: ai làm gì, lúc nào (đăng nhập, tài khoản, cấu hình, sao lưu, duyệt hủy, nhập kho...)."""
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    username: Mapped[str | None] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(50), index=True)
    detail: Mapped[str | None] = mapped_column(String(500))


class SystemSetting(Base):
    """Tham số đổi trên giao diện, ghi đè giá trị trong .env: cấu hình kỹ thuật / AI (quản trị viên)
    và tham số kinh doanh (chủ cửa hàng)."""
    __tablename__ = "system_settings"
    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))


class ChatSession(Base):
    """Lịch sử tra cứu AI: mỗi cuộc trò chuyện thuộc về một người dùng."""
    __tablename__ = "chat_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[str] = mapped_column(String(20), index=True)  # assistant | advisor | ask
    title: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.id"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(10))  # user | assistant
    content: Mapped[str] = mapped_column(Text)
    meta: Mapped[dict | None] = mapped_column(JSON)  # gợi ý sản phẩm, nguồn (AI/dự phòng), kỳ dữ liệu...
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    session: Mapped[ChatSession] = relationship(back_populates="messages")
