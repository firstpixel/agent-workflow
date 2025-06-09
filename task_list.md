# 🏗️ **MCST Agentic Framework — Implementation Task List (v1)**

---

## **Priority 1: Core Foundations**

---

### **1. Implement Generic LLM Agent Class (`LLMAgent`)**

* **Description:** Build a generic class that can be instantiated with any prompt and LLM client, for all static roles.
* **Sample:**

  ```python
  agent = LLMAgent(name="Clarifier", prompt_template="Ask clarifying questions...", llm_client=my_llm)
  ```
* **Depends on:** None
* **Input:** `prompt_template`, `llm_client`, `input_data`
* **Prompt:** As provided per role (clarifier, designer, etc.)
* **Output:** LLM response text
* **Goal:** All roles can use the same class, with only a prompt swap.
* **Verification:** Instantiate and run Clarifier, Designer, TaskLister, Evaluator, and Judge agents with different prompts; each returns a plausible response.

---

### **2. Implement ToolManager (Register, Call, and Sequence Tools)**

* **Description:** Create a class for registering tools and executing them by name; support running a sequence for pre- and post-processing.
* **Sample:**

  ```python
  tool_manager.register("code_executor", code_executor_tool)
  tool_manager.run_sequence(["web_search", "code_executor"], input)
  ```
* **Depends on:** None
* **Input:** Tool names, tool functions/classes, tool input data
* **Prompt:** N/A (direct code)
* **Output:** Tool result(s)
* **Goal:** All tools (static or evolving) can be called by name or as a list.
* **Verification:** Register three tools (e.g., web search, code executor, summarizer); run them in sequence; outputs must appear in expected order.

---

### **3. Define `Task` Class (task.py)**

* **Description:** Represent each task with all metadata (description, agent, tool lists, eval criteria, history, etc.)
* **Sample:**

  ```python
  task = Task(description="Create API", agent_type="evolving", pre_tools=["web_search"], post_tools=["code_executor"], eval_criteria="All tests pass")
  ```
* **Depends on:** None
* **Input:** All fields for task (as above)
* **Prompt:** N/A
* **Output:** Task instance
* **Goal:** Can create, serialize, and log tasks with all metadata.
* **Verification:** Instantiate and serialize to JSON; all fields persist.

---

## **Priority 2: Workflow and Basic Flow**

---

### **4. Implement WorkflowManager (Basic, Linear Workflow)**

* **Description:** Manage main flow: user prompt → clarifier → designer → task list → assign agents/tools.
* **Sample:**

  ```python
  workflow = WorkflowManager()
  workflow.run(user_input)
  ```
* **Depends on:** 1, 2, 3
* **Input:** User input, agent and tool registry
* **Prompt:** Uses agent prompts for each step
* **Output:** Clarified requirements, system design, task list, task assignments
* **Goal:** Can execute full linear planning phase and print all intermediate results.
* **Verification:** Run with "Build a ToDo app"; output should show all stages: clarification, design, task list, and agent/tool assignment.

---

### **5. Implement Agent & Tool Assignment Step**

* **Description:** Create a dedicated step that assigns the appropriate agent type and tool sequence to each task produced by the TaskLister.
* **Sample:**

  ```python
  assignment = assign_agents_and_tools(task_list, tool_registry)
  ```
* **Depends on:** 1, 2, 3, 4
* **Input:** Task list, available agents, available tools
* **Prompt:** Uses assignment prompt
* **Output:** Updated tasks with assigned agents and tool sequences
* **Goal:** Each task specifies which agent to use and which tools to run before and after execution.
* **Verification:** Generated tasks include valid agent and tool assignments that the workflow can process.

---

### **6. Build Initial Immutable Tools (`tools/`)**

* **Description:** Implement minimal, immutable tool scripts for file I/O, code execution, GitHub commit.
* **Sample:** `tools/code_executor_tool.py`
* **Depends on:** 2
* **Input:** Tool-specific (e.g., code string for executor)
* **Prompt:** N/A
* **Output:** Tool-specific result (e.g., code output, file written)
* **Goal:** All pre/post task tools in the workflow can be executed and tested.
* **Verification:** Each tool runs independently and via ToolManager; returns expected output.

---

## **Priority 3: MCST Evolutionary Engine**

---

### **7. Implement `EvolvingAgent` Class (agent code/prompt versioning)**

* **Description:** Handles versioned agent code, prompt, and metadata for MCST. Can load, save, and serialize its state.
* **Sample:**

  ```python
  agent = EvolvingAgent(code="...", prompt="...", version="v1_0", parent=None)
  agent.save("/agents/evolving_agents/evolution_run_1/v1_0_agent.py", "/agents/evolving_agents/evolution_run_1/v1_0_prompt.txt")
  ```
* **Depends on:** 1, 3
* **Input:** Code string, prompt string, parent/version info
* **Prompt:** Evolving agent prompt
* **Output:** Saved code and prompt files
* **Goal:** Can create, save, and retrieve versioned agent artifacts.
* **Verification:** Save/load several generations; check files and metadata are correct.

---

### **8. Implement MCSTExecutor (Evolutionary Tree/Loop)**

* **Description:** Controls branching, mutation, testing, and pruning of agent code, prompt, and tools for each executable task.
* **Sample:**

  ```python
  mcst = MCSTExecutor()
  mcst.run(task, initial_agent)
  ```
* **Depends on:** 2, 3, 6
* **Input:** Task instance, initial EvolvingAgent, branching factor (N), stopping criteria
* **Prompt:** N/A (delegates to evolver agent)
* **Output:** Tree/log of all candidate branches, lineage, and the best solution
* **Goal:** Evolves agents/tools/prompts for a task using MCST; only best child survives each layer; all artifacts/versioning preserved.
* **Verification:** Run on a small code-gen task; produces multiple candidate agents (with files), tests/evaluates, selects winner per round, lineage log builds as expected.

---

### **9. Build Evolver Agent (Prompt/Code/Tool Mutation via LLM)**

* **Description:** Use the generic LLMAgent class with a prompt to propose **N diverse mutations** (code, prompt, tool) per MCST branch.
* **Sample Prompt:**

  ```
  "Given the following code and feedback, generate two distinct new versions: ..."
  ```
* **Depends on:** 1, 7
* **Input:** Agent code, prompt, tool code/config, feedback/test results
* **Prompt:** Diversity-promoting mutation prompt (see previous response)
* **Output:** N new code/prompt/tool versions, each with a rationale
* **Goal:** Always produces diverse, plausible new candidates for MCST branching.
* **Verification:** LLM output includes two (or N) substantially different branches for given agent.

---

### **10. Build Evaluator Agent (LLM or code-based)**

* **Description:** Scores candidate outputs (code, results, etc.) against test cases and evaluation criteria.
* **Sample Prompt:**

  ```
  "Evaluate the following code and output. Did it pass the tests?"
  ```
* **Depends on:** 1
* **Input:** Candidate output, expected results, evaluation criteria
* **Prompt:** Evaluation prompt
* **Output:** Pass/fail/score/feedback for each candidate
* **Goal:** Can reliably score and critique any generated candidate.
* **Verification:** Known-good and known-bad code are correctly evaluated by agent.

---

### **11. Build Judge Agent (LLM for Selection/Hybridization)**

* **Description:** Given a set of candidate outputs (branches), chooses the best (or merges/hybridizes as needed).
* **Sample Prompt:**

  ```
  "Given these two candidate solutions and their test results, pick the best one or propose a merge."
  ```
* **Depends on:** 1, 9
* **Input:** List of candidate results, evaluation scores
* **Prompt:** Judge prompt
* **Output:** Name of winning branch or a merged solution
* **Goal:** Always selects or proposes a single best candidate per MCST layer.
* **Verification:** On synthetic scenarios, always chooses the correct candidate.

---

## **Priority 4: Versioning, Lineage, Logging, and Extensibility**

---

### **12. Implement Versioning and Lineage Tracking**

* **Description:** Save all agents/prompts/tools as versioned files with lineage and mutation metadata; log MCST tree.
* **Sample:**

  ```
  /agents/evolving_agents/evolution_run_1/v2_0_agent.py
  /agents/evolving_agents/evolution_run_1/v2_0_prompt.txt
  /agents/evolving_agents/evolution_run_1/v2_0_metadata.json
  ```
* **Depends on:** 6, 7
* **Input:** Code, prompt, tool, parent/version info, mutation rationale, eval scores
* **Prompt:** N/A
* **Output:** Versioned files and tree/log
* **Goal:** All artifacts traceable to parent; all results auditable.
* **Verification:** For any agent, prompt, or tool file, lineage/metadata is complete and correct.

---

### **13. Implement Evolution Log and MCST Tree Serialization**

* **Description:** Persist MCST tree and evolution logs for each run, including all branches, parents, scores, and outcomes.
* **Sample:**

  ```
  /evolution_logs/evolution_run_1_tree.json
  ```
* **Depends on:** 7, 11
* **Input:** All MCSTExecutor artifacts, version/branch info, evaluation results
* **Prompt:** N/A
* **Output:** Serialized evolution tree/log file
* **Goal:** Tree log can be loaded and traversed; branch lineage can be visualized.
* **Verification:** MCST logs match the file system and all evaluations.

---

### **14. Implement/Integrate Basic MemoryManager**

* **Description:** Log every candidate, score, mutation, and branch for replay, audits, and analysis.
* **Sample:**

  ```
  memory_manager.add_evolution(branch_id, parent_id, code, prompt, tool, score, rationale)
  ```
* **Depends on:** 11, 12
* **Input:** All versioned artifacts, logs, scores
* **Prompt:** N/A
* **Output:** Memory/log database or file
* **Goal:** Any result, code, prompt, or tool can be traced and replayed.
* **Verification:** Run queries to reconstruct evolution history for a given run.

---

## **Priority 5: Full Orchestration and Workflow Testing**

---

### **15. Integrate Everything in Main Workflow**

* **Description:** Wire all classes and flows: user input, planning, assignment, MCST per task, evolution, testing, and selection.
* **Sample:**

  ```python
  workflow = WorkflowManager(...)
  workflow.run(user_input)
  ```
* **Depends on:** 1–13
* **Input:** User prompt, system modules
* **Prompt:** All per-agent prompts
* **Output:** Completed solution, all artifacts/logs
* **Goal:** End-to-end scenario completes, all outputs versioned, all logs correct.
* **Verification:** Run test case from prompt to solution, inspect tree/logs/artifacts.

---

### **16. Validation, Automated Testing, and CI**

* **Description:** Unit tests for each module; scenario tests for end-to-end runs.
* **Sample:** pytest, unittests, or notebook-based tests.
* **Depends on:** All prior
* **Input:** Synthetic and real user prompts, test scripts
* **Prompt:** N/A
* **Output:** Test results, code coverage
* **Goal:** All modules are robust; framework can be used for experiments and further extension.
* **Verification:** All critical paths covered; CI green.

