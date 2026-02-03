import os
from llama_index.llms.ollama import Ollama
from llama_index.core.llms.mock import MockLLM

def get_llm():
    if os.getenv("MOCK_LLM", "false").lower() == "true":
        return MockLLM()

    return Ollama(
        model=os.getenv("OLLAMA_MODEL", "gemma3:1b"),
        request_timeout=120,
    )
