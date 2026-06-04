# arabic-benchmark

Proves the visual-order reordering gap: Arabic extracted from PDFs/OCR causes
**tokenizer blowup** and **retrieval recall collapse** that NFKC and CAMeL Tools
cannot fix — but `arabic-repair` can.

## Install

```bash
pip install arabic-benchmark[all]   # includes tiktoken + sentence-transformers
pip install arabic-benchmark        # core only (bring your own tokenizer)
```

## Run

```bash
python -m arabic_benchmark                   # full benchmark (downloads ~120 MB model on first run)
python -m arabic_benchmark --no-retrieval    # tokenizer only, no download
python -m arabic_benchmark --json            # machine-readable JSON output
```

## Example output

```
========================================================================
  TOKENIZER BLOWUP  (tokens / word — lower is better)
========================================================================
  Pipeline               Tok/Word   vs Clean   Total Tok
  --------------------------------------------------------------------
  Clean (baseline)           2.10        —          1,890
  Baked / raw                4.73    +125%          4,257
  NFKC only                  2.14     +2%           1,926
  CAMeL Tools                2.14     +2%           1,926
  arabic-repair              2.10     +0%           1,890
========================================================================

========================================================================
  RETRIEVAL RECALL  (fraction of correct retrievals — higher is better)
========================================================================
  Pipeline                R@1     R@5    R@10      ΔR@5
  --------------------------------------------------------------------
  Clean (baseline)       100%    100%    100%        —
  Baked / raw              3%     17%     27%      -83%
  NFKC only                3%     17%     27%      -83%  ← same as baked
  CAMeL Tools              3%     17%     27%      -83%  ← same as baked
  arabic-repair          100%    100%    100%       +0%
========================================================================
```

NFKC and CAMeL Tools remove presentation forms (fixing tokenization to ~clean
levels) but cannot restore reversed word order — so retrieval recall stays
broken. `arabic-repair` restores both.

## License

MPL-2.0
