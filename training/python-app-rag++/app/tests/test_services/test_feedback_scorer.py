"""Tests for the feedback scorer service."""

import pytest
from app.services.feedback_scorer import FeedbackScorer


class TestFeedbackScorer:
    """Test cases for FeedbackScorer."""
    
    def test_initialization(self):
        """Test scorer initialization with default parameters."""
        scorer = FeedbackScorer()
        
        assert scorer.positive_boost == 0.2
        assert scorer.negative_penalty == 0.1
        assert len(scorer.doc_feedback_stats) == 0
        assert len(scorer.query_doc_feedback) == 0
    
    def test_initialization_with_custom_params(self):
        """Test scorer initialization with custom parameters."""
        scorer = FeedbackScorer(positive_boost=0.3, negative_penalty=0.15)
        
        assert scorer.positive_boost == 0.3
        assert scorer.negative_penalty == 0.15
    
    def test_add_positive_feedback(self):
        """Test adding positive feedback."""
        scorer = FeedbackScorer()
        
        scorer.add_feedback("machine learning", "doc1:0", "positive")
        
        # Check global stats
        assert scorer.doc_feedback_stats["doc1:0"]["positive"] == 1
        assert scorer.doc_feedback_stats["doc1:0"]["negative"] == 0
        assert scorer.doc_feedback_stats["doc1:0"]["total"] == 1
        
        # Check query-specific stats
        query_hash = scorer._hash_query("machine learning")
        key = (query_hash, "doc1:0")
        assert scorer.query_doc_feedback[key]["positive"] == 1
        assert scorer.query_doc_feedback[key]["negative"] == 0
    
    def test_add_negative_feedback(self):
        """Test adding negative feedback."""
        scorer = FeedbackScorer()
        
        scorer.add_feedback("python tutorial", "doc2:1", "negative")
        
        # Check global stats
        assert scorer.doc_feedback_stats["doc2:1"]["positive"] == 0
        assert scorer.doc_feedback_stats["doc2:1"]["negative"] == 1
        assert scorer.doc_feedback_stats["doc2:1"]["total"] == 1
    
    def test_add_invalid_feedback(self):
        """Test adding invalid feedback raises ValueError."""
        scorer = FeedbackScorer()
        
        with pytest.raises(ValueError, match="Invalid feedback label"):
            scorer.add_feedback("test query", "doc1:0", "invalid")
    
    def test_get_document_boost_no_feedback(self):
        """Test getting boost for document with no feedback."""
        scorer = FeedbackScorer()
        
        boost = scorer.get_document_boost("doc1:0")
        
        assert boost == 1.0  # No change
    
    def test_get_document_boost_positive_feedback(self):
        """Test getting boost for document with positive feedback."""
        scorer = FeedbackScorer(positive_boost=0.2)
        
        # Add positive feedback
        scorer.add_feedback("test query", "doc1:0", "positive")
        
        boost = scorer.get_document_boost("doc1:0")
        
        assert boost > 1.0  # Should be boosted
        assert boost == 1.2  # 1.0 + 0.2 (100% positive)
    
    def test_get_document_boost_negative_feedback(self):
        """Test getting boost for document with negative feedback."""
        scorer = FeedbackScorer(negative_penalty=0.1)
        
        # Add negative feedback
        scorer.add_feedback("test query", "doc1:0", "negative")
        
        boost = scorer.get_document_boost("doc1:0")
        
        assert boost < 1.0  # Should be penalized
        assert boost == 0.9  # 1.0 - 0.1 (100% negative)
    
    def test_get_document_boost_mixed_feedback(self):
        """Test getting boost for document with mixed feedback."""
        scorer = FeedbackScorer(positive_boost=0.2, negative_penalty=0.1)
        
        # Add mixed feedback
        scorer.add_feedback("test query", "doc1:0", "positive")
        scorer.add_feedback("test query", "doc1:0", "negative")
        
        boost = scorer.get_document_boost("doc1:0")
        
        # Should be 1.0 + 0.5*0.2 - 0.5*0.1 = 1.05
        assert boost == 1.05
    
    def test_adjust_search_results_empty(self):
        """Test adjusting empty search results."""
        scorer = FeedbackScorer()
        
        results = scorer.adjust_search_results([])
        
        assert results == []
    
    def test_adjust_search_results_no_feedback(self):
        """Test adjusting search results with no feedback."""
        scorer = FeedbackScorer()
        
        original_results = [
            {
                "hybrid_score": 0.8,
                "source_file": "doc1.md",
                "chunk_index": 0,
                "chunk_text": "Content 1"
            },
            {
                "hybrid_score": 0.6,
                "source_file": "doc2.md", 
                "chunk_index": 0,
                "chunk_text": "Content 2"
            }
        ]
        
        results = scorer.adjust_search_results(original_results, "test query")
        
        # Should maintain original order and scores
        assert len(results) == 2
        assert results[0]["hybrid_score"] == 0.8
        assert results[1]["hybrid_score"] == 0.6
        assert results[0]["feedback_boost"] == 1.0
        assert results[1]["feedback_boost"] == 1.0
    
    def test_adjust_search_results_with_feedback(self):
        """Test adjusting search results with feedback."""
        scorer = FeedbackScorer(positive_boost=0.5)  # Higher boost for testing
        
        # Add positive feedback for second document
        scorer.add_feedback("test query", "doc2.md:0", "positive")
        
        original_results = [
            {
                "hybrid_score": 0.8,
                "source_file": "doc1.md",
                "chunk_index": 0,
                "chunk_text": "Content 1"
            },
            {
                "hybrid_score": 0.6,
                "source_file": "doc2.md",
                "chunk_index": 0,
                "chunk_text": "Content 2"
            }
        ]
        
        results = scorer.adjust_search_results(original_results, "test query")
        
        # Second document should now rank higher due to feedback
        assert len(results) == 2
        assert results[0]["source_file"] == "doc2.md"  # Boosted to top
        assert results[1]["source_file"] == "doc1.md"  # Dropped to second
        assert results[0]["feedback_boost"] > 1.0
        assert results[1]["feedback_boost"] == 1.0
    
    def test_get_feedback_stats_empty(self):
        """Test getting feedback statistics with no feedback."""
        scorer = FeedbackScorer()
        
        stats = scorer.get_feedback_stats()
        
        assert stats["total_feedback_entries"] == 0
        assert stats["total_positive"] == 0
        assert stats["total_negative"] == 0
        assert stats["unique_documents_with_feedback"] == 0
    
    def test_get_feedback_stats_with_data(self):
        """Test getting feedback statistics with data."""
        scorer = FeedbackScorer()
        
        # Add some feedback
        scorer.add_feedback("query1", "doc1:0", "positive")
        scorer.add_feedback("query1", "doc2:0", "negative")
        scorer.add_feedback("query2", "doc1:0", "positive")
        
        stats = scorer.get_feedback_stats()
        
        assert stats["total_feedback_entries"] == 3
        assert stats["total_positive"] == 2
        assert stats["total_negative"] == 1
        assert stats["unique_documents_with_feedback"] == 2
        assert len(stats["top_documents"]) == 2
    
    def test_hash_query(self):
        """Test query hashing functionality."""
        scorer = FeedbackScorer()
        
        # Test basic hashing
        hash1 = scorer._hash_query("machine learning")
        hash2 = scorer._hash_query("machine learning")
        assert hash1 == hash2
        
        # Test normalization
        hash3 = scorer._hash_query("  Machine Learning  ")
        assert hash1 == hash3
        
        # Test word limit
        long_query = "this is a very long query with many words that should be truncated"
        hash_long = scorer._hash_query(long_query)
        assert len(hash_long.split("_")) == 5  # Should only keep first 5 words
    
    def test_get_result_doc_id(self):
        """Test extracting document ID from search result."""
        scorer = FeedbackScorer()
        
        result = {
            "source_file": "docs/test.md",
            "chunk_index": 2
        }
        
        doc_id = scorer._get_result_doc_id(result)
        
        assert doc_id == "docs/test.md:2"
    
    def test_reset_feedback(self):
        """Test resetting all feedback data."""
        scorer = FeedbackScorer()
        
        # Add some feedback
        scorer.add_feedback("test", "doc1:0", "positive")
        assert len(scorer.doc_feedback_stats) > 0
        
        # Reset
        scorer.reset_feedback()
        
        assert len(scorer.doc_feedback_stats) == 0
        assert len(scorer.query_doc_feedback) == 0