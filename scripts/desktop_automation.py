import time
import re
from typing import Optional
import pygetwindow as gw
import pyautogui
import pyperclip
from pywinauto import Application, Desktop


def find_window_by_title_regex(title_regex: str, timeout: int = 10):
    end = time.time() + timeout
    pattern = re.compile(title_regex, re.IGNORECASE)
    while time.time() < end:
        wins = gw.getAllWindows()
        for w in wins:
            try:
                if w.title and pattern.search(w.title):
                    import logging
                    logging.getLogger("yt_downloader").info(f"Found window: '{w.title}'")
                    return w
            except Exception:
                continue
        time.sleep(0.5)
    import logging
    logging.getLogger("yt_downloader").warning(f"Window matching '{title_regex}' not found within {timeout}s")
    return None


def focus_window(win, raise_window: bool = True):
    if not win:
        return False
    import logging
    logger = logging.getLogger("yt_downloader")
    try:
        logger.info(f"Activating window: '{win.title}' using pywinauto")
        # Use pywinauto to connect to the window
        app = Application().connect(handle=win._hWnd)
        app_win = app.window(handle=win._hWnd)
        app_win.set_focus()
        if raise_window:
            if app_win.get_show_state() == 2: # Minimized
                app_win.restore()
        return True
    except Exception as e:
        logger.warning(f"Pywinauto activation failed: {e}")
        try:
            win.activate()
            return True
        except Exception as e2:
            logger.error(f"Fallback activation failed: {e2}")
            return False


def paste_url_and_trigger(url: str, paste_hotkey: tuple = ("ctrl", "v"), trigger_key: str = "enter"):
    # copy to clipboard
    pyperclip.copy(url)
    time.sleep(0.2)
    # paste
    pyautogui.hotkey(*paste_hotkey)
    time.sleep(0.2)
    pyautogui.press(trigger_key)


def send_url_to_app(url: str, app_title_regex: str = r"video.*down.*stand", timeout: int = 10) -> bool:
    win = find_window_by_title_regex(app_title_regex, timeout=timeout)
    if not win:
        return False
    ok = focus_window(win)
    if not ok:
        return False
    time.sleep(0.5)
    paste_url_and_trigger(url)
    return True
