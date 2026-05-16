import os
import sys
import time
import logging
import traceback
from pathlib import Path
from memory_manager import MemoryManager
from playwright_automation import YouTubeAutomation
import pyperclip
import pyautogui
import pygetwindow as gw

# ===== CONFIGURATION =====
TITLES_FILE = "titles.txt"
MEMORY_FILE = "memory.json"
TARGET_WINDOW_TITLE = "Video Downloader Standard"  # Adjust if needed
HEADLESS = False  # Set to False to see what's happening

# ===== LOGGING SETUP =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("batch_automation.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

def activate_target_window():
    """Locate and focus the target application."""
    logger.info(f"Looking for window: '{TARGET_WINDOW_TITLE}'")
    try:
        windows = gw.getWindowsWithTitle(TARGET_WINDOW_TITLE)
        if not windows:
            logger.warning(f"Window '{TARGET_WINDOW_TITLE}' not found. Skipping desktop automation.")
            return False

        win = windows[0]
        if win.isMinimized:
            win.restore()
        win.activate()
        time.sleep(1)
        return True
    except Exception as e:
        logger.error(f"Error activating window: {e}")
        return False

def automate_download(url):
    """Paste URL and trigger download in the target app."""
    if not activate_target_window():
        return False

    try:
        logger.info(f"Automating download for: {url}")
        # Focus input and paste
        pyautogui.hotkey("ctrl", "l") # Common for address bars
        time.sleep(0.5)
        pyperclip.copy(url)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)
        pyautogui.press("enter")
        logger.info("Download triggered in app")
        time.sleep(2)
        return True
    except Exception as e:
        logger.error(f"Desktop automation failed: {e}")
        return False

def main():
    # Ensure stdout handles emojis if possible, or ignore them
    if sys.stdout.encoding != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    memory = MemoryManager(MEMORY_FILE)
    
    # Load titles if pending is empty
    if not memory.data["pending"] and not memory.data["completed"]:
        if os.path.exists(TITLES_FILE):
            with open(TITLES_FILE, 'r', encoding='utf-8') as f:
                titles = [line.strip() for line in f if line.strip()]
            memory.set_pending(titles)
            logger.info(f"Loaded {len(titles)} titles from {TITLES_FILE}")
        else:
            logger.error(f"{TITLES_FILE} not found!")
            return

    logger.info(memory.get_status())

    with YouTubeAutomation() as yt:
        yt.config.headless = HEADLESS
        yt.launch()
        yt.create_page()

        while True:
            query = memory.get_next_title()
            if not query:
                logger.info("All titles processed!")
                break

            logger.info(f"Processing: {query}")
            try:
                # 1. Search and get first video info
                result = yt.search_and_get_first_video(query)
                video_url = result["url"]
                video_title = result["title"]

                logger.info(f"Found: {video_title} -> {video_url}")

                # 2. Copy to clipboard (as requested)
                pyperclip.copy(video_url)
                logger.info("URL copied to clipboard")

                # 3. Optional: Automate desktop downloader
                # automate_download(video_url)

                # 4. Mark as completed
                memory.mark_completed(query, video_title, video_url)
                logger.info(f"Successfully processed: {query}")
                
                # Small delay between requests
                time.sleep(2)

            except Exception as e:
                logger.error(f"Failed to process '{query}': {e}")
                # memory.mark_failed(query, str(e)) # Uncomment to skip on failure
                # For now, let's just stop or wait
                time.sleep(5)
                break 

            logger.info(memory.get_status())

if __name__ == "__main__":
    main()
