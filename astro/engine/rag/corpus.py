"""Corpus ingestion and the ``search_texts(query, system)`` retriever.

Source material lives under ``data/corpus/<system>/*.md`` and is chunked on
Markdown headings/paragraphs, then embedded into the per-system Chroma
collection. Retrieval is always scoped to one system so Vedic prose never
bleeds into a KP answer.

COPYRIGHT — the shipped corpus contains only **original rule summaries written
for this project**. Do not ingest scraped or copyrighted book text. Every
ingested document's provenance must be recorded in ``data/corpus/sources.md``.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import List, Optional

from .store import SYSTEMS, SearchHit, TextStore

# Corpus root relative to the project (astro/) directory.
_THIS = os.path.dirname(os.path.abspath(__file__))
CORPUS_ROOT = os.path.normpath(os.path.join(_THIS, "..", "..", "data", "corpus"))

_MIN_CHUNK_CHARS = 80


@dataclass
class Chunk:
    id: str
    text: str
    system: str
    source: str
    heading: str


def _split_markdown(text: str) -> List[tuple]:
    """Split into (heading, body) sections on ATX headings; merge tiny bodies."""
    sections = []
    heading = ""
    buf: List[str] = []

    def flush():
        body = "\n".join(buf).strip()
        if body:
            sections.append((heading, body))

    for line in text.splitlines():
        m = re.match(r"^#{1,6}\s+(.*)", line)
        if m:
            flush()
            heading = m.group(1).strip()
            buf = []
        else:
            buf.append(line)
    flush()
    return sections


def chunk_document(text: str, system: str, source: str) -> List[Chunk]:
    """Chunk one document into retrievable passages."""
    chunks: List[Chunk] = []
    for s_idx, (heading, body) in enumerate(_split_markdown(text)):
        # Further split long sections on blank lines, keeping the heading.
        paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        merged: List[str] = []
        for p in paras:
            if merged and len(merged[-1]) < _MIN_CHUNK_CHARS:
                merged[-1] = merged[-1] + "\n" + p
            else:
                merged.append(p)
        for p_idx, para in enumerate(merged):
            prefix = f"{heading}: " if heading else ""
            chunks.append(Chunk(
                id=f"{source}#{s_idx}.{p_idx}",
                text=prefix + para,
                system=system,
                source=source,
                heading=heading,
            ))
    return chunks


def load_corpus_chunks(root: str = CORPUS_ROOT) -> List[Chunk]:
    """Read every ``data/corpus/<system>/*.md`` file into chunks."""
    chunks: List[Chunk] = []
    for system in SYSTEMS:
        sys_dir = os.path.join(root, system)
        if not os.path.isdir(sys_dir):
            continue
        for fname in sorted(os.listdir(sys_dir)):
            if not fname.endswith(".md"):
                continue
            path = os.path.join(sys_dir, fname)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            chunks.extend(chunk_document(text, system, fname))
    return chunks


def ingest_corpus(store: TextStore, root: str = CORPUS_ROOT) -> int:
    """Embed and index the whole corpus into ``store``. Returns chunk count."""
    by_system = {s: ([], [], []) for s in SYSTEMS}   # ids, docs, metas
    for ch in load_corpus_chunks(root):
        ids, docs, metas = by_system[ch.system]
        ids.append(ch.id)
        docs.append(ch.text)
        metas.append({"system": ch.system, "source": ch.source,
                      "heading": ch.heading})
    total = 0
    for system, (ids, docs, metas) in by_system.items():
        if ids:
            store.add_texts(system, ids, docs, metas)
            total += len(ids)
    return total


def search_texts(
    store: TextStore,
    query: str,
    system: str,
    k: int = 5,
) -> List[SearchHit]:
    """Retrieve the top-``k`` corpus passages for ``query`` within ``system``.

    This is the function the future agent layer calls as its ``search_texts``
    tool — it returns interpretive prose to *support* a reading, never the
    positional facts (those come from the deterministic engine).
    """
    if system not in SYSTEMS:
        raise ValueError(f"unknown system {system!r}; use one of {SYSTEMS}")
    return store.query(system, query, k=k)
