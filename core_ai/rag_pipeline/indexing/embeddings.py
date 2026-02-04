from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def setup_local_embeddings() -> None:
    """
    Local embeddings (no OpenAI key needed).
    """
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
