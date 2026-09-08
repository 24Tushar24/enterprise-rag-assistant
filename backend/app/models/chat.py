from pydantic import BaseModel


class Citation(BaseModel):
    filename: str
    page: int


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]


class LLMResponse(BaseModel):
    answer: str
    source_ids: list[int]