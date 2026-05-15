# Playwright Browser Automation Implementation

This document describes the enhanced Playwright automation framework for YouTube video extraction and desktop application integration.

## Overview

The project uses **Playwright** for robust, reliable browser automation with the following capabilities:

- **Headless & Headed Modes**: Run in background or show browser window for debugging
- **Anti-Detection Features**: Bypass automation detection with special launch arguments
- **Retry Logic**: Built-in retry mechanisms for resilient automation
- **Error Handling**: Comprehensive error handling and logging throughout
- **Visual Search**: Template matching (OpenCV) + OCR (Tesseract) for intelligent search query extraction
- **Desktop Integration**: Automated URL input to desktop video downloader application

## Architecture

### Core Modules

#### 1. `browser_automation.py`
**Core browser control and navigation functions**

```python
# Launch browser with anti-detection features
p, browser = launch_browser(headless=True, retries=2)

# Navigate to URL and capture content
screenshot_bytes, html = get_page_screenshot_and_html(
    browser,
    "https://www.youtube.com",
    timeout=15000,
    wait_for_load_state="networkidle"
)

# YouTube-specific search
screenshot, html = search_youtube_and_capture(browser, "python tutorial")

# Close resources
close_browser(p, browser)
```

**Key Features:**
- Chrome/Chromium automatic fallback
- Configurable viewport sizes
- Network state monitoring
- Screenshot and HTML capture in one call
- Proper resource cleanup

#### 2. `playwright_utils.py`
**Advanced utilities for robust element interaction**

```python
from scripts.playwright_utils import (
    wait_for_element_with_retry,
    safe_fill_input,
    safe_click,
    safe_text_extraction,
    batch_extract_text,
    execute_with_retry,
)

# Wait for element with retries
found = wait_for_element_with_retry(page, "button.submit", retries=3)

# Fill input safely
safe_fill_input(page, "input#search", "search query", clear_first=True)

# Click with retry logic
success = safe_click(page, "button.search", retries=3, wait_after_click_ms=500)

# Extract text safely
text = safe_text_extraction(page, "h1.title", default="No title")

# Batch operations
data = batch_extract_text(page, {
    "title": "h1",
    "description": "p.desc",
    "author": "span.author"
})

# Execute with retry
result = execute_with_retry(
    lambda: some_function(),
    retries=3,
    wait_between_retries_ms=1000
)
```

**Key Features:**
- Timeout handling with fallback waits
- Automatic element clearing before input
- Retry logic for flaky operations
- Batch text and attribute extraction
- Generic retry wrapper for any callable

#### 3. `cv_ocr.py`
**Computer vision and OCR utilities**

```python
from scripts.cv_ocr import (
    template_match,
    ocr_extract_text,
    derive_search_query_from_reference
)

# Template matching (find visual element)
bbox = template_match(screenshot_bytes, "reference_image.png", threshold=0.7)

# OCR text extraction from region
text = ocr_extract_text(screenshot_bytes, region=(x, y, width, height))

# Full pipeline: find reference image and extract text
query = derive_search_query_from_reference(screenshot_bytes, "search_cue.png")
```

**Key Features:**
- Normalized correlation matching
- Expandable region for OCR context
- Fallback filename-based query derivation
- Grayscale and color image support

#### 4. `parser.py`
**HTML parsing and data extraction**

```python
from scripts.parser import extract_first_video_url

# Extract first video URL from YouTube search results
video_url = extract_first_video_url(html)
# Returns: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Key Features:**
- BeautifulSoup with lxml parser
- HTML5 fallback parsing
- Regex-based video URL extraction
- Absolute URL normalization

#### 5. `desktop_automation.py`
**Desktop application interaction**

```python
from scripts.desktop_automation import (
    find_window_by_title_regex,
    focus_window,
    paste_url_and_trigger,
    send_url_to_app
)

# Send URL to desktop app
success = send_url_to_app(
    "https://www.youtube.com/watch?v=...",
    app_title_regex=r"video\s*downloader",
    timeout=10
)
```

**Key Features:**
- Regex window title matching
- Automatic window restoration/maximization
- Clipboard-based URL transmission
- Keyboard trigger input

### Workflow Pipeline

```
1. Launch Browser (Playwright)
   ↓
2. Navigate to YouTube Homepage
   ↓
3. Capture Screenshot for Visual Analysis
   ↓
4. Template Matching (OpenCV)
   ↓
5. OCR Text Extraction (Tesseract)
   ↓
6. Derive Search Query
   ↓
7. Search YouTube
   ↓
8. Parse HTML for Video URL
   ↓
9. Close Browser
   ↓
10. Activate Desktop Application
   ↓
11. Send URL and Trigger Download
```

## Usage Examples

### Basic Usage

```bash
# Simple search with reference image
python scripts/main.py --ref C:\path\to\reference.png

# Debug mode with browser visible
python scripts/main.py --ref C:\path\to\reference.png --headed --debug

# With logging to file
python scripts/main.py --ref C:\path\to\reference.png --log automation.log
```

### Advanced Usage in Code

```python
from scripts.browser_automation import launch_browser, close_browser
from scripts.playwright_utils import safe_click, safe_text_extraction

p, browser = launch_browser(headless=True, retries=2)
page = browser.new_page()

try:
    page.goto("https://www.youtube.com", timeout=15000)
    
    # Wait for and click element
    safe_click(page, "input[name='search_query']", retries=3)
    page.fill("input[name='search_query']", "python tutorial")
    page.press("input[name='search_query']", "Enter")
    
    # Extract results
    page.wait_for_selector("ytd-video-renderer", timeout=10000)
    titles = batch_extract_text(page, {
        f"video_{i}": f"ytd-video-renderer:nth-child({i}) h3"
        for i in range(1, 6)
    })
    
    print(titles)
    
finally:
    page.close()
    close_browser(p, browser)
```

## Configuration

### Browser Launch Options

```python
launch_browser(
    headless=True,           # Run in background
    channel="chrome",        # Use Chrome browser (falls back to Chromium)
    retries=2,              # Retry count on failure
    # Additional kwargs:
    proxy={"server": "..."}  # Use proxy
    timeout=30000           # Default timeout in ms
)
```

### Element Interaction Options

All safe_* functions support:
- **timeout_ms**: Operation timeout
- **retries**: Retry attempts for flaky elements
- **default**: Fallback value if operation fails

## Error Handling

The framework uses custom exceptions for better error diagnostics:

```python
from scripts.playwright_utils import WaitTimeoutError

try:
    wait_for_element_with_retry(page, "nonexistent", timeout_ms=5000)
except WaitTimeoutError as e:
    print(f"Element not found: {e}")
```

## Logging

Configure logging level via command-line:

```bash
# Debug mode - verbose output
python scripts/main.py --ref image.png --debug

# Standard info level
python scripts/main.py --ref image.png

# Log to file
python scripts/main.py --ref image.png --log output.log
```

Log levels:
- **DEBUG**: Detailed operation steps, selector lookups
- **INFO**: Major workflow steps, results
- **WARNING**: Retries, non-fatal issues
- **ERROR**: Failed operations, exceptions

## Performance Optimization

### Best Practices

1. **Use Headless Mode**: ~3-5x faster than headed mode
2. **Set Reasonable Timeouts**: 15-30 seconds for most operations
3. **Minimize Waits**: Use `networkidle` or `domcontentloaded` appropriately
4. **Batch Operations**: Extract multiple elements in one pass
5. **Cache Selectors**: Reuse selector strings

### Example

```python
# ✗ Bad: Multiple sequential waits
page.wait_for_selector("h1", timeout=5000)
page.wait_for_selector("p", timeout=5000)
page.wait_for_selector("button", timeout=5000)

# ✓ Good: Batch wait
from scripts.playwright_utils import wait_for_multiple_elements
results = wait_for_multiple_elements(
    page,
    ["h1", "p", "button"],
    timeout_ms=5000,
    any_match=False  # Wait for all
)
```

## Troubleshooting

### Browser Won't Launch

```bash
# Try with debug mode to see detailed errors
python scripts/main.py --ref image.png --debug --headed

# Check if Chrome is installed or use Chromium
# The script automatically falls back to Chromium
```

### Elements Not Found

```bash
# Use headed mode to visually inspect
python scripts/main.py --ref image.png --headed

# Increase timeout
# Modify scripts/browser_automation.py timeout values
```

### Slow Performance

```bash
# Ensure headless mode is enabled (default)
python scripts/main.py --ref image.png  # ✓ headless

python scripts/main.py --ref image.png --headed  # ✗ slower
```

### OCR Not Working

Ensure Tesseract is installed:

```bash
# Windows: Install from https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH or set PYTESSERACT path:

import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Dependencies

```
playwright>=1.40.0       # Browser automation
opencv-python           # Template matching
pytesseract            # OCR (requires Tesseract)
beautifulsoup4         # HTML parsing
lxml                   # XML/HTML parsing backend
pygetwindow            # Windows manipulation
pyautogui              # Keyboard/mouse control
pyperclip              # Clipboard access
Pillow                 # Image processing
numpy                  # Numerical operations
```

## Installation

```bash
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium

# Install Tesseract OCR (Windows)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use: choco install tesseract (if using Chocolatey)
```

## API Reference

See individual module docstrings for comprehensive function documentation:

```python
# View detailed docs
python -m pydoc scripts.browser_automation
python -m pydoc scripts.playwright_utils
python -m pydoc scripts.cv_ocr
python -m pydoc scripts.desktop_automation
```

## Future Enhancements

- [ ] Parallel browser instances for batch operations
- [ ] Video download progress tracking
- [ ] Support for additional video platforms (Vimeo, etc.)
- [ ] Database logging of automation runs
- [ ] Web UI for configuration and monitoring
- [ ] Scheduled automation runs
- [ ] Error recovery and fallback strategies

## Performance Metrics

Typical execution times:

- Browser launch: 2-4 seconds
- YouTube navigation: 3-5 seconds
- Screenshot capture: <1 second
- Template matching: 1-2 seconds
- OCR extraction: 2-3 seconds
- Search and results: 3-5 seconds
- Desktop automation: <1 second

**Total workflow: ~15-25 seconds**

## License

[Your License Here]

## Support

For issues or questions:
1. Check troubleshooting section
2. Review logs with `--debug` flag
3. Run in `--headed` mode for visual inspection
4. Check Playwright documentation: https://playwright.dev/python/
