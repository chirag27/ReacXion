"""Pluggable text-embedding backends for the RAG layer.

For an astrology *consultation* product the default is deliberately a **local**
embedder so a client's birth details and questions never leave the machine, no
API key is needed, and retrieval has no per-query cost:

* ``hashing`` — a deterministic, dependency-free hashed bag-of-words embedder.
  Always available; used for tests/CI and as an offline fallback. Quality is
  modest but the cosine geometry is meaningful for keyword overlap.
* ``local``   — sentence-transformers (default ``BAAI/bge-small-en-v1.5``).
  The recommended production default: strong quality, fully offline, private.
* ``voyage``  — Voyage AI (default ``voyage-3.5``). Anthropic recommends Voyage
  for embeddings (Anthropic has no embeddings endpoint); use it when you want
  maximum retrieval quality and accept an API dependency. Reads ``VOYAGE_API_KEY``.

``local`` and ``voyage`` import their heavy/optional dependencies lazily, so the
engine runs out of the box on ``hashing`` with nothing extra installed.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import List, Protocol, runtime_checkable

_TOKEN = re.compile(r"[a-z0-9]+")


@runtime_checkable
class Embedder(Protocol):
    name: str
    dim: int

    def embed(self, texts: List[str]) -> List[List[float]]:
        ...


def _l2_normalize(vec: List[float]) -> List[float]:
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]


class HashingEmbedding:
    """Deterministic hashed bag-of-words embedding (no dependencies).

    Each token is hashed into one of ``dim`` buckets with a signed weight; the
    accumulated vector is L2-normalised so cosine similarity reflects token
    overlap. Stable across processes (uses blake2b, not Python's salted hash).
    """

    name = "hashing"

    def __init__(self, dim: int = 512):
        self.dim = dim

    def _hash(self, token: str) -> tuple:
        h = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        idx = int.from_bytes(h[:4], "big") % self.dim
        sign = 1.0 if (h[4] & 1) else -1.0
        return idx, sign

    def embed(self, texts: List[str]) -> List[List[float]]:
        out = []
        for text in texts:
            vec = [0.0] * self.dim
            for tok in _TOKEN.findall(text.lower()):
                idx, sign = self._hash(tok)
                vec[idx] += sign
            out.append(_l2_normalize(vec))
        return out


class LocalEmbedding:
    """sentence-transformers backend (offline, private). Lazy import."""

    name = "local"

    def __init__(self, model: str = "BAAI/bge-small-en-v1.5"):
        from sentence_transformers import SentenceTransformer  # lazy

        self._model = SentenceTransformer(model)
        self.dim = self._model.get_sentence_embedding_dimension()
        self.model_name = model

    def embed(self, texts: List[str]) -> List[List[float]]:
        vecs = self._model.encode(texts, normalize_embeddings=True)
        return [list(map(float, v)) for v in vecs]


class VoyageEmbedding:
    """Voyage AI backend (Anthropic-recommended). Lazy import; needs VOYAGE_API_KEY."""

    name = "voyage"

    def __init__(self, model: str = "voyage-3.5"):
        import voyageai  # lazy

        self._client = voyageai.Client()
        self.model_name = model
        # voyage-3.5 / voyage-3-large output 1024 dims by default.
        self.dim = 1024

    def embed(self, texts: List[str]) -> List[List[float]]:
        result = self._client.embed(texts, model=self.model_name,
                                    input_type="document")
        return [list(map(float, v)) for v in result.embeddings]


def get_embedder(name: str = "hashing", **kwargs) -> Embedder:
    """Factory: ``"hashing"`` (default), ``"local"``, or ``"voyage"``."""
    name = name.lower()
    if name == "hashing":
        return HashingEmbedding(**kwargs)
    if name == "local":
        return LocalEmbedding(**kwargs)
    if name == "voyage":
        return VoyageEmbedding(**kwargs)
    raise ValueError(f"unknown embedder {name!r}; use hashing | local | voyage")
