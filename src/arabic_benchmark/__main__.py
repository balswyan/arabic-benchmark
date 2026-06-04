"""python -m arabic_benchmark entry point."""
from __future__ import annotations

import argparse
import sys

from ._runner import run_benchmark


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark Arabic text repair pipelines (tokenizer blowup + retrieval recall)."
    )
    parser.add_argument(
        "--no-retrieval", action="store_true",
        help="Skip the retrieval benchmark (no sentence-transformers download needed)."
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output results as JSON instead of a human-readable table."
    )
    parser.add_argument(
        "--model", default="paraphrase-multilingual-MiniLM-L12-v2",
        help="sentence-transformers model for retrieval (default: paraphrase-multilingual-MiniLM-L12-v2)."
    )
    args = parser.parse_args()

    result = run_benchmark(
        run_retrieval=not args.no_retrieval,
        retrieval_model=args.model,
        verbose=not args.json,
    )

    if args.json:
        print(result.to_json())
    else:
        print(result.tokenizer_table)
        if result.retrieval_results:
            print(result.retrieval_table)
        print(result.summary)


if __name__ == "__main__":
    main()
