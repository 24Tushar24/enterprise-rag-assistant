# Project 1: RAG Assistant

Starter structure for a Retrieval-Augmented Generation assistant.

## Structure

- `backend/app/api`: API routes
- `backend/app/core`: configuration and shared application concerns
- `backend/app/models`: request, response, and domain models
- `backend/app/services`: application services
- `backend/app/rag`: retrieval and generation pipeline
- `backend/app/evals`: backend evaluation helpers
- `backend/tests`: backend tests
- `frontend`: frontend application
- `data`: source documents and local data
- `evals`: evaluation datasets and reports

## Run the backend

```powershell
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health endpoint: `GET http://localhost:8000/health`
