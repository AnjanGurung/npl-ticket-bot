import time
import os
from playwright.sync_api import sync_playwright
import smtplib
from email.mime.text import MIMEText


# ----------------------------
# Load Environment Variables
# ----------------------------

SENDER = os.getenv("SENDER")
PASSWORD = os.getenv("PASSWORD")
RECEIVER = os.getenv("RECEIVER")
URL = os.getenv("URL")
KEYWORDS = os.getenv("KEYWORDS").split(",")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))  # default: 60 seconds


# ----------------------------
# Email Sending Function
# ----------------------------

def send_email(message):
    msg = MIMEText(message)
    msg["From"] = SENDER
    msg["To"] = RECEIVER
    msg["Subject"] = "🔥 NPL Ticket Alert"

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER, PASSWORD)
        server.sendmail(SENDER, RECEIVER, msg.as_string())


# ----------------------------
# Ticket Monitor
# ----------------------------

def monitor():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        print("🚀 Railway NPL Ticket Bot Started…")

        while True:
            try:
                page.goto(URL, wait_until="networkidle")
                time.sleep(2)

                text = page.inner_text("body").lower()

                for kw in KEYWORDS:
                    if kw.lower().strip() in text:
                        alert_msg = f"Keyword FOUND: {kw}\nURL: {URL}"
                        print(alert_msg)
                        send_email(alert_msg)

                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print("Error:", e)
                time.sleep(10)  # prevent crash loop


# ----------------------------
# Start Bot
# ----------------------------

if __name__ == "__main__":
    monitor()
