# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Result formatting: plain-text table + JSON export."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._tokenizer import TokenizerResult
    from ._retrieval import RetrievalResult


def _delta_str(delta: float, is_ratio: bool = False) -> str:
    """Format a delta as a signed string."""
    if abs(delta) < 0.001:
        return "  —"
    if is_ratio:
        sign = "+" if delta > 0 else ""
        return f"{sign}{delta * 100:.0f}%"
    sign = "+" if delta > 0 else ""
    return f"{sign}{delta:.2f}x"


def format_tokenizer_table(results: list["TokenizerResult"]) -> str:
    col_w = 22
    lines = [
        "\n" + "=" * 72,
        "  TOKENIZER BLOWUP  (tokens / word — lower is better)",
        "=" * 72,
        f"  {'Pipeline':<{col_w}} {'Tok/Word':>9} {'vs Clean':>10} {'Total Tok':>11}",
        "  " + "-" * 68,
    ]
    for r in results:
        blowup = _delta_str(r.blowup_vs_clean - 1.0, is_ratio=True) if r.pipeline_id != "clean" else "  —"
        lines.append(
            f"  {r.label:<{col_w}} {r.avg_tokens_per_word:>9.2f} {blowup:>10} {r.total_tokens:>11,}"
        )
    lines.append("=" * 72)
    return "\n".join(lines)


def format_retrieval_table(results: list["RetrievalResult"]) -> str:
    col_w = 22
    lines = [
        "\n" + "=" * 72,
        "  RETRIEVAL RECALL  (fraction of correct retrievals — higher is better)",
        "=" * 72,
        f"  {'Pipeline':<{col_w}} {'R@1':>7} {'R@5':>7} {'R@10':>7} {'ΔR@5':>8}",
        "  " + "-" * 68,
    ]
    for r in results:
        d5 = _delta_str(r.delta_at_5, is_ratio=True) if r.pipeline_id != "clean" else "  —"
        lines.append(
            f"  {r.label:<{col_w}}"
            f" {r.recall_at_1:>6.0%}"
            f" {r.recall_at_5:>6.0%}"
            f" {r.recall_at_10:>6.0%}"
            f" {d5:>8}"
        )
    lines.append("=" * 72)
    return "\n".join(lines)


def format_summary(tok_results: list["TokenizerResult"],
                   ret_results: list["RetrievalResult"] | None) -> str:
    lines = ["\n--- KEY FINDINGS ---"]

    # Tokenizer
    tok_map = {r.pipeline_id: r for r in tok_results}
    if "baked" in tok_map and "clean" in tok_map:
        blowup_pct = (tok_map["baked"].blowup_vs_clean - 1.0) * 100
        lines.append(
            f"  Tokenizer blowup (baked vs clean):   +{blowup_pct:.0f}% more tokens"
        )
    if "nfkc" in tok_map and "clean" in tok_map:
        nfkc_pct = (tok_map["nfkc"].blowup_vs_clean - 1.0) * 100
        sign = f"+{nfkc_pct:.0f}%" if nfkc_pct > 0 else f"{nfkc_pct:.0f}%"
        lines.append(
            f"  Tokenizer blowup (NFKC only):         {sign} vs clean"
            + ("  ← NFKC de-shapes but order still wrong" if nfkc_pct > 1 else "  ← NFKC restores tokens (de-shaping works)")
        )
    if "repair" in tok_map and "clean" in tok_map:
        rep_pct = (tok_map["repair"].blowup_vs_clean - 1.0) * 100
        sign = f"+{rep_pct:.0f}%" if rep_pct > 0 else f"{rep_pct:.0f}%"
        lines.append(f"  Tokenizer blowup (arabic-repair):    {sign} vs clean")

    # Retrieval
    if ret_results:
        ret_map = {r.pipeline_id: r for r in ret_results}
        if "baked" in ret_map:
            lines.append(
                f"  Recall@5 drop (baked vs clean):      {ret_map['baked'].delta_at_5 * 100:+.0f}%"
            )
        if "nfkc" in ret_map:
            lines.append(
                f"  Recall@5 drop (NFKC only):           {ret_map['nfkc'].delta_at_5 * 100:+.0f}%"
                + ("  ← NFKC fails: order still reversed" if ret_map['nfkc'].delta_at_5 < -0.05 else "")
            )
        if "repair" in ret_map:
            lines.append(
                f"  Recall@5 delta (arabic-repair):      {ret_map['repair'].delta_at_5 * 100:+.0f}%"
            )
    return "\n".join(lines)


def to_json(tok_results: list["TokenizerResult"],
            ret_results: list["RetrievalResult"] | None) -> str:
    data: dict = {
        "tokenizer": [
            {
                "pipeline_id": r.pipeline_id,
                "label": r.label,
                "avg_tokens_per_word": round(r.avg_tokens_per_word, 4),
                "blowup_vs_clean": round(r.blowup_vs_clean, 4),
                "total_tokens": r.total_tokens,
                "total_words": r.total_words,
            }
            for r in tok_results
        ],
        "retrieval": (
            [
                {
                    "pipeline_id": r.pipeline_id,
                    "label": r.label,
                    "recall_at_1": round(r.recall_at_1, 4),
                    "recall_at_5": round(r.recall_at_5, 4),
                    "recall_at_10": round(r.recall_at_10, 4),
                    "delta_at_5": round(r.delta_at_5, 4),
                }
                for r in ret_results
            ]
            if ret_results else None
        ),
    }
    return json.dumps(data, ensure_ascii=False, indent=2)
