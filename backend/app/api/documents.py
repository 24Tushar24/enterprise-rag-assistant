from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os
from uuid import uuid4
from datetime import datetime, timezone
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore

from app.services.document_service import (
    extract_text_from_pdf,
    chunk_pages,
)

embedding_service = EmbeddingService()
vector_store = VectorStore()
router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("")
async def upload_document(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:

            content = await file.read()
            temp_file.write(content)

            temp_file_path = temp_file.name

        pages  = extract_text_from_pdf(temp_file_path)

        chunks = chunk_pages(pages)

        document_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        for chunk in chunks:
            chunk["metadata"] = {
                "document_id": document_id,
                "filename": file.filename,
                "page": chunk["page"],
                "timestamp": timestamp,
            }
        for chunk in chunks:
            chunk["embedding"] = embedding_service.embed_text(
                chunk["text"]
            )

        for index, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{index}"

            vector_store.add_document(
                document_id=chunk_id,
                text=chunk["text"],
                embedding=chunk["embedding"],
                metadata=chunk["metadata"],
            )

        return {
            "document_id": document_id,
            "filename": file.filename,
            "chunk_count": len(chunks),
            "status": "indexed"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )

    finally:

        if "temp_file_path" in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)