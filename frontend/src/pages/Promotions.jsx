// Khuyến mãi (UC-18)
import { useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import { fmtDateTime, money, num, toLocalInput } from '../format.js'
import Icon from '../ui/Icon.jsx'
import { Empty, ErrorBox, Field, Loading, Modal, MoneyInput, useLoad, useToast } from '../ui/kit.jsx'

const SCOPE = { invoice: 'Toàn hóa đơn', category: 'Nhóm hàng', product: 'Sản phẩm' }
const STATUS = { active: ['Đang bật', 'green'], paused: ['Tạm dừng', 'yellow'], expired: ['Hết hạn', 'red'] }

function PromoForm({ initial, onClose, onSaved }) {
  const toast = useToast()
  const now = new Date()
  const plus30 = new Date(Date.now() + 30 * 86400000)
  const local = (d) => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16)
  const [f, setF] = useState(initial ? { ...initial, start_at: toLocalInput(initial.start_at), end_at: toLocalInput(initial.end_at) } : {
    code: '', name: '', promo_type: 'percent', scope: 'invoice', target_id: '', discount_value: '', max_discount: '',
    min_invoice_amount: 0, usage_limit: '', start_at: local(now), end_at: local(plus30), status: 'active',
  })
  const cats = useLoad(() => api.get('/categories'), [])
  const prods = useLoad(() => api.get('/products', { size: 200, status: 'active' }), [])
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })
  const save = async () => {
    const body = {
      code: f.code || null, name: f.name, promo_type: f.promo_type, scope: f.scope,
      target_id: f.scope === 'invoice' ? null : Number(f.target_id) || null, discount_value: Number(f.discount_value) || 0,
      max_discount: f.max_discount ? Number(f.max_discount) : null, min_invoice_amount: Number(f.min_invoice_amount) || 0,
      usage_limit: f.usage_limit ? Number(f.usage_limit) : null, start_at: f.start_at, end_at: f.end_at,
      status: f.status === 'expired' ? 'active' : f.status,
    }
    try {
      initial ? await api.put(`/promotions/${initial.id}`, body) : await api.post('/promotions', body)
      toast('Đã lưu khuyến mãi', 'success'); onSaved()
    } catch (e) { toast(e.message, 'error') }
  }
  return (
    <Modal title={initial ? 'Sửa khuyến mãi' : 'Tạo khuyến mãi'} onClose={onClose} size="wide" footer={<button className="btn primary" onClick={save}>Lưu</button>}>
      <div className="form-grid">
        <Field label="Tên chương trình" full><input value={f.name} onChange={set('name')} /></Field>
        <Field label="Mã voucher" hint="Bỏ trống: tự động áp dụng khi đủ điều kiện"><input value={f.code || ''} onChange={(e) => setF({ ...f, code: e.target.value.toUpperCase() })} /></Field>
        <Field label="Loại"><select value={f.promo_type} onChange={set('promo_type')}><option value="percent">Giảm phần trăm</option><option value="fixed_amount">Giảm số tiền</option></select></Field>
        <Field label={f.promo_type === 'percent' ? 'Giảm (%)' : 'Giảm (đồng)'}>
          {f.promo_type === 'percent' ? <input value={f.discount_value} onChange={set('discount_value')} inputMode="numeric" />
            : <MoneyInput value={f.discount_value} onChange={(v) => setF({ ...f, discount_value: v })} />}</Field>
        {f.promo_type === 'percent' && <Field label="Giảm tối đa (đồng)"><MoneyInput value={f.max_discount || ''} onChange={(v) => setF({ ...f, max_discount: v })} /></Field>}
        <Field label="Phạm vi"><select value={f.scope} onChange={set('scope')}>{Object.entries(SCOPE).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></Field>
        {f.scope === 'category' && <Field label="Nhóm hàng"><select value={f.target_id || ''} onChange={set('target_id')}><option value="">Chọn nhóm</option>
          {(cats.data || []).map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</select></Field>}
        {f.scope === 'product' && <Field label="Sản phẩm"><select value={f.target_id || ''} onChange={set('target_id')}><option value="">Chọn sản phẩm</option>
          {(prods.data?.items || []).map((p) => <option key={p.id} value={p.id}>{p.code} - {p.name}</option>)}</select></Field>}
        <Field label="Hóa đơn tối thiểu (đồng)"><MoneyInput value={f.min_invoice_amount} onChange={(v) => setF({ ...f, min_invoice_amount: v })} /></Field>
        <Field label="Số lượt dùng tối đa" hint="Bỏ trống: không giới hạn"><input value={f.usage_limit || ''} onChange={set('usage_limit')} inputMode="numeric" /></Field>
        <Field label="Bắt đầu"><input type="datetime-local" value={f.start_at} onChange={set('start_at')} /></Field>
        <Field label="Kết thúc"><input type="datetime-local" value={f.end_at} onChange={set('end_at')} /></Field>
      </div>
      <p className="muted small">Mỗi hóa đơn áp tối đa một khuyến mãi cấp hóa đơn; mỗi sản phẩm chỉ nhận khuyến mãi giảm nhiều tiền nhất (BR-05, BR-06).</p>
    </Modal>
  )
}

export default function Promotions() {
  const { user } = useAuth()
  const owner = user.role === 'owner'
  const toast = useToast()
  const [status, setStatus] = useState('')
  const [dialog, setDialog] = useState(null)
  const { data, loading, error, reload } = useLoad(() => api.get('/promotions', { status }), [status])
  const toggle = async (p) => {
    try { await api.put(`/promotions/${p.id}/status`, { status: p.status === 'active' ? 'paused' : 'active' }); reload() } catch (e) { toast(e.message, 'error') }
  }
  const value = (p) => (p.promo_type === 'percent' ? `${p.discount_value}%${p.max_discount ? ` (tối đa ${money(p.max_discount)})` : ''}` : money(p.discount_value))
  return (
    <div className="card">
      <div className="toolbar">
        <label>Trạng thái<select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">Tất cả</option><option value="running">Đang áp dụng</option>
          {Object.entries(STATUS).map(([k, [v]]) => <option key={k} value={k}>{v}</option>)}</select></label>
        {owner && <div className="actions"><button className="btn primary" onClick={() => setDialog({})}><Icon name="plus" />Tạo khuyến mãi</button></div>}
      </div>
      <ErrorBox error={error} />
      {loading && !data ? <Loading /> : data && (!data.length ? <Empty title="Chưa có khuyến mãi" /> : (
        <div className="table-wrap"><table>
          <thead><tr><th>Chương trình</th><th>Mã</th><th>Giảm</th><th>Áp dụng cho</th><th className="right">Đơn tối thiểu</th><th>Thời gian</th><th className="right">Đã dùng</th><th>Trạng thái</th>{owner && <th />}</tr></thead>
          <tbody>{data.map((p) => (
            <tr key={p.id}>
              <td className="strong">{p.name}</td><td>{p.code ? <span className="badge blue">{p.code}</span> : <span className="muted small">Tự động</span>}</td>
              <td>{value(p)}</td><td>{SCOPE[p.scope]}{p.target_name ? `: ${p.target_name}` : ''}</td>
              <td className="right num">{p.min_invoice_amount ? money(p.min_invoice_amount) : '-'}</td>
              <td className="small">{fmtDateTime(p.start_at)}<br />{fmtDateTime(p.end_at)}</td>
              <td className="right">{num(p.used_count)}{p.usage_limit ? ` / ${num(p.usage_limit)}` : ''}</td>
              <td><span className={`badge ${STATUS[p.status][1]}`}>{STATUS[p.status][0]}</span>{p.running && <span className="badge cyan">Đang chạy</span>}</td>
              {owner && <td className="right nowrap">
                {p.status !== 'expired' && <button className="btn sm" onClick={() => toggle(p)}>{p.status === 'active' ? 'Tạm dừng' : 'Bật lại'}</button>}
                <button className="btn sm" onClick={() => setDialog({ p })}><Icon name="edit" /></button></td>}
            </tr>
          ))}</tbody>
        </table></div>
      ))}
      {dialog && <PromoForm initial={dialog.p} onClose={() => setDialog(null)} onSaved={() => { setDialog(null); reload() }} />}
    </div>
  )
}
