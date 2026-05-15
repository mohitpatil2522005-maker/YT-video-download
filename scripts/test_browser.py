#!/usr/bin/env python3
"""
Test utility to validate Playwright browser automation setup.
Run this script to verify all browser components are working correctly.

Usage:
    python scripts/test_browser.py
    python scripts/test_browser.py --headed  (to see browser in action)
    python scripts/test_browser.py --debug   (for detailed logs)
"""

import argparse
import sys
import logging
import tempfile
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils_logger import setup_logger
from scripts.browser_automation import launch_browser, close_browser, get_page_screenshot_and_html


def test_browser_launch(logger, headless=True):
    """Test 1: Browser launch and close."""
    logger.info("=" * 60)
    logger.info("TEST 1: Browser Launch and Close")
    logger.info("=" * 60)
    try:
        logger.info(f"Launching browser (headless={headless})...")
        p, browser = launch_browser(headless=headless, retries=2)
        logger.info("✓ Browser launched successfully")
        
        close_browser(p, browser)
        logger.info("✓ Browser closed successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Test failed: {e}")
        return False


def test_page_navigation(logger, headless=True):
    """Test 2: Page navigation and screenshot."""
    logger.info("=" * 60)
    logger.info("TEST 2: Page Navigation and Screenshot")
    logger.info("=" * 60)
    p = None
    browser = None
    try:
        logger.info("Launching browser...")
        p, browser = launch_browser(headless=headless, retries=2)
        
        # Test with a simple, lightweight page
        test_url = "https://www.example.com"
        logger.info(f"Navigating to {test_url}...")
        
        try:
            png, html = get_page_screenshot_and_html(
                browser, 
                test_url, 
                timeout=15000,
                wait_for_load_state="domcontentloaded"
            )
            logger.info(f"✓ Page loaded successfully")
            logger.info(f"  - Screenshot: {len(png)} bytes")
            logger.info(f"  - HTML: {len(html)} chars")
            
            # Save screenshot to temp file for verification
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(png)
                logger.info(f"  - Screenshot saved to: {tmp.name}")
            
            # Quick HTML validation
            if "example" in html.lower():
                logger.info("✓ HTML content appears valid")
            else:
                logger.warning("⚠ HTML content unexpected, but page loaded")
            
            return True
        except Exception as e:
            logger.error(f"✗ Navigation/capture failed: {e}")
            return False
    finally:
        if browser or p:
            try:
                close_browser(p, browser)
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")


def test_youtube_connection(logger, headless=True):
    """Test 3: YouTube connectivity (does not execute search)."""
    logger.info("=" * 60)
    logger.info("TEST 3: YouTube Connectivity")
    logger.info("=" * 60)
    p = None
    browser = None
    try:
        logger.info("Launching browser...")
        p, browser = launch_browser(headless=headless, retries=2)
        
        youtube_url = "https://www.youtube.com"
        logger.info(f"Navigating to {youtube_url}...")
        
        try:
            png, html = get_page_screenshot_and_html(
                browser,
                youtube_url,
                timeout=20000,
                wait_for_load_state="domcontentloaded"
            )
            logger.info(f"✓ YouTube loaded successfully")
            logger.info(f"  - Screenshot: {len(png)} bytes")
            logger.info(f"  - HTML: {len(html)} chars")
            
            # Basic validation
            if "youtube" in html.lower() or "search" in html.lower():
                logger.info("✓ YouTube HTML content appears valid")
            else:
                logger.warning("⚠ YouTube content unexpected, but page loaded")
            
            return True
        except Exception as e:
            logger.error(f"✗ YouTube connection failed: {e}")
            logger.info("  Note: This could be due to network issues or YouTube blocking automation")
            return False
    finally:
        if browser or p:
            try:
                close_browser(p, browser)
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")


def run_all_tests(headless=True, debug=False):
    """Run all tests and report results."""
    log_level = logging.DEBUG if debug else logging.INFO
    logger = setup_logger("browser_test", level=log_level)
    
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║ Playwright Browser Automation Test Suite")
    logger.info("║ Mode: %s", "HEADED (visible)" if not headless else "HEADLESS")
    logger.info("╚" + "=" * 58 + "╝")
    
    tests = [
        ("Browser Launch/Close", lambda: test_browser_launch(logger, headless)),
        ("Page Navigation", lambda: test_page_navigation(logger, headless)),
        ("YouTube Connectivity", lambda: test_youtube_connection(logger, headless)),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            logger.warning("Test interrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {name}")
    
    logger.info("=" * 60)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test Playwright browser automation setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/test_browser.py
  python scripts/test_browser.py --headed
  python scripts/test_browser.py --debug
        """
    )
    parser.add_argument("--headed", action="store_true", help="Run tests in headed mode (browser visible)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    exit_code = run_all_tests(headless=not args.headed, debug=args.debug)
    sys.exit(exit_code)
