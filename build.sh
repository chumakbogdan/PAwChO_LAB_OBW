#!/bin/bash

# Utwórz builder o nazwie "multiarch-builder" jeśli nie istnieje
docker buildx create --use --name multiarch-builder --driver docker-container || docker buildx use multiarch-builder

# Włącz eksport do cache oraz multiplatform
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --cache-from=type=registry,ref=chumakbogdan/zadanie1:cache \
  --cache-to=type=inline \
  --push \
  -t chumakbogdan/zadanie1:latest .

# Sprawdzenie manifestu
echo "=== Manifest ==="
docker buildx imagetools inspect chumakbogdan/zadanie1:latest