# Etap 1: Build dependencies
FROM python:3.11-alpine AS builder

WORKDIR /app

# Instalacja zależności systemowych (dla C-extensions)
RUN apk add --no-cache build-base libffi-dev

COPY requirements.txt .

# Instalacja zależności do katalogu tymczasowego
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Etap 2: finalny, ultralekki obraz
FROM python:3.11-alpine

LABEL org.opencontainers.image.authors="Bahdan Chumak"

WORKDIR /app

# Tylko potrzebne zależności (z /install z poprzedniego etapu)
COPY --from=builder /install /usr/local

# Kopiujemy aplikację
COPY app.py .

# Zmniejszenie warstw, usunięcie cache
RUN adduser -D appuser && chown -R appuser /app
USER appuser

# Port aplikacji
EXPOSE 5001

# Healthcheck (opcjonalny)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:5001/ || exit 1

CMD ["python", "app.py"]