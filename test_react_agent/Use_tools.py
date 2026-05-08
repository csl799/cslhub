import inspect
import ast
import os
import re
import platform
from typing import List, Tuple
from string import Template
from dotenv import load_dotenv



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
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("未找到 OPENROUTER_API_KEY 环境变量，请在 .env 文件中设置。")
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

def read_file(file_path):
    """用于读取文件内容"""
    with open(file_path,"r",encoding="utf-8") as f:
        return f.read()


def write_to_file(file_path,content):
    """将指定的内容写入指定文件"""
    with open(file_path,"w",encoding="utf-8") as f:
        f.write(content.replace("\\n","\n"))
    return "写入成功"


def run_terminal_command(command):
    """用于执行终端命令"""
    import subprocess
    run_result = subprocess.run(command,shell=True,capture_output=True,text=True)
    return "执行成功" if run_result.returncode == 0 else run_result.stderr