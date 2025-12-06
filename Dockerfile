FROM mcr.microsoft.com/playwright/python:v1.43.0-focal

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "bot.py"]