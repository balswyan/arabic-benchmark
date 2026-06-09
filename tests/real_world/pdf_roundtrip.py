"""Real PDF round-trip: render Arabic into a PDF, extract it back, repair.

Shows that a standard PDF extractor returns visual-order ("baked") Arabic, that
NFKC fixes characters but not word order, and that arabic-repair restores it.

    pip install arabic-rt arabic-repair reportlab pdfplumber
    python tests/real_world/pdf_roundtrip.py
"""
from __future__ import annotations
import os
import tempfile
import unicodedata

import arabic_rt as ar
import arabic_repair as arep
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pdfplumber

CLEAN = "العربية لغة جميلة وقديمة"

# An Arabic-capable TTF. Override with ARABIC_FONT env var if needed.
FONT_CANDIDATES = [
    os.environ.get("ARABIC_FONT", ""),
    r"C:\Windows\Fonts\arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]


def _font() -> str:
    for p in FONT_CANDIDATES:
        if p and os.path.isfile(p):
            return p
    raise SystemExit("No Arabic-capable TTF found; set ARABIC_FONT=/path/to/font.ttf")


def cps(s: str, n: int = 12) -> str:
    return " ".join(f"U+{ord(c):04X}" for c in s[:n])


def main() -> None:
    baked = ar.fix(CLEAN)  # how legacy PDFs store Arabic (pre-shaped, visual order)

    pdfmetrics.registerFont(TTFont("AR", _font()))
    pdf_path = os.path.join(tempfile.gettempdir(), "arabic_sample.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setFont("AR", 22)
    c.drawString(120, 700, baked)
    c.save()

    with pdfplumber.open(pdf_path) as pdf:
        extracted = (pdf.pages[0].extract_text() or "").strip()

    nfkc = unicodedata.normalize("NFKC", extracted)
    repaired = arep.repair(extracted)
    info = arep.detect(extracted)

    print("CLEAN (ground truth):", CLEAN, "|", cps(CLEAN))
    print("EXTRACTED from PDF  :", extracted, "|", cps(extracted))
    print("  detect():", info.contamination_type, f"({info.contaminated_ratio:.0%})")
    print("NFKC(extracted)     :", nfkc, "| == clean?", nfkc == CLEAN)
    print("repair(extracted)   :", repaired, "| == clean?", repaired == CLEAN)

    assert info.contamination_type == "fully_baked"
    assert nfkc != CLEAN, "NFKC unexpectedly fixed word order"
    assert repaired == CLEAN, "repair did not restore the clean sentence"
    print("\nOK - repair restored the clean sentence; NFKC did not.")


if __name__ == "__main__":
    main()
