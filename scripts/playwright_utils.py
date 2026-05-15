"""
Advanced Playwright utilities for robust browser automation.
Provides retry logic, waits, error handling, and element interactions.
"""

import logging
import time
from typing import Optional, Callable, Any, List, Dict
from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


class WaitTimeoutError(Exception):
    """Custom timeout error for wait operations"""
    pass


def wait_for_condition(
    condition_fn: Callable[[], bool],
    timeout_seconds: float = 10,
    poll_interval: float = 0.5,
    error_message: str = "Condition not met within timeout"
) -> bool:
    """
    Wait for a condition function to return True.
    
    Args:
        condition_fn: Callable that returns True when condition is met
        timeout_seconds: Maximum time to wait in seconds
        poll_interval: How often to check condition in seconds
        error_message: Error message if timeout occurs
    
    Returns:
        True if condition met, raises WaitTimeoutError otherwise
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        try:
            if condition_fn():
                return True
        except Exception as e:
            logger.debug(f"Condition check failed: {e}")
        
        time.sleep(poll_interval)
    
    logger.error(f"Timeout: {error_message} ({timeout_seconds}s)")
    raise WaitTimeoutError(error_message)


def wait_for_element_with_retry(
    page: Page,
    selector: str,
    timeout_ms: int = 10000,
    retries: int = 3,
) -> bool:
    """
    Wait for element to exist with retry logic.
    
    Args:
        page: Playwright page
        selector: CSS selector
        timeout_ms: Timeout per attempt in milliseconds
        retries: Number of retry attempts
    
    Returns:
        True if element found, False otherwise
    """
    for attempt in range(1, retries + 1):
        try:
            logger.debug(f"Waiting for selector '{selector}' (attempt {attempt}/{retries})")
            page.wait_for_selector(selector, timeout=timeout_ms)
            logger.debug(f"Selector found: {selector}")
            return True
        except PlaywrightTimeoutError:
            if attempt < retries:
                logger.debug(f"Selector not found, retrying ({attempt}/{retries})...")
                time.sleep(1)
            else:
                logger.warning(f"Selector not found after {retries} attempts: {selector}")
                return False
        except Exception as e:
            logger.error(f"Error waiting for selector: {e}")
            return False
    
    return False


def safe_fill_input(
    page: Page,
    selector: str,
    text: str,
    clear_first: bool = True,
    timeout_ms: int = 5000,
) -> bool:
    """
    Safely fill an input field with error handling.
    
    Args:
        page: Playwright page
        selector: CSS selector for input
        text: Text to fill
        clear_first: Clear field before filling
        timeout_ms: Timeout in milliseconds
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.debug(f"Filling input '{selector}' with text")
        
        if clear_first:
            page.fill(selector, "")
            page.press(selector, "Control+A")
            page.press(selector, "Backspace")
        
        page.fill(selector, text, timeout=timeout_ms)
        logger.debug(f"Input filled successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error filling input '{selector}': {e}")
        return False


def safe_click(
    page: Page,
    selector: str,
    retries: int = 3,
    timeout_ms: int = 5000,
    wait_after_click_ms: int = 500,
) -> bool:
    """
    Safely click an element with retry logic.
    
    Args:
        page: Playwright page
        selector: CSS selector
        retries: Number of retry attempts
        timeout_ms: Timeout per attempt
        wait_after_click_ms: Wait after click in milliseconds
    
    Returns:
        True if click successful, False otherwise
    """
    for attempt in range(1, retries + 1):
        try:
            logger.debug(f"Clicking '{selector}' (attempt {attempt}/{retries})")
            page.click(selector, timeout=timeout_ms)
            logger.debug(f"Element clicked successfully")
            
            if wait_after_click_ms:
                time.sleep(wait_after_click_ms / 1000)
            
            return True
        
        except PlaywrightTimeoutError:
            logger.warning(f"Click timeout for '{selector}' (attempt {attempt}/{retries})")
            if attempt < retries:
                time.sleep(0.5)
        except Exception as e:
            logger.error(f"Error clicking '{selector}': {e}")
            if attempt < retries:
                time.sleep(0.5)
    
    logger.error(f"Failed to click '{selector}' after {retries} attempts")
    return False


def safe_text_extraction(
    page: Page,
    selector: str,
    default: str = "",
    timeout_ms: int = 5000,
) -> str:
    """
    Safely extract text from element.
    
    Args:
        page: Playwright page
        selector: CSS selector
        default: Default text if extraction fails
        timeout_ms: Timeout in milliseconds
    
    Returns:
        Extracted text or default value
    """
    try:
        logger.debug(f"Extracting text from '{selector}'")
        text = page.text_content(selector, timeout=timeout_ms)
        
        if text:
            logger.debug(f"Text extracted: {text[:50]}...")
            return text.strip()
        else:
            logger.warning(f"No text found in '{selector}'")
            return default
    
    except Exception as e:
        logger.error(f"Error extracting text from '{selector}': {e}")
        return default


def safe_get_attribute(
    page: Page,
    selector: str,
    attribute: str,
    default: Optional[str] = None,
    timeout_ms: int = 5000,
) -> Optional[str]:
    """
    Safely get attribute from element.
    
    Args:
        page: Playwright page
        selector: CSS selector
        attribute: Attribute name
        default: Default value if not found
        timeout_ms: Timeout in milliseconds
    
    Returns:
        Attribute value or default
    """
    try:
        logger.debug(f"Getting attribute '{attribute}' from '{selector}'")
        value = page.get_attribute(selector, attribute, timeout=timeout_ms)
        
        if value:
            logger.debug(f"Attribute value: {value[:50]}...")
            return value
        else:
            logger.debug(f"Attribute '{attribute}' not found in '{selector}'")
            return default
    
    except Exception as e:
        logger.error(f"Error getting attribute '{attribute}' from '{selector}': {e}")
        return default


def wait_for_multiple_elements(
    page: Page,
    selectors: List[str],
    any_match: bool = False,
    timeout_ms: int = 10000,
) -> Dict[str, bool]:
    """
    Wait for multiple elements with flexible matching.
    
    Args:
        page: Playwright page
        selectors: List of CSS selectors
        any_match: If True, return when any selector matches; if False, wait for all
        timeout_ms: Total timeout in milliseconds
    
    Returns:
        Dict of {selector: bool} indicating which were found
    """
    start_time = time.time()
    results = {sel: False for sel in selectors}
    
    while time.time() - start_time < timeout_ms / 1000:
        for selector in selectors:
            if results[selector]:
                continue
            
            try:
                if page.query_selector(selector):
                    results[selector] = True
                    logger.debug(f"Element found: {selector}")
                    
                    if any_match:
                        logger.debug("Any match mode - condition met")
                        return results
            except Exception:
                pass
        
        if not any_match and all(results.values()):
            logger.debug("All elements found")
            return results
        
        time.sleep(0.2)
    
    logger.warning(f"Timeout waiting for elements. Results: {results}")
    return results


def execute_with_retry(
    fn: Callable,
    retries: int = 3,
    wait_between_retries_ms: int = 1000,
    error_message: str = "Operation failed",
) -> Any:
    """
    Execute function with retry logic.
    
    Args:
        fn: Callable to execute
        retries: Number of retry attempts
        wait_between_retries_ms: Wait between retries in milliseconds
        error_message: Error message on final failure
    
    Returns:
        Function result
    
    Raises:
        Exception if all retries fail
    """
    last_error = None
    
    for attempt in range(1, retries + 1):
        try:
            logger.debug(f"Executing function (attempt {attempt}/{retries})")
            result = fn()
            logger.debug(f"Function executed successfully")
            return result
        
        except Exception as e:
            last_error = e
            logger.warning(f"Attempt {attempt}/{retries} failed: {e}")
            
            if attempt < retries:
                time.sleep(wait_between_retries_ms / 1000)
    
    error_msg = f"{error_message}: {last_error}"
    logger.error(error_msg)
    raise Exception(error_msg)


def batch_extract_text(
    page: Page,
    selectors: Dict[str, str],
    timeout_ms: int = 5000,
) -> Dict[str, str]:
    """
    Extract text from multiple elements.
    
    Args:
        page: Playwright page
        selectors: Dict of {name: css_selector}
        timeout_ms: Timeout per extraction
    
    Returns:
        Dict of {name: text_content}
    """
    results = {}
    
    for name, selector in selectors.items():
        text = safe_text_extraction(page, selector, timeout_ms=timeout_ms)
        results[name] = text
        logger.debug(f"Batch extraction - {name}: {text[:30]}...")
    
    return results


def batch_get_attributes(
    page: Page,
    selectors: Dict[str, tuple],
    timeout_ms: int = 5000,
) -> Dict[str, str]:
    """
    Get attributes from multiple elements.
    
    Args:
        page: Playwright page
        selectors: Dict of {name: (css_selector, attribute_name)}
        timeout_ms: Timeout per extraction
    
    Returns:
        Dict of {name: attribute_value}
    """
    results = {}
    
    for name, (selector, attr) in selectors.items():
        value = safe_get_attribute(page, selector, attr, timeout_ms=timeout_ms)
        results[name] = value
        logger.debug(f"Batch attribute extraction - {name}: {value[:30]}...")
    
    return results


if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print("Playwright utilities module loaded successfully")
