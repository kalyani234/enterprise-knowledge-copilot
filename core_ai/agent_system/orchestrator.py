# core_ai/agent_system/orchestrator.py

from core_ai.agent_system.agents.kb_answer_agent import KBAnswerAgent
from core_ai.agent_system.agents.troubleshooting_agent import TroubleshootingAgent
from core_ai.agent_system.agents.ticket_writer_agent import TicketWriterAgent
from core_ai.agent_system.agents.clarifier_agent import ClarifierAgent


# Instantiate agents once (cheap + reusable)
kb_agent = KBAnswerAgent()
troubleshoot_agent = TroubleshootingAgent()
ticket_agent = TicketWriterAgent()
clarifier_agent = ClarifierAgent()


def choose_agent(question: str):
    """
    Very simple router based on keywords.
    """
    q = question.lower()

    # Ticket writing / ITSM
    if any(k in q for k in ["ticket", "jira", "itsm"]):
        return ticket_agent

    # Troubleshooting / incident-like language
    if any(
        k in q
        for k in [
            "troubleshoot",
            "not working",
            "error",
            "issue",
            "failed",
            "fails",
            "cannot connect",
            "can't connect",
            "not connecting",
        ]
    ):
        return troubleshoot_agent

    # Default: knowledge base answer
    return kb_agent


def low_confidence(question: str, result: dict) -> bool:
    """
    Decide when to fall back to ClarifierAgent.

    Rules:
    - If no sources => low confidence
    - If top score is very low => low confidence
    - If question is clearly VPN/WiFi but the top source doesn't mention that domain => low confidence
    - If question contains maternity but top source doesn't mention maternity => low confidence
    """
    sources = result.get("sources") or []
    if not sources:
        return True

    top = sources[0]
    score = top.get("score", None)
    top_file = (top.get("file") or "").lower()
    top_snip = (top.get("snippet") or "").lower()

    # Score gate (not too strict, otherwise valid results get blocked)
    try:
        if score is None or float(score) < 0.15:
            return True
    except Exception:
        return True

    q = question.lower()

    # Domain gating (prevents wrong-domain matches)
    if "vpn" in q:
        if ("vpn" not in top_file) and ("vpn" not in top_snip):
            return True

    if "wifi" in q or "wi-fi" in q:
        if ("wifi" not in top_file) and ("wi-fi" not in top_file) and ("wifi" not in top_snip) and ("wi-fi" not in top_snip):
            return True

    # HR-specific: "maternity" must be present, otherwise treat as not found
    if "maternity" in q:
        if ("maternity" not in top_file) and ("maternity" not in top_snip):
            return True

    return False


def run(question: str) -> dict:
    """
    Main entry point called by FastAPI.
    Chooses an agent, runs it, then applies confidence checks.
    """
    agent = choose_agent(question)
    result = agent.run(question)

    # If retrieval seems weak or wrong-domain, ask clarifying question instead of hallucinating
    if low_confidence(question, result):
        clarified = clarifier_agent.run(question)
        clarified["agent"] = clarifier_agent.name
        return clarified

    # Attach agent name for UI display
    result["agent"] = agent.name
    return result
