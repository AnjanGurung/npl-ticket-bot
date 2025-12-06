FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Install Chromium browser
RUN playwright install chromium

CMD ["python3", "bot.py"]
