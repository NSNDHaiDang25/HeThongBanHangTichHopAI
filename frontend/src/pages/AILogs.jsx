// Nhật ký gọi AI (BR-44, bảng ai_logs). Nhân viên chỉ xem lượt của mình.
import { Fragment, useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import { fmtDateTime, num } from '../format.js'
import Icon from '../ui/Icon.jsx'
import { Badge, Empty, ErrorBox, Loading, Pager, useLoad } from '../ui/kit.jsx'
import { Kpi } from './Dashboard.jsx'

const FEATURE = { assistant: 'Trợ lý đa năng', advisor: 'Tư vấn sản phẩm', report: 'Báo cáo doanh thu', qa: 'Hỏi đáp dữ liệu' }
const STATUS = {
  success: ['Thành công', 'green'], fallback: ['Dự phòng', 'yellow'], timeout: ['Quá thời gian', 'red'],
  rate_limited: ['Hết lượt', 'red'], invalid_format: ['Sai định dạng', 'red'], rejected_sql: ['SQL bị chặn', 'red'], error: ['Lỗi', 'red'],
}

export default function AILogs() {
  const { user } = useAuth()
  const [f, setF] = useState({ feature: '', status: '' })
  const [page, setPage] = useState(1)
  const [open, setOpen] = useState(null)
  const { data, error } = useLoad(() => api.get('/ai/logs', { ...f, page, size: 30 }), [f.feature, f.status, page])
  const ai = useLoad(() => api.get('/ai/status'), [])
  const set = (k) => (e) => { setPage(1); setF({ ...f, [k]: e.target.value }) }
  const sum = data?.summary || {}
  const total = Object.values(sum).reduce((a, b) => a + b, 0)
  return (
    <div className="stack">
      {user.role !== 'staff' && data && (
        <div className="grid kpi">
          <Kpi featured icon="sparkles" label="Tổng lượt gọi" value={num(total)} sub={ai.data ? `Giới hạn ${ai.data.rate_limit_per_hour || 'không giới hạn'} lượt / người / giờ` : ''} />
          <Kpi icon="check" color="green" label="Thành công" value={num(sum.success || 0)} sub={total ? `${(((sum.success || 0) / total) * 100).toFixed(0)}%` : ''} />
          <Kpi icon="clock" label="Thời gian phản hồi TB" value={data.avg_latency_ms ? `${num(data.avg_latency_ms)} ms` : '-'} sub="Lượt thành công (NFR-PER-06)" />
          <Kpi icon="alert" color={total - (sum.success || 0) ? 'yellow' : ''} label="Dự phòng / lỗi" value={num(total - (sum.success || 0))}
            sub={Object.entries(sum).filter(([k]) => k !== 'success').map(([k, v]) => `${STATUS[k]?.[0] || k} ${v}`).join(' · ')} />
        </div>
      )}
      <div className="card">
        <div className="toolbar">
          <label>Tính năng<select value={f.feature} onChange={set('feature')}><option value="">Tất cả</option>
            {Object.entries(FEATURE).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></label>
          <label>Trạng thái<select value={f.status} onChange={set('status')}><option value="">Tất cả</option>
            {Object.entries(STATUS).map(([k, [v]]) => <option key={k} value={k}>{v}</option>)}</select></label>
          {ai.data && <div className="actions"><span className="muted small">Model: {ai.data.model || 'chưa sẵn sàng'} · Prompt tư vấn {ai.data.advisor_prompt_version}</span></div>}
        </div>
        <ErrorBox error={error} />
        {!data ? <Loading /> : !data.items.length ? <Empty icon="history" title="Chưa có lượt gọi AI" /> : <>
          <div className="table-wrap"><table>
            <thead><tr><th>Thời gian</th>{user.role !== 'staff' && <th>Người dùng</th>}<th>Tính năng</th><th>Câu hỏi</th><th>Trạng thái</th><th className="right">Độ trễ</th><th>Model</th></tr></thead>
            <tbody>{data.items.map((r) => (
              <Fragment key={r.id}>
                <tr className="clickable" onClick={() => setOpen(open === r.id ? null : r.id)} aria-expanded={open === r.id}>
                  <td className="small nowrap">{fmtDateTime(r.created_at)}</td>
                  {user.role !== 'staff' && <td>{r.user_name}</td>}
                  <td>{FEATURE[r.feature] || r.feature}{r.prompt_version && r.prompt_version !== '-' && <span className="badge">{r.prompt_version}</span>}</td>
                  <td className="small">{r.question?.length > 90 ? `${r.question.slice(0, 90)}…` : r.question}</td>
                  <td><Badge map={STATUS} value={r.status} />{r.retry_count > 0 && <span className="muted small"> · thử lại {r.retry_count}</span>}</td>
                  <td className="right num">{r.latency_ms ? `${num(r.latency_ms)} ms` : '-'}</td>
                  <td className="small muted">{r.model_name}</td>
                </tr>
                {open === r.id && (
                  <tr><td colSpan={7}>
                    <div className="stack">
                      <div><div className="muted small">Câu hỏi (đã che số điện thoại, email)</div><div>{r.question}</div></div>
                      {r.generated_sql && <div><div className="muted small">SQL do AI sinh</div><pre className="sql-code"><code>{r.generated_sql}</code></pre></div>}
                      <div><div className="muted small">Phản hồi</div><pre className="sql-code">{r.response || '(trống)'}</pre></div>
                    </div>
                  </td></tr>
                )}
              </Fragment>
            ))}</tbody>
          </table></div>
          <Pager page={page} size={30} total={data.total} onPage={setPage} />
        </>}
      </div>
    </div>
  )
}
