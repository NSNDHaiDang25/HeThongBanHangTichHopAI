import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, ensure_schema
from app.routers import (ai, auth, catalog, customers, invoices, loyalty, payments, promotions, purchasing, reports,
                         system)
from app.services.audit import client_ip

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_schema(engine)
    yield


app = FastAPI(
    title="TechStore AI - Hệ thống quản lý bán hàng tích hợp AI",
    version="1.0.0",
    description="Quản lý sản phẩm, khách hàng, hóa đơn, nhập hàng, tồn kho, báo cáo và trợ lý AI (Gemini).",
    lifespan=lifespan,
)


@app.middleware("http")
async def remember_client_ip(request: Request, call_next):
    """Lưu IP người gọi để ghi vào audit_logs. Sau proxy (Render, nginx) IP thật nằm trong X-Forwarded-For."""
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    token = client_ip.set((forwarded or (request.client.host if request.client else ""))[:45] or None)
    try:
        return await call_next(request)
    finally:
        client_ip.reset(token)


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


for r in (auth, catalog, customers, invoices, loyalty, payments, promotions, purchasing, reports, ai, system):
    app.include_router(r.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


class RevalidatedStaticFiles(StaticFiles):
    """Buộc trình duyệt hỏi lại server (ETag, trả 304 nếu không đổi) để không dùng app.js / style.css cũ sau khi cập nhật."""

    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache"
        return response


app.mount("/static", RevalidatedStaticFiles(directory=settings.STATIC_DIR), name="static")
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(settings.STATIC_DIR / "index.html", headers={"Cache-Control": "no-cache"})


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    # Trình duyệt tự gọi /favicon.ico ở các trang không khai báo icon (ví dụ /docs)
    return FileResponse(settings.STATIC_DIR / "img" / "favicon.svg", media_type="image/svg+xml")
