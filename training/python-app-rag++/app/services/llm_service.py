"""LLM service for generating answers with cited spans using Claude API."""

import logging
import re
import os
from typing import List, Dict, Any, Tuple
from anthropic import Anthropic

from ..models.api import CitedSource, TokenUsage

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating answers with cited sources using Claude API."""
    
    def __init__(self, api_key: str | None = None, model: str = "claude-3-haiku-20240307"):
        """Initialize the LLM service.
        
        Args:
            api_key: Anthropic API key. If None, will use ANTHROPIC_API_KEY env var.
            model: Claude model to use for generation.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key must be provided via parameter or ANTHROPIC_API_KEY environment variable")
        
        self.model = model
        self.client = Anthropic(api_key=self.api_key)
        logger.info(f"LLM service initialized with model: {model}")
    
    def generate_answer_with_citations(
        self, 
        query: str, 
        search_results: List[Dict[str, Any]]
    ) -> Tuple[str, List[CitedSource], TokenUsage]:
        """Generate an answer with citations based on search results.
        
        Args:
            query: The user's question.
            search_results: List of relevant document chunks from search.
            
        Returns:
            Tuple of (answer, cited_sources, token_usage).
        """
        logger.debug(f"Generating answer for query: '{query}' with {len(search_results)} sources")
        
        if not search_results:
            empty_usage = TokenUsage(input_tokens=0, output_tokens=0, total_tokens=0)
            return "I couldn't find any relevant information to answer your question.", [], empty_usage
        
        # Prepare context from search results
        context_parts = []
        source_map = {}  # Map source numbers to metadata
        
        for i, result in enumerate(search_results, 1):
            source_id = f"SOURCE_{i}"
            context_parts.append(f"{source_id}: {result.get('chunk_text', '')}")
            source_map[source_id] = result
        
        context = "\n\n".join(context_parts)
        
        # Create the prompt
        prompt = self._create_prompt(query, context)
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            answer = response.content[0].text
            
            # Extract token usage
            token_usage = TokenUsage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens
            )
            
            # Parse citations from the answer
            cited_sources = self._extract_citations(answer, source_map, search_results)
            
            logger.info(f"Generated answer with {len(cited_sources)} citations. Tokens used: {token_usage.total_tokens}")
            return answer, cited_sources, token_usage
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            error_usage = TokenUsage(input_tokens=0, output_tokens=0, total_tokens=0)
            return f"Error generating answer: {str(e)}", [], error_usage
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create the prompt for Claude API.
        
        Args:
            query: User's question.
            context: Concatenated context from search results.
            
        Returns:
            Formatted prompt string.
        """
        return f"""You are a helpful assistant that answers questions based on the provided context. 

IMPORTANT INSTRUCTIONS:
1. Answer the question using ONLY the information provided in the context below.
2. When you reference information from the context, cite the source using the format [SOURCE_X] where X is the source number.
3. If you cannot answer the question based on the provided context, say so clearly.
4. Be concise but comprehensive in your answer.
5. Include specific relevant quotes or details when they directly answer the question.

CONTEXT:
{context}

QUESTION: {query}

Please provide your answer with proper citations:"""
    
    def _extract_citations(
        self, 
        answer: str, 
        source_map: Dict[str, Dict[str, Any]], 
        search_results: List[Dict[str, Any]]
    ) -> List[CitedSource]:
        """Extract citations from the generated answer.
        
        Args:
            answer: The generated answer text.
            source_map: Mapping of source IDs to metadata.
            search_results: Original search results.
            
        Returns:
            List of CitedSource objects.
        """
        cited_sources = []
        
        # Find all source citations in the answer (e.g., [SOURCE_1], [SOURCE_2])
        citation_pattern = r'\[SOURCE_(\d+)\]'
        citations = re.findall(citation_pattern, answer)
        
        # Create CitedSource objects for each citation
        for citation_num in set(citations):  # Use set to avoid duplicates
            source_id = f"SOURCE_{citation_num}"
            
            if source_id in source_map:
                result = source_map[source_id]
                
                # Extract cited spans (text near the citation)
                cited_spans = self._extract_cited_spans(answer, source_id, result.get('chunk_text', ''))
                
                # Get relevance score from search result
                relevance_score = result.get('similarity', result.get('bm25_score', result.get('hybrid_score', 0.0)))
                
                cited_source = CitedSource(
                    source_file=result.get('source_file', ''),
                    title=result.get('title', ''),
                    chunk_text=result.get('chunk_text', ''),
                    chunk_index=result.get('chunk_index', 0),
                    relevance_score=float(relevance_score),
                    cited_spans=cited_spans
                )
                cited_sources.append(cited_source)
        
        # Sort by relevance score (highest first)
        cited_sources.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return cited_sources
    
    def _extract_cited_spans(self, answer: str, source_id: str, chunk_text: str) -> List[str]:
        """Extract specific text spans that were cited.
        
        Args:
            answer: The generated answer.
            source_id: The source ID (e.g., "SOURCE_1").
            chunk_text: The original chunk text.
            
        Returns:
            List of cited text spans.
        """
        cited_spans = []
        
        # Find sentences in the answer that contain this citation
        sentences = re.split(r'[.!?]+', answer)
        
        for sentence in sentences:
            if source_id in sentence:
                # Try to find quotes or specific references in the sentence
                quotes = re.findall(r'"([^"]*)"', sentence)
                for quote in quotes:
                    if quote and len(quote) > 10:  # Only meaningful quotes
                        # Check if this quote appears in the chunk text
                        if quote.lower() in chunk_text.lower():
                            cited_spans.append(quote)
                
                # If no quotes found, try to extract key phrases
                if not cited_spans:
                    # Remove the citation marker and extract meaningful phrases
                    clean_sentence = re.sub(r'\[SOURCE_\d+\]', '', sentence).strip()
                    if len(clean_sentence) > 20:  # Only meaningful sentences
                        cited_spans.append(clean_sentence[:100])  # Limit length
        
        return cited_spans[:3]  # Limit to top 3 spans