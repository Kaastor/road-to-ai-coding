"""Simple MCP-like client for PDF processing."""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import websockets
from PyPDF2 import PdfReader


class MCPPDFClient:
    """Simple MCP-style client for PDF text extraction."""
    
    def __init__(self, server_url: Optional[str] = None):
        """Initialize MCP client. For PoC, we'll use local processing."""
        self.server_url = server_url
        self.use_local = server_url is None
    
    async def extract_text(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text from PDF using MCP-style interface."""
        if self.use_local:
            return await self._extract_text_local(pdf_path)
        else:
            return await self._extract_text_mcp(pdf_path)
    
    async def _extract_text_local(self, pdf_path: str) -> Dict[str, Any]:
        """Local PDF text extraction (fallback for PoC)."""
        try:
            path = Path(pdf_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {pdf_path}")
            
            # Handle text files for demo purposes
            if path.suffix.lower() == '.txt':
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Split by double newlines to simulate pages
                text_pages = content.split('\n\n')
                pages = []
                for i, page_text in enumerate(text_pages):
                    if page_text.strip():
                        pages.append({
                            "page_number": i + 1,
                            "text": page_text.strip()
                        })
                
                return {
                    "filename": path.name,
                    "total_pages": len(pages),
                    "metadata": {"title": path.stem, "type": "text"},
                    "pages": pages,
                    "status": "success"
                }
            
            # Handle PDF files
            reader = PdfReader(str(path))
            
            # Extract text from all pages
            pages = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                pages.append({
                    "page_number": i + 1,
                    "text": text.strip()
                })
            
            # Get metadata
            metadata = {}
            if reader.metadata:
                metadata = {
                    "title": reader.metadata.get("/Title", ""),
                    "author": reader.metadata.get("/Author", ""),
                    "creator": reader.metadata.get("/Creator", ""),
                    "producer": reader.metadata.get("/Producer", ""),
                    "subject": reader.metadata.get("/Subject", "")
                }
            
            return {
                "filename": path.name,
                "total_pages": len(reader.pages),
                "metadata": metadata,
                "pages": pages,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "filename": pdf_path,
                "error": str(e),
                "status": "error"
            }
    
    async def _extract_text_mcp(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text via MCP server (future implementation)."""
        try:
            # This would be the actual MCP call
            message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "pdf/extract",
                "params": {
                    "file_path": pdf_path,
                    "include_metadata": True
                }
            }
            
            async with websockets.connect(self.server_url) as websocket:
                await websocket.send(json.dumps(message))
                response = await websocket.recv()
                return json.loads(response)
                
        except Exception as e:
            # Fallback to local processing
            print(f"MCP server error, falling back to local: {e}")
            return await self._extract_text_local(pdf_path)


def create_pdf_client(server_url: Optional[str] = None) -> MCPPDFClient:
    """Factory function to create PDF client."""
    return MCPPDFClient(server_url)