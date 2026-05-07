"""构建带 MySQL checkpoint 与总结中间件的 LangChain Agent；流式与思考/答案拆分。"""

from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Any, Literal

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from langgraph.checkpoint.base import BaseCheckpointSaver

from middleware import build_message_summary_middleware
from prompts import DEFAULT_SYSTEM_PROMPT
from tools.weather import get_weather

CHAT_MODEL = os.getenv("CHAT_MODEL", "deepseek-chat").strip()

_THINK_HDR = "正在思考："
_ANS_MARK = "答案："


def create_chat_agent(checkpointer: BaseCheckpointSaver[str]) -> Any:
    return create_agent(
        model=CHAT_MODEL,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        tools=[get_weather],
        checkpointer=checkpointer,
        middleware=[build_message_summary_middleware(model=CHAT_MODEL)],
    )


def _strip_think_header(s: str) -> str:
    t = s.lstrip()
    if t.startswith(_THINK_HDR):
        return t[len(_THINK_HDR) :].lstrip("\n ")
    return t


def iter_raw_ai_text_chunks(agent: Any, user_text: str, thread_id: str) -> Iterator[str]:
    cfg = {"configurable": {"thread_id": thread_id}}
    for msg, _metadata in agent.stream(
        {"messages": [HumanMessage(content=user_text.strip())]},
        stream_mode="messages",
        config=cfg,
    ):
        if not isinstance(msg, (AIMessage, AIMessageChunk)):
            continue
        c = msg.content
        if not c:
            continue
        if isinstance(c, str):
            yield c
        elif isinstance(c, list):
            for part in c:
                if isinstance(part, dict) and part.get("type") == "text":
                    t = part.get("text") or ""
                    if t:
                        yield t
                elif isinstance(part, str) and part:
                    yield part


def iter_thinking_answer_deltas(
    raw_chunks: Iterator[str],
) -> Iterator[tuple[Literal["thinking", "answer"], str]]:
    buf = ""
    t_emitted = 0
    a_emitted = 0
    for delta in raw_chunks:
        buf += delta
        mi = buf.find(_ANS_MARK)
        if mi < 0:
            tr = _strip_think_header(buf)
            if len(tr) > t_emitted:
                yield ("thinking", tr[t_emitted:])
                t_emitted = len(tr)
        else:
            tr = _strip_think_header(buf[:mi]).lstrip("\n")
            if len(tr) > t_emitted:
                yield ("thinking", tr[t_emitted:])
                t_emitted = len(tr)
            ar = buf[mi + len(_ANS_MARK) :].lstrip("\n")
            if len(ar) > a_emitted:
                yield ("answer", ar[a_emitted:])
                a_emitted = len(ar)


def split_raw_thinking_answer(raw: str) -> tuple[str, str]:
    if _ANS_MARK in raw:
        pre, post = raw.split(_ANS_MARK, 1)
        return _strip_think_header(pre).strip(), post.strip()
    return "", raw.strip()
