from Agent import LLMAgent, EvolvingAgent

class EvolverAgent(LLMAgent):
    """Generates mutated versions of an EvolvingAgent."""

    def generate_mutations(self, agent: EvolvingAgent, n: int = 2):
        children = []
        for i in range(n):
            new_version = f"{agent.version}_{i}"
            child = EvolvingAgent(
                name=f"{agent.name}_child{i}",
                model_config=agent.model_config,
                system=agent.system,
                prompt=agent.prompt + f" mutation {i}",
                code=agent.code + f"\n# mutation {i}\n",
                version=new_version,
                parent=agent.version,
            )
            child.metadata["score"] = 0
            children.append(child)
        return children
