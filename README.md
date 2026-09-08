# Enterprise RAG AI Assistant

An enterprise-grade Retrieval-Augmented Generation (RAG) application
that allows users to upload documents and ask grounded questions with
source citations.

## Features

- PDF document ingestion
- Text extraction and cleaning
- Recursive text chunking
- Sentence Transformer embeddings
- Persistent ChromaDB vector store
- Semantic similarity retrieval
- Cross-Encoder reranking
- Query rewriting
- Context-bounded generation
- Source/page citations
- Abstention when evidence is insufficient
- Prompt injection protection
- PII and secret redaction
- Structured LLM output validation
- Request-level observability
- Dockerized backend
- Persistent vector database

## Architecture

Next.js Frontend
        ↓
FastAPI Backend
        ↓
Guardrails
        ↓
Query Rewrite
        ↓
Embedding
        ↓
ChromaDB Retrieval
        ↓
Cross-Encoder Reranking
        ↓
Context Assembly
        ↓
Groq LLM
        ↓
Structured Output Validation
        ↓
Answer + Citations

## Tech Stack

### Backend
- Python
- FastAPI
- Pydantic
- ChromaDB
- Sentence Transformers
- LangChain Text Splitters
- Groq

### Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS

### Infrastructure
- Docker
- Docker Volume

## RAG Pipeline

### Ingestion

PDF
→ Text Extraction
→ Cleaning
→ Chunking
→ Metadata
→ Embeddings
→ ChromaDB

### Query

User Query
→ Guardrail
→ Query Rewrite
→ Embedding
→ Retrieval
→ Reranking
→ Context Assembly
→ LLM
→ Validation
→ Answer + Citations

## Guardrails

The system protects against:

- Prompt injection
- Unsupported answers
- Retrieved-document instruction attacks
- Secret leakage
- Basic PII leakage
- Invalid LLM structured output

When sufficient evidence is unavailable, the system abstains instead
of generating an unsupported answer.

## Observability

Each request tracks:

- Request ID
- Request latency
- Retrieval latency
- LLM latency
- Retrieved sources
- Model name
- Input/output/total tokens
- Errors and rate limits

## Docker

The backend runs inside Docker and uses a persistent ChromaDB volume,
so indexed documents survive container recreation.

## Running Locally

### Backend

```bash
cd backend
docker build -t rag-backend .
docker run -d -p 8000:8000 --env-file .env \
  -v rag-chroma-data:/app/chroma_db \
  --name rag-backend-container rag-backend