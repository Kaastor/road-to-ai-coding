"""Document indexing service that combines loading, chunking, embedding, and vector storage."""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .document_loader import DocumentLoader
from .text_chunker import TextChunker
from .adaptive_embedding_service import AdaptiveEmbeddingService
from .vector_storage import VectorStorage
from .hybrid_search import HybridSearch

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """Service for indexing documents with embeddings and vector storage."""
    
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """Initialize the document indexer.
        
        Args:
            embedding_model: Name of the embedding model to use.
            chunk_size: Size of text chunks in characters.
            chunk_overlap: Overlap between chunks in characters.
        """
        self.document_loader = DocumentLoader()
        self.text_chunker = TextChunker(chunk_size=chunk_size, overlap_size=chunk_overlap)
        self.embedding_service = AdaptiveEmbeddingService(
            preferred_model="tfidf",  # Use TF-IDF as primary approach
            embedding_dim=384
        )
        
        # Vector storage will be initialized after we know actual embedding dimension
        self.vector_storage = None
        # Hybrid search will be initialized after vector storage is ready
        self.hybrid_search = None
        
        logger.info(f"Document indexer initialized with embedding model: {embedding_model}")
    
    def index_documents(self, docs_directory: Path) -> Dict[str, Any]:
        """Index all documents in a directory.
        
        Args:
            docs_directory: Path to directory containing markdown documents.
            
        Returns:
            Dictionary with indexing statistics.
        """
        logger.info(f"Starting document indexing from: {docs_directory}")
        
        # Update loader directory and load documents
        self.document_loader.docs_directory = docs_directory
        documents = self.document_loader.load_documents()
        if not documents:
            logger.warning("No documents found to index")
            return {"total_documents": 0, "total_chunks": 0, "error": "No documents found"}
        
        logger.info(f"Loaded {len(documents)} documents")
        
        # Process each document
        all_chunks = []
        chunk_metadata = []
        
        for doc in documents:
            # Chunk the document
            chunks = self.text_chunker.chunk_text(doc.content, doc_id=str(doc.file_path.stem))
            
            for chunk in chunks:
                all_chunks.append(chunk.text)
                
                # Create metadata for each chunk
                chunk_meta = {
                    "source_file": str(doc.file_path),
                    "title": doc.title,
                    "chunk_index": chunk.chunk_index,
                    "chunk_text": chunk.text,
                    "char_count": len(chunk.text)
                }
                chunk_metadata.append(chunk_meta)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        
        if not all_chunks:
            return {"total_documents": len(documents), "total_chunks": 0, "error": "No chunks created"}
        
        # Prepare embedding service for corpus (important for TF-IDF)
        logger.info("Preparing embedding service for corpus...")
        self.embedding_service.prepare_for_corpus(all_chunks)
        
        # Generate embeddings for all chunks
        logger.info("Generating embeddings...")
        embeddings = self.embedding_service.embed_texts(all_chunks)
        
        # Initialize vector storage with actual embedding dimension
        if self.vector_storage is None:
            actual_dim = embeddings.shape[1] if len(embeddings) > 0 else self.embedding_service.get_embedding_dimension()
            self.vector_storage = VectorStorage(dimension=actual_dim)
            logger.info(f"Initialized vector storage with dimension: {actual_dim}")
        
        # Store in vector database
        logger.info("Storing vectors...")
        doc_ids = self.vector_storage.add_documents(embeddings, chunk_metadata)
        
        # Initialize hybrid search with the indexed data
        logger.info("Initializing hybrid search...")
        self.hybrid_search = HybridSearch(
            vector_storage=self.vector_storage,
            embedding_service=self.embedding_service
        )
        self.hybrid_search.index_documents(chunk_metadata)
        
        stats = {
            "total_documents": len(documents),
            "total_chunks": len(all_chunks),
            "embedding_dimension": embeddings.shape[1] if len(embeddings) > 0 else 0,
            "indexed_document_ids": doc_ids,
            "hybrid_search_ready": self.hybrid_search._is_ready()
        }
        
        logger.info(f"Indexing complete: {stats}")
        return stats
    
    def search_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for documents similar to the query.
        
        Args:
            query: Search query text.
            k: Number of results to return.
            
        Returns:
            List of search results with similarity scores and metadata.
        """
        logger.debug(f"Searching for: '{query}' (k={k})")
        
        if self.vector_storage is None:
            logger.warning("No index available for search")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)
        
        # Search in vector storage
        similarities, documents = self.vector_storage.search(query_embedding, k=k)
        
        # Combine results
        results = []
        for similarity, doc in zip(similarities, documents):
            result = {
                "similarity": float(similarity),
                "source_file": doc.get("source_file", ""),
                "title": doc.get("title", ""),
                "chunk_index": doc.get("chunk_index", 0),
                "chunk_text": doc.get("chunk_text", ""),
                "char_count": doc.get("char_count", 0)
            }
            results.append(result)
        
        logger.debug(f"Found {len(results)} results")
        return results
    
    def hybrid_search_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for documents using hybrid BM25 + vector search.
        
        Args:
            query: Search query text.
            k: Number of results to return.
            
        Returns:
            List of search results with hybrid scores and metadata.
        """
        logger.debug(f"Hybrid searching for: '{query}' (k={k})")
        
        if self.hybrid_search is None:
            logger.warning("No hybrid search available - run index_documents first")
            return []
        
        return self.hybrid_search.search(query, k=k)
    
    def bm25_search_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for documents using BM25 keyword search only.
        
        Args:
            query: Search query text.
            k: Number of results to return.
            
        Returns:
            List of search results with BM25 scores and metadata.
        """
        logger.debug(f"BM25 searching for: '{query}' (k={k})")
        
        if self.hybrid_search is None:
            logger.warning("No hybrid search available - run index_documents first")
            return []
        
        scores, documents = self.hybrid_search.bm25_search.search(query, k=k)
        
        # Convert to standard result format
        results = []
        for score, doc in zip(scores, documents):
            result = {
                "bm25_score": float(score),
                "source_file": doc.get("source_file", ""),
                "title": doc.get("title", ""),
                "chunk_index": doc.get("chunk_index", 0),
                "chunk_text": doc.get("chunk_text", ""),
                "char_count": doc.get("char_count", 0)
            }
            results.append(result)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get indexing statistics.
        
        Returns:
            Dictionary with current statistics.
        """
        return {
            "total_documents_indexed": self.vector_storage.get_document_count() if self.vector_storage else 0,
            "embedding_dimension": self.vector_storage.dimension if self.vector_storage else self.embedding_service.get_embedding_dimension(),
            "model_name": self.embedding_service.model_name,
            "service_type": self.embedding_service.get_service_type()
        }
    
    def save_index(self, filepath: Path) -> None:
        """Save the vector index to disk.
        
        Args:
            filepath: Path to save the index.
        """
        if self.vector_storage is None:
            raise ValueError("No index to save - run index_documents first")
        self.vector_storage.save_index(filepath)
        logger.info(f"Index saved to: {filepath}")
    
    def load_index(self, filepath: Path) -> None:
        """Load a vector index from disk.
        
        Args:
            filepath: Path to load the index from.
        """
        # Load metadata to determine dimension
        import json
        metadata_file = filepath.with_suffix('.json')
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Initialize vector storage with loaded dimension
        self.vector_storage = VectorStorage(dimension=metadata['dimension'])
        self.vector_storage.load_index(filepath)
        
        # Prepare embedding service with document content from loaded metadata
        if hasattr(self.embedding_service, 'prepare_for_corpus'):
            # Extract chunk texts from loaded documents
            chunk_texts = [doc.get('chunk_text', '') for doc in metadata['documents'] if doc.get('chunk_text')]
            if chunk_texts:
                logger.info("Preparing embedding service for loaded corpus...")
                self.embedding_service.prepare_for_corpus(chunk_texts)
        
        # Initialize hybrid search with loaded data
        logger.info("Initializing hybrid search for loaded index...")
        self.hybrid_search = HybridSearch(
            vector_storage=self.vector_storage,
            embedding_service=self.embedding_service
        )
        self.hybrid_search.index_documents(metadata['documents'])
        
        logger.info(f"Index loaded from: {filepath}")