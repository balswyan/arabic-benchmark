# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Retrieval / embedding recall measurement.

Metric: Recall@k

Setup
-----
- Embed all sentences from the corpus using their CLEAN form -> the "index".
- For each pipeline, apply its transformation to every sentence -> "queries".
- For each query, retrieve the top-k most similar sentences from the index
  by cosine similarity.
- A hit is scored when the correct sentence (same position in corpus) appears
  in the top-k results.
- Recall@k = hits / total_sentences.

Why this matters
----------------
If the retrieval index was built on clean text (which is the normal production
case), baked queries will miss their counterparts almost entirely because the
embedding model has no way to know that "ﺔﻨﺳ" and "سنة" are the same word.
arabic-repair converts the query back to logical form before embedding, so
recall is restored.

Model
-----
sentence-transformers "paraphrase-multilingual-MiniLM-L12-v2" — 50 languages,
~120 MB, no GPU required.  First run downloads and caches it automatically.

Requires:
  pip install sentence-transformers
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RetrievalResult:
    """Per-pipeline retrieval recall."""
    pipeline_id: str
    label: str
    recall_at_1: float
    recall_at_5: float
    recall_at_10: float
    delta_at_1: float    # relative to clean baseline (0.0 = same)
    delta_at_5: float
    delta_at_10: float


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between a (n, d) and b (m, d) -> (n, m)."""
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-9)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-9)
    return a_norm @ b_norm.T


def _recall_at_k(sim_matrix: np.ndarray, k: int) -> float:
    """Fraction of queries where the correct doc is in the top-k results."""
    n = sim_matrix.shape[0]
    hits = 0
    for i in range(n):
        top_k = np.argsort(sim_matrix[i])[::-1][:k]
        if i in top_k:
            hits += 1
    return hits / n if n else 0.0


def run_retrieval_benchmark(
    corpus: list[str],
    pipelines: list[tuple[str, str, object]],
    model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
) -> list[RetrievalResult]:
    """Measure embedding recall for each pipeline.

    Parameters
    ----------
    corpus:
        List of clean Arabic sentences.
    pipelines:
        List of (pipeline_id, label, callable).
    model_name:
        sentence-transformers model to use.

    Returns
    -------
    List of RetrievalResult, one per pipeline.
    Raises ImportError if sentence-transformers is not installed.
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise ImportError(
            "sentence-transformers is required for the retrieval benchmark.\n"
            "Install it with: pip install sentence-transformers"
        )

    print(f"  Embedding model: {model_name}")
    model = SentenceTransformer(model_name)

    # Build index from clean corpus
    print("  Encoding clean index...")
    index_embeddings = model.encode(corpus, show_progress_bar=False, convert_to_numpy=True)

    results: list[RetrievalResult] = []
    clean_r1 = clean_r5 = clean_r10 = None

    for pid, label, fn in pipelines:
        processed = [fn(s) for s in corpus]
        print(f"  Encoding [{label}]...")
        query_embeddings = model.encode(processed, show_progress_bar=False, convert_to_numpy=True)

        sim = _cosine_similarity(query_embeddings, index_embeddings)
        r1  = _recall_at_k(sim, 1)
        r5  = _recall_at_k(sim, 5)
        r10 = _recall_at_k(sim, 10)

        if pid == "clean":
            clean_r1, clean_r5, clean_r10 = r1, r5, r10

        d1  = (r1  - clean_r1)  if clean_r1  is not None else 0.0
        d5  = (r5  - clean_r5)  if clean_r5  is not None else 0.0
        d10 = (r10 - clean_r10) if clean_r10 is not None else 0.0

        results.append(RetrievalResult(
            pipeline_id=pid,
            label=label,
            recall_at_1=r1,
            recall_at_5=r5,
            recall_at_10=r10,
            delta_at_1=d1,
            delta_at_5=d5,
            delta_at_10=d10,
        ))

    return results
