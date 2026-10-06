// Quản lý người dùng (UC-03 đến UC-05, FR-USR-01..05), chỉ quản trị viên
import { useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import { ROLE_VI, fmtDateTime } from '../format.js'
import Icon from '../ui/Icon.jsx'
import { ConfirmDialog, Empty, ErrorBox, Field, Loading, Modal, useLoad, useToast } from '../ui/kit.jsx'

function UserForm({ initial, onClose, onSaved }) {
  const toast = useToast()
  const [f, setF] = useState(initial
    ? { full_name: initial.full_name, role: initial.role, email: initial.email || '', phone: initial.phone || '', is_active: initial.is_active }
    : { username: '', full_name: '', password: '', role: 'staff', email: '', phone: '' })
  const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })
  const save = async () => {
    setBusy(true)
    try {
      const body = { ...f, email: f.email.trim() || null, phone: f.phone.trim() || null }
      initial ? await api.put(`/users/${initial.id}`, body) : await api.post('/users', body)
      toast(initial ? 'Đã cập nhật tài khoản' : `Đã tạo tài khoản ${f.username}. Người dùng phải đổi mật khẩu ở lần đăng nhập đầu`, 'success')
      onSaved()
    } catch (e) { toast(e.message, 'error') } finally { setBusy(false) }
  }
  return (
    <Modal title={initial ? `Sửa tài khoản ${initial.username}` : 'Tạo tài khoản'} onClose={onClose}
      footer={<button className="btn primary" disabled={busy} onClick={save}><Icon name="save" />Lưu</button>}>
      <div className="form-grid">
        {!initial && <Field label="Tên đăng nhập"><input value={f.username} onChange={set('username')} autoComplete="off" /></Field>}
        <Field label="Họ tên"><input value={f.full_name} onChange={set('full_name')} /></Field>
        {!initial && <Field label="Mật khẩu tạm" hint="Tối thiểu 8 ký tự, có chữ và số"><input type="text" value={f.password} onChange={set('password')} autoComplete="new-password" /></Field>}
        <Field label="Vai trò"><select value={f.role} onChange={set('role')}>
          {Object.entries(ROLE_VI).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></Field>
        <Field label="Email" hint="Dùng để nhận mã khi quên mật khẩu"><input type="email" value={f.email} onChange={set('email')} /></Field>
        <Field label="Số điện thoại"><input value={f.phone} onChange={set('phone')} inputMode="tel" /></Field>
        {initial && <Field label="Trạng thái"><select value={f.is_active ? '1' : '0'} onChange={(e) => setF({ ...f, is_active: e.target.value === '1' })}>
          <option value="1">Đang hoạt động</option><option value="0">Đã khóa</option></select></Field>}
      </div>
    </Modal>
  )
}

function ResetPassword({ u, onClose }) {
  const toast = useToast()
  const [pw, setPw] = useState('')
  const save = async () => {
    try { toast((await api.post(`/users/${u.id}/reset-password`, { new_password: pw })).message, 'success'); onClose() } catch (e) { toast(e.message, 'error') }
  }
  return (
    <Modal title={`Đặt lại mật khẩu cho ${u.username}`} size="narrow" onClose={onClose}
      footer={<button className="btn primary" disabled={pw.length < 8} onClick={save}><Icon name="key" />Đặt mật khẩu tạm</button>}>
      <Field label="Mật khẩu tạm" hint="Người dùng phải đổi mật khẩu khi đăng nhập lại"><input value={pw} onChange={(e) => setPw(e.target.value)} autoComplete="new-password" /></Field>
    </Modal>
  )
}

export default function Users() {
  const { user: me } = useAuth()
  const toast = useToast()
  const { data, error, reload } = useLoad(() => api.get('/users'), [])
  const [dialog, setDialog] = useState(null)
  const act = async (fn, msg) => { try { await fn(); toast(msg, 'success'); reload() } catch (e) { toast(e.message, 'error') } }
  const locked = (u) => u.locked_until && new Date(u.locked_until) > new Date()
  const pending = (data || []).filter((u) => u.pending)
  return (
    <div className="stack">
      {pending.length > 0 && (
        <div className="card">
          <div className="card-head"><h2><Icon name="clock" />Yêu cầu tạo tài khoản chờ duyệt</h2></div>
          <div className="table-wrap"><table>
            <thead><tr><th>Tên đăng nhập</th><th>Họ tên</th><th>Email</th><th>Vai trò yêu cầu</th><th /></tr></thead>
            <tbody>{pending.map((u) => (
              <tr key={u.id}><td className="strong">{u.username}</td><td>{u.full_name}</td><td>{u.email}</td><td>{ROLE_VI[u.role]}</td>
                <td className="right nowrap">
                  <button className="btn sm primary" onClick={() => act(() => api.put(`/users/${u.id}`, { is_active: true }), `Đã duyệt ${u.username}`)}>Duyệt</button>
                  <button className="btn sm danger" onClick={() => setDialog({ reject: u })}>Từ chối</button></td></tr>
            ))}</tbody>
          </table></div>
        </div>
      )}
      <div className="card">
        <div className="toolbar"><div className="actions"><button className="btn primary" onClick={() => setDialog({ form: {} })}><Icon name="plus" />Tạo tài khoản</button></div></div>
        <ErrorBox error={error} />
        {!data ? <Loading /> : !data.length ? <Empty title="Chưa có người dùng" /> : (
          <div className="table-wrap"><table>
            <thead><tr><th>Tên đăng nhập</th><th>Họ tên</th><th>Vai trò</th><th>Liên hệ</th><th>Trạng thái</th><th>Đăng nhập gần nhất</th><th /></tr></thead>
            <tbody>{data.filter((u) => !u.pending).map((u) => (
              <tr key={u.id}>
                <td className="strong">{u.username}{u.id === me.id && <span className="badge blue">Bạn</span>}</td>
                <td>{u.full_name}</td><td>{ROLE_VI[u.role]}</td>
                <td className="small">{u.email}<div className="muted">{u.phone}</div></td>
                <td>{!u.is_active ? <span className="badge red">Đã khóa</span> : locked(u) ? <span className="badge yellow" title={`Đến ${fmtDateTime(u.locked_until)}`}>Khóa tạm</span> : <span className="badge green">Hoạt động</span>}
                  {u.must_change_password && <span className="badge">Chờ đổi mật khẩu</span>}</td>
                <td className="small">{fmtDateTime(u.last_login_at) || '-'}</td>
                <td className="right nowrap">
                  {locked(u) && <button className="btn sm" onClick={() => act(() => api.put(`/users/${u.id}`, { unlock: true }), `Đã mở khóa ${u.username}`)}>Mở khóa</button>}
                  <button className="btn sm" title="Đặt lại mật khẩu" onClick={() => setDialog({ reset: u })}><Icon name="key" /></button>
                  <button className="btn sm" title="Sửa" onClick={() => setDialog({ form: { u } })}><Icon name="edit" /></button>
                </td>
              </tr>
            ))}</tbody>
          </table></div>
        )}
      </div>
      {dialog?.form && <UserForm initial={dialog.form.u} onClose={() => setDialog(null)} onSaved={() => { setDialog(null); reload() }} />}
      {dialog?.reset && <ResetPassword u={dialog.reset} onClose={() => setDialog(null)} />}
      {dialog?.reject && <ConfirmDialog danger title="Từ chối yêu cầu" confirmText="Từ chối" message={`Xóa yêu cầu tạo tài khoản ${dialog.reject.username}?`}
        onClose={() => setDialog(null)} onConfirm={() => act(() => api.del(`/users/${dialog.reject.id}`), 'Đã từ chối yêu cầu')} />}
    </div>
  )
}
