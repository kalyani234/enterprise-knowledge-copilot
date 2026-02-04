# core_ai/agent_system/orchestrator.py
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

MIN_SOURCE_SCORE = 0.20

STOPWORDS = {
    "company", "policy", "process", "steps", "step", "please", "help",
    "how", "what", "why", "when", "where", "which", "tell", "explain",
    "guide", "details", "procedure", "info", "information",
    "apply", "request", "create", "new", "issue", "problem",
}

# Topic keywords per file (keep these specific; avoid broad words like "annual")
FILE_TOPIC_KEYWORDS: Dict[str, List[str]] = {
    "hr_leave_policy.txt": ["leave", "holiday", "workday", "time off", "annual leave"],
    "it_hardware_request.txt": ["laptop", "monitor", "hardware", "itsm", "service portal", "hardware request"],
    "it_onboarding.txt": ["onboarding", "new employee", "starter", "join", "setup"],
    "wifi_troubleshooting.txt": ["wifi", "wi-fi", "wireless", "router", "ssid", "internet"],
    "vpn_runbook.txt": ["vpn", "client", "dns", "connect", "connection"],
    "vpn_installation.txt": ["vpn", "install", "installation", "setup", "configure"],
    "vpn_common_errors.txt": ["vpn", "error", "code", "691", "auth", "authentication"],
    "account_password_reset.txt": ["password", "reset", "forgot", "mfa", "otp", "login"],
}

VPN_TROUBLESHOOT_HINTS = ["not connecting", "can't connect", "cannot connect", "disconnect", "timeout"]


def choose_agent(question: str):
    q = (question or "").lower()

    if any(k in q for k in ["ticket", "jira", "itsm", "servicenow", "service now"]):
        return ticket_agent

    if "vpn" in q and any(k in q for k in VPN_TROUBLESHOOT_HINTS + ["fails", "failed", "stuck"]):
        return troubleshoot_agent

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


def _topic_match(question: str, top_file: str) -> bool:
    """Return True if question contains expected topic keywords for that file."""
    q = (question or "").lower()

    # STRICT guard for HR annual leave policy (avoid matching maternity/paternity etc.)
    if top_file == "hr_leave_policy.txt":
        return (
            "annual leave" in q
            or "holiday" in q
            or "time off" in q
            or "workday" in q
        )

    keys = FILE_TOPIC_KEYWORDS.get(top_file, [])
    if not keys:
        return True
    return any(k in q for k in keys)



def low_confidence(question: str, result: Dict[str, Any]) -> bool:
    answer = (result.get("answer") or "").lower()
    sources = _normalize_sources(result.get("sources"))

    if not sources:
        return True

    q_lower = (question or "").lower()

    # VPN troubleshooting: less strict
    if "vpn" in q_lower and any(k in q_lower for k in VPN_TROUBLESHOOT_HINTS):
        if "not found in knowledge base" in answer:
            return True
        return False

    if _max_score(sources) < MIN_SOURCE_SCORE:
        return True

    if "not found in knowledge base" in answer:
        return True

    # File-topic relevance guard
    top_file = sources[0].get("file", "unknown")
    if not _topic_match(question, top_file):
        return True

    # Semantic relevance guard (ignore generic words)
    q_tokens = set(
        w.strip(".,!?;:()[]{}'\"").lower()
        for w in (question or "").split()
        if len(w) > 3 and w.lower() not in STOPWORDS
    )
    combined_text = " ".join((s.get("snippet") or "").lower() for s in sources)

    if q_tokens and not any(token in combined_text for token in q_tokens):
        return True

    return False


def run(question: str) -> Dict[str, Any]:
    agent = choose_agent(question)
    result = agent.run(question) or {}
    result["sources"] = _normalize_sources(result.get("sources"))

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
