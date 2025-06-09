class JudgeAgent:
    """Selects the child with the highest score."""

    def choose(self, results):
        # results is list of (agent, score)
        best = max(results, key=lambda r: r[1])
        return best[0]
