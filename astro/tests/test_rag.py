"""Tests for the Phase-6 RAG layer (embeddings, chunking, store, retrieval).

Uses the built-in hashing embedder and an in-memory Chroma store, so the suite
needs no network, API key, or model download.
"""

import math

import pytest

from engine.rag import (
    SYSTEMS,
    HashingEmbedding,
    TextStore,
    chunk_document,
    get_embedder,
    ingest_corpus,
    load_corpus_chunks,
    search_texts,
)


# --------------------------------------------------------------------------- #
# Embeddings
# --------------------------------------------------------------------------- #
def test_hashing_embedder_deterministic_and_unit_norm():
    e = HashingEmbedding(dim=256)
    a = e.embed(["marriage timing in kp"])[0]
    b = e.embed(["marriage timing in kp"])[0]
    assert a == b                                   # stable across calls
    assert len(a) == 256
    assert math.isclose(math.sqrt(sum(x * x for x in a)), 1.0, abs_tol=1e-9)


def test_hashing_embedder_similarity_orders_by_overlap():
    e = HashingEmbedding()
    q = e.embed(["raja yoga kendra trikona lords"])[0]
    near = e.embed(["a raja yoga links a kendra lord and a trikona lord"])[0]
    far = e.embed(["mustard oil remedy for an afflicted Saturn"])[0]

    def cos(u, v):
        return sum(a * b for a, b in zip(u, v))

    assert cos(q, near) > cos(q, far)


def test_get_embedder_factory():
    assert get_embedder("hashing").name == "hashing"
    with pytest.raises(ValueError):
        get_embedder("nonsense")


# --------------------------------------------------------------------------- #
# Chunking + corpus
# --------------------------------------------------------------------------- #
def test_chunk_document_splits_on_headings():
    md = "# Title\n\nFirst paragraph here about yogas.\n\n## Sub\n\nSecond para about cusps."
    chunks = chunk_document(md, "vedic", "x.md")
    assert len(chunks) >= 2
    assert all(c.system == "vedic" and c.source == "x.md" for c in chunks)
    assert any("Sub:" in c.text for c in chunks)    # heading prefixed


def test_corpus_loads_for_every_system():
    chunks = load_corpus_chunks()
    systems = {c.system for c in chunks}
    assert systems == set(SYSTEMS)
    assert len(chunks) > 10


# --------------------------------------------------------------------------- #
# Store + retrieval
# --------------------------------------------------------------------------- #
@pytest.fixture
def store():
    s = TextStore(embedder=get_embedder("hashing"))   # in-memory
    ingest_corpus(s)
    return s


def test_ingest_populates_all_collections(store):
    for system in SYSTEMS:
        assert store.count(system) > 0


def test_search_returns_relevant_passage(store):
    hits = search_texts(store, "cuspal sub lord decides marriage", "kp", k=1)
    assert hits
    assert "significators_and_csl.md" == hits[0].metadata["source"]
    assert -1.0 <= hits[0].score <= 1.0


def test_search_is_scoped_to_system(store):
    # A KP-scoped query must only ever return KP documents.
    hits = search_texts(store, "raja yoga kendra trikona", "kp", k=5)
    assert hits
    assert {h.metadata["system"] for h in hits} == {"kp"}


def test_search_unknown_system_raises(store):
    with pytest.raises(ValueError):
        search_texts(store, "anything", "tarot", k=1)


def test_query_empty_collection_returns_empty(tmp_path):
    # Fresh persistent path -> isolated client (Chroma caches in-process clients).
    empty = TextStore(path=str(tmp_path / "empty"), embedder=get_embedder("hashing"))
    assert empty.query("vedic", "anything") == []
