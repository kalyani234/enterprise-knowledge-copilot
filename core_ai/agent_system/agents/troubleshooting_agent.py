from core_ai.agent_system.agents.base_agent import BaseAgent
from core_ai.agent_system.tools.retrieve_tool import retrieve


class TroubleshootingAgent(BaseAgent):
    name = "troubleshooting"

    def run(self, question: str) -> dict:
        q = question.lower()

        # Keep retrieval queries short + intent-only (best for embeddings)
        if "vpn" in q and any(k in q for k in ["not connecting", "can't connect", "cannot connect", "fails", "failed"]):
            return retrieve("vpn not connecting troubleshooting steps", top_k=2)

        if "wifi" in q or "wi-fi" in q:
            return retrieve("wifi troubleshooting steps", top_k=2)

        # Default to raw question
        return retrieve(question, top_k=2)
