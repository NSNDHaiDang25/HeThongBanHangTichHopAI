# SalesAI: Hệ thống quản lý bán hàng tích hợp AI

Web app quản lý bán hàng cho cửa hàng bán lẻ: sản phẩm (quản lý IMEI / serial), khách hàng thân thiết (hạng, điểm), khuyến mãi / voucher, hóa đơn, đổi trả, bảo hành, nhà cung cấp, nhập hàng, tồn kho, báo cáo doanh thu, kèm **4 chức năng AI (Google Gemini)**: trợ lý đa năng, chatbot tư vấn sản phẩm, AI sinh báo cáo doanh thu, hỏi đáp dữ liệu bán hàng.

**Công nghệ:** Python 3.11+ · FastAPI · SQLAlchemy 2 · SQLite (đổi được sang PostgreSQL/MySQL) · HTML/CSS/JavaScript thuần · Chart.js · Gemini API · pytest

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

Mở **http://localhost:8000**. Camera quét QR chỉ hoạt động trên `localhost` hoặc HTTPS (quy định của trình duyệt). Tài liệu API (Swagger): http://localhost:8000/docs

| Tài khoản | Mật khẩu | Vai trò |
|---|---|---|
| `admin` | `admin123` | **Quản trị viên**: quản lý tài khoản, đặt lại mật khẩu, cấu hình kỹ thuật và AI, sao lưu / khôi phục, nhật ký hệ thống. Không bán hàng, không xem giá vốn và doanh thu |
| `owner` | `owner123` | **Chủ cửa hàng**: mọi nghiệp vụ của thu ngân + sản phẩm, serial / IMEI, giá, khuyến mãi, hạng thành viên, điểm, nhà cung cấp, nhập hàng, tồn kho, báo cáo, tham số kinh doanh, duyệt hủy hóa đơn, toàn bộ AI |
| `staff` | `staff123` | **Thu ngân**: lập hóa đơn, khách hàng, đổi trả, bảo hành, phiếu nhập nháp, tra cứu sản phẩm, trợ lý AI và chatbot tư vấn |

Ba vai trò **độc lập, không kế thừa quyền của nhau**: mỗi API khai báo đúng danh sách vai trò được dùng (`app/security.py`), giao diện chỉ hiện menu của vai trò đang đăng nhập.

Màn hình đăng nhập có nút đăng nhập nhanh cho từng vai trò.

### Chạy bằng Docker

```bash
cp .env.example .env    # điền GEMINI_API_KEY
docker compose up --build
```

Lần chạy đầu container tự tạo dữ liệu mẫu. CSDL lưu trong `./data`, log AI trong `./logs`.

## Chức năng

**Quản lý**
- Đăng nhập JWT, phân quyền 3 vai trò độc lập (kiểm tra ở server). Thu ngân không thấy giá nhập, chỉ xem hóa đơn mình lập, không tự sửa giá / tự giảm giá. Đổi mật khẩu, quên mật khẩu qua email.
- **Quản trị hệ thống**: cấu hình kỹ thuật và AI trên giao diện (bật / tắt AI, model, timeout...), sao lưu / khôi phục dữ liệu, nhật ký hệ thống (đăng nhập, cấu hình, duyệt hủy, nhập kho...).
- **Hóa đơn tạm** (lưu chưa thanh toán, sửa rồi thanh toán sau); hóa đơn đã thanh toán không sửa được: **thu ngân yêu cầu hủy, chủ cửa hàng duyệt**.
- **Khuyến mãi, voucher** (%, số tiền, giảm tối đa, đơn tối thiểu, số lượt), **hạng thành viên** giảm giá tự động, **điểm tích lũy** (tích, dùng, điều chỉnh).
- **IMEI / serial**: nhập kho ghi số máy, bán chọn đúng máy (quét IMEI thêm thẳng vào giỏ), tra bảo hành theo IMEI.
- **Đổi trả trong 24 giờ** (hoàn tiền theo tỉ lệ giảm giá, nhập lại kho / hàng lỗi), **bảo hành** (tra cứu, tiếp nhận, cập nhật tiến độ), in phiếu.
- **Nhà cung cấp**, **phiếu nhập nháp** (thu ngân lập, chủ cửa hàng xác nhận), **hủy phiếu nhập**, **thẻ kho**, **báo cáo tồn kho**.
- Hóa đơn in từ trình duyệt (khổ 80mm, có mã QR để tra khi đổi trả / bảo hành), **xuất PDF**, **gửi email** kèm PDF.
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
| **Trợ lý đa năng** | `prompts/assistant.md` | Một khung chat hỏi được mọi thứ: sản phẩm, tồn kho, hóa đơn, khách hàng, doanh thu, xu hướng, nhập hàng, cách dùng phần mềm (`prompts/app_guide.md`), kiến thức chung. Gemini **function calling**: AI tự chọn trong 14 công cụ chỉ-đọc (`app/ai/tools.py`), không sinh SQL; công cụ lọc theo vai trò |
| Chatbot tư vấn sản phẩm | `prompts/product_advisor_v3.md` | Chỉ gửi sản phẩm còn hàng; trả JSON; server hậu kiểm loại mã sai hoặc hết hàng; có nút "Thêm vào giỏ" |
| AI sinh báo cáo doanh thu | `prompts/sales_report.md` | Hệ thống tính số liệu, AI viết nhận xét và khuyến nghị nhập hàng dạng Markdown |
| Hỏi đáp dữ liệu bán hàng | `prompts/sales_qa.md` | Tự nhận diện kỳ ("tháng này", "tháng trước", "7 ngày"...), không cho AI chạy SQL |

Xử lý lỗi AI gồm: timeout, retry có backoff khi gặp 429/5xx, xử lý phản hồi sai định dạng, và **chế độ dự phòng rule-based** khi chưa có key hoặc AI lỗi. Báo cáo AI và hỏi đáp dữ liệu không gửi tên, SĐT hay dữ liệu thanh toán của khách cho AI; trợ lý đa năng chỉ gửi tên / mã khách khi người dùng hỏi về khách hàng, SĐT luôn bị che (090****567), không gửi email, địa chỉ. Mọi lần gọi AI được ghi vào `logs/ai_calls.jsonl`.

## Kiểm thử

```bash
pytest -q
```

243 test gồm phân quyền, sao lưu / khôi phục, cấu hình (`test_roles.py`), khuyến mãi, voucher, hạng, điểm, IMEI, đổi trả, bảo hành, phiếu nhập nháp, thẻ kho (`test_sales_features.py`), hóa đơn (`test_invoices.py`), tồn kho (`test_inventory.py`), báo cáo và xuất file (`test_reports.py`), AI (`test_ai.py`), trợ lý đa năng và công cụ tra cứu (`test_assistant.py`), lịch sử trò chuyện (`test_chat_history.py`), thanh toán, VietQR, quét mã và ảnh sản phẩm (`test_payments_images.py`). Test AI dùng client giả nên không cần mạng hay API key.

So sánh 3 phiên bản prompt với Gemini thật (cần API key):

```bash
python -m scripts.compare_prompts --runs 3
```

## Cấu trúc thư mục

```
app/
  main.py              Khởi tạo FastAPI, phục vụ giao diện
  config.py            Đọc cấu hình từ .env
  models.py            Bảng nghiệp vụ (sản phẩm, serial, khách hàng, hạng, điểm, khuyến mãi, hóa đơn, đổi trả,
                       bảo hành, nhà cung cấp, phiếu nhập, thẻ kho) và hệ thống (người dùng, nhật ký, tham số)
  schemas.py           Kiểm tra dữ liệu vào
  security.py          Băm mật khẩu, JWT, phân quyền 3 vai trò độc lập
  routers/             API: auth, catalog, customers, invoices, payments, promotions (khuyến mãi, nhà cung cấp),
                       aftersales (đổi trả, bảo hành), reports, ai, admin (cấu hình, sao lưu, nhật ký, tham số kinh doanh)
  services/            inventory.py (hóa đơn, nhập hàng, tồn kho, serial), loyalty.py (hạng, điểm), aftersales.py,
                       reports.py, export.py, qr.py, audit.py (nhật ký), system_config.py (tham số), backup.py
  ai/                  client.py (Gemini, function calling), prompts.py (nạp template), service.py (tư vấn, báo cáo, hỏi đáp),
                       assistant.py (trợ lý đa năng), tools.py (công cụ tra cứu chỉ-đọc), history.py (lịch sử chat)
prompts/               Prompt template (tách khỏi code)
static/                Giao diện SPA: index.html, style.css, app.js; img/products/ (ảnh sản phẩm mẫu)
scripts/               seed.py, compare_prompts.py
tests/                 pytest
docs/                  Tài liệu dự án
```

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

Khi nâng cấp từ bản cũ, không cần xóa dữ liệu: lúc khởi động, hệ thống tự tạo bảng mới và thêm các cột mới. Tài khoản nhận tiền cũng chỉnh được trên giao diện (chủ cửa hàng, menu **Tham số kinh doanh**).

## Quên mật khẩu (mã qua email)

Ở màn hình đăng nhập, bấm **Quên mật khẩu?**, nhập tên đăng nhập: hệ thống gửi mã 6 số tới **email của tài khoản** (quản trị viên khai báo email cho từng người trong menu **Người dùng**; tài khoản quản trị viên chưa có email thì gửi tới `ADMIN_EMAIL`). Mã hiệu lực 10 phút, dùng một lần, sai 5 lần thì hủy, 60 giây mới gửi lại được. Tài khoản chưa có email nhờ quản trị viên đặt lại. Đang đăng nhập thì bấm vào tên ở góc trên bên phải để **đổi mật khẩu**. Cấu hình gửi email cũng dùng để gửi hóa đơn cho khách.

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
