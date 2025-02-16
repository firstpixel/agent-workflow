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

Below is a simplified view of the workflow setup in the project:

```python
from WorkflowManager import WorkflowManager
from Agent import LLMAgent

def custom_validate(result):
    output = result.get("output", "")
    return "?" in output.lower() if output else False

def custom_llm_fn(input_data):
    # Custom LLM logic using a different API or prompt
    print(f" #################################### TOOL EXECUTED  Custom LLM called with input: {input_data}")
    
    model_config3 = {
        "model": "llama3.2:latest",
        "temperature": 0.7,
        "top_p": 0.2,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
    }
    prompt5 = "you just have to say goodbye."
    agent5 = LLMAgent(name="Agent5", model_config=model_config3, system=prompt5, retry_limit=3, expected_inputs=1)
    return f"{agent5}"

def main():
    # Initialize workflow manager
    manager = WorkflowManager()

    # Define prompts for each agent
    prompt1 = ("You must break the problem into multiple small problems, "
               "you can do a 'funnel questioning' about the subject, adding 10 questions "
               "that might help answering the provided question, or you can break into multiple tasks "
               "to solve the problem, you can add questions like where it was discovered, how it was discovered, "
               "where it is applied, how it works, locations, dates, main person names involved, everything to add to the question, including history etc.")
    prompt2 = "You must answer as detailed as possible."
    prompt3 = "You must answer the request as if you are explaining to a 10-year-old child, as if you are a YouTuber."
    prompt4 = "You must add missing information, remove redundancy, and make it as clear as possible."
    prompt5 = "You must provide an abstract, a summary, and a broad detailed explanation."

    # Define model configurations
    model_config = {
        "model": "llama3.2:1b",
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
    }

    model_config2 = {
        "model": "llama3.2:latest",
        "temperature": 0.7,
        "top_p": 0.2,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
    }

    # Create LLM agents with different roles
    agent1 = LLMAgent(name="Agent1", model_config=model_config2, validate_fn=custom_validate, system=prompt1, retry_limit=3, expected_inputs=1)
    agent2 = LLMAgent(name="Agent2", model_config=model_config2, llm_fn=custom_llm_fn, system=prompt2, retry_limit=3, expected_inputs=1)
    agent3 = LLMAgent(name="Agent3", model_config=model_config2, system=prompt3, retry_limit=3, expected_inputs=1)
    agent4 = LLMAgent(name="Agent4", model_config=model_config2, system=prompt4, retry_limit=3, expected_inputs=2)
    agent5 = LLMAgent(name="Agent5", model_config=model_config2, system=prompt5, retry_limit=3, expected_inputs=1)

    # Configure the workflow:
    # Agent1 forks to Agent2 and Agent3,
    # both lead into Agent4, which then flows to Agent5.
    manager.add_agent(agent1, next_agents=["Agent2", "Agent3"])
    manager.add_agent(agent2, next_agents=["Agent4"])
    manager.add_agent(agent3, next_agents=["Agent4"])
    manager.add_agent(agent4, next_agents=["Agent5"])
    manager.add_agent(agent5, next_agents=None)

    # Define the initial input for the workflow
    initial_input = "what is Photosynthesis?"
    
    # Start the workflow
    manager.run_workflow(start_agent_name="Agent1", input_data=initial_input)

if __name__ == "__main__":
    main()
```

## How It Works
### Agent Creation:
Each agent is instantiated with a name, model configuration, a system prompt, and additional optional parameters like validate_fn or a custom llm_fn.

### Workflow Configuration:
The WorkflowManager links agents together by specifying which agent(s) should process the output from a given agent. This allows for branching (forking) and merging paths within the workflow.

### Execution Flow:

The workflow starts with an initial input (e.g., "what is Photosynthesis?").
Agent1 processes the input and, based on its configuration (and custom validation), passes its output to Agent2 and Agent3.
Agent2 and Agent3 further process the data and feed into Agent4.
Agent4 refines the combined outputs and finally passes its result to Agent5.
The final output is generated by Agent5.

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

Execute the main script to start the workflow:

```bash
python main.py
```
## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to improve the project. Please adhere to the project's code style and include tests where applicable.

## License
This project is licensed under the MIT License.
