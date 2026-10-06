# Kịch bản demo (khoảng 12 phút)

**Chuẩn bị:** `python -m scripts.seed` (dữ liệu sạch) → `uvicorn app.main:app` → mở http://localhost:8000. Nên có `GEMINI_API_KEY` để demo AI thật; nếu mạng lỗi, hệ thống tự chuyển chế độ dự phòng (badge "AI dự phòng"). Dữ liệu mẫu có sẵn: 1 hóa đơn tạm, 1 yêu cầu hủy chờ duyệt, 1 phiếu đổi trả, 3 phiếu bảo hành, 1 phiếu nhập nháp, voucher `KHAITRUONG50`.

Ba vai trò **độc lập, không kế thừa nhau**: mỗi vai trò chỉ thấy menu của mình.

## Phần 1: Thu ngân (4 phút)

1. Đăng nhập bằng nút **Thu ngân** (staff/staff123). Menu chỉ có: Bán hàng, Hóa đơn, Đổi trả hàng, Bảo hành, Khách hàng, Sản phẩm, Nhập hàng (phiếu nháp), Trợ lý AI. *→ Minh họa phân quyền.*
2. **Chatbot tư vấn** → *"Khách cần tai nghe dưới 500000 đồng, pin lâu, còn hàng"* → AI chỉ gợi ý hàng còn; *Tai nghe A2 Pro (PK002)* đang hết nên không được gợi ý → **Thêm vào giỏ**.
3. **Bán hàng**:
   - Gõ `PK005` rồi Enter (giống máy quét mã vạch USB) → sản phẩm vào thẳng giỏ. Bấm **Quét QR** để quét tem bằng camera.
   - Bấm *Điện thoại Galaxy A15* (nhãn IMEI) → hộp **Chọn IMEI / serial**: tích một máy (hoặc quét IMEI) → giỏ hiện số IMEI.
   - Ô khách hàng gõ "0901" → chọn *Phạm Minh Anh*: hiện hạng thành viên (giảm tự động) và số điểm → nhập số điểm muốn dùng.
   - Ô voucher nhập `KHAITRUONG50` → **Áp dụng**. *Nhấn mạnh: thu ngân không có ô giảm giá tay.*
   - Bấm **Lưu tạm** → hóa đơn tạm (chưa trừ kho). Vào **Hóa đơn** → lọc *Chưa thanh toán* → **Mở để sửa / thanh toán** → **Thanh toán** tiền mặt → hóa đơn in khổ 80mm có mã QR, nút **PDF**, **Email**.
4. **Hóa đơn** → mở hóa đơn vừa thanh toán → **Yêu cầu hủy** (lý do) → trạng thái *Chờ duyệt hủy* (thu ngân không tự hủy được).
5. **Đổi trả hàng** → quét mã QR trên hóa đơn (hoặc gõ mã) → chọn 1 sản phẩm trả, tình trạng *Còn tốt* → **Lập phiếu trả, hoàn tiền** → in phiếu trả. Thử hóa đơn quá 24 giờ → bị từ chối.
6. **Bảo hành** → nhập IMEI của máy vừa bán → thấy *Còn bảo hành đến ...* → **Tiếp nhận**, ghi lỗi → in phiếu tiếp nhận.
7. **Nhập hàng** → **Lập phiếu nhập nháp** (chọn sản phẩm, số lượng) → phiếu ở trạng thái *Nháp, chờ xác nhận*. **Sản phẩm**: không thấy cột giá nhập.

## Phần 2: Chủ cửa hàng (5 phút)

1. Đăng xuất → **Chủ cửa hàng** (owner/owner123): menu có số việc chờ cạnh **Hóa đơn** (yêu cầu hủy) và **Nhập hàng** (phiếu nháp).
2. **Hóa đơn** → bấm *yêu cầu hủy hóa đơn chờ duyệt* → mở hóa đơn → **Duyệt hủy** → **Thẻ kho** của sản phẩm thấy dòng *Hủy hóa đơn* `+1`; điểm khách được hoàn.
3. **Nhập hàng** → mở phiếu nháp → **Kiểm tra, xác nhận nhập kho**: điền giá nhập → tồn kho tăng. Thử **Hủy phiếu nhập** một phiếu đã nhập.
4. **Khuyến mãi, voucher**, **Hạng thành viên**, **Nhà cung cấp**, **Serial / IMEI**, **Tham số kinh doanh** (thời hạn đổi trả, điểm, tài khoản VietQR): giới thiệu nhanh.
5. **Báo cáo doanh thu** (doanh thu thuần đã trừ hoàn trả) → xuất **PDF / Excel**; **Báo cáo tồn kho**; **Báo cáo AI**; **Hỏi đáp dữ liệu** *"Tháng này mặt hàng nào bán chậm?"*.

## Phần 3: Quản trị viên (2 phút)

1. Đăng xuất → **Quản trị** (admin/admin123): menu chỉ có Người dùng, Cấu hình kỹ thuật, AI, Sao lưu, khôi phục, Nhật ký hệ thống. *Không có bán hàng, báo cáo, giá vốn.*
2. **Người dùng**: duyệt tài khoản tự đăng ký, khai báo email để người dùng tự đặt lại mật khẩu.
3. **Cấu hình kỹ thuật, AI**: tắt / bật AI, đổi model → badge AI trên thanh trên cập nhật.
4. **Sao lưu, khôi phục**: tải bản sao lưu .db.
5. **Nhật ký hệ thống**: thấy đăng nhập, yêu cầu hủy, duyệt hủy, xác nhận phiếu nhập vừa làm; tab **Gọi AI** không hiện nội dung câu hỏi.

## Phần 4: Độ bền (1 phút)

1. **Chatbot** → chọn prompt **v1** rồi **v3** để so sánh (xem `docs/03_so_sanh_prompt.md`).
2. Chạy `pytest -q` → 243 test pass.

## Câu hỏi thường gặp khi bảo vệ

| Câu hỏi | Gợi ý trả lời |
|---|---|
| Vì sao các vai trò không kế thừa nhau? | Tách nhiệm vụ: người quản trị kỹ thuật không cần (và không nên) thấy doanh thu, giá vốn; mỗi API khai báo đúng danh sách vai trò, không có vai trò toàn quyền (`require_roles`, `tests/test_roles.py`) |
| Làm sao đảm bảo AI không tư vấn hàng hết? | 3 lớp: lọc trước dữ liệu, JSON có cấu trúc, hậu kiểm bằng code (xem `docs/03_so_sanh_prompt.md`) |
| Sao không để AI tự viết SQL để hỏi đáp? | Rủi ro đọc bảng nhạy cảm, SQL sai, khó kiểm soát. Hệ thống tự tính số liệu tổng hợp rồi đưa cho AI |
| Sửa / hủy hóa đơn thì tồn kho xử lý thế nào? | Chỉ sửa hóa đơn chưa thanh toán (chưa trừ kho). Hủy hóa đơn đã thanh toán cần chủ cửa hàng duyệt: hoàn kho, trả serial, hoàn điểm trong 1 giao dịch, có thẻ kho và nhật ký hệ thống |
| Đổi trả ảnh hưởng doanh thu thế nào? | Phiếu trả ghi tiền hoàn chia theo tỉ lệ giảm giá; báo cáo trừ tiền hoàn vào kỳ có phiếu trả (doanh thu thuần), giá vốn trừ phần hàng nhập lại kho |
| Gửi gì cho AI, có lộ thông tin khách không? | Chỉ số liệu tổng hợp / sản phẩm; không gửi tên, SĐT, thanh toán; có test kiểm chứng |
| AI lỗi / hết quota thì sao? | Timeout, retry với 429/5xx, đổi model dự phòng, rồi chế độ dự phòng rule-based; quản trị viên có thể tắt AI |
