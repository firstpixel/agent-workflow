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

import os

if os.environ.get("MOCK_OLLAMA") == "1":
    from mock_ollama import chat as ollama_chat
else:
    import ollama

    def ollama_chat(**kwargs):
        """Wrapper around `ollama.chat` with fallback to the mock implementation."""
        try:
            return ollama.chat(**kwargs)
        except Exception as e:
            print(f" #################################### Ollama error: {e} - using mock")
            from mock_ollama import chat as mock_chat
            return mock_chat(**kwargs)

class Agent:
    def __init__(self, name, model_config, validate_fn=None, llm_fn=None, system="", prompt="", context="", retry_limit=3, expected_inputs=1, needs_user_input=False):
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
        self.needs_user_input = needs_user_input

    def __repr__(self):
        """Readable representation for debugging."""
        return f"<{self.__class__.__name__} name={self.name}>"

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
            response = ollama_chat(
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


class EvolvingAgent(LLMAgent):
    """LLMAgent with versioning support for MCST evolution."""

    def __init__(self, *, code: str = "", version: str = "v1_0", parent: str = None,
                 metadata: dict = None, **kwargs):
        prompt = kwargs.pop("prompt", "")
        super().__init__(prompt=prompt, **kwargs)
        self.code = code
        self.version = version
        self.parent = parent
        self.metadata = metadata or {}

    def save(self, agent_path: str, prompt_path: str, metadata_path: str = None):
        """Persist code, prompt and metadata to disk."""
        import json
        import os

        os.makedirs(os.path.dirname(agent_path), exist_ok=True)
        with open(agent_path, "w") as f:
            f.write(self.code)
        with open(prompt_path, "w") as f:
            f.write(self.prompt)
        if metadata_path:
            data = {
                "version": self.version,
                "parent": self.parent,
                "metadata": self.metadata,
            }
            with open(metadata_path, "w") as f:
                json.dump(data, f, indent=2)

    @classmethod
    def load(cls, agent_path: str, prompt_path: str, metadata_path: str = None, **kwargs):
        """Load an EvolvingAgent from files."""
        import json
        parent = None
        metadata = {}
        with open(agent_path, "r") as f:
            code = f.read()
        with open(prompt_path, "r") as f:
            prompt = f.read()
        if metadata_path and os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                md = json.load(f)
                parent = md.get("parent")
                metadata = md.get("metadata", {})
                version = md.get("version", "")
        else:
            version = kwargs.get("version", "v1_0")
        return cls(code=code, prompt=prompt, version=version, parent=parent, metadata=metadata,
                   **kwargs)

        
