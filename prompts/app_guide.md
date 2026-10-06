<!--
Hướng dẫn sử dụng SalesAI - kho kiến thức cho trợ lý AI đa năng (công cụ app_guide trong app/ai/tools.py).
Mỗi mục bắt đầu bằng "## "; trợ lý tìm mục khớp chủ đề câu hỏi rồi trả lời dựa trên nội dung mục đó.
Khi thêm / đổi chức năng trên giao diện, cập nhật file này để trợ lý hướng dẫn đúng.
-->

## Vai trò và phân quyền
- Có 3 vai trò **độc lập, không kế thừa quyền của nhau**:
  - **Quản trị viên**: quản lý tài khoản, đặt lại mật khẩu, cấu hình kỹ thuật và AI, sao lưu / khôi phục dữ liệu, xem nhật ký hệ thống. Không bán hàng, không xem giá vốn và doanh thu.
  - **Thu ngân**: lập hóa đơn, quản lý khách hàng, nhận đổi trả và bảo hành, lập phiếu nhập nháp, tra cứu sản phẩm, dùng trợ lý AI và chatbot tư vấn.
  - **Chủ cửa hàng**: mọi nghiệp vụ của thu ngân, thêm quản lý sản phẩm, giá, khuyến mãi, nhà cung cấp, nhập hàng, tồn kho, báo cáo, duyệt hủy hóa đơn, tham số kinh doanh và toàn bộ chức năng AI.
- Menu bên trái chỉ hiện các chức năng của vai trò đang đăng nhập.

## Bán hàng, lập hóa đơn (màn hình Bán hàng / POS)
- Vào menu **Bán hàng**. Bấm vào ô sản phẩm để thêm vào giỏ, hoặc bấm **Quét QR** để quét tem bằng camera, hoặc dùng máy quét mã vạch USB quét vào ô tìm kiếm rồi Enter.
- Sản phẩm hết hàng bị làm mờ, không thêm được. Số lượng trong giỏ không được vượt tồn kho.
- Chọn khách hàng: gõ tên hoặc SĐT ở ô khách hàng; bỏ trống = **Khách lẻ**. Khách có hạng thành viên được giảm giá tự động.
- Thu ngân không tự đặt giá, không tự giảm giá; chỉ áp dụng khuyến mãi / voucher, hạng thành viên và điểm tích lũy. Chủ cửa hàng có thêm ô "Giảm giá thêm" (₫ hoặc %).
- Bấm **Thanh toán** để thanh toán ngay (trừ kho), hoặc **Lưu tạm** để lưu hóa đơn chưa thanh toán.

## Sản phẩm quản lý theo IMEI / serial
- Điện thoại, laptop... có nhãn **IMEI**: mỗi máy có một số IMEI / serial riêng.
- Khi bán: bấm vào sản phẩm sẽ hiện hộp **Chọn IMEI / serial**, tích đúng máy giao cho khách hoặc quét IMEI rồi Enter. Quét IMEI ngay ở ô tìm kiếm của màn hình Bán hàng cũng thêm đúng máy đó vào giỏ.
- Khi nhập hàng: phải nhập đủ số IMEI bằng số lượng (mỗi dòng một số, quét bằng máy quét mã vạch).
- Menu **Serial / IMEI** (chủ cửa hàng): tra cứu từng máy (trong kho, đã bán, hàng lỗi), khai báo serial cho hàng đã có trong kho, đánh dấu máy lỗi.
- Bật / tắt quản lý theo IMEI trong form sửa sản phẩm.

## Khuyến mãi, voucher
- Menu **Khuyến mãi, voucher** (chủ cửa hàng): tạo chương trình giảm theo % (có thể giới hạn mức giảm tối đa) hoặc số tiền, điều kiện đơn tối thiểu, thời gian áp dụng, số lượt dùng.
- Chương trình **không có mã**: thu ngân chọn trong danh sách "Khuyến mãi, voucher" ở màn hình Bán hàng.
- Chương trình **có mã (voucher)**: khách đưa mã, thu ngân nhập mã vào ô voucher rồi bấm **Áp dụng**.
- Mỗi hóa đơn áp dụng một chương trình hoặc một voucher.

## Hạng thành viên, điểm tích lũy
- Khách được xếp **hạng thành viên** tự động theo tổng chi tiêu (đã trừ tiền hoàn trả hàng); mỗi hạng có mức giảm giá tự động khi mua. Chủ cửa hàng chỉnh hạng ở menu **Hạng thành viên**.
- **Điểm tích lũy**: thanh toán đủ số tiền quy định được cộng 1 điểm. Ở màn hình Bán hàng, chọn khách rồi nhập số điểm muốn dùng ở ô "Dùng điểm" (hoặc bấm **Dùng tối đa**).
- Hủy hóa đơn: hoàn lại điểm đã dùng và trừ điểm đã tích. Trả hàng: trừ phần điểm đã tích của hàng trả.
- **Điều chỉnh điểm** (chủ cửa hàng): mở chi tiết khách hàng > **Điều chỉnh điểm**, nhập số điểm cộng / trừ và lý do.
- Mức tích điểm, giá trị 1 điểm, tỉ lệ dùng điểm tối đa chỉnh ở menu **Tham số kinh doanh**.

## Thanh toán: tiền mặt, chuyển khoản, quẹt thẻ, quét mã QR
- **Tiền mặt**: nhập "Tiền khách đưa" để hệ thống tính tiền thừa trả khách; bỏ trống nếu khách đưa đủ. Tiền khách đưa không được ít hơn tổng tiền.
- **Chuyển khoản / Quẹt thẻ**: có thể ghi nội dung chuyển khoản hoặc mã giao dịch trên máy POS.
- **Quét mã QR (VietQR)**: hệ thống hiện mã QR có sẵn số tiền và nội dung. Khách mở app ngân hàng bất kỳ, chọn Quét QR. Kiểm tra tài khoản đã nhận tiền rồi bấm xác nhận.
- Tài khoản nhận tiền do chủ cửa hàng cấu hình ở menu **Tham số kinh doanh**.

## Hóa đơn tạm (chưa thanh toán), sửa hóa đơn
- Ở màn hình Bán hàng bấm **Lưu tạm**: hóa đơn được lưu ở trạng thái "Chưa thanh toán", chưa trừ kho (VD: khách giữ hàng, quay lại sau).
- Menu **Hóa đơn** > lọc trạng thái "Chưa thanh toán" (hoặc biểu tượng tạm dừng trên giỏ hàng) > chọn hóa đơn > **Mở để sửa / thanh toán**: sửa giỏ hàng rồi bấm Thanh toán.
- Chỉ sửa được hóa đơn **chưa thanh toán**. Hóa đơn đã thanh toán không sửa được: hủy (có duyệt) hoặc làm đổi trả.
- Hủy hóa đơn tạm: người lập hoặc chủ cửa hàng hủy ngay, không cần duyệt.

## Xem, in, xuất PDF, gửi email hóa đơn
- Menu **Hóa đơn**: lọc theo từ khóa (mã hóa đơn, tên / SĐT khách), trạng thái, phương thức thanh toán, khoảng ngày. Thu ngân chỉ thấy hóa đơn mình lập; chủ cửa hàng thấy tất cả.
- Bấm một dòng để xem chi tiết > **In / PDF / Email**: in hóa đơn khổ 80mm từ trình duyệt (máy in nhiệt), tải file PDF hoặc gửi hóa đơn kèm PDF qua email cho khách.
- Hóa đơn in có mã QR để tra cứu nhanh khi khách quay lại đổi trả, bảo hành.
- Chủ cửa hàng xuất danh sách hóa đơn ra Excel (xlsx), CSV hoặc PDF.

## Hủy hóa đơn, duyệt hủy
- Hóa đơn đã thanh toán: **thu ngân** mở chi tiết hóa đơn > **Yêu cầu hủy**, nhập lý do. Hóa đơn chuyển sang "Chờ duyệt hủy".
- **Chủ cửa hàng** thấy số yêu cầu chờ duyệt cạnh menu Hóa đơn; mở hóa đơn > **Duyệt hủy** (hoàn kho, trả serial về kho, hoàn điểm) hoặc **Từ chối hủy**. Chủ cửa hàng cũng có thể tự hủy hóa đơn.
- Hóa đơn đã có phiếu đổi trả thì không hủy được.

## Đổi trả hàng (trong 24 giờ)
- Menu **Đổi trả hàng**: quét mã QR trên hóa đơn hoặc nhập mã hóa đơn > **Tra hóa đơn**.
- Nhập số lượng khách trả (hàng IMEI: tích đúng máy), chọn tình trạng "Còn tốt, nhập lại kho" hoặc "Hàng lỗi, không nhập kho", nhập lý do > **Lập phiếu trả, hoàn tiền** rồi in phiếu cho khách ký.
- Tiền hoàn chia theo tỉ lệ giảm giá của hóa đơn; trả hết hàng thì hoàn đúng số tiền khách đã trả.
- Chỉ nhận đổi trả trong thời hạn quy định (mặc định 24 giờ sau khi mua, chủ cửa hàng chỉnh ở Tham số kinh doanh).
- **Đổi hàng**: lập phiếu trả cho món cũ rồi lập hóa đơn mới cho món khách lấy.

## Bảo hành: tra cứu, tiếp nhận, cập nhật tiến độ
- Menu **Bảo hành**: nhập / quét mã hóa đơn hoặc IMEI / serial > **Tra cứu** để biết máy còn bảo hành đến ngày nào (ngày mua + số tháng bảo hành của sản phẩm).
- Bấm **Tiếp nhận**, nhập tình trạng lỗi > in **phiếu tiếp nhận bảo hành** đưa khách. Khách không có hóa đơn: bấm "Khách không có hóa đơn" (tính là ngoài bảo hành).
- Cập nhật tiến độ: mở phiếu trong danh sách > chọn trạng thái (Đang xử lý, Đã trả khách, Từ chối bảo hành), ghi nội dung > **Cập nhật tiến độ**. Lịch sử tiến độ hiện trong phiếu.

## Sản phẩm và nhóm hàng
- Menu **Sản phẩm**: tìm theo tên / mã, lọc theo nhóm, tình trạng tồn (còn hàng, hết hàng, sắp hết), trạng thái.
- Chủ cửa hàng: **Thêm sản phẩm** (mã, tên, nhóm, giá bán, giá vốn, tồn ban đầu, mức tồn tối thiểu, số tháng bảo hành, quản lý theo IMEI, mô tả, ảnh), sửa, xóa. Sản phẩm đã có giao dịch khi xóa sẽ chuyển sang "Ngừng bán".
- Phần **Mô tả** được chatbot dùng để tư vấn, nên ghi rõ tính năng nổi bật.
- Thu ngân xem được sản phẩm nhưng không thấy giá vốn.
- Menu **Nhóm hàng** (chủ cửa hàng): thêm, sửa, xóa nhóm. Không xóa được nhóm đang có sản phẩm.

## In tem QR sản phẩm
- Menu **Sản phẩm** > **In tem QR** (in nhiều sản phẩm) hoặc biểu tượng QR trên từng dòng (chủ cửa hàng).
- Dán tem lên sản phẩm; ở màn hình Bán hàng bấm **Quét QR** và đưa tem vào camera để thêm vào giỏ.

## Nhà cung cấp
- Menu **Nhà cung cấp** (chủ cửa hàng): thêm, sửa nhà cung cấp (tên, SĐT, email, địa chỉ). Nhà cung cấp đã có phiếu nhập khi xóa sẽ chuyển sang ngừng giao dịch.
- Khi lập phiếu nhập, chọn nhà cung cấp trong danh sách gợi ý.

## Nhập hàng, phiếu nhập nháp, hủy phiếu nhập
- **Thu ngân** khi hàng về: menu **Nhập hàng** > **Lập phiếu nhập nháp**: chọn nhà cung cấp, sản phẩm, số lượng thực nhận, IMEI (nếu có), giá theo phiếu giao (không bắt buộc). Phiếu nháp chưa cộng kho.
- **Chủ cửa hàng** thấy số phiếu nháp chờ xác nhận cạnh menu Nhập hàng; mở phiếu > **Kiểm tra, xác nhận nhập kho**: sửa số lượng / giá nhập nếu cần rồi xác nhận, hàng được cộng kho, giá vốn cập nhật theo giá nhập gần nhất.
- Chủ cửa hàng tự lập phiếu nhập: **Tạo phiếu nhập** (cộng kho ngay). Hàng chưa có trong danh mục: gõ tên rồi chọn "Thêm sản phẩm mới".
- **Hủy phiếu nhập** (chủ cửa hàng): mở phiếu đã nhập kho > Hủy phiếu nhập, nhập lý do. Tồn kho bị trừ lại đúng số đã nhập; hàng đã bán bớt thì không hủy được.

## Kiểm kê, điều chỉnh tồn kho, thẻ kho, cảnh báo tồn kho thấp
- Tồn kho không sửa trực tiếp trong form sản phẩm; nó thay đổi qua bán hàng, phiếu nhập, hủy hóa đơn, đổi trả hoặc **Kiểm kê**.
- **Kiểm kê** (chủ cửa hàng): menu Sản phẩm > biểu tượng kiểm kê trên dòng sản phẩm > nhập "Số lượng thực tế" và "Lý do điều chỉnh".
- Menu **Thẻ kho**: chọn sản phẩm và kỳ để xem tồn đầu kỳ, từng lần nhập / xuất, tồn cuối kỳ.
- Menu **Nhập - xuất - tồn**: nhật ký mọi thay đổi tồn kho của tất cả sản phẩm.
- Sản phẩm có tồn <= mức tồn tối thiểu được coi là "sắp hết", hiện cảnh báo ở trang Tổng quan và Báo cáo tồn kho.

## Khách hàng
- Menu **Khách hàng**: tìm theo tên, SĐT, mã; lọc theo nhóm (Thường, VIP, Khách sỉ). Bấm một dòng để xem hạng, điểm, số hóa đơn, tổng chi tiêu, lịch sử mua hàng và lịch sử điểm.
- Thu ngân và chủ cửa hàng đều thêm / sửa được khách hàng; chỉ chủ cửa hàng được xóa và điều chỉnh điểm. Mã khách tự sinh dạng KH0001.

## Báo cáo doanh thu, tồn kho, tổng quan, xuất file
- Menu **Tổng quan** (chủ cửa hàng): doanh thu hôm nay, tháng này, biểu đồ 30 ngày, sản phẩm bán chạy, cảnh báo sắp hết hàng.
- Menu **Báo cáo doanh thu**: chọn khoảng ngày để xem doanh thu thuần (đã trừ hoàn trả hàng), giảm giá, giá vốn, lãi gộp, biểu đồ theo ngày / tháng, theo nhóm hàng, bán chạy, bán chậm.
- Menu **Báo cáo tồn kho**: giá trị tồn theo giá vốn / giá bán, theo nhóm hàng, danh sách sắp hết / hết hàng.
- Xuất báo cáo ra Excel (xlsx), CSV hoặc PDF bằng các nút xuất file.

## Tham số kinh doanh
- Menu **Tham số kinh doanh** (chủ cửa hàng): tên, địa chỉ, SĐT cửa hàng in trên hóa đơn; tài khoản nhận tiền VietQR; mức tích điểm, giá trị điểm, tỉ lệ dùng điểm tối đa; thời hạn đổi trả (giờ).

## Quản trị hệ thống (quản trị viên)
- Menu **Người dùng**: thêm tài khoản, đổi vai trò, khai báo email, đặt lại mật khẩu, khóa / mở, duyệt tài khoản tự đăng ký.
- Menu **Cấu hình kỹ thuật, AI**: bật / tắt AI, model chính và dự phòng, mức suy nghĩ, thời gian chờ, số lần thử lại, phiên bản prompt, thời gian hết hạn phiên đăng nhập. API key chỉ đặt trong file .env.
- Menu **Sao lưu, khôi phục**: tải bản sao lưu toàn bộ dữ liệu; khôi phục từ file sao lưu .db (thay thế toàn bộ dữ liệu hiện tại).
- Menu **Nhật ký hệ thống**: ai đăng nhập, đổi cấu hình, duyệt hủy, nhập kho... lúc nào; nhật ký gọi AI (không hiện nội dung câu hỏi).

## Các chức năng AI
- **Trợ lý đa năng** (thu ngân, chủ cửa hàng): hỏi mọi thứ bằng tiếng Việt: tìm sản phẩm, tồn kho, hóa đơn, khách hàng, khuyến mãi đang chạy, cách dùng phần mềm... AI tự tra dữ liệu thật qua các công cụ chỉ đọc, trong phạm vi quyền của người hỏi.
- **Chatbot tư vấn**: mô tả nhu cầu, ngân sách của khách để được gợi ý tối đa 3 sản phẩm còn hàng; bấm "Thêm vào giỏ" để bán ngay.
- **Báo cáo AI** và **Hỏi đáp dữ liệu** (chủ cửa hàng): AI viết nhận xét doanh thu, khuyến nghị nhập hàng, trả lời câu hỏi về số liệu kinh doanh.
- Lịch sử trò chuyện được lưu theo từng người dùng: tìm kiếm, đổi tên, xóa ở cột bên trái.

## Đăng nhập, đăng xuất, mật khẩu
- Đăng nhập bằng tên đăng nhập và mật khẩu do quản trị viên cấp. Phiên đăng nhập tự hết hạn (mặc định 8 giờ).
- **Đổi mật khẩu**: bấm vào tên của bạn ở góc trên bên phải.
- **Quên mật khẩu**: bấm "Quên mật khẩu?" ở màn hình đăng nhập để nhận mã xác nhận qua email đã khai báo; tài khoản chưa có email thì nhờ quản trị viên đặt lại.
- Đăng xuất: nút ở góc trên bên phải.
