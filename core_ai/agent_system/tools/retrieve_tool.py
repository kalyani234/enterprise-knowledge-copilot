from core_ai.rag_pipeline.retrieval.ask import ask_question


def retrieve(question: str, top_k: int = 2) -> dict:
    """
    Main RAG tool:
    - retrieves relevant context from vector DB
    - asks LLM using that context
    Returns: {"answer": "...", "sources": [...]}
    """

    # IMPORTANT:
    # Pass the raw user question to retrieval.
    # Prompt formatting is handled inside ask_question().
    result = ask_question(
        question=question,
        top_k=top_k,
    )

    return {
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
    }
