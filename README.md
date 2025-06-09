# agent-workflow
# Agent Workflow Project

Agent Workflow is a modular framework designed to orchestrate a series of language model (LLM) agents in a flexible and dynamic workflow. The project demonstrates how to break down complex tasks into smaller sub-tasks, each handled by a dedicated agent with its own prompt, model configuration, and optional custom logic.

## Overview

This project provides a simple yet powerful example of how multiple LLM agents can be linked together to process a single input through a multi-step workflow. Each agent can:

- **Process specific tasks or questions:** For example, decomposing a problem into sub-questions.
- **Validate its output:** Using custom validation functions.
- **Utilize custom LLM functions:** Allowing for the integration of alternative APIs or logic.
- **Chain results:** By defining subsequent agents to handle further processing.

## Features

- **Modular Agent Design:** Each agent is an instance of `LLMAgent` with its own system prompt, model configuration, and optional custom functions.
- **Workflow Management:** The `WorkflowManager` is used to add agents, define the chain of execution (including branching), and start the workflow.
- **Custom Validation:** Agents can use custom functions (like `custom_validate`) to ensure that outputs meet certain criteria.
- **Custom LLM Functions:** Agents can override the default LLM logic with functions like `custom_llm_fn` to implement specialized behavior.
- **Flexible Configuration:** Easily adjust model parameters, prompts, and the workflow structure to fit your use case.

## Project Structure

Below is a simplified view of how the current demo configures and runs the workflow:

```python
from WorkflowManager import WorkflowManager
from Agent import LLMAgent

def build_workflow():
    manager = WorkflowManager()
    model_cfg = {
        "model": "llama3.2:latest",
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
    }

    clarifier = LLMAgent(name="Clarifier", model_config=model_cfg,
                         system="Ask clarifying questions.", needs_user_input=True)
    designer = LLMAgent(name="Designer", model_config=model_cfg,
                        system="Propose a high-level design.")
    task_maker = LLMAgent(name="TaskMaker", model_config=model_cfg,
                          system="Break the design into tasks.")

    manager.add_agent(clarifier, next_agents=["Designer"])
    manager.add_agent(designer, next_agents=["TaskMaker"])
    manager.add_agent(task_maker, next_agents=None)
    return manager

manager = build_workflow()
manager.run_workflow(start_agent_name="Clarifier", input_data="Build a web app",
                     interactive=True)
```

## How It Works
### Agent Creation:
Each agent is instantiated with a name, model configuration, a system prompt, and additional optional parameters like validate_fn or a custom llm_fn.

### Workflow Configuration:
The WorkflowManager links agents together by specifying which agent(s) should process the output from a given agent. This allows for branching (forking) and merging paths within the workflow.

### Execution Flow:

1. **Clarifier** asks questions about the user's request until the requirements are clear.
2. **Designer** creates a high-level architecture from the clarified request.
3. **TaskMaker** breaks that design into concrete tasks that can be executed.

## Customization
### Model Configurations:
Adjust parameters such as temperature, top_p, frequency_penalty, and presence_penalty to control the behavior of your language models.

### Custom Prompts and Validation:
Modify the system prompts for each agent to suit different types of tasks. Custom validation functions (like custom_validate) can enforce specific output requirements.

### Extensible Workflow:
The framework allows you to add more agents or change the workflow structure by altering the next_agents parameter in the WorkflowManager.

## Getting Started
### Clone the Repository:
```bash
git clone https://github.com/firstpixel/agent-workflow.git
cd agent-workflow
```
### Install Dependencies:

Ensure you have the necessary dependencies installed. You might need to install packages such as llama (or any other dependencies related to your LLM agents).

Create a python venv:
```bash
python -m venv venv
source venv/bin/activate
```
if you want to deactivate:
```bash
deactivate
```

Install dependencies:
```bash
pip install -r requirements.txt
```
### Run the Workflow:

Execute the main script to start the workflow. If you do not have an Ollama
server running locally, enable the built-in mock by setting `MOCK_OLLAMA=1`:

```bash
# export MOCK_OLLAMA=1  # uncomment to use the mock server
python main.py
```
## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to improve the project. Please adhere to the project's code style and include tests where applicable.

## License
This project is licensed under the MIT License.
