#!/usr/bin/env python3
"""
Performance and Stress Testing for Agent Workflow Project
Tests system behavior under various load and edge conditions.
"""

import os
import time
import threading
import tempfile
import shutil
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
import json

# Set mock environment
os.environ["MOCK_OLLAMA"] = "1"

from Agent import LLMAgent, EvolvingAgent
from WorkflowManager import WorkflowManager
from task import Task
from mcst_executor import MCSTExecutor
from evolver import EvolverAgent
from evaluator import EvaluatorAgent
from judge import JudgeAgent
from memory_manager import MemoryManager
from main import build_workflow_manager


class PerformanceTester:
    """Performance and stress testing suite."""
    
    def __init__(self):
        self.results = {}
        self.temp_dir = tempfile.mkdtemp(prefix="perf_test_")
    
    def cleanup(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_agent_creation_performance(self):
        """Test agent creation performance."""
        print("Testing agent creation performance...")
        
        model_config = {"model": "test", "temperature": 0.7}
        
        # Test creating many agents
        start_time = time.time()
        agents = []
        for i in range(100):
            agent = LLMAgent(
                name=f"Agent{i}",
                model_config=model_config,
                system=f"System prompt {i}"
            )
            agents.append(agent)
        
        creation_time = time.time() - start_time
        
        self.results['agent_creation'] = {
            'agents_created': len(agents),
            'time_seconds': creation_time,
            'agents_per_second': len(agents) / creation_time
        }
        
        print(f"Created {len(agents)} agents in {creation_time:.3f}s ({len(agents)/creation_time:.1f} agents/sec)")
    
    def test_workflow_execution_performance(self):
        """Test workflow execution performance."""
        print("Testing workflow execution performance...")
        
        manager = build_workflow_manager()
        
        # Test multiple workflow executions
        start_time = time.time()
        executions = 10
        
        for i in range(executions):
            try:
                # Use non-interactive mode to avoid user input
                manager.run_workflow(
                    start_agent_name="Designer",
                    input_data=f"Test workflow {i}",
                    interactive=False
                )
            except Exception as e:
                print(f"Workflow {i} failed: {e}")
        
        execution_time = time.time() - start_time
        
        self.results['workflow_execution'] = {
            'executions': executions,
            'time_seconds': execution_time,
            'executions_per_second': executions / execution_time
        }
        
        print(f"Executed {executions} workflows in {execution_time:.3f}s ({executions/execution_time:.2f} workflows/sec)")
    
    def test_mcst_performance(self):
        """Test MCST evolution performance."""
        print("Testing MCST evolution performance...")
        
        model_config = {"model": "test", "temperature": 0.7}
        
        # Create MCST components
        task = Task(description="performance_test_task")
        initial_agent = EvolvingAgent(
            name="initial",
            model_config=model_config,
            prompt="initial prompt",
            code="initial code",
            version="v1_0"
        )
        evolver = EvolverAgent(name="evolver", model_config=model_config)
        evaluator = EvaluatorAgent()
        judge = JudgeAgent()
        memory_manager = MemoryManager(log_file=os.path.join(self.temp_dir, "perf_memory.json"))
        
        # Test MCST with different configurations
        configurations = [
            {"branching_factor": 2, "max_depth": 1},
            {"branching_factor": 3, "max_depth": 2},
            {"branching_factor": 2, "max_depth": 3},
        ]
        
        mcst_results = []
        
        for config in configurations:
            start_time = time.time()
            
            executor = MCSTExecutor(
                branching_factor=config["branching_factor"],
                max_depth=config["max_depth"],
                work_dir=self.temp_dir
            )
            
            best_agent = executor.run(task, initial_agent, evolver, evaluator, judge, memory_manager)
            
            execution_time = time.time() - start_time
            
            result = {
                'config': config,
                'time_seconds': execution_time,
                'final_version': best_agent.version
            }
            mcst_results.append(result)
            
            print(f"MCST {config} took {execution_time:.3f}s, final version: {best_agent.version}")
        
        self.results['mcst_performance'] = mcst_results
    
    def test_concurrent_agents(self):
        """Test concurrent agent execution."""
        print("Testing concurrent agent execution...")
        
        model_config = {"model": "test", "temperature": 0.7}
        
        def run_agent(agent_id):
            """Run a single agent."""
            agent = LLMAgent(
                name=f"ConcurrentAgent{agent_id}",
                model_config=model_config,
                system="Concurrent test"
            )
            
            results = []
            for i in range(5):
                result = agent.execute(f"Input {i}")
                results.append(result)
                time.sleep(0.01)  # Small delay to simulate work
            
            return len([r for r in results if r['success']])
        
        # Test with different thread counts
        thread_counts = [1, 2, 4, 8]
        concurrent_results = []
        
        for thread_count in thread_counts:
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = [executor.submit(run_agent, i) for i in range(thread_count * 2)]
                successful_executions = sum(f.result() for f in futures)
            
            execution_time = time.time() - start_time
            
            result = {
                'thread_count': thread_count,
                'total_agents': thread_count * 2,
                'successful_executions': successful_executions,
                'time_seconds': execution_time
            }
            concurrent_results.append(result)
            
            print(f"Threads: {thread_count}, Agents: {thread_count * 2}, "
                  f"Success: {successful_executions}, Time: {execution_time:.3f}s")
        
        self.results['concurrent_execution'] = concurrent_results
    
    def test_memory_usage(self):
        """Test memory usage patterns."""
        print("Testing memory usage...")
        
        model_config = {"model": "test", "temperature": 0.7}
        
        # Create many agents and measure memory growth
        agents = []
        memory_samples = []
        
        try:
            import psutil
            process = psutil.Process()
            
            for i in range(0, 200, 10):
                # Create 10 agents
                for j in range(10):
                    agent = EvolvingAgent(
                        name=f"MemAgent{i+j}",
                        model_config=model_config,
                        prompt=f"Prompt {i+j}" * 10,  # Make it larger
                        code=f"# Code {i+j}\n" * 20,
                        version=f"v{i+j}_0"
                    )
                    agents.append(agent)
                
                # Sample memory usage
                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_samples.append({
                    'agent_count': len(agents),
                    'memory_mb': memory_mb
                })
            
            self.results['memory_usage'] = {
                'samples': memory_samples,
                'peak_memory_mb': max(s['memory_mb'] for s in memory_samples),
                'final_agent_count': len(agents)
            }
            
            print(f"Peak memory: {max(s['memory_mb'] for s in memory_samples):.1f} MB "
                  f"with {len(agents)} agents")
                  
        except ImportError:
            print("psutil not available, skipping memory test")
            self.results['memory_usage'] = {'error': 'psutil not available'}
    
    def test_file_io_performance(self):
        """Test file I/O performance."""
        print("Testing file I/O performance...")
        
        model_config = {"model": "test", "temperature": 0.7}
        
        # Test saving/loading many EvolvingAgents
        agents = []
        for i in range(50):
            agent = EvolvingAgent(
                name=f"FileAgent{i}",
                model_config=model_config,
                prompt=f"Prompt {i}" * 50,  # Larger content
                code=f"# Code {i}\nprint('test {i}')\n" * 10,
                version=f"v{i}_0"
            )
            agents.append(agent)
        
        # Test save performance
        save_start = time.time()
        for i, agent in enumerate(agents):
            agent_path = os.path.join(self.temp_dir, f"agent_{i}.py")
            prompt_path = os.path.join(self.temp_dir, f"prompt_{i}.txt")
            metadata_path = os.path.join(self.temp_dir, f"metadata_{i}.json")
            agent.save(agent_path, prompt_path, metadata_path)
        save_time = time.time() - save_start
        
        # Test load performance
        load_start = time.time()
        loaded_agents = []
        for i in range(len(agents)):
            agent_path = os.path.join(self.temp_dir, f"agent_{i}.py")
            prompt_path = os.path.join(self.temp_dir, f"prompt_{i}.txt")
            metadata_path = os.path.join(self.temp_dir, f"metadata_{i}.json")
            loaded_agent = EvolvingAgent.load(
                agent_path, prompt_path, metadata_path,
                name=f"LoadedAgent{i}", model_config=model_config, system="Test"
            )
            loaded_agents.append(loaded_agent)
        load_time = time.time() - load_start
        
        self.results['file_io'] = {
            'agents_tested': len(agents),
            'save_time_seconds': save_time,
            'load_time_seconds': load_time,
            'saves_per_second': len(agents) / save_time,
            'loads_per_second': len(agents) / load_time
        }
        
        print(f"Saved {len(agents)} agents in {save_time:.3f}s ({len(agents)/save_time:.1f}/sec)")
        print(f"Loaded {len(loaded_agents)} agents in {load_time:.3f}s ({len(loaded_agents)/load_time:.1f}/sec)")
    
    def test_stress_scenarios(self):
        """Test stress scenarios and edge cases."""
        print("Testing stress scenarios...")
        
        model_config = {"model": "test", "temperature": 0.7}
        
        stress_results = {}
        
        # Test 1: Very long inputs
        agent = LLMAgent(name="StressAgent", model_config=model_config, system="Stress test")
        long_input = "This is a very long input. " * 1000  # ~25KB input
        
        start_time = time.time()
        result = agent.execute(long_input)
        long_input_time = time.time() - start_time
        
        stress_results['long_input'] = {
            'input_length': len(long_input),
            'success': result['success'],
            'time_seconds': long_input_time
        }
        
        # Test 2: Many rapid executions
        rapid_start = time.time()
        rapid_results = []
        for i in range(100):
            result = agent.execute(f"Rapid test {i}")
            rapid_results.append(result['success'])
        rapid_time = time.time() - rapid_start
        
        stress_results['rapid_execution'] = {
            'executions': len(rapid_results),
            'success_count': sum(rapid_results),
            'time_seconds': rapid_time,
            'executions_per_second': len(rapid_results) / rapid_time
        }
        
        # Test 3: Deep MCST evolution
        try:
            task = Task(description="deep_stress_test")
            initial_agent = EvolvingAgent(
                name="DeepStress", model_config=model_config,
                prompt="stress", code="stress", version="v1_0"
            )
            evolver = EvolverAgent(name="evolver", model_config=model_config)
            evaluator = EvaluatorAgent()
            judge = JudgeAgent()
            memory_manager = MemoryManager(log_file=os.path.join(self.temp_dir, "stress_memory.json"))
            
            deep_start = time.time()
            executor = MCSTExecutor(branching_factor=3, max_depth=4, work_dir=self.temp_dir)
            best_agent = executor.run(task, initial_agent, evolver, evaluator, judge, memory_manager)
            deep_time = time.time() - deep_start
            
            stress_results['deep_mcst'] = {
                'max_depth': 4,
                'branching_factor': 3,
                'time_seconds': deep_time,
                'final_version': best_agent.version,
                'success': True
            }
            
        except Exception as e:
            stress_results['deep_mcst'] = {
                'error': str(e),
                'success': False
            }
        
        self.results['stress_scenarios'] = stress_results
        
        print(f"Long input ({len(long_input)} chars): {long_input_time:.3f}s")
        print(f"Rapid execution (100 calls): {rapid_time:.3f}s ({len(rapid_results)/rapid_time:.1f}/sec)")
    
    def run_all_tests(self):
        """Run all performance tests."""
        print("=" * 60)
        print("AGENT WORKFLOW PROJECT - PERFORMANCE & STRESS TESTING")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            self.test_agent_creation_performance()
            self.test_workflow_execution_performance()
            self.test_mcst_performance()
            self.test_concurrent_agents()
            self.test_memory_usage()
            self.test_file_io_performance()
            self.test_stress_scenarios()
            
            total_time = time.time() - start_time
            self.results['total_test_time'] = total_time
            
            print(f"\nAll performance tests completed in {total_time:.2f} seconds")
            
        finally:
            self.cleanup()
    
    def generate_report(self):
        """Generate performance test report."""
        return {
            'timestamp': time.time(),
            'results': self.results,
            'summary': {
                'total_test_time': self.results.get('total_test_time', 0),
                'tests_run': len(self.results) - 1,  # Exclude total_test_time
            }
        }
    
    def print_summary(self):
        """Print performance test summary."""
        print("\n" + "=" * 60)
        print("PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        
        if 'agent_creation' in self.results:
            ac = self.results['agent_creation']
            print(f"Agent Creation: {ac['agents_per_second']:.1f} agents/sec")
        
        if 'workflow_execution' in self.results:
            we = self.results['workflow_execution']
            print(f"Workflow Execution: {we['executions_per_second']:.2f} workflows/sec")
        
        if 'file_io' in self.results:
            fio = self.results['file_io']
            print(f"File I/O: {fio['saves_per_second']:.1f} saves/sec, {fio['loads_per_second']:.1f} loads/sec")
        
        if 'memory_usage' in self.results and 'peak_memory_mb' in self.results['memory_usage']:
            mu = self.results['memory_usage']
            print(f"Peak Memory: {mu['peak_memory_mb']:.1f} MB with {mu['final_agent_count']} agents")
        
        print("=" * 60)


def main():
    """Main performance testing entry point."""
    tester = PerformanceTester()
    tester.run_all_tests()
    tester.print_summary()
    
    # Save detailed report
    report = tester.generate_report()
    with open("performance_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed performance report saved to: performance_report.json")
    return 0


if __name__ == "__main__":
    exit(main())