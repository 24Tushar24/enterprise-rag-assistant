from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.services.query_rewrite_service import QueryRewriteService

import re


class RAGService:

    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.llm_service = LLMService()
        self.query_rewrite_service = QueryRewriteService()

    def answer(self, query: str):

        # 1. Rewrite user query for better retrieval
        rewritten_query = self.query_rewrite_service.rewrite(query)

        # 2. Retrieve using rewritten query
        results = self.retrieval_service.retrieve(
            query=rewritten_query,
            top_k=3,
        )

        # 3. Abstain if evidence is weak
        if not results["has_evidence"]:
            return {
                "answer": "I don't have enough information in the provided documents.",
                "citations": [],
            }

        # 4. Build context
        context = self.retrieval_service.build_context(results)

        # 5. Generate answer using ORIGINAL user question
        prompt = f"""
You are an enterprise AI assistant.

Answer the user's question using ONLY the provided context.

Rules:
1. Do not use outside knowledge.
2. If the answer is not present in the context, say:
"I don't have enough information in the provided documents."
3. After your answer, provide the source IDs that directly support your answer.
4. Use only source IDs that actually support the answer.
5. Format sources exactly like:
Sources: [Source 1], [Source 2]

Context:
{context}

User Question:
{query}
"""

        answer = self.llm_service.generate(prompt)

        # 6. Extract source IDs
        source_ids = re.findall(
            r"\[Source (\d+)\]",
            answer
        )

        source_ids = list(dict.fromkeys(source_ids))

        metadatas = results.get("metadatas", [[]])[0]

        citations = []

        for source_id in source_ids:
            index = int(source_id) - 1

            if 0 <= index < len(metadatas):
                metadata = metadatas[index]

                citations.append({
                    "filename": metadata["filename"],
                    "page": metadata["page"],
                })

        return {
            "answer": answer,
            "citations": citations,
        }