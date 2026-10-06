from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.ai import assistant, history, service
from app.ai.client import GeminiClient, get_ai_client
from app.config import settings
from app.database import get_db
from app.models import ChatSession, User
from app.schemas import AIReportIn, ChatIn, QuestionIn, SessionRename
from app.security import ALL_STAFF, ANY_ROLE, MANAGERS

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/status")
def ai_status(client: GeminiClient = Depends(get_ai_client), _: User = Depends(ANY_ROLE)):
    """model = model đang dùng được (None nếu mọi model đều đang hết lượt); models = tình trạng từng model."""
    info = client.status() if client.enabled else {"active_model": None, "models": []}
    return {"enabled": client.enabled, "model": info["active_model"], "models": info["models"],
            "advisor_prompt_version": settings.ADVISOR_PROMPT_VERSION}


def _session_for(db: Session, user: User, kind: str, session_id: int | None, text: str) -> ChatSession:
    try:
        return history.get_or_create(db, user, kind, session_id, text)
    except history.SessionNotFound:
        raise HTTPException(404, "Không tìm thấy cuộc trò chuyện")


@router.post("/assistant")
def assistant_chat(data: ChatIn, db: Session = Depends(get_db), client: GeminiClient = Depends(get_ai_client),
                   user: User = Depends(ALL_STAFF)):
    """Trợ lý đa năng: AI tự gọi công cụ tra cứu phù hợp với vai trò người dùng."""
    session = _session_for(db, user, "assistant", data.session_id, data.message)
    result = assistant.reply(db, client, user, data.message, history.recent_history(session, 10))
    meta = {k: result.get(k) for k in ("suggestions", "tools", "source", "warning", "latency_ms", "model", "period", "period_label")}
    reply = history.append_turn(db, session, data.message, result["answer"], meta)
    db.commit()
    return {**result, "session_id": session.id, "session_title": session.title, "message_id": reply.id}


@router.post("/advisor")
def advisor(data: ChatIn, version: str | None = Query(None, pattern="^v[123]$"),
            db: Session = Depends(get_db), client: GeminiClient = Depends(get_ai_client),
            user: User = Depends(ALL_STAFF)):
    session = _session_for(db, user, "advisor", data.session_id, data.message)
    result = service.advise(db, client, data.message, history.recent_history(session),
                            version or settings.ADVISOR_PROMPT_VERSION)
    meta = {k: result.get(k) for k in ("suggestions", "removed", "source", "version", "warning", "latency_ms", "model")}
    reply = history.append_turn(db, session, data.message, result["answer"], meta)
    db.commit()
    return {**result, "session_id": session.id, "session_title": session.title, "message_id": reply.id}


@router.post("/report")
def ai_report(data: AIReportIn, db: Session = Depends(get_db), client: GeminiClient = Depends(get_ai_client),
              _: User = Depends(MANAGERS)):
    return service.sales_report(db, client, data.date_from, data.date_to)


@router.post("/ask")
def ask(data: QuestionIn, db: Session = Depends(get_db), client: GeminiClient = Depends(get_ai_client),
        user: User = Depends(MANAGERS)):
    session = _session_for(db, user, "ask", data.session_id, data.question)
    result = service.ask_data(db, client, data.question)
    meta = {k: result.get(k) for k in ("period", "period_label", "source", "warning", "latency_ms", "model")}
    reply = history.append_turn(db, session, data.question, result["answer"], meta)
    db.commit()
    return {**result, "session_id": session.id, "session_title": session.title, "message_id": reply.id}


# ---------------- Lịch sử tra cứu ----------------
def _check_kind(kind: str, user: User) -> None:
    if kind not in history.KINDS:
        raise HTTPException(400, "Loại lịch sử không hợp lệ")
    if kind == "ask" and user.role != "owner":
        raise HTTPException(403, "Bạn không có quyền thực hiện chức năng này")


def _own_session(db: Session, user: User, session_id: int) -> ChatSession:
    try:
        return history.get_session(db, user, session_id)
    except history.SessionNotFound:
        raise HTTPException(404, "Không tìm thấy cuộc trò chuyện")


@router.get("/sessions")
def list_sessions(kind: str = "advisor", q: str | None = None, db: Session = Depends(get_db),
                  user: User = Depends(ALL_STAFF)):
    _check_kind(kind, user)
    return history.list_sessions(db, user, kind, q)


@router.get("/sessions/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    return history.session_detail(_own_session(db, user, session_id))


@router.patch("/sessions/{session_id}")
def rename_session(session_id: int, data: SessionRename, db: Session = Depends(get_db),
                   user: User = Depends(ALL_STAFF)):
    s = _own_session(db, user, session_id)
    s.title = history.make_title(data.title)
    db.commit()
    return {"id": s.id, "title": s.title}


@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    db.delete(_own_session(db, user, session_id))
    db.commit()
    return {"ok": True}


@router.delete("/sessions")
def clear_sessions(kind: str = "advisor", db: Session = Depends(get_db), user: User = Depends(ALL_STAFF)):
    _check_kind(kind, user)
    sessions = db.scalars(select(ChatSession).where(ChatSession.user_id == user.id, ChatSession.kind == kind)).all()
    for s in sessions:
        db.delete(s)
    db.commit()
    return {"deleted": len(sessions)}
