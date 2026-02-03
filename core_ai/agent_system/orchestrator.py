from __future__ import annotations

from typing import Dict, Any, List, Optional

from core_ai.agent_system.agents.kb_answer_agent import KBAnswerAgent
from core_ai.agent_system.agents.troubleshooting_agent import TroubleshootingAgent
from core_ai.agent_system.agents.ticket_writer_agent import TicketWriterAgent
from core_ai.agent_system.agents.clarifier_agent import ClarifierAgent


kb_agent = KBAnswerAgent()
troubleshoot_agent = TroubleshootingAgent()
ticket_agent = TicketWriterAgent()
clarifier_agent = ClarifierAgent()

# If score is below this, treat retrieval as irrelevant / weak match
MIN_SOURCE_SCORE = 0.30  # increase to stop random matches (0.25–0.35 works well)


def choose_agent(question: str):
    """
    Router rules:
    - Ticket writing keywords -> ticket agent
    - VPN connect issues or error keywords -> troubleshooting agent
    - Otherwise -> KB agent
    """
    q = (question or "").lower()

    # ITSM / ticket creation
    if any(k in q for k in ["ticket", "jira", "itsm", "servicenow", "service now"]):
        return ticket_agent

    # VPN troubleshooting should ALWAYS go to troubleshooting
    if "vpn" in q and any(
        k in q
        for k in [
            "not connecting",
            "can't connect",
            "cannot connect",
            "not connect",
            "fails",
            "failed",
            "disconnect",
            "timeout",
            "stuck",
        ]
    ):
        return troubleshoot_agent

    # Generic troubleshooting intent
    if any(k in q for k in ["troubleshoot", "not working", "error", "issue", "problem"]):
        return troubleshoot_agent

    return kb_agent


def _normalize_sources(sources: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    if not sources:
        return []

    out: List[Dict[str, Any]] = []
    for s in sources:
        if not isinstance(s, dict):
            continue
        out.append(
            {
                "file": s.get("file", "unknown"),
                "score": s.get("score", None),
                "snippet": s.get("snippet", ""),
            }
        )
    return out


def _max_score(sources: List[Dict[str, Any]]) -> float:
    scores = [s.get("score") for s in sources]
    numeric_scores = [float(x) for x in scores if isinstance(x, (int, float))]
    return max(numeric_scores) if numeric_scores else 0.0


def low_confidence(question: str, result: Dict[str, Any]) -> bool:
    answer = (result.get("answer") or "").lower()
    sources = _normalize_sources(result.get("sources"))

    # 1. No sources → low confidence
    if not sources:
        return True

    # 2. Low similarity score → low confidence
    if _max_score(sources) < MIN_SOURCE_SCORE:
        return True

    # 3. Explicit "not found"
    if "not found in knowledge base" in answer:
        return True

    # 4. NEW: semantic relevance guard
    q_tokens = set(
        w for w in question.lower().split()
        if len(w) > 3  # ignore short noise words
    )

    combined_text = " ".join(
        (s.get("snippet") or "").lower() for s in sources
    )

    # If NONE of the meaningful question words appear in sources → irrelevant hit
    if not any(token in combined_text for token in q_tokens):
        return True

    return False

def run(question: str) -> Dict[str, Any]:
    agent = choose_agent(question)
    result = agent.run(question) or {}
    result["sources"] = _normalize_sources(result.get("sources"))

    # Relevance gate: if KB returns weak/irrelevant retrieval -> clarifier
    if low_confidence(question, result):
        clarified = clarifier_agent.run(question) or {}
        clarified["agent"] = clarifier_agent.name
        clarified["sources"] = _normalize_sources(clarified.get("sources"))
        return {
            "agent": clarified["agent"],
            "answer": clarified.get("answer", ""),
            "sources": clarified["sources"],
        }

    return {
        "agent": agent.name,
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
    }
