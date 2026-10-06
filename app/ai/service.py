"""3 chức năng AI: chatbot tư vấn sản phẩm, sinh báo cáo doanh thu, hỏi đáp dữ liệu bán hàng.

Mỗi chức năng đều có chế độ dự phòng (rule-based) khi chưa cấu hình API key hoặc khi AI lỗi,
để hệ thống vẫn hoạt động và demo được.
"""
import json
import re
import sqlite3
import unicodedata
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.ai import text_to_sql as tts
from app.ai.client import AIError, AIResult, GeminiClient
from app.ai.prompts import render_prompt
from app.models import Product, now
from app.services import reports

ADVISOR_VERSIONS = {
    # in_stock_only: chỉ gửi sản phẩm còn hàng; json: yêu cầu đầu ra JSON
    "v1": {"in_stock_only": False, "json": False},
    "v2": {"in_stock_only": False, "json": False},
    "v3": {"in_stock_only": True, "json": True},
}
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


# ---------------------------------------------------------------- tiện ích
def strip_accents(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower()).replace("đ", "d")
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def clean_input(text: str, max_len: int = 1000) -> str:
    """Loại ký tự điều khiển, cắt độ dài: giảm rủi ro chèn dữ liệu rác vào prompt."""
    return _CONTROL.sub("", text).strip()[:max_len]


def mask_phone(phone: str | None) -> str | None:
    """0901234567 -> 090****567. Dùng khi buộc phải đưa thông tin khách vào prompt."""
    if not phone:
        return phone
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 7:
        return "*" * len(digits)
    return digits[:3] + "*" * (len(digits) - 6) + digits[-3:]


def fmt_vnd(value: int) -> str:
    return f"{value:,.0f}".replace(",", ".") + " ₫"


def parse_budget(text: str) -> int | None:
    """Tìm ngân sách tối đa trong câu: 'dưới 500000', '500k', '1,5 triệu', '2tr'."""
    t = strip_accents(text).replace(",", ".")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(trieu|tr)\b", t)
    if m:
        return int(float(m.group(1)) * 1_000_000)
    m = re.search(r"(\d+(?:\.\d+)?)\s*(k|nghin|ngan)\b", t)
    if m:
        return int(float(m.group(1)) * 1_000)
    m = re.search(r"(\d{1,3}(?:\.\d{3})+|\d{5,})", t)
    if m:
        return int(m.group(1).replace(".", ""))
    return None


def extract_json(text: str) -> dict:
    """Lấy object JSON từ phản hồi AI, chấp nhận trường hợp bị bọc trong ```json ... ```."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise AIError("AI không trả về JSON", "bad_response")
        try:
            data = json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            raise AIError("JSON từ AI bị hỏng", "bad_response")
    if not isinstance(data, dict):
        raise AIError("JSON từ AI không phải object", "bad_response")
    return data


def product_table(products: list[Product]) -> str:
    lines = []
    for p in products:
        desc = (p.description or "").replace("\n", " ").replace("|", "/")[:200]
        cat = p.category.name if p.category else "-"
        lines.append(f"{p.code} | {p.name} | {cat} | {p.sale_price} | {p.stock} | {desc}")
    return "\n".join(lines) if lines else "(không có sản phẩm nào)"


def _product_dict(p: Product, reason: str = "") -> dict:
    return {"code": p.code, "name": p.name, "price": p.sale_price, "stock": p.stock, "image_url": p.image_url,
            "category": p.category.name if p.category else None, "reason": reason}


# ---------------------------------------------------------------- 1. Chatbot tư vấn
def _active_products(db: Session) -> list[Product]:
    return list(db.scalars(
        select(Product).options(joinedload(Product.category))
        .where(Product.status == "active").order_by(Product.code)
    ))


def _fallback_advise(products: list[Product], message: str) -> dict:
    """Tư vấn dự phòng: chấm điểm theo từ khóa trùng khớp + lọc ngân sách + chỉ hàng còn."""
    stop = {"toi", "can", "mua", "cho", "mot", "cai", "co", "khong", "duoi", "tren", "gia",
            "khach", "hang", "con", "va", "la", "nao", "loai", "muon", "tim", "san", "pham"}
    text = strip_accents(message)
    # Bỏ cụm ngân sách ("20 triệu", "500k", "1.500.000") khỏi từ khóa: "20" không được khớp "Sạc 20W"
    text = re.sub(r"\d+(?:[.,]\d+)*\s*(?:trieu|tr|k|nghin|ngan|dong|d|vnd)?\b", " ", text)
    stop |= {"trieu", "tr", "nghin", "ngan", "dong", "vnd", "tam", "khoang", "re", "dat"}
    words = {w for w in re.findall(r"[a-z0-9]+", text) if len(w) > 1 and w not in stop}
    budget = parse_budget(message)
    tokens = lambda t: set(re.findall(r"[a-z0-9]+", strip_accents(t or "")))  # noqa: E731
    scored = []
    for p in products:
        if p.stock <= 0 or (budget and p.sale_price > budget):
            continue
        cat, name, desc = tokens(p.category.name if p.category else ""), tokens(f"{p.name} {p.brand or ''}"), tokens(p.description)
        # Khớp nguyên từ (không khớp chuỗi con); trùng nhóm hàng nặng nhất, rồi tên / hãng, rồi mô tả
        score = sum(3 if w in cat else 2 if w in name else 1 if w in desc else 0 for w in words)
        if score:
            # Cùng điểm: ưu tiên sản phẩm giá gần ngân sách (khách đã nêu mức chi), không có ngân sách thì rẻ trước
            scored.append((score, p.sale_price if budget else -p.sale_price, p))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    picks = [s[2] for s in scored[:3]]
    if not picks:
        answer = "Hiện chưa tìm thấy sản phẩm còn hàng phù hợp với nhu cầu này. Bạn có thể mô tả rõ hơn loại sản phẩm hoặc ngân sách không?"
    else:
        answer = "Dựa trên nhu cầu của bạn, mình gợi ý các sản phẩm đang còn hàng sau:"
    return {
        "answer": answer,
        "suggestions": [_product_dict(p, f"Khớp nhu cầu, giá {fmt_vnd(p.sale_price)}, còn {p.stock} sản phẩm") for p in picks],
    }


def _format_history(history: list[dict]) -> str:
    lines = []
    for turn in history[-6:]:
        role = "Khách" if turn.get("role") == "user" else "Trợ lý"
        lines.append(f"{role}: {clean_input(str(turn.get('content', '')), 300)}")
    return "\n".join(lines) or "(chưa có)"


def advise(db: Session, client: GeminiClient, message: str, history: list[dict] | None = None,
           version: str = "v3") -> dict:
    message = clean_input(message)
    cfg = ADVISOR_VERSIONS.get(version, ADVISOR_VERSIONS["v3"])
    products = _active_products(db)
    by_code = {p.code.upper(): p for p in products}
    sent = [p for p in products if p.stock > 0] if cfg["in_stock_only"] else products

    if not client.enabled:
        return {**_fallback_advise(products, message), "source": "fallback", "version": version,
                "warning": "Chưa cấu hình GEMINI_API_KEY - đang dùng tư vấn dự phòng theo từ khóa."}

    system, user = render_prompt(
        f"product_advisor_{version}", message=message, product_table=product_table(sent),
        history=_format_history(history or []),
    )
    try:
        result = client.generate(system, user, json_mode=cfg["json"], temperature=0.2,
                                 feature=f"advisor_{version}")
    except AIError as e:
        return {**_fallback_advise(products, message), "source": "fallback", "version": version,
                "warning": f"{e} - chuyển sang tư vấn dự phòng."}

    # Chuẩn hóa đầu ra về (answer, [(code, reason)])
    raw_suggestions: list[tuple[str, str]] = []
    if cfg["json"]:
        try:
            data = extract_json(result.text)
            answer = str(data.get("answer", "")).strip()
            for s in data.get("suggestions") or []:
                if isinstance(s, dict) and s.get("code"):
                    raw_suggestions.append((str(s["code"]).upper().strip(), str(s.get("reason", ""))))
        except AIError:
            answer = result.text  # phản hồi sai định dạng: vẫn hiển thị văn bản, tự dò mã sản phẩm
            raw_suggestions = _codes_in_text(result.text, by_code)
    else:
        answer = result.text
        raw_suggestions = _codes_in_text(result.text, by_code)

    # Hậu kiểm: chỉ giữ sản phẩm tồn tại, đang bán, còn hàng
    suggestions, removed = [], []
    for code, reason in raw_suggestions[:3]:
        p = by_code.get(code)
        if p is None or p.stock <= 0:
            removed.append(code)
        else:
            suggestions.append(_product_dict(p, reason))

    warning = None
    if removed:
        warning = f"Đã loại bỏ gợi ý không hợp lệ hoặc hết hàng: {', '.join(removed)}"
    return {"answer": answer or "Xin lỗi, mình chưa có câu trả lời phù hợp.", "suggestions": suggestions,
            "removed": removed, "source": "ai", "version": version, "warning": warning,
            "latency_ms": result.latency_ms, "model": result.model}


def _codes_in_text(text: str, by_code: dict[str, Product]) -> list[tuple[str, str]]:
    upper = text.upper()
    found = [(code, upper.find(code)) for code in by_code if re.search(rf"\b{re.escape(code)}\b", upper)]
    found.sort(key=lambda x: x[1])
    return [(code, "") for code, _ in found]


# ---------------------------------------------------------------- 2. Báo cáo doanh thu
def _fallback_report(ctx: dict) -> str:
    s, prev = ctx["summary"], ctx["previous_period_summary"]
    lines = [f"## Tổng quan",
             f"- Kỳ: {ctx['period']['from']} → {ctx['period']['to']} ({ctx['period']['days']} ngày)",
             f"- Doanh thu: **{fmt_vnd(s['revenue'])}** từ {s['invoice_count']} hóa đơn",
             f"- Lãi gộp ước tính: {fmt_vnd(s['gross_profit'])}"]
    if prev["revenue"]:
        growth = (s["revenue"] - prev["revenue"]) / prev["revenue"] * 100
        lines.append(f"- So với kỳ trước ({fmt_vnd(prev['revenue'])}): {growth:+.1f}%")
    lines.append("\n## Điểm nổi bật")
    for c in ctx["revenue_by_category"][:3]:
        lines.append(f"- Nhóm **{c['category']}**: {fmt_vnd(c['revenue'])} ({c['quantity']} sản phẩm)")
    lines.append("\n## Sản phẩm cần chú ý")
    for p in ctx["top_products"][:3]:
        lines.append(f"- Bán chạy: {p['name']} ({p['quantity']} sp, còn {p['stock']})")
    for p in ctx["slow_products"][:3]:
        lines.append(f"- Bán chậm: {p['name']} (bán {p['quantity']}, tồn {p['stock']})")
    lines.append("\n## Khuyến nghị nhập hàng")
    if ctx["low_stock"]:
        for p in ctx["low_stock"][:5]:
            lines.append(f"- Nhập thêm **{p['name']}** (tồn {p['stock']}, mức tối thiểu {p['min_stock']})")
    else:
        lines.append("- Tồn kho hiện đủ, chưa cần nhập gấp.")
    lines.append("\n## Hành động đề xuất")
    lines.append("- Cân nhắc khuyến mãi/đẩy bán nhóm sản phẩm bán chậm.")
    lines.append("- Ưu tiên nhập các sản phẩm bán chạy sắp hết hàng.")
    lines.append("\n> *Báo cáo tự động theo mẫu (chưa cấu hình AI hoặc AI tạm thời lỗi).*")
    return "\n".join(lines)


def sales_report(db: Session, client: GeminiClient, date_from: str | None, date_to: str | None) -> dict:
    start, end = reports.parse_range(date_from, date_to)
    ctx = reports.ai_data_context(db, start, end)
    base = {"data": ctx, "period": ctx["period"]}
    if ctx["summary"]["invoice_count"] == 0:
        return {**base, "markdown": "## Tổng quan\nKhông có hóa đơn nào trong kỳ đã chọn, chưa đủ dữ liệu để phân tích.",
                "source": "fallback", "warning": None}
    if not client.enabled:
        return {**base, "markdown": _fallback_report(ctx), "source": "fallback",
                "warning": "Chưa cấu hình GEMINI_API_KEY - đang dùng báo cáo mẫu."}
    system, user = render_prompt(
        "sales_report", date_from=ctx["period"]["from"], date_to=ctx["period"]["to"],
        data_json=json.dumps(ctx, ensure_ascii=False, indent=1),
    )
    try:
        result = client.generate(system, user, temperature=0.4, feature="sales_report")
    except AIError as e:
        return {**base, "markdown": _fallback_report(ctx), "source": "fallback", "warning": str(e)}
    markdown = re.sub(r"^```(?:markdown)?\s*|\s*```$", "", result.text.strip())
    if "##" not in markdown:
        return {**base, "markdown": _fallback_report(ctx), "source": "fallback",
                "warning": "Phản hồi AI không đúng định dạng Markdown, đã dùng báo cáo mẫu."}
    return {**base, "markdown": markdown, "source": "ai", "warning": None, "latency_ms": result.latency_ms,
            "model": result.model}


# ---------------------------------------------------------------- 3. Hỏi đáp dữ liệu
def detect_period(question: str, today: date | None = None) -> tuple[date, date, str]:
    """Xác định kỳ dữ liệu từ câu hỏi. Mặc định: tháng này."""
    today = today or now().date()
    q = strip_accents(question)
    month_start = today.replace(day=1)
    if "hom qua" in q:
        d = today - timedelta(days=1)
        return d, d, "hôm qua"
    if "hom nay" in q:
        return today, today, "hôm nay"
    if "thang truoc" in q:
        last_end = month_start - timedelta(days=1)
        return last_end.replace(day=1), last_end, "tháng trước"
    if "tuan nay" in q or "7 ngay" in q or "tuan qua" in q:
        return today - timedelta(days=6), today, "7 ngày gần nhất"
    if "30 ngay" in q:
        return today - timedelta(days=29), today, "30 ngày gần nhất"
    if "quy nay" in q or "3 thang" in q:
        return today - timedelta(days=89), today, "90 ngày gần nhất"
    if "nam nay" in q:
        return today.replace(month=1, day=1), today, "năm nay"
    m = re.search(r"thang\s*(\d{1,2})(?:\D+(\d{4}))?", q)
    if m and 1 <= int(m.group(1)) <= 12:
        month, year = int(m.group(1)), int(m.group(2) or today.year)
        start = date(year, month, 1)
        end = (date(year + (month == 12), month % 12 + 1, 1) - timedelta(days=1))
        return start, min(end, today), f"tháng {month}/{year}"
    return month_start, today, "tháng này"


def _fallback_answer(question: str, ctx: dict, label: str) -> str:
    q = strip_accents(question)
    head = ""  # kỳ dữ liệu được giao diện hiển thị thành nhãn riêng dưới câu trả lời
    if "cham" in q or "hang e" in q or "ton nhieu" in q:
        rows = [f"- {p['name']}: bán {p['quantity']}, tồn {p['stock']}" for p in ctx["slow_products"][:5]]
        return head + "Các mặt hàng bán chậm nhất (còn tồn kho):\n" + "\n".join(rows or ["- Không có"])
    if "chay" in q or "nhieu nhat" in q or "top" in q:
        rows = [f"- {p['name']}: {p['quantity']} sp, {fmt_vnd(p['revenue'])}" for p in ctx["top_products"][:5]]
        return head + "Các mặt hàng bán chạy nhất:\n" + "\n".join(rows or ["- Chưa có giao dịch"])
    if "ton" in q or "het hang" in q or "nhap" in q:
        rows = [f"- {p['name']}: còn {p['stock']} (tối thiểu {p['min_stock']})" for p in ctx["low_stock"][:10]]
        return head + "Sản phẩm sắp hết / cần nhập:\n" + "\n".join(rows or ["- Tồn kho đang ổn"])
    if "nhom" in q or "danh muc" in q:
        rows = [f"- {c['category']}: {fmt_vnd(c['revenue'])}" for c in ctx["revenue_by_category"]]
        return head + "Doanh thu theo nhóm hàng:\n" + "\n".join(rows or ["- Chưa có giao dịch"])
    s = ctx["summary"]
    return head + (f"- Doanh thu: {fmt_vnd(s['revenue'])}\n- Số hóa đơn: {s['invoice_count']}\n"
                   f"- Lãi gộp ước tính: {fmt_vnd(s['gross_profit'])}")


def _ask_from_context(db: Session, client: GeminiClient, question: str) -> dict:
    """Cách cũ, dùng khi CSDL không phải SQLite: hệ thống tự tổng hợp số liệu theo kỳ rồi gửi cho AI."""
    d_from, d_to, label = detect_period(question)
    start, end = reports.parse_range(d_from, d_to)
    ctx = reports.ai_data_context(db, start, end)
    base = {"period": ctx["period"], "period_label": label}
    if not client.enabled:
        return {**base, "answer": _fallback_answer(question, ctx, label), "source": "fallback",
                "warning": "Chưa cấu hình GEMINI_API_KEY - đang trả lời theo mẫu."}
    system, user = render_prompt(
        "sales_qa_context", question=question, date_from=ctx["period"]["from"], date_to=ctx["period"]["to"],
        data_json=json.dumps(ctx, ensure_ascii=False, indent=1),
    )
    try:
        result = client.generate(system, user, temperature=0.2, feature="sales_qa")
    except AIError as e:
        return {**base, "answer": _fallback_answer(question, ctx, label), "source": "fallback", "warning": str(e)}
    return {**base, "answer": result.text, "source": "ai", "warning": None, "latency_ms": result.latency_ms,
            "model": result.model}


# ---------------------------------------------------------------- Hỏi đáp bằng text-to-SQL (SRS 6.5)
# Câu SQL mẫu cho chế độ dự phòng (chưa có khóa API): vẫn đi qua đúng bộ kiểm tra và kết nối chỉ đọc.
_FALLBACK_SQL = [
    (("cham", "hang e", "ton nhieu"), "Các mặt hàng bán chậm nhất (còn tồn kho)",
     "SELECT p.name AS san_pham, p.stock_qty AS ton_kho, COALESCE(SUM(s.quantity), 0) AS da_ban\n"
     "FROM v_ai_products p\nLEFT JOIN v_ai_sales_lines s ON s.sku = p.sku AND s.sold_date BETWEEN '{f}' AND '{t}'\n"
     "WHERE p.stock_qty > 0\nGROUP BY p.sku, p.name, p.stock_qty\nORDER BY da_ban ASC, ton_kho DESC\nLIMIT 10"),
    (("chay", "nhieu nhat", "top"), "Các mặt hàng bán chạy nhất",
     "SELECT product_name AS san_pham, SUM(quantity) AS so_luong, SUM(net_revenue) AS doanh_thu\n"
     "FROM v_ai_sales_lines\nWHERE sold_date BETWEEN '{f}' AND '{t}'\nGROUP BY sku, product_name\n"
     "ORDER BY so_luong DESC, doanh_thu DESC\nLIMIT 10"),
    (("het hang", "sap het", "nhap", "ton kho"), "Sản phẩm sắp hết hoặc cần nhập thêm",
     "SELECT name AS san_pham, stock_qty AS ton_kho, min_stock_level AS ton_toi_thieu, sold_30d AS ban_30_ngay\n"
     "FROM v_ai_inventory\nWHERE stock_qty <= min_stock_level\nORDER BY stock_qty ASC, sold_30d DESC"),
    (("nhom", "danh muc", "loai hang"), "Doanh thu theo nhóm hàng",
     "SELECT category AS nhom_hang, SUM(quantity) AS so_luong, SUM(net_revenue) AS doanh_thu\n"
     "FROM v_ai_sales_lines\nWHERE sold_date BETWEEN '{f}' AND '{t}'\nGROUP BY category\nORDER BY doanh_thu DESC"),
    (("khung gio", "cao diem", "theo gio", "gio nao"), "Doanh thu theo khung giờ",
     "SELECT sold_hour AS gio, COUNT(DISTINCT invoice_code) AS so_hoa_don, SUM(net_revenue) AS doanh_thu\n"
     "FROM v_ai_sales_lines\nWHERE sold_date BETWEEN '{f}' AND '{t}'\nGROUP BY sold_hour\nORDER BY doanh_thu DESC"),
    ((), "Tổng hợp doanh thu",
     "SELECT COUNT(DISTINCT invoice_code) AS so_hoa_don, COALESCE(SUM(net_revenue), 0) AS doanh_thu,\n"
     "       COALESCE(SUM(net_revenue - vat_amount - cost_amount), 0) AS lai_gop\n"
     "FROM v_ai_sales_lines\nWHERE sold_date BETWEEN '{f}' AND '{t}'"),
]
_MONEY_COLS = ("doanh_thu", "lai_gop", "revenue", "net_revenue", "gross_profit", "stock_value", "refund", "total",
               "price", "cost", "amount", "tien", "gia")
_COL_VI = {"san_pham": "Sản phẩm", "ton_kho": "tồn", "da_ban": "đã bán", "so_luong": "số lượng", "doanh_thu": "doanh thu",
           "ton_toi_thieu": "tối thiểu", "ban_30_ngay": "bán 30 ngày", "nhom_hang": "Nhóm", "gio": "Giờ",
           "so_hoa_don": "số hóa đơn", "lai_gop": "lãi gộp"}


def _fmt_cell(col: str, value) -> str:
    if isinstance(value, (int, float)) and any(k in col.lower() for k in _MONEY_COLS):
        return fmt_vnd(int(value))
    if isinstance(value, float):
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "" if value is None else str(value)


def format_rows(title: str, columns: list[str], rows: list[list], limit: int = 10) -> str:
    """Viết câu trả lời từ bảng kết quả khi không có AI diễn giải (chế độ dự phòng hoặc AI lỗi ở bước 5)."""
    if not rows:
        return f"{title}: không có dữ liệu phù hợp trong kỳ này."
    if len(rows) == 1 and len(columns) > 1:
        return f"{title}:\n" + "\n".join(f"- {_COL_VI.get(c, c).capitalize()}: {_fmt_cell(c, v)}" for c, v in zip(columns, rows[0]))
    lines = []
    for r in rows[:limit]:
        head = _fmt_cell(columns[0], r[0])
        rest = ", ".join(f"{_COL_VI.get(c, c)} {_fmt_cell(c, v)}" for c, v in zip(columns[1:], r[1:]))
        lines.append(f"- {head}: {rest}" if rest else f"- {head}")
    more = f"\n- ... và {len(rows) - limit} dòng khác (xem bảng kết quả)" if len(rows) > limit else ""
    return f"{title}:\n" + "\n".join(lines) + more


def _table(q: tts.QueryResult) -> dict:
    return {"sql": q.sql, "columns": q.columns, "rows": q.rows, "row_count": len(q.rows), "truncated": q.truncated}


def _ask_fallback(db: Session, question: str, warning: str) -> dict:
    d_from, d_to, label = detect_period(question)
    q = strip_accents(question)
    title, sql = next((t, s) for keys, t, s in _FALLBACK_SQL if not keys or any(k in q for k in keys))
    res = tts.run_sql(db, sql.format(f=d_from.isoformat(), t=d_to.isoformat()))
    return {**_table(res), "answer": format_rows(title, res.columns, res.rows), "source": "fallback", "warning": warning,
            "period": {"from": d_from.isoformat(), "to": d_to.isoformat(), "days": (d_to - d_from).days + 1},
            "period_label": label}


def _gen_sql(client: GeminiClient, question: str, today: date, hint: str, error_block: str = "") -> tuple[dict, AIResult]:
    system, user = render_prompt("sales_sql", schema=tts.VIEW_SCHEMA, today=today.isoformat(), question=question,
                                 period_hint=hint, error_block=error_block)
    result = client.generate(system, user, json_mode=True, temperature=0.0, feature="sales_sql")
    return extract_json(result.text), result


def ask_data(db: Session, client: GeminiClient, question: str) -> dict:
    """UC-47: AI sinh SQL trên view v_ai_*, hệ thống kiểm tra, chạy chỉ đọc, rồi AI diễn giải kết quả."""
    question = clean_input(question, 500)
    if db.get_bind().dialect.name != "sqlite":
        return _ask_from_context(db, client, question)
    if not client.enabled:
        return _ask_fallback(db, question, "Chưa cấu hình GEMINI_API_KEY - đang dùng câu truy vấn mẫu theo từ khóa.")

    today = now().date()
    d_from, d_to, label = detect_period(question)
    hint = f"Gợi ý kỳ dữ liệu: {label} ({d_from.isoformat()} đến {d_to.isoformat()})."
    latency, retries, model = 0, 0, client.model

    # Bước 2: AI sinh SQL
    try:
        data, r = _gen_sql(client, question, today, hint)
    except AIError as e:
        status = "invalid_format" if e.kind == "bad_response" else None
        out = _ask_fallback(db, question, f"AI lỗi khi sinh truy vấn ({e}); đang dùng câu truy vấn mẫu.")
        return {**out, **({"status": status} if status else {})}
    latency, model = r.latency_ms or 0, r.model
    sql = data.get("sql")
    if not sql:  # AI từ chối hợp lệ: hỏi thông tin cá nhân, ngoài phạm vi...
        reason = str(data.get("reason") or "Câu hỏi nằm ngoài phạm vi dữ liệu bán hàng.")
        return {"answer": f"Mình không trả lời được câu này bằng dữ liệu hệ thống: {reason}\n\n"
                          "Thông tin cá nhân của khách hàng xem tại màn hình Khách hàng.",
                "sql": None, "source": "ai", "warning": None, "latency_ms": latency, "model": model}

    # Bước 3, 4: kiểm tra và chạy; lỗi cú pháp cho AI sửa đúng một lần (FR-AIQ-08)
    res = None
    for attempt in range(2):
        try:
            res = tts.run_sql(db, sql)
            break
        except tts.SQLRejected as e:
            return {"answer": f"Câu hỏi này cần truy vấn ngoài phạm vi cho phép nên hệ thống không chạy ({e}). "
                              "Bạn thử diễn đạt lại, ví dụ hỏi về doanh thu, sản phẩm, tồn kho hoặc nhập hàng.",
                    "sql": sql, "source": "ai", "status": "rejected_sql", "warning": str(e),
                    "latency_ms": latency, "model": model, "retry_count": retries}
        except tts.SQLTimeout as e:
            return {"answer": "Truy vấn chạy quá lâu nên đã dừng. Bạn thử thu hẹp kỳ dữ liệu hoặc hỏi cụ thể hơn.",
                    "sql": sql, "source": "fallback", "status": "timeout", "warning": str(e),
                    "latency_ms": latency, "model": model, "retry_count": retries}
        except sqlite3.Error as e:
            if attempt == 1:
                return {"answer": "AI chưa viết được câu truy vấn đúng cho câu hỏi này. Bạn thử diễn đạt lại rõ hơn.",
                        "sql": sql, "source": "fallback", "status": "error", "warning": f"Lỗi SQL: {e}",
                        "latency_ms": latency, "model": model, "retry_count": retries}
            retries = 1
            err = f"Câu SQL trước bị lỗi khi chạy:\n```sql\n{sql}\n```\nThông báo lỗi: {e}\nHãy sửa lại."
            try:
                data, r = _gen_sql(client, question, today, hint, err)
            except AIError as ae:
                return {"answer": "AI không sửa được câu truy vấn. Bạn thử hỏi lại sau.", "sql": sql,
                        "source": "fallback", "warning": str(ae), "latency_ms": latency, "model": model,
                        "retry_count": retries}
            latency += r.latency_ms or 0
            sql = data.get("sql") or ""

    table = _table(res)
    # Bước 5: AI diễn giải kết quả (không có thông tin cá nhân trong view)
    rows_json = json.dumps([dict(zip(res.columns, row)) for row in res.rows], ensure_ascii=False, default=str)
    system, user = render_prompt("sales_qa", question=question, today=today.isoformat(), sql=res.sql,
                                 row_count=len(res.rows), rows_json=rows_json)
    try:
        r = client.generate(system, user, temperature=0.2, feature="sales_qa")
    except AIError as e:
        return {**table, "answer": format_rows("Kết quả truy vấn", res.columns, res.rows), "source": "fallback",
                "warning": f"AI chưa diễn giải được kết quả ({e}), đang hiển thị kết quả thô.",
                "latency_ms": latency, "model": model, "retry_count": retries}
    return {**table, "answer": r.text, "source": "ai", "warning": None, "latency_ms": latency + (r.latency_ms or 0),
            "model": r.model, "retry_count": retries}
