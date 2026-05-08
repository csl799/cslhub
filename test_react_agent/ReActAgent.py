from collections.abc import Callable
from openai import OpenAI
from dotenv import load_dotenv
import platform
import re

from prompt_template import react_system_prompt_template


load_dotenv()


class ReActAgent:
    def __init__(self,tools:list[Callable],model:str,project_directory:str):
        self.tools = {func.__name__:func for func in tools}
        self.model = model
        self.project_directory = project_directory
        self.client = OpenAI(
            base_url = "",
            api_key = ReActAgent.get_api_key(),
        )

    def run(self,use_input:str):
        messages = [
            {"role":"system","content":self.render_system_prompt(react_system_prompt_template)},
            {"role":"user","content":f"<question>{use_input}</question>"}
        ]

        while True:

            # 请求模型
            content = self.call_model(messages)

            # 检测 Thought
            thought_match = re.search(r"<thought>(.*)</thought>",content,re.DOTALL)
            if thought_match:
                thought = thought_match.group(1)
                print(f"\n\n Thought: {thought}")

            # 检测模型是否输出 Final Answer,如果是的话，直接返回
            if "<final_answer>" in content:
                final_answer = re.search(r"<final_answer>(.*)</final_answer>",content,re.DOTALL)
                return final_answer.group(1)

            # 检测 Action
            action_match = re.search(r"<action>(.*)</action>",content,re.DOTALL)
            if not action_match:
                raise RuntimeError("模型未输出<action>")
            action = action_match.group(1)
            tool_name,args = self.parse_action(action)

            # 执行 Action
            print(f"\n\n Action:{tool_name}({','.join(args)})")
            # 只有终端命令才需要询问用户，其他的工具直接执行
            should_continue = input(f"\n\n Continue? (y/n): ") if tool_name == "run_terminal_command" else "y"
            if should_continue.lower() == "y":
                print("\n\n操作已取消。")
                return "操作被用户取消"

            try:
                observation = self.tools[tool_name](*args)
            except Exception as e:
                observation = f"工具执行错误:{str(e)}"
            print(f"\n\n Observation:{observation}")
            obs_msg = f"<observation>{observation}</observation>"
            messages.append({"role":"user","content":obs_msg})





