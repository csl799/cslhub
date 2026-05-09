from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession

from auth.deps import get_current_user_id
from auth.schemas import ConversationCreateOut, ConversationOut
from auth.service import create_conversation, get_owned_conversation, list_conversations
from chat_agent import get_thread_history_messages
from db.session import get_session

router = APIRouter(tags=["conversations"])


@router.get("/api/conversations", response_model=list[ConversationOut])
async def list_all(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> list[ConversationOut]:
    rows = await list_conversations(session, user_id)
    return [ConversationOut.model_validate(x) for x in rows]


@router.post("/api/conversations", response_model=ConversationCreateOut)
async def create_new(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> ConversationCreateOut:
    c = await create_conversation(session, user_id)
    return ConversationCreateOut(id=c.id, thread_id=c.thread_id, title=c.title)


@router.get("/api/conversations/{conversation_id}/messages")
async def conversation_messages(
    request: Request,
    conversation_id: int = Path(..., ge=1),
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> dict[str, list[dict[str, str]]]:
    conv = await get_owned_conversation(session, user_id, conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="会话不存在")
    agent = request.app.state.agent
    return {"messages": get_thread_history_messages(agent, conv.thread_id)}
