FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

ENV PYTHONUNBUFFERED=1
ENV PYTHONUTF8=1
ENV YOUTUBE_TIMEOUT=30
ENV HTTP_PROXY=""
ENV HTTPS_PROXY=""

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-keep-alive", "75"]
