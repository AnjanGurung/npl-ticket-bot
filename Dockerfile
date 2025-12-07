FROM mcr.microsoft.com/playwright/python:v1.56.0-jammy

# Work inside /app
WORKDIR /app

# 1) Install Python deps (includes playwright)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 2) Install browsers + OS deps for Chromium
RUN playwright install --with-deps chromium

# 3) Copy your bot code
COPY bot.py /app/bot.py

# 4) Run the bot
CMD ["python3", "/app/bot.py"]