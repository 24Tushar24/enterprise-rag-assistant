import logging

from fastapi import FastAPI
from pydantic import BaseModel

from app.core.logging_config import setup_logging
from app.services.rag_service import RAGService
from app.api.documents import router as documents_router

setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(title="Enterprise RAG AI Assistant")

app.include_router(documents_router)

rag_service = RAGService()


class ChatRequest(BaseModel):
    prompt: str


@app.get("/health")
def health_check():
    logger.info("Health check called")

    return {
        "status": "healthy"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    logger.info("Chat request received")

    result = rag_service.answer(request.prompt)

    return result