import argparse
import sys
import os
import time
import logging

# Ensure parent directory is in path so 'scripts.module' imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize logging first
from scripts.utils_logger import setup_logger

# Then import other modules
from scripts.browser_automation import launch_browser, close_browser, search_youtube_and_capture
from scripts.cv_ocr import extract_queries_from_image
from scripts.parser import extract_first_video_url
from scripts.desktop_automation import send_url_to_app


def main(ref_image: str, headed: bool = False, debug: bool = False, log_file: str = None, limit: int = None):
    """
    Execute end-to-end YouTube video extraction and download workflow.
    
    Args:
        ref_image: Path to reference image for visual search
        headed: Run browser in headed (non-headless) mode for debugging
        debug: Enable debug-level logging
        log_file: Optional log file path
        
    Returns:
        Exit code (0=success, 1=no video found, 3=error)
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logger = setup_logger("yt_downloader", level=log_level, log_file=log_file)
    
    logger.info("="*60)
    logger.info("YouTube Automation Workflow Started")
    logger.info(f"Reference image: {ref_image}")
    logger.info(f"Browser mode: {'HEADED (debugging)' if headed else 'HEADLESS'}")
    logger.info("="*60)
    
    p = None
    browser = None
    try:
        # Step 1: Extract search queries from the image text
        logger.info("[1/4] Extracting video names from image OCR...")
        queries = extract_queries_from_image(ref_image)
        if not queries:
            logger.error("Could not find any video titles inside the provided image.")
            return 3
            
        logger.info(f"Found {len(queries)} potential video titles to search:")
        for q in queries:
            logger.info(f" - {q}")

        # Step 2: Ensure output folder exists
        output_dir = r"C:\Users\mohit\Desktop\YT video downloa\New folder"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "yt copy links.txt")

        # Step 3: Launch browser
        logger.info("[2/4] Initializing browser automation...")
        try:
            p, browser = launch_browser(headless=not headed, retries=2)
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            return 3
        
        # Step 4: Search and collect links
        logger.info("[3/4] Searching YouTube for each video title...")
        video_links = []
        
        if limit:
            queries = queries[:limit]
            logger.info(f"Limiting search to first {limit} queries for demo/testing.")

        for idx, query in enumerate(queries, 1):
            logger.info(f"Processing ({idx}/{len(queries)}): '{query}'")
            try:
                screenshot_results, html = search_youtube_and_capture(browser, query)
                video_url = extract_first_video_url(html)
                if video_url:
                    logger.info(f"  -> Found URL: {video_url}")
                    video_links.append(video_url)
                else:
                    logger.warning(f"  -> No video URL found for '{query}'")
            except Exception as e:
                logger.error(f"  -> Failed to search YouTube for '{query}': {e}")
        
        # Step 5: Save to text file
        logger.info("[4/4] Saving scraped links to text file...")
        if video_links:
            with open(output_file, "w", encoding="utf-8") as f:
                for link in video_links:
                    f.write(f"{link}\n")
            logger.info(f"✓ Successfully saved {len(video_links)} links to:")
            logger.info(f"  {output_file}")
            
            # Step 6: Send the first found URL to the desktop app (if requested or as part of lifecycle)
            if video_links:
                first_url = video_links[0]
                logger.info(f"[Lifecycle] Sending first URL to desktop app: {first_url}")
                if send_url_to_app(first_url):
                    logger.info("✓ URL sent to application successfully")
                else:
                    logger.error("Failed to send URL to application. Ensure it's open.")

            logger.info("="*60)
            logger.info("Workflow completed successfully!")
            logger.info("="*60)
            return 0
        else:
            logger.error("No video links were successfully extracted.")
            return 1
        
    except Exception as e:
        logger.exception(f"Unexpected error during workflow: {e}")
        return 3
    finally:
        if browser or p:
            logger.info("Cleaning up browser resources...")
            try:
                close_browser(p, browser)
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="YouTube Video Extraction and Desktop Download Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/main.py --ref C:\\path\\to\\search_cue.png
  python scripts/main.py --ref C:\\path\\to\\search_cue.png --headed --debug
  python scripts/main.py --ref C:\\path\\to\\search_cue.png --log automation.log
        """
    )
    parser.add_argument("--ref", required=True, help="Path to reference image for visual search")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode (for debugging)")
    parser.add_argument("--debug", action="store_true", help="Enable debug-level logging")
    parser.add_argument("--log", dest="log_file", help="Log file path (optional; logs to console by default)")
    parser.add_argument("--limit", type=int, help="Limit the number of videos to search (for demo/testing)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    exit_code = main(
        ref_image=args.ref,
        headed=args.headed,
        debug=args.debug,
        log_file=args.log_file,
        limit=args.limit
    )
    sys.exit(exit_code)
