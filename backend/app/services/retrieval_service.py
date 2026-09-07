from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.reranker_service import RerankerService

import numpy as np


class RetrievalService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.reranker_service = RerankerService()

    def remove_semantic_duplicates(
        self,
        documents: list[str],
        metadatas: list[dict],
        distances: list[float],
        similarity_threshold: float = 0.90,
    ):
        unique_documents = []
        unique_metadatas = []
        unique_distances = []
        unique_embeddings = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            embedding = np.array(
                self.embedding_service.embed_text(document)
            )

            is_duplicate = False

            for existing_embedding in unique_embeddings:
                similarity = np.dot(
                    embedding,
                    existing_embedding,
                ) / (
                    np.linalg.norm(embedding)
                    * np.linalg.norm(existing_embedding)
                )

                if similarity >= similarity_threshold:
                    is_duplicate = True
                    break

            if is_duplicate:
                continue

            unique_documents.append(document)
            unique_metadatas.append(metadata)
            unique_distances.append(distance)
            unique_embeddings.append(embedding)

        return (
            unique_documents,
            unique_metadatas,
            unique_distances,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        where: dict | None = None,
    ):
        query_embedding = self.embedding_service.embed_text(query)

        # Retrieve more candidates first
        candidate_k = 10

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=candidate_k,
            where=where,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not documents:
            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
                "rerank_scores": [],
                "has_evidence": False,
            }

        # Rerank candidates
        reranked = self.reranker_service.rerank(
            query=query,
            documents=documents,
            top_k=top_k,
        )

        final_documents = []
        final_metadatas = []
        final_distances = []
        rerank_scores = []

        for document, score in reranked:

            index = documents.index(document)

            final_documents.append(document)
            final_metadatas.append(metadatas[index])
            final_distances.append(distances[index])

            rerank_scores.append(float(score))

        # Remove semantically duplicate chunks
        (
            final_documents,
            final_metadatas,
            final_distances,
        ) = self.remove_semantic_duplicates(
            final_documents,
            final_metadatas,
            final_distances,
            similarity_threshold=0.90,
        )

        # Keep rerank scores aligned with final documents
        final_rerank_scores = []

        for document in final_documents:
            for original_document, score in reranked:
                if document == original_document:
                    final_rerank_scores.append(float(score))
                    break

        if not final_documents:
            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
                "rerank_scores": [],
                "has_evidence": False,
            }

        # Evidence check
        best_distance = final_distances[0]

        has_evidence = best_distance < 1.45

        return {
            "documents": [final_documents],
            "metadatas": [final_metadatas],
            "distances": [final_distances],
            "rerank_scores": final_rerank_scores,
            "has_evidence": has_evidence,
        }

    def build_context(
        self,
        results,
        max_chars: int = 6000,
    ):
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        context_parts = []
        current_length = 0

        for index, (document, metadata) in enumerate(
            zip(documents, metadatas),
            start=1,
        ):
            source = f"""[Source {index}]
Filename: {metadata["filename"]}
Page: {metadata["page"]}

{document}"""

            if current_length + len(source) > max_chars:
                break

            context_parts.append(source)
            current_length += len(source)

        return "\n\n---\n\n".join(context_parts)