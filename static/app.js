/* SalesAI - giao diện SPA thuần JavaScript (không cần build). */
'use strict';

// ============================================================ Icon (nét 2px, 24x24, cùng một phong cách)
const ICONS = {
  store: '<path d="m2 7 4.4-4.4A2 2 0 0 1 7.8 2h8.4a2 2 0 0 1 1.4.6L22 7"/><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"/><path d="M2 7h20"/><path d="M22 7v3a2 2 0 0 1-2 2 2.7 2.7 0 0 1-2-.8 2.7 2.7 0 0 1-2 .8 2.7 2.7 0 0 1-2-.8 2.7 2.7 0 0 1-2 .8 2.7 2.7 0 0 1-2-.8 2.7 2.7 0 0 1-2 .8 2.7 2.7 0 0 1-2-.8A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"/>',
  dashboard: '<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
  cart: '<circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2 2h2l2.7 12.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L22 7H5.1"/>',
  receipt: '<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/><path d="M8 8h8"/><path d="M8 12h8"/><path d="M8 16h5"/>',
  users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9"/><path d="M16 3.1a4 4 0 0 1 0 7.8"/>',
  user: '<circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/>',
  package: '<path d="m7.5 4.3 9 5.1"/><path d="M21 8a2 2 0 0 0-1-1.7l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.7l7 4a2 2 0 0 0 2 0l7-4a2 2 0 0 0 1-1.7Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
  tag: '<path d="M12.6 2.6A2 2 0 0 0 11.2 2H4a2 2 0 0 0-2 2v7.2a2 2 0 0 0 .6 1.4l8.7 8.7a2.4 2.4 0 0 0 3.4 0l6.6-6.6a2.4 2.4 0 0 0 0-3.4z"/><circle cx="7.5" cy="7.5" r="1"/>',
  truck: '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.6a1 1 0 0 0-.2-.6l-3.5-4.4a1 1 0 0 0-.8-.4H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
  arrows: '<path d="M8 3 4 7l4 4"/><path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/>',
  chart: '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
  message: '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
  sparkles: '<path d="M9.9 15.5a2 2 0 0 0-1.4-1.4l-6.1-1.6a.5.5 0 0 1 0-1l6.1-1.6a2 2 0 0 0 1.4-1.4l1.6-6.1a.5.5 0 0 1 1 0l1.6 6.1a2 2 0 0 0 1.4 1.4l6.1 1.6a.5.5 0 0 1 0 1l-6.1 1.6a2 2 0 0 0-1.4 1.4l-1.6 6.1a.5.5 0 0 1-1 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/>',
  help: '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>',
  shield: '<path d="M20 13c0 5-3.5 7.5-7.7 9a1 1 0 0 1-.7 0C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.2-2.7a1.2 1.2 0 0 1 1.5 0C14.5 3.8 17 5 19 5a1 1 0 0 1 1 1z"/>',
  logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/>',
  plus: '<path d="M5 12h14"/><path d="M12 5v14"/>',
  minus: '<path d="M5 12h14"/>',
  edit: '<path d="M21.2 6.8a1 1 0 0 0-4-4L3.8 16.2a2 2 0 0 0-.5.8l-1.3 4.4a.5.5 0 0 0 .6.6l4.4-1.3a2 2 0 0 0 .8-.5z"/><path d="m15 5 4 4"/>',
  trash: '<path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
  printer: '<path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 9V3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v6"/><rect x="6" y="14" width="12" height="8" rx="1"/>',
  download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
  upload: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  image: '<rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.1-3.1a2 2 0 0 0-2.8 0L6 21"/>',
  menu: '<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>',
  cash: '<rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/>',
  bank: '<path d="M3 22h18"/><path d="M6 18v-7"/><path d="M10 18v-7"/><path d="M14 18v-7"/><path d="M18 18v-7"/><path d="m12 2 8 5H4z"/>',
  card: '<rect width="20" height="14" x="2" y="5" rx="2"/><path d="M2 10h20"/><path d="M6 15h4"/>',
  qr: '<rect width="5" height="5" x="3" y="3" rx="1"/><rect width="5" height="5" x="16" y="3" rx="1"/><rect width="5" height="5" x="3" y="16" rx="1"/><path d="M21 16h-3a2 2 0 0 0-2 2v3"/><path d="M21 21v.01"/><path d="M12 7v3a2 2 0 0 1-2 2H7"/><path d="M3 12h.01"/><path d="M12 3h.01"/><path d="M12 16v.01"/><path d="M16 12h1"/><path d="M21 12v.01"/><path d="M12 21v-1"/>',
  scan: '<path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M7 12h10"/>',
  barcode: '<path d="M3 5v14"/><path d="M8 5v14"/><path d="M12 5v14"/><path d="M17 5v14"/><path d="M21 5v14"/>',
  alert: '<path d="m21.7 18-8-14a2 2 0 0 0-3.5 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
  copy: '<rect width="14" height="14" x="8" y="8" rx="2"/><path d="M4 16a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2"/>',
  send: '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
  clipboard: '<rect width="8" height="4" x="8" y="2" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/>',
  up: '<path d="m22 7-8.5 8.5-5-5L2 17"/><path d="M16 7h6v6"/>',
  down: '<path d="m22 17-8.5-8.5-5 5L2 7"/><path d="M16 17h6v-6"/>',
  chevron: '<path d="m6 9 6 6 6-6"/>',
  calendar: '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>',
  wallet: '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
  refresh: '<path d="M3 12a9 9 0 1 0 9-9 9.8 9.8 0 0 0-6.7 2.7L3 8"/><path d="M3 3v5h5"/>',
  panel: '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/>',
  'arrow-up': '<path d="m5 12 7-7 7 7"/><path d="M12 19V5"/>',
  expand: '<path d="M15 3h6v6"/><path d="M9 21H3v-6"/><path d="m21 3-7 7"/><path d="m3 21 7-7"/>',
  camera: '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3z"/><circle cx="12" cy="13" r="3"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.9 4.9 1.4 1.4"/><path d="m17.7 17.7 1.4 1.4"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.3 17.7-1.4 1.4"/><path d="m19.1 4.9-1.4 1.4"/>',
  moon: '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
  lock: '<rect width="18" height="11" x="3" y="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
  eye: '<path d="M2.1 12.3a1 1 0 0 1 0-.6 10.8 10.8 0 0 1 19.8 0 1 1 0 0 1 0 .6 10.8 10.8 0 0 1-19.8 0"/><circle cx="12" cy="12" r="3"/>',
  'eye-off': '<path d="M10.7 5.1A10.7 10.7 0 0 1 21.9 11.7a1 1 0 0 1 0 .6 10.7 10.7 0 0 1-1.4 2.6"/><path d="M14.1 14.2a3 3 0 0 1-4.2-4.2"/><path d="M17.5 17.5a10.8 10.8 0 0 1-15.4-5.2 1 1 0 0 1 0-.6 10.8 10.8 0 0 1 4.4-5.2"/><path d="m2 2 20 20"/>',
  headset: '<path d="M3 11h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-5Zm0 0a9 9 0 1 1 18 0m0 0v5a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3Z"/><path d="M21 16v2a4 4 0 0 1-4 4h-5"/>',
  key: '<path d="m15.5 7.5 2.3 2.3a1 1 0 0 0 1.4 0l2.1-2.1a1 1 0 0 0 0-1.4L19 4"/><path d="m21 2-9.6 9.6"/><circle cx="7.5" cy="15.5" r="5.5"/>',
  settings: '<path d="M12.2 2h-.4a2 2 0 0 0-2 2v.2a2 2 0 0 1-1 1.7l-.4.3a2 2 0 0 1-2 0l-.2-.1a2 2 0 0 0-2.7.7l-.2.4a2 2 0 0 0 .7 2.7l.2.1a2 2 0 0 1 1 1.7v.5a2 2 0 0 1-1 1.7l-.2.1a2 2 0 0 0-.7 2.7l.2.4a2 2 0 0 0 2.7.7l.2-.1a2 2 0 0 1 2 0l.4.3a2 2 0 0 1 1 1.7v.2a2 2 0 0 0 2 2h.4a2 2 0 0 0 2-2v-.2a2 2 0 0 1 1-1.7l.4-.3a2 2 0 0 1 2 0l.2.1a2 2 0 0 0 2.7-.7l.2-.4a2 2 0 0 0-.7-2.7l-.2-.1a2 2 0 0 1-1-1.7v-.5a2 2 0 0 1 1-1.7l.2-.1a2 2 0 0 0 .7-2.7l-.2-.4a2 2 0 0 0-2.7-.7l-.2.1a2 2 0 0 1-2 0l-.4-.3a2 2 0 0 1-1-1.7V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>',
  database: '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/>',
  history: '<path d="M3 12a9 9 0 1 0 9-9 9.8 9.8 0 0 0-6.7 2.7L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>',
  undo: '<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>',
  wrench: '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z"/>',
  percent: '<path d="M19 5 5 19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
  building: '<rect width="16" height="20" x="4" y="2" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>',
  award: '<circle cx="12" cy="8" r="6"/><path d="M15.5 12.9 17 22l-5-3-5 3 1.5-9.1"/>',
  hash: '<path d="M4 9h16"/><path d="M4 15h16"/><path d="M10 3 8 21"/><path d="M16 3l-2 18"/>',
  sliders: '<path d="M4 21v-7"/><path d="M4 10V3"/><path d="M12 21v-9"/><path d="M12 8V3"/><path d="M20 21v-5"/><path d="M20 12V3"/><path d="M2 14h4"/><path d="M10 8h4"/><path d="M18 16h4"/>',
  layers: '<path d="m12.8 2.2 8.6 3.9a1 1 0 0 1 0 1.8l-8.6 3.9a2 2 0 0 1-1.6 0L2.6 7.9a1 1 0 0 1 0-1.8l8.6-3.9a2 2 0 0 1 1.6 0Z"/><path d="m22 17.6-9.2 4.2a2 2 0 0 1-1.6 0L2 17.6"/><path d="m22 12.6-9.2 4.2a2 2 0 0 1-1.6 0L2 12.6"/>',
  mail: '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
  file: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 13H8"/><path d="M16 17H8"/><path d="M16 13h-2"/>',
  pause: '<rect x="14" y="4" width="4" height="16" rx="1"/><rect x="6" y="4" width="4" height="16" rx="1"/>',
  gift: '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13"/><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"/><path d="M7.5 8a2.5 2.5 0 0 1 0-5A4.8 8 0 0 1 12 8a4.8 8 0 0 1 4.5-5 2.5 2.5 0 0 1 0 5"/>',
};
const icon = (name, cls = '') => `<svg class="i ${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ''}</svg>`;

// ============================================================ Tiện ích chung
// Chữ viết tắt tên cho ảnh đại diện: "Nhân viên bán hàng" -> "BH"
const initialsOf = (name) => String(name || '?').trim().split(/\s+/).slice(-2).map((w) => w[0]).join('').toUpperCase();
const newChatState = () => ({ sessionId: null, title: '', messages: [], pending: false, collapsed: false });
const S = { token: null, user: null, ai: null, payCfg: null, charts: [], categories: [], chat: { assistant: newChatState(), advisor: newChatState(), ask: newChatState() } };
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const money = (v) => (Number(v) || 0).toLocaleString('vi-VN') + ' ₫';
const num = (v) => (Number(v) || 0).toLocaleString('vi-VN');
const fmtDate = (s) => (s ? new Date(s).toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '');
const isoDate = (d) => { const x = new Date(d); x.setMinutes(x.getMinutes() - x.getTimezoneOffset()); return x.toISOString().slice(0, 10); };
const today = () => isoDate(new Date());
const daysAgo = (n) => { const d = new Date(); d.setDate(d.getDate() - n); return isoDate(d); };
const stamp = () => { const d = new Date(); const p = (n) => String(n).padStart(2, '0'); return `${String(d.getFullYear()).slice(2)}${p(d.getMonth() + 1)}${p(d.getDate())}${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`; };
// Ba vai trò độc lập (không kế thừa quyền của nhau): quản trị viên chỉ quản trị hệ thống, chủ cửa hàng quản lý kinh doanh,
// thu ngân bán hàng. Server luôn kiểm tra quyền; giao diện chỉ ẩn những gì vai trò không dùng được.
const isManager = () => S.user?.role === 'owner';  // chủ cửa hàng
const isAdmin = () => S.user?.role === 'admin';

const ROLE_VI = { admin: 'Quản trị viên', owner: 'Chủ cửa hàng', staff: 'Thu ngân' };
const GROUP_VI = { regular: 'Thường', vip: 'VIP', wholesale: 'Khách sỉ' };
const MOVE_VI = { import: 'Nhập hàng', sale: 'Bán hàng', cancel: 'Hủy hóa đơn', edit: 'Sửa hóa đơn', adjust: 'Kiểm kho', return: 'Khách trả hàng', import_cancel: 'Hủy phiếu nhập' };
const PAY = {
  cash: { label: 'Tiền mặt', icon: 'cash' },
  transfer: { label: 'Chuyển khoản', icon: 'bank' },
  card: { label: 'Quẹt thẻ', icon: 'card' },
  qr: { label: 'Quét mã QR', icon: 'qr' },
};
const payLabel = (m) => PAY[m]?.label || m;
const payCell = (m) => `<span class="nowrap">${icon(PAY[m]?.icon || 'wallet')} ${payLabel(m)}</span>`;
// Trạng thái hóa đơn; requested = đang chờ chủ cửa hàng duyệt yêu cầu hủy
const statusBadge = (s, requested) => s === 'paid'
  ? (requested ? '<span class="badge dot yellow">Chờ duyệt hủy</span>' : '<span class="badge dot green">Đã thanh toán</span>')
  : s === 'pending' ? '<span class="badge dot blue">Chưa thanh toán</span>' : '<span class="badge dot red">Đã hủy</span>';
const tierBadge = (t) => (t ? `<span class="badge cyan">${icon('award')} ${esc(t.name)}</span>` : '');
const serialChips = (list) => (list?.length ? `<div class="serial-chips">${list.map((s) => `<span class="serial-chip">${esc(s)}</span>`).join('')}</div>` : '');
const fmtDay = (s) => (s ? new Date(s).toLocaleDateString('vi-VN') : '');
const stockBadge = (p) => p.stock <= 0 ? '<span class="badge red">Hết hàng</span>'
  : p.stock <= p.min_stock ? `<span class="badge yellow">Sắp hết · ${p.stock}</span>` : `<span class="badge green">Còn ${p.stock}</span>`;
const groupBadge = (g) => `<span class="badge ${g === 'vip' ? 'yellow' : g === 'wholesale' ? 'blue' : ''}">${GROUP_VI[g] || g}</span>`;
const note = (text) => `<div class="note">${icon('alert')}<span>${esc(text)}</span></div>`;
const loading = (text = 'Đang tải...') => `<div class="loading"><span class="spinner"></span>${text}</div>`;

// Trạng thái dùng chung trên mọi trang: trống / lỗi (có nút Thử lại) / đang tải (khung xương)
function emptyState(ic, title, text = '', { compact = false, dashed = false, action = '' } = {}) {
  return `<div class="empty-state${compact ? ' compact' : ''}${dashed ? ' dashed' : ''}">${icon(ic)}<div class="es-title">${esc(title)}</div>
    ${text ? `<div class="es-text">${esc(text)}</div>` : ''}${action}</div>`;
}
const errorState = (msg) => `<div class="error-state" role="alert">${icon('alert')}<div class="grow"><div class="es-title">Không tải được dữ liệu</div>
  <div class="es-text">${esc(msg)}</div></div><button type="button" class="btn sm" data-retry>${icon('refresh')} Thử lại</button></div>`;
const skeletonLines = (n = 5) => `<div class="skeleton-lines" aria-busy="true" aria-label="Đang tải">${'<span class="skeleton"></span>'.repeat(n)}</div>`;
const skeletonTiles = (n = 8) => '<div class="skeleton-tile" aria-hidden="true"><span class="skeleton"></span><span class="skeleton"></span><span class="skeleton"></span></div>'.repeat(n);

// Ảnh sản phẩm: dùng ảnh thật nếu có, nếu không hiện ô chữ viết tắt cùng một bảng màu
function thumb(p, cls = '') {
  const name = p?.name || p?.product_name || '';
  if (p?.image_url) return `<img class="thumb ${cls}" src="${esc(p.image_url)}" alt="${esc(name)}" loading="lazy">`;
  const initials = name.split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]).join('').toUpperCase() || '?';
  let h = 0;
  for (const ch of name) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return `<div class="thumb thumb-ph ph-${h % 7} ${cls}">${esc(initials)}</div>`;  // màu nền lấy từ biến --ph-0..6
}
const productCell = (p) => `<div class="cell-product">${thumb(p)}<div class="min-w-0"><div class="title">${esc(p.name || p.product_name)}</div>
  <div class="sub">${esc(p.code || p.product_code)}${p.category_name ? ' · ' + esc(p.category_name) : ''}</div></div></div>`;

async function api(path, { method = 'GET', body, params, raw = false, form } = {}) {
  const url = new URL('/api' + path, location.origin);
  Object.entries(params || {}).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, v); });
  const headers = {};
  if (S.token) headers.Authorization = 'Bearer ' + S.token;
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  let res;
  try {
    res = await fetch(url, { method, headers, body: form || (body !== undefined ? JSON.stringify(body) : undefined) });
  } catch {
    throw new Error('Không kết nối được máy chủ');
  }
  if (res.status === 401 && path !== '/auth/login') { logout(); throw new Error('Phiên đăng nhập đã hết hạn'); }
  if (!res.ok) {
    let msg = `Lỗi ${res.status}`;
    try {
      const data = await res.json();
      if (typeof data.detail === 'string') msg = data.detail;
      else if (Array.isArray(data.detail)) msg = data.detail.map((d) => `${d.loc?.slice(-1)[0]}: ${d.msg}`).join('; ');
    } catch { /* bỏ qua */ }
    const err = new Error(msg);
    err.status = res.status;
    throw err;
  }
  return raw ? res : res.json();
}

async function download(path, params) {
  try {
    const res = await api(path, { params, raw: true });
    const name = /filename="([^"]+)"/.exec(res.headers.get('Content-Disposition') || '')?.[1] || 'export';
    const url = URL.createObjectURL(await res.blob());
    const a = Object.assign(document.createElement('a'), { href: url, download: name });
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (e) { toast(e.message, 'error'); }
}

function toast(msg, type = '') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `${icon(type === 'error' ? 'alert' : 'check')}<span>${esc(msg)}</span>`;
  $('#toast-root').appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function modal({ title, body, footer = '', size = '', onClose }) {
  const root = document.createElement('div');
  root.className = 'modal-backdrop';
  root.innerHTML = `<div class="modal ${size}" role="dialog" aria-modal="true">
    <div class="modal-header"><h2>${title}</h2><button class="btn ghost sm icon-only" data-close aria-label="Đóng">${icon('x')}</button></div>
    <div class="modal-body">${body}</div>
    ${footer ? `<div class="modal-footer">${footer}</div>` : ''}</div>`;
  let closed = false;
  const close = () => { if (closed) return; closed = true; root.remove(); onClose?.(); };
  root.addEventListener('mousedown', (e) => { if (e.target === root) close(); });
  root.addEventListener('click', (e) => { if (e.target.closest('[data-close]')) close(); });
  $('#modal-root').appendChild(root);
  return { el: root, close };
}

function confirmBox(message, { input = false, okText = 'Đồng ý', danger = false, value = '' } = {}) {
  return new Promise((resolve) => {
    const m = modal({
      title: 'Xác nhận', size: 'narrow',
      body: `<p class="mt-0">${esc(message)}</p>${input ? `<input id="confirm-input" class="w-full" placeholder="Nhập lý do..." value="${esc(value)}">` : ''}`,
      footer: `<button class="btn" data-close>Hủy bỏ</button><button class="btn ${danger ? 'danger' : 'primary'}" id="confirm-ok">${okText}</button>`,
      onClose: () => resolve(false),
    });
    const inp = $('#confirm-input', m.el);
    inp?.focus();
    $('#confirm-ok', m.el).onclick = () => {
      if (input && !inp.value.trim()) { inp.focus(); return; }
      resolve(input ? inp.value.trim() : true);
      m.close();
    };
  });
}

function formValues(form) {
  const out = {};
  for (const el of form.elements) {
    if (!el.name) continue;
    let v = el.type === 'checkbox' ? el.checked : el.value.trim();
    if (el.dataset.type === 'int') v = v === '' ? null : parseInt(v, 10);
    if (el.dataset.type === 'money') v = v === '' ? (el.dataset.empty != null ? Number(el.dataset.empty) : null) : parseMoney(v);
    if (el.dataset.type === 'nullable' && v === '') v = null;
    out[el.name] = v;
  }
  return out;
}

// ---- Ô nhập tiền (VND không có số lẻ): gõ đến đâu tự thêm dấu chấm ngăn cách hàng nghìn đến đó (3000000 -> 3.000.000).
// Dấu chấm / phẩy người dùng gõ luôn là ngăn cách hàng nghìn. Không dùng <input type="number"> vì trình duyệt hiểu
// "3.000" là 3 (dấu thập phân) nên lưu sai giá mà không báo lỗi.
const MONEY_MAX_DIGITS = 12;  // tối đa 999 tỉ
const MONEY_ATTRS = 'type="text" inputmode="numeric" autocomplete="off" data-money';
const parseMoney = (v) => {
  const d = String(v ?? '').replace(/\D/g, '').slice(0, MONEY_MAX_DIGITS);
  return d ? Number(d) : null;
};
const fmtMoneyInput = (v) => { const n = parseMoney(v); return n == null ? '' : n.toLocaleString('vi-VN'); };

function onMoneyInput(e) {
  const el = e.target;
  if (!el.matches?.('input[data-money]')) return;
  let raw = el.value;
  let caret = el.selectionStart ?? raw.length;
  // Backspace đúng vào dấu chấm: xóa luôn chữ số đứng trước, nếu không phím Backspace sẽ như "không có tác dụng"
  if (e.inputType === 'deleteContentBackward' && raw.replace(/\D/g, '') === (el.dataset.prev || '').replace(/\D/g, '')) {
    let i = caret - 1;
    while (i >= 0 && !/\d/.test(raw[i])) i--;
    if (i >= 0) { raw = raw.slice(0, i) + raw.slice(i + 1); caret = i; }
  }
  const digitsBeforeCaret = raw.slice(0, caret).replace(/\D/g, '').length;
  el.value = fmtMoneyInput(raw);
  el.dataset.prev = el.value;
  // Giữ con trỏ đứng sau đúng chữ số vừa gõ
  let pos = 0;
  for (let seen = 0; pos < el.value.length && seen < digitsBeforeCaret; pos++) if (/\d/.test(el.value[pos])) seen++;
  if (document.activeElement === el) el.setSelectionRange(pos, pos);
}

function renderMarkdown(md) {
  if (window.marked && window.DOMPurify) return DOMPurify.sanitize(marked.parse(md || ''));
  return `<pre class="pre-wrap">${esc(md)}</pre>`;
}

// ============================================================ Biểu đồ (màu lấy từ biến CSS, vẽ lại khi đổi sáng / tối)
// build(t) trả về cấu hình Chart.js cho bảng màu t; lưu lại để dựng lại biểu đồ khi đổi giao diện.
const CHART_BUILD = new WeakMap();

function chartTheme() {
  const cs = getComputedStyle(document.documentElement);
  const v = (n) => cs.getPropertyValue(n).trim();
  return {
    text: v('--text'), text2: v('--text-2'), muted: v('--muted'), surface: v('--surface'), border: v('--border-strong'),
    line: v('--chart-line'), grid: v('--chart-grid'), axis: v('--chart-axis'), other: v('--chart-other'),
    series: [1, 2, 3, 4, 5, 6, 7, 8].map((i) => v(`--chart-${i}`)),
  };
}
const alpha = (hex, a) => { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16}, ${(n >> 8) & 255}, ${n & 255}, ${a})`; };
const chartTooltip = (t, label) => ({ backgroundColor: t.surface, titleColor: t.text, bodyColor: t.text2, borderColor: t.border, borderWidth: 1,
  padding: 10, cornerRadius: 8, boxPadding: 4, callbacks: { label } });

// Vùng dưới đường doanh thu: đậm ở đỉnh, mờ dần về trục hoành
const fadeFill = (c) => ({ chart: { ctx, chartArea: a } }) => {
  if (!a) return alpha(c, .1);
  const g = ctx.createLinearGradient(0, a.top, 0, a.bottom);
  g.addColorStop(0, alpha(c, .24));
  g.addColorStop(1, alpha(c, 0));
  return g;
};

// Một chuỗi doanh thu (đường hoặc cột): màu blue thương hiệu, lưới mờ, không cần chú thích vì tiêu đề thẻ đã nêu tên
function seriesChart(type, labels, values, t) {
  const c = t.line;
  const ds = type === 'line'
    ? { borderColor: c, backgroundColor: fadeFill(c), fill: true, tension: .3, borderWidth: 2, pointRadius: 0, pointHoverRadius: 5,
        pointHoverBackgroundColor: c, pointHoverBorderColor: t.surface, pointHoverBorderWidth: 2 }
    : { backgroundColor: c, hoverBackgroundColor: alpha(c, .8), borderRadius: 4, borderSkipped: 'start', maxBarThickness: 32 };
  return {
    type, data: { labels, datasets: [{ label: 'Doanh thu', data: values, ...ds }] },
    options: {
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: { display: false }, tooltip: chartTooltip(t, (x) => money(x.raw)) },
      scales: {
        x: { grid: { display: false }, border: { color: t.axis }, ticks: { color: t.muted, maxRotation: 0, autoSkipPadding: 12 } },
        y: { grid: { color: t.grid }, border: { display: false }, ticks: { color: t.muted, callback: (v) => num(v) } },
      },
    },
  };
}

// Màu theo nhóm hàng (theo id, không theo thứ hạng doanh thu) để mỗi nhóm luôn giữ một màu
function categoryColor(name, t) {
  const order = [...S.categories].sort((a, b) => a.id - b.id).map((c) => c.name);
  const i = order.indexOf(name);
  return i >= 0 && i < t.series.length ? t.series[i] : t.other;
}

// Tỉ trọng doanh thu theo nhóm: chú thích ghi kèm phần trăm (nhãn hiển thị, không chỉ dựa vào màu)
function categoryChart(rows, t) {
  const total = rows.reduce((sum, r) => sum + r.revenue, 0) || 1;
  const pct = (i) => `${(rows[i].revenue / total * 100).toFixed(1)}%`;
  return {
    type: 'doughnut',
    data: { labels: rows.map((r) => r.category), datasets: [{ data: rows.map((r) => r.revenue),
      backgroundColor: rows.map((r) => categoryColor(r.category, t)), borderColor: t.surface, borderWidth: 2, hoverOffset: 4 }] },
    options: {
      cutout: '62%',
      plugins: {
        legend: { position: 'right', labels: { color: t.text2, usePointStyle: true, pointStyle: 'circle', boxWidth: 8, padding: 14,
          generateLabels: (c) => Chart.overrides.doughnut.plugins.legend.labels.generateLabels(c).map((l) => ({ ...l, text: `${l.text} · ${pct(l.index)}` })) } },
        tooltip: chartTooltip(t, (x) => `${x.label}: ${money(x.raw)} (${pct(x.dataIndex)})`),
      },
    },
  };
}

function makeChart(canvas, build, animate = true) {
  const cfg = build(chartTheme());
  cfg.options = { responsive: true, maintainAspectRatio: false, ...cfg.options, ...(animate ? {} : { animation: false }) };
  const c = new Chart(canvas, cfg);
  CHART_BUILD.set(c, build);
  return c;
}

function chart(canvas, build) {
  if (!window.Chart) { canvas.replaceWith(Object.assign(document.createElement('p'), { className: 'muted', textContent: 'Không tải được thư viện biểu đồ (cần Internet).' })); return; }
  Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
  S.charts.push(makeChart(canvas, build));
}

function repaintCharts() {
  S.charts = S.charts.map((c) => {
    const build = CHART_BUILD.get(c);
    if (!build || !c.canvas?.isConnected) return c;
    const canvas = c.canvas;
    c.destroy();
    return makeChart(canvas, build, false);
  });
}

// ============================================================ Giao diện sáng / tối
const storedTheme = () => { try { const t = localStorage.getItem('theme'); return t === 'light' || t === 'dark' ? t : null; } catch { return null; } };
const currentTheme = () => (document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light');

function renderThemeButton() {
  const dark = currentTheme() === 'dark';
  $$('[data-theme-toggle]').forEach((b) => {
    b.innerHTML = icon(dark ? 'sun' : 'moon');
    b.title = dark ? 'Chuyển sang giao diện sáng' : 'Chuyển sang giao diện tối';
    b.setAttribute('aria-label', b.title);
    b.setAttribute('aria-pressed', String(dark));
  });
}

// origin: toạ độ nút bấm, dùng cho hiệu ứng vòng tròn lan ra (View Transitions API)
function applyTheme(theme, { save = true, origin = null } = {}) {
  const root = document.documentElement;
  const apply = () => {
    root.dataset.theme = theme;
    if (save) { try { localStorage.setItem('theme', theme); } catch { /* chế độ riêng tư: chỉ đổi trong phiên */ } }
    renderThemeButton();
    repaintCharts();
  };
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) { apply(); return; }
  if (!document.startViewTransition || !origin) {
    root.classList.add('theme-fade');
    apply();
    setTimeout(() => root.classList.remove('theme-fade'), 350);
    return;
  }
  const { x, y } = origin;
  const r = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
  document.startViewTransition(apply).ready.then(() => {
    root.animate({ clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${r}px at ${x}px ${y}px)`] },
      { duration: 500, easing: 'cubic-bezier(.4, 0, .2, 1)', pseudoElement: '::view-transition-new(root)' });
  }).catch(() => {});
}

function initTheme() {
  renderThemeButton();
  $$('[data-theme-toggle]').forEach((b) => b.onclick = (e) => {
    const r = e.currentTarget.getBoundingClientRect();
    applyTheme(currentTheme() === 'dark' ? 'light' : 'dark', { origin: { x: r.left + r.width / 2, y: r.top + r.height / 2 } });
  });
  // Chưa chọn thủ công thì đi theo cài đặt sáng / tối của hệ điều hành
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!storedTheme()) applyTheme(e.matches ? 'dark' : 'light', { save: false });
  });
}

// Bảng dùng chung: headers = ['Tên', ['Tổng', 'right']...], rows = mảng ô HTML
function table(headers, rows, { empty = 'Không có dữ liệu', rowAttrs } = {}) {
  const hs = headers.map((h) => (Array.isArray(h) ? h : [h, '']));
  const body = rows.length
    ? rows.map((r, i) => `<tr ${rowAttrs ? rowAttrs(i) : ''}>${r.map((c, j) => `<td class="${hs[j]?.[1] || ''}">${c ?? ''}</td>`).join('')}</tr>`).join('')
    : `<tr><td colspan="${hs.length}" class="empty-cell">${emptyState('clipboard', empty, '', { compact: true })}</td></tr>`;
  return `<div class="table-wrap"><table><thead><tr>${hs.map(([l, c]) => `<th class="${c}">${l}</th>`).join('')}</tr></thead><tbody>${body}</tbody></table></div>`;
}

function pager(total, page, size, onGo) {
  const pages = Math.max(1, Math.ceil(total / size));
  const div = document.createElement('div');
  div.className = 'pager';
  div.innerHTML = `<span>${num(total)} bản ghi</span><span>
    <button class="btn sm" ${page <= 1 ? 'disabled' : ''} data-p="${page - 1}">Trước</button>
    Trang ${page}/${pages}
    <button class="btn sm" ${page >= pages ? 'disabled' : ''} data-p="${page + 1}">Sau</button></span>`;
  div.addEventListener('click', (e) => { const b = e.target.closest('[data-p]'); if (b && !b.disabled) onGo(+b.dataset.p); });
  return div;
}

const exportButtons = () => `<div class="btn-group">
  <button type="button" class="btn" data-exp="csv">${icon('download')} CSV</button>
  <button type="button" class="btn" data-exp="xlsx">Excel</button>
  <button type="button" class="btn" data-exp="pdf">PDF</button></div>`;

async function loadCategories() {
  S.categories = await api('/categories');
  return S.categories;
}
const categoryOptions = (selected, empty = 'Tất cả nhóm hàng') =>
  `<option value="">${empty}</option>` + S.categories.map((c) => `<option value="${c.id}" ${c.id == selected ? 'selected' : ''}>${esc(c.name)}</option>`).join('');

function beep() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.frequency.value = 1200;
    gain.gain.value = 0.08;
    osc.connect(gain).connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.08);
  } catch { /* trình duyệt không hỗ trợ âm thanh */ }
}

// ============================================================ Điều hướng
const SALES = ['owner', 'staff'];
const ROUTES = {
  dashboard: { title: 'Tổng quan', icon: 'dashboard', roles: ['owner'], group: 'Tổng quan', render: pageDashboard },
  pos: { title: 'Bán hàng', icon: 'cart', roles: SALES, group: 'Bán hàng', render: pagePOS },
  invoices: { title: 'Hóa đơn', icon: 'receipt', roles: SALES, group: 'Bán hàng', render: pageInvoices },
  returns: { title: 'Đổi trả hàng', icon: 'undo', roles: SALES, group: 'Bán hàng', render: pageReturns },
  warranty: { title: 'Bảo hành', icon: 'wrench', roles: SALES, group: 'Bán hàng', render: pageWarranty },
  customers: { title: 'Khách hàng', icon: 'users', roles: SALES, group: 'Khách hàng', render: pageCustomers },
  tiers: { title: 'Hạng thành viên', icon: 'award', roles: ['owner'], group: 'Khách hàng', render: pageTiers },
  promotions: { title: 'Khuyến mãi, voucher', icon: 'percent', roles: ['owner'], group: 'Khách hàng', render: pagePromotions },
  products: { title: 'Sản phẩm', icon: 'package', roles: SALES, group: 'Hàng hóa', render: pageProducts },
  categories: { title: 'Nhóm hàng', icon: 'tag', roles: ['owner'], group: 'Hàng hóa', render: pageCategories },
  serials: { title: 'Serial / IMEI', icon: 'hash', roles: ['owner'], group: 'Hàng hóa', render: pageSerials },
  imports: { title: 'Nhập hàng', icon: 'truck', roles: SALES, group: 'Kho hàng', render: pageImports },
  suppliers: { title: 'Nhà cung cấp', icon: 'building', roles: ['owner'], group: 'Kho hàng', render: pageSuppliers },
  stock: { title: 'Nhập - xuất - tồn', icon: 'arrows', roles: ['owner'], group: 'Kho hàng', render: pageStock },
  'stock-card': { title: 'Thẻ kho', icon: 'clipboard', roles: ['owner'], group: 'Kho hàng', render: pageStockCard },
  reports: { title: 'Báo cáo doanh thu', icon: 'chart', roles: ['owner'], group: 'Báo cáo', render: pageReports },
  inventory: { title: 'Báo cáo tồn kho', icon: 'layers', roles: ['owner'], group: 'Báo cáo', render: pageInventory },
  assistant: { title: 'Trợ lý đa năng', icon: 'sparkles', roles: SALES, group: 'Trợ lý AI', render: pageAssistant },
  advisor: { title: 'Chatbot tư vấn', icon: 'message', roles: SALES, group: 'Trợ lý AI', render: pageAdvisor },
  'ai-report': { title: 'Báo cáo AI', icon: 'sparkles', roles: ['owner'], group: 'Trợ lý AI', render: pageAIReport },
  ask: { title: 'Hỏi đáp dữ liệu', icon: 'help', roles: ['owner'], group: 'Trợ lý AI', render: pageAsk },
  business: { title: 'Tham số kinh doanh', icon: 'sliders', roles: ['owner'], group: 'Cài đặt', render: pageBusiness },
  users: { title: 'Người dùng', icon: 'shield', roles: ['admin'], group: 'Hệ thống', render: pageUsers },
  settings: { title: 'Cấu hình kỹ thuật, AI', icon: 'settings', roles: ['admin'], group: 'Hệ thống', render: pageSettings },
  backup: { title: 'Sao lưu, khôi phục', icon: 'database', roles: ['admin'], group: 'Hệ thống', render: pageBackup },
  logs: { title: 'Nhật ký hệ thống', icon: 'history', roles: ['admin'], group: 'Hệ thống', render: pageLogs },
};
// Không có quyền "toàn năng": mỗi vai trò chỉ thấy đúng các mục được liệt kê trong roles
const canAccess = (key) => Boolean(S.user && ROUTES[key].roles.includes(S.user.role));
const defaultRoute = () => ({ admin: 'users', owner: 'dashboard' }[S.user?.role] || 'pos');
const routeQuery = () => new URLSearchParams(location.hash.split('?')[1] || '');
const NAV_COUNTS = ['users', 'invoices', 'imports', 'warranty'];

function buildNav() {
  let html = '', group = '';
  for (const [key, r] of Object.entries(ROUTES)) {
    if (!canAccess(key)) continue;
    if (r.group !== group) { group = r.group; html += `<div class="group">${group}</div>`; }
    const count = NAV_COUNTS.includes(key) ? `<span class="nav-count hidden" id="nav-${key}-count"></span>` : '';
    html += `<a href="#${key}" data-route="${key}">${icon(r.icon)}<span>${r.title}</span>${count}</a>`;
  }
  $('#nav').innerHTML = html;
}

// Số việc đang chờ hiện cạnh mục menu: tài khoản chờ duyệt, yêu cầu hủy / hóa đơn tạm, phiếu nhập nháp, phiếu bảo hành mở
function setNavCount(key, n, what) {
  const el = $(`#nav-${key}-count`);
  if (!el) return;
  el.textContent = n;
  el.title = `${n} ${what}`;
  el.classList.toggle('hidden', !n);
}
const setPendingCount = (n) => setNavCount('users', n, 'tài khoản chờ duyệt');

async function refreshCounts() {
  try {
    if (isAdmin()) { setPendingCount((await api('/users')).filter((x) => x.pending).length); return; }
    const [c, w] = await Promise.all([api('/invoices/pending-count'), api('/warranty', { params: { status: 'open', size: 1 } })]);
    if (isManager()) {
      setNavCount('invoices', c.cancel_requests, 'yêu cầu hủy hóa đơn chờ duyệt');
      setNavCount('imports', c.draft_imports, 'phiếu nhập nháp chờ xác nhận');
    } else setNavCount('invoices', c.held_invoices, 'hóa đơn tạm chưa thanh toán');
    setNavCount('warranty', w.total, 'phiếu bảo hành đang xử lý');
  } catch { /* chỉ là số đếm phụ */ }
}

async function navigate() {
  if (!S.user) return;
  let key = location.hash.slice(1).split('?')[0] || defaultRoute();
  if (!ROUTES[key] || !canAccess(key)) key = defaultRoute();
  S.route = key;
  AIFab.sync();
  S.charts.forEach((c) => c.destroy());
  S.charts = [];
  $$('#nav a').forEach((a) => a.classList.toggle('active', a.dataset.route === key));
  $('#page-title').textContent = ROUTES[key].title;
  document.title = `${ROUTES[key].title} · SalesAI`;
  $('#sidebar').classList.remove('open');
  const page = $('#page');
  page.innerHTML = `<div class="card">${skeletonLines(6)}</div>`;
  try {
    await ROUTES[key].render(page);
  } catch (e) {
    page.innerHTML = `<div class="card">${errorState(e.message)}</div>`;
    $('[data-retry]', page).onclick = navigate;
  }
}

// ============================================================ Đăng nhập
function showLogin() {
  $('#app-view').classList.add('hidden');
  $('#login-view').classList.remove('hidden');
  AIFab.sync();
}

async function startApp() {
  $('#login-view').classList.add('hidden');
  $('#app-view').classList.remove('hidden');
  const u = S.user;
  $('#user-chip').innerHTML = `<div class="avatar">${esc(initialsOf(u.full_name))}</div>
    <div class="who"><div class="name">${esc(u.full_name)}</div>${u.full_name !== ROLE_VI[u.role] ? `<div class="role">${ROLE_VI[u.role]}</div>` : ''}</div>`;
  $('#user-chip').title = 'Tài khoản: đổi mật khẩu';
  $('#user-chip').onclick = changePassword;
  buildNav();
  refreshCounts();
  refreshAIBadge();
  if (!isAdmin()) await api('/payments/config').then((c) => { S.payCfg = c; }).catch(() => {});
  await navigate();
}

// Nhãn AI trên topbar: model đang dùng được, hoặc báo hết lượt / chưa cấu hình
function refreshAIBadge() {
  return api('/ai/status').then((s) => {
    S.ai = s;
    const b = $('#ai-badge');
    const resting = (s.models || []).filter((m) => !m.available);
    b.className = `badge dot ${s.enabled && s.model ? 'cyan' : 'yellow'}`;
    if (!s.enabled) {
      b.textContent = 'AI dự phòng';
      b.title = 'Chưa cấu hình GEMINI_API_KEY trong .env - AI chạy chế độ dự phòng';
    } else if (!s.model && resting.every((m) => m.reason === 'day' || m.reason === 'gone')) {
      const day = resting.find((m) => m.until);
      b.textContent = 'AI hết lượt hôm nay';
      b.title = `Đã dùng hết lượt gọi Gemini miễn phí của mọi model${day ? `, làm mới lúc ${day.until}` : ''}. Tạm thời trả lời bằng chế độ dự phòng.`;
    } else if (!s.model) {
      // Có model chỉ nghỉ ngắn (Google quá tải / giới hạn theo phút): vài phút sau tự dùng lại được
      b.textContent = 'AI đang quá tải';
      b.title = `Các model Gemini đang quá tải hoặc bị giới hạn tần suất, thường chỉ khoảng 1 phút. Tạm thời trả lời bằng chế độ dự phòng.\nĐang nghỉ: ${resting.map((m) => `${m.model}${m.until ? ` (đến ${m.until})` : ''}`).join(', ')}`;
    } else {
      b.textContent = `AI: ${s.model}`;
      b.title = 'Đang dùng Gemini API' + (resting.length ? `\nĐang nghỉ: ${resting.map((m) => `${m.model}${m.until ? ` (đến ${m.until})` : ''}`).join(', ')}` : '');
    }
  }).catch(() => {});
}

function logout() {
  if (S.token) api('/auth/logout', { method: 'POST' }).catch(() => {});
  S.token = S.user = null;
  S.chat = { assistant: newChatState(), advisor: newChatState(), ask: newChatState() };
  resetPOS();
  saveToken(null);
  showLogin();
}

// "Ghi nhớ đăng nhập": token lưu localStorage (giữ sau khi đóng trình duyệt), không thì sessionStorage (mất khi đóng tab)
function saveToken(token, remember = true) {
  try {
    localStorage.removeItem('token');
    sessionStorage.removeItem('token');
    if (token) (remember ? localStorage : sessionStorage).setItem('token', token);
  } catch { /* chế độ riêng tư: token chỉ giữ trong bộ nhớ */ }
}
function readToken() {
  try { return localStorage.getItem('token') || sessionStorage.getItem('token'); } catch { return null; }
}

function showAdminHelp(title) {
  modal({
    title: `${icon('headset')} ${title}`, size: 'narrow',
    body: `<p class="mt-0">Tài khoản SalesAI do <b>quản trị viên</b> của cửa hàng cấp.</p>
      <ul class="list">
        <li>Tài khoản đã khai báo email: bấm <b>Quên mật khẩu?</b> để nhận mã xác nhận qua email và tự đặt mật khẩu mới.</li>
        <li>Chưa có email: liên hệ quản trị viên để được đặt lại mật khẩu hoặc mở khóa tài khoản (menu <b>Người dùng</b>).</li>
        <li>Đang đăng nhập: bấm vào tên của bạn ở góc trên bên phải để <b>đổi mật khẩu</b>.</li>
      </ul>`,
    footer: '<button class="btn primary" data-close>Đã hiểu</button>',
  });
}

// Đổi mật khẩu của chính mình (mọi vai trò): bấm vào tên ở góc trên bên phải
function changePassword() {
  const m = modal({
    title: `${icon('key')} Đổi mật khẩu`, size: 'narrow',
    body: `<form id="cp-form" class="stack">
      <p class="muted small m-0">Tài khoản <b>${esc(S.user.username)}</b> · ${ROLE_VI[S.user.role]}</p>
      <label>Mật khẩu hiện tại *<input name="current_password" type="password" required autocomplete="current-password"></label>
      <label>Mật khẩu mới *<input name="new_password" type="password" required minlength="6" autocomplete="new-password" placeholder="Ít nhất 6 ký tự"></label>
      <label>Nhập lại mật khẩu mới *<input name="confirm" type="password" required autocomplete="new-password"></label>
      <p class="error m-0" id="cp-err"></p><button type="submit" hidden></button></form>`,
    footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="cp-save">${icon('check')} Đổi mật khẩu</button>`,
  });
  const form = $('#cp-form', m.el);
  const save = async () => {
    if (!form.reportValidity()) return;
    const v = formValues(form);
    if (v.new_password !== v.confirm) { $('#cp-err', m.el).textContent = 'Mật khẩu nhập lại không khớp'; return; }
    try {
      const r = await api('/auth/change-password', { method: 'POST', body: { current_password: v.current_password, new_password: v.new_password } });
      toast(r.message, 'success');
      m.close();
    } catch (e) { $('#cp-err', m.el).textContent = e.message; }
  };
  form.onsubmit = (e) => { e.preventDefault(); save(); };
  $('#cp-save', m.el).onclick = save;
  form.current_password.focus();
}

// Tự tạo tài khoản: là thu ngân, đăng nhập được sau khi quản trị viên duyệt (menu Người dùng)
function registerAccount() {
  const m = modal({
    title: `${icon('user')} Tạo tài khoản`, size: 'narrow',
    body: `<form id="rg-form" class="stack">
      <p class="muted small m-0">Tài khoản mới có vai trò <b>Thu ngân</b> và cần quản trị viên duyệt trước khi đăng nhập.</p>
      <label>Họ tên *<input name="full_name" required maxlength="100" autocomplete="name" placeholder="VD: Nguyễn Văn An"></label>
      <label>Tên đăng nhập *<input name="username" required minlength="3" maxlength="50" pattern="[A-Za-z0-9._\\-]+" autocomplete="username"
        title="Chữ không dấu, số và . _ -" placeholder="VD: nguyenvanan"></label>
      <label>Mật khẩu *<input name="password" type="password" required minlength="6" maxlength="128" autocomplete="new-password" placeholder="Ít nhất 6 ký tự"></label>
      <label>Nhập lại mật khẩu *<input name="confirm" type="password" required autocomplete="new-password"></label>
      <p class="error m-0" id="rg-err"></p><button type="submit" hidden></button></form>`,
    footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="rg-save">${icon('check')} Tạo tài khoản</button>`,
  });
  const form = $('#rg-form', m.el);
  const btn = $('#rg-save', m.el);
  const err = (msg) => { $('#rg-err', m.el).textContent = msg; };
  const submit = async () => {
    err('');
    if (!form.reportValidity()) return;
    const v = formValues(form);
    if (v.password !== v.confirm) { err('Mật khẩu nhập lại không khớp'); form.confirm.focus(); return; }
    btn.disabled = true;
    try {
      const r = await api('/auth/register', { method: 'POST', body: { full_name: v.full_name, username: v.username, password: v.password } });
      $('.modal-body', m.el).innerHTML = emptyState('check', 'Đã gửi yêu cầu tạo tài khoản', r.message, { compact: true });
      $('.modal-footer', m.el).innerHTML = '<button class="btn primary" data-close>Đã hiểu</button>';
      $('#login-form').username.value = v.username;
    } catch (e) { err(e.message); btn.disabled = false; }
  };
  form.onsubmit = (e) => { e.preventDefault(); submit(); };
  btn.onclick = submit;
  form.full_name.focus();
}

// Quên mật khẩu: tài khoản có email nhận mã 6 số qua email rồi tự đặt mật khẩu mới; chưa có email thì nhờ quản trị viên.
function forgotPassword() {
  const login = $('#login-form');
  let username = login.username.value.trim();
  let timer = null;
  const m = modal({
    title: `${icon('lock')} Quên mật khẩu`, size: 'narrow', body: '',
    footer: '<button class="btn" data-close>Hủy</button><button class="btn primary" id="fp-next"></button>',
    onClose: () => clearInterval(timer),
  });
  const body = $('.modal-body', m.el);
  const next = $('#fp-next', m.el);
  const err = (msg) => { $('#fp-err', m.el).textContent = msg; };
  const sendCode = async () => { // trả về thông báo của server, lỗi thì hiện lên form và trả về null
    try { return (await api('/auth/forgot-password', { method: 'POST', body: { username } })).message; }
    catch (e) { err(e.message); return null; }
  };

  const stepCode = (message) => {
    body.innerHTML = `<p class="mt-0">${esc(message)}</p>
      <form id="fp-form" class="stack">
        <label>Mã xác nhận<input name="code" required inputmode="numeric" autocomplete="one-time-code" maxlength="6" pattern="\\d{6}" title="Mã gồm 6 chữ số" placeholder="6 chữ số"></label>
        <label>Mật khẩu mới<input name="new_password" type="password" required minlength="6" autocomplete="new-password" placeholder="Ít nhất 6 ký tự"></label>
        <label>Nhập lại mật khẩu mới<input name="confirm" type="password" required autocomplete="new-password"></label>
        <p class="error m-0" id="fp-err"></p><button type="submit" hidden></button></form>
      <p class="muted small mb-0">Không thấy email? Xem cả thư mục Spam, hoặc <button type="button" class="link-btn" id="fp-resend"></button></p>`;
    next.textContent = 'Đổi mật khẩu';
    const form = $('#fp-form', m.el);
    const resend = $('#fp-resend', m.el);
    const countdown = () => { // server chỉ gửi mã mới sau 60 giây
      let left = 60;
      const tick = () => { resend.disabled = left > 0; resend.textContent = left > 0 ? `gửi lại mã sau ${left} giây` : 'gửi lại mã'; };
      tick();
      clearInterval(timer);
      timer = setInterval(() => { left -= 1; tick(); if (left <= 0) clearInterval(timer); }, 1000);
    };
    countdown();
    resend.onclick = async () => {
      resend.disabled = true;
      if (await sendCode()) { err(''); toast('Đã gửi lại mã xác nhận', 'success'); countdown(); } else resend.disabled = false;
    };
    form.onsubmit = async (e) => {
      e.preventDefault();
      if (form.new_password.value !== form.confirm.value) { err('Mật khẩu nhập lại không khớp'); return; }
      next.disabled = true;
      try {
        const r = await api('/auth/reset-password', { method: 'POST', body: { username, code: form.code.value.trim(), new_password: form.new_password.value } });
        m.close();
        toast(r.message, 'success');
        login.username.value = username;
        login.password.value = '';
        login.password.focus();
      } catch (ex) { err(ex.message); next.disabled = false; }
    };
    next.onclick = () => form.requestSubmit();
    form.code.focus();
  };

  body.innerHTML = `<p class="mt-0">Nhập tên đăng nhập, hệ thống gửi mã xác nhận tới <b>email đã khai báo</b> của tài khoản để bạn tự đặt mật khẩu mới.</p>
    <form id="fp-form" class="stack"><label>Tên đăng nhập<input name="username" required autocomplete="username" value="${esc(username)}"></label>
      <p class="error m-0" id="fp-err"></p></form>
    <p class="muted small mb-0">Tài khoản chưa khai báo email: liên hệ quản trị viên để được đặt lại mật khẩu.</p>`;
  next.textContent = 'Gửi mã';
  const form = $('#fp-form', m.el);
  form.onsubmit = async (e) => {
    e.preventDefault();
    username = form.username.value.trim();
    next.disabled = true;
    const message = await sendCode();
    next.disabled = false;
    if (message) stepCode(message);
  };
  next.onclick = () => form.requestSubmit();
  form.username.focus();
}

function initLoginForm() {
  const form = $('#login-form');
  const submit = $('#login-submit');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    $('#login-error').textContent = '';
    submit.disabled = true;
    submit.innerHTML = '<span class="spinner"></span> Đang đăng nhập...';
    try {
      const data = await api('/auth/login', { method: 'POST', body: { username: form.username.value.trim(), password: form.password.value } });
      S.token = data.access_token;
      S.user = data.user;
      saveToken(S.token, form.remember.checked);
      form.password.value = '';
      await startApp();
    } catch (err) {
      $('#login-error').textContent = err.message;
    } finally {
      submit.disabled = false;
      submit.textContent = 'Đăng nhập';
    }
  });
  $('#pw-toggle').onclick = () => {
    const input = form.password;
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    const label = show ? 'Ẩn mật khẩu' : 'Hiện mật khẩu';
    Object.assign($('#pw-toggle'), { innerHTML: icon(show ? 'eye-off' : 'eye'), title: label });
    $('#pw-toggle').setAttribute('aria-label', label);
    input.focus();
  };
  $('#forgot-btn').onclick = forgotPassword;
  $('#register-btn').onclick = registerAccount;
  $('#contact-admin').onclick = () => showAdminHelp('Liên hệ quản trị viên');
  $$('[data-demo]').forEach((b) => b.addEventListener('click', () => {
    const [u, p] = b.dataset.demo.split('/');
    form.username.value = u;
    form.password.value = p;
    form.requestSubmit();
  }));
}

async function init() {
  $$('[data-icon]').forEach((el) => { el.insertAdjacentHTML('afterbegin', icon(el.dataset.icon)); el.removeAttribute('data-icon'); });
  initTheme();
  initLoginForm();
  $('#logout-btn').onclick = logout;
  $('#menu-toggle').onclick = () => $('#sidebar').classList.toggle('open');
  $('#sidebar-backdrop').onclick = () => $('#sidebar').classList.remove('open');
  window.addEventListener('hashchange', navigate);
  // Ô nhập tiền: định dạng trước (pha capture) để các xử lý oninput của từng trang đọc được giá trị đã chuẩn hóa
  document.addEventListener('input', onMoneyInput, true);
  document.addEventListener('focusin', (e) => { if (e.target.matches?.('input[data-money]')) e.target.dataset.prev = e.target.value; });
  AIFab.init();

  S.token = readToken();
  if (!S.token) return showLogin();
  try {
    S.user = await api('/auth/me');
    await startApp();
  } catch { showLogin(); }
}

// ============================================================ Tổng quan
// featured: thẻ chỉ số chính, nền navy -> blue nổi bật so với các thẻ còn lại
const kpi = (ic, color, label, value, sub = '', featured = false) => `<div class="card kpi-card${featured ? ' featured' : ''}"><div class="kpi-icon ${color}">${icon(ic)}</div>
  <div class="min-w-0"><div class="label">${label}</div><div class="value">${value}</div><div class="sub">${sub}</div></div></div>`;
const cardHead = (ic, title, actions = '') => `<div class="card-head"><h2>${icon(ic)}${title}</h2>${actions}</div>`;

async function pageDashboard(page) {
  const d = await api('/reports/dashboard');
  page.innerHTML = `
    <div class="grid kpi">
      ${kpi('wallet', '', 'Doanh thu hôm nay', money(d.today.revenue), `${d.today.invoice_count} hóa đơn`, true)}
      ${kpi('calendar', '', 'Doanh thu tháng này', money(d.month.revenue), `${d.month.invoice_count} hóa đơn`)}
      ${kpi('up', '', 'Lãi gộp tháng này', money(d.month.gross_profit), `Giá vốn ${money(d.month.cost)}`)}
      ${kpi('package', '', 'Sản phẩm đang bán', num(d.product_count), `${d.customer_count} khách hàng`)}
      ${kpi('alert', d.low_stock.length ? 'yellow' : '', 'Cần nhập hàng', num(d.low_stock.length), 'sản phẩm dưới mức tối thiểu')}
    </div>
    <div class="card mt">${cardHead('chart', 'Doanh thu 30 ngày gần nhất')}<div class="chart-box"><canvas id="c-daily"></canvas></div></div>
    <div class="grid two mt">
      <div class="card">${cardHead('up', 'Top 5 bán chạy (30 ngày)')}
        ${table(['Sản phẩm', ['SL bán', 'right'], ['Doanh thu', 'right']], d.top_products_30.map((p) => [productCell(p), num(p.quantity), money(p.revenue)]))}</div>
      <div class="card">${cardHead('alert', 'Sản phẩm sắp hết hàng', `<a href="#imports" class="btn sm">${icon('truck')} Tạo phiếu nhập</a>`)}
        ${table(['Sản phẩm', ['Tồn / tối thiểu', 'right']], d.low_stock.map((p) => [productCell(p), `${stockBadge(p)} <span class="muted">/ ${p.min_stock}</span>`]), { empty: 'Tồn kho đang ổn' })}</div>
    </div>`;
  chart($('#c-daily'), (t) => seriesChart('line', d.daily_30.map((x) => x.date.slice(8) + '/' + x.date.slice(5, 7)), d.daily_30.map((x) => x.revenue), t));
}

// ============================================================ Bán hàng (POS)
// Thu ngân và chủ cửa hàng. POS.editing = hóa đơn tạm (chưa thanh toán) đang mở lại để sửa / thanh toán.
// Thu ngân không tự giảm giá: chỉ áp dụng khuyến mãi / voucher do chủ cửa hàng tạo, hạng thành viên và điểm tích lũy.
const POS = { cart: new Map(), customer: null, editing: null, products: [], pay: { method: 'cash', cash: '', ref: '' },
  promoId: '', voucher: null, pointsUsed: 0, promos: [], renderCart: null };

function resetPOS() {
  POS.cart.clear();
  POS.customer = null;
  POS.editing = null;
  POS.pay = { method: 'cash', cash: '', ref: '' };
  POS.promoId = '';
  POS.voucher = null;
  POS.pointsUsed = 0;
}

// ---- Đơn đang bán dở lưu trên trình duyệt: tải lại trang, lỡ đóng tab hay hết phiên đăng nhập vẫn khôi phục được.
// Chỉ lưu id + số lượng (+ IMEI); khi khôi phục lấy lại sản phẩm từ server để đúng giá và tồn kho hiện tại.
// Mỗi tài khoản một bản lưu riêng nên người khác đăng nhập trên cùng máy không thấy / không ghi đè. Hóa đơn tạm đang mở không lưu (bản gốc đã có trên server).
const posDraftKey = () => `posDraft:${S.user?.id}`;
function readPOSDraft() {
  try { return S.user ? JSON.parse(localStorage.getItem(posDraftKey())) : null; } catch { return null; }
}
function clearPOSDraft() { try { localStorage.removeItem(posDraftKey()); } catch { /* trình duyệt chặn lưu trữ */ } }
function savePOSDraft() {
  if (POS.editing || !S.user) return;
  // Giảm giá / ghi chú là ô nhập trên màn hình bán hàng; đang ở trang khác (thêm vào giỏ từ trợ lý AI) thì giữ giá trị đã lưu
  const prev = readPOSDraft() || {};
  const onPage = Boolean($('#inv-note'));
  const d = {
    items: [...POS.cart.values()].map((r) => [r.product.id, r.qty, r.serials || []]),
    customer: POS.customer ? { id: POS.customer.id } : null,
    method: POS.pay.method,
    discount: $('#disc') ? $('#disc').value : prev.discount ?? '0',
    discountType: $('#disc-type') ? $('#disc-type').value : prev.discountType ?? 'amount',
    note: onPage ? $('#inv-note').value : prev.note ?? '',
    promoId: POS.promoId, voucher: POS.voucher?.code || null, points: POS.pointsUsed,
  };
  if (!d.items.length && !d.customer && !/[1-9]/.test(d.discount) && !d.note.trim()) { clearPOSDraft(); return; }
  try { localStorage.setItem(posDraftKey(), JSON.stringify(d)); } catch { /* trình duyệt chặn lưu trữ: chỉ giữ trong phiên */ }
}
// Trả về số sản phẩm không khôi phục được (đã xóa, ngừng bán, hết hàng, máy đã bán)
async function restorePOSDraft(d) {
  const items = d.items || [];
  const products = await Promise.all(items.map(([id]) => api(`/products/${id}`).catch(() => null)));
  let dropped = 0;
  for (const [i, [, qty, serials]] of items.entries()) {
    const p = products[i];
    if (!p || p.status !== 'active' || p.stock <= 0) { dropped++; continue; }
    if (p.track_serial) {
      const avail = new Set(await api(`/products/${p.id}/serials`).catch(() => []));
      const keep = (serials || []).filter((s) => avail.has(s));
      if (!keep.length) { dropped++; continue; }
      POS.cart.set(p.id, { product: p, qty: keep.length, max: p.stock, serials: keep });
    } else {
      POS.cart.set(p.id, { product: p, qty: Math.min(qty, p.stock), max: p.stock, serials: [] });
    }
  }
  if (d.customer?.id) POS.customer = await api(`/customers/${d.customer.id}`).catch(() => null);  // điểm, hạng mới nhất
  POS.pay = { method: PAY[d.method] ? d.method : 'cash', cash: '', ref: '' };
  POS.promoId = d.promoId || '';
  POS.pointsUsed = d.points || 0;
  if (d.voucher) POS.voucher = await api(`/promotions/voucher/${encodeURIComponent(d.voucher)}`).catch(() => null);
  return dropped;
}

// Chọn đúng máy (IMEI / serial) khi bán sản phẩm quản lý theo từng máy. Trả về danh sách đã chọn, null = bỏ qua.
async function pickSerials(p, selected = []) {
  let avail;
  try { avail = await api(`/products/${p.id}/serials`); } catch (e) { toast(e.message, 'error'); return null; }
  const all = [...new Set([...selected, ...avail])];
  if (!all.length) { toast(`"${p.name}" không còn máy nào trong kho`, 'error'); return null; }
  return new Promise((resolve) => {
    let done = false;
    const m = modal({
      title: `${icon('hash')} Chọn IMEI / serial`,
      body: `<div class="row mb-3">${thumb(p)}<div class="min-w-0"><div class="strong">${esc(p.name)}</div>
          <div class="muted small">Sản phẩm quản lý theo từng máy: chọn đúng máy giao cho khách, hoặc quét IMEI / serial rồi Enter.</div></div></div>
        <div class="input-icon mb-3">${icon('barcode')}<input id="sp-q" placeholder="Tìm hoặc quét IMEI / serial" autocomplete="off"></div>
        <div class="serial-list" id="sp-list">${all.map((s) => `<label><input type="checkbox" value="${esc(s)}" ${selected.includes(s) ? 'checked' : ''}>${esc(s)}</label>`).join('')}</div>
        <p class="muted small mb-0" id="sp-count"></p>`,
      footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="sp-ok">${icon('check')} Xong</button>`,
      onClose: () => { if (!done) resolve(null); },
    });
    const list = $('#sp-list', m.el);
    const boxes = () => $$('input[type=checkbox]', list);
    const count = () => { $('#sp-count', m.el).textContent = `Đã chọn ${boxes().filter((b) => b.checked).length} / ${all.length} máy trong kho`; };
    const q = $('#sp-q', m.el);
    const filter = () => { const v = q.value.trim().toUpperCase(); boxes().forEach((b) => b.parentElement.classList.toggle('hidden', Boolean(v) && !b.value.includes(v))); };
    list.onchange = count;
    q.oninput = filter;
    q.onkeydown = (e) => {
      if (e.key !== 'Enter') return;
      e.preventDefault();
      const v = q.value.trim().toUpperCase();
      const b = boxes().find((x) => x.value === v);
      if (!b) { toast(`Không có IMEI / serial "${v}" trong kho`, 'error'); return; }
      b.checked = true; beep(); q.value = ''; filter(); count();
    };
    $('#sp-ok', m.el).onclick = () => { done = true; resolve(boxes().filter((b) => b.checked).map((b) => b.value)); m.close(); };
    count();
    q.focus();
  });
}

// Thêm vào giỏ. Sản phẩm quản lý theo serial: serial = máy vừa quét; không có thì mở hộp chọn IMEI.
async function addToCart(p, qty = 1, serial = null) {
  if (p.status && p.status !== 'active') { toast(`"${p.name}" đang ngừng kinh doanh`, 'error'); return false; }
  const item = POS.cart.get(p.id);
  if (p.track_serial) {
    let serials = item?.serials || [];
    if (serial) {
      if (serials.includes(serial)) { toast(`IMEI / serial ${serial} đã có trong giỏ`, 'error'); return false; }
      serials = [...serials, serial];
    } else {
      const picked = await pickSerials(p, serials);
      if (!picked) return false;
      serials = picked;
    }
    if (serials.length) POS.cart.set(p.id, { product: item?.product || p, qty: serials.length, max: p.stock, serials });
    else POS.cart.delete(p.id);
    savePOSDraft();
    return true;
  }
  const newQty = (item?.qty || 0) + qty;
  if (newQty > p.stock) { toast(p.stock > 0 ? `"${p.name}" chỉ còn ${p.stock} sản phẩm` : `"${p.name}" đã hết hàng`, 'error'); return false; }
  POS.cart.set(p.id, { product: item?.product || p, qty: newQty, max: p.stock, serials: [] });
  savePOSDraft();  // cả khi thêm từ máy quét hay từ trợ lý AI ở trang khác
  return true;
}

// Mã quét được: mã sản phẩm (tem QR / mã vạch) hoặc IMEI / serial của một máy cụ thể
async function addByCode(code) {
  code = String(code || '').trim();
  if (!code) return null;
  const p = await api(`/products/by-code/${encodeURIComponent(code)}`);
  return (await addToCart(p, 1, p.serial || null)) ? p : null;
}

// Ô giảm giá (chỉ chủ cửa hàng): theo ₫ là ô tiền (tự thêm dấu chấm), theo % thì cho gõ số lẻ (12,5).
// convert: người dùng vừa đổi loại -> giữ con số đã gõ, chỉ đổi cách viết cho hợp loại mới
function syncDiscMode(convert = false) {
  const el = $('#disc');
  if (!el) return;
  const pct = $('#disc-type').value === 'percent';
  el.toggleAttribute('data-money', !pct);
  el.inputMode = pct ? 'decimal' : 'numeric';
  if (convert) el.value = pct ? String(Math.min(parseMoney(el.value) ?? 0, 100)) : fmtMoneyInput(Math.round(parseFloat(el.value.replace(',', '.')) || 0));
}

const promoLabel = (p) => `${p.name} · giảm ${p.discount_type === 'percent' ? `${p.value}%${p.max_discount ? ` tối đa ${money(p.max_discount)}` : ''}` : money(p.value)}`
  + (p.min_subtotal ? ` · đơn từ ${money(p.min_subtotal)}` : '');
const currentPromo = () => POS.voucher || POS.promos.find((p) => String(p.id) === String(POS.promoId)) || null;
function promoValue(p, subtotal) {
  if (!p || subtotal < p.min_subtotal) return 0;
  let d = p.discount_type === 'percent' ? Math.round(subtotal * p.value / 100) : p.value;
  if (p.discount_type === 'percent' && p.max_discount) d = Math.min(d, p.max_discount);
  return Math.min(d, subtotal);
}

// Tính tiền giống hệt máy chủ: hạng thành viên + khuyến mãi / voucher + giảm thêm (chủ cửa hàng) + dùng điểm
function cartTotals() {
  const rows = [...POS.cart.values()];
  const cfg = S.payCfg || {};
  const subtotal = rows.reduce((s, r) => s + r.product.sale_price * r.qty, 0);
  const tierPct = POS.customer?.tier?.discount_percent || 0;
  const tier = Math.round(subtotal * tierPct / 100);
  const promo = currentPromo();
  const promoDisc = promoValue(promo, subtotal);
  const promoShort = promo && subtotal < promo.min_subtotal ? promo.min_subtotal - subtotal : 0;
  const isPct = $('#disc-type')?.value === 'percent';
  const raw = $('#disc')?.value ?? '';
  const dv = Math.max(0, (isPct ? parseFloat(raw.replace(',', '.')) : parseMoney(raw)) || 0);
  const manual = isPct ? Math.round(subtotal * Math.min(dv, 100) / 100) : dv;
  const pv = cfg.point_value || 0;
  const pointsLimit = pv ? Math.floor(Math.max(0, subtotal - tier - promoDisc - manual) * (cfg.points_max_percent ?? 0) / 100 / pv) : 0;
  const maxPoints = Math.min(POS.customer?.points || 0, pointsLimit);
  const points = Math.min(POS.pointsUsed || 0, maxPoints);
  const pointsDisc = points * pv;
  const discount = tier + promoDisc + manual + pointsDisc;
  const total = Math.max(0, subtotal - discount);
  const earn = POS.customer && cfg.points_earn_amount ? Math.floor(total / cfg.points_earn_amount) : 0;
  return { rows, subtotal, tier, tierPct, promo, promoDisc, promoShort, manual, points, maxPoints, pointsDisc, discount,
    total, earn, over: discount > subtotal, dv, isPct };
}

function cashSuggestions(total) {
  if (!total) return [];
  const out = new Set([total]);
  for (const step of [10000, 50000, 100000, 200000, 500000]) out.add(Math.ceil(total / step) * step);
  return [...out].sort((a, b) => a - b).slice(0, 4);
}

async function pagePOS(page) {
  await loadCategories();
  POS.promos = await api('/promotions/active').catch(() => []);
  const owner = isManager();
  const payButtons = Object.entries(PAY).map(([k, v]) => `<button type="button" class="pay-method" data-pay="${k}">${icon(v.icon)}${v.label}</button>`).join('');
  page.innerHTML = `
    ${POS.editing ? `<div class="edit-banner">${icon('pause')}<span>Đang mở hóa đơn tạm <b>${esc(POS.editing.code)}</b>: sửa giỏ hàng rồi bấm <b>Thanh toán</b>, hoặc <b>Lưu tạm</b> để giữ tiếp</span><span class="spacer"></span><button class="btn sm" id="cancel-edit">Đóng hóa đơn tạm</button></div>` : ''}
    <div class="pos">
      <div class="card pos-products">
        <div class="toolbar">
          <div class="input-icon grow">${icon('search')}<input id="pos-q" placeholder="Tìm tên, mã sản phẩm hoặc quét mã vạch / IMEI rồi Enter" autocomplete="off"></div>
          <select id="pos-cat">${categoryOptions('')}</select>
          <button class="btn primary" id="scan-btn">${icon('scan')} Quét QR</button>
        </div>
        <div id="pos-grid" class="product-grid">${skeletonTiles()}</div>
      </div>
      <div class="card cart">
        <div class="card-head m-0"><h2>${icon('cart')}Giỏ hàng <span class="badge" id="cart-count">0</span></h2>
          <div class="row"><a href="#invoices?status=pending" class="btn ghost sm icon-only" title="Hóa đơn tạm chưa thanh toán" aria-label="Hóa đơn tạm">${icon('pause')}</a>
          <button class="btn ghost sm icon-only" id="cart-clear" title="Xóa hết giỏ hàng" aria-label="Xóa hết">${icon('trash')}</button></div></div>
        <div>
          <span class="section-label">Khách hàng</span>
          <div class="row"><div class="input-icon flex-1">${icon('user')}<input id="cust-q" placeholder="Khách lẻ · gõ tên hoặc SĐT để tìm" autocomplete="off"></div>
            <button class="btn icon-only" id="cust-new" title="Thêm khách hàng mới">${icon('plus')}</button></div>
          <div id="cust-results"></div>
          <div id="cust-selected"></div>
        </div>
        <div id="cart-items" class="cart-items"></div>
        <div><span class="section-label">Khuyến mãi, voucher</span>
          <select id="promo-sel" class="w-full"><option value="">Không áp dụng chương trình khuyến mãi</option>
            ${POS.promos.map((p) => `<option value="${p.id}">${esc(promoLabel(p))}</option>`).join('')}</select>
          <div class="row mt-2"><div class="input-icon flex-1">${icon('gift')}<input id="voucher-in" placeholder="Mã voucher khách đưa" autocomplete="off"></div>
            <button type="button" class="btn" id="voucher-btn">Áp dụng</button></div>
          <div id="promo-info"></div></div>
        ${owner ? `<div class="discount-row">
          <label>Giảm giá thêm<input id="disc" ${MONEY_ATTRS} value="0"></label>
          <label>Loại<select id="disc-type"><option value="amount">₫</option><option value="percent">%</option></select></label>
        </div>` : ''}
        <div><span class="section-label">Phương thức thanh toán</span><div class="pay-methods">${payButtons}</div></div>
        <div class="pay-detail" id="pay-detail"></div>
        <label>Ghi chú<input id="inv-note" placeholder="Không bắt buộc"></label>
        <div class="totals" id="totals"></div>
        <div class="row"><button class="btn lg" id="hold" title="Lưu hóa đơn chưa thanh toán (chưa trừ kho), mở lại để sửa / thanh toán sau">${icon('pause')} Lưu tạm</button>
          <button class="btn primary lg flex-1" id="checkout"></button></div>
      </div>
    </div>`;

  const loadProducts = async () => {
    const data = await api('/products', { params: { q: $('#pos-q').value, category_id: $('#pos-cat').value, status: 'active', size: 200 } });
    POS.products = data.items;
    $('#pos-grid').innerHTML = data.items.map((p) => {
      const avail = p.stock;
      const badge = avail <= 0 ? '<span class="badge red">Hết hàng</span>' : avail <= p.min_stock ? `<span class="badge yellow">Còn ${avail}</span>` : `<span class="badge green">Còn ${avail}</span>`;
      return `<button class="product-tile" data-id="${p.id}" ${avail <= 0 ? 'disabled' : ''} title="${esc(p.name)}">
        <div class="tile-img">${thumb(p)}${p.track_serial ? '<span class="badge blue">IMEI</span>' : ''}</div>
        <div class="tile-body"><span class="tile-meta">${esc(p.code)} · ${esc(p.category_name || 'Chưa phân nhóm')}</span>
          <span class="tile-name">${esc(p.name)}</span>
          <div class="tile-foot"><span class="price">${money(p.sale_price)}</span>${badge}</div></div></button>`;
    }).join('') || `<div class="span-all">${emptyState('package', 'Không tìm thấy sản phẩm', 'Thử từ khóa khác hoặc chọn nhóm hàng khác.')}</div>`;
  };

  const updatePayInfo = () => {
    const t = cartTotals();
    const pay = POS.pay;
    let cashShort = false;
    if (pay.method === 'cash' && $('#cash-chips')) {
      const given = Number(pay.cash) || 0;
      cashShort = pay.cash !== '' && given < t.total;
      $('#cash-chips').innerHTML = cashSuggestions(t.total).map((v) => `<button type="button" class="chip" data-cash="${v}">${num(v)}</button>`).join('');
      $('#change-out').innerHTML = pay.cash === '' ? '<span class="muted">Khách đưa đủ</span>'
        : cashShort ? `<span class="error">Thiếu ${money(t.total - given)}</span>` : money(given - t.total);
    }
    if (pay.method === 'qr' && $('#qr-amount')) $('#qr-amount').textContent = money(t.total);
    const blocked = !t.rows.length || t.over || t.promoShort > 0;
    $('#hold').disabled = blocked;
    const btn = $('#checkout');
    btn.disabled = blocked || cashShort || t.total <= 0;
    btn.innerHTML = pay.method === 'qr' ? `${icon('qr')} Tạo mã QR · ${money(t.total)}` : `${icon('check')} Thanh toán · ${money(t.total)}`;
  };

  const renderPayDetail = () => {
    const pay = POS.pay;
    $$('.pay-method').forEach((b) => b.classList.toggle('active', b.dataset.pay === pay.method));
    const box = $('#pay-detail');
    const cfg = S.payCfg || {};
    if (pay.method === 'cash') {
      box.innerHTML = `<label>Tiền khách đưa<input id="cash-in" ${MONEY_ATTRS} placeholder="Bỏ trống nếu khách đưa đủ" value="${fmtMoneyInput(pay.cash)}"></label>
        <div class="cash-chips" id="cash-chips"></div>
        <div class="change-row"><span>Tiền thừa trả khách</span><span id="change-out"></span></div>`;
      // pay.cash giữ dạng chữ số liền (không dấu chấm) để tính tiền thừa và gửi lên server
      $('#cash-in').oninput = (e) => { pay.cash = String(parseMoney(e.target.value) ?? ''); updatePayInfo(); };
      $('#cash-chips').onclick = (e) => { const v = e.target.dataset.cash; if (v) { pay.cash = v; $('#cash-in').value = fmtMoneyInput(v); updatePayInfo(); } };
    } else if (pay.method === 'transfer') {
      pay.ref = pay.ref || `SALESAI ${stamp()}`;
      box.innerHTML = `<div class="bank-info"><span class="k">Ngân hàng</span><span>${esc(cfg.bank_name || '')}</span>
          <span class="k">Số tài khoản</span><span class="strong">${esc(cfg.account_no || '')}</span>
          <span class="k">Chủ tài khoản</span><span>${esc(cfg.account_name || '')}</span></div>
        <label>Nội dung / mã giao dịch chuyển khoản<input id="pay-ref" maxlength="50" value="${esc(pay.ref)}"></label>
        <span class="muted small">Kiểm tra đã nhận tiền trong tài khoản trước khi bấm thanh toán.</span>`;
      $('#pay-ref').oninput = (e) => { pay.ref = e.target.value; };
    } else if (pay.method === 'card') {
      box.innerHTML = `<label>Mã giao dịch trên máy POS<input id="pay-ref" maxlength="50" placeholder="Không bắt buộc, VD: 123456" value="${esc(pay.ref)}"></label>
        <span class="muted small">Quẹt / chạm thẻ trên máy POS với đúng số tiền cần thanh toán.</span>`;
      $('#pay-ref').oninput = (e) => { pay.ref = e.target.value; };
    } else {
      box.innerHTML = `<div class="row gap-3">${icon('qr')}<div><div class="strong">Khách quét VietQR bằng app ngân hàng</div>
        <div class="muted small">Bấm nút bên dưới để hiện mã QR <span id="qr-amount"></span> kèm số tiền và nội dung.</div></div></div>`;
    }
    updatePayInfo();
  };

  const renderPromoInfo = (t) => {
    const box = $('#promo-info');
    if (!t.promo) { box.innerHTML = ''; return; }
    box.innerHTML = t.promoShort
      ? note(`"${t.promo.name}" áp dụng cho đơn từ ${money(t.promo.min_subtotal)}: mua thêm ${money(t.promoShort)} hoặc bỏ chương trình`)
      : `<div class="muted small mt-2">${icon('check')} ${esc(t.promo.name)}: giảm <b>${money(t.promoDisc)}</b>
        ${POS.voucher ? ` · <button type="button" class="link-btn" data-voucher-clear>Bỏ voucher ${esc(POS.voucher.code)}</button>` : ''}</div>`;
  };

  const renderCart = () => {
    const t = cartTotals();
    if (t.points !== (POS.pointsUsed || 0)) {  // giỏ hàng nhỏ lại: số điểm được dùng giảm theo
      POS.pointsUsed = t.points;
      const el = $('#pts');
      if (el && document.activeElement !== el) el.value = t.points || '';
    }
    $('#cart-count').textContent = t.rows.reduce((s, r) => s + r.qty, 0);
    $('#cart-items').innerHTML = t.rows.length ? t.rows.map(({ product: p, qty, serials }) => `
      <div class="cart-row">${thumb(p)}
        <div class="min-w-0"><div class="name" title="${esc(p.name)}">${esc(p.name)}</div>
          ${p.track_serial ? serialChips(serials) : ''}
          <div class="line">${p.track_serial
            ? `<button class="btn sm" data-serial="${p.id}" title="Chọn máy theo IMEI / serial">${icon('hash')} ${qty} máy · đổi IMEI</button>`
            : `<div class="qty"><button data-dec="${p.id}" aria-label="Giảm">${icon('minus')}</button><input type="number" min="1" value="${qty}" data-qty="${p.id}"><button data-inc="${p.id}" aria-label="Tăng">${icon('plus')}</button></div>`}
          <span class="strong num">${money(p.sale_price * qty)}</span></div></div>
        <button class="btn ghost sm icon-only" data-del="${p.id}" title="Xóa khỏi giỏ">${icon('x')}</button></div>`).join('')
      : emptyState('scan', 'Giỏ hàng trống', 'Chọn sản phẩm bên trái hoặc quét mã QR / IMEI để thêm vào giỏ.', { compact: true, dashed: true });
    const minus = (label, v, cls = '') => (v ? `<div><span class="muted">${label}</span><span ${cls}>- ${money(v)}</span></div>` : '');
    $('#totals').innerHTML = `<div><span class="muted">Tạm tính</span><span>${money(t.subtotal)}</span></div>
      ${minus(`Hạng ${esc(POS.customer?.tier?.name || '')} (${t.tierPct}%)`, t.tier)}
      ${minus(POS.voucher ? `Voucher ${esc(POS.voucher.code)}` : 'Khuyến mãi', t.promoDisc)}
      ${minus('Giảm giá thêm', t.manual, t.over ? 'class="error"' : '')}
      ${minus(`Dùng ${num(t.points)} điểm`, t.pointsDisc)}
      <div class="grand"><span>Tổng cộng</span><span>${money(t.total)}</span></div>
      ${t.earn ? `<div class="small"><span class="muted">Điểm tích lũy sẽ cộng</span><span>+${num(t.earn)}</span></div>` : ''}`;
    renderPromoInfo(t);
    updatePayInfo();
    savePOSDraft();  // mọi thay đổi giỏ hàng / giảm giá đều đi qua đây
  };
  POS.renderCart = renderCart;

  const renderCustomer = () => {
    const c = POS.customer;
    const cfg = S.payCfg || {};
    $('#cust-selected').innerHTML = c ? `<div class="customer-pill"><div class="avatar">${esc(c.name.split(/\s+/).slice(-1)[0][0])}</div>
      <div class="grow"><div class="strong">${esc(c.name)} ${tierBadge(c.tier)}</div>
        <div class="muted small">${esc(c.phone || '')} · ${GROUP_VI[c.group] || ''} · ${num(c.points)} điểm</div></div>
      <button class="btn ghost sm icon-only" id="cust-clear" title="Bỏ chọn">${icon('x')}</button></div>
      ${cfg.point_value && c.points ? `<div class="row end mt-2"><label class="flex-1">Dùng điểm (1 điểm = ${money(cfg.point_value)})
        <input id="pts" type="number" min="0" placeholder="0" value="${POS.pointsUsed || ''}"></label>
        <button type="button" class="btn" id="pts-max">Dùng tối đa</button></div>` : ''}` : '';
    $('#cust-clear')?.addEventListener('click', () => { POS.customer = null; POS.pointsUsed = 0; renderCustomer(); renderCart(); });
    $('#pts')?.addEventListener('input', (e) => { POS.pointsUsed = Math.max(0, parseInt(e.target.value, 10) || 0); renderCart(); });
    $('#pts')?.addEventListener('change', (e) => { e.target.value = POS.pointsUsed || ''; });
    $('#pts-max')?.addEventListener('click', () => {
      POS.pointsUsed = c.points;
      renderCart();  // tự giảm về mức tối đa được dùng
      $('#pts').value = POS.pointsUsed || '';
    });
    savePOSDraft();
  };

  // Tìm kiếm; máy quét mã vạch USB gõ mã (mã sản phẩm hoặc IMEI) + Enter => thêm thẳng vào giỏ
  let t;
  $('#pos-q').oninput = () => { clearTimeout(t); t = setTimeout(loadProducts, 250); };
  $('#pos-q').onkeydown = async (e) => {
    if (e.key !== 'Enter') return;
    e.preventDefault();
    const code = e.target.value.trim();
    if (!code) return;
    try {
      const p = await addByCode(code);
      if (p) { beep(); toast(`Đã thêm ${p.name}${p.serial ? ` (IMEI ${p.serial})` : ''}`, 'success'); renderCart(); }
      e.target.value = '';
      loadProducts();
    } catch (err) {
      if (err.status !== 404) toast(err.message, 'error');
    }
  };
  $('#pos-cat').onchange = loadProducts;
  $('#scan-btn').onclick = () => openScanner();
  $('#pos-grid').onclick = async (e) => {
    const tile = e.target.closest('[data-id]');
    if (!tile || tile.disabled) return;
    if (await addToCart(POS.products.find((p) => p.id == tile.dataset.id))) renderCart();
  };
  $('#cart-items').onclick = async (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    const id = +(b.dataset.inc || b.dataset.dec || b.dataset.del || b.dataset.serial);
    const item = POS.cart.get(id);
    if (!item) return;
    if (b.dataset.serial) await addToCart(item.product);
    else if (b.dataset.inc) await addToCart(item.product, 1);
    else if (b.dataset.dec) { item.qty > 1 ? item.qty-- : POS.cart.delete(id); }
    else POS.cart.delete(id);
    renderCart();
  };
  $('#cart-items').onchange = (e) => {
    const id = +e.target.dataset.qty;
    if (!id) return;
    const item = POS.cart.get(id);
    const v = Math.max(1, parseInt(e.target.value, 10) || 1);
    if (v > item.max) toast(`Chỉ còn ${item.max} sản phẩm`, 'error');
    item.qty = Math.min(v, item.max);
    renderCart();
  };
  $('#cart-clear').onclick = () => { POS.cart.clear(); renderCart(); };
  if (owner) {
    $('#disc').oninput = renderCart;
    $('#disc-type').onchange = () => { syncDiscMode(true); renderCart(); };
  }
  $$('.pay-method').forEach((b) => b.onclick = () => { POS.pay = { method: b.dataset.pay, cash: '', ref: '' }; renderPayDetail(); savePOSDraft(); });
  $('#inv-note').oninput = savePOSDraft;

  // Khuyến mãi: một hóa đơn chỉ một chương trình (chọn trong danh sách) hoặc một voucher (nhập mã)
  $('#promo-sel').onchange = (e) => { POS.promoId = e.target.value; POS.voucher = null; $('#voucher-in').value = ''; renderCart(); };
  const applyVoucher = async () => {
    const code = $('#voucher-in').value.trim();
    if (!code) { $('#voucher-in').focus(); return; }
    try {
      POS.voucher = await api(`/promotions/voucher/${encodeURIComponent(code)}`, { params: { subtotal: cartTotals().subtotal } });
      POS.promoId = '';
      $('#promo-sel').value = '';
      $('#voucher-in').value = POS.voucher.code;
      toast(`Đã áp dụng voucher ${POS.voucher.code}`, 'success');
      renderCart();
    } catch (err) { toast(err.message, 'error'); }
  };
  $('#voucher-btn').onclick = applyVoucher;
  $('#voucher-in').onkeydown = (e) => { if (e.key === 'Enter') { e.preventDefault(); applyVoucher(); } };
  $('#promo-info').onclick = (e) => {
    if (!e.target.closest('[data-voucher-clear]')) return;
    POS.voucher = null;
    $('#voucher-in').value = '';
    renderCart();
  };

  let ct;
  $('#cust-q').oninput = () => {
    clearTimeout(ct);
    ct = setTimeout(async () => {
      const q = $('#cust-q').value.trim();
      if (!q) { $('#cust-results').innerHTML = ''; return; }
      const data = await api('/customers', { params: { q, size: 8 } });
      $('#cust-results').innerHTML = data.items.length ? `<div class="search-results">${data.items.map((c) =>
        `<div data-cid="${c.id}"><span>${esc(c.name)} <span class="muted">· ${esc(c.phone || '')}</span></span><span class="row">${tierBadge(c.tier)}${groupBadge(c.group)}</span></div>`).join('')}</div>`
        : '<p class="muted small mt-2 mb-0">Không tìm thấy khách hàng</p>';
      $$('[data-cid]').forEach((el) => el.onclick = () => {
        POS.customer = data.items.find((c) => c.id == el.dataset.cid);
        POS.pointsUsed = 0;
        $('#cust-q').value = ''; $('#cust-results').innerHTML = '';
        renderCustomer();
        renderCart();
      });
    }, 250);
  };
  $('#cust-new').onclick = () => customerForm(null, (c) => { POS.customer = { ...c, tier: null }; renderCustomer(); renderCart(); });
  $('#cancel-edit')?.addEventListener('click', () => { resetPOS(); navigate(); });

  // pay = false: lưu hóa đơn tạm (chưa trừ kho); true: thanh toán
  const submit = async (pay) => {
    const tt = cartTotals();
    const p = POS.pay;
    let ref = p.method === 'cash' ? null : (p.ref || '').trim() || null;
    if (pay && p.method === 'qr') {
      ref = await showQRPayment(tt.total);
      if (!ref) return;
    }
    const body = {
      customer_id: POS.customer?.id ?? null,
      items: tt.rows.map((r) => ({ product_id: r.product.id, quantity: r.qty, ...(r.product.track_serial ? { serials: r.serials } : {}) })),
      promotion_id: POS.voucher ? null : (+POS.promoId || null),
      voucher_code: POS.voucher?.code || null,
      points_used: tt.points,
      pay, payment_method: p.method,
      cash_received: pay && p.method === 'cash' && p.cash !== '' ? Number(p.cash) : null,
      payment_ref: ref,
      note: $('#inv-note').value.trim() || null,
      ...(owner ? (tt.isPct ? { discount_percent: Math.min(tt.dv, 100) } : { discount: tt.dv }) : {}),
    };
    $('#checkout').disabled = $('#hold').disabled = true;
    try {
      const inv = POS.editing
        ? await api(`/invoices/${POS.editing.id}`, { method: 'PUT', body })
        : await api('/invoices', { method: 'POST', body });
      toast(pay ? 'Thanh toán thành công' : `Đã lưu hóa đơn tạm ${inv.code}, mở lại ở menu Hóa đơn để thanh toán`, 'success');
      const wasEditing = Boolean(POS.editing);
      resetPOS();
      if (!wasEditing) clearPOSDraft();
      if (pay) showReceipt(inv);
      refreshCounts();
      navigate();
    } catch (e) {
      toast(e.message, 'error');
      updatePayInfo();
    }
  };
  $('#checkout').onclick = () => submit(true);
  $('#hold').onclick = () => submit(false);

  if (POS.editing) {
    if (owner) $('#disc').value = fmtMoneyInput(POS.editing.discount || 0);
    $('#inv-note').value = POS.editing.note || '';
  } else {
    // Đơn đang bán dở: giảm giá / ghi chú luôn lấy lại; giỏ hàng chỉ khôi phục khi trống (vừa tải lại trang)
    const draft = readPOSDraft();
    if (draft) {
      if (owner) {
        $('#disc-type').value = draft.discountType === 'percent' ? 'percent' : 'amount';
        syncDiscMode();
        $('#disc').value = draft.discountType === 'percent' ? (draft.discount ?? '0') : fmtMoneyInput(draft.discount ?? '0');
      }
      $('#inv-note').value = draft.note ?? '';
      if (!POS.cart.size && (draft.items?.length || draft.customer)) {
        const dropped = await restorePOSDraft(draft);
        if (!document.body.contains($('#inv-note'))) return;  // đã chuyển sang trang khác trong lúc chờ
        const n = [...POS.cart.values()].reduce((s, r) => s + r.qty, 0);
        if (n || dropped) {
          toast(`Đã khôi phục đơn đang bán dở${n ? ` (${n} sản phẩm)` : ''}`
            + (dropped ? `. ${dropped} sản phẩm đã hết hàng hoặc ngừng bán nên được bỏ khỏi giỏ` : ''), dropped ? 'error' : 'success');
        }
      }
    }
  }
  if (POS.promoId && !POS.promos.some((p) => String(p.id) === String(POS.promoId))) POS.promoId = '';  // chương trình đã hết hạn
  $('#promo-sel').value = POS.promoId || '';
  if (POS.voucher) $('#voucher-in').value = POS.voucher.code;
  renderCustomer();
  renderPayDetail();
  renderCart();
  await loadProducts();
  $('#pos-q').focus();
}

// Mã VietQR: khách quét bằng app ngân hàng, thu ngân xác nhận đã nhận tiền
async function showQRPayment(amount) {
  let qr;
  try {
    qr = await api('/payments/vietqr', { method: 'POST', body: { amount, content: `SALESAI ${stamp()}` } });
  } catch (e) { toast(e.message, 'error'); return null; }
  return new Promise((resolve) => {
    const m = modal({
      title: `${icon('qr')} Quét mã để thanh toán`, size: 'wide',
      body: `<div class="qr-pay"><div class="qr-box">${qr.svg}</div>
        <div class="stack gap-3">
          <div><div class="muted small">Số tiền cần thanh toán</div><div class="qr-amount">${money(qr.amount)}</div></div>
          <div class="bank-info"><span class="k">Ngân hàng</span><span>${esc(qr.bank_name)}</span>
            <span class="k">Số tài khoản</span><span class="strong">${esc(qr.account_no)}</span>
            <span class="k">Chủ tài khoản</span><span>${esc(qr.account_name)}</span>
            <span class="k">Nội dung</span><span class="strong">${esc(qr.content)}</span></div>
          <p class="muted small m-0">Khách mở app ngân hàng bất kỳ, chọn <b>Quét QR</b>. Số tiền và nội dung được điền sẵn. Kiểm tra tài khoản đã nhận tiền rồi bấm xác nhận.</p>
          ${qr.is_demo ? note('Đang dùng tài khoản DEMO. Chủ cửa hàng cấu hình tài khoản nhận tiền ở menu Tham số kinh doanh.') : ''}
        </div></div>`,
      footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="qr-ok">${icon('check')} Đã nhận tiền, hoàn tất</button>`,
      onClose: () => resolve(null),
    });
    $('#qr-ok', m.el).onclick = () => { resolve(qr.content); m.close(); };
  });
}

// Quét mã bằng camera (thư viện html5-qrcode) hoặc máy quét mã vạch USB / nhập tay.
// Mặc định thêm sản phẩm vào giỏ; onCode: dùng cho màn hình khác (tra hóa đơn đổi trả, bảo hành), quét một mã rồi đóng.
function openScanner({ onCode = null, title = 'Quét mã sản phẩm', placeholder = 'Nhập mã hoặc dùng máy quét mã vạch USB, rồi Enter' } = {}) {
  let scanner = null;
  let last = { code: '', at: 0 };
  const m = modal({
    title: `${icon('scan')} ${title}`,
    body: `<div class="scanner" id="scanner-box"><div id="scanner-view" class="w-full"></div><div id="scanner-msg" class="loading">${'<span class="spinner"></span> Đang mở camera...'}</div></div>
      <div class="toolbar mt mb-0">
        <div class="input-icon grow">${icon('barcode')}<input id="scan-manual" placeholder="${esc(placeholder)}" autocomplete="off"></div>
        <button class="btn" id="scan-add">${icon(onCode ? 'search' : 'plus')} ${onCode ? 'Tra cứu' : 'Thêm'}</button></div>
      ${onCode ? '' : `<h3 class="mt">Đã thêm vào giỏ</h3><div class="scan-log" id="scan-log"><p class="muted small m-0">Chưa quét sản phẩm nào</p></div>`}`,
    footer: `<button class="btn primary" data-close>${icon('check')} Xong</button>`,
    onClose: () => {
      if (scanner?.isScanning) scanner.stop().then(() => scanner.clear()).catch(() => {});
      if (!onCode) POS.renderCart?.();
    },
  });
  const log = $('#scan-log', m.el);
  const handle = async (code) => {
    code = code.trim();
    const now = Date.now();
    if (!code || (code === last.code && now - last.at < 2000)) return;
    last = { code, at: now };
    if (onCode) { beep(); m.close(); onCode(code); return; }
    try {
      const p = await addByCode(code);
      if (!p) return;
      beep();
      if (log.querySelector('p')) log.innerHTML = '';
      log.insertAdjacentHTML('afterbegin', `<div>${thumb(p, 'sm')}<span class="grow flex-1">${esc(p.name)}${p.serial ? ` <span class="muted">· ${esc(p.serial)}</span>` : ''}</span><span class="badge green">+1</span></div>`);
      POS.renderCart?.();
    } catch (e) { toast(e.message, 'error'); }
  };
  const manual = $('#scan-manual', m.el);
  manual.onkeydown = (e) => { if (e.key === 'Enter') { e.preventDefault(); handle(manual.value); manual.value = ''; } };
  $('#scan-add', m.el).onclick = () => { handle(manual.value); manual.value = ''; manual.focus(); };

  const msg = $('#scanner-msg', m.el);
  if (!window.Html5Qrcode) {
    msg.textContent = 'Không tải được thư viện quét (cần Internet). Hãy nhập mã hoặc dùng máy quét USB.';
    return;
  }
  scanner = new Html5Qrcode('scanner-view', { verbose: false });
  scanner.start({ facingMode: 'environment' }, { fps: 10, qrbox: { width: 220, height: 220 } }, (text) => handle(text), () => {})
    .then(() => msg.remove())
    .catch(() => { msg.textContent = 'Không mở được camera (chưa cấp quyền hoặc máy không có camera). Hãy nhập mã hoặc dùng máy quét USB.'; });
}

// Mở hóa đơn tạm (chưa thanh toán) ở màn hình bán hàng để sửa / thanh toán
async function editInvoice(inv) {
  resetPOS();
  clearPOSDraft();  // như trước: mở hóa đơn tạm thay thế đơn đang bán dở
  POS.editing = { id: inv.id, code: inv.code, discount: inv.manual_discount, note: inv.note };
  POS.pay = { method: inv.payment_method, cash: '', ref: '' };
  if (inv.customer_id) POS.customer = await api(`/customers/${inv.customer_id}`);
  for (const it of inv.items) {
    const p = await api(`/products/${it.product_id}`);
    POS.cart.set(p.id, { product: p, qty: it.quantity, max: p.stock, serials: it.serials || [] });
  }
  POS.pointsUsed = inv.points_used || 0;
  if (inv.voucher_code) POS.voucher = await api(`/promotions/voucher/${encodeURIComponent(inv.voucher_code)}`).catch(() => null);
  else POS.promoId = inv.promotion_id || '';
  if (location.hash === '#pos') navigate(); else location.hash = '#pos';
}

function paymentLines(inv) {
  let html = `<div><span>Thanh toán</span><span>${payLabel(inv.payment_method)}</span></div>`;
  if (inv.cash_received != null) html += `<div><span>Khách đưa</span><span>${money(inv.cash_received)}</span></div><div><span>Tiền thừa</span><span>${money(inv.change)}</span></div>`;
  if (inv.payment_ref) html += `<div><span>Mã giao dịch</span><span>${esc(inv.payment_ref)}</span></div>`;
  return html;
}

// Các khoản giảm trên hóa đơn (hạng, khuyến mãi / voucher, giảm tay, dùng điểm)
function discountLines(inv) {
  return [['tier_discount', 'Giảm hạng thành viên'], ['promo_discount', inv.voucher_code ? `Voucher ${inv.voucher_code}` : `KM: ${inv.promotion_name || ''}`],
    ['manual_discount', 'Giảm giá'], ['points_discount', `Dùng ${num(inv.points_used)} điểm`]]
    .filter(([k]) => inv[k]).map(([k, label]) => [label, inv[k]]);
}

// Hỏi một giá trị (email nhận hóa đơn...). Trả về chuỗi đã nhập hoặc null.
function promptBox(title, label, value = '', type = 'text') {
  return new Promise((resolve) => {
    let done = false;
    const m = modal({
      title, size: 'narrow',
      body: `<form id="pb-form"><label>${esc(label)}<input id="pb-input" type="${type}" required value="${esc(value)}"></label></form>`,
      footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="pb-ok">${icon('check')} Đồng ý</button>`,
      onClose: () => { if (!done) resolve(null); },
    });
    const form = $('#pb-form', m.el);
    const ok = () => { if (!form.reportValidity()) return; done = true; resolve($('#pb-input', m.el).value.trim()); m.close(); };
    form.onsubmit = (e) => { e.preventDefault(); ok(); };
    $('#pb-ok', m.el).onclick = ok;
    $('#pb-input', m.el).focus();
  });
}

async function emailInvoice(inv) {
  const to = await promptBox(`${icon('mail')} Gửi hóa đơn ${esc(inv.code)} qua email`, 'Email nhận hóa đơn (kèm file PDF)', inv.customer_email || '', 'email');
  if (!to) return;
  try { toast((await api(`/invoices/${inv.id}/email`, { method: 'POST', body: { to } })).message, 'success'); }
  catch (e) { toast(e.message, 'error'); }
}

// Trang in hóa đơn khổ 80mm (máy in nhiệt) từ trình duyệt; mã QR trên hóa đơn để tra cứu khi đổi trả, bảo hành
function showReceipt(inv) {
  const cfg = S.payCfg || {};
  const shop = cfg.shop_name || 'Cửa hàng SalesAI';
  const m = modal({
    title: `${icon('receipt')} Hóa đơn ${esc(inv.code)}`, size: 'narrow',
    body: `<div class="receipt print-area">
      <div class="center"><b>${esc(shop.toUpperCase())}</b>${cfg.shop_address ? `<br>${esc(cfg.shop_address)}` : ''}${cfg.shop_phone ? `<br>ĐT: ${esc(cfg.shop_phone)}` : ''}
        <br>HÓA ĐƠN BÁN HÀNG<br>${esc(inv.code)} · ${fmtDate(inv.created_at)}</div><br>
      Khách hàng: ${esc(inv.customer_name)}<br>Thu ngân: ${esc(inv.user_name)}
      <table class="my-2"><thead><tr><th>Sản phẩm</th><th class="right">SL</th><th class="right">T.tiền</th></tr></thead><tbody>
      ${inv.items.map((i) => `<tr><td>${esc(i.product_name)}<br><small>${money(i.unit_price)}${i.serials?.length ? `<br>IMEI/SN: ${i.serials.map(esc).join(', ')}` : ''}${i.warranty_months ? `<br>Bảo hành ${i.warranty_months} tháng` : ''}</small></td>
        <td class="right">${i.quantity}</td><td class="right">${money(i.line_total)}</td></tr>`).join('')}
      </tbody></table>
      <div class="totals"><div><span>Tạm tính</span><span>${money(inv.subtotal)}</span></div>
      ${discountLines(inv).map(([k, v]) => `<div><span>${esc(k)}</span><span>- ${money(v)}</span></div>`).join('')}
      <div class="grand"><span>TỔNG</span><span>${money(inv.total)}</span></div>${inv.status === 'paid' ? paymentLines(inv) : ''}
      ${inv.points_earned ? `<div><span>Điểm tích lũy</span><span>+${num(inv.points_earned)}</span></div>` : ''}</div>
      ${inv.status === 'cancelled' ? `<p class="error center">ĐÃ HỦY: ${esc(inv.cancel_reason)}</p>` : inv.status === 'pending' ? '<p class="error center">HÓA ĐƠN TẠM - CHƯA THANH TOÁN</p>' : ''}
      ${inv.code_qr ? `<div class="receipt-qr">${inv.code_qr}<div class="small">Quét mã khi đổi trả, bảo hành</div></div>` : ''}
      <p class="center small">${cfg.return_hours ? `Đổi trả trong ${cfg.return_hours} giờ kèm hóa đơn. ` : ''}Cảm ơn quý khách!</p></div>`,
    footer: `<button class="btn" data-close>Đóng</button><button class="btn" id="rc-pdf">${icon('file')} PDF</button>
      <button class="btn" id="rc-mail">${icon('mail')} Email</button><button class="btn primary" id="print">${icon('printer')} In hóa đơn</button>`,
  });
  $('#print', m.el).onclick = () => window.print();
  $('#rc-pdf', m.el).onclick = () => download(`/invoices/${inv.id}/pdf`);
  $('#rc-mail', m.el).onclick = () => emailInvoice(inv);
}

// ============================================================ Hóa đơn
// Thu ngân: xem hóa đơn mình lập, mở hóa đơn tạm để thanh toán, gửi yêu cầu hủy. Chủ cửa hàng: xem tất cả, duyệt / từ chối hủy.
const INV_STATUS = [['', 'Tất cả'], ['paid', 'Đã thanh toán'], ['pending', 'Chưa thanh toán (hóa đơn tạm)'], ['cancelled', 'Đã hủy']];

async function pageInvoices(page) {
  const owner = isManager();
  const qs = routeQuery();
  const preset = qs.get('status') || '';
  const f = { q: qs.get('q') || '', status: preset, payment_method: '', date_from: preset ? '' : daysAgo(29), date_to: preset ? '' : today(), page: 1, size: 20 };
  const statuses = owner ? [...INV_STATUS, ['cancel_pending', 'Chờ duyệt hủy']] : INV_STATUS;
  page.innerHTML = `<div id="inv-alerts"></div><div class="card">
    <form class="toolbar" id="inv-filter">
      <label class="grow">Tìm kiếm<div class="input-icon">${icon('search')}<input name="q" placeholder="Mã hóa đơn, tên hoặc SĐT khách" value="${esc(f.q)}"></div></label>
      <label>Trạng thái<select name="status">${statuses.map(([k, v]) => `<option value="${k}" ${k === f.status ? 'selected' : ''}>${v}</option>`).join('')}</select></label>
      <label>Thanh toán<select name="payment_method"><option value="">Tất cả</option>${Object.entries(PAY).map(([k, v]) => `<option value="${k}">${v.label}</option>`).join('')}</select></label>
      <label>Từ ngày<input type="date" name="date_from" value="${f.date_from}"></label>
      <label>Đến ngày<input type="date" name="date_to" value="${f.date_to}"></label>
      <button class="btn primary">${icon('search')} Lọc</button>
      ${owner ? `<div class="actions">${exportButtons()}</div>` : ''}
    </form>
    <div id="inv-sum" class="muted mb-3"></div>
    <div id="inv-table">${skeletonLines()}</div></div>`;
  const params = () => {
    const { status, ...rest } = f;
    return status === 'cancel_pending' ? { ...rest, cancel_pending: true } : { ...rest, status };
  };
  const alerts = async () => {
    const c = await api('/invoices/pending-count').catch(() => ({}));
    const box = $('#inv-alerts');
    if (!box) return;
    const items = [];
    if (owner && c.cancel_requests) items.push(`<button class="btn sm" data-preset="cancel_pending">${icon('alert')} ${c.cancel_requests} yêu cầu hủy hóa đơn chờ duyệt</button>`);
    if (c.held_invoices) items.push(`<button class="btn sm" data-preset="pending">${icon('pause')} ${c.held_invoices} hóa đơn tạm chưa thanh toán</button>`);
    box.innerHTML = items.length ? `<div class="chips">${items.join('')}</div>` : '';
  };
  const load = async () => {
    const data = await api('/invoices', { params: params() });
    if (!$('#inv-table')) return;
    $('#inv-sum').innerHTML = `Tổng tiền hóa đơn đã thanh toán theo bộ lọc: <b class="num text-default">${money(data.sum_paid)}</b>`;
    $('#inv-table').innerHTML = table(
      ['Mã hóa đơn', 'Thời gian', 'Khách hàng', 'Thu ngân', ['Tổng tiền', 'right'], 'Thanh toán', 'Trạng thái'],
      data.items.map((i) => [`<b>${esc(i.code)}</b>`, `<span class="nowrap">${fmtDate(i.created_at)}</span>`, esc(i.customer_name), esc(i.user_name),
        `<b>${money(i.total)}</b>`, i.status === 'pending' ? '<span class="muted">-</span>' : payCell(i.payment_method), statusBadge(i.status, i.cancel_requested_at)]),
      { empty: 'Không có hóa đơn', rowAttrs: (k) => `class="clickable" data-id="${data.items[k].id}"` });
    $('#inv-table').appendChild(pager(data.total, f.page, f.size, (p) => { f.page = p; load(); }));
  };
  const reload = () => { load(); alerts(); refreshCounts(); };
  $('#inv-filter').onsubmit = (e) => { e.preventDefault(); Object.assign(f, formValues(e.target), { page: 1 }); load(); };
  $('#inv-alerts').onclick = (e) => {
    const b = e.target.closest('[data-preset]');
    if (!b) return;
    const form = $('#inv-filter');
    form.status.value = b.dataset.preset;
    form.date_from.value = form.date_to.value = '';
    form.requestSubmit();
  };
  $$('[data-exp]').forEach((b) => b.onclick = () => {
    const { page: _p, size: _s, ...rest } = { ...f, ...formValues($('#inv-filter')) };
    download('/reports/export/invoices', { ...rest, status: rest.status === 'cancel_pending' ? '' : rest.status, format: b.dataset.exp });
  });
  $('#inv-table').onclick = (e) => { const r = e.target.closest('tr[data-id]'); if (r) invoiceDetail(r.dataset.id, reload); };
  await Promise.all([load(), alerts()]);
}

async function invoiceDetail(id, onChange) {
  const inv = await api(`/invoices/${id}`);
  const owner = isManager();
  const requested = inv.status === 'paid' && inv.cancel_requested_at;
  const hasReturns = inv.returns?.length > 0;
  let left = '';
  let right = '';
  if (inv.status === 'pending') {
    left = `<button class="btn danger left" id="inv-cancel">${icon('x')} Hủy hóa đơn tạm</button>`;
    right = `<button class="btn primary" id="inv-open">${icon('cart')} Mở để sửa / thanh toán</button>`;
  } else {
    if (inv.status === 'paid') {
      if (owner && requested) left = `<button class="btn left" id="inv-reject">${icon('x')} Từ chối hủy</button><button class="btn danger" id="inv-cancel">${icon('check')} Duyệt hủy</button>`;
      else if (owner && !hasReturns) left = `<button class="btn danger left" id="inv-cancel">${icon('x')} Hủy hóa đơn</button>`;
      else if (!owner && !requested && !hasReturns) left = `<button class="btn danger left" id="inv-request">${icon('x')} Yêu cầu hủy</button>`;
      right = `<button class="btn" id="inv-return">${icon('undo')} Đổi trả</button><button class="btn" id="inv-warranty">${icon('wrench')} Bảo hành</button>`;
    }
    right += `<button class="btn primary" id="inv-print">${icon('printer')} In / PDF / Email</button>`;
  }
  const m = modal({
    title: `Hóa đơn ${esc(inv.code)} ${statusBadge(inv.status, requested)}`, size: 'wide',
    body: `<div class="info-list">
        <div><span class="k">${inv.status === 'pending' ? 'Lập lúc' : 'Thời gian'}</span>${fmtDate(inv.created_at)}</div>
        <div><span class="k">Thu ngân</span>${esc(inv.user_name)}</div>
        <div><span class="k">Khách hàng</span>${esc(inv.customer_name)} ${inv.customer_phone ? `<span class="muted">· ${esc(inv.customer_phone)}</span>` : ''}</div>
        ${inv.status === 'pending' ? '' : `<div><span class="k">Thanh toán</span>${payCell(inv.payment_method)}${inv.payment_ref ? ` <span class="muted">· ${esc(inv.payment_ref)}</span>` : ''}</div>`}
        ${inv.cash_received != null ? `<div><span class="k">Khách đưa / tiền thừa</span>${money(inv.cash_received)} / ${money(inv.change)}</div>` : ''}
        ${inv.points_used || inv.points_earned ? `<div><span class="k">Điểm tích lũy</span>${inv.points_used ? `dùng ${num(inv.points_used)}` : ''}${inv.points_used && inv.points_earned ? ' · ' : ''}${inv.points_earned ? `cộng ${num(inv.points_earned)}` : ''}</div>` : ''}
        ${inv.note ? `<div><span class="k">Ghi chú</span>${esc(inv.note)}</div>` : ''}
      </div>
      ${requested ? note(`${inv.cancel_requested_by} yêu cầu hủy lúc ${fmtDate(inv.cancel_requested_at)}. Lý do: ${inv.cancel_reason}. ${owner ? 'Duyệt để hoàn kho, hoàn điểm.' : 'Đang chờ chủ cửa hàng duyệt.'}`) : ''}
      ${inv.status === 'cancelled' ? note(`Hủy lúc ${fmtDate(inv.cancelled_at)} - Lý do: ${inv.cancel_reason}`) : ''}
      ${inv.status === 'pending' ? note('Hóa đơn tạm: chưa thanh toán, chưa trừ kho. Mở ở màn hình Bán hàng để sửa hoặc thanh toán.') : ''}
      ${hasReturns ? note(`Đã đổi trả: ${inv.returns.map((r) => `${r.code} (hoàn ${money(r.refund_total)})`).join(', ')}`) : ''}
      ${table(['Sản phẩm', ['SL', 'right'], ['Đơn giá', 'right'], ['Thành tiền', 'right']], inv.items.map((i) => [productCell(i) + serialChips(i.serials), i.quantity, money(i.unit_price), money(i.line_total)]))}
      <div class="totals totals-box">
        <div><span class="muted">Tạm tính</span><span>${money(inv.subtotal)}</span></div>
        ${discountLines(inv).map(([k, v]) => `<div><span class="muted">${esc(k)}</span><span>- ${money(v)}</span></div>`).join('')}
        <div class="grand"><span>Tổng cộng</span><span>${money(inv.total)}</span></div>
        ${inv.refunded ? `<div><span class="muted">Đã hoàn trả hàng</span><span>- ${money(inv.refunded)}</span></div>` : ''}</div>`,
    footer: left + right,
  });
  const act = (sel, fn) => $(sel, m.el)?.addEventListener('click', fn);
  const done = (msg) => { toast(msg, 'success'); m.close(); onChange?.(); };
  act('#inv-print', () => { m.close(); showReceipt(inv); });
  act('#inv-open', () => { m.close(); editInvoice(inv); });
  act('#inv-return', () => { m.close(); location.hash = `#returns?code=${encodeURIComponent(inv.code)}`; });
  act('#inv-warranty', () => { m.close(); location.hash = `#warranty?code=${encodeURIComponent(inv.code)}`; });
  act('#inv-cancel', async () => {
    const msg = inv.status === 'pending' ? `Hủy hóa đơn tạm ${inv.code}?` : `Hủy hóa đơn ${inv.code}? Tồn kho, serial và điểm tích lũy sẽ được hoàn lại.`;
    const reason = await confirmBox(msg, { input: true, okText: 'Hủy hóa đơn', danger: true, value: inv.cancel_reason || '' });
    if (!reason) return;
    try { await api(`/invoices/${inv.id}/cancel`, { method: 'POST', body: { reason } }); done(requested ? 'Đã duyệt hủy hóa đơn' : 'Đã hủy hóa đơn'); }
    catch (e) { toast(e.message, 'error'); }
  });
  act('#inv-request', async () => {
    const reason = await confirmBox(`Gửi yêu cầu hủy hóa đơn ${inv.code} cho chủ cửa hàng duyệt?`, { input: true, okText: 'Gửi yêu cầu', danger: true });
    if (!reason) return;
    try { await api(`/invoices/${inv.id}/cancel-request`, { method: 'POST', body: { reason } }); done('Đã gửi yêu cầu hủy, chờ chủ cửa hàng duyệt'); }
    catch (e) { toast(e.message, 'error'); }
  });
  act('#inv-reject', async () => {
    if (!await confirmBox(`Từ chối yêu cầu hủy hóa đơn ${inv.code}? Hóa đơn giữ nguyên.`, { okText: 'Từ chối' })) return;
    try { await api(`/invoices/${inv.id}/cancel-reject`, { method: 'POST', body: {} }); done('Đã từ chối yêu cầu hủy'); }
    catch (e) { toast(e.message, 'error'); }
  });
}

// ============================================================ Khách hàng
async function pageCustomers(page) {
  const f = { q: '', group: '', page: 1, size: 20 };
  const mgr = isManager();
  page.innerHTML = `<div class="card">
    <form class="toolbar" id="c-filter">
      <label class="grow">Tìm kiếm<div class="input-icon">${icon('search')}<input name="q" placeholder="Tên, SĐT hoặc mã khách"></div></label>
      <label>Nhóm khách<select name="group"><option value="">Tất cả</option>${Object.entries(GROUP_VI).map(([k, v]) => `<option value="${k}">${v}</option>`).join('')}</select></label>
      <button class="btn">${icon('search')} Lọc</button>
      <div class="actions"><button type="button" class="btn primary" id="c-add">${icon('plus')} Thêm khách hàng</button></div>
    </form><div id="c-table">${skeletonLines()}</div></div>`;
  let items = [];
  const load = async () => {
    const data = await api('/customers', { params: f });
    items = data.items;
    $('#c-table').innerHTML = table(['Mã', 'Khách hàng', 'Số điện thoại', 'Nhóm', 'Hạng', ['Điểm', 'right'], ['Số HĐ', 'right'], ['Tổng chi tiêu', 'right'], 'Mua gần nhất', ['', 'right']],
      items.map((c) => [esc(c.code), `<b>${esc(c.name)}</b>`, esc(c.phone || ''), groupBadge(c.group), tierBadge(c.tier), num(c.points), c.invoice_count, money(c.total_spent), fmtDate(c.last_purchase),
        `<div class="row-actions">
        <button class="btn ghost sm icon-only" data-edit="${c.id}" title="Sửa">${icon('edit')}</button>
        ${mgr ? `<button class="btn ghost sm icon-only danger" data-del="${c.id}" title="Xóa">${icon('trash')}</button>` : ''}</div>`]),
      { empty: 'Không có khách hàng', rowAttrs: (k) => `class="clickable" data-id="${items[k].id}"` });
    $('#c-table').appendChild(pager(data.total, f.page, f.size, (p) => { f.page = p; load(); }));
  };
  const find = (id) => items.find((c) => c.id == id);
  $('#c-filter').onsubmit = (e) => { e.preventDefault(); Object.assign(f, formValues(e.target), { page: 1 }); load(); };
  $('#c-add').onclick = () => customerForm(null, load);
  $('#c-table').onclick = async (e) => {
    const b = e.target.closest('button');
    if (b?.dataset.edit) return customerForm(find(b.dataset.edit), load);
    if (b?.dataset.del) {
      const c = find(b.dataset.del);
      if (!await confirmBox(`Xóa khách hàng ${c.name}? Khách đã có hóa đơn sẽ không xóa được.`, { danger: true, okText: 'Xóa' })) return;
      try { await api(`/customers/${c.id}`, { method: 'DELETE' }); toast('Đã xóa khách hàng', 'success'); load(); } catch (err) { toast(err.message, 'error'); }
      return;
    }
    const r = e.target.closest('tr[data-id]');
    if (r) customerDetail(r.dataset.id, load);
  };
  await load();
}

function customerForm(c, onSaved) {
  const m = modal({
    title: c ? 'Sửa khách hàng' : 'Thêm khách hàng',
    body: `<form id="cf" class="form-grid">
      <label>Họ tên *<input name="name" required value="${esc(c?.name)}"></label>
      <label>Số điện thoại<input name="phone" data-type="nullable" type="tel" inputmode="numeric" maxlength="10" pattern="0[0-9]{9}" title="10 chữ số, bắt đầu bằng 0" placeholder="0xxxxxxxxx" value="${esc(c?.phone)}"></label>
      <label>Email (nhận hóa đơn điện tử)<input name="email" type="email" data-type="nullable" value="${esc(c?.email)}"></label>
      <label>Nhóm khách<select name="group">${Object.entries(GROUP_VI).map(([k, v]) => `<option value="${k}" ${c?.group === k ? 'selected' : ''}>${v}</option>`).join('')}</select></label>
      <label class="full">Địa chỉ<input name="address" data-type="nullable" value="${esc(c?.address)}"></label>
      <label class="full">Ghi chú<input name="note" data-type="nullable" value="${esc(c?.note)}"></label>
      <p class="error full" id="cf-err"></p></form>`,
    footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="cf-save">${icon('check')} Lưu</button>`,
  });
  $('#cf-save', m.el).onclick = async () => {
    const form = $('#cf', m.el);
    if (!form.reportValidity()) return;
    try {
      const saved = await api(c ? `/customers/${c.id}` : '/customers', { method: c ? 'PUT' : 'POST', body: formValues(form) });
      toast('Đã lưu khách hàng', 'success');
      m.close(); onSaved?.(saved);
    } catch (e) { $('#cf-err', m.el).textContent = e.message; }
  };
}

async function customerDetail(id, onChange) {
  const c = await api(`/customers/${id}`);
  const mgr = isManager();
  const m = modal({
    title: `${esc(c.name)} ${groupBadge(c.group)} ${tierBadge(c.tier)}`, size: 'wide',
    body: `<div class="grid kpi mb-4">${kpi('receipt', '', 'Số hóa đơn', c.invoice_count)}${kpi('wallet', '', 'Tổng chi tiêu', money(c.total_spent), 'Đã trừ tiền hoàn trả hàng')}
        ${kpi('award', '', 'Hạng thành viên', esc(c.tier?.name || 'Chưa xếp hạng'), c.tier?.discount_percent ? `Giảm ${c.tier.discount_percent}% mỗi đơn` : '')}
        ${kpi('gift', '', 'Điểm tích lũy', num(c.points), S.payCfg?.point_value ? `≈ ${money(c.points * S.payCfg.point_value)}` : '')}</div>
      <div class="info-list"><div><span class="k">Mã khách</span>${esc(c.code)}</div><div><span class="k">Số điện thoại</span>${esc(c.phone || '-')}</div>
        <div><span class="k">Email</span>${esc(c.email || '-')}</div><div><span class="k">Địa chỉ</span>${esc(c.address || '-')}</div>
        <div><span class="k">Mua gần nhất</span>${fmtDate(c.last_purchase) || '-'}</div></div>
      <h3>Lịch sử mua hàng</h3>
      ${table(['Mã HĐ', 'Thời gian', 'Sản phẩm', ['Tổng tiền', 'right'], 'Trạng thái'], c.invoices.map((i) => [esc(i.code), `<span class="nowrap">${fmtDate(i.created_at)}</span>`, esc(i.items),
        money(i.total) + (i.refunded ? `<div class="muted small">hoàn ${money(i.refunded)}</div>` : ''), statusBadge(i.status)]), { empty: 'Chưa có hóa đơn' })}
      <h3>Lịch sử điểm tích lũy</h3>
      ${table(['Thời gian', 'Loại', 'Chứng từ', ['Thay đổi', 'right'], ['Còn lại', 'right'], 'Ghi chú'], c.point_history.map((p) => [`<span class="nowrap">${fmtDate(p.created_at)}</span>`, esc(p.type), esc(p.ref_code || ''),
        `<b class="${p.change > 0 ? 'text-success' : 'text-danger'}">${p.change > 0 ? '+' : ''}${num(p.change)}</b>`, num(p.balance_after), esc(p.note || '')]), { empty: 'Chưa có giao dịch điểm' })}`,
    footer: `${mgr ? `<button class="btn danger left" id="cd-del">${icon('trash')} Xóa</button><button class="btn" id="cd-points">${icon('gift')} Điều chỉnh điểm</button>` : ''}<button class="btn primary" id="cd-edit">${icon('edit')} Sửa</button>`,
  });
  $('#cd-edit', m.el).onclick = () => { m.close(); customerForm(c, onChange); };
  $('#cd-points', m.el)?.addEventListener('click', () => { m.close(); pointsForm(c, () => { onChange?.(); customerDetail(id, onChange); }); });
  $('#cd-del', m.el)?.addEventListener('click', async () => {
    if (!await confirmBox(`Xóa khách hàng ${c.name}?`, { danger: true, okText: 'Xóa' })) return;
    try { await api(`/customers/${c.id}`, { method: 'DELETE' }); toast('Đã xóa', 'success'); m.close(); onChange(); } catch (e) { toast(e.message, 'error'); }
  });
}

// Chủ cửa hàng cộng / trừ điểm tích lũy (tặng điểm, sửa sai sót), bắt buộc ghi lý do
function pointsForm(c, onSaved) {
  const m = modal({
    title: `${icon('gift')} Điều chỉnh điểm · ${esc(c.name)}`, size: 'narrow',
    body: `<form id="ptf" class="stack"><p class="m-0">Điểm hiện có: <b>${num(c.points)}</b></p>
      <label>Số điểm cộng (+) hoặc trừ (-) *<input name="change" type="number" required data-type="int" placeholder="VD: 50 hoặc -20"></label>
      <label>Lý do *<input name="note" required maxlength="255" placeholder="VD: Tặng điểm sinh nhật"></label><p class="error m-0" id="ptf-err"></p></form>`,
    footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="ptf-save">${icon('check')} Lưu</button>`,
  });
  $('#ptf-save', m.el).onclick = async () => {
    const form = $('#ptf', m.el);
    if (!form.reportValidity()) return;
    try {
      const r = await api(`/customers/${c.id}/points`, { method: 'POST', body: formValues(form) });
      toast(`Đã điều chỉnh, khách còn ${num(r.points)} điểm`, 'success');
      m.close(); onSaved?.();
    } catch (e) { $('#ptf-err', m.el).textContent = e.message; }
  };
}

// ============================================================ Sản phẩm
async function pageProducts(page) {
  await loadCategories();
  const f = { q: '', category_id: '', stock: '', status: '', page: 1, size: 20 };
  const mgr = isManager();
  page.innerHTML = `<div class="card">
    <form class="toolbar" id="p-filter">
      <label class="grow">Tìm kiếm<div class="input-icon">${icon('search')}<input name="q" placeholder="Tên hoặc mã sản phẩm"></div></label>
      <label>Nhóm hàng<select name="category_id">${categoryOptions('')}</select></label>
      <label>Tồn kho<select name="stock"><option value="">Tất cả</option><option value="in">Còn hàng</option><option value="low">Sắp hết</option><option value="out">Hết hàng</option></select></label>
      <label>Trạng thái<select name="status"><option value="">Tất cả</option><option value="active">Đang bán</option><option value="inactive">Ngừng bán</option></select></label>
      <button class="btn">${icon('search')} Lọc</button>
      ${mgr ? `<div class="actions"><button type="button" class="btn" id="p-labels">${icon('qr')} In tem QR</button><button type="button" class="btn primary" id="p-add">${icon('plus')} Thêm sản phẩm</button></div>` : ''}
    </form><div id="p-table">${skeletonLines()}</div></div>`;
  let items = [];
  const load = async () => {
    const data = await api('/products', { params: f });
    items = data.items;
    const headers = ['Sản phẩm', 'Nhóm hàng', ['Giá bán', 'right'], ...(mgr ? [['Giá nhập', 'right']] : []), 'Tồn kho', 'Bảo hành', 'Trạng thái', ...(mgr ? [['', 'right']] : [])];
    $('#p-table').innerHTML = table(headers, items.map((p) => [
      productCell({ ...p, category_name: null }) + (p.track_serial ? '<span class="badge blue mt-2">Quản lý IMEI / serial</span>' : ''),
      esc(p.category_name || ''), `<b>${money(p.sale_price)}</b>`,
      ...(mgr ? [money(p.cost_price)] : []), stockBadge(p),
      p.warranty_months ? `${p.warranty_months} tháng` : '<span class="muted">Không</span>',
      p.status === 'active' ? '<span class="badge dot green">Đang bán</span>' : '<span class="badge dot">Ngừng bán</span>',
      ...(mgr ? [`<div class="row-actions">
        <button class="btn ghost sm icon-only" data-edit="${p.id}" title="Sửa">${icon('edit')}</button>
        <button class="btn ghost sm icon-only" data-adj="${p.id}" title="Kiểm kê, điều chỉnh tồn kho">${icon('clipboard')}</button>
        <button class="btn ghost sm icon-only" data-card="${p.id}" title="Thẻ kho">${icon('arrows')}</button>
        ${p.track_serial ? `<button class="btn ghost sm icon-only" data-serial="${p.id}" title="Danh sách IMEI / serial">${icon('hash')}</button>` : ''}
        <button class="btn ghost sm icon-only" data-qr="${p.id}" title="In tem QR">${icon('qr')}</button>
        <button class="btn ghost sm icon-only danger" data-del="${p.id}" title="Xóa">${icon('trash')}</button></div>`] : []),
    ]), { empty: 'Không có sản phẩm' });
    $('#p-table').appendChild(pager(data.total, f.page, f.size, (p) => { f.page = p; load(); }));
  };
  const find = (id) => items.find((p) => p.id == id);
  // Form sản phẩm có thể vừa tạo nhóm hàng mới: nạp lại danh sách nhóm cho bộ lọc
  const afterSave = async () => {
    await loadCategories();
    $('#p-filter [name=category_id]').innerHTML = categoryOptions(f.category_id);
    await load();
  };
  $('#p-table').onclick = async (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    if (b.dataset.edit) productForm(find(b.dataset.edit), afterSave);
    else if (b.dataset.adj) adjustForm(find(b.dataset.adj), load);
    else if (b.dataset.card) location.hash = `#stock-card?product=${b.dataset.card}`;
    else if (b.dataset.serial) location.hash = `#serials?product=${b.dataset.serial}`;
    else if (b.dataset.qr) qrLabels([b.dataset.qr]);
    else if (b.dataset.del) {
      const p = find(b.dataset.del);
      if (!await confirmBox(`Xóa sản phẩm ${p.name}? Nếu đã có giao dịch, sản phẩm sẽ chuyển sang "Ngừng bán".`, { danger: true, okText: 'Xóa' })) return;
      try { const r = await api(`/products/${p.id}`, { method: 'DELETE' }); toast(r.message, 'success'); load(); } catch (err) { toast(err.message, 'error'); }
    }
  };
  $('#p-filter').onsubmit = (e) => { e.preventDefault(); Object.assign(f, formValues(e.target), { page: 1 }); load(); };
  $('#p-add')?.addEventListener('click', () => productForm(null, afterSave));
  $('#p-labels')?.addEventListener('click', () => qrLabels());
  await load();
}

async function qrLabels(ids) {
  const labels = await api('/products/qr-labels', { params: { ids: ids?.join(',') } });
  const m = modal({
    title: `${icon('qr')} Tem QR sản phẩm (${labels.length})`, size: 'wide',
    body: `<p class="muted mt-0">In và dán tem lên sản phẩm. Ở màn hình <b>Bán hàng</b>, bấm <b>Quét QR</b> và đưa tem vào camera để thêm sản phẩm vào giỏ.</p>
      <div class="labels print-area">${labels.map((l) => `<div class="label-card">${l.svg}<div class="n">${esc(l.name)}</div><div class="c">${esc(l.code)} · ${money(l.price)}</div></div>`).join('')}</div>`,
    footer: `<button class="btn" data-close>Đóng</button><button class="btn primary" id="lbl-print">${icon('printer')} In tem</button>`,
  });
  $('#lbl-print', m.el).onclick = () => window.print();
}

function productForm(p, onSaved) {
  let pendingFile = null;
  let removeImage = false;
  const m = modal({
    title: p ? 'Sửa sản phẩm' : 'Thêm sản phẩm', size: 'wide',
    body: `<form id="pf" class="form-grid">
      <div class="image-field full"><div id="pf-img">${thumb(p || { name: '' }, 'lg')}</div>
        <div class="actions"><span class="strong">Ảnh sản phẩm</span>
          <div class="row"><label class="btn sm">${icon('upload')} Chọn ảnh<input type="file" id="pf-file" accept="image/png,image/jpeg,image/webp,image/gif" hidden></label>
          <button type="button" class="btn sm danger" id="pf-img-del">${icon('trash')} Xóa ảnh</button></div>
          <span class="muted small">JPG, PNG, WEBP hoặc GIF, tối đa 5 MB. Ảnh được thu nhỏ về 800px.</span></div></div>
      <label>Mã sản phẩm (in trên tem QR) *<input name="code" required value="${esc(p?.code)}"></label>
      <label>Nhóm hàng<div class="input-icon has-action">${icon('tag')}<input name="category_name" autocomplete="off" placeholder="Chọn nhóm có sẵn hoặc gõ tên nhóm mới" value="${esc(p?.category_name)}">
        <button type="button" class="input-action" id="pf-cat-all" tabindex="-1" aria-label="Xem tất cả nhóm hàng">${icon('chevron')}</button></div>
        <span class="muted small" id="pf-cat-hint"></span></label>
      <label class="full">Tên sản phẩm *<input name="name" required value="${esc(p?.name)}"></label>
      <label>Giá bán (₫) *<input name="sale_price" ${MONEY_ATTRS} required data-type="money" placeholder="VD: 3.000.000" value="${fmtMoneyInput(p?.sale_price)}"></label>
      <label>Giá nhập (₫)<input name="cost_price" ${MONEY_ATTRS} data-type="money" data-empty="0" placeholder="0" value="${fmtMoneyInput(p?.cost_price ?? 0)}"></label>
      ${p ? '' : '<label>Tồn kho đầu kỳ<input name="stock" type="number" min="0" data-type="int" value="0"></label>'}
      <label>Mức tồn tối thiểu<input name="min_stock" type="number" min="0" data-type="int" value="${p?.min_stock ?? 5}"></label>
      <label>Bảo hành (tháng, 0 = không bảo hành)<input name="warranty_months" type="number" min="0" max="120" data-type="int" value="${p?.warranty_months ?? 0}"></label>
      <label>Trạng thái<select name="status"><option value="active">Đang bán</option><option value="inactive" ${p?.status === 'inactive' ? 'selected' : ''}>Ngừng bán</option></select></label>
      <label class="checkbox full"><input type="checkbox" name="track_serial" ${p?.track_serial ? 'checked' : ''}>
        Quản lý theo từng máy (IMEI / serial): nhập kho phải ghi số máy, bán phải chọn đúng máy, tra bảo hành theo IMEI</label>
      <label class="full">Mô tả (chatbot dùng để tư vấn)<textarea name="description" rows="3" data-type="nullable">${esc(p?.description)}</textarea></label>
      <p class="error full" id="pf-err"></p></form>`,
    footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="pf-save">${icon('check')} Lưu</button>`,
  });
  const catInput = $('[name=category_name]', m.el);
  const catCombo = categoryCombo(catInput, m.el, () => {
    const v = catInput.value.trim().replace(/\s+/g, ' ').toLowerCase();
    const isNew = v && !S.categories.some((c) => c.name.toLowerCase() === v);
    $('#pf-cat-hint', m.el).textContent = isNew ? 'Nhóm mới, sẽ được tạo khi lưu sản phẩm' : '';
  });
  const catAll = $('#pf-cat-all', m.el);
  catAll.onmousedown = (e) => e.preventDefault(); // giữ focus ở ô nhập để danh sách không bị đóng khi blur
  catAll.onclick = () => { if (document.activeElement === catInput) catCombo.toggle(); else catInput.focus(); };
  const preview = (url) => { $('#pf-img', m.el).innerHTML = thumb({ name: $('[name=name]', m.el).value, image_url: url }, 'lg'); };
  $('#pf-file', m.el).onchange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) { toast('Ảnh vượt quá 5 MB', 'error'); return; }
    pendingFile = file;
    removeImage = false;
    preview(URL.createObjectURL(file));
  };
  $('#pf-img-del', m.el).onclick = () => { pendingFile = null; removeImage = true; preview(null); };
  $('#pf-save', m.el).onclick = async () => {
    const form = $('#pf', m.el);
    const sale = $('[name=sale_price]', form);
    if (!(parseMoney(sale.value) > 0)) { $('#pf-err', m.el).textContent = 'Giá bán phải lớn hơn 0'; sale.focus(); return; }
    if (!form.reportValidity()) return;
    const btn = $('#pf-save', m.el);
    btn.disabled = true;
    try {
      const saved = await api(p ? `/products/${p.id}` : '/products', { method: p ? 'PUT' : 'POST', body: formValues(form) });
      if (pendingFile) {
        const fd = new FormData();
        fd.append('file', pendingFile);
        await api(`/products/${saved.id}/image`, { method: 'POST', form: fd });
      } else if (removeImage && p?.image_url) {
        await api(`/products/${saved.id}/image`, { method: 'DELETE' });
      }
      toast('Đã lưu sản phẩm', 'success');
      m.close(); onSaved();
    } catch (e) { $('#pf-err', m.el).textContent = e.message; btn.disabled = false; }
  };
}

function adjustForm(p, onSaved) {
  const m = modal({
    title: `Kiểm kê, điều chỉnh tồn kho`, size: 'narrow',
    body: `<form id="af" class="stack">${productCell(p)}<p class="m-0">Tồn kho trên hệ thống: <b>${p.stock}</b></p>
      ${p.track_serial ? note('Sản phẩm quản lý theo IMEI / serial: sau khi điều chỉnh, cập nhật cả danh sách serial (menu Serial / IMEI) cho khớp.') : ''}
      <label>Số lượng thực tế *<input name="new_stock" type="number" min="0" required data-type="int" value="${p.stock}"></label>
      <label>Lý do điều chỉnh *<input name="note" required placeholder="VD: Kiểm kê cuối tháng, hàng lỗi..."></label><p class="error" id="af-err"></p></form>`,
    footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="af-save">${icon('check')} Cập nhật</button>`,
  });
  $('#af-save', m.el).onclick = async () => {
    const form = $('#af', m.el);
    if (!form.reportValidity()) return;
    try { await api(`/products/${p.id}/adjust-stock`, { method: 'POST', body: formValues(form) }); toast('Đã điều chỉnh tồn kho', 'success'); m.close(); onSaved(); }
    catch (e) { $('#af-err', m.el).textContent = e.message; }
  };
}

// ============================================================ Nhóm hàng
async function pageCategories(page) {
  const cats = await loadCategories();
  page.innerHTML = `<div class="card w-md">
    ${cardHead('tag', `Nhóm hàng (${cats.length})`, `<button class="btn primary" id="cat-add">${icon('plus')} Thêm nhóm hàng</button>`)}
    ${table(['Tên nhóm', 'Mô tả', ['', 'right']], cats.map((c) => [`<b>${esc(c.name)}</b>`, esc(c.description || ''),
      `<div class="row-actions"><button class="btn ghost sm icon-only" data-edit="${c.id}" title="Sửa">${icon('edit')}</button><button class="btn ghost sm icon-only danger" data-del="${c.id}" title="Xóa">${icon('trash')}</button></div>`]), { empty: 'Chưa có nhóm hàng' })}</div>`;
  const form = (c) => {
    const m = modal({
      title: c ? 'Sửa nhóm hàng' : 'Thêm nhóm hàng', size: 'narrow',
      body: `<form id="catf" class="stack"><label>Tên nhóm *<input name="name" required value="${esc(c?.name)}"></label>
        <label>Mô tả<input name="description" data-type="nullable" value="${esc(c?.description)}"></label><p class="error" id="catf-err"></p></form>`,
      footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="catf-save">${icon('check')} Lưu</button>`,
    });
    $('#catf-save', m.el).onclick = async () => {
      const f = $('#catf', m.el);
      if (!f.reportValidity()) return;
      try { await api(c ? `/categories/${c.id}` : '/categories', { method: c ? 'PUT' : 'POST', body: formValues(f) }); m.close(); navigate(); }
      catch (e) { $('#catf-err', m.el).textContent = e.message; }
    };
  };
  $('#cat-add').onclick = () => form(null);
  $$('[data-edit]').forEach((b) => b.onclick = () => form(cats.find((c) => c.id == b.dataset.edit)));
  $$('[data-del]').forEach((b) => b.onclick = async () => {
    if (!await confirmBox('Xóa nhóm hàng này?', { danger: true, okText: 'Xóa' })) return;
    try { await api(`/categories/${b.dataset.del}`, { method: 'DELETE' }); navigate(); } catch (e) { toast(e.message, 'error'); }
  });
}

// ============================================================ Nhập hàng
// Chủ cửa hàng: lập phiếu nhập (cộng kho ngay), xác nhận phiếu nháp, hủy phiếu nhập.
// Thu ngân: lập phiếu nhập nháp khi hàng về (chưa cộng kho, không thấy giá vốn), chờ chủ cửa hàng xác nhận.
const IMPORT_STATUS = { draft: '<span class="badge dot yellow">Nháp, chờ xác nhận</span>', completed: '<span class="badge dot green">Đã nhập kho</span>', cancelled: '<span class="badge dot red">Đã hủy</span>' };

async function pageImports(page) {
  const owner = isManager();
  const f = { q: '', status: owner ? '' : '', date_from: '', date_to: '', page: 1, size: 20 };
  page.innerHTML = `${owner ? '' : `<div class="card mb-4">${note('Hàng về: lập phiếu nhập nháp (sản phẩm, số lượng, IMEI nếu có). Chủ cửa hàng kiểm tra, điền giá nhập và xác nhận thì hàng mới cộng vào kho.')}</div>`}
    <div class="card">
    <form class="toolbar" id="im-filter">
      <label class="grow">Tìm kiếm<div class="input-icon">${icon('search')}<input name="q" placeholder="Mã phiếu hoặc nhà cung cấp"></div></label>
      <label>Trạng thái<select name="status"><option value="">Tất cả</option><option value="draft">Nháp, chờ xác nhận</option><option value="completed">Đã nhập kho</option><option value="cancelled">Đã hủy</option></select></label>
      <label>Từ ngày<input type="date" name="date_from"></label><label>Đến ngày<input type="date" name="date_to"></label>
      <button class="btn">${icon('search')} Lọc</button>
      <div class="actions"><button type="button" class="btn primary" id="im-add">${icon('plus')} ${owner ? 'Tạo phiếu nhập' : 'Lập phiếu nhập nháp'}</button></div>
    </form><div id="im-table">${skeletonLines()}</div></div>`;
  const load = async () => {
    const data = await api('/imports', { params: f });
    if (!$('#im-table')) return; // đã chuyển sang trang khác trong lúc chờ
    $('#im-table').innerHTML = table(['Mã phiếu', 'Thời gian', 'Nhà cung cấp', 'Người lập', 'Trạng thái', ['Số mặt hàng', 'right'], ...(owner ? [['Tổng tiền', 'right']] : [])],
      data.items.map((r) => [`<b>${esc(r.code)}</b>`, fmtDate(r.created_at), esc(r.supplier || ''), esc(r.user_name), IMPORT_STATUS[r.status], r.item_count,
        ...(owner ? [`<b>${money(r.total)}</b>`] : [])]),
      { empty: owner ? 'Chưa có phiếu nhập' : 'Bạn chưa lập phiếu nhập nháp nào', rowAttrs: (k) => `class="clickable" data-id="${data.items[k].id}"` });
    $('#im-table').appendChild(pager(data.total, f.page, f.size, (p) => { f.page = p; load(); }));
  };
  const reload = () => { load(); refreshCounts(); };
  $('#im-filter').onsubmit = (e) => { e.preventDefault(); Object.assign(f, formValues(e.target), { page: 1 }); load(); };
  $('#im-add').onclick = () => importForm({ mode: owner ? 'create' : 'draft', onSaved: reload });
  $('#im-table').onclick = (e) => {
    const row = e.target.closest('tr[data-id]');
    if (row) importDetail(row.dataset.id, reload);
  };
  await load();
}

async function importDetail(id, onChange) {
  const r = await api(`/imports/${id}`);
  const owner = isManager();
  const showCost = r.total != null;
  let footer = '';
  if (r.status === 'draft') {
    footer = `<button class="btn danger left" id="ir-cancel">${icon('x')} Hủy phiếu nháp</button>`
      + (owner ? `<button class="btn primary" id="ir-confirm">${icon('check')} Kiểm tra, xác nhận nhập kho</button>`
        : `<button class="btn primary" id="ir-edit">${icon('edit')} Sửa phiếu nháp</button>`);
  } else if (r.status === 'completed' && owner) {
    footer = `<button class="btn danger left" id="ir-cancel">${icon('x')} Hủy phiếu nhập</button><button class="btn" data-close>Đóng</button>`;
  }
  const m = modal({
    title: `${icon('truck')} Phiếu nhập ${esc(r.code)} ${IMPORT_STATUS[r.status]}`, size: 'wide',
    body: `<div class="info-list"><div><span class="k">Lập lúc</span>${fmtDate(r.created_at)}</div><div><span class="k">Nhà cung cấp</span>${esc(r.supplier || '-')}</div>
        <div><span class="k">Người lập</span>${esc(r.user_name)}</div>
        ${r.confirmed_at ? `<div><span class="k">Nhập kho</span>${fmtDate(r.confirmed_at)} · ${esc(r.confirmed_by || '')}</div>` : ''}
        ${r.note ? `<div><span class="k">Ghi chú</span>${esc(r.note)}</div>` : ''}</div>
      ${r.status === 'cancelled' ? note(`Hủy lúc ${fmtDate(r.cancelled_at)} - Lý do: ${r.cancel_reason}`) : ''}
      ${table(['Sản phẩm', ['SL', 'right'], ...(showCost ? [['Giá nhập', 'right'], ['Thành tiền', 'right']] : [])],
        r.items.map((i) => [productCell(i) + serialChips(i.serials), i.quantity, ...(showCost ? [i.unit_cost ? money(i.unit_cost) : '<span class="muted">Chưa có</span>', money(i.line_total)] : [])]))}
      ${showCost ? `<p class="right text-lg"><b>Tổng: ${money(r.total)}</b></p>` : ''}`,
    footer,
  });
  $('#ir-confirm', m.el)?.addEventListener('click', () => { m.close(); importForm({ mode: 'confirm', receipt: r, onSaved: onChange }); });
  $('#ir-edit', m.el)?.addEventListener('click', () => { m.close(); importForm({ mode: 'draft', receipt: r, onSaved: onChange }); });
  $('#ir-cancel', m.el)?.addEventListener('click', async () => {
    const msg = r.status === 'completed' ? `Hủy phiếu nhập ${r.code}? Tồn kho sẽ bị trừ lại đúng số đã nhập (hàng phải còn trong kho).` : `Hủy phiếu nháp ${r.code}?`;
    const reason = await confirmBox(msg, { input: true, okText: 'Hủy phiếu', danger: true });
    if (!reason) return;
    try { await api(`/imports/${r.id}/cancel`, { method: 'POST', body: { reason } }); toast('Đã hủy phiếu nhập', 'success'); m.close(); onChange?.(); }
    catch (e) { toast(e.message, 'error'); }
  });
}

// Ô chọn sản phẩm: gõ để tìm (không phân biệt dấu) theo tên / mã; không có thì cho "Thêm sản phẩm mới".
// Danh sách gợi ý đặt position: fixed trong `host` (nền modal) để không bị bảng cắt mất.
const plain = (t) => String(t ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase().trim();

function productCombo(input, products, host, onPick, { allowCreate = true } = {}) {
  const list = document.createElement('div');
  list.className = 'combo-list hidden';
  list.setAttribute('role', 'listbox');
  host.appendChild(list);
  let items = [];
  let active = 0;
  const open = () => !list.classList.contains('hidden');
  const close = () => list.classList.add('hidden');
  const place = () => {
    const r = input.getBoundingClientRect();
    Object.assign(list.style, { left: `${r.left}px`, top: `${r.bottom + 4}px`, width: `${Math.max(r.width, 340)}px` });
  };
  const highlight = () => $$('.combo-item', list).forEach((el, i) => {
    el.classList.toggle('active', i === active);
    if (i === active) el.scrollIntoView({ block: 'nearest' });
  });
  const render = () => {
    const text = input.value.trim();
    const words = plain(text).split(/\s+/).filter(Boolean);
    const found = products.filter((p) => { const h = plain(`${p.code} ${p.name}`); return words.every((w) => h.includes(w)); }).slice(0, 8);
    const exists = products.some((p) => plain(p.name) === plain(text) || plain(p.code) === plain(text));
    items = found.map((product) => ({ product }));
    if (allowCreate && text && !exists) items.push({ create: text.replace(/\s+/g, ' ') });
    active = 0;
    list.innerHTML = items.length ? items.map((it, i) => (it.product
      ? `<div class="combo-item" data-i="${i}" role="option">${thumb(it.product, 'sm')}<span class="grow"><span class="t">${esc(it.product.name)}</span>
          <span class="s">${esc(it.product.code)} · tồn ${it.product.stock} · giá bán ${money(it.product.sale_price)}</span></span></div>`
      : `<div class="combo-item create" data-i="${i}" role="option"><span class="ico">${icon('plus')}</span><span class="grow">
          <span class="t">Thêm sản phẩm mới "${esc(it.create)}"</span><span class="s">Sản phẩm được tạo khi lưu phiếu nhập</span></span></div>`)).join('')
      : '<div class="combo-empty">Gõ tên hoặc mã để tìm sản phẩm, hoặc nhập tên sản phẩm mới</div>';
    place();
    list.classList.remove('hidden');
    highlight();
  };
  const choose = (i) => {
    const it = items[i];
    if (!it) return;
    close();
    onPick(it.product ? { product: it.product } : { name: it.create });
  };
  input.addEventListener('focus', render);
  input.addEventListener('input', () => { onPick(null); render(); });
  input.addEventListener('blur', () => setTimeout(close, 120));
  input.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      if (!open()) { render(); return; }
      active = Math.max(0, Math.min(items.length - 1, active + (e.key === 'ArrowDown' ? 1 : -1)));
      highlight();
    } else if (e.key === 'Enter' && open() && items.length) {
      e.preventDefault();
      choose(active);
    } else if (e.key === 'Escape' && open()) {
      e.stopPropagation();
      close();
    }
  });
  list.addEventListener('mousedown', (e) => {
    const el = e.target.closest('[data-i]');
    if (el) { e.preventDefault(); choose(+el.dataset.i); }
  });
  host.addEventListener('scroll', close, true);
  return { remove: () => list.remove() };
}

// Ô nhóm hàng: bấm vào là hiện đủ các nhóm để chọn tự do (không lọc theo giá trị đang có), gõ để lọc
// (không phân biệt dấu); tên chưa có thì cho "Tạo nhóm mới", server tạo nhóm khi lưu sản phẩm.
function categoryCombo(input, host, onChange) {
  const list = document.createElement('div');
  list.className = 'combo-list hidden';
  list.setAttribute('role', 'listbox');
  host.appendChild(list);
  let items = [];
  let active = 0;
  const open = () => !list.classList.contains('hidden');
  const close = () => list.classList.add('hidden');
  const highlight = () => $$('.combo-item', list).forEach((el, i) => {
    el.classList.toggle('active', i === active);
    if (i === active) el.scrollIntoView({ block: 'nearest' });
  });
  const render = (all) => {
    const text = input.value.trim().replace(/\s+/g, ' ');
    const words = all ? [] : plain(text).split(/\s+/).filter(Boolean);
    items = S.categories.filter((c) => words.every((w) => plain(c.name).includes(w))).map((c) => ({ name: c.name }));
    // So khớp có dấu như server: "Phu kien" khác "Phụ kiện" nên vẫn là nhóm mới
    if (!all && text && !S.categories.some((c) => c.name.toLowerCase() === text.toLowerCase())) items.push({ name: text, create: true });
    active = Math.max(0, items.findIndex((it) => it.name.toLowerCase() === text.toLowerCase()));
    list.innerHTML = items.length ? items.map((it, i) => (it.create
      ? `<div class="combo-item create" data-i="${i}" role="option"><span class="ico">${icon('plus')}</span><span class="grow">
          <span class="t">Tạo nhóm mới "${esc(it.name)}"</span><span class="s">Nhóm được tạo khi lưu sản phẩm</span></span></div>`
      : `<div class="combo-item" data-i="${i}" role="option"><span class="grow"><span class="t">${esc(it.name)}</span></span></div>`)).join('')
      : '<div class="combo-empty">Chưa có nhóm hàng nào, gõ tên để tạo nhóm mới</div>';
    const r = input.getBoundingClientRect();
    Object.assign(list.style, { left: `${r.left}px`, top: `${r.bottom + 4}px`, width: `${r.width}px` });
    list.classList.remove('hidden');
    highlight();
  };
  const choose = (i) => {
    const it = items[i];
    if (!it) return;
    input.value = it.name;
    close();
    onChange();
  };
  input.addEventListener('focus', () => render(true));
  input.addEventListener('input', () => { onChange(); render(false); });
  input.addEventListener('blur', () => setTimeout(close, 120));
  input.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      if (!open()) { render(true); return; }
      active = Math.max(0, Math.min(items.length - 1, active + (e.key === 'ArrowDown' ? 1 : -1)));
      highlight();
    } else if (e.key === 'Enter' && open() && items.length) {
      e.preventDefault();
      choose(active);
    } else if (e.key === 'Escape' && open()) {
      e.stopPropagation();
      close();
    }
  });
  list.addEventListener('mousedown', (e) => {
    const el = e.target.closest('[data-i]');
    if (el) { e.preventDefault(); choose(+el.dataset.i); }
  });
  host.addEventListener('scroll', close, true);
  return { toggle: () => (open() ? close() : render(true)) };
}

// Danh sách IMEI / serial gõ hoặc quét vào ô nhiều dòng: tách theo dòng, dấu phẩy, khoảng trắng
const parseSerials = (text) => [...new Set(String(text || '').split(/[\s,;]+/).map((s) => s.trim().toUpperCase()).filter(Boolean))];

// mode: create = chủ cửa hàng lập phiếu (cộng kho ngay) | confirm = chủ cửa hàng duyệt phiếu nháp `receipt`
//       | draft = thu ngân lập / sửa phiếu nháp (chỉ sản phẩm có sẵn, giá nhập không bắt buộc)
async function importForm({ mode = 'create', receipt = null, onSaved } = {}) {
  const owner = mode !== 'draft';
  const [{ items: products }, suppliers] = await Promise.all([api('/products', { params: { size: 200 } }), api('/suppliers').catch(() => []), loadCategories()]);
  const title = { create: 'Tạo phiếu nhập hàng', confirm: `Xác nhận nhập kho phiếu ${receipt?.code}`, draft: receipt ? `Sửa phiếu nhập nháp ${receipt.code}` : 'Lập phiếu nhập nháp' }[mode];
  const m = modal({
    title: `${icon('truck')} ${esc(title)}`, size: 'wide',
    body: `<div class="form-grid mb-4"><label>Nhà cung cấp<input id="im-sup" list="im-sup-list" placeholder="Chọn hoặc gõ tên nhà cung cấp" value="${esc(receipt?.supplier || '')}">
        <datalist id="im-sup-list">${suppliers.map((s) => `<option value="${esc(s.name)}"></option>`).join('')}</datalist></label>
      <label>Ghi chú<input id="im-note" placeholder="Không bắt buộc" value="${esc(receipt?.note || '')}"></label></div>
      <p class="muted small mt-0 mb-3">${owner
        ? 'Gõ để tìm sản phẩm có sẵn. Hàng chưa có trong danh mục: gõ tên rồi chọn <b>Thêm sản phẩm mới</b>, nhập nhóm hàng và giá bán ngay trong dòng. Sản phẩm quản lý theo IMEI / serial: quét hoặc gõ đủ số máy, mỗi dòng một số.'
        : 'Chọn sản phẩm có sẵn, nhập số lượng thực nhận. Giá nhập theo phiếu giao hàng (nếu có) để chủ cửa hàng đối chiếu. Sản phẩm quản lý theo IMEI / serial: quét số máy, mỗi dòng một số.'}</p>
      ${mode === 'confirm' ? note('Kiểm tra số lượng, giá nhập và IMEI rồi bấm xác nhận: hàng được cộng vào kho từ lúc này.') : ''}
      <div class="table-wrap"><table class="import-table"><thead><tr><th>Sản phẩm</th><th>Số lượng</th><th>${owner ? 'Giá nhập' : 'Giá theo phiếu giao'}</th><th class="right">Thành tiền</th><th></th></tr></thead><tbody id="im-rows"></tbody></table></div>
      <button class="btn sm mt-3" id="im-row">${icon('plus')} Thêm dòng</button>
      <p class="right text-lg"><b>Tổng: <span id="im-total">0 ₫</span></b></p><p class="error" id="im-err"></p>`,
    footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="im-save">${icon('check')} ${mode === 'draft' ? 'Lưu phiếu nháp' : mode === 'confirm' ? 'Xác nhận nhập kho' : 'Lưu phiếu nhập'}</button>`,
  });
  const rows = $('#im-rows', m.el);
  const serialCount = (tr) => {
    const el = $('[data-sn-count]', tr);
    if (!el) return;
    const n = parseSerials($('[name=sn]', tr).value).length;
    const q = +$('[name=q]', tr).value || 0;
    el.textContent = `${n} / ${q} số máy`;
    el.classList.toggle('error', owner && n !== q);
  };
  const recalc = () => {
    let total = 0;
    $$('tr', rows).forEach((tr) => {
      const line = (+$('[name=q]', tr).value || 0) * (parseMoney($('[name=c]', tr).value) || 0);
      total += line;
      $('.line', tr).textContent = money(line);
      serialCount(tr);
    });
    $('#im-total', m.el).textContent = money(total);
  };
  const addRow = (pre = null) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td><div class="input-icon">${icon('search')}<input name="p" placeholder="${owner ? 'Gõ tên / mã sản phẩm hoặc tên hàng mới' : 'Gõ tên / mã sản phẩm'}" autocomplete="off"></div>
        <div class="im-info"></div>
        <div class="im-new hidden"><select name="cat" title="Nhóm hàng">${categoryOptions('', 'Chưa phân nhóm')}</select>
          <input name="sale" ${MONEY_ATTRS} placeholder="Giá bán (₫)" title="Giá bán"></div>
        <div class="im-serial hidden"><textarea name="sn" rows="2" placeholder="IMEI / serial, mỗi dòng một số (quét bằng máy quét mã vạch)"></textarea>
          <span class="muted small" data-sn-count></span></div></td>
      <td><input name="q" type="number" min="1" value="1" class="w-full"></td>
      <td><input name="c" ${MONEY_ATTRS} placeholder="${owner ? '0' : 'Không bắt buộc'}" class="w-full"></td>
      <td class="right line">0 ₫</td><td><button class="btn ghost sm icon-only danger" data-rm title="Xóa dòng">${icon('x')}</button></td>`;
    rows.appendChild(tr);
    const input = $('[name=p]', tr);
    tr.pick = null;
    const onPick = (pick) => {
      tr.pick = pick;
      const info = $('.im-info', tr);
      $('.im-new', tr).classList.toggle('hidden', !pick?.name);
      $('.im-serial', tr).classList.toggle('hidden', !pick?.product?.track_serial);
      if (pick?.product) {
        const pr = pick.product;
        input.value = `${pr.code} - ${pr.name}`;
        info.innerHTML = `<span class="badge">${esc(pr.code)}</span><span class="muted">Tồn hiện tại ${pr.stock}${owner ? ` · giá bán ${money(pr.sale_price)}` : ''}</span>`
          + (pr.track_serial ? ' <span class="badge blue">IMEI / serial</span>' : '');
        if (owner && pr.cost_price != null && !$('[name=c]', tr).value) $('[name=c]', tr).value = fmtMoneyInput(pr.cost_price);
        $(pr.track_serial ? '[name=sn]' : '[name=q]', tr).focus();
      } else if (pick?.name) {
        input.value = pick.name;
        info.innerHTML = '<span class="badge blue">Sản phẩm mới</span><span class="muted">Mã tự sinh khi lưu. Chọn nhóm hàng và nhập giá bán:</span>';
        $('[name=c]', tr).value = '';
        $('[name=sale]', tr).focus();
      } else {
        info.innerHTML = '';
      }
      recalc();
    };
    tr.combo = productCombo(input, products, m.el, onPick, { allowCreate: owner });
    if (pre) {
      const pr = products.find((p) => p.id === pre.product_id);
      if (pr) onPick({ product: pr });
      $('[name=q]', tr).value = pre.quantity;
      $('[name=c]', tr).value = pre.unit_cost ? fmtMoneyInput(pre.unit_cost) : '';
      $('[name=sn]', tr).value = (pre.serials || []).join('\n');
      recalc();
    } else input.focus();
  };
  rows.oninput = recalc;
  rows.onclick = (e) => {
    const b = e.target.closest('[data-rm]');
    if (!b) return;
    const tr = b.closest('tr');
    tr.combo.remove();
    tr.remove();
    recalc();
  };
  $('#im-row', m.el).onclick = () => addRow();
  if (receipt?.items?.length) receipt.items.forEach((it) => addRow(it)); else addRow();
  $('#im-save', m.el).onclick = async () => {
    const err = $('#im-err', m.el);
    err.textContent = '';
    const items = [];
    for (const [i, tr] of $$('tr', rows).entries()) {
      const n = i + 1;
      const q = +$('[name=q]', tr).value;
      const cost = parseMoney($('[name=c]', tr).value) || 0;
      if (!tr.pick) { err.textContent = `Dòng ${n}: chọn sản phẩm có sẵn${owner ? ' hoặc chọn "Thêm sản phẩm mới"' : ''}`; $('[name=p]', tr).focus(); return; }
      if (!(q > 0) || (owner && !(cost > 0))) {
        err.textContent = owner ? `Dòng ${n}: số lượng và giá nhập phải lớn hơn 0` : `Dòng ${n}: số lượng phải lớn hơn 0`;
        $(q > 0 ? '[name=c]' : '[name=q]', tr).focus(); return;
      }
      const item = { quantity: q, unit_cost: owner ? cost : (cost || null) };
      if (tr.pick.product) {
        item.product_id = tr.pick.product.id;
        if (tr.pick.product.track_serial) {
          const sn = parseSerials($('[name=sn]', tr).value);
          if ((owner && sn.length !== q) || sn.length > q) {
            err.textContent = `Dòng ${n}: "${tr.pick.product.name}" cần ${owner ? 'đủ' : 'tối đa'} ${q} IMEI / serial (đang có ${sn.length})`;
            $('[name=sn]', tr).focus(); return;
          }
          item.serials = sn;
        }
      } else {
        const sale = parseMoney($('[name=sale]', tr).value) || 0;
        if (!(sale > 0)) { err.textContent = `Dòng ${n}: giá bán của sản phẩm mới "${tr.pick.name}" phải lớn hơn 0`; $('[name=sale]', tr).focus(); return; }
        item.new_product = { name: tr.pick.name, sale_price: sale, category_id: +$('[name=cat]', tr).value || null };
      }
      items.push(item);
    }
    if (!items.length) { err.textContent = 'Cần ít nhất 1 dòng'; return; }
    const body = { supplier: $('#im-sup', m.el).value.trim() || null, note: $('#im-note', m.el).value.trim() || null, items };
    const btn = $('#im-save', m.el);
    btn.disabled = true;
    try {
      let r;
      if (mode === 'create') r = await api('/imports', { method: 'POST', body });
      else if (mode === 'confirm') r = await api(`/imports/${receipt.id}/confirm`, { method: 'POST', body });
      else r = await api(receipt ? `/imports/${receipt.id}` : '/imports/drafts', { method: receipt ? 'PUT' : 'POST', body });
      const created = new Set(items.filter((it) => it.new_product).map((it) => plain(it.new_product.name))).size;
      toast(mode === 'draft' ? `Đã lưu phiếu nháp ${r.code}, chờ chủ cửa hàng xác nhận`
        : `Đã nhập kho phiếu ${r.code}${created ? `, thêm ${created} sản phẩm mới` : ''}`, 'success');
      m.close(); onSaved?.();
    } catch (e) { err.textContent = e.message; btn.disabled = false; }
  };
}

// ============================================================ Nhập - xuất - tồn
async function pageStock(page) {
  const f = { type: '', page: 1, size: 50 };
  page.innerHTML = `<div class="card"><form class="toolbar" id="st-filter">
      <label>Loại giao dịch<select name="type"><option value="">Tất cả</option>${Object.entries(MOVE_VI).map(([k, v]) => `<option value="${k}">${v}</option>`).join('')}</select></label>
      <button class="btn">${icon('search')} Lọc</button></form><div id="st-table">${skeletonLines()}</div></div>`;
  const load = async () => {
    const data = await api('/stock-movements', { params: f });
    $('#st-table').innerHTML = table(['Thời gian', 'Sản phẩm', 'Loại', 'Chứng từ', ['Thay đổi', 'right'], ['Tồn sau', 'right'], 'Ghi chú'],
      data.items.map((m) => [`<span class="nowrap">${fmtDate(m.created_at)}</span>`, `${esc(m.product_code)} · ${esc(m.product_name)}`, MOVE_VI[m.type] || m.type, esc(m.ref_code || ''),
        `<b class="${m.change > 0 ? 'text-success' : 'text-danger'}">${m.change > 0 ? '+' : ''}${m.change}</b>`, m.stock_after, esc(m.note || '')]),
      { empty: 'Chưa có giao dịch kho' });
    $('#st-table').appendChild(pager(data.total, f.page, f.size, (p) => { f.page = p; load(); }));
  };
  $('#st-filter').onsubmit = (e) => { e.preventDefault(); Object.assign(f, formValues(e.target), { page: 1 }); load(); };
  await load();
}

// ============================================================ Báo cáo
function rangePicker(id, from, to) {
  const d = new Date();
  const monthStart = isoDate(new Date(d.getFullYear(), d.getMonth(), 1));
  const lastStart = isoDate(new Date(d.getFullYear(), d.getMonth() - 1, 1));
  const lastEnd = isoDate(new Date(d.getFullYear(), d.getMonth(), 0));
  return `<form class="toolbar mb-0" id="${id}">
    <label>Từ ngày<input type="date" name="date_from" value="${from}"></label>
    <label>Đến ngày<input type="date" name="date_to" value="${to}"></label>
    <div class="btn-group">
      <button type="button" class="btn" data-range="${daysAgo(6)}|${today()}">7 ngày</button>
      <button type="button" class="btn" data-range="${daysAgo(29)}|${today()}">30 ngày</button>
      <button type="button" class="btn" data-range="${monthStart}|${today()}">Tháng này</button>
      <button type="button" class="btn" data-range="${lastStart}|${lastEnd}">Tháng trước</button></div>
    <button class="btn primary">${icon('search')} Xem</button></form>`;
}
function bindRange(form, onSubmit) {
  form.onsubmit = (e) => { e.preventDefault(); onSubmit(formValues(form)); };
  $$('[data-range]', form).forEach((b) => b.onclick = () => {
    [form.date_from.value, form.date_to.value] = b.dataset.range.split('|');
    form.requestSubmit();
  });
}

async function pageReports(page) {
  const year = new Date().getFullYear();
  page.innerHTML = `<div class="card"><div class="toolbar m-0">${rangePicker('r-range', daysAgo(29), today())}<div class="actions">${exportButtons()}</div></div></div>
    <div id="r-body" class="stack mt"><div class="card">${skeletonLines(6)}</div></div>
    <div class="card mt">${cardHead('calendar', 'Doanh thu theo tháng', `<select id="r-year">${[year, year - 1, year - 2].map((y) => `<option>${y}</option>`).join('')}</select>`)}
      <div class="chart-box"><canvas id="c-month"></canvas></div></div>`;
  let range = { date_from: daysAgo(29), date_to: today() };
  const load = async (r) => {
    range = r;
    const d = await api('/reports/revenue', { params: r });
    S.charts.filter((c) => c.canvas?.id !== 'c-month').forEach((c) => c.destroy());
    S.charts = S.charts.filter((c) => c.canvas?.id === 'c-month');
    const s = d.summary;
    $('#r-body').innerHTML = `<div class="grid kpi">${kpi('wallet', '', 'Doanh thu thuần', money(s.revenue), `${s.invoice_count} hóa đơn${s.refunds ? ` · bán ${money(s.gross_sales)}` : ''}`, true)}${kpi('undo', s.refunds ? 'yellow' : '', 'Hoàn trả hàng', money(s.refunds), `${s.return_count} phiếu đổi trả · giảm giá ${money(s.discount)}`)}
      ${kpi('package', '', 'Giá vốn', money(s.cost))}${kpi('up', '', 'Lãi gộp', money(s.gross_profit), s.revenue ? `Biên lợi nhuận ${(s.gross_profit / s.revenue * 100).toFixed(1)}%` : '')}</div>
      <div class="grid two"><div class="card">${cardHead('chart', 'Doanh thu theo ngày')}<div class="chart-box"><canvas id="c-day"></canvas></div></div>
      <div class="card">${cardHead('tag', 'Doanh thu theo nhóm hàng')}<div class="chart-box"><canvas id="c-cat"></canvas></div></div></div>
      <div class="grid two"><div class="card">${cardHead('up', 'Sản phẩm bán chạy')}${table(['Sản phẩm', ['SL', 'right'], ['Doanh thu', 'right']], d.top_products.map((p) => [productCell(p), num(p.quantity), money(p.revenue)]))}</div>
      <div class="card">${cardHead('down', 'Sản phẩm bán chậm (còn tồn)')}${table(['Sản phẩm', ['SL bán', 'right'], ['Tồn', 'right']], d.slow_products.map((p) => [productCell(p), num(p.quantity), num(p.stock)]))}</div></div>`;
    chart($('#c-day'), (t) => seriesChart('bar', d.by_day.map((x) => x.date.slice(8) + '/' + x.date.slice(5, 7)), d.by_day.map((x) => x.revenue), t));
    chart($('#c-cat'), (t) => categoryChart(d.by_category, t));
  };
  const loadMonth = async () => {
    const months = await api('/reports/monthly', { params: { year: $('#r-year').value } });
    S.charts.filter((c) => c.canvas?.id === 'c-month').forEach((c) => c.destroy());
    S.charts = S.charts.filter((c) => c.canvas?.id !== 'c-month');
    chart($('#c-month'), (t) => seriesChart('bar', months.map((m) => 'Tháng ' + +m.month.slice(5)), months.map((m) => m.revenue), t));
  };
  await loadCategories().catch(() => []);
  bindRange($('#r-range'), load);
  $$('[data-exp]').forEach((b) => b.onclick = () => download('/reports/export/revenue', { ...range, format: b.dataset.exp }));
  $('#r-year').onchange = loadMonth;
  await Promise.all([load(range), loadMonth()]);
}

// ============================================================ AI: khung chat dùng chung (trợ lý đa năng, chatbot tư vấn, hỏi đáp dữ liệu)
function aiMeta(res) {
  const src = res.source === 'ai' ? '<span class="badge dot cyan">Gemini</span>' : '<span class="badge dot yellow">Dự phòng</span>';
  return `<div class="ai-meta">${src}${res.version ? `<span class="badge">Prompt ${res.version}</span>` : ''}${res.latency_ms ? `<span class="muted">${res.latency_ms} ms</span>` : ''}${res.model ? `<span class="muted">${esc(res.model)}</span>` : ''}</div>
    ${res.warning ? note(res.warning) : ''}`;
}

const CHAT_CFG = {
  assistant: {
    endpoint: '/ai/assistant', assistant: 'Trợ lý SalesAI',
    greeting: 'Hôm nay mình giúp gì được cho bạn?',
    intro: 'Hỏi bất cứ điều gì: sản phẩm, giá, tồn kho, hóa đơn, khách hàng, doanh thu, cách dùng phần mềm, hay nhờ viết tin nhắn chăm sóc khách, ý tưởng khuyến mãi... Trợ lý tự tra dữ liệu thật của cửa hàng trong phạm vi quyền của bạn.',
    placeholder: 'Hỏi bất cứ điều gì, VD: tuần này bán được bao nhiêu? sạc nào dưới 200k còn hàng?',
    suggestions: () => isManager() ? [
      { icon: 'chart', t: 'So sánh doanh thu', s: 'Tháng này và tháng trước', q: 'So sánh doanh thu, lãi gộp tháng này với tháng trước' },
      { icon: 'truck', t: 'Cần nhập hàng gì?', s: 'Sắp hết và đang bán chạy', q: 'Sản phẩm nào sắp hết mà lại đang bán chạy, cần nhập thêm bao nhiêu?' },
      { icon: 'users', t: 'Khách hàng thân thiết', s: 'Top chi tiêu 3 tháng', q: 'Top 5 khách hàng chi tiêu nhiều nhất 3 tháng qua là ai?' },
      { icon: 'calendar', t: 'Giờ cao điểm', s: 'Khung giờ, thứ bán đông', q: 'Khung giờ nào và thứ mấy trong tuần bán được nhiều nhất?' },
    ] : [
      { icon: 'package', t: 'Tìm sản phẩm', s: 'Theo nhu cầu, ngân sách', q: 'Có tai nghe bluetooth nào dưới 500k còn hàng không?' },
      { icon: 'receipt', t: 'Hóa đơn của tôi', s: 'Hôm nay bán được gì', q: 'Hôm nay tôi đã lập bao nhiêu hóa đơn, tổng tiền bao nhiêu?' },
      { icon: 'help', t: 'Cách dùng phần mềm', s: 'Thanh toán bằng QR', q: 'Hướng dẫn thanh toán bằng quét mã QR' },
      { icon: 'message', t: 'Viết tin nhắn', s: 'Chăm sóc khách hàng', q: 'Viết giúp tin nhắn Zalo ngắn cảm ơn khách vừa mua tai nghe' },
    ],
    hint: 'AI có thể nhầm, hãy kiểm tra lại số liệu quan trọng trên các trang quản lý.',
    body: (text) => ({ message: text }),
  },
  advisor: {
    endpoint: '/ai/advisor', assistant: 'Trợ lý tư vấn', versionSelect: true,
    greeting: 'Khách hàng đang cần gì?',
    intro: 'Mô tả nhu cầu và ngân sách của khách. Trợ lý chỉ gợi ý sản phẩm còn hàng trong kho, kèm giá và số lượng tồn.',
    placeholder: 'Nhập nhu cầu của khách, VD: tai nghe dưới 500k, pin lâu...',
    suggestions: [
      { icon: 'message', t: 'Tai nghe dưới 500k', s: 'Pin lâu, còn hàng', q: 'Khách cần tai nghe dưới 500000 đồng, pin lâu, còn hàng' },
      { icon: 'sparkles', t: 'Loa đi du lịch', s: 'Chống nước, nhỏ gọn', q: 'Tư vấn loa bluetooth chống nước để đi du lịch' },
      { icon: 'package', t: 'Pin dự phòng sạc laptop', s: 'Công suất cao', q: 'Có pin dự phòng nào sạc được laptop không?' },
      { icon: 'tag', t: 'Quà tặng sinh viên', s: 'Ngân sách khoảng 300k', q: 'Gợi ý quà tặng cho sinh viên tầm 300k' },
    ],
    hint: 'AI có thể nhầm, hãy kiểm tra lại giá và tồn kho trước khi báo khách.',
    body: (text) => ({ message: text }),
  },
  ask: {
    endpoint: '/ai/ask', assistant: 'Trợ lý dữ liệu',
    greeting: 'Bạn muốn biết gì về tình hình kinh doanh?',
    intro: 'Hỏi bằng tiếng Việt tự nhiên. AI trả lời dựa trên số liệu tổng hợp của hệ thống, không truy cập trực tiếp CSDL.',
    placeholder: 'Hỏi về doanh thu, sản phẩm bán chạy, tồn kho...',
    suggestions: [
      { icon: 'down', t: 'Mặt hàng bán chậm', s: 'Tháng này', q: 'Tháng này mặt hàng nào bán chậm?' },
      { icon: 'wallet', t: 'Doanh thu hôm nay', s: 'So với mọi ngày', q: 'Doanh thu hôm nay thế nào?' },
      { icon: 'up', t: 'Top bán chạy', s: 'Tháng trước', q: 'Top 5 sản phẩm bán chạy tháng trước?' },
      { icon: 'truck', t: 'Cần nhập thêm hàng', s: 'Sản phẩm sắp hết', q: 'Sản phẩm nào cần nhập thêm?' },
    ],
    hint: 'AI có thể nhầm, hãy đối chiếu với trang Báo cáo doanh thu khi cần số liệu chính xác.',
    body: (text) => ({ question: text }),
  },
};

function historyGroup(dateStr) {
  const start = new Date(); start.setHours(0, 0, 0, 0);
  const d = new Date(dateStr); d.setHours(0, 0, 0, 0);
  const days = Math.round((start - d) / 86400000);
  if (days <= 0) return 'Hôm nay';
  if (days === 1) return 'Hôm qua';
  if (days < 7) return '7 ngày qua';
  if (days < 30) return '30 ngày qua';
  return 'Cũ hơn';
}

const aiProductCard = (s) => `<div class="product-card"><div class="img">${thumb(s)}</div><div class="b">
  <div class="strong">${esc(s.name)}</div><div class="muted small">${esc(s.code)}${s.category ? ' · ' + esc(s.category) : ''}</div>
  <div class="tile-foot"><span class="price">${money(s.price)}</span><span class="badge green">Còn ${s.stock}</span></div>
  ${s.reason ? `<div class="reason">${esc(s.reason)}</div>` : ''}
  <button class="btn sm block" data-cart="${esc(s.code)}">${icon('cart')} Thêm vào giỏ</button></div></div>`;

function aiTurnHTML(m, kind, { hideBody = false } = {}) {
  const cfg = CHAT_CFG[kind];
  const meta = m.meta || {};
  const src = meta.source === 'ai' ? '<span class="badge dot cyan">Gemini</span>' : meta.source ? '<span class="badge dot yellow">Dự phòng</span>' : '';
  let extra = '';
  if (meta.tools?.length) extra += `<div class="turn-tools">${icon('search')}Đã tra cứu: ${meta.tools.map((t) => `<span>${esc(t.label)}</span>`).join('')}</div>`;
  if (meta.suggestions?.length) extra += `<div class="product-cards">${meta.suggestions.map(aiProductCard).join('')}</div>`;
  if (meta.period) extra += `<div class="turn-period">${icon('calendar')}Kỳ dữ liệu: ${esc(meta.period_label)} (${esc(meta.period.from)} → ${esc(meta.period.to)})</div>`;
  if (meta.warning) extra += note(meta.warning);
  const time = m.created_at ? new Date(m.created_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) : '';
  return `<div class="turn-ai ${m.error ? 'error' : ''}"><div class="ai-avatar">${icon('sparkles')}</div><div class="body">
    <div class="who">${cfg.assistant} ${src}${meta.version ? `<span class="badge">Prompt ${meta.version}</span>` : ''}</div>
    <div class="content markdown">${hideBody ? '' : renderMarkdown(m.content)}</div>
    <div class="extra ${hideBody ? 'hidden-soft' : ''}">${extra}
      ${m.error ? '' : `<div class="turn-actions"><button class="tool" data-copy="${esc(m.content)}">${icon('copy')} Sao chép</button>
        ${time ? `<span class="sep">·</span>${time}` : ''}${meta.latency_ms ? `<span class="sep">·</span>${meta.latency_ms} ms` : ''}${meta.model ? `<span class="sep">·</span>${esc(meta.model)}` : ''}</div>`}</div>
  </div></div>`;
}

const userTurnHTML = (text) => `<div class="turn-user"><div class="bubble">${esc(text)}</div><div class="avatar">${esc(initialsOf(S.user?.full_name))}</div></div>`;
const aiTypingHTML = (kind) => `<div class="turn-ai is-typing"><div class="ai-avatar">${icon('sparkles')}</div><div class="body">
  <div class="who">${CHAT_CFG[kind].assistant}</div><div class="typing"><span></span><span></span><span></span></div></div></div>`;

// Gửi câu hỏi tới AI, ghi câu trả lời vào cuộc trò chuyện st (dùng chung giữa trang chat và nút AI nổi)
async function aiReply(kind, text, st, params = {}) {
  const cfg = CHAT_CFG[kind];
  const res = await api(cfg.endpoint, { method: 'POST', params, body: { ...cfg.body(text), session_id: st.sessionId } });
  const meta = { suggestions: res.suggestions, tools: res.tools, model: res.model, source: res.source, version: res.version, warning: res.warning,
    latency_ms: res.latency_ms, period: res.period, period_label: res.period_label };
  const msg = { id: res.message_id, role: 'assistant', content: res.answer, meta, created_at: new Date().toISOString() };
  Object.assign(st, { sessionId: res.session_id, title: res.session_title });
  st.messages.push(msg);
  if (st === S.chat[kind]) rememberChat(kind, res.session_id);
  return msg;
}

// Cuộc trò chuyện đang mở của từng loại chat: nhớ id trên trình duyệt để tải lại trang vẫn mở lại đúng cuộc đó
// (nội dung đã lưu trên server, chỉ cần lấy lại). Gắn với tài khoản nên người khác đăng nhập không mở được.
const chatKey = (kind) => `chat:${S.user?.id}:${kind}`;
function rememberChat(kind, sessionId) {
  try {
    if (sessionId) localStorage.setItem(chatKey(kind), String(sessionId));
    else localStorage.removeItem(chatKey(kind));
  } catch { /* trình duyệt chặn lưu trữ: chỉ nhớ trong phiên */ }
}
// Chỉ chạy một lần cho mỗi phiên đăng nhập (trang chat và nút AI nổi dùng chung một lần lấy lại),
// và chỉ khi chưa có cuộc trò chuyện nào đang mở. st.restored = đã xong.
function restoreChat(kind) {
  const st = S.chat[kind];
  st.restoring ??= (async () => {
    let id = null;
    try { id = Number(localStorage.getItem(chatKey(kind))) || null; } catch { /* trình duyệt chặn lưu trữ */ }
    if (id && !st.sessionId && !st.messages.length) {
      try {
        const s = await api(`/ai/sessions/${id}`);
        // Đã đăng xuất hoặc bắt đầu cuộc khác trong lúc chờ: bỏ qua
        if (st === S.chat[kind] && !st.sessionId && !st.messages.length) Object.assign(st, { sessionId: s.id, title: s.title, messages: s.messages });
      } catch { rememberChat(kind, null); }  // cuộc trò chuyện đã bị xóa
    }
    st.restored = true;
  })();
  return st.restoring;
}

// Hiệu ứng chữ hiện dần như AI đang viết, sau đó thay bằng Markdown đã định dạng
async function typeOutTurn(turn, text, onStep) {
  const el = turn.querySelector('.content');
  const plain = text.replace(/[*_`#>|]/g, '');
  const step = Math.max(2, Math.ceil(plain.length / 90));
  el.classList.add('caret');
  for (let i = 0; i < plain.length; i += step) {
    if (!document.body.contains(el)) return;
    el.textContent = plain.slice(0, i);
    onStep();
    await new Promise((r) => setTimeout(r, 16));
  }
  el.classList.remove('caret');
  el.innerHTML = renderMarkdown(text);
  turn.querySelector('.extra')?.classList.remove('hidden-soft');
  onStep();
}

async function chatPage(page, kind) {
  const cfg = CHAT_CFG[kind];
  const st = S.chat[kind];
  page.innerHTML = `<div class="ai-shell ${st.collapsed ? 'collapsed' : ''}" id="ai-shell">
    <aside class="ai-history">
      <div class="ai-history-top">
        <button class="btn primary block" id="ai-new">${icon('plus')} Cuộc trò chuyện mới</button>
        <div class="input-icon">${icon('search')}<input id="ai-search" placeholder="Tìm trong lịch sử tra cứu" autocomplete="off"></div>
      </div>
      <div class="ai-history-list" id="ai-list">${skeletonLines()}</div>
      <div class="ai-history-foot"><button class="btn ghost sm block" id="ai-clear">${icon('trash')} Xóa toàn bộ lịch sử</button></div>
    </aside>
    <section class="ai-main">
      <div class="ai-head">
        <button class="btn ghost sm icon-only" id="ai-toggle" title="Ẩn/hiện lịch sử tra cứu">${icon('panel')}</button>
        <div class="title" id="ai-title"></div>
        ${kind !== 'ask' ? `<a href="#pos" class="btn sm" title="Mở màn hình bán hàng">${icon('cart')} Giỏ hàng <span class="badge blue" id="ai-cart-count">0</span></a>` : ''}
      </div>
      <div class="ai-scroll" id="ai-scroll"><div class="ai-thread" id="ai-thread"></div></div>
      <div class="ai-composer-wrap">
        <form class="ai-composer" id="ai-form">
          <textarea id="ai-input" rows="1" maxlength="${kind === 'ask' ? 500 : 1000}" placeholder="${esc(cfg.placeholder)}"></textarea>
          <div class="row">
            ${cfg.versionSelect ? `<select id="ai-version" title="Phiên bản prompt"><option value="">Prompt mặc định (${S.ai?.advisor_prompt_version || 'v3'})</option><option value="v1">Prompt v1</option><option value="v2">Prompt v2</option><option value="v3">Prompt v3</option></select>` : ''}
            <button class="send-btn" id="ai-send" type="submit" title="Gửi (Enter)" disabled>${icon('arrow-up')}</button>
          </div>
        </form>
        <div class="ai-hint">Enter để gửi · Shift + Enter để xuống dòng · ${cfg.hint}</div>
      </div>
    </section></div>`;

  const shell = $('#ai-shell');
  const thread = $('#ai-thread');
  const scroller = $('#ai-scroll');
  const input = $('#ai-input');
  const sendBtn = $('#ai-send');
  const isMobile = () => matchMedia('(max-width: 860px)').matches;
  const toBottom = () => { scroller.scrollTop = scroller.scrollHeight; };
  const updateCart = () => { const el = $('#ai-cart-count'); if (el) el.textContent = [...POS.cart.values()].reduce((s, r) => s + r.qty, 0); };
  const syncSend = () => { sendBtn.disabled = st.pending || !input.value.trim(); };
  const autoGrow = () => { input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight, 200) + 'px'; };

  const renderThread = () => {
    $('#ai-title').textContent = st.title || 'Cuộc trò chuyện mới';
    if (!st.messages.length) {
      thread.innerHTML = `<div class="ai-welcome"><div class="ai-orb">${icon('sparkles')}</div>
        <div class="muted">Xin chào, ${esc(S.user.full_name)}</div><h2>${esc(cfg.greeting)}</h2><p>${esc(cfg.intro)}</p>
        <div class="suggest-grid">${(typeof cfg.suggestions === 'function' ? cfg.suggestions() : cfg.suggestions).map((x) => `<button class="suggest-item" data-q="${esc(x.q)}">${icon(x.icon)}<span><div class="s1">${esc(x.t)}</div><div class="s2">${esc(x.s)}</div></span></button>`).join('')}</div></div>`;
      return;
    }
    thread.innerHTML = st.messages.map((m) => m.role === 'user' ? userTurnHTML(m.content) : aiTurnHTML(m, kind)).join('')
      + (st.pending ? aiTypingHTML(kind) : '');  // câu hỏi gửi từ nút AI nổi vẫn đang chờ trả lời
    toBottom();
  };
  // Câu trả lời cho câu hỏi gửi từ nơi khác (nút AI nổi) về sau khi đã mở trang này: vẽ lại
  const onSettled = (e) => {
    if (!document.body.contains(thread)) { document.removeEventListener('ai:settled', onSettled); return; }
    if (e.detail.st === st && e.detail.origin !== thread) { renderThread(); syncSend(); }
  };
  document.addEventListener('ai:settled', onSettled);

  const renderList = (items) => {
    if (!items.length) {
      $('#ai-list').innerHTML = ($('#ai-search').value
        ? emptyState('search', 'Không tìm thấy cuộc trò chuyện', 'Thử từ khóa khác.', { compact: true })
        : emptyState('message', 'Chưa có lịch sử', 'Các cuộc trò chuyện sẽ được lưu ở đây.', { compact: true }));
      return;
    }
    let html = '', group = '';
    for (const s of items) {
      const g = historyGroup(s.updated_at);
      if (g !== group) { group = g; html += `<div class="ai-history-group">${g}</div>`; }
      html += `<div class="ai-history-item ${s.id === st.sessionId ? 'active' : ''}" data-sid="${s.id}" title="${esc(s.title)}">
        <span class="t">${esc(s.title)}</span>
        <span class="acts"><button class="icon-tool" data-rename="${s.id}" title="Đổi tên">${icon('edit')}</button><button class="icon-tool del" data-remove="${s.id}" title="Xóa">${icon('trash')}</button></span></div>`;
    }
    $('#ai-list').innerHTML = html;
  };
  let listCache = [];
  const loadList = async () => {
    listCache = await api('/ai/sessions', { params: { kind, q: $('#ai-search').value.trim() } });
    if (document.body.contains(shell)) renderList(listCache);
  };

  const openSession = async (id) => {
    if (st.pending) return;
    const s = await api(`/ai/sessions/${id}`);
    Object.assign(st, { sessionId: s.id, title: s.title, messages: s.messages });
    rememberChat(kind, s.id);
    renderThread();
    renderList(listCache);
    if (isMobile()) shell.classList.remove('show-history');
  };
  const newChat = () => {
    if (st.pending) return;
    Object.assign(st, { sessionId: null, title: '', messages: [] });
    rememberChat(kind, null);
    renderThread();
    renderList(listCache);
    if (isMobile()) shell.classList.remove('show-history');
    input.focus();
  };

  const send = async (text) => {
    text = text.trim();
    if (!text || st.pending) return;
    st.pending = true;
    input.value = ''; autoGrow(); syncSend();
    if (!st.messages.length) thread.innerHTML = '';
    st.messages.push({ role: 'user', content: text, created_at: new Date().toISOString() });
    thread.insertAdjacentHTML('beforeend', userTurnHTML(text) + aiTypingHTML(kind));
    toBottom();
    try {
      const msg = await aiReply(kind, text, st, cfg.versionSelect ? { version: $('#ai-version')?.value } : {});
      if (!document.body.contains(thread)) return;
      $('#ai-title').textContent = st.title;
      thread.querySelector('.is-typing')?.remove();
      thread.insertAdjacentHTML('beforeend', aiTurnHTML(msg, kind, { hideBody: true }));
      // Đã có câu trả lời: mở khóa ngay, hiệu ứng gõ chữ tự dừng nếu người dùng chuyển cuộc trò chuyện
      st.pending = false;
      syncSend();
      loadList();
      refreshAIBadge();
      await typeOutTurn(thread.lastElementChild, msg.content, toBottom);
    } catch (e) {
      thread.querySelector('.is-typing')?.remove();
      thread.insertAdjacentHTML('beforeend', aiTurnHTML({ role: 'assistant', content: e.message, error: true }, kind));
      toBottom();
    } finally {
      st.pending = false;
      syncSend();
      document.dispatchEvent(new CustomEvent('ai:settled', { detail: { st, origin: thread } }));
    }
  };

  // ---- Sự kiện
  input.oninput = () => { autoGrow(); syncSend(); };
  input.onkeydown = (e) => {
    // isComposing: không gửi khi bộ gõ tiếng Việt đang ghép chữ
    if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); send(input.value); }
  };
  $('#ai-form').onsubmit = (e) => { e.preventDefault(); send(input.value); };
  $('#ai-new').onclick = newChat;
  $('#ai-toggle').onclick = () => {
    if (isMobile()) shell.classList.toggle('show-history');
    else { st.collapsed = !st.collapsed; shell.classList.toggle('collapsed', st.collapsed); }
  };
  let searchTimer;
  $('#ai-search').oninput = () => { clearTimeout(searchTimer); searchTimer = setTimeout(loadList, 250); };
  $('#ai-list').onclick = async (e) => {
    const rename = e.target.closest('[data-rename]');
    const remove = e.target.closest('[data-remove]');
    if (rename) {
      e.stopPropagation();
      const item = listCache.find((s) => s.id == rename.dataset.rename);
      const m = modal({
        title: 'Đổi tên cuộc trò chuyện', size: 'narrow',
        body: `<input id="rename-input" class="w-full" maxlength="120" value="${esc(item.title)}">`,
        footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="rename-ok">${icon('check')} Lưu</button>`,
      });
      const inp = $('#rename-input', m.el);
      inp.focus(); inp.select();
      const save = async () => {
        if (!inp.value.trim()) return;
        const r = await api(`/ai/sessions/${item.id}`, { method: 'PATCH', body: { title: inp.value.trim() } });
        if (item.id === st.sessionId) { st.title = r.title; $('#ai-title').textContent = r.title; }
        m.close(); loadList();
      };
      $('#rename-ok', m.el).onclick = save;
      inp.onkeydown = (ev) => { if (ev.key === 'Enter') save(); };
      return;
    }
    if (remove) {
      e.stopPropagation();
      if (!await confirmBox('Xóa cuộc trò chuyện này khỏi lịch sử?', { danger: true, okText: 'Xóa' })) return;
      await api(`/ai/sessions/${remove.dataset.remove}`, { method: 'DELETE' });
      if (+remove.dataset.remove === st.sessionId) newChat();
      toast('Đã xóa cuộc trò chuyện', 'success');
      loadList();
      return;
    }
    const item = e.target.closest('[data-sid]');
    if (item) openSession(+item.dataset.sid);
  };
  $('#ai-clear').onclick = async () => {
    if (!listCache.length) return;
    if (!await confirmBox('Xóa toàn bộ lịch sử tra cứu của trang này? Không thể hoàn tác.', { danger: true, okText: 'Xóa tất cả' })) return;
    const r = await api('/ai/sessions', { method: 'DELETE', params: { kind } });
    newChat();
    toast(`Đã xóa ${r.deleted} cuộc trò chuyện`, 'success');
    loadList();
  };
  thread.onclick = async (e) => {
    const q = e.target.closest('[data-q]');
    if (q) { send(q.dataset.q); return; }
    const copy = e.target.closest('[data-copy]');
    if (copy) { navigator.clipboard.writeText(copy.dataset.copy).then(() => toast('Đã sao chép câu trả lời', 'success')); return; }
    const cart = e.target.closest('[data-cart]');
    if (cart) {
      try {
        const p = await addByCode(cart.dataset.cart);
        if (p) { toast(`Đã thêm "${p.name}" vào giỏ hàng`, 'success'); updateCart(); }
      } catch (err) { toast(err.message, 'error'); }
    }
  };

  await restoreChat(kind);  // vừa tải lại trang: mở lại cuộc trò chuyện đang dở
  if (!document.body.contains(thread)) return;
  renderThread();
  updateCart();
  await loadList();
  input.focus();
}

function pageAssistant(page) { return chatPage(page, 'assistant'); }
function pageAdvisor(page) { return chatPage(page, 'advisor'); }

// ============================================================ AI: báo cáo doanh thu
async function pageAIReport(page) {
  page.innerHTML = `<div class="card">${rangePicker('air-range', daysAgo(29), today())}
    <p class="muted small mt-3 mb-0">Hệ thống tự tính doanh thu, tồn kho, sản phẩm bán chạy/chậm, sau đó AI viết nhận xét và khuyến nghị nhập hàng. Không gửi thông tin cá nhân khách hàng cho AI.</p></div>
    <div class="card mt" id="air-out">${emptyState('sparkles', 'Chưa có báo cáo', 'Chọn kỳ báo cáo rồi bấm Xem để AI viết nhận xét và khuyến nghị nhập hàng.')}</div>`;
  const run = async (r) => {
    const out = $('#air-out');
    out.innerHTML = loading('AI đang phân tích dữ liệu...');
    try {
      const res = await api('/ai/report', { method: 'POST', body: r });
      out.innerHTML = `${cardHead('sparkles', `Báo cáo ${esc(res.period.from)} → ${esc(res.period.to)}`,
          `<button class="btn sm" id="air-copy">${icon('copy')} Sao chép</button><button class="btn sm" id="air-dl">${icon('download')} Tải .md</button>`)}
        <div class="markdown">${renderMarkdown(res.markdown)}</div>${aiMeta(res)}`;
      $('#air-copy').onclick = () => navigator.clipboard.writeText(res.markdown).then(() => toast('Đã sao chép', 'success'));
      $('#air-dl').onclick = () => {
        const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(new Blob([res.markdown], { type: 'text/markdown' })), download: `bao_cao_ai_${res.period.from}_${res.period.to}.md` });
        a.click();
      };
    } catch (e) {
      out.innerHTML = errorState(e.message);
      $('[data-retry]', out).onclick = () => run(r);
    }
  };
  bindRange($('#air-range'), run);
}

// ============================================================ AI: hỏi đáp dữ liệu
function pageAsk(page) { return chatPage(page, 'ask'); }

// ============================================================ Nút trợ lý AI nổi
// Góc dưới phải mọi trang (trừ các trang chat AI): bấm để hỏi nhanh trong khung chat nhỏ mà không rời trang đang làm.
// Dùng chung cuộc trò chuyện với trang "Trợ lý đa năng", nên bấm "Mở rộng" sẽ xem tiếp đúng cuộc trò chuyện đó.
const AI_CHAT_ROUTES = ['assistant', 'advisor', 'ask'];

const AIFab = (() => {
  const kind = 'assistant';
  const st = () => S.chat[kind];  // S.chat được tạo mới khi đăng xuất nên luôn đọc lại
  let wrap, btn, pop, thread, scroller, input, sendBtn;
  let sending = false;            // câu hỏi đang chờ là do khung này gửi

  const isOpen = () => wrap && !pop.hidden;
  const toBottom = () => { scroller.scrollTop = scroller.scrollHeight; };
  const syncSend = () => { sendBtn.disabled = st().pending || !input.value.trim(); };
  // +2: ô nhập có viền 1px; khi khung đang ẩn scrollHeight = 0, CSS min-height giữ chiều cao chuẩn
  const autoGrow = () => { input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight + 2, 120) + 'px'; };

  // Gợi ý đầu tiên là hướng dẫn dùng chính trang đang mở
  const suggestions = () => {
    const page = ROUTES[S.route];
    const help = page ? [{ t: `Cách dùng trang "${page.title}"`, q: `Hướng dẫn tôi cách dùng trang "${page.title}" trong phần mềm` }] : [];
    return [...help, ...CHAT_CFG[kind].suggestions().slice(0, 3)];
  };

  const render = () => {
    const s = st();
    thread.innerHTML = s.messages.length
      ? s.messages.map((m) => m.role === 'user' ? userTurnHTML(m.content) : aiTurnHTML(m, kind)).join('') + (s.pending ? aiTypingHTML(kind) : '')
      : `<div class="ai-pop-welcome"><div class="ai-orb sm">${icon('sparkles')}</div>
          <div class="strong">Xin chào, ${esc(S.user.full_name)}!</div>
          <p class="muted small">Mình tra được sản phẩm, tồn kho, hóa đơn, doanh thu và hướng dẫn cách dùng phần mềm. Bạn cần giúp gì?</p>
          <div class="ai-pop-chips">${suggestions().map((x) => `<button class="chip" data-q="${esc(x.q)}">${esc(x.t)}</button>`).join('')}</div></div>`;
    syncSend();
    if (s.messages.length) toBottom(); else scroller.scrollTop = 0;  // màn hình chào đọc từ trên xuống
  };

  const setOpen = (open) => {
    pop.hidden = !open;
    wrap.classList.toggle('open', open);
    $('#app-view').classList.toggle('fab-open', open);
    btn.setAttribute('aria-expanded', String(open));
    btn.innerHTML = icon(open ? 'x' : 'sparkles');
    btn.title = open ? 'Đóng trợ lý AI (kéo để di chuyển)' : 'Cần trợ giúp? Hỏi trợ lý AI (kéo để di chuyển)';
    if (!open) return;
    placePanel();
    if (st().restored) render();
    else {
      thread.innerHTML = skeletonLines();  // đang lấy lại cuộc trò chuyện trước khi tải lại trang
      restoreChat(kind).then(() => { if (isOpen() && !sending) render(); });
    }
    input.focus();
  };

  // ---- Vị trí nút: kéo thả tự do, thả ra thì dạt về mép trái / phải gần nhất (không che giữa trang).
  // Vị trí lưu trên trình duyệt này: side = mép, t = độ cao theo tỉ lệ (0 sát topbar, 1 sát đáy) để giữ đúng chỗ khi đổi cỡ cửa sổ.
  const POS_KEY = 'aiFabPos';
  const TOPBAR_GAP = 72;  // không kéo lên che topbar (cao 60px)
  let pos = { side: 'right', t: 1 };
  let drag = null;
  let justDragged = false;
  const vw = () => document.documentElement.clientWidth;  // bỏ phần thanh cuộn
  const vh = () => document.documentElement.clientHeight;
  const isMobile = () => matchMedia('(max-width: 860px)').matches;
  const clamp = (v, lo, hi) => Math.min(Math.max(v, lo), Math.max(lo, hi));
  const bounds = () => {
    const size = parseFloat(getComputedStyle(btn).width);  // đọc được cả khi nút đang ẩn
    const m = isMobile() ? 16 : 24;
    return { size, m, minY: TOPBAR_GAP, maxY: vh() - size - m };
  };

  const loadPos = () => {
    try {
      const v = JSON.parse(localStorage.getItem(POS_KEY));
      if (v && ['left', 'right'].includes(v.side) && v.t >= 0 && v.t <= 1) pos = v;
    } catch { /* chưa lưu hoặc trình duyệt chặn: dùng vị trí mặc định */ }
  };
  const savePos = () => { try { localStorage.setItem(POS_KEY, JSON.stringify(pos)); } catch { /* chế độ riêng tư: chỉ nhớ trong phiên */ } };

  const applyPos = () => {
    const { size, m, minY, maxY } = bounds();
    Object.assign(btn.style, {
      left: `${pos.side === 'left' ? m : vw() - size - m}px`,
      top: `${minY + pos.t * Math.max(0, maxY - minY)}px`,
      right: 'auto', bottom: 'auto',
    });
    $('#app-view').classList.toggle('fab-left', pos.side === 'left');
    if (isOpen()) placePanel();
  };

  // Khung chat mở về phía còn nhiều chỗ hơn (trên / dưới nút), bám cùng mép với nút
  const placePanel = () => {
    const r = btn.getBoundingClientRect();
    const gap = 12, edge = 12;
    const above = r.top - gap - edge, below = vh() - r.bottom - gap - edge;
    const up = above >= below;
    const onLeft = r.left + r.width / 2 < vw() / 2;
    const s = pop.style;
    s.height = `${Math.min(600, Math.max(up ? above : below, 240))}px`;
    s.top = up ? 'auto' : `${r.bottom + gap}px`;
    s.bottom = up ? `${vh() - r.top + gap}px` : 'auto';
    if (isMobile()) { s.left = '8px'; s.right = '8px'; }
    else if (onLeft) { s.left = `${r.left}px`; s.right = 'auto'; }
    else { s.right = `${vw() - r.right}px`; s.left = 'auto'; }
    s.transformOrigin = `${up ? 'bottom' : 'top'} ${onLeft ? 'left' : 'right'}`;
  };

  const onPointerDown = (e) => {
    if (e.button !== 0) return;
    // Chặn hành vi mặc định: khi nút nằm đè lên menu, Chrome sẽ tưởng đang kéo liên kết bên dưới rồi hủy thao tác kéo nút.
    // "click" vẫn được phát bình thường nên bấm mở / đóng khung không bị ảnh hưởng.
    e.preventDefault();
    const r = btn.getBoundingClientRect();
    drag = { id: e.pointerId, x: e.clientX, y: e.clientY, dx: e.clientX - r.left, dy: e.clientY - r.top, moved: false };
    btn.setPointerCapture(e.pointerId);
  };
  const onPointerMove = (e) => {
    if (!drag || e.pointerId !== drag.id) return;
    if (!drag.moved && Math.hypot(e.clientX - drag.x, e.clientY - drag.y) < 5) return;  // rung tay khi bấm: vẫn tính là bấm
    drag.moved = true;
    btn.classList.add('dragging');
    const { size, minY, maxY } = bounds();
    btn.style.left = `${clamp(e.clientX - drag.dx, 0, vw() - size)}px`;
    btn.style.top = `${clamp(e.clientY - drag.dy, minY, maxY)}px`;
    if (isOpen()) placePanel();
  };
  const onPointerUp = (e) => {
    if (!drag || e.pointerId !== drag.id) return;
    const { moved } = drag;
    drag = null;
    if (!moved) return;
    btn.classList.remove('dragging');
    // Trình duyệt vẫn phát "click" ngay sau khi thả: bỏ qua lần đó để không mở / đóng khung ngoài ý muốn
    justDragged = true;
    setTimeout(() => { justDragged = false; }, 0);
    const r = btn.getBoundingClientRect();
    const { minY, maxY } = bounds();
    pos = { side: r.left + r.width / 2 < vw() / 2 ? 'left' : 'right', t: maxY > minY ? clamp((r.top - minY) / (maxY - minY), 0, 1) : 1 };
    savePos();
    applyPos();
  };

  const send = async (text) => {
    const s = st();
    text = text.trim();
    if (!text || s.pending) return;
    s.pending = true;
    sending = true;
    input.value = ''; autoGrow(); syncSend();
    if (!s.messages.length) thread.innerHTML = '';
    s.messages.push({ role: 'user', content: text, created_at: new Date().toISOString() });
    thread.insertAdjacentHTML('beforeend', userTurnHTML(text) + aiTypingHTML(kind));
    toBottom();
    try {
      const msg = await aiReply(kind, text, s);
      if (s !== st()) return;  // đã đăng xuất trong lúc chờ
      thread.querySelector('.is-typing')?.remove();
      thread.insertAdjacentHTML('beforeend', aiTurnHTML(msg, kind, { hideBody: true }));
      s.pending = false;
      syncSend();
      refreshAIBadge();
      await typeOutTurn(thread.lastElementChild, msg.content, toBottom);
    } catch (e) {
      if (s !== st()) return;
      thread.querySelector('.is-typing')?.remove();
      thread.insertAdjacentHTML('beforeend', aiTurnHTML({ role: 'assistant', content: e.message, error: true }, kind));
      toBottom();
    } finally {
      s.pending = false;
      sending = false;
      syncSend();
      document.dispatchEvent(new CustomEvent('ai:settled', { detail: { st: s, origin: thread } }));
    }
  };

  const onThreadClick = async (e) => {
    const q = e.target.closest('[data-q]');
    if (q) { send(q.dataset.q); return; }
    const copy = e.target.closest('[data-copy]');
    if (copy) { navigator.clipboard.writeText(copy.dataset.copy).then(() => toast('Đã sao chép câu trả lời', 'success')); return; }
    const cart = e.target.closest('[data-cart]');
    if (cart) {
      try {
        const p = await addByCode(cart.dataset.cart);
        if (!p) return;
        toast(`Đã thêm "${p.name}" vào giỏ hàng`, 'success');
        if ($('#cart-items')) POS.renderCart?.();  // đang ở màn hình bán hàng: cập nhật giỏ ngay
      } catch (err) { toast(err.message, 'error'); }
    }
  };

  function init() {
    wrap = document.createElement('div');
    wrap.className = 'ai-fab-wrap hidden';
    wrap.innerHTML = `
      <section class="ai-pop" id="ai-pop" role="dialog" aria-label="Trợ lý AI" hidden>
        <header class="ai-pop-head">
          <div class="ai-avatar">${icon('sparkles')}</div>
          <div class="grow"><div class="t">${CHAT_CFG[kind].assistant}</div><div class="s">Sẵn sàng hỗ trợ bạn</div></div>
          <button type="button" class="icon-tool" id="ai-pop-new" title="Cuộc trò chuyện mới" aria-label="Cuộc trò chuyện mới">${icon('plus')}</button>
          <a class="icon-tool" href="#assistant" title="Mở rộng toàn trang" aria-label="Mở rộng toàn trang">${icon('expand')}</a>
          <button type="button" class="icon-tool" id="ai-pop-close" title="Đóng (Esc)" aria-label="Đóng">${icon('x')}</button>
        </header>
        <div class="ai-pop-scroll" id="ai-pop-scroll"><div class="ai-pop-thread" id="ai-pop-thread"></div></div>
        <form class="ai-pop-composer" id="ai-pop-form">
          <textarea id="ai-pop-input" rows="1" maxlength="1000" placeholder="Hỏi bất cứ điều gì..." aria-label="Câu hỏi cho trợ lý AI"></textarea>
          <button class="send-btn" id="ai-pop-send" type="submit" title="Gửi (Enter)" aria-label="Gửi" disabled>${icon('arrow-up')}</button>
        </form>
      </section>
      <button type="button" class="ai-fab" id="ai-fab-btn" aria-controls="ai-pop" aria-expanded="false"></button>`;
    $('#app-view').appendChild(wrap);
    btn = $('#ai-fab-btn', wrap);
    pop = $('#ai-pop', wrap);
    thread = $('#ai-pop-thread', wrap);
    scroller = $('#ai-pop-scroll', wrap);
    input = $('#ai-pop-input', wrap);
    sendBtn = $('#ai-pop-send', wrap);
    btn.setAttribute('aria-label', 'Mở trợ lý AI');
    setOpen(false);
    loadPos();
    applyPos();

    btn.onclick = () => { if (!justDragged) setOpen(!isOpen()); };
    btn.addEventListener('pointerdown', onPointerDown);
    btn.addEventListener('pointermove', onPointerMove);
    btn.addEventListener('pointerup', onPointerUp);
    btn.addEventListener('pointercancel', onPointerUp);
    window.addEventListener('resize', applyPos);
    $('#ai-pop-close', wrap).onclick = () => { setOpen(false); btn.focus(); };
    $('#ai-pop-new', wrap).onclick = () => {
      if (st().pending) return;
      Object.assign(st(), { sessionId: null, title: '', messages: [] });
      rememberChat(kind, null);
      render();
      input.focus();
    };
    input.oninput = () => { autoGrow(); syncSend(); };
    input.onkeydown = (e) => {
      if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); send(input.value); }
    };
    $('#ai-pop-form', wrap).onsubmit = (e) => { e.preventDefault(); send(input.value); };
    pop.addEventListener('keydown', (e) => { if (e.key === 'Escape') { setOpen(false); btn.focus(); } });
    thread.onclick = onThreadClick;
    // Câu hỏi gửi từ trang "Trợ lý đa năng" rồi chuyển trang trước khi có trả lời: vẽ lại khi câu trả lời về
    document.addEventListener('ai:settled', (e) => {
      if (isOpen() && !sending && e.detail.st === st() && e.detail.origin !== thread) render();
    });
  }

  // Gọi mỗi lần chuyển trang / đăng nhập / đăng xuất: ẩn nút trên các trang chat AI (đã có khung chat riêng)
  function sync() {
    if (!wrap) return;
    const show = Boolean(S.user) && !isAdmin() && !AI_CHAT_ROUTES.includes(S.route);  // quản trị viên không dùng AI nghiệp vụ
    if (!show && isOpen()) setOpen(false);
    wrap.classList.toggle('hidden', !show);
    $('#app-view').classList.toggle('fab-visible', show);
    if (show) applyPos();
    if (!S.user) { input.value = ''; autoGrow(); }
  }

  return { init, sync };
})();

// ============================================================ Đổi trả hàng (thu ngân, chủ cửa hàng)
// Tra hóa đơn theo mã (quét mã QR in trên hóa đơn bằng camera / máy quét mã vạch), chọn hàng khách trả, hoàn tiền.
async function pageReturns(page) {
  const qs = routeQuery();
  const hours = S.payCfg?.return_hours ?? 24;
  page.innerHTML = `<div class="card">${cardHead('undo', 'Nhận đổi trả hàng')}
      <p class="muted small mt-0">Quét mã QR trên hóa đơn hoặc nhập mã hóa đơn. Cửa hàng nhận đổi trả trong <b>${hours} giờ</b> kể từ lúc mua.
        Đổi hàng: lập phiếu trả cho món cũ rồi lập hóa đơn mới cho món khách lấy.</p>
      <form class="toolbar mb-0" id="rt-find"><div class="input-icon grow">${icon('barcode')}<input name="code" placeholder="Mã hóa đơn, VD: HD2610060001, rồi Enter" autocomplete="off" value="${esc(qs.get('code') || '')}"></div>
        <button class="btn" type="button" id="rt-scan">${icon('scan')} Quét mã</button><button class="btn primary">${icon('search')} Tra hóa đơn</button></form>
      <div id="rt-invoice"></div></div>
    <div class="card mt">${cardHead('history', 'Phiếu đổi trả gần đây')}<div id="rt-list">${skeletonLines()}</div></div>`;
  let returns = [];
  const loadList = async () => {
    const data = await api('/returns', { params: { size: 20 } });
    returns = data.items;
    $('#rt-list').innerHTML = table(['Mã phiếu', 'Thời gian', 'Hóa đơn', 'Khách hàng', 'Lý do', ['Hoàn tiền', 'right'], 'Người nhận'],
      returns.map((r) => [`<b>${esc(r.code)}</b>`, `<span class="nowrap">${fmtDate(r.created_at)}</span>`, esc(r.invoice_code), esc(r.customer_name), esc(r.reason),
        `<b>${money(r.refund_total)}</b>`, esc(r.user_name)]),
      { empty: 'Chưa có phiếu đổi trả', rowAttrs: (k) => `class="clickable" data-id="${returns[k].id}"` });
  };
  const box = $('#rt-invoice');
  const render = (inv) => {
    const open = inv.can_return;
    box.innerHTML = `<div class="mt">
      <div class="info-list"><div><span class="k">Hóa đơn</span><span><b>${esc(inv.code)}</b> ${statusBadge(inv.status)}</span></div>
        <div><span class="k">Thời gian mua</span>${fmtDate(inv.created_at)}</div><div><span class="k">Khách hàng</span>${esc(inv.customer_name)}</div>
        <div><span class="k">Khách đã trả</span>${money(inv.total)}${inv.refunded ? ` · đã hoàn ${money(inv.refunded)}` : ''}</div>
        <div><span class="k">Hạn đổi trả</span>${fmtDate(inv.return_deadline)}</div></div>
      ${open ? '' : note(inv.cannot_return_reason)}
      ${table(['Sản phẩm', ['Đã mua', 'right'], ['Đã trả', 'right'], ['Hoàn / sản phẩm', 'right'], 'Trả lại', 'Tình trạng hàng'], inv.items.map((it) => [
        productCell(it) + serialChips(it.serials), it.quantity, it.returned, money(it.unit_refund),
        !open || !it.returnable ? '<span class="muted">-</span>' : it.track_serial
          ? `<div class="serial-list compact">${it.returnable_serials.map((s) => `<label><input type="checkbox" data-sn="${it.product_id}" value="${esc(s)}">${esc(s)}</label>`).join('')}</div>`
          : `<input type="number" min="0" max="${it.returnable}" value="0" class="w-full" data-qty="${it.product_id}" title="Trả tối đa ${it.returnable}">`,
        open && it.returnable ? `<select data-restock="${it.product_id}"><option value="1">Còn tốt, nhập lại kho</option><option value="0">Hàng lỗi, không nhập kho</option></select>` : '',
      ]))}
      ${open ? `<div class="form-grid mt">
          <label>Lý do đổi trả *<input id="rt-reason" maxlength="255" placeholder="VD: Khách không vừa ý, lỗi kỹ thuật..."></label>
          <label>Ghi chú<input id="rt-note" maxlength="255"></label></div>
        <div class="row mt"><div class="grow muted" id="rt-sum">Chọn hàng khách trả</div>
          <button class="btn primary" id="rt-save">${icon('undo')} Lập phiếu trả, hoàn tiền</button></div>` : ''}</div>`;
    if (!open) return;
    const pick = () => inv.items.map((it) => {
      const serials = $$(`[data-sn="${it.product_id}"]`, box).filter((b) => b.checked).map((b) => b.value);
      const qty = it.track_serial ? serials.length : Math.min(Math.max(0, parseInt($(`[data-qty="${it.product_id}"]`, box)?.value, 10) || 0), it.returnable);
      return { it, qty, serials, restock: $(`[data-restock="${it.product_id}"]`, box)?.value !== '0' };
    }).filter((x) => x.qty > 0);
    const sum = () => {
      const p = pick();
      $('#rt-sum').innerHTML = p.length ? `Trả ${p.reduce((s, x) => s + x.qty, 0)} sản phẩm · dự kiến hoàn <b class="text-default">${money(p.reduce((s, x) => s + x.qty * x.it.unit_refund, 0))}</b>` : 'Chọn hàng khách trả';
    };
    box.oninput = sum;
    box.onchange = sum;
    $('#rt-save').onclick = async () => {
      const p = pick();
      const reason = $('#rt-reason').value.trim();
      if (!p.length) { toast('Chọn sản phẩm và số lượng khách trả', 'error'); return; }
      if (!reason) { $('#rt-reason').focus(); toast('Nhập lý do đổi trả', 'error'); return; }
      if (!await confirmBox(`Lập phiếu trả ${p.reduce((s, x) => s + x.qty, 0)} sản phẩm của hóa đơn ${inv.code} và hoàn tiền cho khách?`, { okText: 'Lập phiếu trả' })) return;
      try {
        const r = await api('/returns', { method: 'POST', body: { invoice_id: inv.id, reason, note: $('#rt-note').value.trim() || null,
          items: p.map((x) => ({ product_id: x.it.product_id, quantity: x.qty, restock: x.restock, ...(x.serials.length ? { serials: x.serials } : {}) })) } });
        toast(`Đã lập phiếu ${r.code}, hoàn ${money(r.refund_total)}`, 'success');
        showReturnSlip(r);
        find(inv.code);
        loadList();
      } catch (e) { toast(e.message, 'error'); }
    };
  };
  const find = async (code) => {
    code = String(code || '').trim();
    if (!code) return;
    box.innerHTML = `<div class="mt">${skeletonLines(3)}</div>`;
    try { render(await api('/aftersales/invoice', { params: { code } })); }
    catch (e) { box.innerHTML = `<div class="mt">${emptyState('search', e.message, 'Kiểm tra lại mã trên hóa đơn của khách.', { compact: true })}</div>`; }
  };
  $('#rt-find').onsubmit = (e) => { e.preventDefault(); find(e.target.code.value); };
  $('#rt-scan').onclick = () => openScanner({ title: 'Quét mã hóa đơn', placeholder: 'Mã hóa đơn, rồi Enter', onCode: (c) => { $('#rt-find').code.value = c; find(c); } });
  $('#rt-list').onclick = (e) => { const r = e.target.closest('tr[data-id]'); if (r) showReturnSlip(returns.find((x) => x.id == r.dataset.id)); };
  if (qs.get('code')) find(qs.get('code'));
  else $('#rt-find').code.focus();
  await loadList();
}

function showReturnSlip(r) {
  const cfg = S.payCfg || {};
  const m = modal({
    title: `${icon('undo')} Phiếu đổi trả ${esc(r.code)}`, size: 'narrow',
    body: `<div class="receipt print-area"><div class="center"><b>${esc((cfg.shop_name || 'Cửa hàng SalesAI').toUpperCase())}</b><br>PHIẾU TRẢ HÀNG, HOÀN TIỀN<br>${esc(r.code)} · ${fmtDate(r.created_at)}</div><br>
      Hóa đơn gốc: ${esc(r.invoice_code)}<br>Khách hàng: ${esc(r.customer_name)}<br>Người nhận: ${esc(r.user_name)}<br>Lý do: ${esc(r.reason)}
      <table class="my-2"><thead><tr><th>Sản phẩm</th><th class="right">SL</th><th class="right">Hoàn</th></tr></thead><tbody>
      ${r.items.map((i) => `<tr><td>${esc(i.product_name)}${i.serials.length ? `<br><small>IMEI/SN: ${i.serials.map(esc).join(', ')}</small>` : ''}
        <br><small>${i.restock ? 'Nhập lại kho' : 'Hàng lỗi, không nhập kho'}</small></td><td class="right">${i.quantity}</td><td class="right">${money(i.refund)}</td></tr>`).join('')}
      </tbody></table>
      <div class="totals"><div class="grand"><span>HOÀN TIỀN</span><span>${money(r.refund_total)}</span></div>
        ${r.points_reverted ? `<div><span>Trừ điểm đã tích</span><span>-${num(r.points_reverted)}</span></div>` : ''}</div>
      <p class="small">Khách hàng ký nhận tiền:<br><br>..............................</p></div>`,
    footer: `<button class="btn" data-close>Đóng</button><button class="btn primary" id="rs-print">${icon('printer')} In phiếu</button>`,
  });
  $('#rs-print', m.el).onclick = () => window.print();
}

// ============================================================ Bảo hành (thu ngân, chủ cửa hàng)
const WARRANTY_COLOR = { received: 'blue', processing: 'yellow', done: 'green', rejected: 'red' };
const WARRANTY_VI = { received: 'Đã tiếp nhận', processing: 'Đang xử lý', done: 'Đã trả khách', rejected: 'Từ chối bảo hành' };
const wBadge = (s) => `<span class="badge dot ${WARRANTY_COLOR[s]}">${WARRANTY_VI[s]}</span>`;
const warrantyState = (inWarranty, until) => (inWarranty ? `<span class="badge green">Còn bảo hành đến ${fmtDay(until)}</span>`
  : until ? `<span class="badge red">Hết bảo hành từ ${fmtDay(until)}</span>` : '<span class="badge">Không có bảo hành</span>');

async function pageWarranty(page) {
  const qs = routeQuery();
  page.innerHTML = `<div class="card">${cardHead('search', 'Tra cứu bảo hành, tiếp nhận máy')}
      <p class="muted small mt-0">Nhập hoặc quét mã hóa đơn / IMEI / serial của máy khách mang tới. Hạn bảo hành = ngày mua + số tháng bảo hành của sản phẩm.</p>
      <form class="toolbar mb-0" id="wr-find"><div class="input-icon grow">${icon('barcode')}<input name="key" placeholder="Mã hóa đơn hoặc IMEI / serial, rồi Enter" autocomplete="off" value="${esc(qs.get('code') || '')}"></div>
        <button type="button" class="btn" id="wr-scan">${icon('scan')} Quét mã</button><button class="btn primary">${icon('search')} Tra cứu</button>
        <button type="button" class="btn" id="wr-noinv">${icon('plus')} Khách không có hóa đơn</button></form>
      <div id="wr-result"></div></div>
    <div class="card mt">${cardHead('wrench', 'Phiếu bảo hành')}
      <form class="toolbar" id="wr-filter"><label class="grow">Tìm kiếm<div class="input-icon">${icon('search')}<input name="q" placeholder="Mã phiếu, tên / SĐT khách, IMEI"></div></label>
        <label>Trạng thái<select name="status"><option value="open">Chưa xong (tiếp nhận, đang xử lý)</option><option value="">Tất cả</option>
          ${Object.entries(WARRANTY_VI).map(([k, v]) => `<option value="${k}">${v}</option>`).join('')}</select></label>
        <button class="btn">${icon('search')} Lọc</button></form>
      <div id="wr-list">${skeletonLines()}</div></div>`;
  const f = { q: '', status: 'open', page: 1, size: 20 };
  let tickets = [];
  const loadList = async () => {
    const data = await api('/warranty', { params: f });
    tickets = data.items;
    $('#wr-list').innerHTML = table(['Mã phiếu', 'Tiếp nhận', 'Khách hàng', 'Sản phẩm', 'Lỗi', 'Bảo hành', 'Trạng thái'],
      tickets.map((t) => [`<b>${esc(t.code)}</b>`, `<span class="nowrap">${fmtDate(t.created_at)}</span>`, `${esc(t.customer_name)}<div class="muted small">${esc(t.customer_phone || '')}</div>`,
        productCell(t) + (t.serial ? serialChips([t.serial]) : ''), esc(t.issue), t.in_warranty ? '<span class="badge green">Trong hạn</span>' : '<span class="badge red">Ngoài hạn</span>', wBadge(t.status)]),
      { empty: 'Không có phiếu bảo hành', rowAttrs: (k) => `class="clickable" data-id="${tickets[k].id}"` });
    $('#wr-list').appendChild(pager(data.total, f.page, f.size, (p) => { f.page = p; loadList(); }));
  };
  const reload = () => { loadList(); refreshCounts(); };
  const out = $('#wr-result');
  const find = async (key) => {
    key = String(key || '').trim();
    if (!key) return;
    out.innerHTML = `<div class="mt">${skeletonLines(3)}</div>`;
    const bySerial = () => api('/aftersales/serial', { params: { serial: key } });
    const byInvoice = () => api('/aftersales/invoice', { params: { code: key } });
    try {
      if (/^hd\d+/i.test(key)) { renderInvoice(await byInvoice()); return; }
      try { renderSerial(await bySerial()); } catch { renderInvoice(await byInvoice()); }
    } catch (e) {
      out.innerHTML = `<div class="mt">${emptyState('search', `Không tìm thấy hóa đơn hoặc IMEI / serial "${key}"`, 'Kiểm tra lại mã, hoặc tiếp nhận như khách không có hóa đơn.', { compact: true })}</div>`;
    }
  };
  const renderInvoice = (inv) => {
    out.innerHTML = `<div class="mt"><div class="info-list"><div><span class="k">Hóa đơn</span><span><b>${esc(inv.code)}</b> ${statusBadge(inv.status)}</span></div>
        <div><span class="k">Ngày mua</span>${fmtDate(inv.created_at)}</div><div><span class="k">Khách hàng</span>${esc(inv.customer_name)} ${inv.customer_phone ? `· ${esc(inv.customer_phone)}` : ''}</div></div>
      ${table(['Sản phẩm', 'Thời hạn', 'Tình trạng bảo hành', ['', 'right']], inv.items.map((it) => [productCell(it) + serialChips(it.serials),
        it.warranty_months ? `${it.warranty_months} tháng` : '-', warrantyState(it.in_warranty, it.warranty_until),
        inv.status === 'paid' ? `<button class="btn sm" data-take="${it.product_id}">${icon('wrench')} Tiếp nhận</button>` : '']))}</div>`;
    out.onclick = (e) => {
      const b = e.target.closest('[data-take]');
      if (!b) return;
      const it = inv.items.find((x) => x.product_id == b.dataset.take);
      warrantyForm({ invoice_id: inv.id, invoice_code: inv.code, product: it, serials: it.serials, customer_name: inv.customer_id ? inv.customer_name : '',
        customer_phone: inv.customer_phone, in_warranty: it.in_warranty, warranty_until: it.warranty_until }, reload);
    };
  };
  const renderSerial = (s) => {
    out.innerHTML = `<div class="mt"><div class="info-list"><div><span class="k">IMEI / serial</span><b>${esc(s.serial)}</b></div>
        <div><span class="k">Sản phẩm</span>${esc(s.product_name)} (${esc(s.product_code)})</div>
        <div><span class="k">Hóa đơn</span>${s.invoice_code ? `${esc(s.invoice_code)} · ${fmtDate(s.sold_at)}` : '<span class="muted">Máy chưa bán / không thuộc hóa đơn nào</span>'}</div>
        <div><span class="k">Khách hàng</span>${esc(s.customer_name || '-')}</div>
        <div><span class="k">Bảo hành</span>${warrantyState(s.in_warranty, s.warranty_until)}</div></div>
      <button class="btn primary" id="wr-take">${icon('wrench')} Tiếp nhận bảo hành máy này</button></div>`;
    $('#wr-take').onclick = () => warrantyForm({ invoice_id: s.invoice_id, invoice_code: s.invoice_code, product: { product_id: s.product_id, product_name: s.product_name, product_code: s.product_code },
      serial: s.serial, customer_name: s.customer_name === 'Khách lẻ' ? '' : s.customer_name, in_warranty: s.in_warranty, warranty_until: s.warranty_until }, reload);
  };
  $('#wr-find').onsubmit = (e) => { e.preventDefault(); find(e.target.key.value); };
  $('#wr-scan').onclick = () => openScanner({ title: 'Quét mã hóa đơn / IMEI', placeholder: 'Mã hóa đơn hoặc IMEI, rồi Enter', onCode: (c) => { $('#wr-find').key.value = c; find(c); } });
  $('#wr-noinv').onclick = async () => {
    const { items } = await api('/products', { params: { size: 200 } });
    warrantyForm({ products: items }, reload);
  };
  $('#wr-filter').onsubmit = (e) => { e.preventDefault(); Object.assign(f, formValues(e.target), { page: 1 }); loadList(); };
  $('#wr-list').onclick = (e) => { const r = e.target.closest('tr[data-id]'); if (r) ticketDetail(r.dataset.id, reload); };
  if (qs.get('code')) find(qs.get('code'));
  await loadList();
}

// Phiếu tiếp nhận bảo hành. ctx.products: khách không có hóa đơn, chọn sản phẩm trong danh mục
function warrantyForm(ctx, onSaved) {
  const p = ctx.product;
  const m = modal({
    title: `${icon('wrench')} Tiếp nhận bảo hành`,
    body: `<form id="wf" class="form-grid">
      ${p ? `<div class="full">${productCell(p)}</div>
        <div class="full">${ctx.invoice_code ? `Hóa đơn <b>${esc(ctx.invoice_code)}</b> · ` : ''}${warrantyState(ctx.in_warranty, ctx.warranty_until)}</div>`
        : `<label class="full">Sản phẩm *<select name="product_id" required>${ctx.products.map((x) => `<option value="${x.id}">${esc(x.code)} - ${esc(x.name)}</option>`).join('')}</select></label>
          <div class="full">${note('Không có hóa đơn: phiếu tính là ngoài bảo hành (sửa chữa dịch vụ, có thể tính phí).')}</div>`}
      <label>Tên khách hàng ${p && ctx.invoice_code ? '' : '*'}<input name="customer_name" ${p && ctx.invoice_code ? '' : 'required'} maxlength="100" value="${esc(ctx.customer_name || '')}" placeholder="${ctx.invoice_code ? 'Theo hóa đơn' : ''}"></label>
      <label>Số điện thoại liên hệ<input name="customer_phone" type="tel" maxlength="20" value="${esc(ctx.customer_phone || '')}"></label>
      ${ctx.serials?.length ? `<label class="full">IMEI / serial<select name="serial">${ctx.serials.map((s) => `<option>${esc(s)}</option>`).join('')}</select></label>`
        : `<label class="full">IMEI / serial (nếu có)<input name="serial" maxlength="100" value="${esc(ctx.serial || '')}" ${ctx.serial ? 'readonly' : ''}></label>`}
      <label class="full">Tình trạng lỗi khách báo *<textarea name="issue" rows="3" required maxlength="500" placeholder="VD: máy sập nguồn, loa rè, màn hình sọc..."></textarea></label>
      <p class="error full" id="wf-err"></p></form>`,
    footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="wf-save">${icon('check')} Tiếp nhận, in phiếu</button>`,
  });
  $('#wf-save', m.el).onclick = async () => {
    const form = $('#wf', m.el);
    if (!form.reportValidity()) return;
    const v = formValues(form);
    const body = { invoice_id: ctx.invoice_id || null, product_id: p ? p.product_id : +v.product_id, customer_name: v.customer_name || null,
      customer_phone: v.customer_phone || null, serial: v.serial || null, issue: v.issue };
    try {
      const t = await api('/warranty', { method: 'POST', body });
      toast(`Đã tiếp nhận, phiếu ${t.code}`, 'success');
      m.close(); onSaved?.(); printTicket(t);
    } catch (e) { $('#wf-err', m.el).textContent = e.message; }
  };
}

async function ticketDetail(id, onChange) {
  const t = await api(`/warranty/${id}`);
  const open = !['done', 'rejected'].includes(t.status);
  const m = modal({
    title: `${icon('wrench')} Phiếu bảo hành ${esc(t.code)} ${wBadge(t.status)}`, size: 'wide',
    body: `<div class="info-list"><div><span class="k">Khách hàng</span>${esc(t.customer_name)} ${t.customer_phone ? `· ${esc(t.customer_phone)}` : ''}</div>
        <div><span class="k">Sản phẩm</span>${esc(t.product_name)} (${esc(t.product_code)})</div><div><span class="k">IMEI / serial</span>${esc(t.serial || '-')}</div>
        <div><span class="k">Hóa đơn</span>${esc(t.invoice_code || 'Không có')}</div><div><span class="k">Bảo hành</span>${warrantyState(t.in_warranty, t.warranty_until)}</div>
        <div><span class="k">Tiếp nhận</span>${fmtDate(t.created_at)} · ${esc(t.user_name)}</div></div>
      <p><b>Lỗi khách báo:</b> ${esc(t.issue)}</p>${t.result ? `<p><b>Kết quả / tiến độ mới nhất:</b> ${esc(t.result)}</p>` : ''}
      <h3>Tiến độ</h3><ul class="timeline">${t.history.map((h) => `<li><div class="strong">${WARRANTY_VI[h.status] || h.status} <span class="muted small">· ${fmtDate(h.time)} · ${esc(h.user)}</span></div>
        ${h.note ? `<div>${esc(h.note)}</div>` : ''}</li>`).join('')}</ul>
      ${open ? `<form id="tu" class="form-grid mt"><label>Cập nhật trạng thái<select name="status">${Object.entries(WARRANTY_VI).map(([k, v]) => `<option value="${k}" ${k === t.status ? 'selected' : ''}>${v}</option>`).join('')}</select></label>
        <label>Nội dung tiến độ / kết quả<input name="note" maxlength="500" placeholder="VD: Đã gửi hãng, đã thay linh kiện..."></label><p class="error full" id="tu-err"></p></form>` : ''}`,
    footer: `<button class="btn left" id="tk-print">${icon('printer')} In phiếu</button>${open ? `<button class="btn primary" id="tu-save">${icon('check')} Cập nhật tiến độ</button>` : '<button class="btn" data-close>Đóng</button>'}`,
  });
  $('#tk-print', m.el).onclick = () => { m.close(); printTicket(t); };
  $('#tu-save', m.el)?.addEventListener('click', async () => {
    try {
      await api(`/warranty/${t.id}`, { method: 'PUT', body: formValues($('#tu', m.el)) });
      toast('Đã cập nhật phiếu bảo hành', 'success');
      m.close(); onChange?.();
    } catch (e) { $('#tu-err', m.el).textContent = e.message; }
  });
}

function printTicket(t) {
  const cfg = S.payCfg || {};
  const m = modal({
    title: `${icon('printer')} Phiếu bảo hành ${esc(t.code)}`, size: 'narrow',
    body: `<div class="receipt print-area"><div class="center"><b>${esc((cfg.shop_name || 'Cửa hàng SalesAI').toUpperCase())}</b>${cfg.shop_phone ? `<br>ĐT: ${esc(cfg.shop_phone)}` : ''}
        <br>PHIẾU TIẾP NHẬN BẢO HÀNH<br>${esc(t.code)} · ${fmtDate(t.created_at)}</div><br>
      Khách hàng: ${esc(t.customer_name)}${t.customer_phone ? `<br>Điện thoại: ${esc(t.customer_phone)}` : ''}<br>
      Sản phẩm: ${esc(t.product_name)}<br>IMEI / serial: ${esc(t.serial || '-')}<br>Hóa đơn: ${esc(t.invoice_code || 'Không có')}<br>
      Bảo hành: ${t.in_warranty ? `còn hạn đến ${fmtDay(t.warranty_until)}` : 'ngoài bảo hành (sửa chữa dịch vụ)'}<br><br>
      Lỗi khách báo: ${esc(t.issue)}<br>Trạng thái: ${WARRANTY_VI[t.status]}${t.result ? `<br>Kết quả: ${esc(t.result)}` : ''}<br><br>
      <div class="row"><div class="grow center small">Khách hàng<br><br><br>.............</div><div class="grow center small">Nhân viên tiếp nhận<br><br><br>${esc(t.user_name)}</div></div>
      <p class="center small">Vui lòng mang phiếu này khi nhận lại máy.</p></div>`,
    footer: `<button class="btn" data-close>Đóng</button><button class="btn primary" id="tp-print">${icon('printer')} In phiếu</button>`,
  });
  $('#tp-print', m.el).onclick = () => window.print();
}

// ============================================================ Serial / IMEI (chủ cửa hàng)
const SERIAL_VI = { in_stock: '<span class="badge dot green">Trong kho</span>', sold: '<span class="badge dot blue">Đã bán</span>', defective: '<span class="badge dot red">Hàng lỗi</span>' };

async function pageSerials(page) {
  const { items: all } = await api('/products', { params: { size: 200 } });
  const tracked = all.filter((p) => p.track_serial);
  const f = { q: '', product_id: routeQuery().get('product') || '', status: '', page: 1, size: 50 };
  page.innerHTML = `<div class="card">
    <form class="toolbar" id="sr-filter">
      <label class="grow">Tìm IMEI / serial<div class="input-icon">${icon('barcode')}<input name="q" placeholder="Nhập hoặc quét số máy"></div></label>
      <label>Sản phẩm<select name="product_id"><option value="">Tất cả sản phẩm quản lý theo serial</option>${tracked.map((p) => `<option value="${p.id}" ${String(p.id) === f.product_id ? 'selected' : ''}>${esc(p.code)} - ${esc(p.name)}</option>`).join('')}</select></label>
      <label>Trạng thái<select name="status"><option value="">Tất cả</option><option value="in_stock">Trong kho</option><option value="sold">Đã bán</option><option value="defective">Hàng lỗi</option></select></label>
      <button class="btn">${icon('search')} Lọc</button>
      <div class="actions"><button type="button" class="btn primary" id="sr-add">${icon('plus')} Khai báo serial</button></div>
    </form>
    <p class="muted small mt-0">Serial được tạo khi nhập kho. "Khai báo serial" dùng cho hàng đã có sẵn trong kho trước khi bật quản lý theo IMEI / serial.
      Sản phẩm quản lý theo serial: ${tracked.map((p) => `${esc(p.code)} (tồn ${p.stock})`).join(', ') || 'chưa có, bật trong form sản phẩm'}.</p>
    <div id="sr-table">${skeletonLines()}</div></div>`;
  let items = [];
  const load = async () => {
    const data = await api('/serials', { params: f });
    items = data.items;
    $('#sr-table').innerHTML = table(['IMEI / serial', 'Sản phẩm', 'Trạng thái', 'Hóa đơn bán', 'Ghi chú', ['', 'right']], items.map((s) => [
      `<b class="mono">${esc(s.serial)}</b>`, `${esc(s.product_code)} · ${esc(s.product_name)}`, SERIAL_VI[s.status],
      s.invoice_code ? `${esc(s.invoice_code)}<div class="muted small">${fmtDate(s.sold_at)}</div>` : '', esc(s.note || ''),
      s.status === 'sold' ? '' : `<div class="row-actions">
        <button class="btn ghost sm" data-flip="${s.id}">${s.status === 'in_stock' ? 'Đánh dấu lỗi' : 'Đưa về kho'}</button>
        <button class="btn ghost sm icon-only danger" data-del="${s.id}" title="Xóa serial khai báo nhầm">${icon('trash')}</button></div>`]), { empty: 'Không có serial' });
    $('#sr-table').appendChild(pager(data.total, f.page, f.size, (p) => { f.page = p; load(); }));
  };
  $('#sr-filter').onsubmit = (e) => { e.preventDefault(); Object.assign(f, formValues(e.target), { page: 1 }); load(); };
  $('#sr-table').onclick = async (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    const s = items.find((x) => x.id == (b.dataset.flip || b.dataset.del));
    try {
      if (b.dataset.flip) {
        const status = s.status === 'in_stock' ? 'defective' : 'in_stock';
        const reason = await confirmBox(`${status === 'defective' ? 'Đánh dấu lỗi' : 'Đưa về kho'} máy ${s.serial}?`, { input: true, okText: 'Lưu', value: s.note || '' });
        if (!reason) return;
        await api(`/serials/${s.id}`, { method: 'PUT', body: { status, note: reason } });
      } else {
        if (!await confirmBox(`Xóa serial ${s.serial}? Chỉ dùng khi khai báo nhầm.`, { danger: true, okText: 'Xóa' })) return;
        await api(`/serials/${s.id}`, { method: 'DELETE' });
      }
      toast('Đã cập nhật', 'success'); load();
    } catch (err) { toast(err.message, 'error'); }
  };
  $('#sr-add').onclick = () => {
    if (!tracked.length) { toast('Chưa có sản phẩm nào bật quản lý theo IMEI / serial', 'error'); return; }
    const m = modal({
      title: `${icon('hash')} Khai báo serial cho hàng trong kho`,
      body: `<form id="saf" class="stack"><label>Sản phẩm<select name="product_id">${tracked.map((p) => `<option value="${p.id}" ${String(p.id) === f.product_id ? 'selected' : ''}>${esc(p.code)} - ${esc(p.name)} (tồn ${p.stock})</option>`).join('')}</select></label>
        <label>IMEI / serial (mỗi dòng một số, quét bằng máy quét mã vạch)<textarea name="serials" rows="6" required></textarea></label>
        <label>Ghi chú<input name="note" maxlength="255"></label><p class="error m-0" id="saf-err"></p></form>`,
      footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="saf-save">${icon('check')} Lưu</button>`,
    });
    $('#saf-save', m.el).onclick = async () => {
      const form = $('#saf', m.el);
      if (!form.reportValidity()) return;
      const v = formValues(form);
      try {
        const r = await api('/serials', { method: 'POST', body: { product_id: +v.product_id, serials: parseSerials(v.serials), note: v.note || null } });
        toast(r.message, 'success'); m.close(); load();
      } catch (e) { $('#saf-err', m.el).textContent = e.message; }
    };
  };
  await load();
}

// ============================================================ Danh sách có form (nhà cung cấp, hạng thành viên, khuyến mãi)
// fields: [{ name, label, type, required, full, attrs, options }]; trả về modal form, onSubmit(values) ném lỗi thì hiện lên form
function recordForm({ title, fields, values = {}, onSubmit }) {
  const input = (f) => {
    const v = values[f.name];
    if (f.type === 'checkbox') return `<label class="checkbox ${f.full ? 'full' : ''}"><input type="checkbox" name="${f.name}" ${v ?? f.default ? 'checked' : ''}> ${f.label}</label>`;
    const label = `${f.label}${f.required ? ' *' : ''}`;
    if (f.type === 'select') return `<label class="${f.full ? 'full' : ''}">${label}<select name="${f.name}">${f.options.map(([k, t]) => `<option value="${k}" ${String(v ?? f.default ?? '') === String(k) ? 'selected' : ''}>${t}</option>`).join('')}</select></label>`;
    if (f.type === 'money') return `<label class="${f.full ? 'full' : ''}">${label}<input name="${f.name}" ${MONEY_ATTRS} data-type="money" ${f.required ? 'required' : ''} value="${fmtMoneyInput(v ?? '')}" placeholder="${f.placeholder || ''}"></label>`;
    return `<label class="${f.full ? 'full' : ''}">${label}<input name="${f.name}" type="${f.type || 'text'}" ${f.type === 'number' ? 'data-type="int"' : 'data-type="nullable"'}
      ${f.required ? 'required' : ''} ${f.attrs || ''} value="${esc(v ?? f.default ?? '')}" placeholder="${esc(f.placeholder || '')}"></label>`;
  };
  const m = modal({
    title,
    body: `<form id="rf" class="form-grid">${fields.map(input).join('')}<p class="error full" id="rf-err"></p></form>`,
    footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="rf-save">${icon('check')} Lưu</button>`,
  });
  $('#rf-save', m.el).onclick = async () => {
    const form = $('#rf', m.el);
    if (!form.reportValidity()) return;
    try { await onSubmit(formValues(form)); m.close(); } catch (e) { $('#rf-err', m.el).textContent = e.message; }
  };
}

async function pageSuppliers(page) {
  const fields = [
    { name: 'name', label: 'Tên nhà cung cấp', required: true, full: true },
    { name: 'phone', label: 'Số điện thoại', type: 'tel' }, { name: 'email', label: 'Email', type: 'email' },
    { name: 'address', label: 'Địa chỉ', full: true }, { name: 'note', label: 'Ghi chú', full: true },
    { name: 'is_active', label: 'Đang giao dịch', type: 'checkbox', default: true, full: true },
  ];
  const render = async () => {
    const list = await api('/suppliers');
    page.innerHTML = `<div class="card">${cardHead('building', `Nhà cung cấp (${list.length})`, `<button class="btn primary" id="sup-add">${icon('plus')} Thêm nhà cung cấp</button>`)}
      ${table(['Mã', 'Nhà cung cấp', 'Liên hệ', 'Địa chỉ', ['Số phiếu nhập', 'right'], 'Nhập gần nhất', 'Trạng thái', ['', 'right']], list.map((s) => [
        esc(s.code), `<b>${esc(s.name)}</b>${s.note ? `<div class="muted small">${esc(s.note)}</div>` : ''}`, `${esc(s.phone || '')}<div class="muted small">${esc(s.email || '')}</div>`,
        esc(s.address || ''), s.import_count, fmtDate(s.last_import), s.is_active ? '<span class="badge dot green">Đang giao dịch</span>' : '<span class="badge dot">Ngừng</span>',
        `<div class="row-actions"><button class="btn ghost sm icon-only" data-edit="${s.id}" title="Sửa">${icon('edit')}</button>
          <button class="btn ghost sm icon-only danger" data-del="${s.id}" title="Xóa">${icon('trash')}</button></div>`]), { empty: 'Chưa có nhà cung cấp' })}</div>`;
    const save = (s) => recordForm({ title: s ? 'Sửa nhà cung cấp' : 'Thêm nhà cung cấp', fields, values: s || {},
      onSubmit: async (v) => { await api(s ? `/suppliers/${s.id}` : '/suppliers', { method: s ? 'PUT' : 'POST', body: v }); toast('Đã lưu nhà cung cấp', 'success'); render(); } });
    $('#sup-add').onclick = () => save(null);
    $$('[data-edit]', page).forEach((b) => b.onclick = () => save(list.find((s) => s.id == b.dataset.edit)));
    $$('[data-del]', page).forEach((b) => b.onclick = async () => {
      if (!await confirmBox('Xóa nhà cung cấp này? Nhà cung cấp đã có phiếu nhập sẽ chuyển sang ngừng giao dịch.', { danger: true, okText: 'Xóa' })) return;
      try { toast((await api(`/suppliers/${b.dataset.del}`, { method: 'DELETE' })).message, 'success'); render(); } catch (e) { toast(e.message, 'error'); }
    });
  };
  await render();
}

async function pageTiers(page) {
  const fields = [
    { name: 'name', label: 'Tên hạng', required: true, placeholder: 'VD: Vàng' },
    { name: 'min_spent', label: 'Tổng chi tiêu tối thiểu (₫)', type: 'money', required: true },
    { name: 'discount_percent', label: 'Giảm giá tự động mỗi đơn (%)', type: 'number', attrs: 'min="0" max="50"', default: 0 },
    { name: 'note', label: 'Ghi chú', full: true },
  ];
  const render = async () => {
    const list = await api('/tiers');
    page.innerHTML = `<div class="card w-lg">${cardHead('award', 'Hạng thành viên', `<button class="btn primary" id="tier-add">${icon('plus')} Thêm hạng</button>`)}
      <p class="muted small mt-0">Khách được xếp hạng tự động theo tổng chi tiêu (đã trừ tiền hoàn trả hàng). Khi bán, thu ngân chọn khách là hệ thống tự giảm giá theo hạng.
        Điểm tích lũy và giá trị điểm chỉnh ở menu <a href="#business">Tham số kinh doanh</a>.</p>
      ${table(['Hạng', ['Chi tiêu từ', 'right'], ['Giảm giá', 'right'], 'Ghi chú', ['', 'right']], list.map((t) => [`<b>${esc(t.name)}</b>`, money(t.min_spent), `${t.discount_percent}%`, esc(t.note || ''),
        `<div class="row-actions"><button class="btn ghost sm icon-only" data-edit="${t.id}" title="Sửa">${icon('edit')}</button>
          <button class="btn ghost sm icon-only danger" data-del="${t.id}" title="Xóa">${icon('trash')}</button></div>`]), { empty: 'Chưa có hạng thành viên' })}</div>`;
    const save = (t) => recordForm({ title: t ? 'Sửa hạng thành viên' : 'Thêm hạng thành viên', fields, values: t || {},
      onSubmit: async (v) => { await api(t ? `/tiers/${t.id}` : '/tiers', { method: t ? 'PUT' : 'POST', body: { ...v, min_spent: v.min_spent ?? 0, discount_percent: v.discount_percent ?? 0 } }); toast('Đã lưu hạng', 'success'); render(); } });
    $('#tier-add').onclick = () => save(null);
    $$('[data-edit]', page).forEach((b) => b.onclick = () => save(list.find((t) => t.id == b.dataset.edit)));
    $$('[data-del]', page).forEach((b) => b.onclick = async () => {
      if (!await confirmBox('Xóa hạng thành viên này?', { danger: true, okText: 'Xóa' })) return;
      try { await api(`/tiers/${b.dataset.del}`, { method: 'DELETE' }); render(); } catch (e) { toast(e.message, 'error'); }
    });
  };
  await render();
}

async function pagePromotions(page) {
  const fields = [
    { name: 'name', label: 'Tên chương trình', required: true, full: true },
    { name: 'code', label: 'Mã voucher (bỏ trống = thu ngân chọn trong danh sách)', placeholder: 'VD: GIAM50K' },
    { name: 'discount_type', label: 'Kiểu giảm', type: 'select', options: [['percent', 'Phần trăm (%)'], ['amount', 'Số tiền (₫)']] },
    { name: 'value', label: 'Mức giảm (% hoặc ₫)', type: 'number', required: true, attrs: 'min="1"' },
    { name: 'max_discount', label: 'Giảm tối đa (₫, với kiểu %)', type: 'money' },
    { name: 'min_subtotal', label: 'Áp dụng cho đơn từ (₫)', type: 'money' },
    { name: 'usage_limit', label: 'Số lượt dùng tối đa (bỏ trống = không giới hạn)', type: 'number', attrs: 'min="1"' },
    { name: 'start_date', label: 'Từ ngày', type: 'date', required: true, default: today() },
    { name: 'end_date', label: 'Đến ngày', type: 'date', required: true },
    { name: 'note', label: 'Ghi chú', full: true },
    { name: 'is_active', label: 'Đang áp dụng', type: 'checkbox', default: true, full: true },
  ];
  const stateColor = { 'Đang chạy': 'green', 'Chưa bắt đầu': 'blue', 'Tạm dừng': '', 'Hết lượt': 'yellow', 'Đã kết thúc': 'red' };
  const render = async () => {
    const list = await api('/promotions');
    page.innerHTML = `<div class="card">${cardHead('percent', 'Khuyến mãi, voucher', `<button class="btn primary" id="pr-add">${icon('plus')} Thêm chương trình</button>`)}
      <p class="muted small mt-0">Thu ngân chỉ áp dụng các chương trình ở đây (không tự giảm giá). Chương trình có mã là voucher: khách đưa mã, thu ngân nhập đúng mã mới được giảm.</p>
      ${table(['Chương trình', 'Mã voucher', ['Mức giảm', 'right'], 'Điều kiện', 'Thời gian', ['Đã dùng', 'right'], 'Trạng thái', ['', 'right']], list.map((p) => [
        `<b>${esc(p.name)}</b>${p.note ? `<div class="muted small">${esc(p.note)}</div>` : ''}`, p.code ? `<span class="badge blue">${esc(p.code)}</span>` : '',
        p.discount_type === 'percent' ? `${p.value}%${p.max_discount ? `<div class="muted small">tối đa ${money(p.max_discount)}</div>` : ''}` : money(p.value),
        p.min_subtotal ? `Đơn từ ${money(p.min_subtotal)}` : 'Mọi đơn', `${fmtDay(p.start_date)} → ${fmtDay(p.end_date)}`,
        `${num(p.used_count)}${p.usage_limit ? ` / ${num(p.usage_limit)}` : ''}`, `<span class="badge dot ${stateColor[p.state] || ''}">${p.state}</span>`,
        `<div class="row-actions"><button class="btn ghost sm icon-only" data-edit="${p.id}" title="Sửa">${icon('edit')}</button>
          <button class="btn ghost sm icon-only danger" data-del="${p.id}" title="Xóa">${icon('trash')}</button></div>`]), { empty: 'Chưa có chương trình khuyến mãi' })}</div>`;
    const save = (p) => recordForm({ title: p ? 'Sửa chương trình khuyến mãi' : 'Thêm chương trình khuyến mãi', fields, values: p || { end_date: isoDate(Date.now() + 30 * 86400000) },
      onSubmit: async (v) => {
        await api(p ? `/promotions/${p.id}` : '/promotions', { method: p ? 'PUT' : 'POST', body: { ...v, min_subtotal: v.min_subtotal ?? 0 } });
        toast('Đã lưu chương trình', 'success'); render();
      } });
    $('#pr-add').onclick = () => save(null);
    $$('[data-edit]', page).forEach((b) => b.onclick = () => save(list.find((p) => p.id == b.dataset.edit)));
    $$('[data-del]', page).forEach((b) => b.onclick = async () => {
      if (!await confirmBox('Xóa chương trình này? Chương trình đã áp dụng cho hóa đơn sẽ chuyển sang tạm dừng.', { danger: true, okText: 'Xóa' })) return;
      try { toast((await api(`/promotions/${b.dataset.del}`, { method: 'DELETE' })).message, 'success'); render(); } catch (e) { toast(e.message, 'error'); }
    });
  };
  await render();
}

// ============================================================ Tham số (kinh doanh: chủ cửa hàng · kỹ thuật, AI: quản trị viên)
const MONEY_PARAMS = ['POINTS_EARN_AMOUNT', 'POINT_VALUE'];
function paramsForm(params) {
  return params.map((p) => {
    const hint = `${p.help ? `<span class="muted small">${esc(p.help)}</span>` : ''}${p.value !== p.default && JSON.stringify(p.value) !== JSON.stringify(p.default)
      ? `<span class="muted small">Giá trị trong .env: ${esc(Array.isArray(p.default) ? p.default.join(', ') : String(p.default))}</span>` : ''}`;
    if (p.kind === 'bool') return `<label class="checkbox full"><input type="checkbox" name="${p.key}" ${p.value ? 'checked' : ''}> ${esc(p.label)} ${hint}</label>`;
    if (p.kind === 'choice') return `<label>${esc(p.label)}<select name="${p.key}">${p.choices.map((c) => `<option value="${esc(c)}" ${c === p.value ? 'selected' : ''}>${esc(c || 'Mặc định của model')}</option>`).join('')}</select>${hint}</label>`;
    if (MONEY_PARAMS.includes(p.key)) return `<label>${esc(p.label)}<input name="${p.key}" ${MONEY_ATTRS} data-type="money" data-empty="0" value="${fmtMoneyInput(p.value)}">${hint}</label>`;
    if (p.kind === 'int' || p.kind === 'float') return `<label>${esc(p.label)}<input name="${p.key}" type="number" ${p.kind === 'int' ? 'data-type="int"' : 'step="0.5"'} min="${p.min}" max="${p.max}" required value="${p.value}">${hint}</label>`;
    const v = Array.isArray(p.value) ? p.value.join(', ') : p.value;
    return `<label class="${p.kind === 'list' ? 'full' : ''}">${esc(p.label)}<input name="${p.key}" value="${esc(v)}">${hint}</label>`;
  }).join('');
}

function bindParamsForm(form, url, onSaved) {
  form.onsubmit = async (e) => {
    e.preventDefault();
    if (!form.reportValidity()) return;
    const err = $('[data-err]', form);
    err.textContent = '';
    try {
      const r = await api(url, { method: 'PUT', body: { values: formValues(form) } });
      toast(r.changed.length ? `Đã lưu ${r.changed.length} tham số` : 'Không có thay đổi', 'success');
      onSaved?.(r);
    } catch (ex) { err.textContent = ex.message; }
  };
}

async function pageBusiness(page) {
  const { params } = await api('/business-settings');
  page.innerHTML = `<div class="card w-lg">${cardHead('sliders', 'Tham số kinh doanh')}
    <p class="muted small mt-0">Thông tin in trên hóa đơn, tài khoản nhận tiền VietQR, điểm tích lũy, thời hạn đổi trả. Hạng thành viên chỉnh ở menu <a href="#tiers">Hạng thành viên</a>.</p>
    <form id="biz" class="form-grid">${paramsForm(params)}<p class="error full" data-err></p>
      <div class="full right"><button class="btn primary">${icon('check')} Lưu tham số</button></div></form></div>`;
  bindParamsForm($('#biz'), '/business-settings', async () => { S.payCfg = await api('/payments/config').catch(() => S.payCfg); navigate(); });
}

// ============================================================ Báo cáo tồn kho, thẻ kho (chủ cửa hàng)
async function pageInventory(page) {
  await loadCategories();
  const f = { category_id: '', stock: '' };
  page.innerHTML = `<div class="card"><form class="toolbar m-0" id="iv-filter">
      <label>Nhóm hàng<select name="category_id">${categoryOptions('')}</select></label>
      <label>Tình trạng<select name="stock"><option value="">Tất cả</option><option value="ok">Còn hàng</option><option value="low">Sắp hết</option><option value="out">Hết hàng</option></select></label>
      <button class="btn primary">${icon('search')} Xem</button><div class="actions">${exportButtons()}</div></form></div>
    <div id="iv-body" class="stack mt">${skeletonLines(6)}</div>`;
  const load = async () => {
    const r = await api('/reports/inventory', { params: f });
    const s = r.summary;
    $('#iv-body').innerHTML = `<div class="grid kpi">${kpi('layers', '', 'Giá trị tồn (giá vốn)', money(s.value_at_cost), `${num(s.units)} sản phẩm trong kho`, true)}
        ${kpi('wallet', '', 'Giá trị tồn (giá bán)', money(s.value_at_price), `Lãi dự kiến ${money(s.value_at_price - s.value_at_cost)}`)}
        ${kpi('package', '', 'Mặt hàng đang bán', num(s.products))}${kpi('alert', s.low ? 'yellow' : '', 'Sắp hết hàng', num(s.low), `${num(s.out)} mặt hàng đã hết`)}</div>
      <div class="card">${cardHead('tag', 'Theo nhóm hàng')}${table(['Nhóm hàng', ['Số mặt hàng', 'right'], ['Số lượng tồn', 'right'], ['Giá trị vốn', 'right'], ['Giá trị bán', 'right']],
        r.by_category.map((c) => [`<b>${esc(c.category)}</b>`, c.products, num(c.units), money(c.value_at_cost), money(c.value_at_price)]))}</div>
      <div class="card">${cardHead('package', `Chi tiết (${r.items.length})`)}${table(['Sản phẩm', ['Tồn', 'right'], ['Tối thiểu', 'right'], ['Giá vốn', 'right'], ['Giá trị tồn', 'right'], 'Tình trạng', ['', 'right']],
        r.items.map((i) => [productCell(i), num(i.stock), i.min_stock, money(i.cost_price), money(i.value_at_cost), stockBadge(i),
          `<a class="btn ghost sm" href="#stock-card?product=${i.id}">${icon('arrows')} Thẻ kho</a>`]), { empty: 'Không có sản phẩm' })}</div>`;
  };
  $('#iv-filter').onsubmit = (e) => { e.preventDefault(); Object.assign(f, formValues(e.target)); load(); };
  $$('[data-exp]').forEach((b) => b.onclick = () => download('/reports/export/inventory', { ...f, format: b.dataset.exp }));
  await load();
}

async function pageStockCard(page) {
  const { items: products } = await api('/products', { params: { size: 200 } });
  const pid = routeQuery().get('product') || products[0]?.id || '';
  page.innerHTML = `<div class="card"><div class="toolbar m-0">
      <label class="grow">Sản phẩm<select id="sc-product">${products.map((p) => `<option value="${p.id}" ${String(p.id) === String(pid) ? 'selected' : ''}>${esc(p.code)} - ${esc(p.name)}</option>`).join('')}</select></label>
      ${rangePicker('sc-range', daysAgo(29), today())}</div></div>
    <div id="sc-body" class="mt">${products.length ? skeletonLines(6) : emptyState('package', 'Chưa có sản phẩm')}</div>`;
  let range = { date_from: daysAgo(29), date_to: today() };
  const load = async () => {
    const product_id = $('#sc-product').value;
    if (!product_id) return;
    const c = await api('/reports/stock-card', { params: { product_id, ...range } });
    $('#sc-body').innerHTML = `<div class="grid kpi">${kpi('layers', '', 'Tồn đầu kỳ', num(c.opening), fmtDay(c.period.from))}${kpi('down', '', 'Nhập trong kỳ', `+${num(c.total_in)}`)}
        ${kpi('up', '', 'Xuất trong kỳ', `-${num(c.total_out)}`)}${kpi('package', '', 'Tồn cuối kỳ', num(c.closing), `Hiện tại ${num(c.product.stock)}`, true)}</div>
      <div class="card mt">${cardHead('clipboard', `Thẻ kho ${esc(c.product.code)} · ${esc(c.product.name)}`)}
      ${table(['Thời gian', 'Loại', 'Chứng từ', ['Nhập', 'right'], ['Xuất', 'right'], ['Tồn sau', 'right'], 'Ghi chú'], c.movements.map((m) => [`<span class="nowrap">${fmtDate(m.created_at)}</span>`,
        esc(m.type_label), esc(m.ref_code || ''), m.change > 0 ? `<b class="text-success">+${m.change}</b>` : '', m.change < 0 ? `<b class="text-danger">${m.change}</b>` : '', m.stock_after, esc(m.note || '')]),
        { empty: 'Không có nhập / xuất trong kỳ' })}</div>`;
  };
  $('#sc-product').onchange = load;
  bindRange($('#sc-range'), (r) => { range = r; load(); });
  await load();
}

// ============================================================ Quản trị hệ thống (chỉ quản trị viên)
async function pageSettings(page) {
  const [{ params, info }, ai] = await Promise.all([api('/admin/settings'), api('/ai/status').catch(() => null)]);
  const yes = (v, t = 'Đã cấu hình') => (v ? `<span class="badge dot green">${esc(typeof v === 'string' ? v : t)}</span>` : '<span class="badge dot yellow">Chưa cấu hình</span>');
  page.innerHTML = `<div class="grid two">
    <div class="card">${cardHead('settings', 'Cấu hình kỹ thuật và AI')}
      <form id="tech" class="form-grid">${paramsForm(params)}<p class="error full" data-err></p>
        <div class="full right"><button class="btn primary">${icon('check')} Lưu cấu hình</button></div></form></div>
    <div class="stack">
      <div class="card">${cardHead('database', 'Thông tin hệ thống')}<div class="info-list">
        <div><span class="k">Phiên bản</span>${esc(info.version)}</div><div><span class="k">CSDL</span>${esc(info.database)}</div>
        <div><span class="k">Gemini API key (.env)</span>${yes(info.gemini_key)}</div><div><span class="k">Gửi email (Resend / SMTP)</span>${yes(info.mail)}</div>
        <div><span class="k">Email quản trị (ADMIN_EMAIL)</span>${esc(info.admin_email || 'Chưa khai báo')}</div></div>
        <p class="muted small m-0">API key, mật khẩu email, SECRET_KEY chỉ đặt trong file .env (không lưu vào CSDL, không sửa trên giao diện).</p></div>
      <div class="card">${cardHead('sparkles', 'Tình trạng AI')}
        ${ai ? `<p class="mt-0">${ai.enabled ? `Đang dùng: <b>${esc(ai.model || 'tạm hết model khả dụng')}</b>` : 'AI đang chạy chế độ dự phòng (tắt hoặc chưa có API key).'}</p>
          ${table(['Model', 'Trạng thái'], (ai.models || []).map((x) => [esc(x.model), x.available ? '<span class="badge dot green">Dùng được</span>'
            : `<span class="badge dot yellow">Đang nghỉ${x.until ? ` đến ${esc(x.until)}` : ''}</span>`]), { empty: 'Chưa bật AI' })}` : ''}
        <a class="btn sm mt-3" href="#logs?tab=ai">${icon('history')} Xem nhật ký gọi AI</a></div></div></div>`;
  bindParamsForm($('#tech'), '/admin/settings', () => { refreshAIBadge(); navigate(); });
}

async function pageBackup(page) {
  const b = await api('/admin/backup/info');
  page.innerHTML = `<div class="grid two">
    <div class="card">${cardHead('download', 'Sao lưu dữ liệu')}
      <p class="mt-0">Tải về toàn bộ dữ liệu hiện tại (${b.database === 'sqlite' ? 'file CSDL SQLite .db' : 'file JSON'}). Nên sao lưu hằng ngày và cất ở nơi khác máy chủ.</p>
      <div class="info-list"><div><span class="k">Lần sao lưu gần nhất</span>${b.last_backup ? `${fmtDate(b.last_backup.at)} · ${esc(b.last_backup.by)}` : 'Chưa sao lưu'}</div>
        <div><span class="k">Dữ liệu hiện có</span>${num(b.counts.users)} tài khoản · ${num(b.counts.products)} sản phẩm · ${num(b.counts.customers)} khách · ${num(b.counts.invoices)} hóa đơn</div></div>
      <button class="btn primary" id="bk-download">${icon('download')} Tải bản sao lưu</button></div>
    <div class="card">${cardHead('upload', 'Khôi phục dữ liệu')}
      ${b.can_restore ? `<p class="mt-0">Chọn file sao lưu .db đã tải trước đó. <b>Toàn bộ dữ liệu hiện tại sẽ bị thay thế</b>; hãy tải bản sao lưu mới nhất trước khi khôi phục.</p>
        ${b.last_restore ? `<p class="muted small">Lần khôi phục gần nhất: ${fmtDate(b.last_restore.at)} · ${esc(b.last_restore.by)}</p>` : ''}
        <div class="row"><input type="file" id="bk-file" accept=".db,.sqlite,application/x-sqlite3" class="flex-1"><button class="btn danger" id="bk-restore">${icon('upload')} Khôi phục</button></div>`
        : note('CSDL đang dùng không phải SQLite: khôi phục bằng công cụ của hệ quản trị CSDL (pg_restore, mysql...).')}</div></div>`;
  $('#bk-download').onclick = async () => { await download('/admin/backup'); navigate(); };
  $('#bk-restore')?.addEventListener('click', async () => {
    const file = $('#bk-file').files[0];
    if (!file) { toast('Chọn file sao lưu .db', 'error'); return; }
    if (!await confirmBox(`Khôi phục dữ liệu từ "${file.name}"? Toàn bộ dữ liệu hiện tại sẽ bị thay thế và không hoàn tác được.`, { danger: true, okText: 'Khôi phục' })) return;
    const fd = new FormData();
    fd.append('file', file);
    try {
      const r = await api('/admin/restore', { method: 'POST', form: fd });
      toast(r.message, 'success');
      startApp();
    } catch (e) { toast(e.message, 'error'); }
  });
}

async function pageLogs(page) {
  const tab = routeQuery().get('tab') === 'ai' ? 'ai' : 'audit';
  page.innerHTML = `<div class="tabs"><a href="#logs" class="${tab === 'audit' ? 'active' : ''}">${icon('history')} Hoạt động người dùng</a>
    <a href="#logs?tab=ai" class="${tab === 'ai' ? 'active' : ''}">${icon('sparkles')} Gọi AI</a></div><div id="lg-body"></div>`;
  const body = $('#lg-body');
  if (tab === 'ai') {
    const r = await api('/admin/ai-logs');
    const s = r.summary;
    body.innerHTML = `<div class="grid kpi">${kpi('sparkles', '', 'Lượt gọi gần đây', num(s.calls || 0), '', true)}${kpi('check', '', 'Thành công', num(s.ok || 0))}
        ${kpi('alert', s.errors ? 'yellow' : '', 'Lỗi', num(s.errors || 0))}${kpi('calendar', '', 'Thời gian trả lời TB', s.avg_latency_ms ? `${num(s.avg_latency_ms)} ms` : '-')}</div>
      <div class="card mt">${note('Chỉ hiện thông tin kỹ thuật; nội dung câu hỏi và câu trả lời (có thể chứa số liệu kinh doanh) không hiển thị cho quản trị viên.')}
      ${table(['Thời gian', 'Chức năng', 'Model', 'Kết quả', ['Thời gian (ms)', 'right']], r.items.map((x) => [esc(x.time), esc(x.feature), esc(x.model || ''),
        x.status === 'ok' ? '<span class="badge dot green">ok</span>' : `<span class="badge dot red">${esc(x.status)}</span>`, num(x.latency_ms)]), { empty: 'Chưa có lượt gọi AI' })}</div>`;
    return;
  }
  const f = { q: '', action: '', date_from: '', date_to: '', page: 1, size: 50 };
  const first = await api('/admin/audit-logs', { params: f });
  body.innerHTML = `<div class="card"><form class="toolbar" id="lg-filter">
      <label class="grow">Tìm kiếm<div class="input-icon">${icon('search')}<input name="q" placeholder="Tài khoản hoặc nội dung"></div></label>
      <label>Hành động<select name="action"><option value="">Tất cả</option>${Object.entries(first.actions).map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join('')}</select></label>
      <label>Từ ngày<input type="date" name="date_from"></label><label>Đến ngày<input type="date" name="date_to"></label>
      <button class="btn primary">${icon('search')} Lọc</button></form><div id="lg-table"></div></div>`;
  const show = (data) => {
    $('#lg-table').innerHTML = table(['Thời gian', 'Tài khoản', 'Hành động', 'Chi tiết'], data.items.map((x) => [`<span class="nowrap">${fmtDate(x.created_at)}</span>`,
      `<b>${esc(x.username || '')}</b>`, `<span class="badge ${x.action === 'login_failed' ? 'red' : ''}">${esc(x.action_label)}</span>`, esc(x.detail || '')]), { empty: 'Không có nhật ký' });
    $('#lg-table').appendChild(pager(data.total, f.page, f.size, (p) => { f.page = p; load(); }));
  };
  const load = async () => show(await api('/admin/audit-logs', { params: f }));
  $('#lg-filter').onsubmit = (e) => { e.preventDefault(); Object.assign(f, formValues(e.target), { page: 1 }); load(); };
  show(first);
}

// ============================================================ Người dùng
async function pageUsers(page) {
  // Tài khoản tự đăng ký đang chờ duyệt lên đầu danh sách
  const users = (await api('/users')).sort((a, b) => b.pending - a.pending || a.id - b.id);
  const pending = users.filter((u) => u.pending).length;
  setPendingCount(pending);
  const status = (u) => u.pending ? '<span class="badge dot yellow">Chờ duyệt</span>'
    : u.is_active ? '<span class="badge dot green">Hoạt động</span>' : '<span class="badge dot red">Đã khóa</span>';
  const actions = (u) => `<div class="row-actions">${u.pending
    ? `<button class="btn sm primary" data-approve="${u.id}">${icon('check')} Duyệt</button><button class="btn sm danger" data-reject="${u.id}">${icon('x')} Từ chối</button>` : ''}
    <button class="btn ghost sm icon-only" data-edit="${u.id}" title="Sửa">${icon('edit')}</button></div>`;
  page.innerHTML = `<div class="card w-lg">${cardHead('shield', `Người dùng (${users.length})`, `<button class="btn primary" id="u-add">${icon('plus')} Thêm người dùng</button>`)}
    ${pending ? note(`${pending} tài khoản tự đăng ký đang chờ duyệt. Duyệt thì tài khoản đăng nhập được với vai trò Thu ngân (đổi vai trò bằng nút Sửa).`) : ''}
    ${note('Ba vai trò độc lập, không kế thừa nhau: Quản trị viên quản trị hệ thống (không bán hàng, không xem giá vốn / doanh thu); Thu ngân bán hàng, đổi trả, bảo hành, lập phiếu nhập nháp; Chủ cửa hàng có nghiệp vụ của thu ngân và quản lý hàng hóa, giá, khuyến mãi, nhập hàng, tồn kho, báo cáo, duyệt hủy hóa đơn.')}
    ${table(['Tên đăng nhập', 'Họ tên', 'Email', 'Vai trò', 'Trạng thái', ['', 'right']], users.map((u) => [`<b>${esc(u.username)}</b>`, esc(u.full_name), esc(u.email || ''), ROLE_VI[u.role],
      status(u), actions(u)]))}</div>`;
  $$('[data-approve]', page).forEach((b) => b.onclick = async () => {
    const u = users.find((x) => x.id == b.dataset.approve);
    try { await api(`/users/${u.id}`, { method: 'PUT', body: { is_active: true } }); toast(`Đã duyệt tài khoản ${u.username}`, 'success'); navigate(); }
    catch (e) { toast(e.message, 'error'); }
  });
  $$('[data-reject]', page).forEach((b) => b.onclick = async () => {
    const u = users.find((x) => x.id == b.dataset.reject);
    if (!await confirmBox(`Từ chối và xóa yêu cầu tạo tài khoản "${u.username}" (${u.full_name})?`, { danger: true, okText: 'Từ chối' })) return;
    try { const r = await api(`/users/${u.id}`, { method: 'DELETE' }); toast(r.message, 'success'); navigate(); }
    catch (e) { toast(e.message, 'error'); }
  });
  const form = (u) => {
    const m = modal({
      title: u ? `Sửa người dùng ${esc(u.username)}` : 'Thêm người dùng',
      body: `<form id="uf" class="form-grid">
        ${u ? '' : '<label>Tên đăng nhập *<input name="username" required minlength="3"></label>'}
        <label>Họ tên *<input name="full_name" required value="${esc(u?.full_name)}"></label>
        <label>Email (nhận mã đặt lại mật khẩu)<input name="email" type="email" data-type="nullable" value="${esc(u?.email)}"></label>
        <label>Vai trò<select name="role">${Object.entries(ROLE_VI).map(([k, v]) => `<option value="${k}" ${u?.role === k ? 'selected' : ''}>${v}</option>`).join('')}</select></label>
        <label>${u ? 'Mật khẩu mới (bỏ trống nếu không đổi)' : 'Mật khẩu *'}<input name="password" type="password" minlength="6" ${u ? 'data-type="nullable"' : 'required'}></label>
        ${u ? `<label class="checkbox"><input type="checkbox" name="is_active" ${u.is_active ? 'checked' : ''}> ${u.pending ? 'Duyệt, cho phép đăng nhập' : 'Đang hoạt động'}</label>` : ''}
        <p class="error full" id="uf-err"></p></form>`,
      footer: `<button class="btn" data-close>Hủy</button><button class="btn primary" id="uf-save">${icon('check')} Lưu</button>`,
    });
    $('#uf-save', m.el).onclick = async () => {
      const f = $('#uf', m.el);
      if (!f.reportValidity()) return;
      try { await api(u ? `/users/${u.id}` : '/users', { method: u ? 'PUT' : 'POST', body: formValues(f) }); m.close(); navigate(); }
      catch (e) { $('#uf-err', m.el).textContent = e.message; }
    };
  };
  $('#u-add').onclick = () => form(null);
  $$('[data-edit]').forEach((b) => b.onclick = () => form(users.find((u) => u.id == b.dataset.edit)));
}

init();
