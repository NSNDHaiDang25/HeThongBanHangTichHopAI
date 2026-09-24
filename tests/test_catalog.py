"""Test sản phẩm: nhập tên nhóm hàng tự do khi tạo / sửa sản phẩm."""
from tests.helpers import product_id


def categories(client, h):
    return {c["name"]: c["id"] for c in client.get("/api/categories", headers=h).json()}


def new_product(**kw):
    return {"code": "NEW01", "name": "Cáp sạc USB-C", "sale_price": 90_000, **kw}


def test_create_product_with_new_category_name(client, owner_h):
    r = client.post("/api/products", json=new_product(category_name="  Cáp   sạc "), headers=owner_h)
    assert r.status_code == 201, r.text
    cats = categories(client, owner_h)
    assert "Cáp sạc" in cats
    assert r.json()["category_id"] == cats["Cáp sạc"]
    assert r.json()["category_name"] == "Cáp sạc"


def test_category_name_reuses_existing_ignoring_case(client, owner_h):
    before = categories(client, owner_h)
    r = client.post("/api/products", json=new_product(category_name="PHỤ KIỆN"), headers=owner_h)
    assert r.status_code == 201, r.text
    assert r.json()["category_id"] == before["Phụ kiện"]
    assert categories(client, owner_h) == before


def test_update_product_category_name(client, owner_h):
    pk1 = product_id(client, owner_h, "PK001")
    r = client.put(f"/api/products/{pk1}", json={"category_name": "Tai nghe"}, headers=owner_h)
    assert r.status_code == 200, r.text
    assert r.json()["category_name"] == "Tai nghe"
    r = client.put(f"/api/products/{pk1}", json={"category_name": ""}, headers=owner_h)
    assert r.json()["category_id"] is None


def test_failed_product_save_does_not_leave_new_category(client, owner_h):
    before = categories(client, owner_h)
    r = client.post("/api/products", json=new_product(code="PK001", category_name="Nhóm thừa"), headers=owner_h)
    assert r.status_code == 400
    assert categories(client, owner_h) == before
