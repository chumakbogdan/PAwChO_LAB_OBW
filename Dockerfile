# Etap 1: Build dependencies
FROM python:3.11-alpine AS builder

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache build-base libffi-dev
RUN pip install --upgrade setuptools==70.0.0
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Etap 2: Finalny, ultralekki obraz
FROM python:3.11-alpine

LABEL org.opencontainers.image.authors="Bahdan Chumak"
LABEL org.opencontainers.image.title="zadanie1-flask-app"
LABEL org.opencontainers.image.description="Flask app for Docker Lab task 1 & 2"
LABEL org.opencontainers.image.version="1.0.0"

WORKDIR /app

RUN pip install --upgrade pip setuptools==70.0.0

COPY --from=builder /install /usr/local

COPY app.py .
COPY requirements.txt .

RUN adduser -D appuser && chown -R appuser /app
USER appuser

EXPOSE 5001

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:5001/ || exit 1

CMD ["python", "app.py"]