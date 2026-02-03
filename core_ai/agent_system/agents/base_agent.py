class BaseAgent:
    name = "base"

    def run(self, question: str) -> dict:
        raise NotImplementedError
