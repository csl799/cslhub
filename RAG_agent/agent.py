import click
import os

from ReActAgent import ReActAgent

@click.command()
@click.argument(
    "project_directory",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
def main(project_directory):
    project_dic = os.path.abspath(project_directory)

    tools = []
    agent = ReActAgent(tools=tools,model="deepseek-chat",project_directory=project_dic)

    task = input("Task: ")

    final_answer = agent.run(task)

    print(f"\n\n Final Answer: {final_answer}")


if __name__ == "__main__":
    main()
