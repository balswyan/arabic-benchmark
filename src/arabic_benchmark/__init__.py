# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""arabic-benchmark — prove the visual-order reordering gap.

Measures two things for five text pipelines
(clean baseline / baked / NFKC-only / CAMeL-Tools / arabic-repair):

1. **Tokenizer blowup** — how many more subword tokens does a baked
   Arabic string consume compared with clean logical Arabic?
2. **Retrieval recall** — if your vector index was built on clean text,
   how many queries survive baking? Does NFKC/CAMeL-Tools restore recall?
   Does arabic-repair?

Quick start::

    python -m arabic_benchmark               # both metrics, default corpus
    python -m arabic_benchmark --no-retrieval  # tokenizer only (no download)
    python -m arabic_benchmark --json > results.json

Programmatic use::

    from arabic_benchmark import run_benchmark, BenchmarkResult
    result = run_benchmark()
    print(result.tokenizer_table)
"""
from __future__ import annotations

from ._runner import BenchmarkResult, run_benchmark

__version__ = "0.1.0"
__all__ = ["BenchmarkResult", "run_benchmark"]
