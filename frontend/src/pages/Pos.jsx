// Màn hình bán hàng tại quầy (SRS 8.2 hình 8.2, UC-19 đến UC-27)
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { api, openFile } from '../api.js'
import { money, num } from '../format.js'
import Icon from '../ui/Icon.jsx'
import { Modal, MoneyInput, Thumb, useToast } from '../ui/kit.jsx'

const DRAFT_KEY = 'pos-draft-id'

function stockBadge(p) {
  if (p.stock <= 0) return <span className="badge red">Hết hàng</span>
  if (p.stock_state === 'low') return <span className="badge yellow">Sắp hết · {p.stock}</span>
  return <span className="badge green">Còn {p.stock}</span>
}

// ---------------------------------------------------------------- Chọn serial
function SerialPicker({ product, taken, onPick, onClose }) {
  const [serials, setSerials] = useState(null)
  const [q, setQ] = useState('')
  useEffect(() => { api.get(`/products/${product.id}/serials`, { status: 'in_stock' }).then(setSerials) }, [product.id])
  const list = (serials || []).filter((s) => !taken.has(s.id) && s.serial_no.includes(q.trim().toUpperCase()))
  return (
    <Modal title={`Chọn serial / IMEI: ${product.name}`} onClose={onClose} size="narrow">
      <input autoFocus placeholder="Quét hoặc gõ serial" value={q} onChange={(e) => setQ(e.target.value)}
        onKeyDown={(e) => { if (e.key === 'Enter' && list.length === 1) onPick(list[0]) }} />
      <div className="list mt-3">
        {serials === null && <div className="muted">Đang tải...</div>}
        {serials && !list.length && <div className="muted">Không còn serial phù hợp trong kho</div>}
        {list.map((s) => (
          <button key={s.id} className="combo-item" onClick={() => onPick(s)}>
            <Icon name="barcode" /><span className="strong">{s.serial_no}</span>
          </button>
        ))}
      </div>
    </Modal>
  )
}

// ---------------------------------------------------------------- Chọn / thêm khách
function CustomerBox({ customer, onChange }) {
  const toast = useToast()
  const [q, setQ] = useState('')
  const [results, setResults] = useState([])
  const [adding, setAdding] = useState(null)
  useEffect(() => {
    if (q.trim().length < 2) { setResults([]); return }
    const t = setTimeout(() => api.get('/customers', { q, size: 8, active: true, full_phone: true })
      .then((r) => setResults(r.items)).catch(() => {}), 250)
    return () => clearTimeout(t)
  }, [q])
  const create = async () => {
    try {
      const c = await api.post('/customers', adding)
      onChange(c); setAdding(null); setQ(''); toast('Đã thêm khách hàng', 'success')
    } catch (e) { toast(e.message, 'error') }
  }
  if (customer) {
    return (
      <div className="customer-pill">
        <Icon name="user" />
        <div className="flex-1">
          <div className="strong">{customer.name} <span className="badge cyan">{customer.tier_name}</span></div>
          <div className="muted small">{customer.phone} · {num(customer.loyalty_points)} điểm</div>
        </div>
        <button className="btn ghost sm icon-only" onClick={() => onChange(null)} aria-label="Bỏ chọn khách"><Icon name="x" /></button>
      </div>
    )
  }
  const digits = q.replace(/\D/g, '')
  return (
    <div className="combo">
      <div className="input-icon"><Icon name="user" />
        <input placeholder="Khách lẻ · tìm SĐT hoặc tên khách" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      {q.trim().length >= 2 && (
        <div className="combo-list">
          {results.map((c) => (
            <button key={c.id} className="combo-item" onClick={() => { onChange(c); setQ('') }}>
              <span className="strong">{c.name}</span><span className="muted small">{c.phone} · {c.tier_name} · {num(c.loyalty_points)} điểm</span>
            </button>
          ))}
          <button className="combo-item create" onClick={() => setAdding({ name: digits ? '' : q, phone: digits || '', email: '' })}>
            <Icon name="plus" />Thêm khách mới
          </button>
        </div>
      )}
      {adding && (
        <Modal title="Thêm khách hàng" onClose={() => setAdding(null)} size="narrow"
          footer={<button className="btn primary" onClick={create}>Lưu khách hàng</button>}>
          <div className="stack">
            <label>Họ tên<input value={adding.name} onChange={(e) => setAdding({ ...adding, name: e.target.value })} /></label>
            <label>Số điện thoại<input value={adding.phone} onChange={(e) => setAdding({ ...adding, phone: e.target.value })} /></label>
            <label>Email (gửi hóa đơn)<input value={adding.email} onChange={(e) => setAdding({ ...adding, email: e.target.value })} /></label>
          </div>
        </Modal>
      )}
    </div>
  )
}

// ---------------------------------------------------------------- Chờ chuyển khoản
function TransferDialog({ invoice, onPaid, onClose }) {
  const toast = useToast()
  const [qr, setQr] = useState(null)
  const [left, setLeft] = useState(0)
  useEffect(() => { api.get(`/invoices/${invoice.id}/qr`).then(setQr).catch((e) => toast(e.message, 'error')) }, [invoice.id, toast])
  useEffect(() => {
    if (!qr?.deadline) return
    const tick = () => setLeft(Math.max(0, Math.floor((new Date(qr.deadline) - Date.now()) / 1000)))
    tick()
    const t = setInterval(tick, 1000)
    return () => clearInterval(t)
  }, [qr])
  const confirm = async () => {
    try { onPaid(await api.post(`/invoices/${invoice.id}/confirm-payment`, {})) } catch (e) { toast(e.message, 'error') }
  }
  return (
    <Modal title={`Chờ chuyển khoản · ${invoice.code}`} onClose={onClose} footer={<>
      <button className="btn" onClick={onClose}>Để sau (giữ hàng)</button>
      <button className="btn primary" onClick={confirm} disabled={left === 0 && !!qr}><Icon name="check" />Đã nhận tiền</button>
    </>}>
      {!qr ? <div className="muted">Đang tạo mã VietQR...</div> : (
        <div className="qr-pay">
          <div className="qr-box" dangerouslySetInnerHTML={{ __html: qr.svg }} />
          <div className="stack">
            <div className="qr-amount">{money(qr.amount)}</div>
            <div className="bank-info">
              <div><span className="muted">Ngân hàng</span> <span className="strong">{qr.bank_name}</span></div>
              <div><span className="muted">Số tài khoản</span> <span className="strong">{qr.account_no}</span></div>
              <div><span className="muted">Chủ tài khoản</span> <span>{qr.account_name}</span></div>
              <div><span className="muted">Nội dung</span> <span className="strong">{qr.content}</span></div>
            </div>
            <div className={`badge ${left < 300 ? 'red' : 'yellow'}`}>
              <Icon name="clock" />Giữ hàng còn {Math.floor(left / 60)}:{String(left % 60).padStart(2, '0')}
            </div>
            <p className="muted small m-0">Chỉ bấm "Đã nhận tiền" khi đã thấy tiền về tài khoản (BR-28). Quá hạn hóa đơn tự hủy và hoàn tồn kho.</p>
          </div>
        </div>
      )}
    </Modal>
  )
}

// ---------------------------------------------------------------- Hóa đơn đã thanh toán
function PaidDialog({ invoice, onClose }) {
  const toast = useToast()
  const email = async () => {
    try { toast((await api.post(`/invoices/${invoice.id}/email`, {})).message, 'success') } catch (e) { toast(e.message, 'error') }
  }
  return (
    <Modal title="Thanh toán thành công" onClose={onClose} size="narrow" footer={<>
      <button className="btn" onClick={() => openFile(`/invoices/${invoice.id}/pdf`)}><Icon name="printer" />In hóa đơn</button>
      {invoice.customer_id && <button className="btn" onClick={email}><Icon name="mail" />Gửi email</button>}
      <button className="btn primary" onClick={onClose}>Đơn mới</button>
    </>}>
      <div className="center stack">
        <div className="kpi-icon green" style={{ margin: '0 auto' }}><Icon name="check" /></div>
        <div className="strong">{invoice.code}</div>
        <div className="qr-amount">{money(invoice.total)}</div>
        {invoice.change ? <div>Tiền thừa trả khách: <span className="strong">{money(invoice.change)}</span></div> : null}
        {invoice.points_earned ? <div className="muted">Khách được cộng {num(invoice.points_earned)} điểm</div> : null}
        {(invoice.warnings || []).map((w) => <div key={w} className="note">{w}</div>)}
      </div>
    </Modal>
  )
}

// ---------------------------------------------------------------- Màn hình chính
export default function Pos() {
  const toast = useToast()
  const scanRef = useRef(null)
  const [cats, setCats] = useState([])
  const [cat, setCat] = useState('')
  const [products, setProducts] = useState([])
  const [search, setSearch] = useState('')
  const [lines, setLines] = useState([])  // {product, quantity, serial}
  const [customer, setCustomer] = useState(null)
  const [promo, setPromo] = useState('')
  const [points, setPoints] = useState('')
  const [method, setMethod] = useState('cash')
  const [cash, setCash] = useState('')
  const [ref, setRef] = useState('')
  const [cart, setCart] = useState(null)
  const [cartErr, setCartErr] = useState('')
  const [draftId, setDraftId] = useState(() => { try { return Number(localStorage.getItem(DRAFT_KEY)) || null } catch { return null } })
  const [picker, setPicker] = useState(null)
  const [pending, setPending] = useState(null)
  const [paid, setPaid] = useState(null)
  const [busy, setBusy] = useState(false)
  const [holdMinutes, setHoldMinutes] = useState(30)
  const [restored, setRestored] = useState(!draftId)  // giỏ nháp đã khôi phục xong (hoặc không có)
  const location = useLocation()
  const navigate = useNavigate()

  const loadProducts = useCallback(() => {
    api.get('/products', { q: search, category_id: cat, status: 'active', size: 60 }).then((r) => setProducts(r.items)).catch(() => {})
  }, [search, cat])
  useEffect(() => {
    api.get('/categories', { active_only: true }).then(setCats)
    api.get('/settings').then((r) => {
      const m = r.items.find((x) => x.key === 'pending_payment_minutes')
      if (m) setHoldMinutes(m.value)
    }).catch(() => {})
  }, [])
  useEffect(() => { const t = setTimeout(loadProducts, 200); return () => clearTimeout(t) }, [loadProducts])
  useEffect(() => { scanRef.current?.focus() }, [])

  // Khôi phục giỏ nháp khi mở lại trang (FR-SAL-07)
  useEffect(() => {
    if (!draftId) return
    api.get(`/invoices/${draftId}`).then(async (inv) => {
      if (inv.status !== 'draft') { localStorage.removeItem(DRAFT_KEY); setDraftId(null); return }
      const restored = await Promise.all(inv.items.map(async (it) => ({
        product: await api.get(`/products/${it.product_id}`), quantity: it.quantity,
        serial: it.serial_id ? { id: it.serial_id, serial_no: it.serial_no } : null,
      })))
      setLines(restored)
      if (inv.customer_id) setCustomer(await api.get(`/customers/${inv.customer_id}`))
      if (inv.promotion_code) setPromo(inv.promotion_code)
      if (restored.length) toast(`Đã khôi phục giỏ hàng nháp ${inv.code}`)
    }).catch(() => { localStorage.removeItem(DRAFT_KEY); setDraftId(null) }).finally(() => setRestored(true))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const body = useMemo(() => ({
    items: lines.map((l) => ({ product_id: l.product.id, quantity: l.quantity, serial_id: l.serial?.id || null })),
    customer_id: customer?.id || null, promo_code: promo.trim() || null, points_used: Number(points) || 0,
  }), [lines, customer, promo, points])

  // Tính lại tiền mỗi khi giỏ thay đổi (FR-SAL-05) và tự lưu nháp
  useEffect(() => {
    if (!lines.length) { setCart(null); setCartErr(''); return }
    const t = setTimeout(async () => {
      try { setCart(await api.post('/invoices/preview', body)); setCartErr('') } catch (e) { setCartErr(e.message) }
    }, 250)
    return () => clearTimeout(t)
  }, [body, lines.length])
  useEffect(() => {
    if (!lines.length) return
    const t = setTimeout(async () => {
      try {
        const d = await api.post('/invoices/drafts', { ...body, draft_id: draftId, promo_code: cartErr ? null : body.promo_code, points_used: cartErr ? 0 : body.points_used })
        if (d.id !== draftId) { setDraftId(d.id); try { localStorage.setItem(DRAFT_KEY, d.id) } catch { /* bỏ qua */ } }
      } catch { /* lưu nháp lỗi không chặn bán hàng */ }
    }, 1500)
    return () => clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [body])

  const taken = useMemo(() => new Set(lines.filter((l) => l.serial).map((l) => l.serial.id)), [lines])

  const addProduct = (p, serial = null) => {
    if (p.stock <= 0) { toast(`${p.name} đã hết hàng`, 'error'); return }
    if (p.track_serial && !serial) { setPicker(p); return }
    setLines((ls) => {
      if (serial) {
        if (ls.some((l) => l.serial?.id === serial.id)) { toast('Serial này đã có trong giỏ', 'error'); return ls }
        return [...ls, { product: p, quantity: 1, serial }]
      }
      const i = ls.findIndex((l) => l.product.id === p.id && !l.serial)
      if (i >= 0) {
        if (ls[i].quantity + 1 > p.stock) { toast(`Chỉ còn ${p.stock} ${p.name}`, 'error'); return ls }
        return ls.map((l, j) => (j === i ? { ...l, quantity: l.quantity + 1 } : l))
      }
      return [...ls, { product: p, quantity: 1, serial: null }]
    })
    scanRef.current?.focus()
  }

  // "Thêm vào giỏ" từ chatbot tư vấn: chờ khôi phục giỏ nháp xong rồi mới thêm, sau đó xóa state để F5 không thêm lần nữa
  useEffect(() => {
    const code = location.state?.addCode
    if (!restored || !code) return
    navigate(location.pathname, { replace: true, state: null })
    api.get(`/products/by-code/${encodeURIComponent(code)}`)
      .then((p) => { addProduct(p); if (!p.track_serial && p.stock > 0) toast(`Đã thêm "${p.name}" vào giỏ`, 'success') })
      .catch((err) => toast(err.message, 'error'))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [restored, location.state])

  // FR-SAL-01: máy quét gửi mã như bàn phím rồi Enter
  const onScan = async (e) => {
    if (e.key !== 'Enter') return
    const code = e.target.value.trim()
    if (!code) return
    e.target.value = ''
    try {
      const p = await api.get(`/products/by-code/${encodeURIComponent(code)}`)
      if (p.serial) {
        if (p.serial.status !== 'in_stock') { toast(`Serial ${p.serial.serial_no} không còn trong kho`, 'error'); return }
        addProduct(p, p.serial)
      } else addProduct(p)
    } catch (err) { toast(err.message, 'error') }
  }

  const setQty = (i, q) => setLines((ls) => ls.map((l, j) => {
    if (j !== i) return l
    const qty = Math.max(1, Math.min(q, l.product.stock))
    if (q > l.product.stock) toast(`Chỉ còn ${l.product.stock} ${l.product.name}`, 'error')
    return { ...l, quantity: qty }
  }))

  const reset = () => {
    setLines([]); setCustomer(null); setPromo(''); setPoints(''); setCash(''); setRef(''); setMethod('cash'); setCart(null)
    setDraftId(null); try { localStorage.removeItem(DRAFT_KEY) } catch { /* bỏ qua */ }
    scanRef.current?.focus()
  }

  const checkout = async () => {
    if (!cart) return
    if (method === 'cash' && cash !== '' && cash < cart.total) { toast('Tiền khách đưa ít hơn số phải trả', 'error'); return }
    if (method === 'card' && !ref.trim()) { toast('Nhập mã giao dịch in trên biên lai máy POS', 'error'); return }
    setBusy(true)
    try {
      const inv = await api.post('/invoices', {
        ...body, draft_id: draftId, payment_method: method, cash_received: method === 'cash' && cash !== '' ? cash : null,
        payment_ref: ref.trim() || null,
      })
      try { localStorage.removeItem(DRAFT_KEY) } catch { /* bỏ qua */ }
      setDraftId(null)
      if (inv.status === 'pending_payment') setPending(inv)
      else { setPaid(inv); reset() }
    } catch (e) { toast(e.message, 'error') } finally { setBusy(false) }
  }

  const quickCash = cart ? [...new Set([cart.total, Math.ceil(cart.total / 50000) * 50000, Math.ceil(cart.total / 100000) * 100000,
    Math.ceil(cart.total / 500000) * 500000])].slice(0, 4) : []

  return (
    <div className="pos">
      <section className="pos-products card">
        <div className="toolbar">
          <div className="grow input-icon"><Icon name="scan" />
            <input ref={scanRef} placeholder="Quét mã vạch / SKU / serial rồi Enter" onKeyDown={onScan} aria-label="Ô quét mã" />
          </div>
          <div className="grow input-icon"><Icon name="search" />
            <input placeholder="Tìm theo tên hoặc SKU (không cần dấu)" value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
        </div>
        <div className="chips mb-3">
          <button className={`chip ${cat === '' ? 'active' : ''}`} onClick={() => setCat('')}>Tất cả</button>
          {cats.map((c) => <button key={c.id} className={`chip ${cat === c.id ? 'active' : ''}`} onClick={() => setCat(c.id)}>{c.name}</button>)}
        </div>
        <div className="product-grid">
          {products.map((p) => (
            <button key={p.id} className="product-tile" disabled={p.stock <= 0} onClick={() => addProduct(p)}>
              <div className="tile-img"><Thumb url={p.image_url} name={p.name} size="lg" /></div>
              <div className="tile-body">
                <div className="tile-name">{p.name}</div>
                <div className="tile-meta muted small">{p.code}{p.track_serial ? ' · serial' : ''}</div>
                <div className="tile-foot"><span className="price">{money(p.sale_price)}</span>{stockBadge(p)}</div>
              </div>
            </button>
          ))}
        </div>
      </section>

      <section className="cart card">
        <div className="card-head"><h2><Icon name="cart" />Giỏ hàng {draftId ? <span className="badge">Nháp đã lưu</span> : null}</h2>
          {lines.length > 0 && <button className="btn ghost sm" onClick={reset}><Icon name="trash" />Xóa giỏ</button>}
        </div>
        <CustomerBox customer={customer} onChange={(c) => { setCustomer(c); setPoints('') }} />
        <div className="cart-items mt-3">
          {!lines.length && <div className="empty-state compact dashed"><Icon name="scan" /><div>Quét mã hoặc chọn sản phẩm để thêm vào giỏ</div></div>}
          {lines.map((l, i) => {
            const pl = cart?.lines?.[i]
            return (
              <div key={`${l.product.id}-${l.serial?.id || i}`} className="cart-row">
                <Thumb url={l.product.image_url} name={l.product.name} size="sm" />
                <div className="flex-1">
                  <div className="strong">{l.product.name}</div>
                  <div className="muted small">{money(l.product.sale_price)}{l.serial ? ` · ${l.serial.serial_no}` : ''}</div>
                  {pl?.line_promo > 0 && <div className="small text-success">{pl.promo_name}: -{money(pl.line_promo)}</div>}
                </div>
                {l.serial ? <span className="qty muted">x1</span> : (
                  <div className="qty">
                    <button className="btn sm icon-only" onClick={() => setQty(i, l.quantity - 1)} aria-label="Giảm"><Icon name="minus" /></button>
                    <input value={l.quantity} inputMode="numeric" onChange={(e) => setQty(i, Number(e.target.value.replace(/\D/g, '')) || 1)} />
                    <button className="btn sm icon-only" onClick={() => setQty(i, l.quantity + 1)} aria-label="Tăng"><Icon name="plus" /></button>
                  </div>
                )}
                <div className="right num strong" style={{ minWidth: 96 }}>{money(pl ? pl.line_total : l.product.sale_price * l.quantity)}</div>
                <button className="btn ghost sm icon-only" onClick={() => setLines((ls) => ls.filter((_, j) => j !== i))} aria-label="Bỏ dòng"><Icon name="x" /></button>
              </div>
            )
          })}
        </div>

        {lines.length > 0 && <>
          <div className="discount-row mt-3">
            <div className="input-icon flex-1"><Icon name="tag" />
              <input placeholder="Mã voucher" value={promo} onChange={(e) => setPromo(e.target.value.toUpperCase())} />
            </div>
            {customer && (
              <div className="input-icon flex-1"><Icon name="award" />
                <input placeholder={`Dùng điểm (tối đa ${num(cart?.points_max || 0)})`} value={points} inputMode="numeric"
                  onChange={(e) => setPoints(e.target.value.replace(/\D/g, ''))} />
              </div>
            )}
          </div>
          {cartErr && <p className="error mt-2">{cartErr}</p>}
          {cart && (
            <div className="totals mt-3">
              <div className="row"><span className="flex-1 muted">Tạm tính</span><span className="num">{money(cart.subtotal)}</span></div>
              {cart.promotions.map((p) => (
                <div className="row" key={p.id}><span className="flex-1 muted">{p.scope === 'invoice' ? 'Khuyến mãi' : 'KM sản phẩm'}: {p.name}</span><span className="num text-success">-{money(p.amount)}</span></div>
              ))}
              {cart.points_discount > 0 && <div className="row"><span className="flex-1 muted">Dùng {num(cart.points_used)} điểm</span><span className="num text-success">-{money(cart.points_discount)}</span></div>}
              <div className="row text-lg strong"><span className="flex-1">Khách phải trả</span><span className="num">{money(cart.total)}</span></div>
              <div className="row small muted"><span className="flex-1">VAT đã gồm</span><span className="num">{money(cart.vat_amount)}</span></div>
              {customer && <div className="row small muted"><span className="flex-1">Điểm dự kiến được cộng</span><span className="num">+{num(cart.points_earned)}</span></div>}
              {cart.warnings.map((w) => <div key={w} className="note small">{w}</div>)}
            </div>
          )}

          <div className="pay-methods mt-3">
            {[['cash', 'cash', 'Tiền mặt'], ['bank_transfer', 'qr', 'Chuyển khoản'], ['card', 'card', 'Thẻ']].map(([m, ic, label]) => (
              <button key={m} className={`pay-method ${method === m ? 'active' : ''}`} onClick={() => setMethod(m)}><Icon name={ic} />{label}</button>
            ))}
          </div>
          {method === 'cash' && cart && (
            <div className="pay-detail">
              <label>Tiền khách đưa<MoneyInput value={cash} onChange={setCash} placeholder="Bỏ trống nếu đưa vừa đủ" /></label>
              <div className="cash-chips">{quickCash.map((v) => <button key={v} className="chip" onClick={() => setCash(v)}>{num(v)}</button>)}</div>
              {cash !== '' && cash >= cart.total && <div className="change-row">Tiền thừa: <span className="strong">{money(cash - cart.total)}</span></div>}
            </div>
          )}
          {method === 'card' && <div className="pay-detail"><label>Mã giao dịch trên biên lai POS<input value={ref} onChange={(e) => setRef(e.target.value)} /></label></div>}
          {method === 'bank_transfer' && <p className="muted small">Hệ thống tạo mã VietQR theo hóa đơn, giữ hàng {holdMinutes} phút chờ khách chuyển khoản.</p>}
          <button className="btn primary block lg mt-3" disabled={!cart || !!cartErr || busy} onClick={checkout}>
            <Icon name="check" />{method === 'bank_transfer' ? 'Tạo mã QR thanh toán' : `Thanh toán ${cart ? money(cart.total) : ''}`}
          </button>
        </>}
      </section>

      {picker && <SerialPicker product={picker} taken={taken} onClose={() => setPicker(null)}
        onPick={(s) => { addProduct(picker, s); setPicker(null) }} />}
      {pending && <TransferDialog invoice={pending} onClose={() => { setPending(null); reset(); toast('Hóa đơn đang chờ chuyển khoản, xem ở trang Hóa đơn') }}
        onPaid={(inv) => { setPending(null); setPaid(inv); reset() }} />}
      {paid && <PaidDialog invoice={paid} onClose={() => { setPaid(null); scanRef.current?.focus() }} />}
    </div>
  )
}
