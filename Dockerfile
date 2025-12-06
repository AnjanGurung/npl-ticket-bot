FROM mcr.microsoft.com/playwright/python:v1.56.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

# Install browsers + dependencies
RUN playwright install --with-deps chromium

CMD ["python3", "bot.py"]