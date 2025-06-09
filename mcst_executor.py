import json
import os
from typing import List

from Agent import EvolvingAgent


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

    def run(self, task, initial_agent: EvolvingAgent, evolver, evaluator, judge):
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
                results.append((child, result))
            winner = judge.choose(results)
            tree["nodes"][winner.version] = {"parent": current_agent.version, "score": winner.metadata.get("score")}
            current_agent = winner
            depth += 1
        self._log(run_dir, tree)
        return current_agent
