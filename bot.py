import os
import sys
import time
import json
from urllib import request, error as urlerror

from playwright.sync_api import sync_playwright


# ---------------------------------------------------------
# 1. HELPER: Safe env getter
# ---------------------------------------------------------
def get_env(name: str, required: bool = True, default: str | None = None) -> str:
    """Read an env var, optionally require it."""
    value = os.getenv(name, default)
    if required and not value:
        print(f"❌ ERROR: Missing required environment variable: {name}")
        sys.stdout.flush()
        sys.exit(1)
    return value


# ---------------------------------------------------------
# 2. LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------
print("🔵 bot.py starting…")
print("Python version:", sys.version)

# Discord webhook (required)
print("DEBUG: DISCORD_WEBHOOK raw:", repr(os.getenv("DISCORD_WEBHOOK")))
DISCORD_WEBHOOK = get_env("DISCORD_WEBHOOK")

# Ticket-check config
URL = get_env("URL")
KEYWORDS_RAW = get_env("KEYWORDS")          # e.g. "Sudurpaschim,Karnali,Book Now"
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))

KEYWORDS = [kw.strip().lower() for kw in KEYWORDS_RAW.split(",") if kw.strip()]

print("\n🔧 ENV loaded successfully!")
print("URL =", URL)
print("KEYWORDS =", KEYWORDS)
print("CHECK_INTERVAL =", CHECK_INTERVAL)
print("------------------------------------------------------\n")


# ---------------------------------------------------------
# 3. DISCORD NOTIFICATION
# ---------------------------------------------------------
def send_discord(message: str) -> None:
    """Send a message to Discord via webhook."""
    try:
        payload = json.dumps({"content": message}).encode("utf-8")
        req = request.Request(
            DISCORD_WEBHOOK,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=10) as resp:
            # Discord usually returns 204 No Content on success
            if resp.status not in (200, 204):
                body = resp.read().decode("utf-8", errors="ignore")
                print(f"⚠️ Discord webhook returned {resp.status}: {body}")
        print("✅ Discord notification sent.")
    except urlerror.URLError as e:
        print("❌ Discord notification failed (URLError):", e)
    except Exception as e:
        print("❌ Discord notification failed:", e)


# ---------------------------------------------------------
# 4. MAIN MONITOR FUNCTION
# ---------------------------------------------------------
def monitor() -> None:
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
                        msg = f"Keyword FOUND: {kw}\nURL: {URL}"
                        print("🔥", msg)
                        send_discord(msg)

                print(f"⏳ Checked page — sleeping {CHECK_INTERVAL} seconds...\n")
                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print("⚠️ Error during monitoring:", e)
                # Avoid tight crash loops
                time.sleep(10)


# ---------------------------------------------------------
# 5. ENTRYPOINT
# ---------------------------------------------------------
if __name__ == "__main__":
    monitor()