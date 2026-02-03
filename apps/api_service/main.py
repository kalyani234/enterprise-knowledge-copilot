import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, List

from core_ai.rag_pipeline.ingestion.load_documents import load_documents
from core_ai.rag_pipeline.indexing.index_manager import ingest_documents
from core_ai.agent_system.orchestrator import run as run_agent

load_dotenv()

app = FastAPI(title="Enterprise Knowledge Copilot API")


class AskRequest(BaseModel):
    question: str
    top_k: int = 4


class AskResponse(BaseModel):
    agent: str
    answer: str
    sources: List[Dict[str, Any]]



@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest():
    data_dir = os.getenv("DATA_DIR", "./data/raw_documents")
    docs = load_documents(data_dir)

    if not docs:
        return {"message": f"No documents found in {data_dir}", "documents": 0}

    result = ingest_documents(docs)
    return {"message": "Ingestion complete", **result}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    result = run_agent(req.question)
    return {
        "agent": result.get("agent", "unknown"),
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
    }
