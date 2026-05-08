import click

from Use_tools import *
from ReActAgent import ReActAgent

@click.command()
@click.argument("project_directory",
                type = click.Path(exists = True,file_okay = False,dir_okay = True))
def main(project_directory):
    project_dic = os.path.abspath(project_directory)

    tools = [read_file,write_to_file,run_terminal_command]
    agent = ReActAgent(tools=tools,model="deepseek-chat",project_directory=project_dic)

    task = input("Task: ")

    final_answer = agent.run(task)

    print(f"\n\n Final Answer: {final_answer}")


if __name__ == "__main__":
    main()

