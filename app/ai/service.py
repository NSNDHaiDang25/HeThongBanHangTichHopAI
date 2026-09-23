"""3 chức năng AI: chatbot tư vấn sản phẩm, sinh báo cáo doanh thu, hỏi đáp dữ liệu bán hàng.

Mỗi chức năng đều có chế độ dự phòng (rule-based) khi chưa cấu hình API key hoặc khi AI lỗi,
để hệ thống vẫn hoạt động và demo được.
"""
import json
import re
import unicodedata
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.ai.client import AIError, GeminiClient
from app.ai.prompts import render_prompt
from app.models import Product
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
    words = {w for w in re.findall(r"[a-z0-9]+", strip_accents(message)) if len(w) > 1 and w not in stop}
    budget = parse_budget(message)
    scored = []
    for p in products:
        if p.stock <= 0 or (budget and p.sale_price > budget):
            continue
        hay = strip_accents(f"{p.name} {p.category.name if p.category else ''} {p.description or ''}")
        name = strip_accents(p.name)
        score = sum(2 if w in name else 1 for w in words if w in hay)
        if score:
            scored.append((score, -p.sale_price, p))
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
    today = today or date.today()
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


def ask_data(db: Session, client: GeminiClient, question: str) -> dict:
    question = clean_input(question, 500)
    d_from, d_to, label = detect_period(question)
    start, end = reports.parse_range(d_from, d_to)
    ctx = reports.ai_data_context(db, start, end)
    base = {"period": ctx["period"], "period_label": label}
    if not client.enabled:
        return {**base, "answer": _fallback_answer(question, ctx, label), "source": "fallback",
                "warning": "Chưa cấu hình GEMINI_API_KEY - đang trả lời theo mẫu."}
    system, user = render_prompt(
        "sales_qa", question=question, date_from=ctx["period"]["from"], date_to=ctx["period"]["to"],
        data_json=json.dumps(ctx, ensure_ascii=False, indent=1),
    )
    try:
        result = client.generate(system, user, temperature=0.2, feature="sales_qa")
    except AIError as e:
        return {**base, "answer": _fallback_answer(question, ctx, label), "source": "fallback", "warning": str(e)}
    return {**base, "answer": result.text, "source": "ai", "warning": None, "latency_ms": result.latency_ms,
            "model": result.model}
