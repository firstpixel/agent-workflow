import json
import os
from typing import List, Optional

from Agent import EvolvingAgent
from memory_manager import MemoryManager


class MCSTExecutor:
    """Simplified Monte Carlo Search Tree executor."""

    def __init__(self, branching_factor: int = 2, max_depth: int = 2, work_dir: str = "evolution_runs"):
        self.branching_factor = branching_factor
        self.max_depth = max_depth
        self.work_dir = work_dir

    def _log(self, run_dir: str, data: dict):
        os.makedirs(run_dir, exist_ok=True)
        log_file = os.path.join(run_dir, "tree.json")
        with open(log_file, "w") as f:
            json.dump(data, f, indent=2)

    def run(
        self,
        task,
        initial_agent: EvolvingAgent,
        evolver,
        evaluator,
        judge,
        memory_manager: Optional[MemoryManager] = None,
    ):
        """Run a toy MCST evolution loop."""
        run_dir = os.path.join(self.work_dir, task.description.replace(" ", "_"))
        tree = {"root": initial_agent.version, "nodes": {initial_agent.version: {"parent": None}}}
        current_agent = initial_agent
        depth = 0
        while depth < self.max_depth:
            # generate children via evolver
            children: List[EvolvingAgent] = evolver.generate_mutations(current_agent, self.branching_factor)
            results = []
            for child in children:
                result = evaluator.evaluate(child)
                if memory_manager:
                    memory_manager.add_evolution(
                        branch_id=child.version,
                        parent_id=current_agent.version,
                        code=child.code,
                        prompt=child.prompt,
                        tool=None,
                        score=result,
                        rationale="auto-generated",
                    )
                results.append((child, result))
            winner = judge.choose(results)
            tree["nodes"][winner.version] = {"parent": current_agent.version, "score": winner.metadata.get("score")}
            current_agent = winner
            depth += 1
        self._log(run_dir, tree)
        if memory_manager:
            memory_manager.add_evolution(
                branch_id=current_agent.version,
                parent_id=current_agent.parent,
                code=current_agent.code,
                prompt=current_agent.prompt,
                tool=None,
                score=current_agent.metadata.get("score"),
                rationale="final",
            )
        return current_agent
