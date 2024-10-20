from WorkflowManager import WorkflowManager 
from Agent import LLMAgent


def custom_validate(result):
    # Access the "output" key in the result dictionary and check if "valid" is present
    output = result.get("output", "")
    return "valid" in output.lower() if output else 0

def custom_llm_fn(input_data, model_config):
    """Custom LLM function that uses a different API or logic."""
    print(f"Custom LLM called with input: {input_data}")
    return f"Processed {input_data} with custom LLM"

def main():
    # Initialize workflow manager
    manager = WorkflowManager()

    prompt1 = "You should provide a funnel questioning about the subject, make sure to include the best questions to answer the first."
    prompt2 = "You must answer the more detailed as possible or else you get no cookies."
    prompt3 = "You must answer the request as if you are explaining for a 10 year old chield as if you are an youtuber or else you are a failure."
    prompt4 = "You must answer and check if its the best answer or give a feedback to improove it, telling the missing points, if you think there is nothink else to add and its perfect, you should finish it with a message GREAT_SUCCESS"
    prompt5 = "You must summarize the text, removing any redundance and leaving it more clear possible."

    # Define LLaMA model configuration
    model_config = {
        "model": "llama3.2:1b",
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "context": "This is additional context for the LLM.",
    }

    # Create LLM agents
    agent1 = LLMAgent(name="Agent1", model_config=model_config, system=prompt1, retry_limit=3, expected_inputs=1)
    agent2 = LLMAgent(name="Agent2", model_config=model_config, validate_fn=custom_validate, 
        llm_fn=custom_llm_fn, system=prompt2, retry_limit=3, expected_inputs=1)
    agent3 = LLMAgent(name="Agent3", model_config=model_config, system=prompt3, retry_limit=3, expected_inputs=1)
    agent4 = LLMAgent(name="Agent4", model_config=model_config, system=prompt4, retry_limit=3, expected_inputs=2)
    agent5 = LLMAgent(name="Agent5", model_config=model_config, system=prompt4, retry_limit=3, expected_inputs=1)

    # Add agents to the workflow
    manager.add_agent(agent1, next_agents=["Agent2", "Agent3"])  # Fork: Agent1 -> Agent2, Agent3
    manager.add_agent(agent2, next_agents=["Agent4"])  # Agent2 also connects to Agent3
    manager.add_agent(agent3, next_agents=["Agent4"])  # Agent2 also connects to Agent3
    manager.add_agent(agent4, next_agents=None)  # End of the flow

    # Start workflow with initial input
    initial_input = "What is photosynthesis?"
    
    # Start the workflow
    manager.run_workflow(start_agent_name="Agent1", input_data=initial_input)

if __name__ == "__main__":
    main()