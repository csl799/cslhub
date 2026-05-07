"""FastAPI 异步应用：认证、会话、SSE 聊天。"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from chat_agent import create_chat_agent
from database import checkpoint_lifecycle
from db.session import dispose_engine, init_models
from web.routers import auth, chat, conversations

load_dotenv()

_STATIC = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    cm = checkpoint_lifecycle()
    checkpointer = await asyncio.to_thread(cm.__enter__)
    app.state._cm = cm
    app.state.agent = create_chat_agent(checkpointer)
    await init_models()
    yield
    await dispose_engine()

    def _exit_cm() -> None:
        cm.__exit__(None, None, None)

    await asyncio.to_thread(_exit_cm)


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(chat.router)


@app.get("/")
async def page() -> FileResponse:
    p = _STATIC / "index.html"
    if not p.is_file():
        raise HTTPException(404)
    return FileResponse(p, media_type="text/html; charset=utf-8")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("web.app:app", host="127.0.0.1", port=8000, reload=False)
