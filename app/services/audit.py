"""Ghi nhật ký hệ thống (bảng audit_logs). Không ghi mật khẩu, giá vốn, doanh thu: quản trị viên đọc được nhật ký này."""
from sqlalchemy.orm import Session

from app.models import AuditLog, User

ACTIONS = {
    "login": "Đăng nhập",
    "login_failed": "Đăng nhập thất bại",
    "logout": "Đăng xuất",
    "password_change": "Đổi mật khẩu",
    "password_reset": "Đặt lại mật khẩu qua email",
    "user_create": "Tạo tài khoản",
    "user_update": "Sửa tài khoản",
    "user_approve": "Duyệt tài khoản",
    "user_reject": "Từ chối tài khoản",
    "user_register": "Tự đăng ký tài khoản",
    "settings_update": "Đổi cấu hình kỹ thuật / AI",
    "business_update": "Đổi tham số kinh doanh",
    "backup": "Sao lưu dữ liệu",
    "restore": "Khôi phục dữ liệu",
    "invoice_cancel_request": "Yêu cầu hủy hóa đơn",
    "invoice_cancel": "Hủy hóa đơn",
    "invoice_cancel_reject": "Từ chối hủy hóa đơn",
    "import_confirm": "Xác nhận phiếu nhập",
    "import_cancel": "Hủy phiếu nhập",
    "price_change": "Đổi giá bán",
    "points_adjust": "Điều chỉnh điểm tích lũy",
    "stock_adjust": "Kiểm kê, điều chỉnh tồn kho",
}


def audit(db: Session, user: User | None, action: str, detail: str | None = None,
          username: str | None = None) -> None:
    """Thêm một dòng nhật ký vào phiên hiện tại; được lưu cùng lúc commit nghiệp vụ."""
    db.add(AuditLog(user_id=user.id if user else None, username=(user.username if user else username or "")[:50],
                    action=action, detail=(detail or "")[:500] or None))
