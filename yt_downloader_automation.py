"""
YouTube Video Download Automation Framework
==========================================

This script automates the process of:
1. Searching YouTube using text extracted from a reference image (OCR)
2. Extracting the first video URL from search results
3. Switching to a desktop video downloader application
4. Automating URL input and download triggering

Requirements:
- playwright
- pytesseract
- pygetwindow
- pyautogui
- pyperclip
- pillow
- numpy
- Tesseract OCR (separate installation)

Usage:
1. Install required packages: pip install -r requirements.txt
2. Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract
3. Update CONFIGURATION section with your specific values
4. Run: python yt_downloader_automation.py
"""

import logging
import sys
import time
import traceback
from pathlib import Path


# ===== DEPENDENCY CHECKING =====
def check_dependencies():
    """Check for required dependencies and return availability status."""
    deps = {
        "numpy": False,
        "pytesseract": False,
        "PIL": False,
        "playwright": False,
        "pygetwindow": False,
        "pyautogui": False,
        "pyperclip": False,
    }

    # Check each dependency
    try:
        import numpy

        deps["numpy"] = True
    except ImportError:
        pass

    try:
        import pytesseract

        deps["pytesseract"] = True
    except ImportError:
        pass

    try:
        from PIL import Image

        deps["PIL"] = True
    except ImportError:
        pass

    try:
        from playwright.sync_api import sync_playwright

        deps["playwright"] = True
    except ImportError:
        pass

    try:
        import pygetwindow as gw

        deps["pygetwindow"] = True
    except ImportError:
        pass

    try:
        import pyautogui

        deps["pyautogui"] = True
    except ImportError:
        pass

    try:
        import pyperclip

        deps["pyperclip"] = True
    except ImportError:
        pass

    return deps


# ===== CONFIGURATION =====
# !! UPDATE THESE VALUES FOR YOUR ENVIRONMENT !!
REFERENCE_IMAGE_PATH = r"C:\Users\mohit\Pictures\MEmu Photo\IMG_20260515_231534_845.jpg"
FALLBACK_QUERY = "YouTube video"  # Default fallback query if OCR fails
TARGET_WINDOW_TITLE = (
    "Video Downloader Standard"  # Exact window title of your downloader app
)

# ===== LOGGING SETUP =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("automation.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ===== HELPER FUNCTIONS =====
def get_reference_image_path(path_str):
    """Resolve reference image path: if directory, find first image file."""
    path = Path(path_str)
    if not path.exists():
        logger.error(f"Reference path does not exist: {path_str}")
        raise FileNotFoundError(f"Reference path not found: {path_str}")

    if path.is_file():
        logger.info(f"Using reference image file: {path}")
        return str(path)

    # If directory, search for image files
    if path.is_dir():
        logger.info(f"Reference path is a directory, searching for image files...")
        image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff"]
        image_files = []
        for ext in image_extensions:
            image_files.extend(path.glob(ext))
            image_files.extend(path.glob(ext.upper()))  # case-insensitive

        if not image_files:
            logger.error(f"No image files found in directory: {path_str}")
            raise FileNotFoundError(f"No image files found in directory: {path_str}")

        # Use the first image found
        selected = image_files[0]
        logger.info(f"Selected reference image: {selected}")
        return str(selected)

    raise ValueError(f"Invalid reference path: {path_str}")


def extract_text_from_image(image_path):
    """Extract text from an image using pytesseract OCR."""
    try:
        from PIL import Image
        import pytesseract

        logger.info(f"Extracting text from image: {image_path}")
        img = Image.open(image_path)
        # Convert to grayscale for better OCR results
        if img.mode != "L":
            img = img.convert("L")

        # Use pytesseract to extract text
        custom_config = r"--oem 3 --psm 6"
        text = pytesseract.image_to_string(img, config=custom_config).strip()
        logger.info(f"OCR extracted text: '{text}'")
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from image: {e}")
        logger.debug(traceback.format_exc())
        return ""


# ===== BROWSER AUTOMATION =====
def launch_youtube_and_search():
    """Launch YouTube, perform search using OCR from reference image, extract first video URL."""
    logger.info("Starting YouTube search...")

    # Import dependencies inside function to handle missing gracefully
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        logger.error(f"Missing dependency for browser automation: {e}")
        raise

    with sync_playwright() as p:
        # Launch browser with arguments to avoid detection
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
        )
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        try:
            # Navigate to YouTube
            logger.info("Navigating to YouTube...")
            page.goto("https://www.youtube.com", timeout=30000)

            # Wait for page to load
            page.wait_for_selector("ytd-masthead", timeout=15000)
            logger.info("YouTube page loaded")

            # Extract text from reference image using OCR
            ref_path = get_reference_image_path(REFERENCE_IMAGE_PATH)
            search_query = extract_text_from_image(ref_path)

            # If OCR failed to extract text, use fallback query
            if not search_query:
                logger.warning(
                    f"OCR returned empty text, using fallback query: '{FALLBACK_QUERY}'"
                )
                search_query = FALLBACK_QUERY
            else:
                logger.info(f"Using OCR-extracted query: '{search_query}'")

            # Perform search
            logger.info(f"Entering search query: '{search_query}'")
            search_box = page.locator("input[name='search_query']")
            search_box.fill(search_query)
            page.keyboard.press("Enter")

            # Wait for results to load
            logger.info("Waiting for search results...")
            page.wait_for_selector("ytd-video-renderer", timeout=15000)
            page.wait_for_timeout(2000)  # Additional wait for content

            # Extract first video URL
            logger.info("Extracting first video URL...")
            first_video = page.locator("ytd-video-renderer #video-title").first
            if first_video.count() == 0:
                logger.error("No video results found")
                raise ValueError("Empty search results")

            href = first_video.get_attribute("href")
            if not href:
                logger.error("Failed to get href attribute from first video")
                raise ValueError("Missing href attribute")

            # Ensure absolute URL
            if not href.startswith("http"):
                href = f"https://www.youtube.com{href}"

            logger.info(f"Extracted video URL: {href}")
            return href

        except Exception as e:
            logger.error(f"Error during browser automation: {e}")
            logger.debug(traceback.format_exc())
            raise
        finally:
            browser.close()
            logger.info("Browser closed")


# ===== DESKTOP AUTOMATION =====
def activate_target_window():
    """Locate, focus, and bring the target application to foreground."""
    logger.info(f"Looking for window with title: '{TARGET_WINDOW_TITLE}'")
    try:
        import pygetwindow as gw
    except ImportError:
        logger.error("pygetwindow dependency missing for window management")
        raise

    try:
        windows = gw.getWindowsWithTitle(TARGET_WINDOW_TITLE)
        if not windows:
            logger.error(f"No window found with title: '{TARGET_WINDOW_TITLE}'")
            raise WindowNotFoundError(
                f"No window found with title: '{TARGET_WINDOW_TITLE}'"
            )

        win = windows[0]
        if win.isMinimized:
            win.restore()
            logger.info("Restored minimized window")

        win.activate()
        if win.isMaximized == False:
            win.maximize()
            logger.info("Maximized window")

        logger.info(f"Activated window: {win.title}")
        time.sleep(1.5)  # Allow time for window to gain focus
        return win
    except Exception as e:
        logger.error(f"Error activating target window: {e}")
        logger.debug(traceback.format_exc())
        raise


def automate_download(url):
    """Automate URL input and download trigger in the target application."""
    logger.info("Starting desktop automation for download...")
    try:
        import pyautogui
        import pyperclip
    except ImportError as e:
        logger.error(f"Missing dependency for desktop automation: {e}")
        raise

    try:
        # Focus URL input field (common shortcut: Ctrl+L for address bar)
        logger.info("Focusing URL input field with Ctrl+L...")
        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.5)

        # Clear any existing content (optional)
        pyautogui.press("backspace")
        time.sleep(0.2)

        # Paste URL from clipboard
        logger.info("Copying URL to clipboard and pasting...")
        pyperclip.copy(url)
        pyautogui.hotkey("ctrl", "v")
        logger.info("URL pasted into input field")
        time.sleep(0.5)

        # Trigger download (common: Enter key)
        logger.info("Triggering download with Enter key...")
        pyautogui.press("enter")
        logger.info("Download triggered")
        time.sleep(2)  # Wait for download to initiate

    except Exception as e:
        logger.error(f"Error during desktop automation: {e}")
        logger.debug(traceback.format_exc())
        raise


# ===== CUSTOM EXCEPTIONS =====
class WindowNotFoundError(Exception):
    pass


# ===== MAIN FUNCTION =====
def main():
    """Main automation workflow."""
    logger.info("=" * 60)
    logger.info("Starting YouTube Video Download Automation")
    logger.info("=" * 60)

    # Check dependencies
    deps = check_dependencies()
    missing = [name for name, available in deps.items() if not available]
    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        logger.error(
            "Please install missing packages using: pip install -r requirements.txt"
        )
        logger.error(
            "Also ensure Tesseract OCR is installed: https://github.com/tesseract-ocr/tesseract"
        )
        sys.exit(1)

    try:
        # Step 1: Browser automation to get video URL
        video_url = launch_youtube_and_search()

        # Step 2: Switch to desktop application
        activate_target_window()

        # Step 3: Automate download in the application
        automate_download(video_url)

        logger.info("=" * 60)
        logger.info("Automation completed successfully!")
        logger.info("=" * 60)

    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        sys.exit(1)
    except WindowNotFoundError as e:
        logger.error(f"Window error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Automation failed: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
