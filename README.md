# TechStore AI: Hệ thống quản lý bán hàng tích hợp AI

Web app quản lý bán hàng cho cửa hàng bán lẻ: sản phẩm, khách hàng, hóa đơn, nhập hàng, tồn kho, báo cáo doanh thu, kèm **4 chức năng AI (Google Gemini)**: trợ lý đa năng, chatbot tư vấn sản phẩm, AI sinh báo cáo doanh thu, hỏi đáp dữ liệu bán hàng.

**Công nghệ:** Python 3.11+ · FastAPI · SQLAlchemy 2 · SQLite (đổi được sang PostgreSQL/MySQL) · React 18 + Vite · Chart.js · Gemini API · pytest

Đặc tả yêu cầu: tài liệu SRS TechStore AI (Nhóm 1). Giao diện React theo SRS mục 2.6; giao diện HTML/JS cũ vẫn mở được ở `/classic`.

## Chạy nhanh

```bash
# 1. Tạo môi trường và cài thư viện
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt

# 2. Cấu hình
copy .env.example .env          # Windows  (macOS/Linux: cp .env.example .env)
#    Mở .env, điền GEMINI_API_KEY (lấy tại https://aistudio.google.com/apikey)
#    Để trống thì AI chạy chế độ dự phòng, mọi chức năng khác vẫn dùng bình thường.

# 3. Tạo dữ liệu mẫu (26 sản phẩm, 12 khách hàng, ~650 hóa đơn trong 120 ngày)
python -m scripts.seed

# 4. Chạy server
uvicorn app.main:app --reload
```

Mở **http://localhost:8000** (giao diện React, bản build có sẵn trong `static/app/`, không cần cài Node để chạy). Camera quét QR chỉ hoạt động trên `localhost` hoặc HTTPS (quy định của trình duyệt). Tài liệu API (Swagger): http://localhost:8000/docs

| Tài khoản | Mật khẩu | Vai trò |
|---|---|---|
| `admin` | `admin123` | Quản trị viên: toàn quyền, quản lý người dùng |
| `owner` | `owner123` | Chủ cửa hàng: quản lý, báo cáo, AI báo cáo/hỏi đáp |
| `staff` | `staff123` | Nhân viên bán hàng: bán hàng, khách hàng, trợ lý AI, chatbot |

Màn hình đăng nhập có nút đăng nhập nhanh cho từng vai trò.

### Chạy bằng Docker

```bash
cp .env.example .env    # điền GEMINI_API_KEY
docker compose up --build
```

Lần chạy đầu container tự tạo dữ liệu mẫu. CSDL lưu trong `./data`, log AI trong `./logs`.

## Chức năng

**Quản lý**
- Đăng nhập JWT, phân quyền 3 vai trò (kiểm tra ở server). Nhân viên không thấy giá nhập, chỉ xem hóa đơn mình lập và không được tự sửa giá bán.
- Sản phẩm: mã, tên, **ảnh**, nhóm hàng, giá bán, giá nhập, tồn kho, mức tồn tối thiểu, mô tả, trạng thái. Lọc theo còn / sắp hết / hết hàng. Ảnh tải lên được thu nhỏ về 800px, lưu dạng WEBP trong `data/uploads/`. 26 sản phẩm mẫu có sẵn ảnh chụp thật trong `static/img/products/` (nguồn Pexels, giấy phép miễn phí, xem `NGUON_ANH.md`).
- Khách hàng: liên hệ, nhóm (thường / VIP / sỉ), lịch sử mua, tổng chi tiêu.
- Bán hàng (POS): giỏ hàng có ảnh, giảm giá theo ₫ hoặc %, in hóa đơn.
- **4 phương thức thanh toán:** tiền mặt (nhập tiền khách đưa, tự tính tiền thừa), chuyển khoản (hiện số tài khoản, ghi nội dung CK), quẹt thẻ (ghi mã giao dịch POS), **quét mã QR** (sinh mã VietQR có sẵn số tiền, khách quét bằng app ngân hàng bất kỳ).
- **Quét QR / mã vạch sản phẩm:** bấm *Quét QR* để quét bằng camera, hoặc dùng máy quét mã vạch USB gõ thẳng vào ô tìm kiếm. Trang Sản phẩm có chức năng **in tem QR** để dán lên hàng.
- Hủy / sửa hóa đơn với tồn kho tự điều chỉnh trong một giao dịch.
- Phiếu nhập hàng, kiểm kho có lý do, nhật ký **nhập - xuất - tồn**.
- Dashboard, thống kê doanh thu theo ngày / tháng / nhóm hàng, bán chạy, bán chậm, lãi gộp.
- Xuất báo cáo doanh thu và danh sách hóa đơn ra **PDF / Excel / CSV**.

**AI**

| Chức năng | Prompt | Điểm chính |
|---|---|---|
| **Trợ lý đa năng** | `prompts/assistant.md` | Một khung chat hỏi được mọi thứ: sản phẩm, tồn kho, hóa đơn, khách hàng, doanh thu, xu hướng, nhập hàng, cách dùng phần mềm (`prompts/app_guide.md`), kiến thức chung. Gemini **function calling**: AI tự chọn trong 13 công cụ chỉ-đọc (`app/ai/tools.py`), không sinh SQL; công cụ lọc theo vai trò |
| Chatbot tư vấn sản phẩm | `prompts/product_advisor_v3.md` | Chỉ gửi sản phẩm còn hàng; trả JSON; server hậu kiểm loại mã sai hoặc hết hàng; có nút "Thêm vào giỏ" |
| AI sinh báo cáo doanh thu | `prompts/sales_report.md` | Hệ thống tính số liệu, AI viết nhận xét và khuyến nghị nhập hàng dạng Markdown |
| Hỏi đáp dữ liệu bán hàng | `prompts/sales_sql.md`, `prompts/sales_qa.md` | **Text-to-SQL** theo SRS 6.5: AI sinh một câu SELECT trên 7 view `v_ai_*`, hệ thống kiểm tra rồi chạy chỉ đọc, AI diễn giải bảng kết quả; giao diện hiện bảng và câu SQL. Xem mục bên dưới |

Xử lý lỗi AI gồm: timeout, retry có backoff khi gặp 429/5xx, xử lý phản hồi sai định dạng, và **chế độ dự phòng rule-based** khi chưa có key hoặc AI lỗi. Báo cáo AI và hỏi đáp dữ liệu không gửi tên, SĐT hay dữ liệu thanh toán của khách cho AI; trợ lý đa năng chỉ gửi tên / mã khách khi người dùng hỏi về khách hàng, SĐT luôn bị che (090****567), không gửi email, địa chỉ. Mọi lần gọi AI được ghi vào `logs/ai_calls.jsonl`.

## Kiểm thử

```bash
pytest -q
```

300+ test gồm hóa đơn (`test_invoices.py`), tồn kho (`test_inventory.py`), báo cáo và xuất file (`test_reports.py`), AI (`test_ai.py`), hỏi đáp text-to-SQL và 5 lớp bảo vệ (`test_text_to_sql.py`), API bổ sung theo SRS 8.4 như nhập CSV, `/api/inventory/*`, `/api/export/*` (`test_srs_api.py`), trợ lý đa năng (`test_assistant.py`), lịch sử trò chuyện (`test_chat_history.py`), thanh toán, VietQR, quét mã và ảnh sản phẩm (`test_payments_images.py`). Test AI dùng client giả nên không cần mạng hay API key.

So sánh 3 phiên bản prompt với Gemini thật (cần API key):

```bash
python -m scripts.compare_prompts --runs 3
```

## Cấu trúc thư mục

```
app/
  main.py              Khởi tạo FastAPI, phục vụ giao diện React (static/app) và giao diện cũ (/classic)
  config.py            Đọc cấu hình từ .env
  models.py            Các bảng dữ liệu (SRS chương 7)
  schemas.py           Kiểm tra dữ liệu vào
  security.py          Băm mật khẩu, JWT, phân quyền
  routers/             API theo SRS 8.4 (auth, catalog, product_import, inventory, invoices, aftersales, reports, ai, system...)
  services/            Nghiệp vụ: sales, pricing, inventory, purchasing, aftersales, loyalty, reports, export, qr...
  ai/                  client.py (Gemini), service.py (tư vấn, báo cáo, hỏi đáp), text_to_sql.py (view v_ai_*, kiểm tra SQL,
                       kết nối chỉ đọc), assistant.py + tools.py (trợ lý đa năng), history.py (lịch sử chat)
frontend/              Mã nguồn giao diện React (Vite): src/pages/ mỗi màn hình một file, src/ui/ thành phần dùng chung
static/app/            Bản build React (npm run build), FastAPI phục vụ trực tiếp
static/                Giao diện cũ: index.html, style.css, app.js; img/products/ (ảnh sản phẩm mẫu)
prompts/               Prompt template (tách khỏi code)
scripts/               seed.py, compare_prompts.py
tests/                 pytest
docs/                  Tài liệu dự án; docs/templates/mau_nhap_san_pham.csv (mẫu nhập sản phẩm)
```

### Sửa giao diện React

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173, tự chuyển /api sang uvicorn ở cổng 8000
npm run build    # ghi bản build vào static/app/ (nhớ commit thư mục này)
```

## Hỏi đáp dữ liệu bằng text-to-SQL (SRS 6.5)

Luồng UC-47: AI nhận lược đồ 7 view và câu hỏi, trả về đúng một câu `SELECT`; hệ thống kiểm tra, chạy, rồi gửi bảng kết quả cho AI diễn giải. Giao diện hiển thị câu trả lời, bảng kết quả và câu SQL đã chạy (FR-AIQ-07).

| Lớp bảo vệ (bảng 6.6) | Cài đặt |
|---|---|
| 1. Chỉ chủ cửa hàng | `/api/ai/ask` dùng quyền `MANAGERS`, nhân viên nhận 403 |
| 2. AI chỉ biết view an toàn | `v_ai_products`, `v_ai_sales_lines`, `v_ai_sales_daily`, `v_ai_inventory`, `v_ai_purchases`, `v_ai_returns`, `v_ai_customers` (khách chỉ có mã KHxxxx) |
| 3. Kiểm tra SQL bằng code | `validate_sql()`: một câu SELECT/WITH, không chú thích, không `;` giữa câu, chỉ đọc view `v_ai_*`, cấm INSERT/UPDATE/DELETE/DROP/ALTER/ATTACH/PRAGMA/CREATE/REPLACE và hàm hệ thống |
| 4. Kết nối chỉ đọc | SQLite mở `mode=ro` và `PRAGMA query_only = ON` |
| 5. Giới hạn | Tự bọc `LIMIT 200`, dừng sau 5 giây bằng `set_progress_handler` |

SQL vi phạm không được chạy và được ghi `ai_logs.status = rejected_sql`. Lỗi cú pháp được gửi lại cho AI sửa đúng một lần (FR-AIQ-08). Khi chưa có `GEMINI_API_KEY`, hệ thống dùng các câu SQL mẫu theo từ khóa, đi qua cùng bộ kiểm tra và kết nối chỉ đọc. Các view được tạo lại mỗi lần khởi động. Với CSDL không phải SQLite, tính năng quay về cách cũ: hệ thống tự tổng hợp số liệu rồi gửi cho AI.

## Nhập sản phẩm từ CSV (SRS 7.7)

Trang **Sản phẩm** → **Nhập CSV**: tải tệp mẫu, điền, bấm **Kiểm tra tệp** để xem trước, rồi **Nhập**. Cột bắt buộc: `sku`, `ten`, `gia_ban`. Một dòng lỗi thì không dòng nào được ghi; SKU đã có được bỏ qua; nhóm hàng chưa có sẽ được tạo mới. Tồn đầu kỳ nhập bằng phiếu nhập. API: `GET /api/products/import-template`, `POST /api/products/import?dry_run=true|false`.

## Tài liệu

| File | Nội dung |
|---|---|
| [docs/01_phan_tich_thiet_ke.md](docs/01_phan_tich_thiet_ke.md) | **KT1**: quy trình nghiệp vụ, actor, use case, FR/NFR, phân quyền, ERD, kiến trúc, vị trí tích hợp AI, wireframe, danh sách API |
| [docs/02_minh_chung_su_dung_AI.md](docs/02_minh_chung_su_dung_AI.md) | Minh chứng dùng AI trong từng giai đoạn SDLC, kèm mẫu để nhóm bổ sung |
| [docs/03_so_sanh_prompt.md](docs/03_so_sanh_prompt.md) | **KT3**: so sánh 3 phiên bản prompt tư vấn |
| [docs/04_kich_ban_demo.md](docs/04_kich_ban_demo.md) | Kịch bản demo 10 phút và câu hỏi bảo vệ |

## Cấu hình tài khoản nhận tiền (VietQR)

Trong `.env`, đổi các giá trị demo thành tài khoản thật của cửa hàng:

```
VIETQR_BANK_BIN=970436          # mã BIN ngân hàng, xem https://api.vietqr.io/v2/banks
VIETQR_BANK_NAME=Vietcombank
VIETQR_ACCOUNT_NO=0123456789
VIETQR_ACCOUNT_NAME=CUA HANG SALESAI
```

Mã QR được sinh ngay trên máy chủ theo chuẩn EMVCo/NAPAS, không gọi dịch vụ bên ngoài. Hệ thống **không tự xác nhận** tiền đã về tài khoản: thu ngân kiểm tra app ngân hàng rồi bấm "Đã nhận tiền".

Khi nâng cấp từ bản cũ, không cần xóa dữ liệu: lúc khởi động, hệ thống tự thêm các cột mới (`image_url`, `cash_received`, `payment_ref`).

## Quản trị viên quên mật khẩu (mã qua email)

Ở màn hình đăng nhập, bấm **Quên mật khẩu?**, nhập tên đăng nhập quản trị viên: hệ thống gửi mã 6 số tới `ADMIN_EMAIL` (hiệu lực 10 phút, dùng một lần, sai 5 lần thì hủy, 60 giây mới gửi lại được). Chủ cửa hàng và nhân viên vẫn nhờ quản trị viên đặt lại trong menu **Người dùng**.

Điền `ADMIN_EMAIL` trong `.env` và chọn một cách gửi email:

| Cách gửi | Cấu hình | Dùng khi |
|---|---|---|
| **Resend** (HTTPS) | Đăng ký [resend.com](https://resend.com) bằng chính `ADMIN_EMAIL`, tạo API key, điền `RESEND_API_KEY` | Deploy trên **Render gói miễn phí** (Render chặn cổng SMTP) |
| **Gmail SMTP** | Bật Xác minh 2 bước, tạo [mật khẩu ứng dụng](https://myaccount.google.com/apppasswords), điền `SMTP_USER` (địa chỉ Gmail) và `SMTP_PASSWORD` | Chạy trên máy hoặc server không chặn SMTP |

Có `RESEND_API_KEY` thì hệ thống dùng Resend, ngược lại dùng SMTP. Chưa cấu hình thì nút gửi mã báo lỗi, các chức năng khác không bị ảnh hưởng.

## Đổi sang PostgreSQL

```bash
pip install "psycopg[binary]"
# .env
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/sales
python -m scripts.seed
```
