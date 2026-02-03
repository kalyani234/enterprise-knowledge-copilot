from core_ai.rag_pipeline.indexing.index_manager import get_index
from core_ai.rag_pipeline.generation.llm_client import get_llm


def ask_question(question: str, top_k: int = 4) -> dict:
    index = get_index()
    llm = get_llm()

    # 1) explicit retrieval
    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(question)

    # Build sources from retrieved nodes
    sources = []
    for n in nodes[:top_k]:
        meta = n.node.metadata or {}
        file_name = meta.get("file_name") or meta.get("filename") or "unknown"
        score = getattr(n, "score", None)

        try:
            text = n.node.get_content()
        except Exception:
            text = getattr(n.node, "text", "")

        text = text or ""
        snippet = (text[:240] + "...") if len(text) > 240 else text

        sources.append(
            {"file": file_name, "score": score, "snippet": snippet}
        )

    # 2) generation (use retrieved context)
    context = "\n\n".join([s["snippet"] for s in sources]) if sources else ""

    prompt = (
        "You are an enterprise knowledge assistant.\n"
        "Use ONLY the context below.\n"
        "If the context is not enough, say: 'Not found in knowledge base' and ask ONE clarifying question.\n\n"
        "Rules:\n"
        "- Extract steps ONLY from the context. Do not invent new steps.\n"
        "- If the context lists multiple items, include ALL of them.\n"
        "- Keep each step to one line.\n\n"
        f"Context:\n{context}\n\n"
        "Output format (MUST follow):\n"
        "Summary: <one sentence>\n"
        "Steps:\n"
        "- <step 1>\n"
        "- <step 2>\n"
        "- <step 3>\n"
        "- <step N>\n"
        "Done.\n\n"
        "Formatting rules:\n"
        "- Each step MUST start with '- '.\n"
        f"User question: {question}\n"
    )

    response = llm.complete(prompt)
    return {"answer": str(response), "sources": sources}
