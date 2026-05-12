import click
import os

from rag_knowledge import build_search_knowledge_base_tool
from ReActAgent import ReActAgent
from Tools import read_file, run_terminal_command, write_to_file

@click.command()
@click.argument(
    "project_directory",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
def main(project_directory):
    project_dic = os.path.abspath(project_directory)

    tools = [
        read_file,
        write_to_file,
        run_terminal_command,
        build_search_knowledge_base_tool(project_dic),
    ]
    agent = ReActAgent(tools=tools, model="deepseek-chat", project_directory=project_dic)

    query = input("query: ")

    final_answer = agent.run(query)

    print(f"\n\n Final Answer: {final_answer}")


if __name__ == "__main__":
    main()
