import time
import os
import sys
import urllib.parse
from playwright.sync_api import sync_playwright

# Set stdout to UTF-8 to handle emojis in terminal if possible
if sys.stdout.encoding != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

def bulk_search():
    titles_file = "extracted_titles.txt"
    output_dir = r"C:\Users\mohit\Desktop\YT video downloa\New folder"
    output_file = os.path.join(output_dir, "yt copy links.txt")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(titles_file, "r", encoding="utf-8") as f:
        titles = [line.strip() for line in f if line.strip()]

    print(f"Found {len(titles)} titles to search.", flush=True)

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context()
        page = context.new_page()

        for i, title in enumerate(titles):
            try:
                print(f"[{i+1}/{len(titles)}] Searching for: {title}...", flush=True)
            except:
                print(f"[{i+1}/{len(titles)}] Searching for next title...", flush=True)
            try:
                # URL encode search query
                query = urllib.parse.quote_plus(title)
                search_url = f"https://www.youtube.com/results?search_query={query}"
                
                page.goto(search_url, timeout=60000, wait_until="domcontentloaded")
                
                # Wait for video results
                page.wait_for_selector("ytd-video-renderer", timeout=15000)
                
                # Get the first video link
                first_video = page.locator("ytd-video-renderer #video-title").first
                href = first_video.get_attribute("href")
                
                if href:
                    if not href.startswith("http"):
                        url = f"https://www.youtube.com{href}"
                    else:
                        url = href
                    results.append(url)
                    print(f"   Found: {url}", flush=True)
                else:
                    print(f"   No URL found for: {title}", flush=True)
                    results.append(f"No result for: {title}")
                
            except Exception as e:
                print(f"   Error searching for '{title}': {e}", flush=True)
                results.append(f"Error for: {title}")
            
            # Small delay to be polite
            time.sleep(1)

        browser.close()

    # Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        for url in results:
            f.write(url + "\n")

    print(f"Finished! Results saved to {output_file}", flush=True)

if __name__ == "__main__":
    bulk_search()
