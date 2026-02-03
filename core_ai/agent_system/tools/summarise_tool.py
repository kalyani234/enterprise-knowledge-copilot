from core_ai.agent_system.tools.retrieve_tool import retrieve

def summarise(question: str) -> dict:
    """
    Summarise relevant knowledge base content.
    Returns: {"answer": "...", "sources": [...]}
    """
    prompt = (
        "Summarise the relevant knowledge base content in 5 bullet points.\n"
        "Be accurate and do not invent information.\n\n"
        f"User request: {question}"
    )

    return retrieve(prompt, top_k=3)
