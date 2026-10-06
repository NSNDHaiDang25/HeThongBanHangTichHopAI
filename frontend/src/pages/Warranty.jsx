// Bảo hành theo serial (UC-32, UC-33, FR-WAR-01..08)
import { useState } from 'react'
import { api, openFile } from '../api.js'
import { TICKET_STATUS, fmtDate, fmtDateTime } from '../format.js'
import Icon from '../ui/Icon.jsx'
import { Badge, Empty, ErrorBox, Loading, Modal, Pager, useLoad, useToast } from '../ui/kit.jsx'

const WARRANTY_STATUS = {
  active: ['Còn bảo hành', 'green'], expired: ['Hết hạn', 'red'], void: ['Không còn hiệu lực', ''],
}

function ReceiveDialog({ w, onClose, onDone }) {
  const toast = useToast()
  const [issue, setIssue] = useState('')
  const [busy, setBusy] = useState(false)
  const submit = async () => {
    setBusy(true)
    try {
      const t = await api.post('/warranty-tickets', { warranty_id: w.id, issue_description: issue.trim() })
      toast(`Đã tạo phiếu ${t.code}`, 'success'); onDone(t)
    } catch (e) { toast(e.message, 'error') } finally { setBusy(false) }
  }
  return (
    <Modal title="Tiếp nhận bảo hành" onClose={onClose} footer={
      <button className="btn primary" disabled={busy || issue.trim().length < 5} onClick={submit}><Icon name="check" />Tạo phiếu và in biên nhận</button>}>
      <div className="info-list">
        <div><span className="muted">Sản phẩm</span><span className="strong">{w.product_name}</span></div>
        <div><span className="muted">Serial / IMEI</span><span>{w.serial_no || 'Không theo serial'}</span></div>
        <div><span className="muted">Khách hàng</span><span>{w.customer_name}{w.customer_phone ? ` · ${w.customer_phone}` : ''}</span></div>
        <div><span className="muted">Hạn bảo hành</span><span>{fmtDate(w.end_date)} (còn {w.days_left} ngày)</span></div>
      </div>
      <label>Mô tả lỗi khách báo (bắt buộc)
        <textarea rows={4} value={issue} onChange={(e) => setIssue(e.target.value)} placeholder="VD: Máy không lên nguồn, màn hình sọc ngang" /></label>
    </Modal>
  )
}

function TicketDialog({ id, onClose, onChanged }) {
  const toast = useToast()
  const { data: t, error, reload } = useLoad(() => api.get(`/warranty-tickets/${id}`), [id])
  const [resolution, setResolution] = useState(null)
  const [busy, setBusy] = useState(false)
  if (error) return <Modal title="Phiếu bảo hành" onClose={onClose}><ErrorBox error={error} /></Modal>
  if (!t) return <Modal title="Phiếu bảo hành" onClose={onClose}><Loading /></Modal>
  const res = resolution ?? (t.resolution || '')
  const update = async (status) => {
    setBusy(true)
    try {
      await api.put(`/warranty-tickets/${t.id}`, { status, resolution: res })
      toast(status ? `Đã chuyển sang "${TICKET_STATUS[status][0]}"` : 'Đã lưu kết quả xử lý', 'success')
      setResolution(null); reload(); onChanged()
    } catch (e) { toast(e.message, 'error') } finally { setBusy(false) }
  }
  const needResult = (s) => ['done', 'rejected'].includes(s) && !res.trim()
  return (
    <Modal title={`Phiếu ${t.code}`} onClose={onClose} size="wide" footer={<>
      <button className="btn" onClick={() => openFile(`/warranty-tickets/${t.id}/pdf`)}><Icon name="printer" />In biên nhận</button>
      {t.status !== 'returned' && <button className="btn" disabled={busy || res === (t.resolution || '')} onClick={() => update(null)}><Icon name="save" />Lưu kết quả</button>}
      {t.next_statuses.map((s) => (
        <button key={s} className={`btn ${s === 'rejected' ? 'danger' : 'primary'}`} disabled={busy || needResult(s)}
          title={needResult(s) ? 'Nhập kết quả xử lý trước' : ''} onClick={() => update(s)}>{TICKET_STATUS[s][0]}</button>
      ))}
    </>}>
      <div className="row mb-4"><Badge map={TICKET_STATUS} value={t.status} />
        <span className="muted small">Tiếp nhận {fmtDateTime(t.received_at)} bởi {t.received_by}</span></div>
      <div className="info-list">
        <div><span className="muted">Sản phẩm</span><span className="strong">{t.product_name}</span></div>
        <div><span className="muted">Serial / IMEI</span><span>{t.serial_no || '-'}</span></div>
        <div><span className="muted">Hóa đơn</span><span>{t.invoice_code}</span></div>
        <div><span className="muted">Khách hàng</span><span>{t.customer_name}{t.customer_phone ? ` · ${t.customer_phone}` : ''}</span></div>
        <div><span className="muted">Hết hạn bảo hành</span><span>{fmtDate(t.warranty_end)}</span></div>
        <div><span className="muted">Email thông báo</span><span>{t.customer_email || 'Khách chưa có email'}</span></div>
        {t.completed_at && <div><span className="muted">Xử lý xong</span><span>{fmtDateTime(t.completed_at)}</span></div>}
        {t.returned_at && <div><span className="muted">Trả khách</span><span>{fmtDateTime(t.returned_at)}</span></div>}
      </div>
      <label>Lỗi khách báo<textarea rows={2} value={t.issue_description} readOnly /></label>
      <label className="mt-3">Kết quả xử lý {['received', 'in_repair', 'waiting_parts'].includes(t.status) && <span className="muted small">(bắt buộc trước khi hoàn tất hoặc từ chối)</span>}
        <textarea rows={3} value={res} disabled={t.status === 'returned'} onChange={(e) => setResolution(e.target.value)}
          placeholder="VD: Thay màn hình mới, kiểm tra hoạt động bình thường" /></label>
    </Modal>
  )
}

export default function Warranty() {
  const toast = useToast()
  const [q, setQ] = useState('')
  const [found, setFound] = useState(null)
  const [receive, setReceive] = useState(null)
  const [ticket, setTicket] = useState(null)
  const [filter, setFilter] = useState({ status: '', q: '', open_only: true })
  const [page, setPage] = useState(1)
  const list = useLoad(() => api.get('/warranty-tickets', { ...filter, open_only: filter.open_only || '', page, size: 20 }), [JSON.stringify(filter), page])

  const search = async (e) => {
    e.preventDefault()
    if (q.trim().length < 3) { toast('Nhập ít nhất 3 ký tự', 'error'); return }
    try { setFound(await api.get('/warranties/lookup', { q: q.trim() })) } catch (err) { toast(err.message, 'error') }
  }
  const counts = list.data?.counts || {}
  return (
    <div className="stack">
      <div className="card">
        <div className="card-head"><h2><Icon name="search" />Tra cứu bảo hành</h2></div>
        <form className="toolbar" onSubmit={search}>
          <label className="grow">Serial / IMEI, số điện thoại khách hoặc mã hóa đơn
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Quét serial hoặc nhập 0912345678 / HD-20261001-0001" autoFocus /></label>
          <div className="actions"><button className="btn primary" type="submit"><Icon name="search" />Tra cứu</button></div>
        </form>
        {found && (!found.length ? <Empty title="Không tìm thấy hồ sơ bảo hành" /> : (
          <div className="table-wrap"><table>
            <thead><tr><th>Sản phẩm</th><th>Serial</th><th>Khách</th><th>Hóa đơn</th><th>Thời hạn</th><th>Trạng thái</th><th /></tr></thead>
            <tbody>{found.map((w) => (
              <tr key={w.id}>
                <td className="strong">{w.product_name}<div className="muted small">{w.product_code}</div></td>
                <td>{w.serial_no || '-'}</td><td>{w.customer_name}<div className="muted small">{w.customer_phone}</div></td><td>{w.invoice_code}</td>
                <td className="small">{fmtDate(w.start_date)} → {fmtDate(w.end_date)}{w.status === 'active' && <div className="muted">Còn {w.days_left} ngày</div>}</td>
                <td><Badge map={WARRANTY_STATUS} value={w.status} />{w.open_ticket && <div className="mt-2"><button className="link-btn small" onClick={() => setTicket(w.open_ticket.id)}>Đang có phiếu {w.open_ticket.code}</button></div>}</td>
                <td className="right">{w.can_receive && <button className="btn sm primary" onClick={() => setReceive(w)}>Tiếp nhận</button>}</td>
              </tr>
            ))}</tbody>
          </table></div>
        ))}
      </div>

      <div className="card">
        <div className="card-head"><h2><Icon name="wrench" />Phiếu bảo hành</h2></div>
        <div className="chips">
          <button className={`chip ${filter.open_only && !filter.status ? 'active' : ''}`} onClick={() => { setPage(1); setFilter({ ...filter, status: '', open_only: true }) }}>Chưa trả khách</button>
          {Object.entries(TICKET_STATUS).map(([k, [label]]) => (
            <button key={k} className={`chip ${filter.status === k ? 'active' : ''}`} onClick={() => { setPage(1); setFilter({ ...filter, status: k, open_only: false }) }}>
              {label}{counts[k] ? ` (${counts[k]})` : ''}</button>
          ))}
          <button className={`chip ${!filter.open_only && !filter.status ? 'active' : ''}`} onClick={() => { setPage(1); setFilter({ ...filter, status: '', open_only: false }) }}>Tất cả</button>
        </div>
        <div className="toolbar"><label className="grow">Tìm theo mã phiếu hoặc serial
          <input value={filter.q} onChange={(e) => { setPage(1); setFilter({ ...filter, q: e.target.value }) }} placeholder="BH-... hoặc serial" /></label></div>
        <ErrorBox error={list.error} />
        {!list.data ? <Loading /> : !list.data.items.length ? <Empty icon="wrench" title="Không có phiếu bảo hành" /> : <>
          <div className="table-wrap"><table>
            <thead><tr><th>Mã phiếu</th><th>Sản phẩm</th><th>Khách</th><th>Lỗi</th><th>Tiếp nhận</th><th>Trạng thái</th><th /></tr></thead>
            <tbody>{list.data.items.map((t) => (
              <tr key={t.id} className="clickable" onClick={() => setTicket(t.id)}>
                <td className="strong">{t.code}</td><td>{t.product_name}<div className="muted small">{t.serial_no}</div></td>
                <td>{t.customer_name}</td><td className="small">{t.issue_description}</td><td className="small">{fmtDateTime(t.received_at)}</td>
                <td><Badge map={TICKET_STATUS} value={t.status} /></td>
                <td className="right"><button className="btn sm" title="In biên nhận" onClick={(e) => { e.stopPropagation(); openFile(`/warranty-tickets/${t.id}/pdf`) }}><Icon name="printer" /></button></td>
              </tr>
            ))}</tbody>
          </table></div>
          <Pager page={page} size={20} total={list.data.total} onPage={setPage} />
        </>}
      </div>

      {receive && <ReceiveDialog w={receive} onClose={() => setReceive(null)} onDone={(t) => {
        setReceive(null); setFound(null); list.reload(); openFile(`/warranty-tickets/${t.id}/pdf`)
      }} />}
      {ticket && <TicketDialog id={ticket} onClose={() => setTicket(null)} onChanged={list.reload} />}
    </div>
  )
}
