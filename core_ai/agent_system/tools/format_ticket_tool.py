from core_ai.agent_system.tools.retrieve_tool import retrieve

def format_ticket(question: str) -> dict:
    """
    Create an ITSM/Jira ticket-like output grounded in the knowledge base.
    Returns: {"answer": "...", "sources": [...]}
    """
    prompt = (
        "Create an ITSM ticket summary using ONLY retrieved context.\n"
        "If context is missing, state what is missing.\n\n"
        "Format exactly:\n"
        "Title:\n"
        "Impact:\n"
        "Symptoms:\n"
        "Likely Cause:\n"
        "Suggested Next Steps:\n"
        "References:\n\n"
        f"User request: {question}"
    )

    return retrieve(prompt, top_k=3)
