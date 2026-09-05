import sys
import os

# Set up path for scripts module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.cv_ocr import extract_queries_from_image

IMAGE_PATH = r"c:\Users\mohit\Desktop\PROJECTS\YT video download\images\photo_2026-09-05_18-31-25.jpg"

print(f"Checking image: {IMAGE_PATH}")
print(f"Image exists: {os.path.exists(IMAGE_PATH)}")

if os.path.exists(IMAGE_PATH):
    print("\n--- Running OCR extraction ---")
    queries = extract_queries_from_image(IMAGE_PATH)
    print(f"\nExtracted {len(queries)} query/queries:")
    for i, q in enumerate(queries, 1):
        print(f"  {i}. {q}")
else:
    print("ERROR: Image file not found!")
