import { useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import { ThemeToggle } from '../Shell.jsx'
import Icon from '../ui/Icon.jsx'
import { Modal, useToast } from '../ui/kit.jsx'

const DEMO = [
  ['admin', 'admin123', 'Quản trị', 'shield'],
  ['chucuahang', 'owner123', 'Chủ cửa hàng', 'store'],
  ['nhanvien01', 'staff123', 'Nhân viên', 'user'],
]

function ForgotDialog({ onClose }) {
  const toast = useToast()
  const [step, setStep] = useState(1)
  const [f, setF] = useState({ username: '', code: '', new_password: '' })
  const [err, setErr] = useState('')
  const send = async () => {
    setErr('')
    try { toast((await api.post('/auth/forgot-password', { username: f.username })).message, 'success'); setStep(2) } catch (e) { setErr(e.message) }
  }
  const reset = async () => {
    setErr('')
    try { toast((await api.post('/auth/reset-password', f)).message, 'success'); onClose() } catch (e) { setErr(e.message) }
  }
  return (
    <Modal title="Quên mật khẩu" onClose={onClose} size="narrow" footer={step === 1
      ? <button className="btn primary" onClick={send} disabled={!f.username}>Gửi mã xác nhận</button>
      : <button className="btn primary" onClick={reset} disabled={!f.code || !f.new_password}>Đặt lại mật khẩu</button>}>
      <p className="muted mt-0">Mã 6 số được gửi tới email của tài khoản. Tài khoản chưa có email hãy nhờ quản trị viên đặt lại.</p>
      <div className="stack">
        <label>Tên đăng nhập<input value={f.username} onChange={(e) => setF({ ...f, username: e.target.value })} /></label>
        {step === 2 && <>
          <label>Mã xác nhận<input value={f.code} onChange={(e) => setF({ ...f, code: e.target.value })} /></label>
          <label>Mật khẩu mới<input type="password" value={f.new_password} placeholder="Tối thiểu 8 ký tự, có chữ và số"
            onChange={(e) => setF({ ...f, new_password: e.target.value })} /></label>
        </>}
        <p className="error">{err}</p>
      </div>
    </Modal>
  )
}

export default function Login() {
  const { login } = useAuth()
  const [form, setForm] = useState({ username: '', password: '', remember: true })
  const [show, setShow] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [forgot, setForgot] = useState(false)

  const submit = async (e, creds) => {
    e?.preventDefault()
    const { username, password } = creds || form
    setBusy(true); setError('')
    try { await login(username.trim(), password, form.remember) } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  return (
    <section className="auth">
      <aside className="auth-hero">
        <img className="auth-hero-img" src="/static/img/login-bg.webp" alt="" aria-hidden="true" />
        <div className="auth-hero-inner">
          <div className="auth-logo"><span className="brand-mark"><Icon name="store" /></span>TechStore AI</div>
          <div>
            <h1 className="auth-title">Quản lý bán hàng<br /><span className="accent-text">thiết bị điện tử</span></h1>
            <p className="auth-lead">Bán hàng tại quầy, serial và bảo hành, đổi trả 24 giờ, khuyến mãi, tích điểm, nhập kho và báo cáo. Trợ lý AI tư vấn sản phẩm và phân tích doanh thu từ dữ liệu thật.</p>
            <span className="auth-pill">Đề tài 01 · Nhóm 1</span>
          </div>
          <div className="auth-copy">© 2026 TechStore AI</div>
        </div>
      </aside>
      <main className="auth-main">
        <div className="auth-top">
          <span className="muted">Giao diện</span>
          <div className="auth-top-actions"><ThemeToggle /></div>
        </div>
        <form className="auth-card" onSubmit={submit}>
          <div className="auth-card-brand"><span className="brand-mark"><Icon name="store" /></span>TechStore AI</div>
          <div>
            <h2 className="auth-card-title">Chào mừng trở lại</h2>
            <p className="muted auth-card-sub">Đăng nhập để tiếp tục vào hệ thống.</p>
          </div>
          <label>Tên đăng nhập
            <div className="input-icon"><Icon name="user" />
              <input value={form.username} autoComplete="username" required placeholder="Nhập tên đăng nhập"
                onChange={(e) => setForm({ ...form, username: e.target.value })} /></div>
          </label>
          <label>Mật khẩu
            <div className="input-icon has-action"><Icon name="lock" />
              <input type={show ? 'text' : 'password'} value={form.password} autoComplete="current-password" required
                placeholder="Nhập mật khẩu" onChange={(e) => setForm({ ...form, password: e.target.value })} />
              <button type="button" className="input-action" onClick={() => setShow(!show)} aria-label="Hiện mật khẩu"><Icon name="eye" /></button>
            </div>
          </label>
          <div className="auth-row">
            <label className="checkbox"><input type="checkbox" checked={form.remember}
              onChange={(e) => setForm({ ...form, remember: e.target.checked })} />Ghi nhớ đăng nhập</label>
            <button type="button" className="link-btn" onClick={() => setForgot(true)}>Quên mật khẩu?</button>
          </div>
          <button className="btn primary block lg" type="submit" disabled={busy}>{busy ? 'Đang đăng nhập...' : 'Đăng nhập'}</button>
          <p className="error" role="alert">{error}</p>
          <div className="auth-divider">Tài khoản dữ liệu mẫu</div>
          <div className="demo-grid">
            {DEMO.map(([u, p, label, icon]) => (
              <button key={u} type="button" className="btn" onClick={(e) => { setForm({ ...form, username: u, password: p }); submit(e, { username: u, password: p }) }}>
                <Icon name={icon} />{label}
              </button>
            ))}
          </div>
          <p className="auth-secure"><Icon name="shield" /> Sai mật khẩu 5 lần liên tiếp tài khoản bị khóa 15 phút</p>
        </form>
        <div className="auth-foot"><span>Phiên bản 2.0</span><a href="/docs" target="_blank" rel="noopener">Tài liệu API</a></div>
      </main>
      {forgot && <ForgotDialog onClose={() => setForgot(false)} />}
    </section>
  )
}
