from app.services.retrieval_service import RetrievalService

retrieval_service = RetrievalService()

query = "How many annual leave days do employees get?"

results = retrieval_service.retrieve(
    query=query,
    top_k=3
)

print("\nDocuments:")
for doc in results["documents"][0]:
    print("\n---")
    print(doc)

print("\nRerank Scores:")
print(results["rerank_scores"])

print("\nDistances:")
print(results["distances"][0])

print("\nHas Evidence:")
print(results["has_evidence"])