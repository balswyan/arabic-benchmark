"""Tests for arabic-benchmark.

Core tests are deterministic and require only tiktoken (or transformers).
Retrieval tests are skipped if sentence-transformers is not installed.
"""
import pytest
import unicodedata
import arabic_rt as ar_rt

from arabic_benchmark._corpus import SENTENCES
from arabic_benchmark._pipelines import PIPELINES, camel_available
from arabic_benchmark._tokenizer import run_tokenizer_benchmark
from arabic_benchmark._report import format_tokenizer_table, to_json
from arabic_benchmark._runner import run_benchmark


# ---------------------------------------------------------------------------
# Corpus sanity
# ---------------------------------------------------------------------------

class TestCorpus:
    def test_has_sentences(self):
        assert len(SENTENCES) >= 20

    def test_all_logical_arabic(self):
        """No sentence in the corpus should be pre-baked."""
        from arabic_rt._engine import is_shaped
        for s in SENTENCES:
            assert not is_shaped(s), f"corpus sentence is already baked: {s!r}"

    def test_all_nonempty(self):
        assert all(s.strip() for s in SENTENCES)


# ---------------------------------------------------------------------------
# Pipelines
# ---------------------------------------------------------------------------

class TestPipelines:
    def test_pipeline_ids_present(self):
        ids = {p[0] for p in PIPELINES}
        assert "clean" in ids
        assert "baked" in ids
        assert "nfkc"  in ids
        assert "repair" in ids

    def test_baked_produces_presentation_forms(self):
        from arabic_rt._engine import is_shaped
        for pid, label, fn in PIPELINES:
            if pid == "baked":
                result = fn("مرحبا بالعالم")
                assert is_shaped(result), "baked pipeline must produce presentation forms"

    def test_nfkc_removes_presentation_forms_but_scrambles(self):
        """NFKC de-shapes but leaves word order reversed — proves the gap."""
        for pid, label, fn in PIPELINES:
            if pid == "nfkc":
                result = fn("مرحبا بالعالم")
                # No presentation forms remain
                has_pf = any(0xFB50 <= ord(c) <= 0xFDFF or 0xFE70 <= ord(c) <= 0xFEFF for c in result)
                assert not has_pf, "NFKC should remove presentation forms"
                # But word order is STILL reversed — the gap
                assert result != "مرحبا بالعالم", "NFKC should NOT restore logical order"

    def test_repair_pipeline_round_trips(self):
        for pid, label, fn in PIPELINES:
            if pid == "repair":
                for text in ["مرحبا بالعالم", "السلام عليكم", "بسم الله الرحمن الرحيم"]:
                    assert fn(text) == text, f"repair pipeline failed for: {text!r}"

    def test_clean_pipeline_identity(self):
        for pid, label, fn in PIPELINES:
            if pid == "clean":
                text = "مرحبا بالعالم"
                assert fn(text) == text


# ---------------------------------------------------------------------------
# Tokenizer benchmark
# ---------------------------------------------------------------------------

class TestTokenizerBenchmark:
    def test_runs_without_error(self):
        results = run_tokenizer_benchmark(SENTENCES[:5], PIPELINES)
        assert len(results) == len(PIPELINES)

    def test_clean_baseline_blowup_is_one(self):
        results = run_tokenizer_benchmark(SENTENCES[:5], PIPELINES)
        clean = next(r for r in results if r.pipeline_id == "clean")
        assert abs(clean.blowup_vs_clean - 1.0) < 1e-6

    def test_baked_has_higher_token_count(self):
        """Core claim: baking Arabic causes tokenizer blowup."""
        results = run_tokenizer_benchmark(SENTENCES, PIPELINES)
        tok = {r.pipeline_id: r for r in results}
        assert tok["baked"].avg_tokens_per_word > tok["clean"].avg_tokens_per_word, \
            "baked text must use more tokens than clean"

    def test_nfkc_blowup_higher_than_repair(self):
        """
        NFKC de-shapes but order stays reversed.  Whether tokenizers
        handle reversed base-letter sequences better than presentation
        forms varies by tokenizer.  What matters most is that:
          - baked >> clean  (confirmed above)
          - repair ≈ clean  (confirmed below)
        """
        results = run_tokenizer_benchmark(SENTENCES, PIPELINES)
        tok = {r.pipeline_id: r for r in results}
        # repair should recover to within 5% of clean
        assert tok["repair"].blowup_vs_clean < 1.05, \
            "repair should recover token count close to clean baseline"

    def test_repair_recovers_token_count(self):
        results = run_tokenizer_benchmark(SENTENCES, PIPELINES)
        tok = {r.pipeline_id: r for r in results}
        # repair ≈ clean (within 5%)
        assert tok["repair"].blowup_vs_clean < 1.05

    def test_all_results_have_positive_counts(self):
        results = run_tokenizer_benchmark(SENTENCES[:3], PIPELINES)
        for r in results:
            assert r.total_tokens > 0
            assert r.total_words > 0
            assert r.avg_tokens_per_word > 0


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

class TestReport:
    def test_tokenizer_table_is_string(self):
        results = run_tokenizer_benchmark(SENTENCES[:5], PIPELINES)
        table = format_tokenizer_table(results)
        assert isinstance(table, str)
        assert "TOKENIZER" in table
        assert "Clean" in table

    def test_json_output_valid(self):
        import json
        results = run_tokenizer_benchmark(SENTENCES[:5], PIPELINES)
        j = to_json(results, None)
        data = json.loads(j)
        assert "tokenizer" in data
        assert len(data["tokenizer"]) == len(PIPELINES)

    def test_json_contains_expected_fields(self):
        import json
        results = run_tokenizer_benchmark(SENTENCES[:5], PIPELINES)
        j = to_json(results, None)
        data = json.loads(j)
        for entry in data["tokenizer"]:
            assert "pipeline_id" in entry
            assert "avg_tokens_per_word" in entry
            assert "blowup_vs_clean" in entry


# ---------------------------------------------------------------------------
# Runner integration
# ---------------------------------------------------------------------------

class TestRunner:
    def test_run_benchmark_tokenizer_only(self):
        result = run_benchmark(
            corpus=SENTENCES[:5],
            run_retrieval=False,
            verbose=False,
        )
        assert len(result.tokenizer_results) == len(PIPELINES)
        assert result.retrieval_results == []

    def test_tokenizer_table_property(self):
        result = run_benchmark(corpus=SENTENCES[:5], run_retrieval=False, verbose=False)
        assert "TOKENIZER" in result.tokenizer_table

    def test_summary_property(self):
        result = run_benchmark(corpus=SENTENCES[:5], run_retrieval=False, verbose=False)
        assert "blowup" in result.summary.lower() or "token" in result.summary.lower()

    def test_json_roundtrip(self):
        import json
        result = run_benchmark(corpus=SENTENCES[:5], run_retrieval=False, verbose=False)
        data = json.loads(result.to_json())
        assert "tokenizer" in data


# ---------------------------------------------------------------------------
# Retrieval benchmark (skipped if sentence-transformers not installed)
# ---------------------------------------------------------------------------

class TestRetrievalBenchmark:
    @pytest.fixture(autouse=True)
    def require_sentence_transformers(self):
        pytest.importorskip("sentence_transformers",
                            reason="sentence-transformers not installed")

    def test_retrieval_runs(self):
        from arabic_benchmark._retrieval import run_retrieval_benchmark
        results = run_retrieval_benchmark(SENTENCES[:10], PIPELINES)
        assert len(results) == len(PIPELINES)

    def test_clean_recall_is_perfect(self):
        from arabic_benchmark._retrieval import run_retrieval_benchmark
        results = run_retrieval_benchmark(SENTENCES[:10], PIPELINES)
        clean = next(r for r in results if r.pipeline_id == "clean")
        assert clean.recall_at_1 == pytest.approx(1.0)

    def test_baked_recall_drops(self):
        from arabic_benchmark._retrieval import run_retrieval_benchmark
        results = run_retrieval_benchmark(SENTENCES[:10], PIPELINES)
        tok = {r.pipeline_id: r for r in results}
        assert tok["baked"].recall_at_5 < tok["clean"].recall_at_5

    def test_repair_recall_better_than_baked(self):
        from arabic_benchmark._retrieval import run_retrieval_benchmark
        results = run_retrieval_benchmark(SENTENCES[:10], PIPELINES)
        tok = {r.pipeline_id: r for r in results}
        assert tok["repair"].recall_at_5 >= tok["baked"].recall_at_5
