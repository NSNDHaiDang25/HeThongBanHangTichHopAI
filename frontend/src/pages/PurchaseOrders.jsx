// Phiếu nhập hàng (UC-36, UC-37): nháp -> xác nhận nhập kho -> hủy
import { useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import { PO_STATUS, daysAgo, fmtDateTime, money, num, today } from '../format.js'
import Icon from '../ui/Icon.jsx'
import { Badge, ConfirmDialog, Empty, ErrorBox, Loading, Modal, MoneyInput, Pager, useLoad, useToast } from '../ui/kit.jsx'

function ProductPicker({ onPick }) {
  const [q, setQ] = useState('')
  const { data } = useLoad(() => (q.trim().length >= 1 ? api.get('/products', { q, size: 8 }) : Promise.resolve(null)), [q])
  return (
    <div className="combo">
      <div className="input-icon"><Icon name="search" /><input placeholder="Thêm sản phẩm: gõ SKU hoặc tên" value={q} onChange={(e) => setQ(e.target.value)} /></div>
      {data?.items?.length > 0 && q && (
        <div className="combo-list">{data.items.map((p) => (
          <button key={p.id} className="combo-item" onClick={() => { onPick(p); setQ('') }}>
            <span className="strong">{p.code}</span> {p.name} <span className="muted small">tồn {p.stock}{p.track_serial ? ' · serial' : ''}</span>
          </button>
        ))}</div>
      )}
    </div>
  )
}

function POForm({ initial, onClose, onSaved }) {
  const { user } = useAuth()
  const owner = user.role === 'owner'
  const toast = useToast()
  const sups = useLoad(() => api.get('/suppliers', { status: 'active' }), [])
  const [supplier, setSupplier] = useState(initial?.supplier_id || '')
  const [note, setNote] = useState(initial?.note || '')
  const [lines, setLines] = useState(() => (initial?.items || []).map((it) => ({
    product: { id: it.product_id, code: it.product_code, name: it.product_name, track_serial: it.track_serial },
    quantity: it.quantity, unit_cost: it.unit_cost ?? '', serials: (it.serials || []).join('\n'),
  })))
  const add = (p) => setLines((ls) => (ls.some((l) => l.product.id === p.id) ? ls
    : [...ls, { product: p, quantity: 1, unit_cost: owner ? p.cost_price || '' : '', serials: '' }]))
  const upd = (i, k, v) => setLines((ls) => ls.map((l, j) => (j === i ? { ...l, [k]: v } : l)))
  const total = lines.reduce((s, l) => s + (Number(l.unit_cost) || 0) * (Number(l.quantity) || 0), 0)
  const save = async (confirm) => {
    const body = {
      supplier_id: Number(supplier) || null, note: note || null, confirm,
      items: lines.map((l) => ({
        product_id: l.product.id, quantity: Number(l.quantity) || 0, unit_cost: owner && l.unit_cost !== '' ? Number(l.unit_cost) : null,
        serials: l.product.track_serial ? l.serials.split(/[\s,;]+/).map((s) => s.trim()).filter(Boolean) : [],
      })),
    }
    try {
      initial ? await api.put(`/purchase-orders/${initial.id}`, body) : await api.post('/purchase-orders', body)
      toast(confirm ? 'Đã nhập kho' : 'Đã lưu phiếu nháp', 'success'); onSaved()
    } catch (e) { toast(e.message, 'error') }
  }
  return (
    <Modal title={initial ? `Sửa phiếu ${initial.code}` : 'Lập phiếu nhập'} onClose={onClose} size="wide" footer={<>
      <button className="btn" onClick={() => save(false)} disabled={!lines.length}><Icon name="save" />Lưu nháp</button>
      {owner && <button className="btn primary" onClick={() => save(true)} disabled={!lines.length}><Icon name="check" />Lưu và nhập kho</button>}
    </>}>
      <div className="form-grid">
        <label>Nhà cung cấp<select value={supplier} onChange={(e) => setSupplier(e.target.value)}>
          <option value="">Chọn nhà cung cấp</option>{(sups.data || []).map((s) => <option key={s.id} value={s.id}>{s.code} - {s.name}</option>)}</select></label>
        <label>Ghi chú<input value={note} onChange={(e) => setNote(e.target.value)} /></label>
      </div>
      <div className="mt-3"><ProductPicker onPick={add} /></div>
      {!owner && <p className="note small">Nhân viên lập phiếu nháp không kèm giá nhập; chủ cửa hàng điền giá và xác nhận nhập kho.</p>}
      {lines.length > 0 && (
        <div className="table-wrap mt-3"><table className="import-table">
          <thead><tr><th>Sản phẩm</th><th style={{ width: 90 }}>Số lượng</th>{owner && <th style={{ width: 150 }}>Giá nhập</th>}<th>Serial / IMEI</th>{owner && <th className="right">Thành tiền</th>}<th /></tr></thead>
          <tbody>{lines.map((l, i) => {
            const count = l.serials.split(/[\s,;]+/).filter(Boolean).length
            return (
              <tr key={l.product.id}>
                <td className="strong">{l.product.name}<div className="muted small">{l.product.code}</div></td>
                <td><input value={l.quantity} inputMode="numeric" onChange={(e) => upd(i, 'quantity', e.target.value.replace(/\D/g, ''))} /></td>
                {owner && <td><MoneyInput value={l.unit_cost} onChange={(v) => upd(i, 'unit_cost', v)} /></td>}
                <td>{l.product.track_serial ? <>
                  <textarea rows={2} placeholder="Mỗi serial một dòng (có thể quét liên tiếp)" value={l.serials} onChange={(e) => upd(i, 'serials', e.target.value)} />
                  <div className={`small ${count === Number(l.quantity) ? 'text-success' : 'muted'}`}>{count}/{l.quantity} serial</div>
                </> : <span className="muted small">Không theo serial</span>}</td>
                {owner && <td className="right num">{money((Number(l.unit_cost) || 0) * (Number(l.quantity) || 0))}</td>}
                <td><button className="btn ghost sm icon-only" onClick={() => setLines((ls) => ls.filter((_, j) => j !== i))}><Icon name="x" /></button></td>
              </tr>
            )
          })}</tbody>
        </table></div>
      )}
      {owner && lines.length > 0 && <div className="totals-box"><div className="row strong"><span className="flex-1">Tổng tiền nhập</span><span className="num">{money(total)}</span></div></div>}
    </Modal>
  )
}

function PODetail({ id, onClose, onChanged }) {
  const { user } = useAuth()
  const owner = user.role === 'owner'
  const toast = useToast()
  const { data: po, reload } = useLoad(() => api.get(`/purchase-orders/${id}`), [id])
  const [dialog, setDialog] = useState(null)
  if (!po) return <Modal title="Phiếu nhập" onClose={onClose}><Loading /></Modal>
  const act = async (fn, msg) => { try { await fn(); toast(msg, 'success'); reload(); onChanged() } catch (e) { toast(e.message, 'error'); throw e } }
  const mine = po.user_id === user.id
  return (
    <Modal title={`Phiếu nhập ${po.code}`} onClose={onClose} size="wide" footer={<>
      {po.status === 'draft' && (owner || mine) && <>
        <button className="btn danger" onClick={() => act(() => api.del(`/purchase-orders/${po.id}`), 'Đã xóa phiếu nháp').then(onClose)}><Icon name="trash" />Xóa nháp</button>
        <button className="btn" onClick={() => setDialog('edit')}><Icon name="edit" />Sửa</button>
      </>}
      {owner && po.status === 'draft' && <button className="btn primary" onClick={() => act(() => api.post(`/purchase-orders/${po.id}/confirm`), 'Đã xác nhận nhập kho')}><Icon name="check" />Xác nhận nhập kho</button>}
      {owner && po.status === 'confirmed' && <button className="btn danger" onClick={() => setDialog('cancel')}>Hủy phiếu</button>}
    </>}>
      <div className="info-list">
        <div><span className="muted">Trạng thái</span><span><Badge map={PO_STATUS} value={po.status} /></span></div>
        <div><span className="muted">Nhà cung cấp</span><span>{po.supplier || '-'}</span></div>
        <div><span className="muted">Người lập</span><span>{po.user_name}</span></div>
        <div><span className="muted">Ngày lập</span><span>{fmtDateTime(po.created_at)}</span></div>
        <div><span className="muted">Nhập kho lúc</span><span>{fmtDateTime(po.received_at) || '-'}</span></div>
        {po.cancel_reason && <div><span className="muted">Lý do hủy</span><span>{po.cancel_reason}</span></div>}
      </div>
      <div className="table-wrap"><table>
        <thead><tr><th>Sản phẩm</th><th className="right">SL</th>{owner && <><th className="right">Giá nhập</th><th className="right">Thành tiền</th></>}<th>Serial</th></tr></thead>
        <tbody>{po.items.map((it) => (
          <tr key={it.id}><td>{it.product_name}<div className="muted small">{it.product_code}</div></td><td className="right">{it.quantity}</td>
            {owner && <><td className="right num">{money(it.unit_cost)}</td><td className="right num">{money(it.line_total)}</td></>}
            <td className="small">{it.serials.join(', ') || '-'}</td></tr>
        ))}</tbody>
      </table></div>
      {owner && <div className="totals-box"><div className="row strong"><span className="flex-1">Tổng tiền</span><span className="num">{money(po.total)}</span></div></div>}
      {dialog === 'edit' && <POForm initial={po} onClose={() => setDialog(null)} onSaved={() => { setDialog(null); reload(); onChanged() }} />}
      {dialog === 'cancel' && <ConfirmDialog title="Hủy phiếu nhập đã xác nhận" danger reason="Lý do hủy"
        message="Tồn kho sẽ bị trừ lại và giá vốn tính ngược. Chỉ hủy được khi tồn còn đủ và chưa bán serial nào của phiếu."
        onClose={() => setDialog(null)} onConfirm={(reason) => act(() => api.post(`/purchase-orders/${po.id}/cancel`, { reason }), 'Đã hủy phiếu nhập')} />}
    </Modal>
  )
}

export default function PurchaseOrders() {
  const { user } = useAuth()
  const [f, setF] = useState({ status: '', q: '', date_from: daysAgo(89), date_to: today() })
  const [page, setPage] = useState(1)
  const [dialog, setDialog] = useState(null)
  const { data, loading, error, reload } = useLoad(() => api.get('/purchase-orders', { ...f, page, size: 20 }), [JSON.stringify(f), page])
  const set = (k) => (e) => { setPage(1); setF({ ...f, [k]: e.target.value }) }
  return (
    <div className="card">
      <div className="toolbar">
        <label className="grow">Tìm<input value={f.q} onChange={set('q')} placeholder="Mã phiếu, nhà cung cấp" /></label>
        <label>Trạng thái<select value={f.status} onChange={set('status')}><option value="">Tất cả</option>
          {Object.entries(PO_STATUS).map(([k, [v]]) => <option key={k} value={k}>{v}{data?.counts?.[k] ? ` (${data.counts[k]})` : ''}</option>)}</select></label>
        <label>Từ ngày<input type="date" value={f.date_from} onChange={set('date_from')} /></label>
        <label>Đến ngày<input type="date" value={f.date_to} onChange={set('date_to')} /></label>
        <div className="actions"><button className="btn primary" onClick={() => setDialog({ type: 'new' })}><Icon name="plus" />Lập phiếu nhập</button></div>
      </div>
      <ErrorBox error={error} />
      {loading && !data ? <Loading /> : data && (!data.items.length ? <Empty title="Chưa có phiếu nhập" /> : <>
        <div className="table-wrap"><table>
          <thead><tr><th>Mã phiếu</th><th>Ngày lập</th><th>Nhà cung cấp</th><th>Người lập</th><th className="right">Số lượng</th>{user.role !== 'staff' && <th className="right">Tổng tiền</th>}<th>Trạng thái</th></tr></thead>
          <tbody>{data.items.map((o) => (
            <tr key={o.id} className="clickable" onClick={() => setDialog({ type: 'detail', id: o.id })}>
              <td className="strong">{o.code}</td><td>{fmtDateTime(o.created_at)}</td><td>{o.supplier || '-'}</td><td>{o.user_name}</td>
              <td className="right">{num(o.quantity)}</td>{user.role !== 'staff' && <td className="right num">{money(o.total)}</td>}
              <td><Badge map={PO_STATUS} value={o.status} /></td>
            </tr>
          ))}</tbody>
        </table></div>
        <Pager page={page} size={20} total={data.total} onPage={setPage} />
      </>)}
      {dialog?.type === 'new' && <POForm onClose={() => setDialog(null)} onSaved={() => { setDialog(null); reload() }} />}
      {dialog?.type === 'detail' && <PODetail id={dialog.id} onClose={() => setDialog(null)} onChanged={reload} />}
    </div>
  )
}
