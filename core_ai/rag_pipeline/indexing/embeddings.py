import os
from functools import lru_cache

from llama_index.embeddings.huggingface import HuggingFaceEmbedding


@lru_cache(maxsize=1)
def get_embed_model() -> HuggingFaceEmbedding:
    """
    Loads the embedding model ONCE per process (singleton).
    Without this, HuggingFace weights may load repeatedly -> slow + CI flakes.
    """
    model_name = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    return HuggingFaceEmbedding(model_name=model_name)
