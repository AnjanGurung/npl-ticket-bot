import os
import sys
import time
import json
from urllib import request, error
from playwright.sync_api import sync_playwright


# ---------------------------------------------------------
# 1. Helper to read env vars
# ---------------------------------------------------------
def get_env(name: str, required: bool = True, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if required and not value:
        print(f"❌ ERROR: Missing required environment variable: {name}")
        sys.stdout.flush()
        sys.exit(1)
    return value


# ---------------------------------------------------------
# 2. Load configuration
# ---------------------------------------------------------
print("🔵 bot.py starting…")
print("Python version:", sys.version)

DISCORD_WEBHOOK = get_env("DISCORD_WEBHOOK")
SENDER = get_env("SENDER", required=False, default="npl-ticket-bot")
RECEIVER = get_env("RECEIVER", required=False, default="discord")
URL = get_env("URL")
KEYWORDS_RAW = get_env("KEYWORDS")
CHECK_INTERVAL = int(get_env("CHECK_INTERVAL", required=False, default="60"))

KEYWORDS = [kw.strip().lower() for kw in KEYWORDS_RAW.split(",") if kw.strip()]

print("🛠 ENV loaded successfully!")
print("DISCORD_WEBHOOK set:", bool(DISCORD_WEBHOOK))
print("URL:", URL)
print("KEYWORDS:", KEYWORDS)
print("CHECK_INTERVAL:", CHECK_INTERVAL)
print("------------------------------------------------------")
sys.stdout.flush()


# ---------------------------------------------------------
# 3. Discord notification
# ---------------------------------------------------------
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
            # read to force the request to complete
            resp.read()
        print("✅ Discord message sent")
    except error.HTTPError as e:
        print(f"❌ Discord HTTP error: {e.code} {e.reason}")
    except error.URLError as e:
        print(f"❌ Discord network error: {e.reason}")
    except Exception as e:
        print("❌ Discord unknown error:", e)

    sys.stdout.flush()


# ---------------------------------------------------------
# 4. Main monitor loop
# ---------------------------------------------------------
def monitor() -> None:
    print("🚀 Launching Playwright…")
    sys.stdout.flush()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        print("🎉 Chromium launched successfully!")
        print("🚀 Ticket monitor started…")
        sys.stdout.flush()

        while True:
            try:
                page.goto(URL, wait_until="networkidle")
                time.sleep(2)

                body_text = page.inner_text("body").lower()

                found_any = False
                for kw in KEYWORDS:
                    if kw in body_text:
                        print(f"🔥 KEYWORD FOUND: {kw}")
                        msg = f"🔥 NPL Ticket Alert\nKeyword: **{kw}**\nURL: {URL}"
                        send_discord(msg)
                        found_any = True

                if not found_any:
                    print("⌛ No keywords found this round.")

                print(f"🕒 Sleeping {CHECK_INTERVAL} seconds…")
                print("------------------------------------------------------")
                sys.stdout.flush()
                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print("⚠️ Error during monitor loop:", e)
                sys.stdout.flush()
                time.sleep(10)


# ---------------------------------------------------------
# 5. Entry point
# ---------------------------------------------------------
if __name__ == "__main__":
    monitor()