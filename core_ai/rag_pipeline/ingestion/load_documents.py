from llama_index.core import SimpleDirectoryReader

def load_documents(data_dir: str):
    """
    Reads files (PDF/TXT/MD/HTML) from a folder and returns LlamaIndex documents.
    """
    return SimpleDirectoryReader(data_dir, recursive=True).load_data()
