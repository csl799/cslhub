"""对话过长时用模型总结前文（LangChain SummarizationMiddleware）。"""

from __future__ import annotations

from langchain.agents.middleware import SummarizationMiddleware

_SUMMARY_TRIGGER_MESSAGE_COUNT = 4
_KEEP_RECENT_MESSAGES = 3

_DEFAULT_SUMMARY_PROMPT_ZH = """下面是用户与助手的一段对话记录。请用中文写一段简洁的摘要，抓住：
- 用户主要关心什么、提出了哪些要求或问题；
- 助手已经做了哪些回答或操作（例如调用了哪些工具、结论是什么）。

只输出摘要正文，不要加标题或列表符号以外的多余客套话。

对话记录：
{messages}
"""


def build_message_summary_middleware(model: str = "deepseek-chat") -> SummarizationMiddleware:
    return SummarizationMiddleware(
        model=model,
        trigger=("messages", _SUMMARY_TRIGGER_MESSAGE_COUNT),
        keep=("messages", _KEEP_RECENT_MESSAGES),
        summary_prompt=_DEFAULT_SUMMARY_PROMPT_ZH,
    )


__all__ = ["build_message_summary_middleware"]
