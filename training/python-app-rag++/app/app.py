"""RAG++ FastAPI application with hybrid search and LLM answer generation."""

import logging
import time
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from .models.api import AskRequest, AskResponse, FeedbackRequest, FeedbackResponse, MetricsResponse
from .services.document_indexer import DocumentIndexer
from .services.llm_service import LLMService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG++ Service",
    description="Retrieval-Augmented Generation service with feedback and live re-ranking",
    version="0.1.0"
)

# Global instances
document_indexer: DocumentIndexer | None = None
llm_service: LLMService | None = None

# In-memory feedback storage and metrics
feedback_store: list[Dict[str, Any]] = []
query_metrics: list[float] = []  # Response times in ms


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global document_indexer, llm_service
    
    try:
        # Initialize document indexer
        document_indexer = DocumentIndexer()
        logger.info("Document indexer initialized")
        
        # Index documents if docs directory exists
        docs_path = Path("docs")
        if docs_path.exists():
            logger.info(f"Indexing documents from: {docs_path}")
            stats = document_indexer.index_documents(docs_path)
            logger.info(f"Indexing stats: {stats}")
        else:
            logger.warning(f"Docs directory not found at: {docs_path}")
        
        # Initialize LLM service
        llm_service = LLMService()
        logger.info("LLM service initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        # Continue startup even if initialization fails


@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest) -> AskResponse:
    """Answer a question using RAG pipeline with hybrid search and LLM generation.
    
    Args:
        request: The ask request containing the query.
        
    Returns:
        Response with generated answer, cited sources, and metrics.
    """
    start_time = time.time()
    
    try:
        if not document_indexer or not llm_service:
            raise HTTPException(status_code=503, detail="Services not initialized")
        
        # Perform hybrid search to retrieve relevant documents
        logger.info(f"Processing query: '{request.q}'")
        search_results = document_indexer.hybrid_search_documents(
            query=request.q,
            k=request.max_sources
        )
        
        if not search_results:
            logger.warning(f"No search results found for query: '{request.q}'")
        
        # Generate answer with citations using LLM
        answer, cited_sources, token_usage = llm_service.generate_answer_with_citations(
            query=request.q,
            search_results=search_results
        )
        
        # Calculate response latency
        lat_ms = int((time.time() - start_time) * 1000)
        query_metrics.append(lat_ms)
        
        response = AskResponse(
            answer=answer,
            sources=cited_sources,
            lat_ms=lat_ms,
            token_usage=token_usage,
            query=request.q
        )
        
        logger.info(f"Query processed in {lat_ms}ms with {len(cited_sources)} sources")
        return response
        
    except Exception as e:
        logger.error(f"Error processing query '{request.q}': {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """Submit feedback for a query-document pair.
    
    Args:
        request: The feedback request.
        
    Returns:
        Confirmation of feedback submission.
    """
    try:
        # Validate feedback label
        if request.label not in ["positive", "negative"]:
            raise HTTPException(status_code=400, detail="Label must be 'positive' or 'negative'")
        
        # Store feedback
        feedback_entry = {
            "query": request.q,
            "doc_id": request.doc_id,
            "label": request.label,
            "timestamp": time.time()
        }
        feedback_store.append(feedback_entry)
        
        logger.info(f"Feedback recorded: {request.label} for query '{request.q}' and doc '{request.doc_id}'")
        
        return FeedbackResponse(
            ok=True,
            message=f"Feedback '{request.label}' recorded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Error recording feedback: {str(e)}")


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """Get service metrics including latency and feedback statistics.
    
    Returns:
        Service metrics.
    """
    try:
        # Calculate latency percentiles
        if query_metrics:
            sorted_metrics = sorted(query_metrics)
            p50_idx = int(len(sorted_metrics) * 0.5)
            p95_idx = int(len(sorted_metrics) * 0.95)
            p50 = sorted_metrics[p50_idx]
            p95 = sorted_metrics[p95_idx] if p95_idx < len(sorted_metrics) else sorted_metrics[-1]
        else:
            p50 = p95 = 0.0
        
        # Calculate hit rate (simplified - assume positive feedback means hit)
        total_feedback = len(feedback_store)
        positive_feedback = sum(1 for f in feedback_store if f["label"] == "positive")
        hit_rate_at_3 = positive_feedback / total_feedback if total_feedback > 0 else 0.0
        
        # Estimate rerank time (currently we don't track this separately)
        avg_rerank_ms = p50 * 0.1 if p50 > 0 else 0.0  # Rough estimate
        
        return MetricsResponse(
            p50=p50,
            p95=p95,
            hit_rate_at_3=hit_rate_at_3,
            avg_rerank_ms=avg_rerank_ms,
            total_queries=len(query_metrics),
            total_feedback=total_feedback
        )
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating metrics: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "services": {"indexer": document_indexer is not None, "llm": llm_service is not None}}


def main() -> None:
    """Main entry point for the application."""
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()