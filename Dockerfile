FROM mcr.microsoft.com/playwright/python:v1.56.0-jammy

# Work in /app
WORKDIR /app

# Copy only the bot code (no requirements step needed!)
COPY bot.py .

# Run Python in unbuffered mode so logs show up immediately
CMD ["python", "-u", "bot.py"]