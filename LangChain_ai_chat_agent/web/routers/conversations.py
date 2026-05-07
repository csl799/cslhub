from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.deps import get_current_user_id
from auth.schemas import ConversationCreateOut, ConversationOut
from auth.service import create_conversation, list_conversations
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
