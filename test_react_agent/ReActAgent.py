from collections.abc import Callable
from openai import OpenAI
from dotenv import load_dotenv

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
            {"role":"system","content":self.render_system_prompt(react_system_prompt_template)}
        ]