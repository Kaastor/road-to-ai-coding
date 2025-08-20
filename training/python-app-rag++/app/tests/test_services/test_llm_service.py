"""Tests for LLM service."""

import pytest
from unittest.mock import Mock, patch
from app.services.llm_service import LLMService
from app.models.api import CitedSource, TokenUsage


class TestLLMService:
    """Test cases for LLM service."""

    def test_init_with_api_key(self):
        """Test initialization with API key parameter."""
        service = LLMService(api_key="test-key")
        assert service.api_key == "test-key"
        assert service.model == "claude-3-haiku-20240307"

    def test_init_with_custom_model(self):
        """Test initialization with custom model."""
        service = LLMService(api_key="test-key", model="claude-3-opus-20240229")
        assert service.model == "claude-3-opus-20240229"

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'env-key'})
    def test_init_with_env_var(self):
        """Test initialization using environment variable."""
        service = LLMService()
        assert service.api_key == "env-key"

    def test_init_without_api_key_raises_error(self):
        """Test that initialization without API key raises error."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Anthropic API key must be provided"):
                LLMService()

    def test_create_prompt(self):
        """Test prompt creation."""
        service = LLMService(api_key="test-key")
        query = "What is machine learning?"
        context = "SOURCE_1: Machine learning is a subset of AI."
        
        prompt = service._create_prompt(query, context)
        
        assert "What is machine learning?" in prompt
        assert "SOURCE_1: Machine learning is a subset of AI." in prompt
        assert "cite the source using the format [SOURCE_X]" in prompt

    def test_extract_citations_with_sources(self):
        """Test citation extraction from answer."""
        service = LLMService(api_key="test-key")
        answer = "Machine learning is a subset of AI [SOURCE_1]. It uses algorithms [SOURCE_2]."
        source_map = {
            "SOURCE_1": {
                "source_file": "doc1.md",
                "title": "AI Basics",
                "chunk_text": "Machine learning is a subset of AI that focuses on algorithms.",
                "chunk_index": 0,
                "similarity": 0.85
            },
            "SOURCE_2": {
                "source_file": "doc2.md", 
                "title": "Algorithms",
                "chunk_text": "Algorithms are the foundation of machine learning.",
                "chunk_index": 1,
                "bm25_score": 2.5
            }
        }
        search_results = []
        
        citations = service._extract_citations(answer, source_map, search_results)
        
        assert len(citations) == 2
        # Citations are sorted by relevance score (highest first)
        # BM25 score of 2.5 > similarity of 0.85
        assert citations[0].source_file == "doc2.md"
        assert citations[0].relevance_score == 2.5
        assert citations[1].source_file == "doc1.md"
        assert citations[1].relevance_score == 0.85

    def test_extract_citations_no_sources(self):
        """Test citation extraction with no citations in answer."""
        service = LLMService(api_key="test-key")
        answer = "This is an answer without citations."
        source_map = {}
        search_results = []
        
        citations = service._extract_citations(answer, source_map, search_results)
        
        assert len(citations) == 0

    def test_extract_cited_spans_with_quotes(self):
        """Test extraction of cited spans with quotes."""
        service = LLMService(api_key="test-key")
        answer = 'Machine learning is "a subset of artificial intelligence" [SOURCE_1].'
        source_id = "SOURCE_1"
        chunk_text = "Machine learning is a subset of artificial intelligence that focuses on algorithms."
        
        spans = service._extract_cited_spans(answer, source_id, chunk_text)
        
        assert len(spans) > 0
        assert "a subset of artificial intelligence" in spans[0]

    @patch('app.services.llm_service.Anthropic')
    def test_generate_answer_with_citations_success(self, mock_anthropic):
        """Test successful answer generation with citations."""
        # Mock the Anthropic client response
        mock_response = Mock()
        mock_response.content = [Mock(text="Machine learning is a subset of AI [SOURCE_1].")]
        mock_response.usage = Mock(
            input_tokens=100,
            output_tokens=50
        )
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        service = LLMService(api_key="test-key")
        search_results = [{
            "source_file": "doc1.md",
            "title": "AI Basics", 
            "chunk_text": "Machine learning is a subset of AI.",
            "chunk_index": 0,
            "similarity": 0.85
        }]
        
        answer, citations, token_usage = service.generate_answer_with_citations(
            "What is machine learning?", search_results
        )
        
        assert "Machine learning is a subset of AI" in answer
        assert len(citations) == 1
        assert citations[0].source_file == "doc1.md"
        assert token_usage.input_tokens == 100
        assert token_usage.output_tokens == 50
        assert token_usage.total_tokens == 150

    def test_generate_answer_empty_search_results(self):
        """Test answer generation with empty search results."""
        service = LLMService(api_key="test-key")
        
        answer, citations, token_usage = service.generate_answer_with_citations(
            "What is machine learning?", []
        )
        
        assert "couldn't find any relevant information" in answer
        assert len(citations) == 0
        assert token_usage.total_tokens == 0

    @patch('app.services.llm_service.Anthropic')
    def test_generate_answer_api_error(self, mock_anthropic):
        """Test answer generation with API error."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.return_value = mock_client
        
        service = LLMService(api_key="test-key")
        search_results = [{
            "source_file": "doc1.md",
            "title": "Test",
            "chunk_text": "Test content",
            "chunk_index": 0,
            "similarity": 0.5
        }]
        
        answer, citations, token_usage = service.generate_answer_with_citations(
            "Test query", search_results
        )
        
        assert "Error generating answer" in answer
        assert len(citations) == 0
        assert token_usage.total_tokens == 0