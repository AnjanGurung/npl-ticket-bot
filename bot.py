import time
import os
import sys
from playwright.sync_api import sync_playwright
import smtplib
from email.mime.text import MIMEText   # ✅ fixed: mime.text, not mime_text


def get_env(key, required=True, default=None):
    value = os.getenv(key, default)
    if required and not value:
        print(f"❌ ERROR: Missing required environment variable: {key}")
        sys.exit(1)
    return value


print("🔵 BOT.PY HAS STARTED EXECUTING")
print("Python version:", sys.version)

SENDER = get_env("SENDER")
PASSWORD = get_env("PASSWORD")
RECEIVER = get_env("RECEIVER")
URL = get_env("URL")
KEYWORDS_RAW = get_env("KEYWORDS")
CHECK_INTERVAL = int(get_env("CHECK_INTERVAL", required=False, default="60"))

KEYWORDS = [kw.strip().lower() for kw in KEYWORDS_RAW.split(",")]

print("\n🔧 DEBUG ENVIRONMENT LOADED")
print("SENDER:", SENDER)
print("RECEIVER:", RECEIVER)
print("URL:", URL)
print("KEYWORDS:", KEYWORDS)
print("CHECK_INTERVAL:", CHECK_INTERVAL)
print("------------------------------------------------------\n")


def send_email(message):
    try:
        email = MIMEText(message)
        email["From"] = SENDER
        email["To"] = RECEIVER
        email["Subject"] = "🔥 NPL Ticket Alert"

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER, PASSWORD)
            server.sendmail(SENDER, RECEIVER, email.as_string())

        print("📧 Email sent successfully!")
    except Exception as e:
        print("❌ Email sending failed:", e)


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
                        msg = f"Keyword FOUND: {kw}\nURL: {URL}"
                        print("🔥", msg)
                        send_email(msg)

                print(f"⏳ Checked page — waiting {CHECK_INTERVAL} seconds...\n")
                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print("⚠️ Error during monitoring:", e)
                time.sleep(10)


if __name__ == "__main__":
    monitor()