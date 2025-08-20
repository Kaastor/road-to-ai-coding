"""Feedback-based document scoring service for live re-ranking."""

import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict
import math

logger = logging.getLogger(__name__)


class FeedbackScorer:
    """Service for adjusting document scores based on user feedback."""
    
    def __init__(self, positive_boost: float = 0.2, negative_penalty: float = 0.1):
        """Initialize the feedback scorer.
        
        Args:
            positive_boost: Score boost for documents with positive feedback (0-1).
            negative_penalty: Score penalty for documents with negative feedback (0-1).
        """
        self.positive_boost = positive_boost
        self.negative_penalty = negative_penalty
        
        # Store feedback statistics per document
        # Format: doc_id -> {"positive": count, "negative": count, "total": count}
        self.doc_feedback_stats: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"positive": 0, "negative": 0, "total": 0}
        )
        
        # Store query-specific feedback for more granular scoring
        # Format: (query_hash, doc_id) -> {"positive": count, "negative": count}
        self.query_doc_feedback: Dict[tuple, Dict[str, int]] = defaultdict(
            lambda: {"positive": 0, "negative": 0}
        )
        
        logger.info(f"Feedback scorer initialized with positive_boost={positive_boost}, "
                   f"negative_penalty={negative_penalty}")
    
    def add_feedback(self, query: str, doc_id: str, label: str) -> None:
        """Record feedback for a query-document pair.
        
        Args:
            query: The search query.
            doc_id: The document identifier.
            label: Feedback label ("positive" or "negative").
        """
        if label not in ["positive", "negative"]:
            raise ValueError(f"Invalid feedback label: {label}")
        
        # Update global document statistics
        self.doc_feedback_stats[doc_id][label] += 1
        self.doc_feedback_stats[doc_id]["total"] += 1
        
        # Update query-specific statistics
        query_hash = self._hash_query(query)
        query_doc_key = (query_hash, doc_id)
        self.query_doc_feedback[query_doc_key][label] += 1
        
        logger.debug(f"Recorded {label} feedback for doc {doc_id} on query '{query}'")
    
    def get_document_boost(self, doc_id: str, query: Optional[str] = None) -> float:
        """Calculate the feedback-based boost for a document.
        
        Args:
            doc_id: The document identifier.
            query: Optional query for query-specific scoring.
            
        Returns:
            Score multiplier (1.0 = no change, >1.0 = boost, <1.0 = penalty).
        """
        # Start with neutral score
        boost = 1.0
        
        # Apply global document feedback
        global_stats = self.doc_feedback_stats[doc_id]
        if global_stats["total"] > 0:
            positive_ratio = global_stats["positive"] / global_stats["total"]
            negative_ratio = global_stats["negative"] / global_stats["total"]
            
            # Apply boost/penalty based on feedback ratio
            boost += positive_ratio * self.positive_boost
            boost -= negative_ratio * self.negative_penalty
        
        # Apply query-specific feedback if query is provided
        if query:
            query_hash = self._hash_query(query)
            query_doc_key = (query_hash, doc_id)
            query_stats = self.query_doc_feedback[query_doc_key]
            
            total_query_feedback = query_stats["positive"] + query_stats["negative"]
            if total_query_feedback > 0:
                query_positive_ratio = query_stats["positive"] / total_query_feedback
                query_negative_ratio = query_stats["negative"] / total_query_feedback
                
                # Give more weight to query-specific feedback
                query_boost = 1.0
                query_boost += query_positive_ratio * self.positive_boost * 1.5
                query_boost -= query_negative_ratio * self.negative_penalty * 1.5
                
                # Combine with global boost (weighted average)
                boost = 0.7 * boost + 0.3 * query_boost
        
        # Ensure boost stays within reasonable bounds
        boost = max(0.1, min(2.0, boost))
        
        return boost
    
    def adjust_search_results(
        self, 
        results: List[Dict[str, Any]], 
        query: Optional[str] = None,
        score_key: str = "hybrid_score"
    ) -> List[Dict[str, Any]]:
        """Adjust search result scores based on feedback.
        
        Args:
            results: List of search results with scores.
            query: The search query for query-specific adjustments.
            score_key: The key containing the relevance score to adjust.
            
        Returns:
            List of results with adjusted scores, re-sorted by adjusted score.
        """
        if not results:
            return results
        
        adjusted_results = []
        
        for result in results:
            # Create a copy to avoid modifying original
            adjusted_result = result.copy()
            
            # Get document ID
            doc_id = self._get_result_doc_id(result)
            
            # Get feedback boost
            boost = self.get_document_boost(doc_id, query)
            
            # Adjust the score
            original_score = result.get(score_key, 0.0)
            adjusted_score = original_score * boost
            
            # Store both original and adjusted scores
            adjusted_result[score_key] = adjusted_score
            adjusted_result["original_score"] = original_score
            adjusted_result["feedback_boost"] = boost
            
            adjusted_results.append(adjusted_result)
        
        # Re-sort by adjusted score
        adjusted_results.sort(key=lambda x: x.get(score_key, 0.0), reverse=True)
        
        logger.debug(f"Adjusted {len(results)} search results with feedback scoring")
        return adjusted_results
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics.
        
        Returns:
            Dictionary with feedback statistics.
        """
        total_feedback = sum(stats["total"] for stats in self.doc_feedback_stats.values())
        total_positive = sum(stats["positive"] for stats in self.doc_feedback_stats.values())
        total_negative = sum(stats["negative"] for stats in self.doc_feedback_stats.values())
        
        # Calculate most and least liked documents
        doc_scores = []
        for doc_id, stats in self.doc_feedback_stats.items():
            if stats["total"] > 0:
                score = (stats["positive"] - stats["negative"]) / stats["total"]
                doc_scores.append((doc_id, score, stats["total"]))
        
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "total_feedback_entries": total_feedback,
            "total_positive": total_positive,
            "total_negative": total_negative,
            "unique_documents_with_feedback": len(self.doc_feedback_stats),
            "unique_query_document_pairs": len(self.query_doc_feedback),
            "top_documents": doc_scores[:5],
            "bottom_documents": doc_scores[-5:] if len(doc_scores) > 5 else [],
            "positive_boost_factor": self.positive_boost,
            "negative_penalty_factor": self.negative_penalty
        }
    
    def _hash_query(self, query: str) -> str:
        """Create a hash for the query to use as a key.
        
        Args:
            query: The search query.
            
        Returns:
            Hash string for the query.
        """
        # Simple hash - normalize and take first few words
        normalized = query.lower().strip()
        words = normalized.split()[:5]  # Take first 5 words
        return "_".join(words)
    
    def _get_result_doc_id(self, result: Dict[str, Any]) -> str:
        """Extract document ID from search result.
        
        Args:
            result: Search result dictionary.
            
        Returns:
            Document identifier.
        """
        source_file = result.get("source_file", "")
        chunk_index = result.get("chunk_index", 0)
        return f"{source_file}:{chunk_index}"
    
    def reset_feedback(self) -> None:
        """Reset all feedback data."""
        self.doc_feedback_stats.clear()
        self.query_doc_feedback.clear()
        logger.info("All feedback data has been reset")