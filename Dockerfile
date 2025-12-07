FROM mcr.microsoft.com/playwright/python:v1.56.0-jammy

WORKDIR /app

# Copy dependency list
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install required browsers (Railway often needs this!)
RUN playwright install --with-deps chromium

# Copy bot
COPY bot.py .

CMD ["python3", "bot.py"]