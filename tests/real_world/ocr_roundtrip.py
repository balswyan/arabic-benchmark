"""Real image OCR round-trip: render Arabic to PNG, OCR it, inspect.

Honest negative result: modern neural OCR (EasyOCR, which ships python-bidi)
returns logical-order Arabic already, so it does NOT produce baked text. The
visual-order contamination this benchmark targets is characteristic of legacy
PDF text layers and Tesseract-style extraction, not every OCR engine.

    pip install arabic-rt arabic-repair pillow easyocr
    python tests/real_world/ocr_roundtrip.py
"""
from __future__ import annotations
import os
import tempfile

import arabic_rt as ar
import arabic_repair as arep
from PIL import Image, ImageDraw, ImageFont

CLEAN = "العربية لغة جميلة وقديمة"
FONT_CANDIDATES = [
    os.environ.get("ARABIC_FONT", ""),
    r"C:\Windows\Fonts\arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    for p in FONT_CANDIDATES:
        if p and os.path.isfile(p):
            return ImageFont.truetype(p, size)
    raise SystemExit("No Arabic-capable TTF found; set ARABIC_FONT=/path/to/font.ttf")


def cps(s: str, n: int = 12) -> str:
    return " ".join(f"U+{ord(c):04X}" for c in s[:n])


def main() -> None:
    baked = ar.fix(CLEAN)  # so a naive renderer draws correct Arabic glyphs
    img = Image.new("RGB", (900, 160), "white")
    ImageDraw.Draw(img).text((30, 50), baked, fill="black", font=_font(56))
    png = os.path.join(tempfile.gettempdir(), "arabic_sample.png")
    img.save(png)

    import easyocr
    reader = easyocr.Reader(["ar"], gpu=False, verbose=False)
    ocr_text = " ".join(reader.readtext(png, detail=0)).strip()
    info = arep.detect(ocr_text)

    print("CLEAN     :", CLEAN, "|", cps(CLEAN))
    print("OCR raw   :", ocr_text, "|", cps(ocr_text))
    print("  detect():", info.contamination_type, f"({info.contaminated_ratio:.0%})")
    print("  OCR == clean? ", ocr_text == CLEAN)
    print("\nNote: EasyOCR returns logical order; repair() is a no-op on clean text.")


if __name__ == "__main__":
    main()
