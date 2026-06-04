# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Text processing pipelines used as benchmark columns.

Each pipeline is a callable: str -> str.

Pipelines
---------
baked       Raw fix() output — simulates what comes out of a legacy PDF/OCR.
nfkc        Unicode NFKC only — the standard "free" baseline.
camel       CAMeL Tools normalize_unicode — NFKC + alef/yaa variants.
repair      arabic-repair (our tool) — de-shape + restore logical order.
clean       Identity — the ground truth.
"""
from __future__ import annotations

import unicodedata
from typing import Callable

import arabic_rt as ar_rt
import arabic_repair as ar_repair


def _pipeline_baked(text: str) -> str:
    """Simulate PDF/OCR contamination: fix() bakes logical -> visual order."""
    return ar_rt.fix(text)


def _pipeline_nfkc(text: str) -> str:
    """NFKC only: de-shapes presentation forms, does NOT restore word order."""
    return unicodedata.normalize("NFKC", ar_rt.fix(text))


def _pipeline_camel(text: str) -> str:
    """CAMeL Tools normalize_unicode applied to baked text.

    Falls back to NFKC if camel-tools is not installed or fails to import
    (e.g. Python 3.14 compatibility issues).
    """
    baked = ar_rt.fix(text)
    try:
        from camel_tools.utils.normalize import normalize_unicode
        return normalize_unicode(baked)
    except Exception:
        return unicodedata.normalize("NFKC", baked)


def _pipeline_repair(text: str) -> str:
    """arabic-repair applied to baked text: de-shape + restore logical order."""
    return ar_repair.repair(ar_rt.fix(text))


def _pipeline_clean(text: str) -> str:
    """Identity — ground truth logical Arabic."""
    return text


# Ordered list of (pipeline_id, label, callable)
PIPELINES: list[tuple[str, str, Callable[[str], str]]] = [
    ("clean",  "Clean (baseline)",   _pipeline_clean),
    ("baked",  "Baked / raw",        _pipeline_baked),
    ("nfkc",   "NFKC only",          _pipeline_nfkc),
    ("camel",  "CAMeL Tools",        _pipeline_camel),
    ("repair", "arabic-repair",      _pipeline_repair),
]


def camel_available() -> bool:
    """True if camel-tools imports cleanly."""
    try:
        from camel_tools.utils.normalize import normalize_unicode  # noqa: F401
        return True
    except Exception:
        return False
