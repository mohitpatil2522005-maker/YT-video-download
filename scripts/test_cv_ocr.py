#!/usr/bin/env python3
"""Focused smoke tests for the OpenCV/PyTesseract visual-search helpers."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.cv_ocr import _sanitize_query, ocr_extract_text, template_match, derive_search_query_from_reference


def make_text_image(text: str, path: str) -> None:
    image = Image.new("RGB", (800, 240), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((40, 80), text, fill="black", font=font)
    image.save(path)


def main() -> int:
    print("Running CV/OCR smoke tests...")

    assert _sanitize_query("  YouTube  search:  best   music! ") == "YouTube+search+best+music"
    print("✓ sanitize_query")

    with tempfile.TemporaryDirectory() as tmpdir:
        screenshot_path = os.path.join(tmpdir, "screenshot.png")
        reference_path = os.path.join(tmpdir, "reference.png")

        make_text_image("Best Music Mix", screenshot_path)
        make_text_image("Best Music Mix", reference_path)

        screenshot_bytes = Path(screenshot_path).read_bytes()

        assert template_match(screenshot_bytes, reference_path, threshold=0.5) is not None
        print("✓ template_match")

        extracted = ocr_extract_text(screenshot_bytes)
        print(f"OCR output: {extracted!r}")
        assert isinstance(extracted, str)

        query = derive_search_query_from_reference(screenshot_bytes, reference_path)
        print(f"Derived query: {query!r}")
        assert query

    print("All CV/OCR smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
