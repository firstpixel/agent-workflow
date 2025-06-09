import json
from dataclasses import dataclass, field
from typing import List

@dataclass
class Task:
    """Represents a single executable task."""

    description: str
    agent_type: str = "llm"
    pre_tools: List[str] = field(default_factory=list)
    post_tools: List[str] = field(default_factory=list)
    eval_criteria: str = ""
    status: str = "pending"
    history: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "description": self.description,
            "agent_type": self.agent_type,
            "pre_tools": self.pre_tools,
            "post_tools": self.post_tools,
            "eval_criteria": self.eval_criteria,
            "status": self.status,
            "history": self.history,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, data: str):
        obj = json.loads(data)
        return cls(**obj)
