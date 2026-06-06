"""RAG layer: pluggable embeddings + Chroma store + corpus retriever.

Provides interpretive *prose* to support a reading. Positional facts always come
from the deterministic engine — the corpus never supplies a longitude, dasha,
sub-lord, or cusp.
"""

from .embeddings import (
    Embedder,
    HashingEmbedding,
    LocalEmbedding,
    VoyageEmbedding,
    get_embedder,
)
from .store import SYSTEMS, SearchHit, TextStore
from .corpus import (
    CORPUS_ROOT,
    Chunk,
    chunk_document,
    ingest_corpus,
    load_corpus_chunks,
    search_texts,
)

__all__ = [
    "Embedder",
    "HashingEmbedding",
    "LocalEmbedding",
    "VoyageEmbedding",
    "get_embedder",
    "SYSTEMS",
    "SearchHit",
    "TextStore",
    "CORPUS_ROOT",
    "Chunk",
    "chunk_document",
    "ingest_corpus",
    "load_corpus_chunks",
    "search_texts",
]
