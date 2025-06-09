"""
Agent Workflow demo entrypoint.
"""

from WorkflowManager import WorkflowManager
from Agent import LLMAgent, EvolvingAgent
from task import Task
from mcst_executor import MCSTExecutor
from evolver import EvolverAgent
from evaluator import EvaluatorAgent
from judge import JudgeAgent


def build_workflow_manager():
    """Create a WorkflowManager with the standard agents registered."""
    manager = WorkflowManager()
    from tools.echo_tool import run as echo
    from tools.uppercase_tool import run as upper
    from tools.code_executor_tool import run as exec_tool
    manager.tool_manager.register("echo", echo)
    manager.tool_manager.register("upper", upper)
    manager.tool_manager.register("exec", exec_tool)

    model_config = {
        "model": "llama3.2:latest",
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
    }

    clarifier = LLMAgent(
        name="Clarifier",
        model_config=model_config,
        system="Ask clarifying questions about the user's request.",
        needs_user_input=True,
    )
    designer = LLMAgent(
        name="Designer",
        model_config=model_config,
        system="Propose a high-level design given the clarified requirements.",
    )
    task_maker = LLMAgent(
        name="TaskMaker",
        model_config=model_config,
        system="Break the design into concrete implementation tasks.",
    )

    manager.add_agent(clarifier, next_agents=["Designer"])
    manager.add_agent(designer, next_agents=["TaskMaker"])
    manager.add_agent(task_maker, next_agents=None)
    return manager


def run_demo(user_prompt, interactive=False, user_input_fn=None):
    manager = build_workflow_manager()
    start_agent = "Clarifier" if interactive else "Designer"
    manager.run_workflow(start_agent_name=start_agent, input_data=user_prompt, interactive=interactive, user_input_fn=user_input_fn)

    with open("task_list.md", "r") as f:
        first_lines = [next(f).strip() for _ in range(10)]
    print("\nLoaded task list excerpt:\n" + "\n".join(first_lines))

    # Simple MCST demonstration
    model_config = {
        "model": "llama3.2:latest",
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
    }
    evolver = EvolverAgent(name="evolver", model_config=model_config)
    evaluator = EvaluatorAgent()
    judge = JudgeAgent()
    task = Task(description="simple evolution task", pre_tools=["echo"], post_tools=["upper"])
    base_agent = EvolvingAgent(name="base", model_config=model_config, prompt="say hi", code="print('hi')")
    executor = MCSTExecutor(branching_factor=2, max_depth=1)
    best = executor.run(task, base_agent, evolver, evaluator, judge)
    print(f"Best version: {best.version}")


def main():
    user_prompt = "Build a web app for image classification"
    run_demo(user_prompt, interactive=False)


if __name__ == "__main__":
    main()
