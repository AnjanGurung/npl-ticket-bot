import time
import os
import sys
import requests
from playwright.sync_api import sync_playwright

# ---------------------------------------------------------
# 1. HELPER: Safe env getter
# ---------------------------------------------------------
def get_env(key, required=True, default=None):
    value = os.getenv(key, default)
    if required and not value:
        print(f"❌ ERROR: Missing required environment variable: {key}")
        sys.exit(1)
    return value


# ---------------------------------------------------------
# 2. LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------
print("🔵 bot.py starting…")
print("Python version:", sys.version)

URL = get_env("URL")
KEYWORDS_RAW = get_env("KEYWORDS")
CHECK_INTERVAL = int(get_env("CHECK_INTERVAL", required=False, default="60"))
WEBHOOK = get_env("DISCORD_WEBHOOK")

KEYWORDS = [kw.strip().lower() for kw in KEYWORDS_RAW.split(",")]

print("\n🔧 ENV loaded successfully!")
print("URL =", URL)
print("KEYWORDS =", KEYWORDS)
print("CHECK_INTERVAL =", CHECK_INTERVAL)
print("DISCORD_WEBHOOK =", WEBHOOK)
print("------------------------------------------------------\n")


# ---------------------------------------------------------
# 3. DISCORD NOTIFICATION FUNCTION
# ---------------------------------------------------------
def send_discord(message):
    try:
        payload = {"content": message}
        r = requests.post(WEBHOOK, json=payload)

        if r.status_code == 204:
            print("📩 Discord alert sent!")
        else:
            print("⚠️ Discord response:", r.text)

    except Exception as e:
        print("❌ Failed to send Discord alert:", e)


# ---------------------------------------------------------
# 4. MAIN MONITOR FUNCTION
# ---------------------------------------------------------
def monitor():
    print("🚀 Launching Playwright…")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        print("🎉 Chromium launched successfully!")
        print("🚀 Ticket monitoring started...\n")

        while True:
            try:
                page.goto(URL, wait_until="networkidle")
                time.sleep(2)

                body_text = page.inner_text("body").lower()

                for kw in KEYWORDS:
                    if kw in body_text:
                        msg = f"🔥 KEYWORD FOUND: **{kw}**\n🔗 {URL}"
                        print(msg)
                        send_discord(msg)

                print(f"⏳ Checked page — sleeping {CHECK_INTERVAL}s...\n")
                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print("⚠️ Error:", e)
                time.sleep(10)


# ---------------------------------------------------------
# 5. START
# ---------------------------------------------------------
if __name__ == "__main__":
    monitor()