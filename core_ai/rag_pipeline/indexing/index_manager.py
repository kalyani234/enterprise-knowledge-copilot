from llama_index.core import StorageContext, VectorStoreIndex
from core_ai.rag_pipeline.indexing.vector_store import get_vector_store
from core_ai.rag_pipeline.indexing.embeddings import get_embedding_model

def get_index():
    """
    Connects to an existing Qdrant collection if it exists.
    """
    vector_store = get_vector_store()
    embed_model = get_embedding_model()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    return VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
        embed_model=embed_model,
    )

def ingest_documents(documents):
    """
    Builds/updates the index directly from documents (no private attributes).
    """
    vector_store = get_vector_store()
    embed_model = get_embedding_model()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # This automatically chunks and inserts into Qdrant
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True,
    )

    # We can't reliably count chunks without deeper internals,
    # but docs count is enough for MVP.
    return {"documents": len(documents)}
