"""Tạo dữ liệu mẫu: 3 vai trò người dùng (độc lập), nhóm hàng, sản phẩm (điện thoại, laptop quản lý theo IMEI / serial),
nhà cung cấp, khách hàng, hạng thành viên, khuyến mãi / voucher, phiếu nhập, ~4 tháng hóa đơn (dùng đúng service
nghiệp vụ để tồn kho, serial, điểm tích lũy luôn khớp) và vài chứng từ mẫu cho đổi trả, bảo hành, duyệt hủy, phiếu nháp.

Chạy:  python -m scripts.seed          (xóa và tạo lại toàn bộ dữ liệu)
"""
import random
import sys
from datetime import date, datetime, time, timedelta

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Category, Customer, CustomerTier, Invoice, Product, ProductSerial, Promotion, Supplier, User, now
from app.schemas import (ImportDraftIn, ImportDraftItemIn, ImportIn, ImportItemIn, InvoiceIn, InvoiceItemIn, ReturnIn,
                         ReturnItemIn, WarrantyIn, WarrantyUpdate)
from app.security import hash_password
from app.services import aftersales, inventory

USERS = [
    ("admin", "Quản trị viên", "admin123", "admin"),
    ("owner", "Chủ cửa hàng", "owner123", "owner"),
    ("staff", "Thu ngân", "staff123", "staff"),
    ("staff2", "Thu ngân 2", "staff123", "staff"),
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



# Bảo hành theo nhóm hàng (tháng); laptop bảo hành 24 tháng
WARRANTY = {"Phụ kiện": 6, "Điện thoại": 12, "Âm thanh": 12, "Máy tính": 12, "Gia dụng": 12}
WARRANTY_OVERRIDE = {"MT003": 24, "PK006": 3, "PK008": 0}
# Hàng giá trị cao quản lý theo từng máy: nhập kho ghi IMEI / serial, bán phải chọn đúng máy
SERIAL_PRODUCTS = {"DT001", "DT002", "DT003", "DT004", "MT003"}

SUPPLIERS = [
    ("Công ty Phân phối Điện tử Sài Gòn", "02838123456", "sales@pp-saigon.example", "Quận 10, TP. Hồ Chí Minh"),
    ("Nhà cung cấp Hòa Bình", "02439876543", "lienhe@hoabinh.example", "Cầu Giấy, Hà Nội"),
    ("Digiworld Phụ kiện", "02873005588", None, "Quận 1, TP. Hồ Chí Minh"),
]

TIERS = [("Thành viên", 0, 0), ("Bạc", 5_000_000, 2), ("Vàng", 15_000_000, 3), ("Kim cương", 40_000_000, 5)]


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
        suppliers = [Supplier(code=f"NCC{i:03d}", name=name, phone=phone, email=email, address=address)
                     for i, (name, phone, email, address) in enumerate(SUPPLIERS, 1)]
        db.add_all(suppliers)
        db.flush()

        products, weights = [], []
        for code, name, cat, sale, cost, pop, min_stock, desc in PRODUCTS:
            p = Product(code=code, name=name, category_id=cats[cat].id, sale_price=sale, cost_price=cost,
                        stock=0, min_stock=min_stock, description=desc, image_url=f"/static/img/products/{code}.webp",
                        warranty_months=WARRANTY_OVERRIDE.get(code, WARRANTY[cat]), track_serial=code in SERIAL_PRODUCTS)
            db.add(p)
            products.append(p)
            weights.append(pop)
        for i, (name, phone, group) in enumerate(CUSTOMERS, 1):
            db.add(Customer(code=f"KH{i:04d}", name=name, phone=phone, group=group,
                            email=f"khach{i}@example.com", address="TP. Hồ Chí Minh"))
        db.flush()
        customers = db.query(Customer).all()
        by_id = {p.id: p for p in products}

        start_day = now().date() - timedelta(days=DAYS)
        owner, staffs = users["owner"], [users["staff"], users["staff2"]]

        def new_serials(p: Product, qty: int) -> list[str] | None:
            if not p.track_serial:
                return None
            if p.code.startswith("DT"):
                return [f"35{rnd.randint(10 ** 12, 10 ** 13 - 1)}" for _ in range(qty)]  # IMEI 15 số
            return [f"SN{p.code}{rnd.randint(10 ** 7, 10 ** 8 - 1)}" for _ in range(qty)]

        def in_stock_serials(p: Product, qty: int) -> list[str] | None:
            if not p.track_serial:
                return None
            return list(db.scalars(select(ProductSerial.serial).where(ProductSerial.product_id == p.id,
                                                                      ProductSerial.status == "in_stock")
                                   .order_by(ProductSerial.id).limit(qty)))

        def import_goods(day: date, qty_factor: float, supplier: Supplier):
            items = []
            for p, w in zip(products, weights):
                qty = max(2, int(w * qty_factor * rnd.uniform(0.8, 1.2)))
                items.append(ImportItemIn(product_id=p.id, quantity=qty, unit_cost=p.cost_price,
                                          serials=new_serials(p, qty)))
            inventory.create_import(db, ImportIn(supplier_id=supplier.id, items=items, note="Nhập hàng định kỳ"),
                                    owner, at=datetime.combine(day, time(8, 0)))

        import_goods(start_day, 4, suppliers[0])

        for offset in range(1, DAYS + 1):
            day = start_day + timedelta(days=offset)
            if offset % 30 == 0:
                import_goods(day, 3, suppliers[1])
            weekend = day.weekday() >= 5
            for _ in range(rnd.randint(2, 7) + (3 if weekend else 0)):
                at = datetime.combine(day, time(rnd.randint(8, 20), rnd.randint(0, 59)))
                if at > now():
                    continue
                picked = rnd.choices(products, weights=weights, k=rnd.choice([1, 1, 1, 2, 2, 3]))
                items = {}
                for p in picked:
                    if p.stock > items.get(p.id, 0):
                        items[p.id] = items.get(p.id, 0) + 1
                if not items:
                    continue
                customer = rnd.choice(customers) if rnd.random() < 0.6 else None
                subtotal = sum(by_id[pid].sale_price * q for pid, q in items.items())
                discount = 0
                if customer and customer.group == "vip":
                    discount = round(subtotal * 0.05)
                elif customer and customer.group == "wholesale":
                    discount = round(subtotal * 0.08)
                data = InvoiceIn(
                    customer_id=customer.id if customer else None,
                    items=[InvoiceItemIn(product_id=pid, quantity=q, serials=in_stock_serials(by_id[pid], q))
                           for pid, q in items.items()],
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
            for s in db.scalars(select(ProductSerial).where(ProductSerial.product_id == by_code[code].id,
                                                            ProductSerial.status == "in_stock")):
                s.status, s.note = "defective", "Lỗi, trả nhà cung cấp"
        for code in INACTIVE:
            by_code[code].status = "inactive"

        # Hạng thành viên, khuyến mãi, voucher
        db.add_all(CustomerTier(name=n, min_spent=m, discount_percent=d) for n, m, d in TIERS)
        today = now().date()
        db.add_all([
            Promotion(name="Giảm 5% đơn từ 2 triệu", discount_type="percent", value=5, max_discount=300_000,
                      min_subtotal=2_000_000, start_date=today - timedelta(days=10), end_date=today + timedelta(days=20),
                      note="Áp dụng mọi khách hàng"),
            Promotion(name="Giảm 20.000 ₫ đơn từ 300.000 ₫", discount_type="amount", value=20_000,
                      min_subtotal=300_000, start_date=today - timedelta(days=3), end_date=today + timedelta(days=30)),
            Promotion(name="Voucher khai trương 50.000 ₫", code="KHAITRUONG50", discount_type="amount", value=50_000,
                      min_subtotal=500_000, usage_limit=100, start_date=today - timedelta(days=5),
                      end_date=today + timedelta(days=60), note="Phát tờ rơi, dùng chung 100 lượt"),
            Promotion(name="Black Friday giảm 10%", discount_type="percent", value=10, max_discount=500_000,
                      start_date=today - timedelta(days=60), end_date=today - timedelta(days=50)),
        ])
        db.flush()

        # Chứng từ mẫu cho các luồng nghiệp vụ: hóa đơn tạm, yêu cầu hủy, đổi trả, bảo hành, phiếu nhập nháp
        staff = users["staff"]
        pk = by_code["PK005"]
        inventory.create_invoice(db, InvoiceIn(items=[InvoiceItemIn(product_id=pk.id, quantity=2)], pay=False,
                                               note="Khách giữ hàng, chiều quay lại lấy"), staff)
        recent = db.scalars(select(Invoice).where(Invoice.status == "paid", Invoice.user_id == staff.id)
                            .order_by(Invoice.created_at.desc())).all()
        if recent:
            inventory.request_cancel(db, recent[0], "Khách đổi ý ngay sau khi thanh toán", staff)
        returnable = next((i for i in recent[1:6] if aftersales.invoice_lookup(db, i)["can_return"]), None)
        if returnable:
            it = returnable.items[0]
            serials = it.serials[:1] if it.serials else None
            aftersales.create_return(db, ReturnIn(invoice_id=returnable.id, reason="Khách không vừa ý", items=[
                ReturnItemIn(product_id=it.product_id, quantity=1, serials=serials)]), staff)
        sold = db.scalars(select(ProductSerial).where(ProductSerial.status == "sold")
                          .order_by(ProductSerial.sold_at.desc()).limit(3)).all()
        issues = ["Máy sập nguồn liên tục", "Loa ngoài rè khi nghe nhạc", "Màn hình xuất hiện sọc"]
        for i, s in enumerate(sold):
            t = aftersales.create_ticket(db, WarrantyIn(invoice_id=s.invoice_id, product_id=s.product_id,
                                                        serial=s.serial, issue=issues[i]), staff)
            if i >= 1:
                aftersales.update_ticket(db, t, WarrantyUpdate(status="processing",
                                                               note="Đã gửi trung tâm bảo hành của hãng"), owner)
            if i == 2:
                aftersales.update_ticket(db, t, WarrantyUpdate(status="done", note="Đã thay màn hình, trả khách"), owner)
        low = [p for p in products if p.status == "active" and not p.track_serial and p.stock <= p.min_stock][:2]
        inventory.create_import_draft(db, ImportDraftIn(
            supplier_id=suppliers[2].id, note="Hàng về, chờ chủ cửa hàng kiểm và xác nhận",
            items=[ImportDraftItemIn(product_id=p.id, quantity=10) for p in low or [by_code["PK001"]]]), staff)
        db.commit()
        print(f"Đã tạo dữ liệu mẫu: {len(products)} sản phẩm, {len(customers)} khách hàng, {DAYS} ngày bán hàng.")
        print("Tài khoản: admin/admin123 (quản trị viên), owner/owner123 (chủ cửa hàng), staff/staff123 (thu ngân)")
    finally:
        db.close()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252
    run()
