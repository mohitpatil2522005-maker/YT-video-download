"""Resolve exact YouTube links for titles seen in images/ screenshots using plain HTTP."""
import json
import re
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TITLES = [
    "100% FREE AWS Certification Voucher + $757 Benefits",
    "Google Play Console Developer Account Banaye 2026 | Step by Step Complete Guide",
    "HOW TO GET FREE 24/7 VPS | 96GB DDR4 RAM - Ryzn 9 - Pterodactyl Panel",
    "FREE 24/7 VPS + RDP with 335GB RAM & 48 Core CPU | Host Access | INFINITE LABS",
    "How to Get a Free Educational Email ID | Easy & Legit Method 2026",
    "How to Setup FREE & UNLIMITED Claude Code With 1.3B Tokens Locally Using FCC-Claude & OpenRouter API",
    "Get UNLIMITED FREE Claude API Key (2026) (Groenen & Gruelas Method)",
    "FABLE 5 FREE API INSIDE CLAUDE CODE + 30M FREE TOKEN PER DAY FULL SETUP",
    "How to Get Free API Keys for ANY AI Model in 2026",
    "I Got a FREE VPS on Azure (No Credit Card)",
    "I Built and Deployed a Live AI App For $0!",
    "MoneyPrinterTurbo Setup Free AI Video Generator Unlimited AI Shorts Generator",
    "DeepSeek Harness Is INSANE!! Everything Is Plugin + Real Test (Full Setup)",
    "FREE Business Email With Your Own Domain in 8 Minutes (No Zoho, No Paid Plan)",
    "FREE 640GB RAM + 16 Core VPS (No Card) | Deepnote Method",
    "$0 Business Email - Why No One Talks About It?",
    "FREE 62GB VPS - Pterodactyl Panel Setup 24/7 server",
    "FREE 400GB RAM + 8Core + 4TB Storage VPS/RDP - INSANE SPECS!",
    "How to Build & Monetize AI apps in 20 Minutes With AI - No code app builder",
    "5 FREE Student Resources You're Missing (GPU, VPS, GitHub, Azure, SCP)",
]

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

VID_RE = re.compile(r'"videoRenderer":\{"videoId":"([\w-]{11})".*?"title":\{"runs":\[\{"text":"((?:[^"\\]|\\.)*)"', re.S)
SIMPLE_RE = re.compile(r'"videoId":"([\w-]{11})"')


def search(title):
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(title)
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "CONSENT=YES+1",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode("utf-8", "ignore")
    m = VID_RE.search(html)
    if m:
        vid, raw = m.group(1), m.group(2)
        yt_title = raw.encode().decode("unicode_escape", "ignore")
        return vid, yt_title
    m = SIMPLE_RE.search(html)
    if m:
        return m.group(1), ""
    return None, None


def main():
    import time
    results = []
    for i, title in enumerate(TITLES, 1):
        vid = yt_title = None
        for attempt in range(3):
            try:
                vid, yt_title = search(title)
                break
            except Exception as e:
                print(f"[{i}/{len(TITLES)}] try{attempt+1} ERROR: {e}")
                time.sleep(2)
        if vid:
            results.append((title, vid, yt_title))
            print(f"[{i}/{len(TITLES)}] OK  {vid}  |  {(yt_title or '')[:70]}")
        else:
            results.append((title, None, None))
            print(f"[{i}/{len(TITLES)}] NO RESULT")

    with open("exact_links.txt", "w", encoding="utf-8") as f:
        for title, vid, yt_title in results:
            if vid:
                f.write(f"{title}\n    -> https://www.youtube.com/watch?v={vid}\n    -> found as: {yt_title}\n\n")
            else:
                f.write(f"{title}\n    -> NOT FOUND\n\n")
    print("\nSaved to exact_links.txt")


if __name__ == "__main__":
    main()