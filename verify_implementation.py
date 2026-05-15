#!/usr/bin/env python3
"""
Verification script to ensure all Playwright automation components are properly installed.
Run this to verify the implementation is complete and working.
"""

import sys
import importlib
from pathlib import Path

def check_module(module_name, required=True):
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        status = "✓"
        print(f"{status} {module_name:40s} - Installed")
        return True
    except ImportError as e:
        status = "✗" if required else "⚠"
        print(f"{status} {module_name:40s} - {str(e)}")
        return False

def check_script_file(file_path, required=True):
    """Check if a script file exists."""
    if file_path.exists():
        print(f"✓ {file_path.name:50s} - Found")
        return True
    else:
        status = "✗" if required else "⚠"
        print(f"{status} {file_path.name:50s} - Not found")
        return False

def check_documentation(file_path):
    """Check if documentation file exists."""
    if file_path.exists():
        print(f"✓ {file_path.name:50s} - Available")
        return True
    else:
        print(f"⚠ {file_path.name:50s} - Not found")
        return False

def main():
    """Run all verification checks."""
    print("\n" + "="*70)
    print("PLAYWRIGHT AUTOMATION VERIFICATION")
    print("="*70 + "\n")
    
    project_root = Path(__file__).parent
    scripts_dir = project_root / "scripts"
    
    all_passed = True
    
    # 1. Check Python packages
    print("[1/4] Checking Python Packages")
    print("-" * 70)
    
    packages = [
        ("playwright", True),
        ("opencv", True),
        ("pytesseract", True),
        ("beautifulsoup4", True),
        ("lxml", True),
        ("PIL", True),
        ("numpy", True),
        ("pygetwindow", True),
        ("pyautogui", True),
        ("pyperclip", True),
    ]
    
    for package, required in packages:
        if not check_module(package, required=required):
            if required:
                all_passed = False
    
    print()
    
    # 2. Check script files
    print("[2/4] Checking Script Files")
    print("-" * 70)
    
    script_files = [
        (scripts_dir / "main.py", True),
        (scripts_dir / "browser_automation.py", True),
        (scripts_dir / "playwright_utils.py", True),
        (scripts_dir / "cv_ocr.py", True),
        (scripts_dir / "parser.py", True),
        (scripts_dir / "desktop_automation.py", True),
        (scripts_dir / "utils_logger.py", True),
        (scripts_dir / "__init__.py", False),
    ]
    
    for file_path, required in script_files:
        if not check_script_file(file_path, required=required):
            if required:
                all_passed = False
    
    print()
    
    # 3. Check documentation
    print("[3/4] Checking Documentation")
    print("-" * 70)
    
    docs = [
        (project_root / "README.md", True),
        (project_root / "PLAYWRIGHT_IMPLEMENTATION.md", True),
        (project_root / "PLAYWRIGHT_QUICK_REFERENCE.md", True),
        (project_root / "IMPLEMENTATION_SUMMARY.md", True),
        (project_root / "requirements.txt", True),
    ]
    
    for file_path in docs:
        if isinstance(file_path, tuple):
            file_path = file_path[0]
        check_documentation(file_path)
    
    print()
    
    # 4. Verify key functionality
    print("[4/4] Verifying Key Functionality")
    print("-" * 70)
    
    # Check if playwright_utils module can be imported and has key functions
    try:
        from scripts import playwright_utils
        key_functions = [
            'wait_for_element_with_retry',
            'safe_fill_input',
            'safe_click',
            'safe_text_extraction',
            'safe_get_attribute',
            'batch_extract_text',
            'batch_get_attributes',
            'execute_with_retry',
        ]
        
        for func_name in key_functions:
            if hasattr(playwright_utils, func_name):
                print(f"✓ {func_name:50s} - Available")
            else:
                print(f"✗ {func_name:50s} - Not found")
                all_passed = False
    except ImportError as e:
        print(f"✗ playwright_utils module - {e}")
        all_passed = False
    
    print()
    
    # Summary
    print("="*70)
    if all_passed:
        print("✓ ALL CHECKS PASSED - Implementation is complete!")
        print("="*70 + "\n")
        print("Next steps:")
        print("1. Review PLAYWRIGHT_IMPLEMENTATION.md for detailed guide")
        print("2. Check PLAYWRIGHT_QUICK_REFERENCE.md for common patterns")
        print("3. Run: python scripts/main.py --ref C:\\path\\to\\reference.png")
        print("4. For debugging: --headed --debug --log output.log")
        print()
        return 0
    else:
        print("✗ SOME CHECKS FAILED - Please resolve issues above")
        print("="*70 + "\n")
        print("To fix:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Install Playwright browsers: python -m playwright install")
        print("3. Check file paths and permissions")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
