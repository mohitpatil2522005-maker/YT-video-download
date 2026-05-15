# Playwright Automation Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    YOUTUBE VIDEO DOWNLOADER AUTOMATION                   │
│                     (Playwright + OpenCV + PyAutoGUI)                    │
└─────────────────────────────────────────────────────────────────────────┘

┌─ ENTRY POINT ─────────────────────────────────────────────────────────┐
│                          scripts/main.py                               │
│                                                                         │
│  • Parse command-line arguments                                       │
│  • Initialize logging                                                 │
│  • Orchestrate workflow                                               │
│  • Handle errors and exit codes                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
        ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
        │   BROWSER LAYER  │  │  UTILITIES   │  │   HELPERS    │
        └──────────────────┘  └──────────────┘  └──────────────┘


┌─ LAYER 1: BROWSER CONTROL ────────────────────────────────────────────┐
│                      browser_automation.py                             │
├───────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─ Browser Lifecycle ────────┐                                       │
│  │ • launch_browser()         │  ┌─ Navigation ─────────────────┐    │
│  │ • close_browser()          │  │ • goto(url)                   │    │
│  │ • get launch args          │  │ • wait_for_load_state()      │    │
│  │ • Chrome/Chromium fallback │  │ • handle timeouts            │    │
│  │ • Retry logic              │  └────────────────────────────┘    │
│  └────────────────────────────┘                                       │
│                                                                         │
│  ┌─ Content Capture ──────────┐                                       │
│  │ • screenshot()             │  ┌─ YouTube Specific ────────────┐   │
│  │ • page.content()           │  │ • search_youtube_and_capture()│   │
│  │ • full_page / viewport     │  │ • URL encoding                │   │
│  │ • error handling           │  │ • results parsing             │   │
│  └────────────────────────────┘  └────────────────────────────┘   │
│                                                                         │
│  FEATURES:                                                             │
│  ✓ Anti-detection arguments                                           │
│  ✓ Configurable timeouts                                              │
│  ✓ Automatic channel fallback                                         │
│  ✓ Comprehensive error logging                                        │
└─────────────────────────────────────────────────────────────────────────┘


┌─ LAYER 2: SAFE UTILITIES ─────────────────────────────────────────────┐
│                      playwright_utils.py (NEW)                         │
├───────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─ Safe Wait Operations ────────────────────────────────────────┐   │
│  │ • wait_for_element_with_retry(selector, retries=3)          │   │
│  │ • wait_for_condition(fn, timeout_seconds=10)                │   │
│  │ • wait_for_multiple_elements(selectors, any_match=False)    │   │
│  │                                                               │   │
│  │ PURPOSE: Robust waiting with automatic retries              │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─ Safe Interaction Operations ─────────────────────────────────┐   │
│  │ • safe_fill_input(selector, text, clear_first=True)         │   │
│  │ • safe_click(selector, retries=3, wait_after_click_ms=500)  │   │
│  │ • safe_text_extraction(selector, default="")                │   │
│  │ • safe_get_attribute(selector, attr, default=None)          │   │
│  │                                                               │   │
│  │ PURPOSE: Error-resistant element interaction                │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─ Batch Operations ────────────────────────────────────────────┐   │
│  │ • batch_extract_text(page, selectors={...})                 │   │
│  │ • batch_get_attributes(page, selectors={...})               │   │
│  │                                                               │   │
│  │ PURPOSE: Extract multiple values efficiently                │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─ Generic Retry Wrapper ────────────────────────────────────────┐  │
│  │ • execute_with_retry(fn, retries=3, error_message="...")     │  │
│  │                                                               │  │
│  │ PURPOSE: Add retries to any operation                        │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  FEATURES:                                                             │
│  ✓ Automatic retries                                                  │
│  ✓ Timeout handling                                                   │
│  ✓ Custom exceptions                                                  │
│  ✓ Default fallbacks                                                  │
│  ✓ Comprehensive logging                                              │
└─────────────────────────────────────────────────────────────────────────┘


┌─ LAYER 3: CONTENT PROCESSING ─────────────────────────────────────────┐
│                      cv_ocr.py & parser.py                             │
├───────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─ Computer Vision (cv_ocr.py) ──────────────────────────────┐      │
│  │ • template_match()              - OpenCV matching          │      │
│  │ • ocr_extract_text()            - Tesseract OCR            │      │
│  │ • derive_search_query_from_ref()- Pipeline                 │      │
│  │                                                             │      │
│  │ FLOW: Screenshot → Find reference → Extract text           │      │
│  │       → Generate search query                              │      │
│  └─────────────────────────────────────────────────────────┘      │
│                                                                         │
│  ┌─ HTML Parsing (parser.py) ─────────────────────────────────┐      │
│  │ • extract_first_video_url()     - Parse YouTube results    │      │
│  │                                                             │      │
│  │ FLOW: YouTube results HTML → BeautifulSoup → Regex →      │      │
│  │       Absolute URL                                         │      │
│  └─────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘


┌─ LAYER 4: DESKTOP INTEGRATION ────────────────────────────────────────┐
│                    desktop_automation.py                               │
├───────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─ Window Management ──────────────────────────────────────────┐    │
│  │ • find_window_by_title_regex(pattern)                       │    │
│  │ • focus_window(win, raise_window=True)                      │    │
│  │                                                              │    │
│  │ PURPOSE: Locate and focus desktop application              │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                         │
│  ┌─ URL Transmission ───────────────────────────────────────────┐    │
│  │ • paste_url_and_trigger(url)                                │    │
│  │ • send_url_to_app(url, app_title_regex, timeout)           │    │
│  │                                                              │    │
│  │ PURPOSE: Copy URL to clipboard, paste, trigger download    │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘


┌─ LAYER 5: LOGGING & UTILITIES ────────────────────────────────────────┐
│                      utils_logger.py                                   │
├───────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  • setup_logger(name, level, log_file)  - Logger configuration        │
│  • Console output (stdout)                                            │
│  • File output (optional)                                             │
│  • Timestamp formatting                                               │
│  • UTF-8 encoding support                                             │
│                                                                         │
│  LOG LEVELS:                                                           │
│  DEBUG   - Detailed operation info, selector info                     │
│  INFO    - Major workflow steps, results                              │
│  WARNING - Retries, non-fatal issues                                  │
│  ERROR   - Failed operations, exceptions                              │
└─────────────────────────────────────────────────────────────────────────┘


┌─ WORKFLOW FLOW ────────────────────────────────────────────────────────┐
│                                                                          │
│  START                                                                   │
│    │                                                                     │
│    ▼                                                                     │
│  1. Launch Browser                                                       │
│     ├─ Try Chrome channel                                               │
│     └─ Fallback to Chromium                                             │
│    │                                                                     │
│    ▼                                                                     │
│  2. Navigate YouTube                                                     │
│     └─ Wait for page load (networkidle)                                │
│    │                                                                     │
│    ▼                                                                     │
│  3. Capture Screenshot                                                   │
│     ├─ Store as bytes                                                   │
│     └─ Extract HTML                                                     │
│    │                                                                     │
│    ▼                                                                     │
│  4. Visual Search (if reference image provided)                         │
│     ├─ Template matching (OpenCV)                                       │
│     ├─ If matched: Extract text region                                  │
│     └─ OCR (Tesseract) → Search query                                  │
│    │                                                                     │
│    ▼                                                                     │
│  5. YouTube Search                                                       │
│     ├─ URL-encode query                                                │
│     └─ Navigate to results                                              │
│    │                                                                     │
│    ▼                                                                     │
│  6. Extract Video URL                                                    │
│     ├─ Parse HTML with BeautifulSoup                                    │
│     ├─ Find first /watch?v= link                                        │
│     └─ Regex fallback if needed                                         │
│    │                                                                     │
│    ▼                                                                     │
│  7. Close Browser                                                        │
│     └─ Clean up resources                                               │
│    │                                                                     │
│    ▼                                                                     │
│  8. Find Desktop App                                                     │
│     └─ Regex window title matching                                      │
│    │                                                                     │
│    ▼                                                                     │
│  9. Focus App Window                                                     │
│     ├─ Restore if minimized                                             │
│     └─ Maximize                                                         │
│    │                                                                     │
│    ▼                                                                     │
│  10. Send URL                                                            │
│      ├─ Copy to clipboard                                               │
│      ├─ Paste (Ctrl+V)                                                  │
│      └─ Trigger (Enter)                                                 │
│    │                                                                     │
│    ▼                                                                     │
│  SUCCESS - Download triggered                                           │
│                                                                          │
│  ON ERROR:                                                               │
│  ├─ Log error with context                                              │
│  ├─ Exit with appropriate code                                          │
│  └─ Cleanup resources                                                   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘


┌─ ERROR HANDLING STRATEGY ──────────────────────────────────────────────┐
│                                                                          │
│  For each operation:                                                     │
│                                                                          │
│    ┌─ TRY ────────────────┐                                             │
│    │ Execute operation    │                                             │
│    └──────────────────────┘                                             │
│         │                                                                │
│         ├─ SUCCESS ─────────────────────────────────────────► RETURN   │
│         │                                                                │
│         └─ FAIL                                                          │
│             │                                                            │
│             ▼                                                            │
│    ┌─ RETRY ──────────────────────┐  (up to N times)                   │
│    │ Wait between retries          │                                     │
│    │ Log attempt number            │                                     │
│    └───────────────────────────────┘                                     │
│         │                                                                │
│         ├─ SUCCESS ─────────────────────────────────────────► RETURN   │
│         │                                                                │
│         └─ FAIL                                                          │
│             │                                                            │
│             ▼                                                            │
│    ┌─ EXCEPTION HANDLING ─────────────────────┐                        │
│    │ Catch specific exception type            │                        │
│    │ Log detailed error                       │                        │
│    │ Return default/fallback value            │                        │
│    │ OR raise exception                       │                        │
│    └───────────────────────────────────────────┘                        │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘


┌─ CONFIGURATION HIERARCHY ──────────────────────────────────────────────┐
│                                                                          │
│  Command-Line Arguments                                                 │
│  │                                                                       │
│  ├─ --ref IMAGE.PNG          Reference image for visual search         │
│  ├─ --headed                 Show browser window                        │
│  ├─ --debug                  Enable debug logging                       │
│  └─ --log FILE.LOG           Log to file                                │
│                                                                          │
│  These configure:                                                        │
│  ├─ Browser launch (headless mode)                                      │
│  ├─ Logging level (DEBUG or INFO)                                       │
│  ├─ Log file path (console or file)                                     │
│  └─ Reference image for visual search                                   │
│                                                                          │
│  Defaults:                                                               │
│  ├─ headless = True                                                      │
│  ├─ log_level = INFO                                                     │
│  ├─ ref_image = required                                                 │
│  └─ log_file = None (console only)                                      │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘


┌─ DEPENDENCIES GRAPH ───────────────────────────────────────────────────┐
│                                                                          │
│  main.py                                                                │
│  ├─ browser_automation.py (Playwright)                                  │
│  ├─ playwright_utils.py (Safe wrappers)                                 │
│  │  └─ playwright (native)                                              │
│  ├─ cv_ocr.py (Computer Vision)                                         │
│  │  ├─ cv2 (OpenCV)                                                     │
│  │  ├─ pytesseract (OCR)                                                │
│  │  └─ PIL (Image)                                                      │
│  ├─ parser.py (HTML parsing)                                            │
│  │  ├─ beautifulsoup4                                                   │
│  │  └─ lxml                                                             │
│  ├─ desktop_automation.py (Desktop control)                             │
│  │  ├─ pygetwindow (Windows)                                            │
│  │  ├─ pyautogui (Input)                                                │
│  │  └─ pyperclip (Clipboard)                                            │
│  └─ utils_logger.py (Logging)                                           │
│     └─ logging (stdlib)                                                 │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘


SUMMARY:

┌─────────────────────────────────────────────┐
│  BROWSER               UTILITIES              │
│  ┌─────────────────┐  ┌──────────────────┐  │
│  │ Playwright      │  │ Safe Operations  │  │
│  │ Chrome/Chromium │  │ Retries          │  │
│  │ Anti-detection  │  │ Batch Extract    │  │
│  │ Timeouts        │  │ Error Handling   │  │
│  └─────────────────┘  └──────────────────┘  │
│          ▼                     ▼             │
│  ┌─────────────────────────────────────┐   │
│  │      YOUTUBE WORKFLOW                │   │
│  │  Navigate → Search → Parse → Extract │   │
│  └─────────────────────────────────────┘   │
│          ▼                                  │
│  ┌─────────────────────────────────────┐   │
│  │    DESKTOP AUTOMATION                │   │
│  │  Find → Focus → Paste → Trigger     │   │
│  └─────────────────────────────────────┘   │
│                                            │
│  LOGGING & DEBUGGING                      │
│  • Debug mode                             │
│  • File logging                           │
│  • Console output                         │
│  • Error tracking                         │
└─────────────────────────────────────────────┘
```

## Module Interaction

```
User
  │
  ▼
main.py (Orchestrator)
  │
  ├─► browser_automation.py
  │    ├─► Launch browser
  │    ├─► Navigate URLs
  │    └─► Capture content
  │
  ├─► playwright_utils.py
  │    ├─► Wait for elements
  │    ├─► Safe clicks & fills
  │    └─► Batch operations
  │
  ├─► cv_ocr.py
  │    ├─► Template matching
  │    ├─► OCR text extraction
  │    └─► Search query generation
  │
  ├─► parser.py
  │    └─► Extract video URLs from HTML
  │
  ├─► desktop_automation.py
  │    ├─► Find window
  │    ├─► Focus app
  │    └─► Send URL
  │
  └─► utils_logger.py
       └─► Log all operations

  │
  ▼
Result: Download triggered or error reported
```

This architecture ensures:
- ✅ Separation of concerns
- ✅ Reusability of components
- ✅ Easy testing and debugging
- ✅ Clear error handling
- ✅ Comprehensive logging
- ✅ Production-ready reliability
