import os
import re
from typing import List, Optional, Tuple

import cv2
import numpy as np
import pytesseract
from PIL import Image

# Automatically find and set Tesseract executable path for Windows
TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
]
for p in TESSERACT_PATHS:
    if os.path.exists(p):
        pytesseract.pytesseract.tesseract_cmd = p
        break


def _decode_screenshot(screenshot_bytes: bytes) -> Optional[np.ndarray]:
    nparr = np.frombuffer(screenshot_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image


def _preprocess_for_template(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray, (3, 3), 0)


def _preprocess_for_ocr(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    enlarged = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    denoised = cv2.bilateralFilter(enlarged, 9, 75, 75)
    _, thresholded = cv2.threshold(
        denoised,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )
    return thresholded


def _sanitize_query(text: str) -> str:
    cleaned = re.sub(r"[^\w\s-]+", " ", text, flags=re.UNICODE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return "+".join(part for part in cleaned.split(" ") if part)


def _ocr_image(image: np.ndarray) -> str:
    if image is None or image.size == 0:
        return ""

    prepared = _preprocess_for_ocr(image)
    pil_image = Image.fromarray(prepared)

    try:
        text = pytesseract.image_to_string(
            pil_image,
            config="--psm 6 --oem 3",
        )
    except Exception:
        return ""

    return text.strip()


def template_match(
    screenshot_bytes: bytes,
    template_path: str,
    threshold: float = 0.7,
    scales: Tuple[float, ...] = (0.75, 0.9, 1.0, 1.1, 1.25),
) -> Optional[Tuple[int, int, int, int]]:
    screenshot = _decode_screenshot(screenshot_bytes)
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)

    if screenshot is None or template is None:
        return None

    screenshot_gray = _preprocess_for_template(screenshot)
    best_match: Optional[Tuple[float, Tuple[int, int, int, int]]] = None

    for scale in scales:
        scaled_template = cv2.resize(
            template,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC,
        )
        if scaled_template.size == 0:
            continue

        template_gray = _preprocess_for_template(scaled_template)
        if template_gray.shape[0] > screenshot_gray.shape[0] or template_gray.shape[1] > screenshot_gray.shape[1]:
            continue

        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if best_match is None or max_val > best_match[0]:
            height, width = template_gray.shape[:2]
            best_match = (max_val, (max_loc[0], max_loc[1], width, height))

    if best_match and best_match[0] >= threshold:
        return best_match[1]

    return None


def ocr_extract_text(screenshot_bytes: bytes, region: Optional[Tuple[int, int, int, int]] = None) -> str:
    screenshot = _decode_screenshot(screenshot_bytes)
    if screenshot is None:
        return ""

    if region:
        x, y, w, h = region
        x = max(x, 0)
        y = max(y, 0)
        w = max(w, 1)
        h = max(h, 1)
        screenshot = screenshot[y : y + h, x : x + w]

    return _ocr_image(screenshot)


def _reference_text_candidates(template_path: str) -> List[str]:
    candidates: List[str] = []

    if os.path.exists(template_path):
        template_image = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template_image is not None:
            reference_text = _ocr_image(template_image)
            if reference_text:
                candidates.append(reference_text)

    basename = os.path.splitext(os.path.basename(template_path))[0]
    if basename:
        candidates.append(basename.replace("_", " ").replace("-", " "))

    return candidates


def extract_queries_from_image(image_path: str) -> List[str]:
    """
    Extract multiple video titles/queries directly from the text inside the image.
    Ignores the image filename entirely.
    """
    if not os.path.exists(image_path):
        return []

    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        return []

    # Preprocess heavily for OCR to read lists of names
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    enlarged = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    denoised = cv2.bilateralFilter(enlarged, 9, 75, 75)
    _, thresholded = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    pil_image = Image.fromarray(thresholded)
    try:
        # psm 4 assumes a single column of text of variable sizes (good for lists of videos)
        text = pytesseract.image_to_string(pil_image, config="--psm 4")
    except Exception as e:
        print(f"OCR Error (Is Tesseract installed?): {e}")
        return []

    queries = []
    # Split text line by line to get individual video names
    for line in text.split('\n'):
        # Keep alphanumeric characters and basic punctuation
        cleaned = re.sub(r"[^\w\s\-\'\,]+", " ", line, flags=re.UNICODE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        # Filter out very short noisy lines (e.g., stray characters)
        if len(cleaned) > 5:
            queries.append(cleaned)
            
    return queries


def derive_search_query_from_reference(screenshot_bytes: bytes, template_path: str) -> str:
    """
    Derive a search query by combining OCR from the reference image,
    OCR from the matched region in the live screenshot, and a filename fallback.
    """
    candidates: List[str] = []

    # OCR from the reference image itself is the strongest hint when available.
    candidates.extend(_reference_text_candidates(template_path))

    # Try matching the reference against the live screenshot and OCR the context around it.
    bbox = template_match(screenshot_bytes, template_path)
    if bbox:
        x, y, w, h = bbox
        expand = max(40, int(max(w, h) * 0.35))
        region = (
            max(x - expand, 0),
            max(y - expand, 0),
            w + expand * 2,
            h + expand * 2,
        )
        matched_text = ocr_extract_text(screenshot_bytes, region)
        if matched_text:
            candidates.insert(0, matched_text)

    # As a last OCR attempt, read the whole screenshot in case the reference is not visible.
    full_text = ocr_extract_text(screenshot_bytes)
    if full_text:
        candidates.append(full_text)

    for candidate in candidates:
        query = _sanitize_query(candidate)
        if query:
            return query

    return _sanitize_query(os.path.splitext(os.path.basename(template_path))[0])
