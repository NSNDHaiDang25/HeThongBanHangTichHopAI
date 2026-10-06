import re
from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator, model_validator

Role = Literal["admin", "owner", "staff"]
PaymentMethod = Literal["cash", "transfer", "card", "qr"]
CustomerGroup = Literal["regular", "vip", "wholesale"]
EMAIL_RE = r"[^@\s]+@[^@\s]+\.[^@\s]+"


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


def _positive(message: str) -> AfterValidator:
    """Số phải > 0, báo lỗi bằng câu chữ trong SRS thay cho thông báo tiếng Anh mặc định của Pydantic."""
    def check(v: int) -> int:
        if v <= 0:
            raise ValueError(message)
        return v
    return AfterValidator(check)


def _email(v: str | None) -> str | None:
    v = (v or "").strip()
    if v and not re.fullmatch(EMAIL_RE, v):
        raise ValueError("Email không hợp lệ")
    return v or None


def _serials(v: list[str] | None) -> list[str] | None:
    """Danh sách serial / IMEI: bỏ khoảng trắng, bỏ dòng trống, không trùng nhau."""
    if v is None:
        return None
    out = [s.strip().upper() for s in v if s and s.strip()]
    if any(len(s) > 100 for s in out):
        raise ValueError("Serial / IMEI tối đa 100 ký tự")
    if len(set(out)) != len(out):
        raise ValueError("Danh sách serial / IMEI bị trùng")
    return out


SalePrice = Annotated[int, _positive("Giá bán phải lớn hơn 0")]
ImportAmount = Annotated[int, _positive("Số lượng và giá nhập phải lớn hơn 0")]  # số lượng / giá nhập
Email = Annotated[str | None, AfterValidator(_email)]
Serials = Annotated[list[str] | None, AfterValidator(_serials)]


# ---------- Auth / User ----------
class LoginIn(BaseModel):
    username: str
    password: str


class UserOut(ORM):
    id: int
    username: str
    full_name: str
    email: str | None = None
    role: Role
    is_active: bool
    pending: bool = False


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=1, max_length=100)
    email: Email = None
    password: str = Field(min_length=6)
    role: Role = "staff"


class RegisterIn(BaseModel):
    """Tự tạo tài khoản ở màn hình đăng nhập (chờ quản trị viên duyệt)."""
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("username")
    @classmethod
    def username_chars(cls, v: str):
        v = v.strip()
        if not re.fullmatch(r"[A-Za-z0-9._-]{3,50}", v):
            raise ValueError("Tên đăng nhập gồm 3-50 ký tự: chữ không dấu, số và . _ -")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_not_blank(cls, v: str):
        v = " ".join(v.split())
        if not v:
            raise ValueError("Vui lòng nhập họ tên")
        return v


class ForgotPasswordIn(BaseModel):
    username: str = Field(min_length=1, max_length=50)


class ResetPasswordIn(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    code: str = Field(min_length=1, max_length=12)
    new_password: str = Field(min_length=6, max_length=128)


class ChangePasswordIn(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=6, max_length=128)


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: Email = None
    password: str | None = Field(default=None, min_length=6)
    role: Role | None = None
    is_active: bool | None = None


# ---------- Category ----------
class CategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class CategoryOut(ORM):
    id: int
    name: str
    description: str | None


# ---------- Product ----------
class ProductIn(BaseModel):
    code: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=200)
    category_id: int | None = None
    # Nhập tên nhóm thay cho category_id: chưa có thì tạo mới, chuỗi rỗng = không phân nhóm
    category_name: str | None = Field(default=None, max_length=100)
    sale_price: SalePrice
    cost_price: int = Field(ge=0, default=0)
    stock: int = Field(ge=0, default=0)
    min_stock: int = Field(ge=0, default=5)
    warranty_months: int = Field(ge=0, le=120, default=0)
    track_serial: bool = False
    description: str | None = None
    status: Literal["active", "inactive"] = "active"


class ProductUpdate(BaseModel):
    """Không cho sửa trực tiếp tồn kho ở đây: tồn kho thay đổi qua hóa đơn, phiếu nhập hoặc điều chỉnh kho."""
    code: str | None = Field(default=None, min_length=1, max_length=30)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category_id: int | None = None
    category_name: str | None = Field(default=None, max_length=100)  # như ProductIn.category_name
    sale_price: SalePrice | None = None
    cost_price: int | None = Field(default=None, ge=0)
    min_stock: int | None = Field(default=None, ge=0)
    warranty_months: int | None = Field(default=None, ge=0, le=120)
    track_serial: bool | None = None
    description: str | None = None
    status: Literal["active", "inactive"] | None = None


class StockAdjustIn(BaseModel):
    new_stock: int = Field(ge=0)
    note: str = Field(min_length=1, max_length=255)


class ProductOut(ORM):
    id: int
    code: str
    name: str
    category_id: int | None
    category_name: str | None = None
    sale_price: int
    cost_price: int
    stock: int
    min_stock: int
    warranty_months: int = 0
    track_serial: bool = False
    description: str | None
    image_url: str | None = None
    status: str


class SerialsIn(BaseModel):
    """Thêm serial cho hàng đang có trong kho (VD: bật quản lý serial cho sản phẩm đã có tồn)."""
    product_id: int
    serials: Serials = Field(min_length=1)
    note: str | None = Field(default=None, max_length=255)


class SerialUpdate(BaseModel):
    status: Literal["in_stock", "defective"] | None = None
    note: str | None = Field(default=None, max_length=255)


# ---------- Customer ----------
class CustomerIn(BaseModel):
    code: str | None = Field(default=None, max_length=30)
    name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    email: Email = None
    address: str | None = None
    group: CustomerGroup = "regular"
    note: str | None = None

    @field_validator("phone")
    @classmethod
    def phone_digits(cls, v: str | None):
        if v:
            v = re.sub(r"[\s.\-]", "", v)
            if not re.fullmatch(r"0\d{9}", v):
                raise ValueError("Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 0")
        return v or None


class CustomerOut(ORM):
    id: int
    code: str
    name: str
    phone: str | None
    email: str | None
    address: str | None
    group: str
    note: str | None
    points: int = 0
    created_at: datetime


class PointsAdjustIn(BaseModel):
    change: int = Field(ge=-1_000_000, le=1_000_000)
    note: str = Field(min_length=1, max_length=255)

    @field_validator("change")
    @classmethod
    def not_zero(cls, v: int):
        if v == 0:
            raise ValueError("Số điểm điều chỉnh phải khác 0")
        return v


class TierIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    min_spent: int = Field(ge=0)
    discount_percent: int = Field(ge=0, le=50)
    note: str | None = Field(default=None, max_length=255)


# ---------- Invoice ----------
class InvoiceItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: int | None = Field(default=None, ge=0)  # bỏ trống => lấy giá bán hiện tại (chỉ chủ cửa hàng được đặt)
    serials: Serials = None  # bắt buộc khi thanh toán sản phẩm quản lý theo serial / IMEI


class InvoiceIn(BaseModel):
    customer_id: int | None = None
    items: list[InvoiceItemIn] = Field(min_length=1)
    promotion_id: int | None = None  # chương trình khuyến mãi không cần mã
    voucher_code: str | None = Field(default=None, max_length=30)  # hoặc mã voucher khách đưa
    points_used: int = Field(default=0, ge=0)  # điểm tích lũy khách dùng để trừ tiền
    # Giảm giá tự nhập (chỉ chủ cửa hàng); cộng thêm vào các khoản giảm khác
    discount: int = Field(default=0, ge=0)
    discount_percent: float | None = Field(default=None, ge=0, le=100)
    pay: bool = True  # False = lưu hóa đơn tạm (chưa thanh toán, chưa trừ kho, còn sửa được)
    payment_method: PaymentMethod = "cash"
    cash_received: int | None = Field(default=None, ge=0)  # chỉ dùng với tiền mặt
    payment_ref: str | None = Field(default=None, max_length=50)  # nội dung CK / mã giao dịch POS
    note: str | None = None


class InvoicePayIn(BaseModel):
    payment_method: PaymentMethod = "cash"
    cash_received: int | None = Field(default=None, ge=0)
    payment_ref: str | None = Field(default=None, max_length=50)


class InvoiceCancelIn(BaseModel):
    reason: str = Field(min_length=1, max_length=255)


class CancelRejectIn(BaseModel):
    note: str | None = Field(default=None, max_length=255)


class InvoiceEmailIn(BaseModel):
    to: Email = None  # bỏ trống = email của khách hàng trên hóa đơn


# ---------- Import ----------
class NewProductIn(BaseModel):
    """Sản phẩm chưa có trong danh mục: tạo luôn khi lưu phiếu nhập."""
    name: str = Field(min_length=1, max_length=200)
    code: str | None = Field(default=None, max_length=30)  # bỏ trống => tự sinh SP0001, SP0002...
    category_id: int | None = None
    sale_price: SalePrice
    min_stock: int = Field(default=5, ge=0)
    description: str | None = None


class ImportItemIn(BaseModel):
    product_id: int | None = None
    new_product: NewProductIn | None = None
    quantity: ImportAmount
    unit_cost: ImportAmount
    serials: Serials = None  # sản phẩm quản lý theo serial: đủ số serial bằng số lượng

    @model_validator(mode="after")
    def one_product(self):
        if (self.product_id is None) == (self.new_product is None):
            raise ValueError("Mỗi dòng cần chọn sản phẩm có sẵn (product_id) hoặc nhập sản phẩm mới (new_product)")
        return self


class ImportIn(BaseModel):
    supplier_id: int | None = None
    supplier: str | None = None  # tên nhà cung cấp chưa có trong danh sách (bỏ qua khi có supplier_id)
    note: str | None = None
    items: list[ImportItemIn] = Field(min_length=1)


class ImportDraftItemIn(BaseModel):
    product_id: int
    quantity: ImportAmount
    unit_cost: int | None = Field(default=None, ge=0)  # theo phiếu giao hàng nếu có; chủ cửa hàng hoàn thiện khi duyệt
    serials: Serials = None


class ImportDraftIn(BaseModel):
    """Phiếu nhập nháp: thu ngân ghi nhận hàng về, chưa cộng kho cho tới khi chủ cửa hàng xác nhận."""
    supplier_id: int | None = None
    supplier: str | None = None
    note: str | None = None
    items: list[ImportDraftItemIn] = Field(min_length=1)


class ImportCancelIn(BaseModel):
    reason: str = Field(min_length=1, max_length=255)


# ---------- Supplier ----------
class SupplierIn(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=20)
    email: Email = None
    address: str | None = Field(default=None, max_length=255)
    note: str | None = Field(default=None, max_length=255)
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str):
        v = " ".join(v.split())
        if not v:
            raise ValueError("Vui lòng nhập tên nhà cung cấp")
        return v


class SupplierOut(ORM):
    id: int
    code: str
    name: str
    phone: str | None
    email: str | None
    address: str | None
    note: str | None
    is_active: bool


# ---------- Promotion / voucher ----------
class PromotionIn(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    code: str | None = Field(default=None, max_length=30)  # có mã = voucher
    discount_type: Literal["percent", "amount"] = "percent"
    value: int = Field(gt=0)
    max_discount: int | None = Field(default=None, gt=0)
    min_subtotal: int = Field(default=0, ge=0)
    usage_limit: int | None = Field(default=None, gt=0)
    start_date: date
    end_date: date
    is_active: bool = True
    note: str | None = Field(default=None, max_length=255)

    @field_validator("code")
    @classmethod
    def code_chars(cls, v: str | None):
        v = (v or "").strip().upper()
        if v and not re.fullmatch(r"[A-Z0-9_-]{3,30}", v):
            raise ValueError("Mã voucher gồm 3-30 ký tự: chữ không dấu, số, - và _")
        return v or None

    @model_validator(mode="after")
    def check(self):
        if self.discount_type == "percent" and self.value > 100:
            raise ValueError("Phần trăm giảm phải từ 1 đến 100")
        if self.end_date < self.start_date:
            raise ValueError("Ngày kết thúc phải sau ngày bắt đầu")
        return self


class PromotionOut(ORM):
    id: int
    name: str
    code: str | None
    discount_type: str
    value: int
    max_discount: int | None
    min_subtotal: int
    usage_limit: int | None
    start_date: date
    end_date: date
    is_active: bool
    note: str | None


# ---------- Đổi trả, bảo hành ----------
class ReturnItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    restock: bool = True  # False = hàng lỗi, không nhập lại kho
    serials: Serials = None  # sản phẩm quản lý theo serial: đúng các máy khách trả


class ReturnIn(BaseModel):
    invoice_id: int
    items: list[ReturnItemIn] = Field(min_length=1)
    reason: str = Field(min_length=1, max_length=255)
    note: str | None = Field(default=None, max_length=255)


class WarrantyIn(BaseModel):
    invoice_id: int | None = None  # bỏ trống = khách không có hóa đơn (tính là ngoài bảo hành)
    product_id: int
    customer_name: str | None = Field(default=None, max_length=100)  # bỏ trống = lấy theo hóa đơn
    customer_phone: str | None = Field(default=None, max_length=20)
    serial: str | None = Field(default=None, max_length=100)
    issue: str = Field(min_length=1, max_length=500)


class WarrantyUpdate(BaseModel):
    status: Literal["received", "processing", "done", "rejected"]
    note: str | None = Field(default=None, max_length=500)  # tiến độ / kết quả xử lý


# ---------- Quản trị hệ thống ----------
class SettingsUpdate(BaseModel):
    values: dict[str, str | int | float | bool | list[str] | None] = Field(min_length=1)


# ---------- AI ----------
class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    session_id: int | None = None  # bỏ trống => bắt đầu cuộc trò chuyện mới


class QuestionIn(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    session_id: int | None = None


class SessionRename(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class VietQRIn(BaseModel):
    amount: int = Field(gt=0)
    content: str = Field(default="", max_length=50)


class AIReportIn(BaseModel):
    date_from: str | None = None  # YYYY-MM-DD
    date_to: str | None = None
