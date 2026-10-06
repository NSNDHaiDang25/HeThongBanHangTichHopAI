// Nhật ký thao tác (UC-06, bảng audit_logs) và nhật ký gửi email
import { useState } from 'react'
import { api } from '../api.js'
import { daysAgo, fmtDateTime, today } from '../format.js'
import Icon from '../ui/Icon.jsx'
import { Empty, ErrorBox, Loading, Pager, useLoad } from '../ui/kit.jsx'

const ACTION_VI = {
  LOGIN_FAILED: 'Đăng nhập sai', ACCOUNT_LOCKED: 'Khóa tài khoản tạm', USER_CREATE: 'Tạo tài khoản', USER_UPDATE: 'Sửa tài khoản',
  ROLE_CHANGE: 'Đổi vai trò', PASSWORD_RESET: 'Đặt lại mật khẩu', PASSWORD_CHANGE: 'Đổi mật khẩu', SETTINGS_UPDATE: 'Sửa cấu hình',
  SETTINGS_UPDATE_OWNER: 'Sửa cấu hình kinh doanh', DB_BACKUP: 'Sao lưu CSDL', DB_RESTORE: 'Khôi phục CSDL',
  INVOICE_CANCEL: 'Hủy hóa đơn', INVOICE_CANCEL_REQUEST: 'Yêu cầu hủy hóa đơn', INVOICE_CANCEL_REJECT: 'Từ chối hủy hóa đơn',
  INVOICE_REPRINT: 'In lại hóa đơn', INVOICE_BELOW_COST: 'Bán dưới giá vốn', PRICE_CHANGE: 'Đổi giá', STOCK_ADJUST: 'Điều chỉnh tồn',
  SERIAL_UPDATE: 'Sửa serial', PURCHASE_CONFIRM: 'Xác nhận nhập kho', PURCHASE_CANCEL: 'Hủy phiếu nhập', RETURN_CREATE: 'Đổi trả',
  POINTS_ADJUST: 'Điều chỉnh điểm', TIER_UPDATE: 'Sửa hạng khách', PROMOTION_UPDATE: 'Sửa khuyến mãi', CUSTOMER_DEACTIVATE: 'Ngừng theo dõi khách', PRODUCT_IMPORT: 'Nhập sản phẩm từ CSV',
}

function Json({ value }) {
  if (!value) return <span className="muted">-</span>
  let text = value
  try { text = JSON.stringify(JSON.parse(value), null, 1).replace(/^\{\n|\n\}$/g, '').replace(/"/g, '') } catch { /* để nguyên */ }
  return <pre className="json-diff">{text}</pre>
}

function AuditLogs() {
  const [f, setF] = useState({ action: '', date_from: daysAgo(29), date_to: today() })
  const [page, setPage] = useState(1)
  const { data, error } = useLoad(() => api.get('/audit-logs', { ...f, page, size: 50 }), [JSON.stringify(f), page])
  const set = (k) => (e) => { setPage(1); setF({ ...f, [k]: e.target.value }) }
  return <>
    <div className="toolbar">
      <label>Thao tác<select value={f.action} onChange={set('action')}><option value="">Tất cả</option>
        {(data?.actions || []).map((a) => <option key={a} value={a}>{ACTION_VI[a] || a}</option>)}</select></label>
      <label>Từ ngày<input type="date" value={f.date_from} onChange={set('date_from')} /></label>
      <label>Đến ngày<input type="date" value={f.date_to} onChange={set('date_to')} /></label>
    </div>
    <ErrorBox error={error} />
    {!data ? <Loading /> : !data.items.length ? <Empty icon="clipboard" title="Không có thao tác nào trong kỳ" /> : <>
      <div className="table-wrap"><table>
        <thead><tr><th>Thời gian</th><th>Người thực hiện</th><th>Thao tác</th><th>Đối tượng</th><th>Trước</th><th>Sau</th><th>IP</th></tr></thead>
        <tbody>{data.items.map((r) => (
          <tr key={r.id}><td className="small nowrap">{fmtDateTime(r.created_at)}</td><td>{r.user_name || <span className="muted">Hệ thống</span>}</td>
            <td><span className="badge">{ACTION_VI[r.action] || r.action}</span></td>
            <td className="small">{r.entity}{r.entity_id ? ` #${r.entity_id}` : ''}</td>
            <td><Json value={r.old_value} /></td><td><Json value={r.new_value} /></td><td className="small muted">{r.ip_address || '-'}</td></tr>
        ))}</tbody>
      </table></div>
      <Pager page={page} size={50} total={data.total} onPage={setPage} />
    </>}
  </>
}

const MAIL_STATUS = { sent: ['Đã gửi', 'green'], failed: ['Lỗi', 'red'] }

function EmailLogs() {
  const [page, setPage] = useState(1)
  const { data, error } = useLoad(() => api.get('/email-logs', { page, size: 50 }), [page])
  return <>
    <ErrorBox error={error} />
    {!data ? <Loading /> : !data.items.length ? <Empty icon="mail" title="Chưa gửi email nào" /> : <>
      <div className="table-wrap"><table>
        <thead><tr><th>Thời gian</th><th>Người nhận</th><th>Tiêu đề</th><th>Loại</th><th>Trạng thái</th></tr></thead>
        <tbody>{data.items.map((r) => (
          <tr key={r.id}><td className="small nowrap">{fmtDateTime(r.created_at)}</td><td>{r.to_email}</td><td>{r.subject}</td><td className="small">{r.mail_type}</td>
            <td><span className={`badge ${(MAIL_STATUS[r.status] || [])[1] || ''}`}>{(MAIL_STATUS[r.status] || [r.status])[0]}</span>
              {r.error_message && <div className="muted small">{r.error_message}</div>}</td></tr>
        ))}</tbody>
      </table></div>
      <Pager page={page} size={50} total={data.total} onPage={setPage} />
    </>}
  </>
}

export default function Audit() {
  const [tab, setTab] = useState('audit')
  return (
    <div className="card">
      <div className="chips mb-4">
        <button className={`chip ${tab === 'audit' ? 'active' : ''}`} onClick={() => setTab('audit')}><Icon name="clipboard" />Thao tác</button>
        <button className={`chip ${tab === 'email' ? 'active' : ''}`} onClick={() => setTab('email')}><Icon name="mail" />Email đã gửi</button>
      </div>
      {tab === 'audit' ? <AuditLogs /> : <EmailLogs />}
    </div>
  )
}
