"""Document loader service for reading and processing markdown files."""

from pathlib import Path
from typing import Any
import logging

logger = logging.getLogger(__name__)


class Document:
    """Represents a loaded document with metadata."""
    
    def __init__(self, content: str, source: str, doc_id: str = None):
        self.content = content
        self.source = source
        self.doc_id = doc_id or self._generate_doc_id(source)
        self.metadata = {
            "source": source,
            "doc_id": self.doc_id,
            "content_length": len(content)
        }
    
    def _generate_doc_id(self, source: str) -> str:
        """Generate a unique document ID from source path."""
        return Path(source).stem
    
    @property
    def file_path(self) -> Path:
        """Get the file path as a Path object."""
        return Path(self.source)
    
    @property
    def title(self) -> str:
        """Extract title from document content or use filename."""
        lines = self.content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        # Fallback to filename without extension
        return self.file_path.stem.replace('_', ' ').replace('-', ' ').title()
    
    def __repr__(self) -> str:
        return f"Document(doc_id='{self.doc_id}', source='{self.source}', length={len(self.content)})"


class DocumentLoader:
    """Loads and manages markdown documents from the filesystem."""
    
    def __init__(self, docs_directory: str = "docs"):
        self.docs_directory = Path(docs_directory)
        self.documents = {}
        
    def load_document(self, file_path: Path) -> Document:
        """Load a single markdown document from file path."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc = Document(
                content=content,
                source=str(file_path),
                doc_id=file_path.stem
            )
            
            logger.info(f"Loaded document: {doc.doc_id} from {file_path}")
            return doc
            
        except Exception as e:
            logger.error(f"Failed to load document from {file_path}: {e}")
            raise
    
    def load_documents(self, pattern: str = "*.md") -> list[Document]:
        """Load all markdown documents from the docs directory."""
        documents = []
        
        if not self.docs_directory.exists():
            logger.warning(f"Documents directory {self.docs_directory} does not exist")
            return documents
        
        markdown_files = list(self.docs_directory.glob(pattern))
        
        if not markdown_files:
            logger.warning(f"No markdown files found in {self.docs_directory}")
            return documents
        
        for file_path in markdown_files:
            try:
                doc = self.load_document(file_path)
                documents.append(doc)
                self.documents[doc.doc_id] = doc
            except Exception as e:
                logger.error(f"Skipping file {file_path} due to error: {e}")
                continue
        
        logger.info(f"Loaded {len(documents)} documents from {self.docs_directory}")
        return documents
    
    def get_document(self, doc_id: str) -> Document | None:
        """Retrieve a document by its ID."""
        return self.documents.get(doc_id)
    
    def get_all_documents(self) -> list[Document]:
        """Get all loaded documents."""
        return list(self.documents.values())
    
    def get_document_count(self) -> int:
        """Get the total number of loaded documents."""
        return len(self.documents)