from core_ai.agent_system.agents.base_agent import BaseAgent

class ClarifierAgent(BaseAgent):
    name = "clarifier"

    def run(self, question: str) -> dict:
        q = question.lower()

        if any(k in q for k in ["leave", "holiday", "annual", "vacation", "hr"]):
            answer = (
                "I don’t have HR policy details in my knowledge base yet.\n"
                "Do you use a specific HR system (e.g., Workday, BambooHR), "
                "or would you like to upload the leave policy document?"
            )
        else:
            answer = (
                "I don’t have enough information to answer accurately.\n"
                "Could you clarify the system, environment, or provide more details?"
            )

        return {
            "answer": answer,
            "sources": []
        }
