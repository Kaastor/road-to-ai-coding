# BM25 Search

BM25 (Best Matching 25) is a ranking function used in information retrieval to estimate the relevance of documents to a given search query.

## Algorithm Overview

BM25 builds upon the TF-IDF (Term Frequency-Inverse Document Frequency) concept but includes additional parameters to handle document length normalization and term frequency saturation.

### Key Parameters
- **k1**: Controls term frequency normalization (typically 1.2-2.0)
- **b**: Controls document length normalization (typically 0.75)

## Formula
The BM25 score for a document D given query Q is calculated using term frequencies, document lengths, and collection statistics.

## Advantages
- Handles varying document lengths well
- More robust than simple TF-IDF
- Proven effectiveness in many domains
- Fast computation and indexing

## Limitations
- Purely lexical matching (no semantic understanding)
- Requires exact term matches
- May miss synonyms or related concepts

## Hybrid Approaches
Combining BM25 with vector search provides:
- Lexical precision from BM25
- Semantic understanding from embeddings
- Better overall retrieval performance