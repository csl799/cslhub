import sys

from dotenv import load_dotenv

from chat_agent import create_chat_agent, iter_raw_ai_text_chunks, split_raw_thinking_answer
from database import checkpoint_lifecycle

load_dotenv()

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (OSError, ValueError):
        pass


def main() -> None:
    with checkpoint_lifecycle() as checkpointer:
        agent = create_chat_agent(checkpointer)
        tid = "session-1"
        q = "帮我查一下上海明天的天气"
        raw = "".join(iter_raw_ai_text_chunks(agent, q, tid))
        think, ans = split_raw_thinking_answer(raw)
        if think:
            print("正在思考：\n" + think)
            print()
        print("答案：\n" + ans)


if __name__ == "__main__":
    main()
