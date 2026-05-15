# Quick Start Guide - YouTube Downloader with Playwright Automation

Get started in 5 minutes!

## Prerequisites

- Windows 10+
- Python 3.9+
- Google Chrome (or Chromium)
- Internet connection

## Step 1: Installation (2 minutes)

```powershell
# Navigate to project directory
cd "c:\Users\mohit\Desktop\YT video downloa"

# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium

# Verify installation
python verify_implementation.py
```

Expected output: `✓ ALL CHECKS PASSED`

## Step 2: Prepare Reference Image (1 minute)

1. Take a screenshot of something you want to search for
2. Save it as `C:\reference_image.png`
3. Or use an existing image

Example:
- Screenshot of a book cover you want to search
- Logo of a product you're interested in
- Icon representing your search intent

## Step 3: Run the Automation (30 seconds)

```powershell
# Basic run (fastest)
python scripts/main.py --ref C:\reference_image.png

# Debug run (see what's happening)
python scripts/main.py --ref C:\reference_image.png --headed --debug

# With logging
python scripts/main.py --ref C:\reference_image.png --log output.log
```

**Important:** Make sure the desktop video downloader app is open and visible!

## Step 4: Verify Success

Watch for:
- ✓ Browser launches and navigates to YouTube
- ✓ Screenshot analysis and search query extraction
- ✓ YouTube search execution
- ✓ Video URL extraction
- ✓ Desktop app receives URL
- ✓ Download starts

Check exit code:
```powershell
echo $LASTEXITCODE
# 0 = Success
# 1 = No video found
# 2 = Desktop app not found
# 3 = Error (check logs)
```

## Common Issues & Fixes

### Issue: "Browser won't launch"
```powershell
# Solution: Reinstall Playwright
python -m playwright install chromium
```

### Issue: "No video found in search results"
```powershell
# Solution: Try with visual debug mode
python scripts/main.py --ref C:\reference.png --headed

# Check if YouTube loaded correctly and search executed
```

### Issue: "Desktop app not found"
```powershell
# Solution: Make sure app is open and window title matches
# Edit scripts/desktop_automation.py if needed
```

### Issue: "OCR not working"
```powershell
# Solution: Install Tesseract (optional but recommended)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or: choco install tesseract (if using Chocolatey)
```

## Usage Patterns

### 1. Simple Run (Production)
```bash
python scripts/main.py --ref image.png
```
- Fastest (headless mode)
- No visual output
- Good for scheduled runs

### 2. Debug Run (Development)
```bash
python scripts/main.py --ref image.png --headed --debug --log output.log
```
- Browser visible
- Verbose logging
- See everything happening
- Great for troubleshooting

### 3. Silent Run with Logging
```bash
python scripts/main.py --ref image.png --log output.log
```
- Headless (no browser window)
- Logs saved to file
- Good for background tasks

## Next Steps

1. **Read the Quick Reference**: `PLAYWRIGHT_QUICK_REFERENCE.md`
   - Common code patterns
   - CSS selector examples
   - Debugging tips

2. **Learn the Full Guide**: `PLAYWRIGHT_IMPLEMENTATION.md`
   - Detailed architecture
   - Module documentation
   - Performance optimization

3. **Customize Your Script**
   ```python
   # Example: Add custom search query
   python scripts/main.py --ref image.png
   # Then modify scripts/main.py to customize behavior
   ```

4. **Integrate with Python**
   ```python
   from scripts.browser_automation import launch_browser
   from scripts.playwright_utils import safe_click
   
   p, browser = launch_browser()
   # Your custom automation here
   ```

## Useful Commands

```powershell
# Verify setup
python verify_implementation.py

# Test browser setup
python scripts/test_browser.py

# Run main automation
python scripts/main.py --ref C:\image.png

# Debug mode
python scripts/main.py --ref C:\image.png --headed --debug

# With logging
python scripts/main.py --ref C:\image.png --log output.log

# Help
python scripts/main.py --help
```

## Performance Optimization

```bash
# ✓ FAST - Headless mode (default)
python scripts/main.py --ref image.png

# ✗ SLOW - Headed mode
python scripts/main.py --ref image.png --headed
```

**Typical execution time: 15-25 seconds (headless)**

## Documentation Quick Links

- **Main README**: `README.md` - Full project overview
- **Playwright Guide**: `PLAYWRIGHT_IMPLEMENTATION.md` - Detailed docs
- **Quick Reference**: `PLAYWRIGHT_QUICK_REFERENCE.md` - Code patterns
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md` - What's included

## Key Features

✅ **Browser Automation** - Playwright with anti-detection features
✅ **Visual Search** - OpenCV template matching + Tesseract OCR
✅ **Error Recovery** - Automatic retries and fallback logic
✅ **Logging** - Comprehensive debug information
✅ **Desktop Integration** - Automated application control

## Troubleshooting Checklist

- [ ] Python 3.9+ installed?
- [ ] Dependencies installed: `pip install -r requirements.txt`?
- [ ] Playwright installed: `python -m playwright install`?
- [ ] Reference image exists?
- [ ] Desktop app is open?
- [ ] Internet connection working?
- [ ] Running with correct path?

## Getting Help

1. **Check Logs**: Look for errors in console output
2. **Debug Mode**: Run with `--debug` flag for verbose output
3. **Visual Inspection**: Use `--headed` to see browser
4. **Read Docs**: See `PLAYWRIGHT_IMPLEMENTATION.md` troubleshooting
5. **Verify Setup**: Run `verify_implementation.py`

## Advanced Usage

### Custom Python Script

```python
from scripts.browser_automation import launch_browser, close_browser
from scripts.playwright_utils import safe_click, batch_extract_text

p, browser = launch_browser(headless=True)
page = browser.new_page()

try:
    page.goto("https://www.youtube.com")
    # Your automation here
    print("Done!")
finally:
    close_browser(p, browser)
```

### Batch Processing

```python
queries = ["python", "javascript", "web development"]

for query in queries:
    # Your automation for each query
    print(f"Processing: {query}")
```

### Scheduled Execution

```bash
# Windows Task Scheduler - Run at 3 PM daily
# Command: python.exe C:\path\to\scripts\main.py --ref C:\image.png
```

## Tips & Best Practices

1. **Use headless mode for speed** (default)
2. **Use headed mode for debugging** (`--headed`)
3. **Enable debug logging for troubleshooting** (`--debug`)
4. **Save logs for review** (`--log output.log`)
5. **Test with debug mode first**, then production
6. **Keep reference images clear and distinct**
7. **Ensure desktop app is visible when running**

## Success Criteria

Your automation is working if:
1. ✓ Browser launches and navigates YouTube
2. ✓ Screenshot is analyzed (CV/OCR)
3. ✓ Search query is extracted
4. ✓ YouTube search is executed
5. ✓ Results are parsed
6. ✓ Desktop app receives URL
7. ✓ Download starts
8. ✓ Exit code is 0

## Exit Codes Explained

```
0 - ✓ Success! Video URL extracted and sent to app
1 - ⚠ No video found in search results (check search query)
2 - ⚠ Desktop app not found (open the app and try again)
3 - ✗ Unexpected error (check logs with --debug)
```

## Performance Stats

- Browser launch: 2-4 seconds
- YouTube navigation: 3-5 seconds
- Screenshot + analysis: 3-5 seconds
- Search + results: 3-5 seconds
- Desktop automation: <1 second
- **Total: 15-25 seconds**

## Limitations & Notes

- **Windows only** - Uses Windows-specific APIs
- **Desktop app required** - Must be installed and running
- **Visual search optional** - Falls back to default if reference missing
- **Rate limiting** - Don't run too frequently (YouTube may block)
- **Terms of Service** - Check YouTube ToS for automation rules

## Next Level

Ready to dive deeper? Check out:
- `PLAYWRIGHT_IMPLEMENTATION.md` - Full architecture
- Module source code with detailed docstrings
- `PLAYWRIGHT_QUICK_REFERENCE.md` - Common patterns
- Playwright official docs: https://playwright.dev/python/

## Done! 🎉

You now have a working YouTube video extraction automation system!

Questions? Check the documentation files or review the source code comments.

Enjoy automating! 🚀
