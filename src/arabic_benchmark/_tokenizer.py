# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not available with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tokenizer blowup measurement.

Metric: average tokens-per-word ratio across the corpus.

A "word" is a whitespace-separated token in the original clean text.
"Tokens" are subword units produced by the tokenizer.

Baked presentation-form Arabic typically causes 2-5x blowup because
the tokenizer has no entries for these rare codepoints and falls back
to character-level or byte-level splits.

Tokenizers supported (auto-detected in priority order):
  1. tiktoken  (cl100k_base — GPT-4 / GPT-3.5-turbo)
  2. transformers AutoTokenizer with "bert-base-multilingual-cased"
     (always available if `transformers` is installed, no download for
      the tokenizer config — only vocab, ~180 MB on first use)

At least one must be installed.  tiktoken is recommended (lightweight,
no model download).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenizerResult:
    """Per-pipeline token statistics."""
    pipeline_id: str
    label: str
    avg_tokens_per_word: float
    total_tokens: int
    total_words: int
    blowup_vs_clean: float   # ratio relative to clean baseline (1.0 = same)


def _count_tokens_tiktoken(texts: list[str]) -> int:
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    return sum(len(enc.encode(t)) for t in texts)


def _count_tokens_hf(texts: list[str]) -> int:
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
    return sum(
        len(tok.encode(t, add_special_tokens=False))
        for t in texts
    )


def _get_token_counter():
    """Return the best available token counter."""
    try:
        import tiktoken  # noqa: F401
        return _count_tokens_tiktoken, "tiktoken/cl100k_base"
    except ImportError:
        pass
    try:
        from transformers import AutoTokenizer  # noqa: F401
        return _count_tokens_hf, "bert-base-multilingual-cased"
    except ImportError:
        pass
    raise ImportError(
        "No tokenizer available. Install one of:\n"
        "  pip install tiktoken\n"
        "  pip install transformers"
    )


def run_tokenizer_benchmark(
    corpus: list[str],
    pipelines: list[tuple[str, str, object]],
) -> list[TokenizerResult]:
    """Measure tokenizer blowup for each pipeline.

    Parameters
    ----------
    corpus:
        List of clean Arabic sentences (ground truth).
    pipelines:
        List of (pipeline_id, label, callable) tuples as defined in _pipelines.

    Returns
    -------
    List of TokenizerResult, one per pipeline.
    """
    counter, tokenizer_name = _get_token_counter()
    print(f"  Tokenizer: {tokenizer_name}")

    results: list[TokenizerResult] = []
    clean_tpw: float | None = None

    for pid, label, fn in pipelines:
        processed = [fn(s) for s in corpus]
        total_words = sum(len(s.split()) for s in corpus)
        total_tokens = counter(processed)
        avg_tpw = total_tokens / total_words if total_words else 0.0

        if pid == "clean":
            clean_tpw = avg_tpw

        blowup = (avg_tpw / clean_tpw) if clean_tpw else 1.0

        results.append(TokenizerResult(
            pipeline_id=pid,
            label=label,
            avg_tokens_per_word=avg_tpw,
            total_tokens=total_tokens,
            total_words=total_words,
            blowup_vs_clean=blowup,
        ))

    return results
