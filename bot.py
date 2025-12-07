import time
import os
import sys
import requests
from playwright.sync_api import sync_playwright


# ---------------------------------------------------------
# Helper: Safe env loader
# ---------------------------------------------------------
def get_env(key, required=True, default=None):
    value = os.getenv(key, default)
    if required and not value:
        print(f"❌ ERROR: Missing required environment variable: {key}")
        sys.exit(1)
    return value


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
print("🔵 bot.py starting…")
print("Python version:", sys.version)

SENDER = get_env("SENDER")
PASSWORD = get_env("PASSWORD")
RECEIVER = get_env("RECEIVER")
URL = get_env("URL")
KEYWORDS_RAW = get_env("KEYWORDS")
WEBHOOK = get_env("DISCORD_WEBHOOK")   # <-- THIS IS NOW REQUIRED
CHECK_INTERVAL = int(get_env("CHECK_INTERVAL", required=False, default="60"))

KEYWORDS = [kw.strip().lower() for kw in KEYWORDS_RAW.split(",")]

print("\n🔧 ENV loaded successfully!")
print("URL=", URL)
print("KEYWORDS=", KEYWORDS)
print("CHECK_INTERVAL=", CHECK_INTERVAL)
print("DISCORD_WEBHOOK=", WEBHOOK[:50] + "...")  # Hide full URL
print("------------------------------------------------------\n")


# ---------------------------------------------------------
# Send Discord Notification
# ---------------------------------------------------------
def send_discord(message):
    try:
        payload = { "content": message }
        r = requests.post(WEBHOOK, json=payload)
        print("📨 Discord status:", r.status_code)
    except Exception as e:
        print("❌ Discord error:", e)


# ---------------------------------------------------------
# Ticket Monitor
# ---------------------------------------------------------
def monitor():
    print("🚀 Launching Playwright…")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        print("🎉 Chromium launched successfully!")
        print("🚀 Ticket monitor started...\n")

        while True:
            try:
                page.goto(URL, wait_until="networkidle")
                time.sleep(2)

                body_text = page.inner_text("body").lower()

                for kw in KEYWORDS:
                    if kw in body_text:
                        msg = f"🔥 Keyword FOUND: {kw}\n🔗 {URL}"
                        print(msg)
                        send_discord(msg)

                print(f"⏳ Sleeping {CHECK_INTERVAL} seconds…\n")
                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print("⚠ Error:", e)
                time.sleep(10)


# ---------------------------------------------------------
# Start Bot
# ---------------------------------------------------------
if __name__ == "__main__":
    monitor()