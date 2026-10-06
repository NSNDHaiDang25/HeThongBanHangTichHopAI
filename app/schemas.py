import re
from datetime import datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator, model_validator

Role = Literal["admin", "owner", "staff"]
# "transfer" và "qr" là tên cũ của chuyển khoản, vẫn nhận để không vỡ client cũ và được đổi thành bank_transfer
PaymentMethod = Literal["cash", "bank_transfer", "card", "transfer", "qr"]
CustomerGroup = Literal["regular", "vip", "wholesale"]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


def _positive(message: str) -> AfterValidator:
    """Số phải > 0, báo lỗi bằng câu chữ trong SRS thay cho thông báo tiếng Anh mặc định của Pydantic."""
    def check(v: int) -> int:
        if v <= 0:
            raise ValueError(message)
        return v
    return AfterValidator(check)


def _strong_password(v: str) -> str:
    from app.security import check_password_strength
    return check_password_strength(v)


StrongPassword = Annotated[str, Field(max_length=128), AfterValidator(_strong_password)]
Reason = Annotated[str, Field(min_length=5, max_length=255)]  # lý do hủy, đổi trả, điều chỉnh (bảng 5.18)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_phone(v: str | None) -> str | None:
    if v:
        v = re.sub(r"[\s.\-]", "", v)
        if not re.fullmatch(r"0\d{9}", v):
            raise ValueError("Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 0")
    return v or None


def normalize_email(v: str | None) -> str | None:
    v = (v or "").strip()
    if v and (len(v) > 100 or not EMAIL_RE.match(v)):
        raise ValueError("Email không hợp lệ")
    return v or None


SalePrice = Annotated[int, _positive("Giá bán phải lớn hơn 0")]
ImportAmount = Annotated[int, _positive("Số lượng và giá nhập phải lớn hơn 0")]  # số lượng / giá nhập


# ---------- Auth / User ----------
class LoginIn(BaseModel):
    username: str
    password: str


class UserOut(ORM):
    id: int
    username: str
    full_name: str
    role: Role
    email: str | None = None
    phone: str | None = None
    is_active: bool
    pending: bool = False
    must_change_password: bool = False
    locked_until: datetime | None = None
    last_login_at: datetime | None = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=1, max_length=100)
    password: StrongPassword  # mật khẩu tạm, người dùng phải đổi ở lần đăng nhập đầu (FR-USR-02)
    role: Role = "staff"
    email: Annotated[str | None, AfterValidator(normalize_email)] = None
    phone: Annotated[str | None, AfterValidator(normalize_phone)] = None


class ChangePasswordIn(BaseModel):
    old_password: str = Field(min_length=1, max_length=128)
    new_password: StrongPassword


class AdminResetPasswordIn(BaseModel):
    new_password: StrongPassword


class RegisterIn(BaseModel):
    """Tự tạo tài khoản ở màn hình đăng nhập (chờ quản trị viên duyệt)."""
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=1, max_length=100)
    password: StrongPassword

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
    new_password: StrongPassword


class UserUpdate(BaseModel):
    full_name: str | None = None
    password: StrongPassword | None = None
    role: Role | None = None
    is_active: bool | None = None
    email: Annotated[str | None, AfterValidator(normalize_email)] = None
    phone: Annotated[str | None, AfterValidator(normalize_phone)] = None
    unlock: bool = False  # mở khóa tạm do đăng nhập sai nhiều lần


# ---------- Category ----------
class CategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    default_vat_rate: int | None = Field(default=None, ge=0, le=100)  # bỏ trống => vat_rate_default
    default_warranty_months: int | None = Field(default=None, ge=0, le=120)
    is_active: bool = True


class CategoryOut(ORM):
    id: int
    name: str
    description: str | None
    default_vat_rate: int = 10
    default_warranty_months: int = 12
    is_active: bool = True


# ---------- Product ----------
ProductStatus = Literal["active", "inactive", "discontinued"]


def _sku(v: str) -> str:
    v = v.strip().upper()
    if not re.fullmatch(r"[A-Z0-9\-]{2,30}", v):
        raise ValueError("Mã sản phẩm (SKU) chỉ gồm chữ in hoa, số và dấu gạch ngang")
    return v


def _barcode(v: str | None) -> str | None:
    v = (v or "").strip()
    if v and not re.fullmatch(r"\d{8,14}", v):
        raise ValueError("Mã vạch phải là chuỗi số 8 đến 14 ký tự")
    return v or None


Sku = Annotated[str, Field(min_length=1, max_length=30), AfterValidator(_sku)]
Barcode = Annotated[str | None, AfterValidator(_barcode)]


class ProductIn(BaseModel):
    code: Sku
    barcode: Barcode = None
    name: str = Field(min_length=1, max_length=200)
    category_id: int | None = None
    # Nhập tên nhóm thay cho category_id: chưa có thì tạo mới, chuỗi rỗng = không phân nhóm
    category_name: str | None = Field(default=None, max_length=100)
    brand: str | None = Field(default=None, max_length=50)
    sale_price: SalePrice
    cost_price: int = Field(ge=0, default=0)
    vat_rate: int | None = Field(default=None, ge=0, le=100)  # bỏ trống => theo nhóm hàng
    warranty_months: int | None = Field(default=None, ge=0, le=120)  # bỏ trống => theo nhóm hàng
    track_serial: bool = False
    stock: int = Field(ge=0, default=0)
    min_stock: int = Field(ge=0, default=5)
    description: str | None = None
    status: ProductStatus = "active"


class ProductUpdate(BaseModel):
    """Không cho sửa trực tiếp tồn kho ở đây: tồn kho thay đổi qua hóa đơn, phiếu nhập hoặc điều chỉnh kho."""
    code: Sku | None = None
    barcode: Barcode = None
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category_id: int | None = None
    category_name: str | None = Field(default=None, max_length=100)  # như ProductIn.category_name
    brand: str | None = Field(default=None, max_length=50)
    sale_price: SalePrice | None = None
    cost_price: int | None = Field(default=None, ge=0)
    vat_rate: int | None = Field(default=None, ge=0, le=100)
    warranty_months: int | None = Field(default=None, ge=0, le=120)
    track_serial: bool | None = None
    min_stock: int | None = Field(default=None, ge=0)
    description: str | None = None
    status: ProductStatus | None = None


class StockAdjustIn(BaseModel):
    new_stock: int = Field(ge=0)
    note: str = Field(min_length=1, max_length=255)


class ProductOut(ORM):
    id: int
    code: str
    barcode: str | None = None
    name: str
    category_id: int | None
    category_name: str | None = None
    brand: str | None = None
    sale_price: int
    cost_price: int
    vat_rate: int = 10
    warranty_months: int = 12
    track_serial: bool = False
    stock: int
    min_stock: int
    description: str | None
    image_url: str | None = None
    status: str


class SerialUpdateIn(BaseModel):
    serial_no: str | None = Field(default=None, min_length=5, max_length=50)
    status: Literal["in_stock", "defective"] | None = None
    note: str | None = Field(default=None, max_length=255)


# ---------- Customer ----------
class CustomerIn(BaseModel):
    code: str | None = Field(default=None, max_length=30)
    name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = None
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
    created_at: datetime


# ---------- Invoice ----------
class InvoiceItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: int | None = Field(default=None, ge=0)  # bỏ trống => lấy giá bán hiện tại


class InvoiceIn(BaseModel):
    customer_id: int | None = None
    items: list[InvoiceItemIn] = Field(min_length=1)
    discount: int = Field(default=0, ge=0)
    discount_percent: float | None = Field(default=None, ge=0, le=100)
    payment_method: PaymentMethod = "cash"
    cash_received: int | None = Field(default=None, ge=0)  # chỉ dùng với tiền mặt
    payment_ref: str | None = Field(default=None, max_length=50)  # nội dung CK / mã giao dịch POS
    note: str | None = None


class InvoiceCancelIn(BaseModel):
    reason: str = Field(min_length=1, max_length=255)


class InvoiceItemOut(ORM):
    product_id: int
    product_code: str
    product_name: str
    quantity: int
    unit_price: int
    line_total: int


class InvoiceOut(ORM):
    id: int
    code: str
    customer_id: int | None
    customer_name: str | None
    user_name: str
    created_at: datetime
    subtotal: int
    discount: int
    total: int
    payment_method: str
    status: str
    note: str | None
    cancel_reason: str | None
    items: list[InvoiceItemOut] = []


# ---------- Import ----------
class NewProductIn(BaseModel):
    """Sản phẩm chưa có trong danh mục: tạo luôn khi lưu phiếu nhập."""
    name: str = Field(min_length=1, max_length=200)
    code: str | None = Field(default=None, max_length=30)  # bỏ trống => tự sinh SP0001, SP0002...
    category_id: int | None = None
    sale_price: SalePrice
    min_stock: int = Field(default=5, ge=0)
    track_serial: bool = False
    description: str | None = None


class _OneProduct(BaseModel):
    product_id: int | None = None
    new_product: NewProductIn | None = None
    serials: list[str] = Field(default_factory=list, max_length=9999)  # sản phẩm theo serial: đủ số lượng

    @model_validator(mode="after")
    def one_product(self):
        if (self.product_id is None) == (self.new_product is None):
            raise ValueError("Mỗi dòng cần chọn sản phẩm có sẵn (product_id) hoặc nhập sản phẩm mới (new_product)")
        return self


class ImportItemIn(_OneProduct):
    quantity: ImportAmount
    unit_cost: ImportAmount


class ImportIn(BaseModel):
    supplier: str | None = None
    supplier_id: int | None = None
    note: str | None = None
    items: list[ImportItemIn] = Field(min_length=1)


class PurchaseItemIn(_OneProduct):
    quantity: Annotated[int, Field(le=9999), _positive("Số lượng và giá nhập phải lớn hơn 0")]
    # Bỏ trống khi lập nháp (nhân viên không thấy giá nhập); bắt buộc lớn hơn 0 khi xác nhận nhập kho
    unit_cost: Annotated[int | None, Field(default=None, ge=1, le=2_000_000_000)] = None


class PurchaseOrderIn(BaseModel):
    supplier_id: int | None = None
    supplier_name: str | None = Field(default=None, max_length=150)  # chỉ dùng cho /api/imports kiểu cũ
    note: str | None = Field(default=None, max_length=255)
    items: list[PurchaseItemIn] = Field(min_length=1)
    confirm: bool = False  # True: lưu và xác nhận nhập kho ngay (chủ cửa hàng)


class CancelIn(BaseModel):
    reason: Reason


class SupplierIn(BaseModel):
    code: str | None = Field(default=None, max_length=20)  # bỏ trống => tự sinh NCC001...
    name: str = Field(min_length=1, max_length=150)
    contact_name: str | None = Field(default=None, max_length=100)
    phone: Annotated[str | None, AfterValidator(normalize_phone)] = None
    email: Annotated[str | None, AfterValidator(normalize_email)] = None
    address: str | None = Field(default=None, max_length=255)
    tax_code: str | None = Field(default=None, max_length=20)
    status: Literal["active", "inactive"] = "active"

    @field_validator("code")
    @classmethod
    def code_upper(cls, v: str | None):
        v = (v or "").strip().upper()
        if v and not re.fullmatch(r"[A-Z0-9\-]{2,20}", v):
            raise ValueError("Mã nhà cung cấp gồm chữ in hoa, số và dấu gạch ngang")
        return v or None


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


# ---------- Hệ thống ----------
class SettingsUpdateIn(BaseModel):
    values: dict[str, str | int | float | bool] = Field(min_length=1)


class TierIn(BaseModel):
    id: int
    min_total_spent: int = Field(ge=0, le=2_000_000_000)
    points_multiplier: float = Field(ge=0, le=10)


class TiersIn(BaseModel):
    tiers: list[TierIn] = Field(min_length=1)
