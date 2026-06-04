# Changelog

## 0.1.0 — 2026-06-04
- Initial release.
- Built-in 30-sentence MSA corpus (no download required).
- Five pipelines: clean / baked / NFKC-only / CAMeL-Tools / arabic-repair.
- Tokenizer blowup metric via tiktoken (cl100k_base / GPT-4) with HF tokenizers fallback.
- Retrieval Recall@1/5/10 via sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2).
- CLI: `python -m arabic_benchmark [--no-retrieval] [--json]`.
- Programmatic API: `run_benchmark()` → `BenchmarkResult`.
- Key findings on default corpus: baked text causes +253% tokenizer blowup and −73% R@5
  recall drop; NFKC and CAMeL Tools restore tokens but NOT recall; arabic-repair restores both.
