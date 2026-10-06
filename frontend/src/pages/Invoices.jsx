// Danh sách và chi tiết hóa đơn (UC-26 đến UC-30)
import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api, openFile } from '../api.js'
import { useAuth } from '../auth.jsx'
import { INVOICE_STATUS, PAY_VI, daysAgo, fmtDateTime, money, num, today } from '../format.js'
import Icon from '../ui/Icon.jsx'
import { Badge, ConfirmDialog, Empty, ErrorBox, Loading, Modal, Pager, useLoad, useToast } from '../ui/kit.jsx'

export function InvoiceDetail({ id, onClose, onChanged }) {
  const { user } = useAuth()
  const toast = useToast()
  const { data: inv, reload } = useLoad(() => api.get(`/invoices/${id}`), [id])
  const [dialog, setDialog] = useState(null)
  if (!inv) return <Modal title="Hóa đơn" onClose={onClose}><Loading /></Modal>
  const act = async (fn, msg) => {
    try { await fn(); toast(msg, 'success'); reload(); onChanged?.() } catch (e) { toast(e.message, 'error'); throw e }
  }
  const owner = user.role === 'owner'
  const canCancel = ['draft', 'pending_payment'].includes(inv.status) || (inv.status === 'paid' && !inv.cancel_requested_at)
  return (
    <Modal title={`Hóa đơn ${inv.code}`} onClose={onClose} size="wide" footer={<>
      {inv.status !== 'draft' && <button className="btn" onClick={() => openFile(`/invoices/${inv.id}/pdf`)}><Icon name="printer" />{inv.print_count ? 'In lại' : 'In hóa đơn'}</button>}
      {inv.customer_id && ['paid', 'partially_returned'].includes(inv.status) &&
        <button className="btn" onClick={() => act(() => api.post(`/invoices/${inv.id}/email`, {}), 'Đang gửi email hóa đơn')}><Icon name="mail" />Gửi email</button>}
      {inv.status === 'pending_payment' &&
        <button className="btn primary" onClick={() => act(() => api.post(`/invoices/${inv.id}/confirm-payment`, {}), 'Đã xác nhận nhận tiền')}><Icon name="check" />Xác nhận đã nhận tiền</button>}
      {owner && inv.cancel_requested_at && inv.status === 'paid' && <>
        <button className="btn" onClick={() => act(() => api.post(`/invoices/${inv.id}/cancel/approve`, { approve: false }), 'Đã từ chối yêu cầu hủy')}>Từ chối hủy</button>
        <button className="btn danger" onClick={() => act(() => api.post(`/invoices/${inv.id}/cancel/approve`, { approve: true }), 'Đã duyệt hủy hóa đơn')}>Duyệt hủy</button>
      </>}
      {canCancel && <button className="btn danger" onClick={() => setDialog('cancel')}>
        <Icon name="trash" />{inv.status === 'paid' && !owner ? 'Yêu cầu hủy' : 'Hủy hóa đơn'}</button>}
    </>}>
      <div className="info-list">
        <div><span className="muted">Trạng thái</span><span><Badge map={INVOICE_STATUS} value={inv.status} />{inv.cancel_requested_at && inv.status === 'paid' && <span className="badge red">Chờ duyệt hủy</span>}</span></div>
        <div><span className="muted">Thời gian lập</span><span>{fmtDateTime(inv.created_at)}</span></div>
        <div><span className="muted">Thanh toán lúc</span><span>{fmtDateTime(inv.paid_at) || '-'}</span></div>
        <div><span className="muted">Khách hàng</span><span>{inv.customer_name}{inv.customer_phone ? ` · ${inv.customer_phone}` : ''}</span></div>
        <div><span className="muted">Nhân viên</span><span>{inv.user_name}</span></div>
        <div><span className="muted">Phương thức</span><span>{PAY_VI[inv.payment_method]}{inv.payment_ref ? ` · ${inv.payment_ref}` : ''}</span></div>
        {inv.pending_deadline && <div><span className="muted">Giữ hàng đến</span><span className="text-danger">{fmtDateTime(inv.pending_deadline)}</span></div>}
        {inv.cancel_reason && <div><span className="muted">Lý do hủy</span><span>{inv.cancel_reason}</span></div>}
      </div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Sản phẩm</th><th>Serial</th><th className="right">SL</th><th className="right">Đơn giá</th>
            <th className="right">Giảm</th><th className="right">Thành tiền</th><th className="right">VAT</th><th className="right">Đã trả</th></tr></thead>
          <tbody>{inv.items.map((it) => (
            <tr key={it.id}><td>{it.product_name}<div className="muted small">{it.product_code}</div></td><td>{it.serial_no || '-'}</td>
              <td className="right">{it.quantity}</td><td className="right num">{money(it.unit_price)}</td>
              <td className="right num">{it.discount_amount ? `-${money(it.discount_amount)}` : '-'}</td>
              <td className="right num strong">{money(it.net_total)}</td><td className="right num muted">{money(it.vat_amount)} ({it.vat_rate}%)</td>
              <td className="right">{it.returned_qty || ''}</td></tr>
          ))}</tbody>
        </table>
      </div>
      <div className="totals-box">
        <div className="row"><span className="flex-1 muted">Tạm tính</span><span className="num">{money(inv.subtotal)}</span></div>
        {inv.promo_discount > 0 && <div className="row"><span className="flex-1 muted">Khuyến mãi {inv.promotion_code || ''}</span><span className="num">-{money(inv.promo_discount)}</span></div>}
        {inv.points_discount > 0 && <div className="row"><span className="flex-1 muted">Dùng {num(inv.points_used)} điểm</span><span className="num">-{money(inv.points_discount)}</span></div>}
        <div className="row strong text-lg"><span className="flex-1">Tổng thanh toán</span><span className="num">{money(inv.total)}</span></div>
        <div className="row small muted"><span className="flex-1">VAT đã gồm</span><span className="num">{money(inv.vat_amount)}</span></div>
        {inv.change !== null && <div className="row small muted"><span className="flex-1">Khách đưa / tiền thừa</span><span className="num">{money(inv.cash_received)} / {money(inv.change)}</span></div>}
        {inv.points_earned > 0 && <div className="row small muted"><span className="flex-1">Điểm cộng</span><span className="num">+{num(inv.points_earned)}</span></div>}
      </div>
      {inv.returns?.length > 0 && <p className="muted small">Phiếu đổi trả: {inv.returns.map((r) => `${r.code} (${money(r.refund_amount)})`).join(', ')}</p>}
      {dialog === 'cancel' && <ConfirmDialog title={inv.status === 'paid' && !owner ? 'Gửi yêu cầu hủy' : 'Hủy hóa đơn'}
        message={inv.status === 'paid' ? 'Hủy dành cho hóa đơn lập sai, chỉ trong ngày lập. Khách đổi ý hoặc hàng lỗi hãy dùng Đổi trả.' : 'Hàng giữ cho hóa đơn sẽ được hoàn về kho.'}
        reason="Lý do hủy" danger confirmText="Xác nhận" onClose={() => setDialog(null)}
        onConfirm={(reason) => act(() => api.post(`/invoices/${inv.id}/cancel`, { reason }), inv.status === 'paid' && !owner ? 'Đã gửi yêu cầu hủy' : 'Đã hủy hóa đơn')} />}
    </Modal>
  )
}

export default function Invoices() {
  const { user } = useAuth()
  // Liên kết từ trang Tổng quan: ?status=pending_payment hoặc ?cancel=requested (xem mọi ngày)
  const [params] = useSearchParams()
  const fromLink = params.get('status') || params.get('cancel')
  const [f, setF] = useState({ q: '', status: params.get('status') || '', payment_method: '', date_from: fromLink ? '' : daysAgo(29),
    date_to: fromLink ? '' : today(), cancel_requested: params.get('cancel') === 'requested' })
  const [page, setPage] = useState(1)
  const [open, setOpen] = useState(null)
  const { data, loading, error, reload } = useLoad(() => api.get('/invoices', { ...f, cancel_requested: f.cancel_requested || '', page, size: 20 }), [JSON.stringify(f), page])
  const set = (k) => (e) => { setPage(1); setF({ ...f, [k]: e.target.value }) }
  const exportFile = (format) => openFile('/reports/export/invoices', { ...f, format, cancel_requested: '' }, `hoa-don-${f.date_from}-${f.date_to}.${format}`)
  return (
    <div className="card">
      <div className="toolbar">
        <label className="grow">Tìm kiếm<input placeholder="Mã hóa đơn, tên hoặc SĐT khách" value={f.q} onChange={set('q')} /></label>
        <label>Trạng thái<select value={f.status} onChange={set('status')}>
          <option value="">Tất cả</option>{Object.entries(INVOICE_STATUS).map(([k, [v]]) => <option key={k} value={k}>{v}</option>)}
        </select></label>
        <label>Thanh toán<select value={f.payment_method} onChange={set('payment_method')}>
          <option value="">Tất cả</option>{Object.entries(PAY_VI).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select></label>
        <label>Từ ngày<input type="date" value={f.date_from} onChange={set('date_from')} /></label>
        <label>Đến ngày<input type="date" value={f.date_to} onChange={set('date_to')} /></label>
        <div className="actions">
          {user.role === 'owner' && <button className={`btn ${f.cancel_requested ? 'primary' : ''}`} onClick={() => setF({ ...f, cancel_requested: !f.cancel_requested })}>
            Chờ duyệt hủy {data?.cancel_requests ? <span className="badge red">{data.cancel_requests}</span> : null}</button>}
          <button className="btn" onClick={() => exportFile('xlsx')}><Icon name="download" />Excel</button>
          <button className="btn" onClick={() => exportFile('pdf')}>PDF</button>
          <button className="btn" onClick={() => exportFile('csv')}>CSV</button>
        </div>
      </div>
      <ErrorBox error={error} />
      {loading && !data ? <Loading /> : data && (<>
        <p className="muted small mt-0">{data.total} hóa đơn · doanh thu đã thanh toán {money(data.sum_paid)}{user.role === 'staff' ? ' · bạn chỉ thấy hóa đơn mình lập' : ''}</p>
        {!data.items.length ? <Empty title="Không có hóa đơn phù hợp" /> : (
          <div className="table-wrap"><table>
            <thead><tr><th>Mã</th><th>Thời gian</th><th>Khách hàng</th><th>Nhân viên</th><th>Thanh toán</th><th className="right">Tổng tiền</th><th>Trạng thái</th></tr></thead>
            <tbody>{data.items.map((i) => (
              <tr key={i.id} className="clickable" onClick={() => setOpen(i.id)}>
                <td className="strong">{i.code}</td><td>{fmtDateTime(i.created_at)}</td>
                <td>{i.customer_name}{i.customer_phone ? <div className="muted small">{i.customer_phone}</div> : null}</td>
                <td>{i.user_name}</td><td>{PAY_VI[i.payment_method]}</td><td className="right num strong">{money(i.total)}</td>
                <td><Badge map={INVOICE_STATUS} value={i.status} />{i.cancel_requested_at && i.status === 'paid' && <span className="badge red">Chờ duyệt hủy</span>}</td>
              </tr>
            ))}</tbody>
          </table></div>
        )}
        <Pager page={page} size={20} total={data.total} onPage={setPage} />
      </>)}
      {open && <InvoiceDetail id={open} onClose={() => setOpen(null)} onChanged={reload} />}
    </div>
  )
}
