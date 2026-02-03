from core_ai.agent_system.agents.base_agent import BaseAgent
from core_ai.agent_system.tools.format_ticket_tool import format_ticket

class TicketWriterAgent(BaseAgent):
    name = "ticket_writer"

    def run(self, question: str) -> dict:
        return format_ticket(question)
