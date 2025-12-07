FROM mcr.microsoft.com/playwright/python:v1.56.0-jammy

WORKDIR /app

# Copy dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install Chromium
RUN playwright install --with-deps chromium

# Copy bot code
COPY bot.py /app/bot.py

CMD ["python3", "/app/bot.py"]