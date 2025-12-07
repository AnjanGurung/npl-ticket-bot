import time
import os
import sys
from playwright.sync_api import sync_playwright
import smtplib
from email.mime.text import MIMEText

def log(msg):
    print(msg, flush=True)

def get_env(key, required=True, default=None):
    value = os.getenv(key, default)
    if required and not value:
        log(f"❌ ERROR: Missing required env var: {key}")
        sys.exit(1)
    return value

log("🔵 bot.py starting…")
log("Python version: " + sys.version)

SENDER = get_env("SENDER")
PASSWORD = get_env("PASSWORD")
RECEIVER = get_env("RECEIVER")
URL = get_env("URL")
KEYWORDS_RAW = get_env("KEYWORDS")
CHECK_INTERVAL = int(get_env("CHECK_INTERVAL", required=False, default="60"))

KEYWORDS = [k.strip().lower() for k in KEYWORDS_RAW.split(",")]

log("🔧 ENV loaded successfully!")
log(f"SENDER={SENDER}")
log(f"RECEIVER={RECEIVER}")
log(f"URL={URL}")
log(f"KEYWORDS={KEYWORDS}")
log(f"CHECK_INTERVAL={CHECK_INTERVAL}")

def send_email(message):
    try:
        email = MIMEText(message)
        email["From"] = SENDER
        email["To"] = RECEIVER
        email["Subject"] = "🔥 NPL Ticket Alert"

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER, PASSWORD)
            server.sendmail(SENDER, RECEIVER, email.as_string())

        log("📧 Email sent!")
    except Exception as e:
        log(f"❌ Email error: {e}")

def monitor():
    log("🚀 Launching Playwright")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        log("🎉 Chromium launched successfully!")

        while True:
            try:
                page.goto(URL, wait_until="networkidle")
                body = page.inner_text("body").lower()

                for kw in KEYWORDS:
                    if kw in body:
                        msg = f"🔥 KEYWORD FOUND: {kw}"
                        log(msg)
                        send_email(msg)

                log(f"⏳ Sleeping {CHECK_INTERVAL}s")
                time.sleep(CHECK_INTERVAL)
            except Exception as e:
                log(f"⚠️ Runtime Error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    monitor()