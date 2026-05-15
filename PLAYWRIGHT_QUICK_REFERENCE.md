# Playwright Browser Automation - Quick Reference

A quick lookup guide for common Playwright operations in this project.

## Browser Lifecycle

### Launch Browser
```python
from scripts.browser_automation import launch_browser, close_browser

p, browser = launch_browser(
    headless=True,      # Run in background
    channel="chrome",   # Use Chrome (auto-fallback to Chromium)
    retries=2          # Retry on failure
)
```

### Close Browser
```python
close_browser(p, browser)
```

### With Context Manager (Safe Cleanup)
```python
try:
    p, browser = launch_browser()
    # ... use browser ...
finally:
    close_browser(p, browser)
```

## Page Navigation

### Navigate to URL
```python
from scripts.browser_automation import get_page_screenshot_and_html

screenshot_bytes, html = get_page_screenshot_and_html(
    browser,
    url="https://www.youtube.com",
    timeout=15000,              # 15 seconds
    wait_for_load_state="networkidle"  # Wait for network idle
)
```

### Navigate & Wait for Element
```python
page = browser.new_page()
page.goto(url, timeout=15000)
page.wait_for_selector("h1", timeout=5000)  # Wait for heading
```

### Wait States
```python
# Wait for DOM ready
page.wait_for_load_state("domcontentloaded")

# Wait for network to idle (recommended for YouTube)
page.wait_for_load_state("networkidle")

# Wait for full page load
page.wait_for_load_state("load")
```

## Element Interaction - Safe Methods

### Wait for Element (with Retry)
```python
from scripts.playwright_utils import wait_for_element_with_retry

found = wait_for_element_with_retry(
    page,
    selector="button.search",
    retries=3,
    timeout_ms=5000
)
```

### Fill Input
```python
from scripts.playwright_utils import safe_fill_input

safe_fill_input(
    page,
    selector="input#search",
    text="search query",
    clear_first=True  # Clear before filling
)
```

### Click Element
```python
from scripts.playwright_utils import safe_click

success = safe_click(
    page,
    selector="button.search",
    retries=3,
    wait_after_click_ms=500  # Wait after click
)
```

### Extract Text
```python
from scripts.playwright_utils import safe_text_extraction

text = safe_text_extraction(
    page,
    selector="h1.title",
    default="No title found"  # Fallback value
)
```

### Get Attribute
```python
from scripts.playwright_utils import safe_get_attribute

url = safe_get_attribute(
    page,
    selector="a.video-link",
    attribute="href",
    default=None
)
```

## Batch Operations

### Extract Multiple Text Values
```python
from scripts.playwright_utils import batch_extract_text

data = batch_extract_text(page, {
    "title": "h1",
    "description": "p.desc",
    "author": "span.author",
    "views": "span.views"
})

# Returns: {"title": "...", "description": "...", ...}
```

### Extract Multiple Attributes
```python
from scripts.playwright_utils import batch_get_attributes

links = batch_get_attributes(page, {
    "video_1": ("a.result:nth-child(1)", "href"),
    "video_2": ("a.result:nth-child(2)", "href"),
    "video_3": ("a.result:nth-child(3)", "href")
})

# Returns: {"video_1": "url1", "video_2": "url2", ...}
```

## Advanced Waits

### Wait for Multiple Elements
```python
from scripts.playwright_utils import wait_for_multiple_elements

results = wait_for_multiple_elements(
    page,
    selectors=["h1", "p", "button"],
    any_match=True,  # Return when any match found
    timeout_ms=5000
)

# Returns: {"h1": True, "p": False, "button": True}
```

### Custom Wait Condition
```python
from scripts.playwright_utils import wait_for_condition

try:
    wait_for_condition(
        condition_fn=lambda: page.query_selector("video") is not None,
        timeout_seconds=10,
        poll_interval=0.5
    )
except WaitTimeoutError:
    print("Video element not found")
```

## Retry Logic

### Execute with Retry
```python
from scripts.playwright_utils import execute_with_retry

result = execute_with_retry(
    fn=lambda: page.text_content("h1"),
    retries=3,
    wait_between_retries_ms=1000,
    error_message="Failed to get heading"
)
```

### Manual Retry Loop
```python
for attempt in range(1, 4):  # 3 attempts
    try:
        element = page.query_selector("button")
        if element:
            element.click()
            break
    except Exception as e:
        print(f"Attempt {attempt} failed: {e}")
        if attempt < 3:
            time.sleep(1)  # Wait before retry
```

## YouTube-Specific

### YouTube Search
```python
from scripts.browser_automation import search_youtube_and_capture

screenshot, html = search_youtube_and_capture(
    browser,
    query="python tutorial",
    timeout=15000
)
```

### Extract First Video URL
```python
from scripts.parser import extract_first_video_url

url = extract_first_video_url(html)
# Returns: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Screenshots & Content

### Take Screenshot
```python
# Viewport only (fast)
screenshot = page.screenshot(full_page=False)

# Full page (slow)
screenshot = page.screenshot(full_page=True)

# Save to file
page.screenshot(path="screenshot.png", full_page=False)
```

### Extract HTML
```python
html = page.content()  # Full HTML

# Extract specific content
content = page.text_content("body")  # All text
```

## Keyboard & Mouse

### Press Key
```python
page.press("body", "Enter")
page.press("input", "Escape")
```

### Type Text
```python
page.locator("input").type("search text", delay=50)  # 50ms between chars
```

### Click Mouse
```python
# Simple click
page.click("button")

# Click with options
page.click("button", button="right")  # Right-click
page.click("button", modifiers=["Control"])  # Ctrl+click
```

### Double Click
```python
page.dblclick("text")
```

## Error Handling

### Catch Timeout
```python
from playwright.sync_api import TimeoutError

try:
    page.wait_for_selector("element", timeout=5000)
except TimeoutError:
    print("Element not found within 5 seconds")
```

### Catch Generic Errors
```python
try:
    page.fill("input", "text")
except Exception as e:
    print(f"Error: {e}")
```

## CSS Selectors Cheat Sheet

```python
# Basic selectors
"button"                          # Element type
"#id"                            # By ID
".class"                         # By class
"div.container"                  # Type + class
"div#header"                     # Type + ID

# Attributes
"[name='search']"                # By attribute value
"[href^='https']"                # Attribute starts with
"[class*='video']"               # Attribute contains

# Combinators
"div > button"                   # Direct child
"div button"                     # Descendant
"button + span"                  # Adjacent sibling
"button ~ span"                  # General sibling

# Pseudo-selectors
"div:first-child"                # First child
"div:last-child"                 # Last child
"div:nth-child(2)"               # Nth child
"div:not(.hidden)"               # Negation

# YouTube Specific
"ytd-video-renderer"             # Video item
"#video-title"                   # Video title
"input[name='search_query']"    # Search input
"ytd-masthead"                   # YouTube header
```

## Performance Tips

```python
# ✓ GOOD - Headless mode (default)
p, browser = launch_browser(headless=True)

# ✗ SLOW - Headed mode (for debugging only)
p, browser = launch_browser(headless=False)

# ✓ GOOD - Reasonable timeout
timeout=15000  # 15 seconds

# ✗ SLOW - Excessive timeout
timeout=60000  # 60 seconds

# ✓ GOOD - Batch operations
batch_extract_text(page, {...})

# ✗ SLOW - Sequential operations
text1 = page.text_content("selector1")
text2 = page.text_content("selector2")
text3 = page.text_content("selector3")
```

## Debugging

### Enable Debug Logging
```bash
python scripts/main.py --ref image.png --debug
```

### Run in Headed Mode
```bash
python scripts/main.py --ref image.png --headed
```

### Print Selectors
```python
# Find all matching elements
elements = page.query_selector_all("button")
print(f"Found {len(elements)} buttons")

# Check element state
is_visible = page.is_visible("button")
is_enabled = page.is_enabled("input")
```

### Save Page State
```python
# Screenshot
page.screenshot(path="debug.png")

# HTML
with open("debug.html", "w") as f:
    f.write(page.content())

# Text
with open("debug.txt", "w") as f:
    f.write(page.text_content())
```

## Common Patterns

### Navigate → Wait → Extract
```python
page = browser.new_page()
page.goto(url)
page.wait_for_selector("h1")
title = page.text_content("h1")
```

### Search → Wait Results → Parse
```python
page.fill("input[name='search']", "query")
page.press("input[name='search']", "Enter")
page.wait_for_selector(".results")
results = page.query_selector_all(".result")
```

### Click → Wait Navigation
```python
page.click("a.link")
page.wait_for_load_state("networkidle")
new_url = page.url
```

## Quick Checklist

- [ ] Import required functions
- [ ] Launch browser with `launch_browser()`
- [ ] Navigate to URL with `page.goto()` or `get_page_screenshot_and_html()`
- [ ] Wait for elements with `wait_for_selector()` or `wait_for_element_with_retry()`
- [ ] Use safe methods: `safe_click()`, `safe_fill_input()`, `safe_text_extraction()`
- [ ] Handle errors with try/except
- [ ] Close browser with `close_browser(p, browser)`
- [ ] Test with `--headed` flag first
- [ ] Check logs with `--debug` flag
- [ ] Verify selectors with browser DevTools

## Resources

- **Documentation**: `PLAYWRIGHT_IMPLEMENTATION.md`
- **Playwright Docs**: https://playwright.dev/python/
- **CSS Selectors**: https://www.w3schools.com/cssref/selectors.asp
- **YouTube HTML Structure**: Use browser DevTools (F12) to inspect
