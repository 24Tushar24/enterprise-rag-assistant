import chromadb


class VectorStore:

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="documents"
        )

    def add_document(
        self,
        document_id: str,
        text: str,
        embedding: list[float],
        metadata: dict,
    ):
        self.collection.add(
            ids=[document_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 3,
        where: dict | None = None,
    ):
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
        )

    
    def list_documents(self):
        results = self.collection.get(
            include=["metadatas"]
        )

        metadatas = results.get("metadatas", [])

        documents = {}

        for metadata in metadatas:
            document_id = metadata.get("document_id")

            if not document_id:
                continue

            if document_id not in documents:
                documents[document_id] = {
                    "document_id": document_id,
                    "filename": metadata.get("filename", "Unknown"),
                    "timestamp": metadata.get("timestamp"),
                    "pages": set(),
                }

            page = metadata.get("page")
            if page is not None:
                documents[document_id]["pages"].add(page)

        for document in documents.values():
            document["pages"] = sorted(
                document["pages"]
            )

        return list(documents.values())