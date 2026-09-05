"""Search YouTube for exact titles from the screenshot and extract real video IDs."""
import json
import re
import sys
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright

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


def find_video_renderers(obj, out):
    """Recursively collect videoRenderer dicts."""
    if isinstance(obj, dict):
        if "videoRenderer" in obj:
            out.append(obj["videoRenderer"])
        for v in obj.values():
            find_video_renderers(v, out)
    elif isinstance(obj, list):
        for item in obj:
            find_video_renderers(item, out)


def main():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
            locale="en-US",
        )
        page = ctx.new_page()
        # Accept consent page if shown
        page.on("domcontentloaded", lambda _: None)

        for i, title in enumerate(TITLES, 1):
            url = f"https://www.youtube.com/results?search_query={quote_plus(title)}"
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2500)
                # Try consent button
                try:
                    btn = page.query_selector('button[aria-label*="Accept"], button[aria-label*="accept"]')
                    if btn:
                        btn.click()
                        page.wait_for_timeout(2000)
                except Exception:
                    pass

                data = page.evaluate("() => JSON.stringify(window.ytInitialData || {})")
                renderers = []
                find_video_renderers(json.loads(data or "{}"), renderers)

                found = None
                for r in renderers:
                    vid = r.get("videoId")
                    t_runs = (
                        r.get("title", {}).get("runs", [{}])[0].get("text", "")
                        if isinstance(r.get("title"), dict) else str(r.get("title", ""))
                    )
                    if vid:
                        found = (vid, t_runs)
                        break

                if found:
                    results.append((title, found[0], found[1]))
                    print(f"[{i}/{len(TITLES)}] OK  {found[0]}  |  {found[1][:70]}")
                else:
                    results.append((title, None, None))
                    print(f"[{i}/{len(TITLES)}] NO RESULT")
            except Exception as e:
                results.append((title, None, None))
                print(f"[{i}/{len(TITLES)}] ERROR: {e}")

        browser.close()

    # Save results
    out_path = "exact_links.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        for title, vid, yt_title in results:
            if vid:
                f.write(f"{title}\n    -> https://www.youtube.com/watch?v={vid}\n    -> found as: {yt_title}\n\n")
            else:
                f.write(f"{title}\n    -> NOT FOUND\n\n")
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
