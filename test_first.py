from playwright_automation import YouTubeAutomation
import sys

def test_first():
    try:
        # Context manager handles launch and create_page
        with YouTubeAutomation() as yt:
            yt.config.headless = True
            # yt.launch()  # REMOVED: context manager already does this
            # yt.create_page() # REMOVED: context manager already does this
            
            query = "Claude Code is FREE & UNLIMITED Now?! (No GPU Needed)"
            print(f"Searching for: {query}")
            res = yt.search_and_get_first_video(query)
            print("\n--- RESULT ---")
            print(f"Title: {res['title']}")
            print(f"URL: {res['url']}")
            print("--------------")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_first()
