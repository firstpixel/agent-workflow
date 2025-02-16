from WorkflowManager import WorkflowManager
from Agent import LLMAgent


def custom_validate(result):
    # Access the "output" key in the result dictionary and check if "valid" is present
    output = result.get("output", "")
    return "?" in output.lower() if output else False

def custom_llm_fn(input_data):
    """Custom LLM function that uses a different API or logic."""
    print(f" #################################### TOOL EXECUTED  Custom LLM called with input: {input_data}")
    return f"TOOL EXECUTED  {input_data}"


def custom_llm_fn(input_data):

    model_config3 = {
        "model": "llama3.2:latest",
        "temperature": 0.7,
        "top_p": 0.2,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
    }
    """Custom LLM function that uses a different API or logic."""
    print(f" #################################### TOOL EXECUTED  Custom LLM called with input: {input_data}")
    prompt5 = "you just have to say goodbye."
    agent5 = LLMAgent(name="Agent5", model_config=model_config3, system=prompt5, retry_limit=3, expected_inputs=1)

    return f"{agent5}"

def main():
    # Initialize workflow manager
    manager = WorkflowManager()

    prompt1 = "You must break the problem into multiple small problems, you can do a 'funnel questioning' about the subject, adding 10 questions that might help answering the provided question, or you can break into multiple tasks to solve the problem, you can add questions like where it was discovered, how it was discovered, where it is applied, how it works, locations, dates, main person names involved, everything to add to the question, including history etc."
    prompt2 = "You must answer the more detailed as possible."
    prompt3 = "You must answer the request as if you are explaining for a 10-year-old child as if you are a YouTuber or else you are a failure."
    prompt4 = "You must add missing information, removing any redundancy and leaving it as clear as possible."
    prompt5 = "You must provide a abstract, a summary text, and a broad detailed text explaning it."

    # Define LLaMA model configuration
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

    # Create LLM agents
    agent1 = LLMAgent(name="Agent1", model_config=model_config2, validate_fn=custom_validate, system=prompt1, retry_limit=3, expected_inputs=1)
    agent2 = LLMAgent(name="Agent2", model_config=model_config2, llm_fn=custom_llm_fn, system=prompt2, retry_limit=3, expected_inputs=1)
    agent3 = LLMAgent(name="Agent3", model_config=model_config2, system=prompt3, retry_limit=3, expected_inputs=1)
    agent4 = LLMAgent(name="Agent4", model_config=model_config2, system=prompt4, retry_limit=3, expected_inputs=2)
    agent5 = LLMAgent(name="Agent5", model_config=model_config2, system=prompt5, retry_limit=3, expected_inputs=1)

    # Add agents to the workflow
    manager.add_agent(agent1, next_agents=["Agent2", "Agent3"])  # Fork: Agent1 -> Agent2, Agent3
    manager.add_agent(agent2, next_agents=["Agent4"])
    manager.add_agent(agent3, next_agents=["Agent4"])
    manager.add_agent(agent4, next_agents=["Agent5"])  # End of the flow
    manager.add_agent(agent5, next_agents=None)  # End of the flow

    # Start workflow with initial input
    initial_input = "what is Photosynthesis?"
    
    #initial_input = "Explain to me how to build a agent ai system that based on a question, I can have a agent break into multiple tasks, that it can send to other agent that will build a system input for each task to be executed by an llm?"
    
    # Start the workflow
    manager.run_workflow(start_agent_name="Agent1", input_data=initial_input)

if __name__ == "__main__":
    main()
