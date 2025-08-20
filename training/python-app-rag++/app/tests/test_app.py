"""Tests for FastAPI application endpoints."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from app.app import app
from app.models.api import TokenUsage, CitedSource


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_services():
    """Mock document indexer and LLM service."""
    with patch('app.app.document_indexer') as mock_indexer, \
         patch('app.app.llm_service') as mock_llm:
        
        mock_indexer.hybrid_search_documents.return_value = [
            {
                "source_file": "test.md",
                "title": "Test Document", 
                "chunk_text": "This is test content about machine learning.",
                "chunk_index": 0,
                "hybrid_score": 0.85
            }
        ]
        
        mock_cited_source = CitedSource(
            source_file="test.md",
            title="Test Document",
            chunk_text="This is test content about machine learning.",
            chunk_index=0,
            relevance_score=0.85,
            cited_spans=["machine learning"]
        )
        
        mock_token_usage = TokenUsage(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150
        )
        
        mock_llm.generate_answer_with_citations.return_value = (
            "Machine learning is a field of AI [SOURCE_1].",
            [mock_cited_source],
            mock_token_usage
        )
        
        yield mock_indexer, mock_llm


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check returns proper status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data


class TestAskEndpoint:
    """Test /ask endpoint."""
    
    def test_ask_success(self, client, mock_services):
        """Test successful ask request."""
        mock_indexer, mock_llm = mock_services
        
        request_data = {
            "q": "What is machine learning?",
            "max_sources": 5
        }
        
        response = client.post("/ask", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
        assert "lat_ms" in data
        assert "token_usage" in data
        assert "query" in data
        
        assert data["query"] == "What is machine learning?"
        assert len(data["sources"]) == 1
        assert data["sources"][0]["source_file"] == "test.md"
        assert data["token_usage"]["total_tokens"] == 150

    def test_ask_missing_query(self, client):
        """Test ask request with missing query."""
        request_data = {}
        
        response = client.post("/ask", json=request_data)
        
        assert response.status_code == 422  # Validation error

    def test_ask_services_not_initialized(self, client):
        """Test ask request when services are not initialized."""
        with patch('app.app.document_indexer', None), \
             patch('app.app.llm_service', None):
            
            request_data = {"q": "test query"}
            response = client.post("/ask", json=request_data)
            
            assert response.status_code == 503
            assert "Services not initialized" in response.json()["detail"]

    def test_ask_with_max_sources(self, client, mock_services):
        """Test ask request with custom max_sources."""
        mock_indexer, mock_llm = mock_services
        
        request_data = {
            "q": "What is AI?",
            "max_sources": 3
        }
        
        response = client.post("/ask", json=request_data)
        
        assert response.status_code == 200
        # Verify that hybrid_search_documents was called with k=3
        mock_indexer.hybrid_search_documents.assert_called_once_with(
            query="What is AI?", k=3
        )


class TestFeedbackEndpoint:
    """Test /feedback endpoint."""
    
    def test_feedback_success(self, client):
        """Test successful feedback submission."""
        request_data = {
            "q": "What is machine learning?",
            "doc_id": "test.md",
            "label": "positive"
        }
        
        response = client.post("/feedback", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "recorded successfully" in data["message"]

    def test_feedback_invalid_label(self, client):
        """Test feedback with invalid label."""
        request_data = {
            "q": "test query",
            "doc_id": "test.md", 
            "label": "invalid"
        }
        
        response = client.post("/feedback", json=request_data)
        
        assert response.status_code == 400
        assert "positive" in response.json()["detail"]
        assert "negative" in response.json()["detail"]

    def test_feedback_missing_fields(self, client):
        """Test feedback with missing fields."""
        request_data = {"q": "test query"}  # Missing doc_id and label
        
        response = client.post("/feedback", json=request_data)
        
        assert response.status_code == 422  # Validation error


class TestMetricsEndpoint:
    """Test /metrics endpoint."""
    
    def test_metrics_empty(self, client):
        """Test metrics when no data available."""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "p50" in data
        assert "p95" in data
        assert "hit_rate_at_3" in data
        assert "avg_rerank_ms" in data
        assert "total_queries" in data
        assert "total_feedback" in data
        
        assert data["p50"] == 0.0
        assert data["p95"] == 0.0
        assert data["total_queries"] == 0
        assert data["total_feedback"] == 0

    def test_metrics_with_data(self, client, mock_services):
        """Test metrics after some queries and feedback."""
        # First make a query to generate metrics
        request_data = {"q": "test query"}
        response = client.post("/ask", json=request_data)
        assert response.status_code == 200
        
        # Then submit feedback
        feedback_data = {
            "q": "test query",
            "doc_id": "test.md", 
            "label": "positive"
        }
        response = client.post("/feedback", json=feedback_data)
        assert response.status_code == 200
        
        # Check metrics
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_queries"] == 1
        assert data["total_feedback"] == 1
        assert data["p50"] > 0
        assert data["hit_rate_at_3"] == 1.0  # 100% positive feedback
