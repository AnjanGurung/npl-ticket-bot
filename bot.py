import os
import sys
import time
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright


# ---------------------------------------------------------
# 1. HELPER: Safe env getter
# ---------------------------------------------------------
def get_env(key, required=True, default=None):
    value = os.getenv(key, default)
    if required and (value is None or value == ""):
        print(f"❌ ERROR: Missing required environment variable: {key}", flush=True)
        sys.exit(1)
    return value


# ---------------------------------------------------------
# 2. LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------
print("🔵 BOT.PY HAS STARTED EXECUTING", flush=True)
print("Python version:", sys.version, flush=True)

# Read env vars from Railway
SENDER = get_env("SENDER")
PASSWORD = get_env("PASSWORD")
RECEIVER = get_env("RECEIVER")
URL = get_env("URL")
KEYWORDS_RAW = get_env("KEYWORDS")
CHECK_INTERVAL = int(get_env("CHECK_INTERVAL", required=False, default="60"))

# Normalise keywords
KEYWORDS = [kw.strip().lower() for kw in KEYWORDS_RAW.split(",") if kw.strip()]

print("\n🔧 DEBUG ENVIRONMENT LOADED", flush=True)
print("SENDER:", SENDER, flush=True)
print("RECEIVER:", RECEIVER, flush=True)
print("URL:", URL, flush=True)
print("KEYWORDS_RAW:", KEYWORDS_RAW, flush=True)
print("KEYWORDS:", KEYWORDS, flush=True)
print("CHECK_INTERVAL:", CHECK_INTERVAL, flush=True)
print("------------------------------------------------------\n", flush=True)


# ---------------------------------------------------------
# 3. EMAIL SENDING FUNCTION
# ---------------------------------------------------------
def send_email(message: str) -> None:
    try:
        email = MIMEText(message)
        email["From"] = SENDER
        email["To"] = RECEIVER
        email["Subject"] = "🔥 NPL Ticket Alert"

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER, PASSWORD)
            server.sendmail(SENDER, RECEIVER, email.as_string())

        print("📧 Email sent successfully!", flush=True)
    except Exception as e:
        print("❌ Email sending failed:", e, flush=True)


# ---------------------------------------------------------
# 4. MAIN MONITOR FUNCTION
# ---------------------------------------------------------
def monitor() -> None:
    print("🚀 Launching Playwright…", flush=True)

    with sync_playwright() as pw:
        # Launch Chromium headless
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        print("🎉 Chromium launched successfully!", flush=True)
        print("🚀 Ticket monitor started...\n", flush=True)

        while True:
            try:
                page.goto(URL, wait_until="networkidle")
                time.sleep(2)

                body_text = page.inner_text("body").lower()

                matched = False
                for kw in KEYWORDS:
                    if kw in body_text:
                        matched = True
                        msg = f"Keyword FOUND: {kw}\nURL: {URL}"
                        print("🔥", msg, flush=True)
                        send_email(msg)

                if not matched:
                    print("😴 No keywords found this round.", flush=True)

                print(f"⏳ Checked page — waiting {CHECK_INTERVAL} seconds...\n", flush=True)
                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print("⚠️ Error during monitoring:", e, flush=True)
                # Sleep a bit before retrying to avoid crash loops
                time.sleep(10)


# ---------------------------------------------------------
# 5. START
# ---------------------------------------------------------
if __name__ == "__main__":
    try:
        monitor()
    except Exception as e:
        print("💥 FATAL ERROR in monitor():", e, flush=True)
        # Keep the container alive long enough to see logs
        time.sleep(60)
        raise
