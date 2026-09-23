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
from app.models import Category, InvoiceItem, Product, StockMovement, User
from app.schemas import CategoryIn, CategoryOut, ProductIn, ProductOut, ProductUpdate, StockAdjustIn
from app.security import ALL_STAFF, MANAGERS
from app.services.inventory import BusinessError, adjust_stock, change_stock
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
    if user.role == "staff":
        data["cost_price"] = None  # nhân viên bán hàng không xem giá nhập
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
    """Tra sản phẩm theo mã, dùng khi quét QR / mã vạch ở màn hình bán hàng."""
    p = db.scalar(select(Product).where(func.upper(Product.code) == code.strip().upper()))
    if p is None:
        raise HTTPException(404, f"Không tìm thấy sản phẩm có mã '{code.strip()}'")
    return product_out(p, user)


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


@router.post("/products", status_code=201)
def create_product(data: ProductIn, db: Session = Depends(get_db), user: User = Depends(MANAGERS)):
    if data.category_id and db.get(Category, data.category_id) is None:
        raise HTTPException(400, "Nhóm hàng không tồn tại")
    initial_stock = data.stock
    p = Product(**data.model_dump(exclude={"stock"}), stock=0)
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
    if changes.get("category_id") and db.get(Category, changes["category_id"]) is None:
        raise HTTPException(400, "Nhóm hàng không tồn tại")
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
    if db.scalar(select(func.count(InvoiceItem.id)).where(InvoiceItem.product_id == product_id)):
        # Đã phát sinh giao dịch: chỉ ngừng kinh doanh để giữ lịch sử hóa đơn
        p.status = "inactive"
        db.commit()
        return {"ok": True, "message": "Sản phẩm đã có giao dịch nên được chuyển sang ngừng kinh doanh"}
    db.query(StockMovement).filter(StockMovement.product_id == product_id).delete()
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
    try:
        adjust_stock(db, p, data.new_stock, data.note, user)
    except BusinessError as e:
        db.rollback()
        raise HTTPException(400, str(e))
    db.commit()
    return product_out(p, user)


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
