import logging
import sys
import time
import traceback
from pathlib import Path
import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
from playwright.sync_api import sync_playwright
import pygetwindow as gw
import pyautogui
import pyperclip

# ===== CONFIGURATION =====
# User-provided values
REFERENCE_IMAGE_PATH = r"C:\Users\mohit\Pictures\MEmu Photo\IMG_20260515_231534_845.jpg"
FALLBACK_QUERY = "YouTube video"  # Default fallback query
TARGET_WINDOW_TITLE = "Video Downloader Standard"  # Default window title

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


def check_tesseract():
    """Check if Tesseract OCR is available."""
    try:
        # Try to get Tesseract version
        version = pytesseract.get_tesseract_version()
        logger.info(f"Tesseract OCR version: {version}")
        return True
    except Exception as e:
        logger.warning(f"Tesseract OCR not available: {e}")
        logger.warning(
            "OCR functionality will be disabled; will use fallback query only."
        )
        return False


# ===== BROWSER AUTOMATION =====
def launch_youtube_and_search():
    """Launch YouTube, perform visual search, extract first video URL."""
    logger.info("Starting YouTube search...")
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

            # Take screenshot
            logger.info("Taking screenshot for visual search...")
            screenshot = page.screenshot(full_page=False)
            img_np = np.array(Image.open(io.BytesIO(screenshot)))

            # Load reference image
            ref_path = get_reference_image_path(REFERENCE_IMAGE_PATH)
            logger.info(f"Loading reference image: {ref_path}")
            ref_img = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE)
            if ref_img is None:
                logger.error(f"Reference image not found or unreadable: {ref_path}")
                raise FileNotFoundError(f"Reference image missing: {ref_path}")

            # Convert screenshot to grayscale
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

            # Template matching
            logger.info("Performing template matching...")
            res = cv2.matchTemplate(gray, ref_img, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            threshold = 0.8

            # Check if Tesseract is available for OCR
            tesseract_available = check_tesseract()

            if max_val >= threshold:
                logger.info(f"Reference image matched with confidence {max_val:.2f}")
                # Click at the matched location
                w, h = ref_img.shape[::-1]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                page.mouse.click(center_x, center_y)
                logger.info(f"Clicked at coordinates ({center_x}, {center_y})")

                # Extract text via OCR from the matched region if Tesseract is available
                if tesseract_available:
                    roi = gray[max_loc[1] : max_loc[1] + h, max_loc[0] : max_loc[0] + w]
                    custom_config = r"--oem 3 --psm 6"
                    ocr_text = pytesseract.image_to_string(
                        roi, config=custom_config
                    ).strip()
                    if ocr_text:
                        search_query = ocr_text
                        logger.info(f"OCR extracted query: '{search_query}'")
                    else:
                        search_query = FALLBACK_QUERY
                        logger.info(
                            f"OCR empty, using fallback query: '{search_query}'"
                        )
                else:
                    search_query = FALLBACK_QUERY
                    logger.info(
                        f"Tesseract not available, using fallback query: '{search_query}'"
                    )
            else:
                logger.warning(
                    f"Reference image not found (max confidence: {max_val:.2f}), using fallback query"
                )
                search_query = FALLBACK_QUERY

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
