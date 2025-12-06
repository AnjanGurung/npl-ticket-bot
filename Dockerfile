# Use the latest Playwright image that matches the library version
FROM mcr.microsoft.com/playwright/python:v1.56.0-jammy

WORKDIR /app

# Copy dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your bot code
COPY bot.py .

# Start the bot
CMD ["python3", "bot.py"]
