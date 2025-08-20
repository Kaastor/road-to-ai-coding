"""Create a simple test text file."""

with open("test_document.txt", "w") as f:
    f.write("""Test Document

This is a test document for the RAG system.
It contains some sample text that will be extracted
and chunked for search and retrieval.

Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Sed do eiusmod tempor incididunt ut labore et dolore magna
aliqua. Ut enim ad minim veniam, quis nostrud exercitation
ullamco laboris nisi ut aliquip ex ea commodo consequat.

Page 2

Duis aute irure dolor in reprehenderit in voluptate velit
esse cillum dolore eu fugiat nulla pariatur. Excepteur sint
occaecat cupidatat non proident, sunt in culpa qui officia
deserunt mollit anim id est laborum.

This document demonstrates the ingestion capability
of the Goose RAG system. The text will be chunked and
stored for semantic search.
""")

print("Created test_document.txt")