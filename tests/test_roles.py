"""Test phân quyền: ba vai trò độc lập, không kế thừa quyền của nhau."""
import pytest

from tests.helpers import product_id

# Chức năng nghiệp vụ: quản trị viên không vào được (không bán hàng, không xem giá vốn / doanh thu)
BUSINESS = [
    ("get", "/api/products"), ("get", "/api/customers"), ("get", "/api/invoices"),
    ("get", "/api/reports/dashboard"), ("get", "/api/reports/revenue"), ("get", "/api/reports/inventory"),
    ("get", "/api/imports"), ("get", "/api/promotions/active"), ("get", "/api/returns"), ("get", "/api/warranty"),
    ("get", "/api/payments/config"), ("post", "/api/ai/assistant"), ("post", "/api/ai/advisor"),
    ("post", "/api/ai/report"), ("get", "/api/business-settings"),
]
# Chức năng quản trị hệ thống: chủ cửa hàng và thu ngân không vào được
ADMIN = [
    ("get", "/api/users"), ("get", "/api/admin/settings"), ("get", "/api/admin/backup"),
    ("get", "/api/admin/backup/info"), ("get", "/api/admin/audit-logs"), ("get", "/api/admin/ai-logs"),
]
# Chỉ chủ cửa hàng
OWNER = [
    ("get", "/api/reports/dashboard"), ("get", "/api/reports/stock-card?product_id=1"), ("get", "/api/promotions"),
    ("get", "/api/serials"), ("get", "/api/stock-movements"), ("post", "/api/ai/ask"), ("get", "/api/business-settings"),
    ("post", "/api/imports"), ("post", "/api/tiers"), ("post", "/api/suppliers"), ("post", "/api/promotions"),
]


def call(client, method, url, h):
    body = {"message": "x", "question": "x"} if method == "post" else None
    return getattr(client, method)(url, headers=h, **({"json": body} if body else {}))


@pytest.mark.parametrize("method,url", BUSINESS)
def test_admin_has_no_business_access(client, admin_h, method, url):
    assert call(client, method, url, admin_h).status_code == 403


@pytest.mark.parametrize("method,url", ADMIN)
def test_owner_and_cashier_have_no_admin_access(client, owner_h, staff_h, method, url):
    assert call(client, method, url, owner_h).status_code == 403
    assert call(client, method, url, staff_h).status_code == 403


@pytest.mark.parametrize("method,url", OWNER)
def test_cashier_has_no_owner_access(client, staff_h, method, url):
    assert call(client, method, url, staff_h).status_code == 403


def test_everyone_sees_ai_status(client, admin_h, owner_h, staff_h):
    for h in (admin_h, owner_h, staff_h):
        assert client.get("/api/ai/status", headers=h).status_code == 200


def test_admin_cannot_sell(client, admin_h, owner_h):
    pk1 = product_id(client, owner_h, "PK001")
    r = client.post("/api/invoices", json={"items": [{"product_id": pk1, "quantity": 1}]}, headers=admin_h)
    assert r.status_code == 403


def test_only_owner_sees_cost_price(client, owner_h, staff_h):
    pk1 = product_id(client, owner_h, "PK001")
    assert client.get(f"/api/products/{pk1}", headers=owner_h).json()["cost_price"] == 220_000
    assert client.get(f"/api/products/{pk1}", headers=staff_h).json()["cost_price"] is None


def test_cancel_paid_invoice_needs_owner_approval(client, owner_h, staff_h):
    pk1 = product_id(client, owner_h, "PK001")
    inv = client.post("/api/invoices", json={"items": [{"product_id": pk1, "quantity": 2}]}, headers=staff_h).json()
    # thu ngân không tự hủy được hóa đơn đã thanh toán
    assert client.post(f"/api/invoices/{inv['id']}/cancel", json={"reason": "x"}, headers=staff_h).status_code == 403
    r = client.post(f"/api/invoices/{inv['id']}/cancel-request", json={"reason": "Nhập nhầm"}, headers=staff_h)
    assert r.status_code == 200 and r.json()["cancel_requested_at"]
    assert client.post(f"/api/invoices/{inv['id']}/cancel-request", json={"reason": "lần 2"},
                       headers=staff_h).status_code == 400
    counts = client.get("/api/invoices/pending-count", headers=owner_h).json()
    assert counts["cancel_requests"] == 1
    pending = client.get("/api/invoices", params={"cancel_pending": True}, headers=owner_h).json()
    assert [i["code"] for i in pending["items"]] == [inv["code"]]
    # từ chối: hóa đơn giữ nguyên
    assert client.post(f"/api/invoices/{inv['id']}/cancel-reject", json={}, headers=staff_h).status_code == 403
    r = client.post(f"/api/invoices/{inv['id']}/cancel-reject", json={"note": "Không đúng"}, headers=owner_h)
    assert r.json()["status"] == "paid" and r.json()["cancel_requested_at"] is None
    # yêu cầu lại rồi duyệt: hoàn kho
    client.post(f"/api/invoices/{inv['id']}/cancel-request", json={"reason": "Nhập nhầm"}, headers=staff_h)
    r = client.post(f"/api/invoices/{inv['id']}/cancel", json={"reason": "Nhập nhầm"}, headers=owner_h)
    assert r.json()["status"] == "cancelled"
    assert client.get(f"/api/products/{pk1}", headers=owner_h).json()["stock"] == 12


def test_audit_log_records_login_and_admin_actions(client, admin_h, owner_h):
    client.post("/api/auth/login", json={"username": "owner", "password": "sai"})
    logs = client.get("/api/admin/audit-logs", headers=admin_h).json()["items"]
    actions = [x["action"] for x in logs]
    assert "login" in actions and "login_failed" in actions
    client.post("/api/users", json={"username": "thungan2", "full_name": "Thu ngân 2", "password": "abc12345"},
                headers=admin_h)
    logs = client.get("/api/admin/audit-logs", params={"action": "user_create"}, headers=admin_h).json()["items"]
    assert logs and "thungan2" in logs[0]["detail"]


def test_admin_updates_ai_settings(client, admin_h):
    r = client.put("/api/admin/settings", json={"values": {"AI_THINKING_LEVEL": "low", "AI_MAX_RETRIES": 3,
                                                            "GEMINI_FALLBACK_MODELS": "a-1, b-2"}}, headers=admin_h)
    assert r.status_code == 200, r.text
    params = {p["key"]: p["value"] for p in r.json()["params"]}
    assert params["AI_THINKING_LEVEL"] == "low" and params["AI_MAX_RETRIES"] == 3
    assert params["GEMINI_FALLBACK_MODELS"] == ["a-1", "b-2"]
    assert client.put("/api/admin/settings", json={"values": {"AI_MAX_RETRIES": 99}}, headers=admin_h).status_code == 400
    # quản trị viên không sửa được tham số kinh doanh, chủ cửa hàng không sửa được cấu hình kỹ thuật
    assert client.put("/api/admin/settings", json={"values": {"RETURN_HOURS": 1}}, headers=admin_h).status_code == 400


def test_owner_updates_business_settings(client, owner_h):
    r = client.put("/api/business-settings", json={"values": {"RETURN_HOURS": 48, "SHOP_NAME": "Shop ABC"}},
                   headers=owner_h)
    assert r.status_code == 200, r.text
    assert client.get("/api/payments/config", headers=owner_h).json()["return_hours"] == 48
    r = client.put("/api/business-settings", json={"values": {"AI_ENABLED": False}}, headers=owner_h)
    assert r.status_code == 400


def test_backup_and_restore(client, admin_h, owner_h):
    r = client.get("/api/admin/backup", headers=admin_h)
    assert r.status_code == 200 and r.content.startswith(b"SQLite format 3")
    backup = r.content
    client.post("/api/customers", json={"name": "Khách mới sau sao lưu"}, headers=owner_h)
    assert client.get("/api/customers", params={"q": "sau sao lưu"}, headers=owner_h).json()["total"] == 1
    bad = client.post("/api/admin/restore", files={"file": ("x.db", b"not a db", "application/octet-stream")},
                      headers=admin_h)
    assert bad.status_code == 400
    r = client.post("/api/admin/restore", files={"file": ("backup.db", backup, "application/octet-stream")},
                    headers=admin_h)
    assert r.status_code == 200, r.text
    assert client.get("/api/customers", params={"q": "sau sao lưu"}, headers=owner_h).json()["total"] == 0
    actions = [x["action"] for x in client.get("/api/admin/audit-logs", headers=admin_h).json()["items"]]
    assert "restore" in actions
