import os
import sys
import time
import json
from urllib import request, error
from playwright.sync_api import sync_playwright


# ------------ helpers ------------

def get_env(name: str, required: bool = True, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if required and not value:
        print(f"❌ ERROR: Missing required environment variable: {name}")
        sys.stdout.flush()
        sys.exit(1)
    return value


# ------------ load env ------------

print("🔵 bot.py starting…")
print("Python version:", sys.version)

# Debug what the container actually has
print("DEBUG: DISCORD_WEBHOOK raw:", repr(os.getenv("DISCORD_WEBHOOK")))
print("DEBUG: ENV KEYS containing 'DISCORD':",
      [k for k in os.environ.keys() if "DISCORD" in k.upper()])

DISCORD_WEBHOOK = get_env("DISCORD_WEBHOOK", required=False) # <--- ADD required=False
URL = get_env("URL")
KEYWORDS_RAW = get_env("KEYWORDS")
CHECK_INTERVAL = int(get_env("CHECK_INTERVAL", required=False, default="60"))

KEYWORDS = [kw.strip().lower() for kw in KEYWORDS_RAW.split(",")]

print("🛠 ENV loaded successfully!")
print("URL =", URL)
print("KEYWORDS =", KEYWORDS)
print("CHECK_INTERVAL =", CHECK_INTERVAL)
print("---------------------------------------------")


# ------------ discord notifier ------------

def send_discord(message: str) -> None:
    payload = {"content": message}
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        DISCORD_WEBHOOK,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=10) as resp:
            print("📨 Discord status:", resp.status)
    except error.URLError as e:
        print("❌ Discord send failed:", e)


# ------------ monitor loop ------------

def monitor() -> None:
    print("🚀 Launching Playwright…")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        print("🎉 Chromium launched!")
        print("🚦 Starting monitor loop…")

        while True:
            try:
                page.goto(URL, wait_until="networkidle")
                time.sleep(2)

                body_text = page.inner_text("body").lower()

                for kw in KEYWORDS:
                    if kw in body_text:
                        msg = f"🔥 NPL alert: keyword '{kw}' found\n{URL}"
                        print(msg)
                        send_discord(msg)

                print(f"⏳ Checked page, sleeping {CHECK_INTERVAL}s\n")
                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print("⚠️ Error in monitor loop:", e)
                time.sleep(10)


if __name__ == "__main__":
    monitor()