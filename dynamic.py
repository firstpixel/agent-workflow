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

import ollama

class LLMTaskAgent:
    def __init__(self, model_name, task_description, system_prompt):
        self.model = model_name
        self.task_description = task_description
        self.system_prompt = system_prompt

    def execute_task(self):
        response = ollama.chat(
            model=self.model,
            stream=False,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.task_description}
            ],
            options={"temperature": 0.7, "max_tokens": 500}
        )
        print(f"LLMTaskAgent : {response}")
        output = response['message']['content'].strip()
        return output

class ValidationAgent:
    def __init__(self, model_name, criteria):
        self.model = model_name
        self.criteria = criteria


    def validate_task(self, task_output):
        validation_response = ollama.chat(
            model=self.model,
            stream=False,
            messages=[
                {"role": "system", "content": f"Check if the task meets criteria: {self.criteria}"},
                {"role": "assistant", "content": task_output}
            ],
            options={"temperature": 0.2}
        )
        print(f"ValidationAgent : {validation_response}")
        output = validation_response['message']['content'].strip()
        return output

class WorkflowManager:
    def __init__(self, model_name):
        self.model = model_name
        self.tasks = []

    def add_task(self, task_description, system_prompt):
        task_agent = LLMTaskAgent(self.model, task_description, system_prompt)
        self.tasks.append({"task_agent": task_agent, "validated": False})
        print(f"TASK DESCRIPTION : {task_description}, SYSTEM: {system_prompt}")

    def run(self):
        final_results = []
        for task in self.tasks:
            task_output = task["task_agent"].execute_task()
            
            # Validate output
            validator = ValidationAgent(self.model, "Make sure it is correct and complete.")
            validation_response = validator.validate_task(task_output)
            
            # Check if validation succeeded
            if "Task is valid" in validation_response:
                task["validated"] = True
                final_results.append(task_output)
            else:
                task["task_agent"].task_description += f" Please correct the following: {validation_response}"
        
        # Synthesize results
        return "\n".join(final_results)

# Example Usage
# workflow = WorkflowManager(model_name="llama3.2:1b")
# workflow.add_task("Find the shortest path from A to D using Dijkstra’s algorithm.", "Split the problem into steps.")
# workflow.add_task("Each step should have clear instructions for the next task.", "Ensure clarity.")
# final_solution = workflow.run()
# print(final_solution)
