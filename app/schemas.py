from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Role = Literal["admin", "owner", "staff"]
PaymentMethod = Literal["cash", "transfer", "card", "qr"]
CustomerGroup = Literal["regular", "vip", "wholesale"]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Auth / User ----------
class LoginIn(BaseModel):
    username: str
    password: str


class UserOut(ORM):
    id: int
    username: str
    full_name: str
    role: Role
    is_active: bool


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=6)
    role: Role = "staff"


class ForgotPasswordIn(BaseModel):
    username: str = Field(min_length=1, max_length=50)


class ResetPasswordIn(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    code: str = Field(min_length=1, max_length=12)
    new_password: str = Field(min_length=6, max_length=128)


class UserUpdate(BaseModel):
    full_name: str | None = None
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
    sale_price: int = Field(ge=0)
    cost_price: int = Field(ge=0, default=0)
    stock: int = Field(ge=0, default=0)
    min_stock: int = Field(ge=0, default=5)
    description: str | None = None
    status: Literal["active", "inactive"] = "active"


class ProductUpdate(BaseModel):
    """Không cho sửa trực tiếp tồn kho ở đây: tồn kho thay đổi qua hóa đơn, phiếu nhập hoặc điều chỉnh kho."""
    code: str | None = Field(default=None, min_length=1, max_length=30)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category_id: int | None = None
    category_name: str | None = Field(default=None, max_length=100)  # như ProductIn.category_name
    sale_price: int | None = Field(default=None, ge=0)
    cost_price: int | None = Field(default=None, ge=0)
    min_stock: int | None = Field(default=None, ge=0)
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
    description: str | None
    image_url: str | None = None
    status: str


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
            v = v.strip().replace(" ", "")
            if not v.lstrip("+").isdigit() or not 8 <= len(v.lstrip("+")) <= 15:
                raise ValueError("Số điện thoại không hợp lệ")
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
    sale_price: int = Field(ge=0)
    min_stock: int = Field(default=5, ge=0)
    description: str | None = None


class ImportItemIn(BaseModel):
    product_id: int | None = None
    new_product: NewProductIn | None = None
    quantity: int = Field(gt=0)
    unit_cost: int = Field(ge=0)

    @model_validator(mode="after")
    def one_product(self):
        if (self.product_id is None) == (self.new_product is None):
            raise ValueError("Mỗi dòng cần chọn sản phẩm có sẵn (product_id) hoặc nhập sản phẩm mới (new_product)")
        return self


class ImportIn(BaseModel):
    supplier: str | None = None
    note: str | None = None
    items: list[ImportItemIn] = Field(min_length=1)


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
