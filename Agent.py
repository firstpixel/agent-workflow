import ollama

class Agent:
    def __init__(self, name, model_config, validate_fn=None, tool_fn=None, system="", prompt="", context="", retry_limit=3, expected_inputs=1):
        self.name = name
        self.model_config = model_config
        self.system = system
        self.prompt = prompt
        self.context = context
        self.retry_limit = retry_limit  # Max retries if validation fails
        self.retry_count = 0
        self.expected_inputs = expected_inputs  # Number of inputs expected before processing
        self.received_inputs = []  # To store inputs until all are received
        self.validate_fn = validate_fn if validate_fn else self.default_validate  # Set custom or default validation
        self.tool_fn = tool_fn if tool_fn else self.default_tool_fn  # Set custom or default LLM function (tool mode)

    def execute(self, user_input):
        """Agent processes data. This function must be implemented by subclasses."""
        raise NotImplementedError("Execute method must be implemented by subclasses.")

    def validate(self, result):
        """Validate the result using the provided validation function."""
        return self.validate_fn(result)

    def should_retry(self):
        """Check if the agent can retry based on the retry limit."""
        return self.retry_count < self.retry_limit

    def reset_retry(self):
        """Resets retry count after a successful execution."""
        
        self.retry_count = 0

    def receive_input(self, user_input):
        """Aggregates input data until the expected number of inputs is received."""
        self.received_inputs.append(user_input)
        if len(self.received_inputs) == self.expected_inputs:
            combined_input = " | ".join(self.received_inputs)  # Combines all inputs
            self.received_inputs = []  # Reset after aggregation
            return combined_input
        return None

    def default_validate(self, result):
        """Default validation logic. Returns true if 'a' is in the output."""
        print(" #################################### No vallidate function for agent: ",{self.name})
        return True

    def default_tool_fn(self, input_data):
        """Default TOOL function to be used as a tool by the agent."""
        # Basic TOOL function that doesn't call ollama
        # This can be overridden by custom functions or tools in specific use cases
        print(" #################################### No tool setup for agent: ",{self.name})
        return f"{input_data}"

class LLMAgent(Agent):
    def execute(self, user_input):
        """Executes the LLM to process the input using the ollama API."""
        print(" #################################### Agent starting: ", self.name, " with input: ", user_input)
        combined_input = self.receive_input(user_input)
        if combined_input:
            while self.should_retry():
                print(f" #################################### {self.name}: Processing input using LLM. Retry {self.retry_count + 1}/{self.retry_limit}")

                # Use ollama API for LLM
                
                full_prompt = f"{self.context}\n\n{self.prompt}\n\n{combined_input}" if self.context else f"{self.prompt}\n\n{combined_input}"
                system_prompt = f"{self.system}" if self.system else "You should provide assistance to the user."

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ]
                
                try:
                    response = ollama.chat(
                        model=self.model_config["model"],
                        stream=False,
                        messages=messages,
                        options={
                            "temperature": self.model_config["temperature"],
                            "top_p": self.model_config["top_p"],
                            "frequency_penalty": self.model_config["frequency_penalty"],
                            "presence_penalty": self.model_config["presence_penalty"],
                            "seed": 42,
                            "echo": False,
                            "stream": False,
                            "stop": ["<|endoftext|>"]
                        }
                    )
                except ollama.ResponseError as e:
                    print('Error:', e.error)
                    if e.status_code == 404:
                        print(" #################################### ollama not found")
                    return {"output": "Error during LLM call", "success": False}
                except Exception as e:
                    print(f" #################################### {self.name}: Error during execution - {str(e)}")
                    return {"output": "Error during LLM call", "success": False}

                # Handle the response structure properly
                if 'message' in response and 'content' in response['message']:
                    output = response['message']['content'].strip()  # Extract content
                    print(" #################################### Response from ollama.chat:", output)

                    # Validate the output
                    success = self.validate({"output": output})

                    if success:
                        # Reset retry count on success
                        self.reset_retry() 
                        return {"output": output, "success": success}
                    else:
                        print(f" #################################### {self.name}: Validation failed, retrying...")
                        self.retry_count += 1  # Increment retry count on failure
                        # Will loop again to retry
                        
                        
            print(f" #################################### {self.name}: Retry limit reached. Returning last output.")
            return {"output": output, "success": False}
        else:
            print(f" #################################### {self.name}: Waiting for more inputs.")
            return {"output": None, "success": False}  # Failure after retries