from fastapi import APIRouter, Depends

from app.config import settings
from app.models import User
from app.schemas import VietQRIn
from app.security import ALL_STAFF
from app.services.qr import vietqr

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.get("/config")
def payment_config(_: User = Depends(ALL_STAFF)):
    """Thông tin cửa hàng, tài khoản nhận tiền và tham số bán hàng cho màn hình bán hàng / in hóa đơn."""
    return {
        "shop_name": settings.SHOP_NAME,
        "shop_address": settings.SHOP_ADDRESS,
        "shop_phone": settings.SHOP_PHONE,
        "bank_name": settings.VIETQR_BANK_NAME,
        "account_no": settings.VIETQR_ACCOUNT_NO,
        "account_name": settings.VIETQR_ACCOUNT_NAME,
        "is_demo": settings.VIETQR_ACCOUNT_NO == "0123456789",
        "point_value": settings.POINT_VALUE,
        "points_earn_amount": settings.POINTS_EARN_AMOUNT,
        "points_max_percent": settings.POINTS_MAX_PERCENT,
        "return_hours": settings.RETURN_HOURS,
    }


@router.post("/vietqr")
def create_vietqr(data: VietQRIn, _: User = Depends(ALL_STAFF)):
    """Mã VietQR cho khách quét bằng app ngân hàng: đã điền sẵn số tài khoản, số tiền, nội dung."""
    return vietqr(data.amount, data.content)
