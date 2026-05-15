from bs4 import BeautifulSoup
from typing import Optional
import re


def extract_first_video_url(html: str) -> Optional[str]:
    # robustly find first /watch?v= link
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")
    # search for anchors with /watch?v=
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/watch?v=" in href and "list=" not in href:
            if href.startswith("http"):
                return href
            else:
                return "https://www.youtube.com" + href
    # fallback: regex search
    m = re.search(r"(/watch\?v=[A-Za-z0-9_-]{6,})", html)
    if m:
        return "https://www.youtube.com" + m.group(1)
    return None
