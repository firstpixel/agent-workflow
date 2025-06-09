class ToolManager:
    """Registry and executor for tools."""

    def __init__(self):
        self._tools = {}

    def register(self, name, func):
        """Register a tool function by name."""
        self._tools[name] = func

    def run(self, name, *args, **kwargs):
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not registered")
        return self._tools[name](*args, **kwargs)

    def run_sequence(self, tools, input_data=None):
        data = input_data
        for name in tools:
            data = self.run(name, data)
        return data
