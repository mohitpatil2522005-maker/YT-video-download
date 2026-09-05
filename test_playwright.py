"""Quick test to verify Playwright Chromium browser is available."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from playwright.sync_api import sync_playwright
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    print("Browser launched successfully!")
    page = browser.new_page()
    page.goto("https://www.youtube.com", timeout=30000)
    print(f"YouTube loaded. Title: {page.title()}")
    browser.close()
    p.stop()
    print("Browser closed successfully.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
