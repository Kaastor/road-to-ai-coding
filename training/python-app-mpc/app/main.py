"""Main FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import hashlib
from pathlib import Path

from .database import create_tables, get_db
from .models import Document, Chunk
from .mcp_client import create_pdf_client
from .chunking import create_chunker


# Pydantic models for API
class IngestResponse(BaseModel):
    message: str
    document_id: int
    filename: str
    chunks_created: int


class IngestRequest(BaseModel):
    file_path: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup: Create database tables
    create_tables()
    print("Database tables created successfully")
    yield
    # Shutdown: Any cleanup would go here
    print("Application shutting down")


# Create FastAPI app
app = FastAPI(
    title="Goose RAG API",
    description="A local-first RAG service for PDF documents",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Goose RAG API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connectivity test."""
    try:
        # Test database connection by counting documents
        document_count = db.query(Document).count()
        return {
            "status": "healthy",
            "database": "connected",
            "document_count": document_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@app.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(request: IngestRequest, db: Session = Depends(get_db)):
    """Ingest a PDF file and create chunks."""
    try:
        # Initialize clients
        pdf_client = create_pdf_client()
        chunker = create_chunker()
        
        # Check if file exists
        file_path = Path(request.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
        # Calculate file hash for deduplication
        file_hash = _calculate_file_hash(file_path)
        
        # Check if document already exists
        existing_doc = db.query(Document).filter(Document.filename == file_path.name).first()
        if existing_doc:
            return IngestResponse(
                message="Document already exists",
                document_id=existing_doc.id,
                filename=existing_doc.filename,
                chunks_created=len(existing_doc.chunks)
            )
        
        # Extract text using MCP client
        extraction_result = await pdf_client.extract_text(str(file_path))
        
        if extraction_result["status"] == "error":
            raise HTTPException(status_code=400, detail=f"PDF extraction failed: {extraction_result['error']}")
        
        # Create document record
        document = Document(
            filename=file_path.name,
            content=f"Extracted from {extraction_result['total_pages']} pages"
        )
        db.add(document)
        db.flush()  # Get the document ID
        
        # Create chunks
        text_chunks = chunker.chunk_document(extraction_result["pages"])
        
        chunk_records = []
        for text_chunk in text_chunks:
            chunk_record = Chunk(
                document_id=document.id,
                text=text_chunk.text,
                chunk_index=text_chunk.chunk_index
            )
            chunk_records.append(chunk_record)
        
        db.add_all(chunk_records)
        db.commit()
        
        return IngestResponse(
            message="PDF ingested successfully",
            document_id=document.id,
            filename=document.filename,
            chunks_created=len(chunk_records)
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    """List all ingested documents."""
    documents = db.query(Document).all()
    return {
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "chunk_count": len(doc.chunks),
                "created_at": doc.created_at
            }
            for doc in documents
        ]
    }


def _calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


@app.get("/docs")
async def get_docs():
    """Redirect to automatic docs."""
    return {"message": "Visit /docs for interactive API documentation"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)