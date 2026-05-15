"""
Enhanced Playwright Browser Automation Module
Provides robust browser control, navigation, and element interaction utilities.
"""

import logging
import sys
import time
import traceback
from typing import Optional, Dict, List, Any
from pathlib import Path

from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
from playwright.sync_api import expect

# ===== LOGGING SETUP =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("playwright.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ===== CUSTOM EXCEPTIONS =====
class PlaywrightAutomationError(Exception):
    """Base exception for Playwright automation errors"""
    pass


class BrowserLaunchError(PlaywrightAutomationError):
    """Failed to launch browser"""
    pass


class NavigationError(PlaywrightAutomationError):
    """Failed to navigate to URL"""
    pass


class ElementNotFoundError(PlaywrightAutomationError):
    """Element not found on page"""
    pass


# ===== BROWSER CONFIGURATION =====
class BrowserConfig:
    """Configuration for browser launch and behavior"""
    
    def __init__(
        self,
        headless: bool = True,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        timeout: int = 30000,
        user_agent: Optional[str] = None,
        disable_detection: bool = True,
    ):
        self.headless = headless
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.timeout = timeout
        self.user_agent = user_agent
        self.disable_detection = disable_detection
    
    def get_launch_args(self) -> List[str]:
        """Get browser launch arguments"""
        args = []
        if self.disable_detection:
            args.extend([
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ])
        return args
    
    def get_context_options(self) -> Dict[str, Any]:
        """Get browser context options"""
        options = {
            "viewport": {
                "width": self.viewport_width,
                "height": self.viewport_height,
            },
        }
        if self.user_agent:
            options["user_agent"] = self.user_agent
        return options


# ===== BROWSER AUTOMATION CLASS =====
class PlaywrightAutomation:
    """Main Playwright automation handler"""
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        self.config = config or BrowserConfig()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        logger.info("PlaywrightAutomation initialized")
    
    def launch(self) -> Browser:
        """Launch browser instance"""
        try:
            logger.info("Launching browser...")
            self.playwright = sync_playwright().start()
            
            launch_args = {
                "headless": self.config.headless,
                "args": self.config.get_launch_args(),
            }
            
            self.browser = self.playwright.chromium.launch(**launch_args)
            logger.info("Browser launched successfully")
            return self.browser
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            logger.debug(traceback.format_exc())
            raise BrowserLaunchError(f"Browser launch failed: {e}")
    
    def create_page(self) -> Page:
        """Create a new browser page/tab"""
        try:
            if not self.browser:
                self.launch()
            
            self.context = self.browser.new_context(**self.config.get_context_options())
            self.page = self.context.new_page()
            self.page.set_default_timeout(self.config.timeout)
            logger.info("New page created")
            return self.page
        except Exception as e:
            logger.error(f"Failed to create page: {e}")
            logger.debug(traceback.format_exc())
            raise PlaywrightAutomationError(f"Page creation failed: {e}")
    
    def navigate(self, url: str, wait_until: str = "networkidle") -> Page:
        """Navigate to URL"""
        try:
            if not self.page:
                self.create_page()
            
            logger.info(f"Navigating to {url}...")
            self.page.goto(url, wait_until=wait_until, timeout=self.config.timeout)
            logger.info(f"Navigation successful: {url}")
            return self.page
        except Exception as e:
            logger.error(f"Navigation failed to {url}: {e}")
            logger.debug(traceback.format_exc())
            raise NavigationError(f"Failed to navigate to {url}: {e}")
    
    def wait_for_element(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Wait for element to appear"""
        try:
            timeout_ms = timeout or self.config.timeout
            logger.info(f"Waiting for element: {selector}")
            self.page.wait_for_selector(selector, timeout=timeout_ms)
            logger.info(f"Element found: {selector}")
            return True
        except Exception as e:
            logger.warning(f"Element not found within timeout: {selector}")
            return False
    
    def fill_input(self, selector: str, text: str) -> None:
        """Fill input field with text"""
        try:
            logger.info(f"Filling input '{selector}' with text")
            self.page.fill(selector, text)
            logger.debug(f"Input filled successfully")
        except Exception as e:
            logger.error(f"Failed to fill input '{selector}': {e}")
            raise ElementNotFoundError(f"Failed to fill input: {e}")
    
    def click(self, selector: str) -> None:
        """Click on element"""
        try:
            logger.info(f"Clicking element: {selector}")
            self.page.click(selector)
            logger.debug(f"Element clicked")
        except Exception as e:
            logger.error(f"Failed to click element '{selector}': {e}")
            raise ElementNotFoundError(f"Failed to click element: {e}")
    
    def get_text(self, selector: str) -> str:
        """Extract text from element"""
        try:
            logger.info(f"Extracting text from: {selector}")
            text = self.page.text_content(selector)
            logger.debug(f"Text extracted: {text}")
            return text or ""
        except Exception as e:
            logger.error(f"Failed to get text from '{selector}': {e}")
            raise ElementNotFoundError(f"Failed to get text: {e}")
    
    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get attribute value from element"""
        try:
            logger.info(f"Getting attribute '{attribute}' from: {selector}")
            value = self.page.get_attribute(selector, attribute)
            logger.debug(f"Attribute value: {value}")
            return value
        except Exception as e:
            logger.error(f"Failed to get attribute '{attribute}' from '{selector}': {e}")
            raise ElementNotFoundError(f"Failed to get attribute: {e}")
    
    def take_screenshot(self, path: str, full_page: bool = False) -> bytes:
        """Take and save screenshot"""
        try:
            logger.info(f"Taking screenshot: {path}")
            screenshot = self.page.screenshot(path=path, full_page=full_page)
            logger.info(f"Screenshot saved to {path}")
            return screenshot
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            raise PlaywrightAutomationError(f"Screenshot failed: {e}")
    
    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript on page"""
        try:
            logger.info("Executing JavaScript")
            result = self.page.evaluate(script, args)
            logger.debug(f"Script result: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to execute script: {e}")
            raise PlaywrightAutomationError(f"Script execution failed: {e}")
    
    def press_key(self, key: str) -> None:
        """Press keyboard key"""
        try:
            logger.info(f"Pressing key: {key}")
            self.page.press("body", key)
        except Exception as e:
            logger.error(f"Failed to press key '{key}': {e}")
            raise PlaywrightAutomationError(f"Key press failed: {e}")
    
    def type_text(self, selector: str, text: str, delay: int = 50) -> None:
        """Type text character by character"""
        try:
            logger.info(f"Typing text into: {selector}")
            self.page.locator(selector).type(text, delay=delay)
            logger.debug("Text typed successfully")
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            raise ElementNotFoundError(f"Failed to type text: {e}")
    
    def wait_for_navigation(self, timeout: Optional[int] = None) -> None:
        """Wait for page navigation to complete"""
        try:
            timeout_ms = timeout or self.config.timeout
            logger.info("Waiting for navigation...")
            self.page.wait_for_load_state("networkidle", timeout=timeout_ms)
            logger.info("Navigation completed")
        except Exception as e:
            logger.warning(f"Navigation wait timeout: {e}")
    
    def close(self) -> None:
        """Close browser and cleanup"""
        try:
            logger.info("Closing browser...")
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
            logger.debug(traceback.format_exc())
    
    def __enter__(self):
        """Context manager entry"""
        self.launch()
        self.create_page()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False


# ===== SPECIALIZED AUTOMATION CLASSES =====
class YouTubeAutomation(PlaywrightAutomation):
    """YouTube-specific automation"""
    
    YOUTUBE_URL = "https://www.youtube.com"
    SEARCH_BOX_SELECTOR = "input[name='search_query']"
    VIDEO_RENDERER_SELECTOR = "ytd-video-renderer"
    MASTHEAD_SELECTOR = "ytd-masthead"
    
    def navigate_to_youtube(self) -> Page:
        """Navigate to YouTube"""
        return self.navigate(self.YOUTUBE_URL, wait_until="networkidle")
    
    def wait_for_page_load(self) -> bool:
        """Wait for YouTube page to fully load"""
        return self.wait_for_element(self.MASTHEAD_SELECTOR, timeout=15000)
    
    def search(self, query: str) -> None:
        """Perform YouTube search"""
        try:
            logger.info(f"Searching for: {query}")
            self.fill_input(self.SEARCH_BOX_SELECTOR, query)
            self.press_key("Enter")
            logger.info("Search query entered")
            time.sleep(2)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise PlaywrightAutomationError(f"Search failed: {e}")
    
    def get_first_video_url(self) -> str:
        """Extract first video URL from search results"""
        try:
            logger.info("Extracting first video URL...")
            self.wait_for_element(self.VIDEO_RENDERER_SELECTOR, timeout=15000)
            
            url = self.page.locator(f"{self.VIDEO_RENDERER_SELECTOR} #video-title").first.get_attribute("href")
            if not url:
                raise ElementNotFoundError("Failed to get video URL")
            
            if not url.startswith("http"):
                url = f"{self.YOUTUBE_URL}{url}"
            
            logger.info(f"First video URL: {url}")
            return url
        except Exception as e:
            logger.error(f"Failed to get video URL: {e}")
            raise ElementNotFoundError(f"Failed to get video URL: {e}")
    
    def get_video_title(self) -> str:
        """Extract first video title"""
        try:
            logger.info("Extracting first video title...")
            title = self.get_text(f"{self.VIDEO_RENDERER_SELECTOR} #video-title")
            logger.info(f"Video title: {title}")
            return title
        except Exception as e:
            logger.error(f"Failed to get video title: {e}")
            raise ElementNotFoundError(f"Failed to get video title: {e}")
    
    def search_and_get_first_video(self, query: str) -> Dict[str, str]:
        """Perform search and extract first video info"""
        try:
            self.navigate_to_youtube()
            self.wait_for_page_load()
            self.search(query)
            
            url = self.get_first_video_url()
            title = self.get_video_title()
            
            return {
                "url": url,
                "title": title,
                "query": query,
            }
        except Exception as e:
            logger.error(f"Search and extract failed: {e}")
            raise


# ===== UTILITY FUNCTIONS =====
def create_automation(
    headless: bool = True,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
    automation_class: type = PlaywrightAutomation,
) -> PlaywrightAutomation:
    """Factory function to create automation instance"""
    config = BrowserConfig(
        headless=headless,
        viewport_width=viewport_width,
        viewport_height=viewport_height,
    )
    return automation_class(config)


if __name__ == "__main__":
    # Example usage
    logger.info("Starting Playwright automation example...")
    
    try:
        # Example: YouTube automation
        with YouTubeAutomation() as yt:
            yt.launch()
            yt.create_page()
            result = yt.search_and_get_first_video("Python programming")
            
            logger.info("Search Result:")
            logger.info(f"  Title: {result['title']}")
            logger.info(f"  URL: {result['url']}")
            logger.info(f"  Query: {result['query']}")
    
    except PlaywrightAutomationError as e:
        logger.error(f"Automation error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)
