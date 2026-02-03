def clarify(question: str) -> dict:
    """
    Returns a clarifying question. No LLM call needed.
    """
    return {
        "answer": (
            "I need one more detail to answer accurately.\n"
            f"Your question: '{question}'\n\n"
            "Clarifying question: Which system/app, environment (prod/dev), "
            "or exact error message are you seeing?"
        ),
        "sources": [],
    }
