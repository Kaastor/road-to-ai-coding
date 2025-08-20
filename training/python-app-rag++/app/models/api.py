"""API request and response models for the RAG++ service."""

from typing import List, Optional
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Request model for the /ask endpoint."""
    
    q: str = Field(..., description="The question or query to ask")
    max_sources: int = Field(default=5, description="Maximum number of source documents to retrieve")


class CitedSource(BaseModel):
    """Model for a cited source document with relevant spans."""
    
    source_file: str = Field(..., description="Path to the source document")
    title: str = Field(..., description="Title of the source document")
    chunk_text: str = Field(..., description="Relevant text chunk from the source")
    chunk_index: int = Field(..., description="Index of the chunk within the document")
    relevance_score: float = Field(..., description="Relevance score for this source")
    cited_spans: List[str] = Field(default_factory=list, description="Specific text spans cited in the answer")


class TokenUsage(BaseModel):
    """Model for tracking token usage from LLM calls."""
    
    input_tokens: int = Field(..., description="Number of input tokens used")
    output_tokens: int = Field(..., description="Number of output tokens generated")
    total_tokens: int = Field(..., description="Total tokens used")


class AskResponse(BaseModel):
    """Response model for the /ask endpoint."""
    
    answer: str = Field(..., description="The generated answer to the query")
    sources: List[CitedSource] = Field(..., description="List of source documents with cited spans")
    lat_ms: int = Field(..., description="Response latency in milliseconds")
    token_usage: TokenUsage = Field(..., description="Token usage statistics")
    query: str = Field(..., description="The original query that was asked")


class FeedbackRequest(BaseModel):
    """Request model for the /feedback endpoint."""
    
    q: str = Field(..., description="The original query")
    doc_id: str = Field(..., description="Document identifier (source_file)")
    label: str = Field(..., description="Feedback label: 'positive' or 'negative'")


class FeedbackResponse(BaseModel):
    """Response model for the /feedback endpoint."""
    
    ok: bool = Field(..., description="Whether feedback was successfully recorded")
    message: Optional[str] = Field(default=None, description="Optional feedback message")


class MetricsResponse(BaseModel):
    """Response model for the /metrics endpoint."""
    
    p50: float = Field(..., description="50th percentile response time in milliseconds")
    p95: float = Field(..., description="95th percentile response time in milliseconds")
    hit_rate_at_3: float = Field(..., description="Hit rate at top 3 results")
    avg_rerank_ms: float = Field(..., description="Average reranking time in milliseconds")
    total_queries: int = Field(..., description="Total number of queries processed")
    total_feedback: int = Field(..., description="Total feedback entries received")