# Agent Workflow: Running the Demo

This repository demonstrates a simple multi-agent workflow.
You can run it directly from the command line or launch the optional Streamlit UI.

## Command-line usage

Install the required dependencies and run `main.py`:

```bash
pip install -r requirements.txt
MOCK_OLLAMA=1 python main.py
```

This executes the clarifier, designer, and task-making agents and prints a snippet from `task_list.md`.

## Streamlit UI

To interact with the workflow step by step, run:

```bash
streamlit run ui_streamlit.py
```

The UI lets you enter the initial prompt, answer clarifier questions, and observe each stage's output.
