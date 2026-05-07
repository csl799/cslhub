"""Tavily 联网搜索（LangChain 预置封装）。"""

from __future__ import annotations

import os
from typing import Any

from langchain.tools import tool

_TAVILY_ENV = "TAVILY_API_KEY"
_client: Any | None = None


def _tavily_tool() -> Any | None:
    global _client
    if _client is not None:
        return _client
    key = os.getenv(_TAVILY_ENV, "").strip()
    if not key:
        return None
    from langchain_community.tools.tavily_search import TavilySearchResults

    _client = TavilySearchResults(
        api_key=key,
        max_results=5,
        search_depth="basic",
        include_answer=True,
        include_raw_content=False,
    )
    return _client


@tool
def web_search(query: str) -> str:
    """
    使用 Tavily 对互联网做检索，返回摘要与链接片段。
    适用于：人物/梗/时事等你训练数据里没有或明显过时；用户质疑你给出的说法需要查证。
    query 用简短中文或英文关键词，可含多个词。
    """
    q = (query or "").strip()
    if not q:
        return "请提供非空的搜索 query。"
    t = _tavily_tool()
    if t is None:
        return f"未配置环境变量 {_TAVILY_ENV}，无法联网搜索。"
    try:
        out = t.invoke({"query": q})
        if isinstance(out, str):
            return out
        return str(out)
    except Exception as e:
        return f"联网搜索失败：{e}"
