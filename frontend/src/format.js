export const money = (v) => (Number(v) || 0).toLocaleString('vi-VN') + ' ₫'
export const num = (v) => (Number(v) || 0).toLocaleString('vi-VN')
export const fmtDateTime = (s) => (s ? new Date(s).toLocaleString('vi-VN', {
  day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
}) : '')
export const fmtDate = (s) => (s ? new Date(s).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' }) : '')
export const isoDate = (d) => { const x = new Date(d); x.setMinutes(x.getMinutes() - x.getTimezoneOffset()); return x.toISOString().slice(0, 10) }
export const today = () => isoDate(new Date())
export const daysAgo = (n) => isoDate(Date.now() - n * 86400000)
export const initialsOf = (name) => String(name || '?').trim().split(/\s+/).slice(-2).map((w) => w[0]).join('').toUpperCase()
export const toLocalInput = (s) => (s ? String(s).slice(0, 16) : '')

export const ROLE_VI = { admin: 'Quản trị viên', owner: 'Chủ cửa hàng', staff: 'Nhân viên bán hàng' }
export const PAY_VI = { cash: 'Tiền mặt', bank_transfer: 'Chuyển khoản', card: 'Thẻ (POS)' }
export const INVOICE_STATUS = {
  draft: ['Nháp', ''], pending_payment: ['Chờ thanh toán', 'yellow'], paid: ['Đã thanh toán', 'green'],
  partially_returned: ['Trả một phần', 'cyan'], fully_returned: ['Đã trả hết', 'blue'], cancelled: ['Đã hủy', 'red'],
}
export const PO_STATUS = { draft: ['Nháp', 'yellow'], confirmed: ['Đã nhập kho', 'green'], cancelled: ['Đã hủy', 'red'] }
export const TICKET_STATUS = {
  received: ['Đã tiếp nhận', 'blue'], in_repair: ['Đang sửa', 'yellow'], waiting_parts: ['Chờ linh kiện', 'yellow'],
  done: ['Đã sửa xong', 'green'], rejected: ['Từ chối', 'red'], returned: ['Đã trả khách', ''],
}
export const SERIAL_STATUS = {
  in_stock: ['Trong kho', 'green'], sold: ['Đã bán', 'blue'], returned: ['Khách trả', 'cyan'],
  defective: ['Lỗi', 'red'], in_warranty: ['Đang bảo hành', 'yellow'],
}
export const MOVE_VI = {
  import: 'Nhập hàng', import_cancel: 'Hủy phiếu nhập', sale: 'Bán hàng', cancel: 'Hủy hóa đơn',
  edit: 'Sửa hóa đơn', return: 'Khách trả hàng', adjust: 'Điều chỉnh / kiểm kê',
}
