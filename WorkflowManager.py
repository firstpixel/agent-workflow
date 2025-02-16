"""
Licensed under the MIT License given below.
Copyright (c) 2025 Gil Beyruth

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the “Software”), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

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
        input_queue = [(start_agent_name, input_data)]  # Queue for agent processing

        while input_queue:
            current_agent_name, input_data = input_queue.pop(0)
            current_agent = self.agents.get(current_agent_name)

            if current_agent is None:
                print(f" #################################### Agent {current_agent_name} not found!")
                continue

            # Store the input data for the agent
            combined_input = current_agent.receive_input(input_data)
            if combined_input is None:
                print(f" #################################### {current_agent_name} is waiting for more inputs...")
                continue  # Skip processing until all inputs are received

            # Execute the agent logic, including retries
            result = current_agent.run_with_retries(combined_input)

            # If the result is valid, move to the next agents in the flow
            if result["success"]:
                current_agent.reset_retry()
                next_agents = self.connections.get(current_agent_name, [])
                for next_agent in next_agents:
                    input_queue.append((next_agent, result["output"]))
            else:
                print(f" #################################### {current_agent_name} failed after {current_agent.retry_count} retries.")
