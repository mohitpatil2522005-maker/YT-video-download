from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Browser, Page
from typing import Tuple, Optional
import time
import logging


logger = logging.getLogger(__name__)


def launch_browser(
    headless: bool = True,
    user_agent: Optional[str] = None,
    timeout: int = 30000,
    retries: int = 2
) -> Tuple:
    """
    Launch a Playwright Chrome browser with error handling and retry logic.
    
    Args:
        headless: Run browser in headless mode (default True)
        user_agent: Optional custom user agent string
        timeout: Navigation timeout in ms
        retries: Number of retry attempts on failure
        
    Returns:
        Tuple of (playwright_context, browser_instance)
    """
    attempt = 0
    while attempt <= retries:
        try:
            logger.info(f"Launching Playwright browser (attempt {attempt + 1}/{retries + 1}, headless={headless})")
            p = sync_playwright().start()
            
            # Try Chrome channel first, fallback to chromium
            try:
                logger.debug("Attempting to launch Chrome channel...")
                browser = p.chromium.launch(headless=headless, channel="chrome")
                logger.info("Successfully launched Chrome channel")
            except Exception as e:
                logger.debug(f"Chrome channel unavailable ({e}), falling back to Chromium")
                browser = p.chromium.launch(headless=headless)
                logger.info("Successfully launched Chromium")
            
            return p, browser
        except Exception as e:
            attempt += 1
            if attempt > retries:
                logger.error(f"Failed to launch browser after {retries + 1} attempts: {e}")
                raise
            logger.warning(f"Browser launch failed (attempt {attempt}), retrying in 2s...")
            time.sleep(2)


def close_browser(p, browser):
    """Safely close browser and playwright context."""
    try:
        if browser:
            logger.debug("Closing browser...")
            browser.close()
            logger.info("Browser closed successfully")
    except Exception as e:
        logger.warning(f"Error closing browser: {e}")
    finally:
        try:
            if p:
                logger.debug("Stopping Playwright...")
                p.stop()
                logger.info("Playwright stopped")
        except Exception as e:
            logger.warning(f"Error stopping Playwright: {e}")


def get_page_screenshot_and_html(
    browser,
    url: str,
    timeout: int = 15000,
    wait_for_load_state: str = "networkidle",
    full_page: bool = True
) -> Tuple[bytes, str]:
    """
    Navigate to URL, capture screenshot and HTML content.
    
    Args:
        browser: Playwright browser instance
        url: URL to navigate to
        timeout: Navigation timeout in ms
        wait_for_load_state: Wait state ('load', 'domcontentloaded', 'networkidle')
        full_page: If True, capture full page; else viewport only
        
    Returns:
        Tuple of (png_bytes, html_content)
        
    Raises:
        PlaywrightTimeoutError: On timeout
        Exception: On other navigation/capture errors
    """
    page = None
    try:
        logger.info(f"Navigating to {url}")
        page = browser.new_page()
        
        # Set reasonable defaults
        page.set_default_timeout(timeout)
        page.set_default_navigation_timeout(timeout)
        
        # Navigate and wait
        logger.debug(f"Goto URL with timeout {timeout}ms")
        page.goto(url, timeout=timeout, wait_until="domcontentloaded")
        
        # Wait for additional load state
        logger.debug(f"Waiting for {wait_for_load_state} state...")
        try:
            page.wait_for_load_state(wait_for_load_state, timeout=timeout)
        except PlaywrightTimeoutError:
            logger.warning(f"Timeout waiting for {wait_for_load_state}, continuing anyway")
        
        # Give page a moment to settle
        time.sleep(0.5)
        
        # Capture screenshot and content
        logger.debug(f"Capturing screenshot (full_page={full_page})...")
        png = page.screenshot(full_page=full_page)
        logger.debug(f"Screenshot captured ({len(png)} bytes)")
        
        logger.debug("Extracting HTML content...")
        html = page.content()
        logger.debug(f"HTML extracted ({len(html)} chars)")
        
        logger.info(f"Successfully loaded {url}")
        return png, html
        
    except PlaywrightTimeoutError as e:
        logger.error(f"Timeout error navigating to {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading {url}: {e}")
        raise
    finally:
        if page:
            try:
                page.close()
            except Exception as e:
                logger.debug(f"Error closing page: {e}")


def search_youtube_and_capture(browser, query: str, timeout: int = 60000) -> Tuple[bytes, str]:
    """
    Execute YouTube search and capture results page.
    
    Args:
        browser: Playwright browser instance
        query: Search query string
        timeout: Navigation timeout in ms
        
    Returns:
        Tuple of (screenshot_bytes, html_content)
    """
    if not query:
        search_url = "https://www.youtube.com"
        logger.info("Empty query, navigating to YouTube homepage")
    else:
        # URL-encode query
        import urllib.parse
        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        logger.info(f"Searching YouTube for: {query}")
    
    logger.debug(f"Search URL: {search_url}")
    
    return get_page_screenshot_and_html(browser, search_url, timeout=timeout)
