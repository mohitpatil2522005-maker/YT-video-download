"""Check if pywinauto is installed."""
try:
    import pywinauto
    print("pywinauto OK")
except ImportError as e:
    print(f"pywinauto NOT installed: {e}")
