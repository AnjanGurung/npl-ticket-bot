FROM mcr.microsoft.com/playwright/python:v1.56.0-jammy

WORKDIR /app

# Copy dependency list
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install browsers + deps
RUN playwright install --with-deps chromium

# Copy bot code
COPY bot.py /app/bot.py

# Run Python unbuffered so logs appear immediately
CMD ["python", "-u", "bot.py"]