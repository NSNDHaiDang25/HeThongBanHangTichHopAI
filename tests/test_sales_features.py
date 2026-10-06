"""Test nghiệp vụ mới: khuyến mãi / voucher, hạng thành viên, điểm tích lũy, serial / IMEI, đổi trả, bảo hành,
phiếu nhập nháp, hủy phiếu nhập, nhà cung cấp, thẻ kho, báo cáo tồn kho, hóa đơn PDF / email."""
from datetime import timedelta

from sqlalchemy import select

from app.models import Customer, Invoice, now
from app.routers import invoices as invoices_router
from tests.helpers import product_id, stock_of

TODAY = now().date()


def sell(client, h, items, **extra):
    r = client.post("/api/invoices", json={"items": items, **extra}, headers=h)
    assert r.status_code == 201, r.text
    return r.json()


def promo(client, h, **kw):
    body = {"name": "KM", "discount_type": "percent", "value": 10, "start_date": str(TODAY - timedelta(days=1)),
            "end_date": str(TODAY + timedelta(days=5)), **kw}
    r = client.post("/api/promotions", json=body, headers=h)
    assert r.status_code == 201, r.text
    return r.json()


def customer_id(db):
    return db.scalar(select(Customer.id).where(Customer.code == "KH0001"))


# ---------------- Khuyến mãi, voucher ----------------
def test_cashier_applies_promotion_and_voucher(client, owner_h, staff_h):
    pk1 = product_id(client, owner_h, "PK001")
    p = promo(client, owner_h, name="Giảm 10% tối đa 50k", max_discount=50_000, min_subtotal=500_000)
    v = promo(client, owner_h, name="Voucher 30k", code="giam30k", discount_type="amount", value=30_000, usage_limit=1)
    assert [x["id"] for x in client.get("/api/promotions/active", headers=staff_h).json()] == [p["id"]]  # voucher ẩn
    # đơn chưa đủ tối thiểu
    r = client.post("/api/invoices", json={"items": [{"product_id": pk1, "quantity": 1}], "promotion_id": p["id"]},
                    headers=staff_h)
    assert r.status_code == 400 and "áp dụng cho đơn từ" in r.json()["detail"]
    inv = sell(client, staff_h, [{"product_id": pk1, "quantity": 2}], promotion_id=p["id"])
    assert inv["promo_discount"] == 50_000 and inv["total"] == 650_000  # 10% của 700k = 70k, tối đa 50k
    # voucher phải nhập mã, không chọn theo id
    r = client.post("/api/invoices", json={"items": [{"product_id": pk1, "quantity": 1}], "promotion_id": v["id"]},
                    headers=staff_h)
    assert r.status_code == 400
    assert client.get("/api/promotions/voucher/GIAM30K", params={"subtotal": 350_000},
                      headers=staff_h).json()["discount"] == 30_000
    inv = sell(client, staff_h, [{"product_id": pk1, "quantity": 1}], voucher_code="giam30k")
    assert inv["total"] == 320_000 and inv["voucher_code"] == "GIAM30K"
    r = client.post("/api/invoices", json={"items": [{"product_id": pk1, "quantity": 1}], "voucher_code": "GIAM30K"},
                    headers=staff_h)
    assert r.status_code == 400 and "hết lượt" in r.json()["detail"]


def test_expired_promotion_rejected(client, owner_h):
    pk1 = product_id(client, owner_h, "PK001")
    p = promo(client, owner_h, start_date=str(TODAY - timedelta(days=10)), end_date=str(TODAY - timedelta(days=1)))
    r = client.post("/api/invoices", json={"items": [{"product_id": pk1, "quantity": 1}], "promotion_id": p["id"]},
                    headers=owner_h)
    assert r.status_code == 400


# ---------------- Hạng thành viên, điểm tích lũy ----------------
def test_tier_discount_and_points(client, owner_h, staff_h, db):
    cid = customer_id(db)
    pk1 = product_id(client, owner_h, "PK001")
    client.post("/api/tiers", json={"name": "Thành viên", "min_spent": 0, "discount_percent": 0}, headers=owner_h)
    client.post("/api/tiers", json={"name": "Vàng", "min_spent": 500_000, "discount_percent": 5}, headers=owner_h)
    inv = sell(client, staff_h, [{"product_id": pk1, "quantity": 2}], customer_id=cid)  # 700k, chưa lên hạng
    assert inv["tier_discount"] == 0 and inv["points_earned"] == 7  # 100.000 ₫ = 1 điểm
    c = client.get(f"/api/customers/{cid}", headers=staff_h).json()
    assert c["points"] == 7 and c["tier"]["name"] == "Vàng" and c["total_spent"] == 700_000
    inv2 = sell(client, staff_h, [{"product_id": pk1, "quantity": 1}], customer_id=cid, points_used=5)
    assert inv2["tier_discount"] == 17_500  # 5% của 350k
    assert inv2["points_discount"] == 5_000 and inv2["total"] == 350_000 - 17_500 - 5_000
    c = client.get(f"/api/customers/{cid}", headers=staff_h).json()
    assert c["points"] == 7 - 5 + 3
    # dùng quá số điểm đang có
    r = client.post("/api/invoices", json={"items": [{"product_id": pk1, "quantity": 1}], "customer_id": cid,
                                           "points_used": 100}, headers=staff_h)
    assert r.status_code == 400
    # hủy hóa đơn: trừ điểm đã tích, hoàn điểm đã dùng
    client.post(f"/api/invoices/{inv2['id']}/cancel", json={"reason": "test"}, headers=owner_h)
    assert client.get(f"/api/customers/{cid}", headers=staff_h).json()["points"] == 7


def test_owner_adjusts_points(client, owner_h, staff_h, db):
    cid = customer_id(db)
    assert client.post(f"/api/customers/{cid}/points", json={"change": 50, "note": "Tặng"},
                       headers=staff_h).status_code == 403
    r = client.post(f"/api/customers/{cid}/points", json={"change": 50, "note": "Tặng sinh nhật"}, headers=owner_h)
    assert r.json()["points"] == 50
    assert client.post(f"/api/customers/{cid}/points", json={"change": -60, "note": "x"},
                       headers=owner_h).status_code == 400
    hist = client.get(f"/api/customers/{cid}", headers=owner_h).json()["point_history"]
    assert hist[0]["change"] == 50 and hist[0]["type"] == "Điều chỉnh"


# ---------------- Serial / IMEI ----------------
def make_phone(client, owner_h):
    r = client.post("/api/products", json={"code": "DT001", "name": "Điện thoại A", "sale_price": 5_000_000,
                                           "track_serial": True, "warranty_months": 12}, headers=owner_h)
    assert r.status_code == 201, r.text
    pid = r.json()["id"]
    r = client.post("/api/imports", json={"items": [{"product_id": pid, "quantity": 2, "unit_cost": 4_000_000}]},
                    headers=owner_h)
    assert r.status_code == 400 and "serial" in r.json()["detail"]
    r = client.post("/api/imports", json={"items": [{"product_id": pid, "quantity": 2, "unit_cost": 4_000_000,
                                                     "serials": ["imei-111", "IMEI-222"]}]}, headers=owner_h)
    assert r.status_code == 201, r.text
    return pid, r.json()


def test_serial_products_need_serial_to_sell(client, owner_h, staff_h):
    pid, _ = make_phone(client, owner_h)
    assert client.get(f"/api/products/{pid}/serials", headers=staff_h).json() == ["IMEI-111", "IMEI-222"]
    r = client.post("/api/invoices", json={"items": [{"product_id": pid, "quantity": 1}]}, headers=staff_h)
    assert r.status_code == 400 and "serial" in r.json()["detail"]
    # quét IMEI ở màn hình bán hàng: ra đúng sản phẩm kèm serial
    scanned = client.get("/api/products/by-code/imei-222", headers=staff_h).json()
    assert scanned["id"] == pid and scanned["serial"] == "IMEI-222"
    inv = sell(client, staff_h, [{"product_id": pid, "quantity": 1, "serials": ["IMEI-222"]}])
    assert inv["items"][0]["serials"] == ["IMEI-222"]
    assert client.get("/api/products/by-code/IMEI-222", headers=staff_h).status_code == 400  # đã bán
    assert client.get(f"/api/products/{pid}/serials", headers=staff_h).json() == ["IMEI-111"]
    info = client.get("/api/aftersales/serial", params={"serial": "imei-222"}, headers=staff_h).json()
    assert info["invoice_code"] == inv["code"] and info["in_warranty"] is True
    # hủy hóa đơn: serial về kho
    client.post(f"/api/invoices/{inv['id']}/cancel", json={"reason": "x"}, headers=owner_h)
    assert client.get(f"/api/products/{pid}/serials", headers=staff_h).json() == ["IMEI-111", "IMEI-222"]


# ---------------- Đổi trả ----------------
def test_return_refunds_proportionally_and_restocks(client, owner_h, staff_h):
    pk1, pk3 = product_id(client, owner_h, "PK001"), product_id(client, owner_h, "PK003")
    inv = sell(client, owner_h, [{"product_id": pk1, "quantity": 2}, {"product_id": pk3, "quantity": 1}],
               discount=89_000)  # 890k - 89k = 801k (giảm 10%)
    look = client.get("/api/aftersales/invoice", params={"code": inv["code"].lower()}, headers=staff_h).json()
    assert look["can_return"] and look["items"][0]["returnable"] == 2
    r = client.post("/api/returns", json={"invoice_id": inv["id"], "reason": "Không vừa ý",
                                          "items": [{"product_id": pk1, "quantity": 1}]}, headers=staff_h)
    assert r.status_code == 201, r.text
    assert r.json()["refund_total"] == 315_000  # 350k * 90%
    assert stock_of(client, owner_h, "PK001") == 11
    # trả quá số lượng còn lại
    r = client.post("/api/returns", json={"invoice_id": inv["id"], "reason": "x",
                                          "items": [{"product_id": pk1, "quantity": 2}]}, headers=staff_h)
    assert r.status_code == 400
    # hàng lỗi không nhập lại kho; trả hết: tổng hoàn đúng bằng tiền khách trả
    r = client.post("/api/returns", json={"invoice_id": inv["id"], "reason": "Lỗi", "items": [
        {"product_id": pk1, "quantity": 1, "restock": False}, {"product_id": pk3, "quantity": 1}]}, headers=staff_h)
    assert r.status_code == 201
    assert 315_000 + r.json()["refund_total"] == 801_000
    assert stock_of(client, owner_h, "PK001") == 11 and stock_of(client, owner_h, "PK003") == 50
    # báo cáo: doanh thu thuần = 0, không hủy được hóa đơn đã trả hàng
    s = client.get("/api/reports/revenue", headers=owner_h).json()["summary"]
    assert s["gross_sales"] == 801_000 and s["refunds"] == 801_000 and s["revenue"] == 0
    assert client.post(f"/api/invoices/{inv['id']}/cancel", json={"reason": "x"}, headers=owner_h).status_code == 400


def test_return_only_within_deadline(client, owner_h, staff_h, db):
    pk1 = product_id(client, owner_h, "PK001")
    inv = sell(client, owner_h, [{"product_id": pk1, "quantity": 1}])
    row = db.get(Invoice, inv["id"])
    row.created_at = now() - timedelta(hours=25)
    db.commit()
    r = client.post("/api/returns", json={"invoice_id": inv["id"], "reason": "x",
                                          "items": [{"product_id": pk1, "quantity": 1}]}, headers=staff_h)
    assert r.status_code == 400 and "quá thời hạn đổi trả 24 giờ" in r.json()["detail"]
    client.put("/api/business-settings", json={"values": {"RETURN_HOURS": 48}}, headers=owner_h)
    r = client.post("/api/returns", json={"invoice_id": inv["id"], "reason": "x",
                                          "items": [{"product_id": pk1, "quantity": 1}]}, headers=staff_h)
    assert r.status_code == 201


# ---------------- Bảo hành ----------------
def test_warranty_ticket_flow(client, owner_h, staff_h):
    pid, _ = make_phone(client, owner_h)
    inv = sell(client, staff_h, [{"product_id": pid, "quantity": 1, "serials": ["IMEI-111"]}])
    # khách chỉ mang máy: tra theo IMEI, tự gắn hóa đơn
    r = client.post("/api/warranty", json={"product_id": pid, "serial": "imei-111", "issue": "Không lên nguồn"},
                    headers=staff_h)
    assert r.status_code == 201, r.text
    t = r.json()
    assert t["invoice_code"] == inv["code"] and t["in_warranty"] and t["status"] == "received"
    assert client.put(f"/api/warranty/{t['id']}", json={"status": "received"}, headers=staff_h).status_code == 400
    r = client.put(f"/api/warranty/{t['id']}", json={"status": "processing", "note": "Gửi hãng"}, headers=staff_h)
    assert r.json()["status"] == "processing"
    r = client.put(f"/api/warranty/{t['id']}", json={"status": "done", "note": "Đã thay main"}, headers=owner_h)
    assert r.json()["completed_at"] and len(r.json()["history"]) == 3
    assert client.put(f"/api/warranty/{t['id']}", json={"status": "processing"}, headers=staff_h).status_code == 400
    # serial không thuộc hóa đơn
    r = client.post("/api/warranty", json={"invoice_id": inv["id"], "product_id": pid, "serial": "IMEI-222",
                                           "issue": "x"}, headers=staff_h)
    assert r.status_code == 400


# ---------------- Phiếu nhập nháp, hủy phiếu nhập, nhà cung cấp ----------------
def test_cashier_draft_import_confirmed_by_owner(client, owner_h, staff_h):
    pk1 = product_id(client, owner_h, "PK001")
    s = client.post("/api/suppliers", json={"name": "NCC Sài Gòn"}, headers=owner_h).json()
    assert s["code"].startswith("NCC")
    assert [x["name"] for x in client.get("/api/suppliers", headers=staff_h).json()] == ["NCC Sài Gòn"]
    r = client.post("/api/imports/drafts", json={"supplier_id": s["id"], "items": [{"product_id": pk1, "quantity": 5}]},
                    headers=staff_h)
    assert r.status_code == 201, r.text
    draft = r.json()
    assert draft["status"] == "draft" and stock_of(client, owner_h, "PK001") == 12
    assert client.post(f"/api/imports/{draft['id']}/confirm", json={"items": [
        {"product_id": pk1, "quantity": 5, "unit_cost": 200_000}]}, headers=staff_h).status_code == 403
    assert client.get("/api/invoices/pending-count", headers=owner_h).json()["draft_imports"] == 1
    r = client.post(f"/api/imports/{draft['id']}/confirm", json={"supplier_id": s["id"], "items": [
        {"product_id": pk1, "quantity": 6, "unit_cost": 200_000}]}, headers=owner_h)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "completed" and r.json()["supplier"] == "NCC Sài Gòn"
    assert stock_of(client, owner_h, "PK001") == 18
    staff_view = client.get(f"/api/imports/{draft['id']}", headers=staff_h).json()
    assert staff_view["total"] is None and staff_view["items"][0]["unit_cost"] is None  # thu ngân không thấy giá nhập
    # hủy phiếu đã nhập: trừ lại kho
    assert client.post(f"/api/imports/{draft['id']}/cancel", json={"reason": "x"}, headers=staff_h).status_code == 403
    r = client.post(f"/api/imports/{draft['id']}/cancel", json={"reason": "Nhập trùng"}, headers=owner_h)
    assert r.json()["status"] == "cancelled" and stock_of(client, owner_h, "PK001") == 12


def test_cannot_cancel_import_after_goods_sold(client, owner_h):
    pk1 = product_id(client, owner_h, "PK001")
    r = client.post("/api/imports", json={"items": [{"product_id": pk1, "quantity": 3, "unit_cost": 200_000}]},
                    headers=owner_h).json()
    sell(client, owner_h, [{"product_id": pk1, "quantity": 14}])  # 15 -> 1
    res = client.post(f"/api/imports/{r['id']}/cancel", json={"reason": "x"}, headers=owner_h)
    assert res.status_code == 400 and "đã bán bớt" in res.json()["detail"]


# ---------------- Thẻ kho, báo cáo tồn kho, PDF, email ----------------
def test_stock_card_and_inventory_report(client, owner_h):
    pk1 = product_id(client, owner_h, "PK001")
    client.post("/api/imports", json={"items": [{"product_id": pk1, "quantity": 3, "unit_cost": 200_000}]},
                headers=owner_h)
    sell(client, owner_h, [{"product_id": pk1, "quantity": 5}])
    card = client.get("/api/reports/stock-card", params={"product_id": pk1}, headers=owner_h).json()
    assert card["total_in"] == 3 and card["total_out"] == 5 and card["closing"] == 10
    rep = client.get("/api/reports/inventory", headers=owner_h).json()
    assert rep["summary"]["value_at_cost"] == 10 * 200_000 + 50 * 95_000
    assert [i["code"] for i in client.get("/api/reports/inventory", params={"stock": "out"},
                                          headers=owner_h).json()["items"]] == ["PK002"]
    for fmt in ("csv", "xlsx", "pdf"):
        assert client.get("/api/reports/export/inventory", params={"format": fmt}, headers=owner_h).status_code == 200


def test_invoice_pdf_and_email(client, staff_h, monkeypatch, db):
    pk1 = product_id(client, staff_h, "PK001")
    inv = sell(client, staff_h, [{"product_id": pk1, "quantity": 1}], customer_id=customer_id(db))
    r = client.get(f"/api/invoices/{inv['id']}/pdf", headers=staff_h)
    assert r.status_code == 200 and r.content.startswith(b"%PDF")
    sent = []
    monkeypatch.setattr(invoices_router, "mail_configured", lambda: True)
    monkeypatch.setattr(invoices_router, "send_mail", lambda to, subject, text, attachments: sent.append((to, attachments)))
    assert client.post(f"/api/invoices/{inv['id']}/email", json={}, headers=staff_h).status_code == 400  # khách chưa có email
    r = client.post(f"/api/invoices/{inv['id']}/email", json={"to": "khach@example.com"}, headers=staff_h)
    assert r.status_code == 200
    assert sent[0][0] == "khach@example.com" and sent[0][1][0][1].startswith(b"%PDF")
