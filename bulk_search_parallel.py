import time
import os
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

# Set stdout to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

def get_video_url(title):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, channel="chrome")
            context = browser.new_context()
            page = context.new_page()
            
            query = urllib.parse.quote_plus(title)
            search_url = f"https://www.youtube.com/results?search_query={query}"
            
            page.goto(search_url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_selector("ytd-video-renderer", timeout=20000)
            
            first_video = page.locator("ytd-video-renderer #video-title").first
            href = first_video.get_attribute("href")
            
            browser.close()
            
            if href:
                return f"https://www.youtube.com{href}" if not href.startswith("http") else href
            return f"No result for: {title}"
    except Exception as e:
        return f"Error for: {title} ({str(e)})"

def bulk_search_parallel():
    titles_file = "extracted_titles.txt"
    output_dir = r"C:\Users\mohit\Desktop\YT video downloa\New folder"
    output_file = os.path.join(output_dir, "yt copy links.txt")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(titles_file, "r", encoding="utf-8") as f:
        titles = [line.strip() for line in f if line.strip()]

    print(f"Found {len(titles)} titles to search. Using parallel workers...", flush=True)

    results = [None] * len(titles)

    def worker(index):
        title = titles[index]
        print(f"[{index+1}/{len(titles)}] Searching: {title.encode('ascii', 'ignore').decode('ascii')}...", flush=True)
        url = get_video_url(title)
        results[index] = url
        print(f"[{index+1}/{len(titles)}] Done: {url}", flush=True)

    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(worker, range(len(titles)))

    # Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        for url in results:
            if url:
                f.write(url + "\n")

    print(f"Finished! Results saved to {output_file}", flush=True)

if __name__ == "__main__":
    bulk_search_parallel()
