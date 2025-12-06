import time
from playwright.sync_api import sync_playwright
import smtplib
from email.mime.text import MIMEText

URL = "https://events.khalti.com/events/ET25AMY4AUYM?sub_event=true"
KEYWORDS = ["Sudurpaschim", "Karnali", "Book Now"]

SENDER = "anjangurung1995@gmail.com"
PASSWORD = "yocqeyqbvwtwpgmx"   # your Google App Password
RECEIVER = "anjangurung1995@gmail.com"

CHECK_INTERVAL = 60  # 1 minute


def send_email(msg):
    email = MIMEText(msg)
    email["From"] = SENDER
    email["To"] = RECEIVER
    email["Subject"] = "🔥 NPL Ticket Alert"

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(SENDER, PASSWORD)
    server.sendmail(SENDER, RECEIVER, email.as_string())
    server.quit()


def monitor():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("🚀 Ticket monitor started on Railway")

        while True:
            page.goto(URL, wait_until="networkidle")
            time.sleep(3)

            text = page.inner_text("body").lower()

            for kw in KEYWORDS:
                if kw.lower() in text:
                    msg = f"Keyword '{kw}' found!\nURL: {URL}"
                    print(msg)
                    send_email(msg)

            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    monitor()