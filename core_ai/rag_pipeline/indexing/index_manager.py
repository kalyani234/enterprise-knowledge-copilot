from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, List

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter

from core_ai.rag_pipeline.indexing.embeddings import setup_local_embeddings
from core_ai.rag_pipeline.indexing.vector_store import get_vector_store


@lru_cache(maxsize=1)
def get_index() -> VectorStoreIndex:
    # Always use local embeddings (simple + works on your laptop)
    setup_local_embeddings()

    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    return VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
    )


def ingest_documents(documents: List[Any]) -> Dict[str, Any]:
    index = get_index()

    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=64)
    nodes = splitter.get_nodes_from_documents(documents)

    # llama-index 0.14.x uses insert_nodes (NOT insert_documents)
    index.insert_nodes(nodes)

    return {"documents": len(documents), "chunks": len(nodes)}
