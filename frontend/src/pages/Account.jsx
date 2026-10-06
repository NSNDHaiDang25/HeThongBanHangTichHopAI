import { useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import { ROLE_VI, fmtDateTime } from '../format.js'
import Icon from '../ui/Icon.jsx'
import { useToast } from '../ui/kit.jsx'

export function ChangePasswordForm({ forced, onDone }) {
  const toast = useToast()
  const [f, setF] = useState({ old_password: '', new_password: '', confirm: '' })
  const [err, setErr] = useState('')
  const submit = async (e) => {
    e.preventDefault()
    setErr('')
    if (f.new_password !== f.confirm) { setErr('Mật khẩu nhập lại không khớp'); return }
    try {
      await api.post('/auth/change-password', { old_password: f.old_password, new_password: f.new_password })
      toast('Đã đổi mật khẩu', 'success')
      setF({ old_password: '', new_password: '', confirm: '' })
      onDone?.()
    } catch (e2) { setErr(e2.message) }
  }
  return (
    <form className="stack" onSubmit={submit}>
      {forced && <p className="note mt-0">Tài khoản mới hoặc vừa được đặt lại mật khẩu: bạn cần đổi mật khẩu trước khi sử dụng.</p>}
      <label>Mật khẩu hiện tại<input type="password" required value={f.old_password} onChange={(e) => setF({ ...f, old_password: e.target.value })} /></label>
      <label>Mật khẩu mới<input type="password" required value={f.new_password} placeholder="Tối thiểu 8 ký tự, có chữ và số"
        onChange={(e) => setF({ ...f, new_password: e.target.value })} /></label>
      <label>Nhập lại mật khẩu mới<input type="password" required value={f.confirm} onChange={(e) => setF({ ...f, confirm: e.target.value })} /></label>
      <p className="error">{err}</p>
      <button className="btn primary" type="submit"><Icon name="key" />Đổi mật khẩu</button>
    </form>
  )
}

export function ForcedChange() {
  const { refresh, logout } = useAuth()
  return (
    <section className="auth">
      <main className="auth-main" style={{ margin: '0 auto' }}>
        <div className="auth-card">
          <div className="auth-card-brand"><span className="brand-mark"><Icon name="store" /></span>TechStore AI</div>
          <h2 className="auth-card-title">Đổi mật khẩu</h2>
          <ChangePasswordForm forced onDone={refresh} />
          <button className="link-btn" onClick={logout}>Đăng xuất</button>
        </div>
      </main>
    </section>
  )
}

export default function Account() {
  const { user } = useAuth()
  return (
    <div className="grid two w-lg">
      <div className="card">
        <div className="card-head"><h2><Icon name="user" />Thông tin tài khoản</h2></div>
        <div className="info-list">
          <div><span className="muted">Tên đăng nhập</span><span className="strong">{user.username}</span></div>
          <div><span className="muted">Họ tên</span><span>{user.full_name}</span></div>
          <div><span className="muted">Vai trò</span><span>{ROLE_VI[user.role]}</span></div>
          <div><span className="muted">Email</span><span>{user.email || 'Chưa có'}</span></div>
          <div><span className="muted">Đăng nhập gần nhất</span><span>{fmtDateTime(user.last_login_at)}</span></div>
        </div>
      </div>
      <div className="card">
        <div className="card-head"><h2><Icon name="key" />Đổi mật khẩu</h2></div>
        <ChangePasswordForm />
      </div>
    </div>
  )
}
