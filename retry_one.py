import urllib.parse
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel='chrome')
    page = browser.new_page()
    query = urllib.parse.quote_plus('Ultimate Free Editing Pack (SECRET MATERIAL)')
    page.goto(f'https://www.youtube.com/results?search_query={query}')
    page.wait_for_selector('ytd-video-renderer')
    url = page.locator('ytd-video-renderer #video-title').first.get_attribute('href')
    print(f"https://www.youtube.com{url}")
    browser.close()
