import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import RateLimitError
from pydantic import BaseModel, Field, field_validator

from app.core.logging_config import setup_logging
from app.services.rag_service import RAGService
from app.api.documents import router as documents_router
from app.services.guardrail_service import GuardrailService
from app.models.chat import ChatResponse
from app.middleware.request_logging import RequestLoggingMiddleware

setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(title="Enterprise RAG AI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)
app.include_router(documents_router)

rag_service = RAGService()
guardrail_service = GuardrailService()


class ChatRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=2000
    )

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value):
        if not value.strip():
            raise ValueError("Prompt cannot be empty or whitespace")
        return value

@app.get("/health")
def health_check():
    logger.info("Health check called")

    return {
        "status": "healthy"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, http_request: Request):
    request_id = http_request.state.request_id

    logger.info(f"Request ID available in chat: {request_id}")
    logger.info("Chat request received")

    # Casual conversation
    if guardrail_service.is_casual_query(request.prompt):
        return {
            "answer": "Hello! I'm doing well. How can I help you with your documents?",
            "citations": []
        }

    # Prompt injection
    is_injection = guardrail_service.check_prompt_injection(
        request.prompt
    )

    if is_injection:
        logger.warning("Potential prompt injection detected")

        return {
            "answer": "I can't follow instructions that attempt to bypass the assistant's rules.",
            "citations": []
        }

    try:
        result = rag_service.answer(
            request.prompt,
            request_id=request_id
        )
    except RateLimitError:
        logger.warning(
            f"[{request_id}] Returning HTTP 429 due to Groq rate limit"
        )
        raise HTTPException(
            status_code=429,
            detail="AI service is temporarily rate limited. Please try again shortly."
        )   

    result["answer"] = guardrail_service.redact_secrets(
        result["answer"]
    )

    result["answer"] = guardrail_service.redact_pii(
        result["answer"]
    )
    return result