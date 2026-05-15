# YouTube CV + Playwright Downloader (Windows)

A robust Python automation framework using Playwright for browser orchestration, OpenCV/PyTesseract for computer vision-based visual search, and PyAutoGUI/pywinauto for desktop automation. Executes an end-to-end workflow to extract YouTube video URLs and pass them to a local desktop application.

## Overview

**Workflow:**
1. **Browser Automation (Playwright)** - Launch Chrome, navigate to YouTube
2. **Visual Search (OpenCV + PyTesseract)** - Capture screenshots, process with CV to locate visual cues, perform OCR for text extraction
3. **Data Extraction (BeautifulSoup)** - Parse YouTube search results, extract first video URL
4. **Cross-Application Automation** - Locate desktop app "video downloder standerd", focus window, paste URL, trigger download
5. **Error Handling & Logging** - Comprehensive logging at each stage with retry logic

## Prerequisites

### System Requirements
- **OS:** Windows 10+ (tested on Windows)
- **Python:** 3.9 or later
- **Chrome:** Installed locally (Playwright will auto-detect)
- **Tesseract OCR:** Optional (for advanced OCR; can fall back to template matching)

### Optional: Tesseract Installation

If you want to use Tesseract OCR for text extraction:

1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install (default: `C:\Program Files\Tesseract-OCR`)
3. Verify installation:
   ```powershell
   tesseract --version
   ```

## Installation

### 1. Clone/Extract Project
```powershell
cd c:\Users\mohit\Desktop\YT video downloa
```

### 2. Create Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python -m playwright install
```

This will:
- Install all Python packages (Playwright, OpenCV, PyTesseract, PyAutoGUI, etc.)
- Download Playwright browser binaries

### 4. Verify Installation
```powershell
python scripts\test_browser.py
```

Expected output: All 3 tests pass (browser launch, page navigation, YouTube connectivity)

## Usage

### Basic Usage

```powershell
python scripts\main.py --ref C:\path\to\reference_image.png
```

### Advanced Options

```powershell
# Run with browser visible (for debugging)
python scripts\main.py --ref C:\path\to\reference_image.png --headed

# Enable debug logging
python scripts\main.py --ref C:\path\to\reference_image.png --debug

# Save logs to file
python scripts\main.py --ref C:\path\to\reference_image.png --log automation.log

# Combine options
python scripts\main.py --ref C:\path\to\reference_image.png --headed --debug --log output.log
```

### Example Workflow

1. **Prepare reference image** - A screenshot or image containing visual cues for your search
   ```powershell
   # Save a screenshot or find an image representing your search intent
   ```

2. **Run automation** (headless, production mode)
   ```powershell
   python scripts\main.py --ref C:\my_references\search_cue.png
   ```

3. **Observe execution**
   - Browser launches and navigates to YouTube
   - CV processes reference image and derives search query
   - YouTube is searched with extracted query
   - First video URL is extracted from results
   - Desktop app is located and focused
   - URL is pasted and download is triggered

## Project Structure

```
YT video downloa/
├── scripts/
│   ├── __init__.py                   # Package marker
│   ├── main.py                       # Entry point; orchestrates workflow
│   ├── browser_automation.py         # Playwright browser launch/navigation/capture
│   ├── cv_ocr.py                    # OpenCV template-matching and PyTesseract OCR
│   ├── parser.py                     # YouTube HTML parsing and URL extraction
│   ├── desktop_automation.py         # Window management, focus, clipboard, input simulation
│   ├── utils_logger.py              # Centralized logging setup
│   ├── test_browser.py              # Test utility for Playwright setup verification
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
```

## Module Details

### `browser_automation.py`
- `launch_browser(headless, user_agent, timeout, retries)` - Launch Chrome with retry logic
- `close_browser(p, browser)` - Clean up browser resources
- `get_page_screenshot_and_html(browser, url, timeout, wait_for_load_state, full_page)` - Navigate, capture, and extract HTML
- `search_youtube_and_capture(browser, query, timeout)` - Execute YouTube search and capture results

**Features:**
- Headless or headed mode (headed useful for debugging)
- Retry logic on launch failure
- Configurable timeouts and wait states
- Full-page or viewport-only screenshots
- Comprehensive error logging

### `cv_ocr.py`
- `template_match(screenshot_bytes, template_path, threshold)` - OpenCV template matching
- `ocr_extract_text(screenshot_bytes, region)` - PyTesseract OCR on image region
- `derive_search_query_from_reference(screenshot_bytes, template_path)` - Intelligently combine template matching + OCR to produce search query

**Features:**
- Falls back from template matching to OCR if needed
- Configurable matching threshold
- Region-based OCR for targeted text extraction

### `parser.py`
- `extract_first_video_url(html)` - Parse YouTube search results HTML to find first video link

**Features:**
- Multiple parsing strategies (BeautifulSoup + regex fallback)
- Excludes playlists and other non-video results
- Returns absolute URL

### `desktop_automation.py`
- `find_window_by_title_regex(title_regex, timeout)` - Locate desktop app by window title
- `focus_window(win, raise_window)` - Activate and bring window to foreground
- `paste_url_and_trigger(url, paste_hotkey, trigger_key)` - Clipboard paste + keyboard simulation
- `send_url_to_app(url, app_title_regex, timeout)` - Orchestrate window finding, focusing, and pasting

**Features:**
- Fuzzy window title matching (regex-based)
- Configurable paste hotkey and trigger key
- Timeout handling for window search

## Troubleshooting

### "Failed to launch browser"
- Ensure Chrome is installed
- Verify Playwright is installed: `pip list | findstr playwright`
- Run: `python -m playwright install chromium`

### "No video URL found in search results"
- Check YouTube connectivity: `python scripts/test_browser.py`
- The reference image might not produce a valid search query
- Run with `--headed --debug` to observe browser and logs

### "Failed to find 'video downloder standerd' application"
- Ensure the desktop app is open and visible
- Check the app window title matches the regex pattern in `desktop_automation.py`
- Edit `app_title_regex` parameter if your app has a different title

### "Tesseract not found" (optional warning)
- This is non-fatal; template matching will be used as primary method
- To enable OCR, install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Ensure `pytesseract` can locate Tesseract: `python -c "import pytesseract; print(pytesseract.pytesseract.pytesseract_cmd)"`

## Testing

### Test Browser Setup
```powershell
python scripts\test_browser.py
```
Tests:
1. Browser launch/close
2. Page navigation and screenshot capture
3. YouTube connectivity

### Test with Headed Mode
```powershell
python scripts\test_browser.py --headed
```
Browser will be visible; useful for visual debugging.

### Test with Debug Logging
```powershell
python scripts\test_browser.py --debug
```
Enables detailed DEBUG-level logs for all operations.

## Performance & Configuration

### Timeouts
- Default page navigation: 15 seconds
- Default wait state: "networkidle"
- Adjustable in `get_page_screenshot_and_html()` and `main.py`

### Browser Launch Retries
- Default: 2 retries on launch failure
- Adjustable in `launch_browser(retries=N)`

### Template Matching Threshold
- Default: 0.7 (70% match confidence)
- Adjustable in `cv_ocr.py` `template_match(threshold=N)`

### Window Search Timeout
- Default: 10 seconds for finding desktop app
- Adjustable in `desktop_automation.py` `send_url_to_app(timeout=N)`

## Security & Rate Limiting

**Important:**
- This script performs automated web scraping and browser automation
- YouTube's Terms of Service may restrict automated access
- Recommended: Use delays and randomization if running repeatedly
- Consider: Adding delays between requests (`time.sleep()`) to avoid rate limiting

## Requirements

See `requirements.txt` for all dependencies:
- `playwright` - Browser automation
- `opencv-python` - Computer vision
- `pytesseract` - OCR (Python wrapper for Tesseract)
- `pyautogui` - Keyboard/mouse simulation
- `pygetwindow` - Window management
- `pywinauto` - Alternative window management (Windows)
- `pyperclip` - Clipboard access
- `beautifulsoup4` - HTML parsing
- `lxml` - HTML parsing backend
- `Pillow` - Image processing
- `numpy` - Numerical computing (required by OpenCV)

## Logging

Logs are output to:
1. **Console (stdout)** - By default
2. **Log file** - If `--log` option is provided

Format: `YYYY-MM-DD HH:MM:SS [LEVEL] logger_name: message`

Example:
```
2026-05-15 14:32:10 [INFO] yt_downloader: ============================================================
2026-05-15 14:32:10 [INFO] yt_downloader: YouTube Automation Workflow Started
2026-05-15 14:32:10 [INFO] yt_downloader: Reference image: C:\search_cue.png
2026-05-15 14:32:10 [INFO] yt_downloader: Browser mode: HEADLESS
2026-05-15 14:32:10 [INFO] yt_downloader: [1/6] Initializing browser automation...
```

## Exit Codes

- `0` - Success
- `1` - No video found in search results
- `2` - Desktop application not found
- `3` - Unhandled error (see logs for details)

## License

[Add your license here]

## Support

For issues or questions, check logs with `--debug` flag or run `test_browser.py` to verify setup.

