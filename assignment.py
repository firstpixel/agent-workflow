"""Simple agent and tool assignment step."""

from task import Task


def assign_agents_and_tools(task_list, tool_registry=None):
    """Assign default agent types and tool sequences to each task."""
    available_tools = set(tool_registry or [])
    for task in task_list:
        # Assign a generic agent type
        task.agent_type = task.agent_type or "llm"
        # naive tool assignment based on keywords
        desc = task.description.lower()
        if "code" in desc and "exec" in available_tools:
            task.pre_tools.append("exec")
        if "echo" in available_tools:
            task.post_tools.append("echo")
    return task_list
