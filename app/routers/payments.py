from fastapi import APIRouter, Depends

from app.config import settings
from app.models import User
from app.schemas import VietQRIn
from app.security import ALL_STAFF
from app.services.qr import vietqr

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.get("/config")
def payment_config(_: User = Depends(ALL_STAFF)):
    return {
        "shop_name": settings.SHOP_NAME,
        "bank_name": settings.VIETQR_BANK_NAME,
        "account_no": settings.VIETQR_ACCOUNT_NO,
        "account_name": settings.VIETQR_ACCOUNT_NAME,
        "is_demo": settings.VIETQR_ACCOUNT_NO == "0123456789",
    }


@router.post("/vietqr")
def create_vietqr(data: VietQRIn, _: User = Depends(ALL_STAFF)):
    """Mã VietQR cho khách quét bằng app ngân hàng: đã điền sẵn số tài khoản, số tiền, nội dung."""
    return vietqr(data.amount, data.content)
