import os
import qdrant_client
from llama_index.vector_stores.qdrant import QdrantVectorStore

def get_vector_store():
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    collection = os.getenv("QDRANT_COLLECTION", "enterprise_kb")
    client = qdrant_client.QdrantClient(url=qdrant_url)
    return QdrantVectorStore(client=client, collection_name=collection)
