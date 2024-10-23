class WorkflowManager:
    def __init__(self):
        self.agents = {}  # Store agents by name
        self.connections = {}  # Track agent connections (agent -> next agents)
        self.pending_inputs = {}  # Track received inputs for each agent

    def add_agent(self, agent, next_agents=None):
        """Adds an agent to the workflow, along with its next agents."""
        self.agents[agent.name] = agent
        self.connections[agent.name] = next_agents if next_agents else []
        self.pending_inputs[agent.name] = []  # Initialize pending inputs for the agent

    def run_workflow(self, start_agent_name, input_data):
        """Starts the workflow from the initial agent."""
        current_agent_name = start_agent_name
        input_queue = [(current_agent_name, input_data)]  # Queue for agent processing

        while input_queue:
            current_agent_name, input_data = input_queue.pop(0)
            current_agent = self.agents.get(current_agent_name)

            if current_agent is None:
                print(f"Agent {current_agent_name} not found!")
                continue

            # Store the input data for the agent
            self.pending_inputs[current_agent_name].append(input_data)

            # Combine inputs if waiting for multiple agents
            combined_input = current_agent.receive_input(input_data)
            if combined_input is None:
                print(f"{current_agent_name} is waiting for more inputs...")
                continue  # Skip processing until all inputs are received

            # Execute the agent logic, including retries
            result = self._execute_agent_with_retries(current_agent, combined_input)

            # If the result is valid, move to the next agents in the flow
            if result["success"]:
                current_agent.reset_retry()
                next_agents = self.connections.get(current_agent_name, [])
                for next_agent in next_agents:
                    input_queue.append((next_agent, result["output"]))
            else:
                print(f"{current_agent_name} failed after {current_agent.retry_count} retries.")

    def _execute_agent_with_retries(self, agent, input_data):
        """Executes an agent with retry logic."""
        while agent.should_retry():
            result = agent.execute(input_data)
            if result["success"]:
                return result  # Success, return valid result
            else:
                print(f"{agent.name}: Validation failed. Retrying {agent.retry_count}/{agent.retry_limit}")
                agent.retry_count += 1
        return {"output": None, "success": False}  # Failure after retries