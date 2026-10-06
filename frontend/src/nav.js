// Menu theo vai trò, khớp ma trận phân quyền SRS bảng 4.2 (backend vẫn kiểm tra quyền ở từng API)
export const NAV = [
  { group: 'Bán hàng', items: [
    { to: '/', label: 'Tổng quan', icon: 'dashboard', roles: ['owner'] },
    { to: '/pos', label: 'Bán hàng', icon: 'cart', roles: ['owner', 'staff'] },
    { to: '/invoices', label: 'Hóa đơn', icon: 'receipt', roles: ['owner', 'staff'] },
    { to: '/returns', label: 'Đổi trả', icon: 'undo', roles: ['owner', 'staff'] },
    { to: '/warranty', label: 'Bảo hành', icon: 'wrench', roles: ['owner', 'staff'] },
  ] },
  { group: 'Danh mục', items: [
    { to: '/customers', label: 'Khách hàng', icon: 'users', roles: ['owner', 'staff'] },
    { to: '/products', label: 'Sản phẩm', icon: 'package', roles: ['owner', 'staff'] },
    { to: '/promotions', label: 'Khuyến mãi', icon: 'percent', roles: ['owner', 'staff'] },
  ] },
  { group: 'Kho', items: [
    { to: '/purchase-orders', label: 'Phiếu nhập', icon: 'truck', roles: ['owner', 'staff'] },
    { to: '/suppliers', label: 'Nhà cung cấp', icon: 'building', roles: ['owner', 'staff'] },
    { to: '/inventory', label: 'Tồn kho', icon: 'arrows', roles: ['owner', 'staff'] },
  ] },
  { group: 'Báo cáo', items: [
    { to: '/reports', label: 'Doanh thu', icon: 'chart', roles: ['owner'] },
  ] },
  { group: 'Trợ lý AI', items: [
    { to: '/ai/assistant', label: 'Trợ lý đa năng', icon: 'sparkles', roles: ['owner', 'staff'] },
    { to: '/ai/advisor', label: 'Tư vấn sản phẩm', icon: 'message', roles: ['owner', 'staff'] },
    { to: '/ai/report', label: 'AI báo cáo', icon: 'file', roles: ['owner'] },
    { to: '/ai/ask', label: 'Hỏi đáp dữ liệu', icon: 'help', roles: ['owner'] },
    { to: '/ai/logs', label: 'Nhật ký AI', icon: 'history', roles: ['owner', 'admin', 'staff'] },
  ] },
  { group: 'Hệ thống', items: [
    { to: '/users', label: 'Người dùng', icon: 'shield', roles: ['admin'] },
    { to: '/settings', label: 'Cấu hình', icon: 'settings', roles: ['owner', 'admin'] },
    { to: '/audit', label: 'Nhật ký thao tác', icon: 'clipboard', roles: ['owner', 'admin'] },
    { to: '/system', label: 'Sao lưu dữ liệu', icon: 'database', roles: ['admin'] },
    { to: '/account', label: 'Tài khoản của tôi', icon: 'key', roles: ['owner', 'staff', 'admin'] },
  ] },
]

export const homeFor = (role) => (role === 'owner' ? '/' : role === 'admin' ? '/users' : '/pos')
