class EvaluatorAgent:
    """Simple evaluator that assigns a score based on code length."""

    def evaluate(self, agent):
        score = len(agent.code)
        agent.metadata["score"] = score
        return score
