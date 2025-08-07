#!/usr/bin/env python3
"""
Comprehensive Validation Suite for Agent Workflow Project
Performs systematic testing of all components, features, and functionalities.
"""

import os
import sys
import json
import traceback
import tempfile
import shutil
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Set up mock environment for testing
os.environ["MOCK_OLLAMA"] = "1"

# Import project modules
try:
    from Agent import LLMAgent, EvolvingAgent
    from WorkflowManager import WorkflowManager
    from task import Task
    from tool_manager import ToolManager
    from mcst_executor import MCSTExecutor
    from evolver import EvolverAgent
    from evaluator import EvaluatorAgent
    from judge import JudgeAgent
    from assignment import assign_agents_and_tools
    from memory_manager import MemoryManager
    from main import build_workflow_manager, run_demo
    import mock_ollama
except ImportError as e:
    print(f"Failed to import project modules: {e}")
    sys.exit(1)


class ValidationResult:
    """Container for validation test results."""
    
    def __init__(self, test_name: str, passed: bool, message: str = "", details: Dict = None):
        self.test_name = test_name
        self.passed = passed
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()


class ValidationSuite:
    """Comprehensive validation suite for the Agent Workflow project."""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.temp_dir = None
        
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp(prefix="agent_workflow_test_")
        os.makedirs(os.path.join(self.temp_dir, "evolution_runs"), exist_ok=True)
        
    def tearDown(self):
        """Clean up test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def add_result(self, test_name: str, passed: bool, message: str = "", details: Dict = None):
        """Add a test result."""
        result = ValidationResult(test_name, passed, message, details)
        self.results.append(result)
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {test_name}: {message}")
        
    def run_test(self, test_func, test_name: str):
        """Run a single test with exception handling."""
        try:
            test_func()
            self.add_result(test_name, True, "Test completed successfully")
        except Exception as e:
            self.add_result(test_name, False, f"Test failed with exception: {str(e)}", 
                          {"traceback": traceback.format_exc()})
    
    def test_imports_and_dependencies(self):
        """Test 1: Verify all imports work correctly."""
        try:
            # Test core module imports
            assert LLMAgent is not None
            assert EvolvingAgent is not None
            assert WorkflowManager is not None
            assert Task is not None
            
            # Test tool imports
            from tools.echo_tool import run as echo
            from tools.uppercase_tool import run as upper
            from tools.code_executor_tool import run as exec_tool
            assert echo is not None
            assert upper is not None
            assert exec_tool is not None
            
            self.add_result("Import Dependencies", True, "All imports successful")
        except Exception as e:
            self.add_result("Import Dependencies", False, f"Import failed: {str(e)}")
    
    def test_agent_creation(self):
        """Test 2: Test agent creation and basic functionality."""
        model_config = {
            "model": "llama3.2:latest",
            "temperature": 0.7,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        }
        
        # Test LLMAgent creation
        agent = LLMAgent(
            name="TestAgent",
            model_config=model_config,
            system="Test system prompt"
        )
        assert agent.name == "TestAgent"
        assert agent.model_config == model_config
        assert agent.system == "Test system prompt"
        
        # Test agent execution
        result = agent.execute("Test input")
        assert isinstance(result, dict)
        assert "output" in result
        assert "success" in result
        
        self.add_result("Agent Creation", True, "LLMAgent created and executed successfully")
        
    def test_evolving_agent(self):
        """Test 3: Test EvolvingAgent functionality."""
        model_config = {"model": "test", "temperature": 0.7}
        
        agent = EvolvingAgent(
            name="TestEvolving",
            model_config=model_config,
            system="Test system",
            prompt="Test prompt",
            code="print('test')",
            version="v1_0"
        )
        
        assert agent.name == "TestEvolving"
        assert agent.code == "print('test')"
        assert agent.version == "v1_0"
        assert agent.prompt == "Test prompt"
        
        # Test save/load functionality
        agent_path = os.path.join(self.temp_dir, "test_agent.py")
        prompt_path = os.path.join(self.temp_dir, "test_prompt.txt")
        metadata_path = os.path.join(self.temp_dir, "test_metadata.json")
        
        agent.save(agent_path, prompt_path, metadata_path)
        
        assert os.path.exists(agent_path)
        assert os.path.exists(prompt_path)
        assert os.path.exists(metadata_path)
        
        # Test loading
        loaded_agent = EvolvingAgent.load(
            agent_path, prompt_path, metadata_path,
            name="LoadedAgent", model_config=model_config, system="Test"
        )
        
        assert loaded_agent.code == agent.code
        assert loaded_agent.prompt == agent.prompt
        assert loaded_agent.version == agent.version
        
        self.add_result("Evolving Agent", True, "EvolvingAgent save/load functionality works correctly")
    
    def test_workflow_manager(self):
        """Test 4: Test WorkflowManager functionality."""
        manager = WorkflowManager()
        
        model_config = {"model": "test", "temperature": 0.7}
        
        agent1 = LLMAgent(name="Agent1", model_config=model_config, system="Agent 1")
        agent2 = LLMAgent(name="Agent2", model_config=model_config, system="Agent 2")
        
        manager.add_agent(agent1, next_agents=["Agent2"])
        manager.add_agent(agent2, next_agents=None)
        
        assert "Agent1" in manager.agents
        assert "Agent2" in manager.agents
        assert manager.connections["Agent1"] == ["Agent2"]
        assert manager.connections["Agent2"] == []
        
        self.add_result("Workflow Manager", True, "WorkflowManager agent registration works correctly")
    
    def test_tools(self):
        """Test 5: Test tool functionality."""
        from tools.echo_tool import run as echo
        from tools.uppercase_tool import run as upper
        from tools.code_executor_tool import run as exec_tool
        
        # Test echo tool
        result = echo("test input")
        assert result == "test input"
        
        # Test uppercase tool
        result = upper("test input")
        assert result == "TEST INPUT"
        
        # Test code executor tool
        result = exec_tool("print('hello world')")
        assert "hello world" in result
        
        self.add_result("Tool Functionality", True, "All tools execute correctly")
    
    def test_tool_manager(self):
        """Test 6: Test ToolManager functionality."""
        tool_manager = ToolManager()
        
        # Register tools
        tool_manager.register("test_tool", lambda x: f"processed: {x}")
        
        # Test tool execution
        result = tool_manager.run("test_tool", "input")
        assert result == "processed: input"
        
        # Test tool sequence
        tool_manager.register("upper", lambda x: x.upper())
        tool_manager.register("prefix", lambda x: f"PREFIX:{x}")
        
        result = tool_manager.run_sequence(["upper", "prefix"], "test")
        assert result == "PREFIX:TEST"
        
        self.add_result("Tool Manager", True, "ToolManager registration and execution works correctly")
    
    def test_task_functionality(self):
        """Test 7: Test Task class functionality."""
        task = Task(
            description="Test task",
            agent_type="llm",
            pre_tools=["echo"],
            post_tools=["upper"],
            eval_criteria="test criteria"
        )
        
        assert task.description == "Test task"
        assert task.agent_type == "llm"
        assert task.pre_tools == ["echo"]
        assert task.post_tools == ["upper"]
        assert task.status == "pending"
        
        # Test serialization
        task_dict = task.to_dict()
        assert isinstance(task_dict, dict)
        assert task_dict["description"] == "Test task"
        
        task_json = task.to_json()
        assert isinstance(task_json, str)
        
        # Test deserialization
        loaded_task = Task.from_json(task_json)
        assert loaded_task.description == task.description
        assert loaded_task.agent_type == task.agent_type
        
        self.add_result("Task Functionality", True, "Task serialization/deserialization works correctly")
    
    def test_assignment(self):
        """Test 8: Test agent and tool assignment."""
        tasks = [
            Task(description="Generate sample code"),
            Task(description="Echo hello world"),
            Task(description="Process text data")
        ]
        
        tools = ["echo", "upper", "exec"]
        assign_agents_and_tools(tasks, tools)
        
        # Check that assignments were made
        for task in tasks:
            assert task.agent_type == "llm"
            assert isinstance(task.pre_tools, list)
            assert isinstance(task.post_tools, list)
        
        # Verify specific assignments based on keywords
        code_task = next(t for t in tasks if "code" in t.description.lower())
        assert "exec" in code_task.pre_tools
        
        self.add_result("Assignment Logic", True, "Agent and tool assignment works correctly")
    
    def test_evolver_evaluator_judge(self):
        """Test 9: Test MCST components (evolver, evaluator, judge)."""
        model_config = {"model": "test", "temperature": 0.7}
        
        # Test EvolverAgent
        evolver = EvolverAgent(name="evolver", model_config=model_config)
        base_agent = EvolvingAgent(
            name="base", model_config=model_config,
            prompt="base prompt", code="base code", version="v1_0"
        )
        
        children = evolver.generate_mutations(base_agent, n=2)
        assert len(children) == 2
        assert all(isinstance(child, EvolvingAgent) for child in children)
        assert all(child.parent == base_agent.version for child in children)
        
        # Test EvaluatorAgent
        evaluator = EvaluatorAgent()
        score = evaluator.evaluate(children[0])
        assert isinstance(score, int)
        assert "score" in children[0].metadata
        
        # Test JudgeAgent
        judge = JudgeAgent()
        results = [(child, evaluator.evaluate(child)) for child in children]
        winner = judge.choose(results)
        assert isinstance(winner, EvolvingAgent)
        
        self.add_result("MCST Components", True, "Evolver, Evaluator, and Judge work correctly")
    
    def test_mcst_executor(self):
        """Test 10: Test MCSTExecutor functionality."""
        model_config = {"model": "test", "temperature": 0.7}
        
        # Create components
        task = Task(description="test_evolution_task")
        initial_agent = EvolvingAgent(
            name="initial", model_config=model_config,
            prompt="initial prompt", code="initial code", version="v1_0"
        )
        evolver = EvolverAgent(name="evolver", model_config=model_config)
        evaluator = EvaluatorAgent()
        judge = JudgeAgent()
        memory_manager = MemoryManager(log_file=os.path.join(self.temp_dir, "test_memory.json"))
        
        # Run MCST
        executor = MCSTExecutor(branching_factor=2, max_depth=1, work_dir=self.temp_dir)
        best_agent = executor.run(task, initial_agent, evolver, evaluator, judge, memory_manager)
        
        assert isinstance(best_agent, EvolvingAgent)
        assert best_agent.version != initial_agent.version  # Should have evolved
        
        # Check that evolution log was created
        run_dir = os.path.join(self.temp_dir, task.description.replace(" ", "_"))
        tree_file = os.path.join(run_dir, "tree.json")
        assert os.path.exists(tree_file)
        
        with open(tree_file, 'r') as f:
            tree_data = json.load(f)
            assert "root" in tree_data
            assert "nodes" in tree_data
        
        self.add_result("MCST Executor", True, "MCSTExecutor evolution loop works correctly")
    
    def test_memory_manager(self):
        """Test 11: Test MemoryManager functionality."""
        memory_file = os.path.join(self.temp_dir, "test_memory.json")
        memory_manager = MemoryManager(log_file=memory_file)
        
        # Add evolution entry
        memory_manager.add_evolution(
            branch_id="v2_0",
            parent_id="v1_0",
            code="test code",
            prompt="test prompt",
            tool="test tool",
            score=85,
            rationale="test evolution"
        )
        
        # Verify file was created and contains data
        assert os.path.exists(memory_file)
        
        with open(memory_file, 'r') as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) >= 1
            
            entry = data[-1]  # Last entry
            assert entry["branch_id"] == "v2_0"
            assert entry["parent_id"] == "v1_0"
            assert entry["score"] == 85
        
        self.add_result("Memory Manager", True, "MemoryManager logging works correctly")
    
    def test_workflow_execution(self):
        """Test 12: Test complete workflow execution."""
        # Test build_workflow_manager
        manager = build_workflow_manager()
        
        assert "Clarifier" in manager.agents
        assert "Designer" in manager.agents
        assert "TaskMaker" in manager.agents
        
        # Test workflow connections
        assert manager.connections["Clarifier"] == ["Designer"]
        assert manager.connections["Designer"] == ["TaskMaker"]
        assert manager.connections["TaskMaker"] == []
        
        # Test tool registration
        assert "echo" in manager.tool_manager._tools
        assert "upper" in manager.tool_manager._tools
        assert "exec" in manager.tool_manager._tools
        
        self.add_result("Workflow Execution", True, "Complete workflow setup works correctly")
    
    def test_mock_ollama(self):
        """Test 13: Test mock Ollama functionality."""
        response = mock_ollama.chat(
            model="test",
            messages=[{"role": "user", "content": "test message"}]
        )
        
        assert isinstance(response, dict)
        assert "message" in response
        assert "content" in response["message"]
        assert "test message" in response["message"]["content"]
        
        self.add_result("Mock Ollama", True, "Mock Ollama responses work correctly")
    
    def test_error_handling(self):
        """Test 14: Test error handling and edge cases."""
        model_config = {"model": "test", "temperature": 0.7}
        
        # Test agent with invalid tool
        tool_manager = ToolManager()
        try:
            tool_manager.run("nonexistent_tool", "input")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "not registered" in str(e)
        
        # Test agent retry logic
        agent = LLMAgent(
            name="FailingAgent",
            model_config=model_config,
            system="Test",
            retry_limit=2,
            validate_fn=lambda x: False  # Always fail validation
        )
        
        result = agent.run_with_retries("test input")
        assert result["success"] is False
        assert agent.retry_count == 2
        
        self.add_result("Error Handling", True, "Error handling and retry logic work correctly")
    
    def test_file_operations(self):
        """Test 15: Test file I/O operations."""
        # Test EvolvingAgent save/load with missing files
        model_config = {"model": "test", "temperature": 0.7}
        
        agent_path = os.path.join(self.temp_dir, "missing_agent.py")
        prompt_path = os.path.join(self.temp_dir, "missing_prompt.txt")
        
        # Create minimal files
        with open(agent_path, 'w') as f:
            f.write("# test code")
        with open(prompt_path, 'w') as f:
            f.write("test prompt")
        
        # Load without metadata
        loaded_agent = EvolvingAgent.load(
            agent_path, prompt_path,
            name="LoadedAgent", model_config=model_config, system="Test"
        )
        
        assert loaded_agent.code == "# test code"
        assert loaded_agent.prompt == "test prompt"
        assert loaded_agent.version == "v1_0"  # Default version
        
        self.add_result("File Operations", True, "File I/O operations work correctly")
    
    def run_all_tests(self):
        """Run all validation tests."""
        print("=" * 60)
        print("AGENT WORKFLOW PROJECT - COMPREHENSIVE VALIDATION SUITE")
        print("=" * 60)
        
        self.setUp()
        
        try:
            # Core functionality tests
            self.run_test(self.test_imports_and_dependencies, "Import Dependencies")
            self.run_test(self.test_agent_creation, "Agent Creation")
            self.run_test(self.test_evolving_agent, "Evolving Agent")
            self.run_test(self.test_workflow_manager, "Workflow Manager")
            self.run_test(self.test_tools, "Tool Functionality")
            self.run_test(self.test_tool_manager, "Tool Manager")
            self.run_test(self.test_task_functionality, "Task Functionality")
            self.run_test(self.test_assignment, "Assignment Logic")
            
            # MCST and evolution tests
            self.run_test(self.test_evolver_evaluator_judge, "MCST Components")
            self.run_test(self.test_mcst_executor, "MCST Executor")
            self.run_test(self.test_memory_manager, "Memory Manager")
            
            # Integration tests
            self.run_test(self.test_workflow_execution, "Workflow Execution")
            self.run_test(self.test_mock_ollama, "Mock Ollama")
            
            # Edge case and error tests
            self.run_test(self.test_error_handling, "Error Handling")
            self.run_test(self.test_file_operations, "File Operations")
            
        finally:
            self.tearDown()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp
                }
                for r in self.results
            ],
            "failed_tests": [
                {
                    "test_name": r.test_name,
                    "message": r.message,
                    "details": r.details
                }
                for r in self.results if not r.passed
            ]
        }
        
        return report
    
    def print_summary(self):
        """Print test summary."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\nFAILED TESTS:")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.test_name}: {result.message}")
        
        print("=" * 60)


def main():
    """Main validation entry point."""
    suite = ValidationSuite()
    suite.run_all_tests()
    suite.print_summary()
    
    # Save detailed report
    report = suite.generate_report()
    with open("validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: validation_report.json")
    
    # Return exit code based on test results
    failed_tests = sum(1 for r in suite.results if not r.passed)
    return 0 if failed_tests == 0 else 1


if __name__ == "__main__":
    sys.exit(main())