from app.services.reranker_service import RerankerService


reranker = RerankerService()

query = "How many annual leave days do employees get?"

documents = [
    "Employees are entitled to 20 days of annual leave every year.",
    "Employees can work from home up to two days per week.",
    "The office working hours are 9 AM to 6 PM.",
    "Tushar has experience with Python, React, Next.js and Docker.",
]

results = reranker.rerank(
    query=query,
    documents=documents,
    top_k=3,
)

for document, score in results:
    print("\nScore:", score)
    print("Document:", document)