"""Chroma-backed vector store, one collection per astrology *system*.

Embeddings are always computed by our pluggable :mod:`embeddings` backend and
passed to Chroma explicitly — Chroma's own default embedder (which would try to
download a model) is never invoked, so the store works fully offline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .embeddings import Embedder, get_embedder

SYSTEMS = ("vedic", "kp", "lalkitab")


@dataclass
class SearchHit:
    id: str
    text: str
    score: float                # cosine similarity in [-1, 1] (higher = closer)
    metadata: Dict


class TextStore:
    """Persistent (or in-memory) Chroma store scoped by astrology system."""

    def __init__(self, path: Optional[str] = None, embedder: Optional[Embedder] = None):
        import chromadb

        self.embedder = embedder or get_embedder("hashing")
        if path:
            self._client = chromadb.PersistentClient(path=path)
        else:
            self._client = chromadb.EphemeralClient()
        self._collections = {}

    def _collection(self, system: str):
        if system not in SYSTEMS:
            raise ValueError(f"unknown system {system!r}; use one of {SYSTEMS}")
        if system not in self._collections:
            # Chroma collection names must be 3-512 chars; prefix the system key.
            self._collections[system] = self._client.get_or_create_collection(
                name=f"astro_{system}", metadata={"hnsw:space": "cosine"})
        return self._collections[system]

    def add_texts(
        self,
        system: str,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
    ) -> None:
        col = self._collection(system)
        embeddings = self.embedder.embed(documents)
        metas = metadatas or [{} for _ in documents]
        for m in metas:
            m.setdefault("system", system)
        col.upsert(ids=ids, embeddings=embeddings, documents=documents,
                   metadatas=metas)

    def query(self, system: str, text: str, k: int = 5) -> List[SearchHit]:
        col = self._collection(system)
        if col.count() == 0:
            return []
        q = self.embedder.embed([text])
        res = col.query(query_embeddings=q, n_results=min(k, col.count()),
                        include=["documents", "distances", "metadatas"])
        hits = []
        for i in range(len(res["ids"][0])):
            # cosine distance -> similarity
            dist = res["distances"][0][i]
            hits.append(SearchHit(
                id=res["ids"][0][i],
                text=res["documents"][0][i],
                score=1.0 - dist,
                metadata=res["metadatas"][0][i] or {},
            ))
        return hits

    def count(self, system: str) -> int:
        return self._collection(system).count()
