"""Tạo dữ liệu mẫu: 3 vai trò người dùng, nhóm hàng, sản phẩm, khách hàng, phiếu nhập,
và ~4 tháng hóa đơn (dùng đúng service nghiệp vụ để tồn kho luôn khớp).

Chạy:  python -m scripts.seed          (xóa và tạo lại toàn bộ dữ liệu)
"""
import random
import sys
from datetime import date, datetime, time, timedelta

from app.database import Base, SessionLocal, engine
from app.models import Category, Customer, Product, User
from app.schemas import ImportIn, ImportItemIn, InvoiceIn, InvoiceItemIn
from app.security import hash_password
from app.services import inventory

USERS = [
    ("admin", "Quản trị viên", "admin123", "admin"),
    ("owner", "Chủ cửa hàng", "owner123", "owner"),
    ("staff", "Nhân viên bán hàng", "staff123", "staff"),
    ("staff2", "Nhân viên bán hàng 2", "staff123", "staff"),
]

CATEGORIES = [
    ("Phụ kiện", "Tai nghe, sạc, cáp, ốp lưng"),
    ("Điện thoại", "Điện thoại thông minh"),
    ("Âm thanh", "Loa, tai nghe cao cấp"),
    ("Máy tính", "Laptop, chuột, bàn phím"),
    ("Gia dụng", "Đồ gia dụng thông minh"),
]

# code, name, category, sale, cost, popularity(1-10), min_stock, description
PRODUCTS = [
    ("PK001", "Tai nghe Bluetooth A1", "Phụ kiện", 350_000, 220_000, 9, 5, "Pin 20 giờ, kết nối Bluetooth 5.3, chống nước IPX4"),
    ("PK002", "Tai nghe Bluetooth A2 Pro", "Phụ kiện", 490_000, 310_000, 6, 5, "Pin 30 giờ, chống ồn chủ động ANC, sạc nhanh USB-C"),
    ("PK003", "Tai nghe có dây C10", "Phụ kiện", 120_000, 60_000, 3, 5, "Jack 3.5mm, có micro đàm thoại"),
    ("PK004", "Tai nghe Bluetooth Sport S5", "Phụ kiện", 450_000, 280_000, 5, 5, "Pin 40 giờ, móc tai thể thao, chống mồ hôi IPX5"),
    ("PK005", "Sạc nhanh 20W USB-C", "Phụ kiện", 190_000, 95_000, 10, 10, "Sạc nhanh PD 20W cho iPhone và Android"),
    ("PK006", "Cáp USB-C to Lightning 1m", "Phụ kiện", 150_000, 70_000, 8, 10, "Cáp bện dù, hỗ trợ sạc nhanh"),
    ("PK007", "Pin dự phòng 10000mAh", "Phụ kiện", 390_000, 240_000, 7, 5, "Sạc nhanh 22.5W, 2 cổng ra, nhỏ gọn"),
    ("PK008", "Ốp lưng silicon iPhone 15", "Phụ kiện", 90_000, 30_000, 4, 10, "Silicon mềm, chống sốc 4 góc"),
    ("PK009", "Pin dự phòng 20000mAh", "Phụ kiện", 590_000, 380_000, 2, 3, "Sạc nhanh 65W, sạc được laptop"),
    ("DT001", "Điện thoại Galaxy A15", "Điện thoại", 4_290_000, 3_600_000, 5, 3, "Màn 6.5 inch, pin 5000mAh, RAM 8GB"),
    ("DT002", "Điện thoại Redmi Note 13", "Điện thoại", 4_890_000, 4_100_000, 4, 3, "Camera 108MP, sạc nhanh 33W, pin 5000mAh"),
    ("DT003", "Điện thoại iPhone 13 128GB", "Điện thoại", 13_990_000, 12_500_000, 3, 2, "Chip A15, camera kép 12MP"),
    ("DT004", "Điện thoại Nokia 105", "Điện thoại", 590_000, 420_000, 1, 3, "Điện thoại phổ thông, pin 12 ngày"),
    ("AT001", "Loa Bluetooth Mini M1", "Âm thanh", 450_000, 270_000, 5, 5, "Pin 12 giờ, chống nước IPX7, nhỏ gọn"),
    ("AT002", "Loa Bluetooth Party P5", "Âm thanh", 1_890_000, 1_300_000, 2, 2, "Công suất 40W, đèn LED, pin 15 giờ"),
    ("AT003", "Tai nghe chụp tai Studio H9", "Âm thanh", 1_290_000, 850_000, 3, 3, "Chống ồn ANC, pin 50 giờ, đệm tai êm"),
    ("AT004", "Tai nghe True Wireless T3", "Âm thanh", 690_000, 450_000, 6, 5, "Pin 24 giờ kèm hộp sạc, chống ồn ENC khi gọi"),
    ("MT001", "Chuột không dây Logi M190", "Máy tính", 250_000, 150_000, 7, 5, "Kết nối USB 2.4GHz, pin 18 tháng"),
    ("MT002", "Bàn phím cơ K2", "Máy tính", 990_000, 650_000, 3, 3, "Switch đỏ, LED RGB, kết nối Bluetooth và dây"),
    ("MT003", "Laptop Vivobook 15", "Máy tính", 12_490_000, 11_000_000, 2, 2, "Core i5, RAM 16GB, SSD 512GB, màn 15.6 inch"),
    ("MT004", "Giá đỡ laptop nhôm", "Máy tính", 320_000, 180_000, 2, 3, "Nhôm nguyên khối, gập gọn, 6 mức cao"),
    ("MT005", "Webcam Full HD C920", "Máy tính", 890_000, 600_000, 1, 2, "1080p, micro kép, kẹp màn hình"),
    ("GD001", "Ổ cắm thông minh WiFi", "Gia dụng", 220_000, 120_000, 3, 5, "Điều khiển qua app, hẹn giờ, đo điện năng"),
    ("GD002", "Đèn bàn LED chống cận", "Gia dụng", 390_000, 230_000, 2, 3, "3 chế độ màu, cảm ứng, cổng sạc USB"),
    ("GD003", "Camera an ninh 2K", "Gia dụng", 690_000, 450_000, 3, 3, "Xoay 360 độ, đàm thoại 2 chiều, hồng ngoại"),
    ("GD004", "Quạt mini để bàn", "Gia dụng", 150_000, 80_000, 1, 5, "Sạc USB, 3 tốc độ, pin 6 giờ"),
]
# Các sản phẩm được đưa về tồn kho 0 để kiểm thử chatbot không tư vấn hàng hết
OUT_OF_STOCK = ["PK002", "AT003", "DT003"]
INACTIVE = ["DT004"]

CUSTOMERS = [
    ("Phạm Minh Anh", "0901234567", "vip"), ("Nguyễn Thu Hà", "0912345678", "regular"),
    ("Trần Quốc Bảo", "0987654321", "regular"), ("Lê Thị Mai", "0934567890", "vip"),
    ("Hoàng Văn Nam", "0976543210", "wholesale"), ("Vũ Thị Lan", "0945678901", "regular"),
    ("Đặng Hữu Phúc", "0967890123", "regular"), ("Bùi Ngọc Trâm", "0923456789", "vip"),
    ("Công ty TNHH Minh Phát", "0283456789", "wholesale"), ("Đỗ Thanh Tùng", "0956789012", "regular"),
    ("Ngô Bích Ngọc", "0918765432", "regular"), ("Phan Đức Huy", "0908765432", "regular"),
]

DAYS = 120


def run(seed: int = 42):
    rnd = random.Random(seed)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        users = {}
        for username, name, pw, role in USERS:
            users[username] = User(username=username, full_name=name, password_hash=hash_password(pw), role=role)
            db.add(users[username])
        cats = {n: Category(name=n, description=d) for n, d in CATEGORIES}
        db.add_all(cats.values())
        db.flush()

        products, weights = [], []
        for code, name, cat, sale, cost, pop, min_stock, desc in PRODUCTS:
            p = Product(code=code, name=name, category_id=cats[cat].id, sale_price=sale, cost_price=cost,
                        stock=0, min_stock=min_stock, description=desc,
                        image_url=f"/static/img/products/{code}.webp")
            db.add(p)
            products.append(p)
            weights.append(pop)
        for i, (name, phone, group) in enumerate(CUSTOMERS, 1):
            db.add(Customer(code=f"KH{i:04d}", name=name, phone=phone, group=group,
                            email=f"khach{i}@example.com", address="TP. Hồ Chí Minh"))
        db.flush()
        customers = db.query(Customer).all()

        start_day = date.today() - timedelta(days=DAYS)
        owner, staffs = users["owner"], [users["staff"], users["staff2"]]

        def import_goods(day: date, qty_factor: float, supplier: str):
            items = [ImportItemIn(product_id=p.id, quantity=max(2, int(w * qty_factor * rnd.uniform(0.8, 1.2))),
                                  unit_cost=p.cost_price) for p, w in zip(products, weights)]
            inventory.create_import(db, ImportIn(supplier=supplier, items=items, note="Nhập hàng định kỳ"),
                                    owner, at=datetime.combine(day, time(8, 0)))

        import_goods(start_day, 4, "Công ty Phân phối Điện tử Sài Gòn")

        for offset in range(1, DAYS + 1):
            day = start_day + timedelta(days=offset)
            if offset % 30 == 0:
                import_goods(day, 3, "Nhà cung cấp Hòa Bình")
            weekend = day.weekday() >= 5
            for _ in range(rnd.randint(2, 7) + (3 if weekend else 0)):
                at = datetime.combine(day, time(rnd.randint(8, 20), rnd.randint(0, 59)))
                if at > datetime.now():
                    continue
                picked = rnd.choices(products, weights=weights, k=rnd.choice([1, 1, 1, 2, 2, 3]))
                items = {}
                for p in picked:
                    if p.stock > items.get(p.id, 0):
                        items[p.id] = items.get(p.id, 0) + 1
                if not items:
                    continue
                customer = rnd.choice(customers) if rnd.random() < 0.6 else None
                subtotal = sum(next(p for p in products if p.id == pid).sale_price * q for pid, q in items.items())
                discount = 0
                if customer and customer.group == "vip":
                    discount = round(subtotal * 0.05)
                elif customer and customer.group == "wholesale":
                    discount = round(subtotal * 0.08)
                data = InvoiceIn(
                    customer_id=customer.id if customer else None,
                    items=[InvoiceItemIn(product_id=pid, quantity=q) for pid, q in items.items()],
                    discount=discount, payment_method=rnd.choice(["cash", "cash", "transfer", "card", "qr"]),
                )
                if data.payment_method == "cash":
                    total = subtotal - discount
                    data.cash_received = -(-total // 50_000) * 50_000  # làm tròn lên bội số 50.000
                elif data.payment_method == "card":
                    data.payment_ref = f"POS{rnd.randint(100000, 999999)}"
                else:
                    data.payment_ref = f"SALESAI {at:%y%m%d%H%M}{rnd.randint(10, 99)}"
                inv = inventory.create_invoice(db, data, rnd.choice(staffs), at=at)
                if rnd.random() < 0.02:
                    inventory.cancel_invoice(db, inv, "Khách đổi ý", owner)

        by_code = {p.code: p for p in products}
        for code in OUT_OF_STOCK:
            inventory.adjust_stock(db, by_code[code], 0, "Kiểm kê: hàng hết / lỗi trả nhà cung cấp", owner)
        for code in INACTIVE:
            by_code[code].status = "inactive"
        db.commit()
        print(f"Đã tạo dữ liệu mẫu: {len(products)} sản phẩm, {len(customers)} khách hàng, {DAYS} ngày bán hàng.")
        print("Tài khoản: admin/admin123, owner/owner123, staff/staff123")
    finally:
        db.close()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252
    run()
