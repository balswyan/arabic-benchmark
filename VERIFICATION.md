# Independent verification

This document records an independent reproduction of the benchmark and two
real-world round-trip tests (PDF and image OCR). Scripts live in
[`tests/real_world/`](tests/real_world/).

## Environment

| | |
|---|---|
| Python | 3.14.4 |
| Tokenizer | `tiktoken` `cl100k_base` (GPT-4 / GPT-3.5) |
| Embeddings | `sentence-transformers` `paraphrase-multilingual-MiniLM-L12-v2` |
| Packages | `arabic-rt` 0.1.4, `arabic-repair` 0.1.0 |

## 1. Benchmark reproduction (`python -m arabic_benchmark`)

Both halves reproduce the published numbers exactly.

```
TOKENIZER BLOWUP (tokens / word)          RETRIEVAL RECALL
Pipeline          Tok/Word  vs Clean      Pipeline          R@1    R@5    R@10   ΔR@5
Clean                 4.22     —          Clean            100%   100%   100%     —
Baked / raw          14.92  +253%         Baked / raw        7%    27%    43%   −73%
NFKC only             4.77   +13%         NFKC only          7%    27%    43%   −73%
CAMeL Tools *         4.77   +13%         CAMeL Tools *      7%    27%    43%   −73%
arabic-repair         4.22     0%         arabic-repair    100%   100%   100%     0%
```

`*` **CAMeL Tools row.** In this run `camel-tools` was not importable on Python 3.14, so the
benchmark used its NFKC fallback for that column (it prints `CAMeL Tools: not available
(using NFKC fallback)`). The result is expected to equal the NFKC row regardless, because
`normalize_unicode` is NFKC plus character-level variant folding and does not reorder words.

## 2. Real PDF round-trip (`tests/real_world/pdf_roundtrip.py`)

The benchmark uses *simulated* contamination. This test renders a sentence into an **actual
PDF** (reportlab) and extracts it back with a **standard extractor** (pdfplumber / pdfminer):

```
CLEAN (ground truth) : العربية لغة جميلة وقديمة
  code points        : U+0627 U+0644 U+0639 U+0631 U+0628 U+064A U+0629 …  (base letters)

EXTRACTED from PDF   : ﺔﻤﻳﺪﻗﻭ ﺔﻠﻴﻤﺟ ﺔﻐﻟ ﺔﻴﺑﺮﻌﻟﺍ
  code points        : U+FE94 U+FEE4 U+FEF3 U+FEAA U+FED7 U+FEED …  (presentation forms, reversed)
  detect()           : fully_baked (100%)

NFKC(extracted)      : ةميدقو ةليمج ةغل ةيبرعلا   →  base letters, but order still reversed (≠ clean)
repair(extracted)    : العربية لغة جميلة وقديمة   →  byte-identical to clean  ✓
```

Confirms the core claim on a real file: NFKC fixes characters but not order; `repair` restores both.

## 3. Real image OCR (`tests/real_world/ocr_roundtrip.py`)

An honest negative result worth recording. We render Arabic to a PNG and run **EasyOCR**:

```
OCR raw  : العربية لغة جميلة وقديمة   →  detect() = clean (0%)   (already logical order)
```

Modern neural OCR (EasyOCR ships `python-bidi`) returns **logical order already** — it does not
produce baked text. The visual-order contamination this benchmark targets is characteristic of
**legacy PDF text layers and Tesseract-style extraction**, not every OCR engine. Treat `repair()`
as a safe, no-op-on-clean normalization step.

---

*Reproduced June 2026. See `tests/real_world/` to re-run.*
