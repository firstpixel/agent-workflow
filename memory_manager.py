import json
import os

class MemoryManager:
    def __init__(self, log_file="memory_log.json"):
        self.log_file = log_file
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    def add_evolution(self, branch_id, parent_id, code, prompt, tool, score, rationale):
        entry = {
            "branch_id": branch_id,
            "parent_id": parent_id,
            "score": score,
            "rationale": rationale,
        }
        with open(self.log_file, "r+") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)
