import ollama

class Agent:
    def __init__(self, name, model_config, validate_fn=None, llm_fn=None, system="", prompt="", context="", retry_limit=3, expected_inputs=1):
        self.name = name
        self.model_config = model_config
        self.system = system
        self.prompt = prompt
        self.context = context
        self.retry_limit = retry_limit
        self.retry_count = 0
        self.expected_inputs = expected_inputs
        self.received_inputs = []
        self.validate_fn = validate_fn if validate_fn else self.default_validate
        self.llm_fn = llm_fn if llm_fn else self.default_llm_fn

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
            combined_input = " | ".join(self.received_inputs)
            self.received_inputs = []
            return combined_input
        return None

    def run_with_retries(self, input_data):
        """Executes the agent with retry logic."""
        while self.should_retry():
            result = self.execute(input_data)
            if result["success"]:
                return result  # Success
            else:
                self.retry_count += 1
                print(f" #################################### Agent {self.name}: Retry {self.retry_count}/{self.retry_limit} failed")
        return {"output": None, "success": False}  # Failure after retries

    def default_validate(self, result):
        """Default validation logic."""
       # "valid" in result["output"].lower()
        print(f" #################################### Agent {self.name}: No validation needed")
        return True
    def default_llm_fn(self, input_data):
        """Default LLM function."""
        print(f" #################################### Agent {self.name}: No tools available")
        return f"{input_data}"

class LLMAgent(Agent):
    def execute(self, user_input):
        """Executes the LLM using the ollama API."""
        print(f" #################################### Agent {self.name}: Executing with input: {user_input}")
        full_prompt = f"{self.context}\n\n{self.prompt}\n\n{user_input}"
        messages = [
            {"role": "system", "content": self.system},
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
                    "presence_penalty": self.model_config["presence_penalty"]
                }
            )
            output = response['message']['content'].strip()
            print(f" #################################### Agent {self.name}: output - {output}")
            
            success = self.validate({"output": output})
            print(f" #################################### Agent {self.name}: validate - {success}")
            
            output = self.llm_fn({"output": output})

            print(f" #################################### Agent {self.name}: tool executed - {success}")
            
            return {"output": output, "success": success}

        except Exception as e:
            print(f" #################################### Agent {self.name}: Error during execution - {e}")
            return {"output": None, "success": False}
        
