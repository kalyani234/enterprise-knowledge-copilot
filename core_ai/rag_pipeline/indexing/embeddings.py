import os
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def get_embedding_model():
    model_name = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    return HuggingFaceEmbedding(model_name=model_name)
