from __future__ import annotations

import asyncio
import json
import re
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from auth.deps import get_current_user_id
from auth.service import get_owned_conversation, set_conversation_title_if_default, touch_conversation
from chat_agent import iter_raw_ai_text_chunks, iter_thinking_answer_deltas
from db.session import get_session

router = APIRouter(tags=["chat"])

_TID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_ANS = "答案："


class ChatIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    conversation_id: int


@router.post("/api/chat/stream")
async def chat_stream(
    request: Request,
    body: ChatIn,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    conv = await get_owned_conversation(session, user_id, body.conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="会话不存在")
    tid = conv.thread_id.strip()
    if not _TID.fullmatch(tid):
        raise HTTPException(status_code=400, detail="thread_id 异常")
    msg = body.message.strip()
    agent = request.app.state.agent

    await set_conversation_title_if_default(session, conv.id, msg)
    await touch_conversation(session, conv.id)

    async def gen() -> AsyncIterator[str]:
        try:
            chunks = await asyncio.to_thread(lambda: list(iter_raw_ai_text_chunks(agent, msg, tid)))
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
            return
        full = "".join(chunks)
        meta = {
            "thread_id": tid,
            "conversation_id": conv.id,
            "no_answer_marker": _ANS not in full,
        }
        yield f"event: meta\ndata: {json.dumps(meta, ensure_ascii=False)}\n\n"
        try:
            for phase, d in iter_thinking_answer_deltas(iter(chunks)):
                if d:
                    yield f"event: {phase}\ndata: {json.dumps({'delta': d}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
            return
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        gen(),
        media_type="text/event-stream; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
