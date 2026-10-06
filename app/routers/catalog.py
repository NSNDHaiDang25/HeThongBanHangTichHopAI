import io
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from PIL import Image, ImageOps
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.models import Category, ImportItem, InvoiceItem, Product, ProductSerial, StockMovement, User
from app.schemas import (CategoryIn, CategoryOut, ProductIn, ProductOut, ProductUpdate, SerialsIn, SerialUpdate,
                         StockAdjustIn)
from app.security import ALL_STAFF, MANAGERS
from app.services.audit import audit
from app.services.inventory import BusinessError, add_serials, adjust_stock, change_stock
from app.services.qr import qr_svg

router = APIRouter(prefix="/api", tags=["catalog"])


# ---------------- Danh mục ----------------
@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db), _: User = Depends(ALL_STAFF)):
    return db.scalars(select(Category).order_by(Category.name)).all()


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(data: CategoryIn, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    cat = Category(**data.model_dump())
    db.add(cat)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, "Tên nhóm hàng đã tồn tại")
    return cat


@router.put("/categories/{cat_id}", response_model=CategoryOut)
def update_category(cat_id: int, data: CategoryIn, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    cat = db.get(Category, cat_id)
    if cat is None:
        raise HTTPException(404, "Không tìm thấy nhóm hàng")
    cat.name, cat.description = data.name, data.description
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, "Tên nhóm hàng đã tồn tại")
    return cat


@router.delete("/categories/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    cat = db.get(Category, cat_id)
    if cat is None:
        raise HTTPException(404, "Không tìm thấy nhóm hàng")
    if db.scalar(select(func.count(Product.id)).where(Product.category_id == cat_id)):
        raise HTTPException(400, "Nhóm hàng đang có sản phẩm, không thể xóa")
    db.delete(cat)
    db.commit()
    return {"ok": True}


# ---------------- Sản phẩm ----------------
def product_out(p: Product, user: User) -> dict:
    data = ProductOut.model_validate(p).model_dump()
    data["category_name"] = p.category.name if p.category else None
    if user.role != "owner":
        data["cost_price"] = None  # chỉ chủ cửa hàng xem giá nhập
    return data


@router.get("/products")
def list_products(
    q: str | None = None, category_id: int | None = None,
    status: str | None = Query(None, pattern="^(active|inactive)$"),
    stock: str | None = Query(None, pattern="^(in|out|low)$"),
    page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db), user: User = Depends(ALL_STAFF),
):
    stmt = select(Product).options(joinedload(Product.category))
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Product.name.ilike(like), Product.code.ilike(like)))
    if category_id:
        stmt = stmt.where(Product.category_id == category_id)
    if status:
        stmt = stmt.where(Product.status == status)
    if stock == "in":
        stmt = stmt.where(Product.stock > 0)
    elif stock == "out":
        stmt = stmt.where(Product.stock == 0)
    elif stock == "low":
        stmt = stmt.where(Product.stock <= Product.min_stock)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(Product.code).offset((page - 1) * size).limit(size)).all()
    return {"items": [product_out(p, user) for p in rows], "total": total, "page": page, "size": size}


@router.get("/products/by-code/{code}")
def get_product_by_code(code: str, db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    """Tra sản phẩm theo mã, dùng khi quét QR / mã vạch ở màn hình bán hàng.
    Quét đúng serial / IMEI của một máy còn trong kho: trả về sản phẩm kèm serial đó để thêm thẳng vào giỏ."""
    key = code.strip().upper()
    p = db.scalar(select(Product).where(func.upper(Product.code) == key))
    if p is not None:
        return product_out(p, user)
    s = db.scalar(select(ProductSerial).where(ProductSerial.serial == key))
    if s is None:
        raise HTTPException(404, f"Không tìm thấy sản phẩm có mã '{code.strip()}'")
    if s.status != "in_stock":
        raise HTTPException(400, f"Serial / IMEI '{s.serial}' không còn trong kho ({SERIAL_STATUS[s.status]})")
    return {**product_out(s.product, user), "serial": s.serial}


@router.get("/products/qr-labels")
def product_qr_labels(ids: str | None = None, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    """Tem QR để in dán lên sản phẩm. Mã QR chứa đúng mã sản phẩm (VD: PK001)."""
    stmt = select(Product).where(Product.status == "active").order_by(Product.code)
    if ids:
        try:
            id_list = [int(x) for x in ids.split(",") if x.strip()]
        except ValueError:
            raise HTTPException(400, "Danh sách id không hợp lệ")
        stmt = stmt.where(Product.id.in_(id_list))
    return [{"id": p.id, "code": p.code, "name": p.name, "price": p.sale_price, "svg": qr_svg(p.code)}
            for p in db.scalars(stmt)]


@router.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    p = db.get(Product, product_id)
    if p is None:
        raise HTTPException(404, "Không tìm thấy sản phẩm")
    return product_out(p, user)


def _category_id_by_name(db: Session, name: str) -> int | None:
    """Tìm nhóm hàng theo tên (không phân biệt hoa thường, khoảng trắng thừa), chưa có thì tạo mới.
    So khớp bằng Python vì lower() của SQLite không xử lý chữ có dấu tiếng Việt."""
    name = " ".join(name.split())
    if not name:
        return None
    cat = next((c for c in db.scalars(select(Category)) if c.name.casefold() == name.casefold()), None)
    if cat is None:
        cat = Category(name=name)
        db.add(cat)
        db.flush()
    return cat.id


@router.post("/products", status_code=201)
def create_product(data: ProductIn, db: Session = Depends(get_db), user: User = Depends(MANAGERS)):
    fields = data.model_dump(exclude={"stock", "category_name"})
    if data.category_name is not None:
        fields["category_id"] = _category_id_by_name(db, data.category_name)
    elif data.category_id and db.get(Category, data.category_id) is None:
        raise HTTPException(400, "Nhóm hàng không tồn tại")
    initial_stock = data.stock
    p = Product(**fields, stock=0)
    db.add(p)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, "Mã sản phẩm đã tồn tại")
    if initial_stock:
        change_stock(db, p, initial_stock, "adjust", None, user, note="Tồn kho đầu kỳ")
    db.commit()
    db.refresh(p)
    return product_out(p, user)


@router.put("/products/{product_id}")
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db),
                   user: User = Depends(MANAGERS)):
    p = db.get(Product, product_id)
    if p is None:
        raise HTTPException(404, "Không tìm thấy sản phẩm")
    changes = data.model_dump(exclude_unset=True)
    if "category_name" in changes:
        changes["category_id"] = _category_id_by_name(db, changes.pop("category_name") or "")
    elif changes.get("category_id") and db.get(Category, changes["category_id"]) is None:
        raise HTTPException(400, "Nhóm hàng không tồn tại")
    if "sale_price" in changes and changes["sale_price"] != p.sale_price:
        audit(db, user, "price_change", f"{p.code}: {p.sale_price:,} -> {changes['sale_price']:,} ₫".replace(",", "."))
    for k, v in changes.items():
        setattr(p, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, "Mã sản phẩm đã tồn tại")
    return product_out(p, user)


@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    p = db.get(Product, product_id)
    if p is None:
        raise HTTPException(404, "Không tìm thấy sản phẩm")
    if (db.scalar(select(func.count(InvoiceItem.id)).where(InvoiceItem.product_id == product_id))
            or db.scalar(select(func.count(ImportItem.id)).where(ImportItem.product_id == product_id))):
        # Đã có trong hóa đơn hoặc phiếu nhập: chỉ ngừng kinh doanh để giữ lịch sử chứng từ
        p.status = "inactive"
        db.commit()
        return {"ok": True, "message": "Sản phẩm đã có trong hóa đơn hoặc phiếu nhập nên không thể xóa, "
                                       "đã chuyển sang ngừng kinh doanh"}
    db.query(StockMovement).filter(StockMovement.product_id == product_id).delete()
    db.query(ProductSerial).filter(ProductSerial.product_id == product_id).delete()
    _remove_upload(p.image_url)
    db.delete(p)
    db.commit()
    return {"ok": True, "message": "Đã xóa sản phẩm"}


@router.post("/products/{product_id}/adjust-stock")
def adjust_product_stock(product_id: int, data: StockAdjustIn, db: Session = Depends(get_db),
                         user: User = Depends(MANAGERS)):
    p = db.get(Product, product_id)
    if p is None:
        raise HTTPException(404, "Không tìm thấy sản phẩm")
    old = p.stock
    try:
        adjust_stock(db, p, data.new_stock, data.note, user)
    except BusinessError as e:
        db.rollback()
        raise HTTPException(400, str(e))
    if old != p.stock:
        audit(db, user, "stock_adjust", f"{p.code}: {old} -> {p.stock} ({data.note})")
    db.commit()
    return product_out(p, user)


# ---------------- Serial / IMEI ----------------
SERIAL_STATUS = {"in_stock": "Trong kho", "sold": "Đã bán", "defective": "Hàng lỗi"}


def serial_out(s: ProductSerial) -> dict:
    inv = s.invoice
    return {"id": s.id, "serial": s.serial, "status": s.status, "status_label": SERIAL_STATUS.get(s.status, s.status),
            "product_id": s.product_id, "product_code": s.product.code, "product_name": s.product.name,
            "invoice_id": inv.id if inv else None, "invoice_code": inv.code if inv else None,
            "sold_at": s.sold_at, "note": s.note, "created_at": s.created_at}


@router.get("/serials")
def list_serials(q: str | None = None, product_id: int | None = None,
                 status: str | None = Query(None, pattern="^(in_stock|sold|defective)$"),
                 page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=500),
                 db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    stmt = select(ProductSerial).options(joinedload(ProductSerial.product), joinedload(ProductSerial.invoice))
    if q:
        stmt = stmt.where(ProductSerial.serial.ilike(f"%{q.strip()}%"))
    if product_id:
        stmt = stmt.where(ProductSerial.product_id == product_id)
    if status:
        stmt = stmt.where(ProductSerial.status == status)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(ProductSerial.id.desc()).offset((page - 1) * size).limit(size)).all()
    return {"total": total, "items": [serial_out(s) for s in rows]}


@router.get("/products/{product_id}/serials")
def available_serials(product_id: int, db: Session = Depends(get_db), _: User = Depends(ALL_STAFF)):
    """Serial / IMEI còn trong kho của một sản phẩm: thu ngân chọn khi bán."""
    return list(db.scalars(select(ProductSerial.serial).where(ProductSerial.product_id == product_id,
                                                               ProductSerial.status == "in_stock")
                           .order_by(ProductSerial.serial)))


@router.post("/serials", status_code=201)
def create_serials(data: SerialsIn, db: Session = Depends(get_db), user: User = Depends(MANAGERS)):
    """Khai báo serial cho hàng đang có trong kho (VD: vừa bật quản lý serial cho sản phẩm đã có tồn)."""
    p = db.get(Product, data.product_id)
    if p is None:
        raise HTTPException(404, "Không tìm thấy sản phẩm")
    if not p.track_serial:
        raise HTTPException(400, f"Sản phẩm '{p.name}' chưa bật quản lý theo serial / IMEI")
    in_stock = db.scalar(select(func.count(ProductSerial.id)).where(ProductSerial.product_id == p.id,
                                                                    ProductSerial.status == "in_stock"))
    if in_stock + len(data.serials) > p.stock:
        raise HTTPException(400, f"Tồn kho '{p.name}' là {p.stock}, đã có {in_stock} serial: chỉ thêm được "
                                 f"{max(0, p.stock - in_stock)} serial. Hàng mới về hãy nhập qua phiếu nhập")
    try:
        add_serials(db, p, data.serials, note=data.note)
    except BusinessError as e:
        db.rollback()
        raise HTTPException(400, str(e))
    db.commit()
    return {"ok": True, "message": f"Đã thêm {len(data.serials)} serial cho {p.name}"}


@router.put("/serials/{serial_id}")
def update_serial(serial_id: int, data: SerialUpdate, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    s = db.get(ProductSerial, serial_id)
    if s is None:
        raise HTTPException(404, "Không tìm thấy serial")
    if data.status and data.status != s.status:
        if s.status == "sold":
            raise HTTPException(400, "Serial đã bán: đổi trạng thái qua đổi trả hàng")
        s.status = data.status
    if data.note is not None:
        s.note = data.note.strip() or None
    db.commit()
    return serial_out(s)


@router.delete("/serials/{serial_id}")
def delete_serial(serial_id: int, db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    """Xóa serial khai báo nhầm (chỉ máy chưa bán)."""
    s = db.get(ProductSerial, serial_id)
    if s is None:
        raise HTTPException(404, "Không tìm thấy serial")
    if s.status == "sold" or s.invoice_id:
        raise HTTPException(400, "Không xóa được serial đã bán")
    db.delete(s)
    db.commit()
    return {"ok": True}


@router.get("/stock-movements")
def list_movements(product_id: int | None = None, type: str | None = None,
                   page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=200),
                   db: Session = Depends(get_db), _: User = Depends(MANAGERS)):
    stmt = select(StockMovement).options(joinedload(StockMovement.product))
    if product_id:
        stmt = stmt.where(StockMovement.product_id == product_id)
    if type:
        stmt = stmt.where(StockMovement.type == type)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(StockMovement.id.desc()).offset((page - 1) * size).limit(size)).all()
    return {"total": total, "items": [{
        "id": m.id, "product_code": m.product.code, "product_name": m.product.name, "change": m.change,
        "stock_after": m.stock_after, "type": m.type, "ref_code": m.ref_code, "note": m.note,
        "created_at": m.created_at,
    } for m in rows]}


# ---------------- Ảnh sản phẩm ----------------
MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "GIF"}
Image.MAX_IMAGE_PIXELS = 40_000_000  # chặn ảnh "bom giải nén"


def _upload_dir() -> Path:
    path = settings.UPLOAD_DIR / "products"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _remove_upload(url: str | None) -> None:
    """Chỉ xóa ảnh do người dùng tải lên (/uploads/...), không xóa ảnh mẫu trong /static."""
    if url and url.startswith("/uploads/products/"):
        (_upload_dir() / Path(url).name).unlink(missing_ok=True)


@router.post("/products/{product_id}/image")
def upload_product_image(product_id: int, file: UploadFile = File(...), db: Session = Depends(get_db),
                         user: User = Depends(MANAGERS)):
    p = db.get(Product, product_id)
    if p is None:
        raise HTTPException(404, "Không tìm thấy sản phẩm")
    raw = file.file.read(MAX_IMAGE_BYTES + 1)
    if len(raw) > MAX_IMAGE_BYTES:
        raise HTTPException(400, "Ảnh vượt quá 5 MB")
    try:
        with Image.open(io.BytesIO(raw)) as probe:
            probe.verify()
        img = Image.open(io.BytesIO(raw))
        if img.format not in ALLOWED_FORMATS:
            raise ValueError
        img = ImageOps.exif_transpose(img)
        img.thumbnail((800, 800))
        img = img.convert("RGBA" if img.mode in ("RGBA", "LA", "P") else "RGB")
    except Exception:
        raise HTTPException(400, "File không phải ảnh hợp lệ (chấp nhận JPG, PNG, WEBP, GIF)")
    # Lưu lại dưới dạng WEBP: đồng nhất định dạng, nhẹ, loại bỏ metadata/EXIF của file gốc
    name = f"{uuid.uuid4().hex}.webp"
    img.save(_upload_dir() / name, "WEBP", quality=85)
    _remove_upload(p.image_url)
    p.image_url = f"/uploads/products/{name}"
    db.commit()
    return product_out(p, user)


@router.delete("/products/{product_id}/image")
def delete_product_image(product_id: int, db: Session = Depends(get_db), user: User = Depends(MANAGERS)):
    p = db.get(Product, product_id)
    if p is None:
        raise HTTPException(404, "Không tìm thấy sản phẩm")
    _remove_upload(p.image_url)
    p.image_url = None
    db.commit()
    return product_out(p, user)
