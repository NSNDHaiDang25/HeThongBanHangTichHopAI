// Tồn kho: cảnh báo sắp hết, thẻ kho, báo cáo tồn (UC-38 đến UC-40, UC-43)
import { useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import { MOVE_VI, daysAgo, fmtDateTime, money, num, today } from '../format.js'
import Icon from '../ui/Icon.jsx'
import { Empty, ErrorBox, Loading, Pager, Thumb, useLoad } from '../ui/kit.jsx'

function LowStock() {
  const { data, loading } = useLoad(() => api.get('/products', { stock: 'low', status: 'active', size: 100 }), [])
  const out = useLoad(() => api.get('/products', { stock: 'out', status: 'active', size: 100 }), [])
  const rows = [...(out.data?.items || []), ...(data?.items || [])]
  if (loading) return <Loading />
  return !rows.length ? <Empty icon="check" title="Không có sản phẩm sắp hết hàng" /> : (
    <div className="table-wrap"><table>
      <thead><tr><th>Sản phẩm</th><th className="right">Tồn</th><th className="right">Ngưỡng</th><th>Tình trạng</th></tr></thead>
      <tbody>{rows.map((p) => (
        <tr key={p.id}><td><div className="cell-product"><Thumb url={p.image_url} name={p.name} size="sm" /><div><div className="strong">{p.name}</div><div className="muted small">{p.code}</div></div></div></td>
          <td className="right strong">{p.stock}</td><td className="right muted">{p.min_stock}</td>
          <td>{p.stock <= 0 ? <span className="badge red">Hết hàng</span> : <span className="badge yellow">Sắp hết hàng</span>}</td></tr>
      ))}</tbody>
    </table></div>
  )
}

function StockCard() {
  const [f, setF] = useState({ product_id: '', type: '', date_from: daysAgo(29), date_to: today() })
  const [page, setPage] = useState(1)
  const products = useLoad(() => api.get('/products', { size: 200 }), [])
  const { data, loading, error } = useLoad(() => api.get('/stock-movements', { ...f, page, size: 50 }), [JSON.stringify(f), page])
  const set = (k) => (e) => { setPage(1); setF({ ...f, [k]: e.target.value }) }
  return <>
    <div className="toolbar">
      <label className="grow">Sản phẩm<select value={f.product_id} onChange={set('product_id')}><option value="">Tất cả sản phẩm</option>
        {(products.data?.items || []).map((p) => <option key={p.id} value={p.id}>{p.code} - {p.name}</option>)}</select></label>
      <label>Loại<select value={f.type} onChange={set('type')}><option value="">Tất cả</option>
        {Object.entries(MOVE_VI).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></label>
      <label>Từ ngày<input type="date" value={f.date_from} onChange={set('date_from')} /></label>
      <label>Đến ngày<input type="date" value={f.date_to} onChange={set('date_to')} /></label>
    </div>
    <ErrorBox error={error} />
    {loading && !data ? <Loading /> : data && (!data.items.length ? <Empty title="Không có biến động" /> : <>
      <div className="table-wrap"><table>
        <thead><tr><th>Thời gian</th><th>Sản phẩm</th><th>Loại</th><th>Chứng từ</th><th className="right">Tồn trước</th><th className="right">Thay đổi</th><th className="right">Tồn sau</th><th>Ghi chú</th></tr></thead>
        <tbody>{data.items.map((m) => (
          <tr key={m.id}><td>{fmtDateTime(m.created_at)}</td><td>{m.product_name}<div className="muted small">{m.product_code}</div></td>
            <td>{MOVE_VI[m.type] || m.type}</td><td>{m.ref_code || '-'}</td><td className="right">{m.stock_before}</td>
            <td className={`right strong ${m.change > 0 ? 'text-success' : 'text-danger'}`}>{m.change > 0 ? '+' : ''}{m.change}</td>
            <td className="right">{m.stock_after}</td><td className="small muted">{m.note || ''}</td></tr>
        ))}</tbody>
      </table></div>
      <Pager page={page} size={50} total={data.total} onPage={setPage} />
    </>)}
  </>
}

function InventoryReport() {
  const { data, loading } = useLoad(() => api.get('/reports/inventory'), [])
  if (loading || !data) return <Loading />
  const s = data.summary
  return <>
    <div className="grid kpi">
      <div className="card kpi-card featured"><div className="kpi-icon"><Icon name="package" /></div><div><div className="label">Giá trị tồn (giá vốn)</div><div className="value">{money(s.value_at_cost)}</div><div className="sub">{num(s.units)} sản phẩm trong kho</div></div></div>
      <div className="card kpi-card"><div className="kpi-icon"><Icon name="tag" /></div><div><div className="label">Giá trị theo giá bán</div><div className="value">{money(s.value_at_sale)}</div></div></div>
      <div className="card kpi-card"><div className="kpi-icon red"><Icon name="alert" /></div><div><div className="label">Không bán được 30 ngày</div><div className="value">{data.unsold.length}</div></div></div>
    </div>
    <div className="grid two mt-3">
      <div><h3>Theo nhóm hàng</h3><div className="table-wrap"><table><thead><tr><th>Nhóm</th><th className="right">SL</th><th className="right">Giá vốn</th></tr></thead>
        <tbody>{data.by_category.map((c) => <tr key={c.category}><td>{c.category}</td><td className="right">{num(c.units)}</td><td className="right num">{money(c.value_at_cost)}</td></tr>)}</tbody></table></div></div>
      <div><h3>Không bán được trong 30 ngày</h3>{!data.unsold.length ? <p className="muted">Không có</p> : <div className="table-wrap"><table><thead><tr><th>Sản phẩm</th><th className="right">Tồn</th><th className="right">Vốn đọng</th></tr></thead>
        <tbody>{data.unsold.map((p) => <tr key={p.code}><td>{p.name}<div className="muted small">{p.code}</div></td><td className="right">{p.stock}</td><td className="right num">{money(p.value_at_cost)}</td></tr>)}</tbody></table></div>}</div>
    </div>
  </>
}

export default function Inventory() {
  const { user } = useAuth()
  const tabs = [['low', 'Sắp hết hàng', 'alert'], ['card', 'Thẻ kho', 'arrows'], ...(user.role === 'owner' ? [['report', 'Báo cáo tồn kho', 'chart']] : [])]
  const [tab, setTab] = useState('low')
  return (
    <div className="card">
      <div className="chips mb-4">{tabs.map(([k, label, icon]) => (
        <button key={k} className={`chip ${tab === k ? 'active' : ''}`} onClick={() => setTab(k)}><Icon name={icon} />{label}</button>))}</div>
      {tab === 'low' && <LowStock />}
      {tab === 'card' && <StockCard />}
      {tab === 'report' && <InventoryReport />}
    </div>
  )
}
