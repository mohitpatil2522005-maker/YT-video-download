"""Resolve exact YouTube links for videos visible in images/ folder using yt-dlp search."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from yt_dlp import YoutubeDL

# Titles transcribed from images/ screenshots (verbatim as shown)
QUERIES = [
    # --- photo_2026-09-10_14-56-06.jpg (12 videos, clear) ---
    ("img2-01", "FREE 24/7 RDP with 4Gbps Speed (No Card!) CodeSandbox Method INFINITE LABS"),
    ("img2-02", "I Made UNLIMITED Free Windows 11 RDPs GitHub Method INFINITE LABS"),
    ("img2-03", "How I Earned My First 5000 as a Student Real Story ekoaham"),
    ("img2-04", "I Built a Full AI Backend in 20 Minutes No Backend Coding ekoaham"),
    ("img2-05", "I Got a Free Domain in 5 Minutes 2026 NO CAP ekoaham"),
    ("img2-06", "Free Hosting in 2026 This Actually Works ekoaham"),
    ("img2-07", "FREE AI TOOLS for 24 HOURS Leonardo AI DeepSeek ekoaham"),
    ("img2-08", "FREE Avira VPN Kiro AI Access Limited Time ekoaham"),
    ("img2-09", "Claim 500GB FREE Storage Before Everyone Finds Out ekoaham pCloud"),
    ("img2-10", "This Website Gives You a FREE Windows PC ekoaham"),
    ("img2-11", "GET 20000 OPENART AI CREDITS FOR FREE ekoaham"),
    ("img2-12", "Launch Your AI Startup Without Coding in 2026 ekoaham"),
    # --- photo_2026-09-10_14-55-56.jpg (long Downloads list) ---
    ("img1-01", "GET FREE 24/7 VPS FOR LIFETIME Pterodactyl Panel"),
    ("img1-02", "I used GPT-5 Astra for FREE 10 Minutes Later I built THIS"),
    ("img1-03", "Render Backend Sleeping Fix It FREE with Cron Jobs"),
    ("img1-04", "Unlimited Gmail Account Without Phone Number Multiple Gmail Accounts Without Verification 2026"),
    ("img1-05", "AI agent runs on Termux Hermes agent Technical Bolt"),
    ("img1-06", "I Found A Free VPS That No One Knows 16GB RAM 8 CPU"),
    ("img1-07", "how to make amplifier at home amplifier"),
    ("img1-08", "GET 6 MONTHS PREMIUM VPN FREE ALL COUNTRIES FAST SAFE VPN"),
    ("img1-09", "I Built A Self Improving AI Trading Bot You Can Copy It SumedhKumar"),
    ("img1-10", "How To Convert Claude to Trading View Most IMP video of 2025 Sumedhkumar"),
    ("img1-11", "I Got a FREE 8GB VPS in 2026 No Hidden Charges"),
    ("img1-12", "Best FREE VPS in 2026 250GB RAM 32 CPU No Cost"),
    ("img1-13", "Opencode termux better than claude code Technical Bot"),
    ("img1-14", "How to make peltier module at home peltier module kaise banaye Chandan Experiment"),
    ("img1-15", "Xiruzhi ai ko phone Se kaise banaye"),
    ("img1-16", "Learn Termux Hacking from Scratch for Beginners 2026"),
    ("img1-17", "Make Your Own VPS Hosting Business FREE Method CodeSandbox Discord Bot"),
    ("img1-18", "How to Create an Organization and Google Play Console Account Full Setup Instant Website Verification"),
    ("img1-19", "Fix RAM LEAKS in Windows Boost FPS Performance RAM Overclocking Techno Uplift"),
    ("img1-20", "How to Make Paid Subscription Bot Full Tutorial Monetize Telegram Channel 2026 TEKNO KRISH"),
    ("img1-21", "5 Skills to Earn Money as a Student in 2026"),
]

def resolve(query, n=3):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{n}:{query}", download=False)
        entries = info.get("entries", []) if info else []
        out = []
        for e in entries:
            if e:
                out.append({
                    "id": e.get("id"),
                    "title": e.get("title"),
                    "channel": e.get("channel") or e.get("uploader"),
                    "duration": e.get("duration"),
                    "view_count": e.get("view_count"),
                    "url": f"https://www.youtube.com/watch?v={e.get('id')}",
                })
        return out

def main():
    lines = []
    for key, q in QUERIES:
        try:
            results = resolve(q, n=3)
        except Exception as e:
            print(f"[{key}] ERROR: {e}", flush=True)
            lines.append(f"[{key}] QUERY: {q}\n    -> ERROR: {e}\n")
            continue
        if results:
            best = results[0]
            print(f"[{key}] OK {best['url']} | {best['title']} | {best['channel']}", flush=True)
            lines.append(f"[{key}] QUERY: {q}\n    -> {best['url']}\n    -> found as: {best['title']} | channel: {best['channel']} | duration: {best['duration']}s | views: {best['view_count']}\n")
            for alt in results[1:]:
                lines.append(f"       alt: {alt['url']} | {alt['title']} | {alt['channel']}\n")
            lines.append("\n")
        else:
            print(f"[{key}] NO RESULT for: {q}", flush=True)
            lines.append(f"[{key}] QUERY: {q}\n    -> NOT FOUND\n\n")
    with open("images_video_links.txt", "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("\nSaved to images_video_links.txt")

if __name__ == "__main__":
    main()
