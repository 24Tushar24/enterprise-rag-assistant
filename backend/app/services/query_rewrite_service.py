from app.services.llm_service import LLMService


class QueryRewriteService:

    def __init__(self):
        self.llm_service = LLMService()

    def rewrite(self, query: str, request_id: str | None = None) -> str:

        prompt = f"""
You are a search query optimizer for an enterprise document retrieval system.

Rewrite the user's query into a clear, specific search query.

Rules:
1. Preserve the original meaning.
2. Do not add information that is not present in the user's query.
3. Expand abbreviations or informal language when helpful.
4. Return ONLY the rewritten query.
5. Do not answer the question.

User query:
{query}
"""

        rewritten_query = self.llm_service.generate(prompt, request_id=request_id)

        return rewritten_query.strip()