from core_ai.agent_system.agents.base_agent import BaseAgent
from core_ai.agent_system.tools.retrieve_tool import retrieve

class KBAnswerAgent(BaseAgent):
    name = "kb_answer"

    def run(self, question: str) -> dict:
        return retrieve(question, top_k=2)
