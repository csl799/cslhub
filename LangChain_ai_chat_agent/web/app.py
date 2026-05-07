"""FastAPI：SSE 流式聊天 + 静态页。"""

from __future__ import annotations

import json
import re
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from chat_agent import create_chat_agent, iter_raw_ai_text_chunks, iter_thinking_answer_deltas
from database import checkpoint_lifecycle

load_dotenv()

_STATIC = Path(__file__).resolve().parent / "static"
_TID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_ANS = "答案："


class ChatIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    thread_id: str | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    cm = checkpoint_lifecycle()
    app.state._cm = cm
    app.state.agent = create_chat_agent(cm.__enter__())
    yield
    cm.__exit__(None, None, None)


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.post("/api/chat/stream")
def chat_stream(body: ChatIn) -> StreamingResponse:
    tid = (body.thread_id or "").strip() or str(uuid.uuid4())
    if not _TID.fullmatch(tid):
        raise HTTPException(400, "thread_id 格式无效")
    msg = body.message.strip()
    agent = app.state.agent

    def gen():
        try:
            chunks = list(iter_raw_ai_text_chunks(agent, msg, tid))
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
            return
        full = "".join(chunks)
        yield f"event: meta\ndata: {json.dumps({'thread_id': tid, 'no_answer_marker': _ANS not in full}, ensure_ascii=False)}\n\n"
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


@app.get("/")
def page() -> FileResponse:
    p = _STATIC / "index.html"
    if not p.is_file():
        raise HTTPException(404)
    return FileResponse(p, media_type="text/html; charset=utf-8")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
