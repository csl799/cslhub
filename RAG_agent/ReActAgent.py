from collections.abc import Callable
from functools import wraps
from openai import OpenAI
import inspect
import ast
import os
import subprocess
import re
import platform
from typing import List, Tuple
from string import Template
from dotenv import load_dotenv

from prompt_template import react_system_prompt_template


load_dotenv()


class ReActAgent:
    def __init__(self,tools:list[Callable],model:str,project_directory:str):
        self.project_directory = os.path.abspath(project_directory)
        self.tools = {func.__name__: self._wrap_tool(func) for func in tools}
        self.model = model
        self.client = OpenAI(
            base_url = "https://api.deepseek.com",
            api_key = ReActAgent.get_api_key(),
        )

    def _resolve_under_project(self, file_path: str) -> str:
        if os.path.isabs(file_path):
            return file_path
        return os.path.normpath(os.path.join(self.project_directory, file_path))

    def _wrap_tool(self, func: Callable) -> Callable:
        root = self.project_directory
        name = func.__name__

        if name == "read_file":
            @wraps(func)
            def wrapped(file_path: str):
                return func(self._resolve_under_project(file_path))
            return wrapped

        if name == "write_to_file":
            @wraps(func)
            def wrapped(file_path: str, content: str):
                path = self._resolve_under_project(file_path)
                parent = os.path.dirname(path)
                if parent:
                    os.makedirs(parent, exist_ok=True)
                return func(path, content)
            return wrapped

        if name == "run_terminal_command":
            @wraps(func)
            def wrapped(command: str):
                run_result = subprocess.run(
                    command, shell=True, capture_output=True, text=True, cwd=root
                )
                return "执行成功" if run_result.returncode == 0 else run_result.stderr
            return wrapped

        return func

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

            # 检测模型是否输出 Final Answer（须成对标签），匹配成功才返回
            final_answer_match = re.search(
                r"<final_answer>(.*)</final_answer>", content, re.DOTALL
            )
            if final_answer_match:
                return final_answer_match.group(1).strip()

            if "<final_answer>" in content:
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "你上一轮回复里出现了 <final_answer>，但未与 </final_answer> 成对闭合。"
                            "请重新输出：要么给出完整的 <final_answer>...</final_answer>，"
                            "要么在本轮只使用 <thought> 与 <action> 继续调用工具。"
                        ),
                    }
                )
                continue

            # 检测 Action
            action_match = re.search(r"<action>(.*)</action>", content, re.DOTALL)
            if not action_match:
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "你上一轮回复既没有成对的 <final_answer>...</final_answer>，"
                            "也没有成对的 <action>...</action>。"
                            "请二选一重新输出本轮内容："
                            "若不需要工具，请输出 <thought>...</thought> 后紧跟完整的 <final_answer>...</final_answer>；"
                            "若需要工具，请输出 <thought>...</thought> 后紧跟完整的 <action>...</action>（参数与可用工具一致），"
                            "且输出 <action> 后不要自己写 <observation>。"
                        ),
                    }
                )
                continue
            action = action_match.group(1)
            tool_name,args = self.parse_action(action)

            # 执行 Action
            print(f"\n\n Action:{tool_name}({','.join(args)})")
            # 只有终端命令才需要询问用户，其他的工具直接执行
            should_continue = input(f"\n\n Continue? (y/n): ") if tool_name == "run_terminal_command" else "y"
            if should_continue.lower() != "y":
                print("\n\n操作已取消。")
                return "操作被用户取消"

            try:
                observation = self.tools[tool_name](*args)
            except Exception as e:
                observation = f"工具执行错误:{str(e)}"
            print(f"\n\n Observation:{observation}")
            obs_msg = f"<observation>{observation}</observation>"
            messages.append({"role":"user","content":obs_msg})

    def get_tool_list(self) -> str:
        """生成工具列表字符串，包含函数签名和简要说明"""
        tool_descriptions = []
        for func in self.tools.values():
            name = func.__name__
            signature = str(inspect.signature(func))
            doc = inspect.getdoc(func)
            tool_descriptions.append(f"- {name}{signature}: {doc}")
        return "\n".join(tool_descriptions)

    def render_system_prompt(self, system_prompt_template: str) -> str:
        """渲染系统提示模板，替换变量"""
        tool_list = self.get_tool_list()
        file_list = ", ".join(
            os.path.abspath(os.path.join(self.project_directory, f))
            for f in os.listdir(self.project_directory)
        )
        return Template(system_prompt_template).substitute(
            operating_system=self.get_operating_system_name(),
            tool_list=tool_list,
            file_list=file_list
        )

    @staticmethod
    def get_api_key() -> str:
        """Load the API key from an environment variable."""
        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY 环境变量，请在 .env 文件中设置。")
        return api_key

    def call_model(self, messages):
        print("\n\n正在请求模型，请稍等...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        content = response.choices[0].message.content
        messages.append({"role": "assistant", "content": content})
        return content

    def parse_action(self, code_str: str) -> Tuple[str, List[str]]:
        match = re.match(r'(\w+)\((.*)\)', code_str, re.DOTALL)
        if not match:
            raise ValueError("Invalid function call syntax")

        func_name = match.group(1)
        args_str = match.group(2).strip()

        # 手动解析参数，特别处理包含多行内容的字符串
        args = []
        current_arg = ""
        in_string = False
        string_char = None
        i = 0
        paren_depth = 0

        while i < len(args_str):
            char = args_str[i]

            if not in_string:
                if char in ['"', "'"]:
                    in_string = True
                    string_char = char
                    current_arg += char
                elif char == '(':
                    paren_depth += 1
                    current_arg += char
                elif char == ')':
                    paren_depth -= 1
                    current_arg += char
                elif char == ',' and paren_depth == 0:
                    # 遇到顶层逗号，结束当前参数
                    args.append(self._parse_single_arg(current_arg.strip()))
                    current_arg = ""
                else:
                    current_arg += char
            else:
                current_arg += char
                if char == string_char and (i == 0 or args_str[i - 1] != '\\'):
                    in_string = False
                    string_char = None

            i += 1

        # 添加最后一个参数
        if current_arg.strip():
            args.append(self._parse_single_arg(current_arg.strip()))

        return func_name, args

    def _parse_single_arg(self, arg_str: str):
        """解析单个参数"""
        arg_str = arg_str.strip()

        # 如果是字符串字面量
        if (arg_str.startswith('"') and arg_str.endswith('"')) or \
                (arg_str.startswith("'") and arg_str.endswith("'")):
            # 移除外层引号并处理转义字符
            inner_str = arg_str[1:-1]
            # 处理常见的转义字符
            inner_str = inner_str.replace('\\"', '"').replace("\\'", "'")
            inner_str = inner_str.replace('\\n', '\n').replace('\\t', '\t')
            inner_str = inner_str.replace('\\r', '\r').replace('\\\\', '\\')
            return inner_str

        # 尝试使用 ast.literal_eval 解析其他类型
        try:
            return ast.literal_eval(arg_str)
        except (SyntaxError, ValueError):
            # 如果解析失败，返回原始字符串
            return arg_str

    def get_operating_system_name(self):
        os_map = {
            "Darwin": "macOS",
            "Windows": "Windows",
            "Linux": "Linux"
        }

        return os_map.get(platform.system(), "Unknown")

