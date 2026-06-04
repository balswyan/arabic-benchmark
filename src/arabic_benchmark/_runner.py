# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Top-level benchmark runner."""
from __future__ import annotations

from dataclasses import dataclass, field

from ._corpus import SENTENCES
from ._pipelines import PIPELINES, camel_available
from ._report import format_tokenizer_table, format_retrieval_table, format_summary, to_json
from ._tokenizer import TokenizerResult, run_tokenizer_benchmark


@dataclass
class BenchmarkResult:
    """Collected results from one benchmark run."""
    tokenizer_results: list[TokenizerResult]
    retrieval_results: list = field(default_factory=list)   # list[RetrievalResult] | []

    @property
    def tokenizer_table(self) -> str:
        return format_tokenizer_table(self.tokenizer_results)

    @property
    def retrieval_table(self) -> str:
        if not self.retrieval_results:
            return "(retrieval benchmark not run)"
        from ._report import format_retrieval_table
        return format_retrieval_table(self.retrieval_results)

    @property
    def summary(self) -> str:
        return format_summary(self.tokenizer_results, self.retrieval_results or None)

    def to_json(self) -> str:
        return to_json(self.tokenizer_results, self.retrieval_results or None)


def run_benchmark(
    corpus: list[str] | None = None,
    run_retrieval: bool = True,
    retrieval_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
    verbose: bool = True,
) -> BenchmarkResult:
    """Run the full benchmark.

    Parameters
    ----------
    corpus:
        Sentences to benchmark on.  Defaults to the built-in 30-sentence corpus.
    run_retrieval:
        Whether to run the retrieval benchmark (requires sentence-transformers
        and ~120 MB model download on first run).  Set False for tokenizer-only.
    retrieval_model:
        sentence-transformers model name for embeddings.
    verbose:
        Print progress to stdout.

    Returns
    -------
    BenchmarkResult
    """
    corpus = corpus or SENTENCES

    if verbose:
        print(f"arabic-benchmark  |  corpus: {len(corpus)} sentences")
        print(f"                  |  CAMeL Tools: {'available' if camel_available() else 'not available (using NFKC fallback)'}")
        print()

    # --- Tokenizer ---
    if verbose:
        print("[1/2] Tokenizer blowup...")
    tok_results = run_tokenizer_benchmark(corpus, PIPELINES)

    # --- Retrieval ---
    ret_results = []
    if run_retrieval:
        if verbose:
            print("\n[2/2] Retrieval recall...")
        try:
            from ._retrieval import run_retrieval_benchmark
            ret_results = run_retrieval_benchmark(corpus, PIPELINES, retrieval_model)
        except ImportError as e:
            if verbose:
                print(f"  SKIPPED: {e}")

    return BenchmarkResult(tokenizer_results=tok_results, retrieval_results=ret_results)
