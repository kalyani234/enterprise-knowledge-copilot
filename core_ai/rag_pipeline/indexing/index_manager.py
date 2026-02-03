import os
from functools import lru_cache
from typing import List, Dict, Any

from llama_index.core import VectorStoreIndex

from core_ai.rag_pipeline.indexing.vector_store import get_vector_store
from core_ai.rag_pipeline.indexing.embeddings import get_embed_model


@lru_cache(maxsize=1)
def get_index() -> VectorStoreIndex:
    """
    Creates (and caches) the VectorStoreIndex ONCE per process.
    This prevents re-building the index / embed model on every request.
    """
    vector_store = get_vector_store()
    embed_model = get_embed_model()

    # index object that wraps the vector store + embed model
    return VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )


def ingest_documents(documents) -> Dict[str, Any]:
    """
    Ingest docs into the existing Qdrant collection.
    Assumes docs are already loaded as LlamaIndex Document objects.
    """
    index = get_index()
    # Insert documents into vector store through index
    index.insert_documents(documents)
    return {"documents": len(documents)}
