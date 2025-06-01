# Zadanie 2

## Cel zadania

Celem zadania było opracować łańcuch (pipeline) w usłudzie GitHub Actions, który zbuduje obraz kontenera na podstawie Dockerfile-a oraz kodów źródłowych aplikacji opracowanej jako rozwiązanie zadania nr 1 a następnie prześle go do publicznego repozytorium autora na Github (ghcr.io).

Mimo to proces budowania obrazu powinien spełniać warunki:
- Wspiera dwie architektury: `linux/amd64` oraz `linux/arm64`
- Wykorzystuje cache warstw Docker BuildKit z rejestrem DockerHub (`mode=max`)
- Wykonuje skanowanie obrazu na obecność luk bezpieczeństwa (CVE)
- Wysyła obraz do publicznego rejestru kontenerów GitHub (`ghcr.io`)


## Konfiguracja i wykonanie

### 📁 Struktura repozytorium

```
.
├── app.py
├── Dockerfile
├── requirements.txt
├── .dockerignore
└── .github/
    └── workflows/
        └── docker.yml
```

### Plik workflow: `.github/workflows/docker.yml`

Workflow wykonuje następujące kroki:

#### 1. Pobranie kodu źródłowego z repozytorium
Pipeline rozpoczyna się od pobrania aktualnego stanu kodu z gałęzi, na której został uruchomiony.

```yaml
- name: Checkout repository
  uses: actions/checkout@v3
```

#### 2. Przygotowanie środowiska do budowy obrazów wieloarchitekturnych
Aktywowane są narzędzia QEMU i Docker Buildx, które umożliwiają budowanie obrazów na różne architektury (np. amd64, arm64) w ramach jednej akcji.

```yaml
- name: Set up QEMU
  uses: docker/setup-qemu-action@v2

- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v2
```

#### 3. Autoryzacja do DockerHub i GitHub Container Registry
Pipeline loguje się do dwóch rejestrów:
 - DockerHub – do wykorzystania i zapisu cache’a builda,
 - GHCR (ghcr.io) – do publikacji końcowego obrazu kontenera.

Dane logowania są przechowywane jako sekrety GitHub.

```yaml
- name: Log in to DockerHub
  uses: docker/login-action@v2
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}

- name: Log in to GitHub Container Registry
  uses: docker/login-action@v2
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

#### 4. Budowanie i publikowanie obrazu dla wielu architektur
W tej fazie tworzony jest obraz Dockera z wykorzystaniem Buildx. Obraz wspiera linux/amd64 oraz linux/arm64 i zostaje przesłany do GitHub Container Registry. Dodatkowo, podczas budowy wykorzystywany jest cache z DockerHub, co znacznie przyspiesza proces.

```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    context: .
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/${{ github.repository_owner }}/flask-app:latest
    cache-from: type=registry,ref=docker.io/${{ secrets.DOCKERHUB_USERNAME }}/cache:latest
    cache-to: type=registry,ref=docker.io/${{ secrets.DOCKERHUB_USERNAME }}/cache:latest,mode=max
```

#### 5. Skanowanie obrazu pod kątem zagrożeń bezpieczeństwa
Przy pomocy narzędzia Trivy obraz jest analizowany pod kątem podatności o poziomie HIGH i CRITICAL. Jeśli którakolwiek z nich zostanie wykryta, pipeline zostaje przerwany — obraz nie zostanie opublikowany.

```yaml
- name: Scan image with Trivy
  uses: aquasecurity/trivy-action@0.13.0
  with:
    image-ref: ghcr.io/${{ github.repository_owner }}/flask-app:latest
    severity: CRITICAL,HIGH
    exit-code: 1
```

#### 6. Zastosowanie cache warstw BuildKit
Mechanizm cache’owania wykorzystuje zewnętrzny rejestr DockerHub jako źródło i miejsce zapisu cache’a (type=registry, mode=max). To sprawia, że kolejne budowy są szybsze i bardziej zoptymalizowane.

```yaml
cache-from: type=registry,ref=docker.io/${{ secrets.DOCKERHUB_USERNAME }}/cache:latest
cache-to: type=registry,ref=docker.io/${{ secrets.DOCKERHUB_USERNAME }}/cache:latest,mode=max
```


### Sekrety wykorzystywane w GitHub Actions

W celu prawidłowego działania pipeline’a, w repozytorium skonfigurowane są dwa sekrety:
 - `DOCKERHUB_USERNAME` - nazwa konta DockerHub,
 - `DOCKERHUB_TOKEN` - access token z uprawnieniami RW

Są one używane do logowania się do rejestru w trakcie budowy i cache’owania obrazów.


### Walidacja działania pipeline’a

Workflow został poprawnie uruchomiony na gałęzi main. Proces zakończył się sukcesem, a zbudowany obraz został przesłany do:

[ghcr.io/chumakbogdan/flask-app:latest](https://github.com/chumakbogdan/PAwChO_LAB_OBW/pkgs/container/flask-app)

Wspierane architektury tego obrazu:
 - `linux/amd64`
 - `linux/arm64`


### System tagowania obrazów

Obecnie obraz oznaczany jest tagiem `:latest`, odpowiadającym najnowszej wersji.

Istnieje możliwość rozbudowy systemu tagowania np. o:
 - `:sha-<hash>` – identyfikator powiązany z konkretnym commitem Git,
 - `:v1.0.0` – wersjonowanie semantyczne, np. dla wydań produkcyjnych.


### Tagowanie i przechowywanie cache’a

Podczas budowy cache warstw Dockera zapisywany jest w publicznym repozytorium:
```
docker.io/chumakbogdan/cache:latest
```
Tryb `mode=max` zapewnia zachowanie maksymalnej liczby warstw, co pozwala na znaczące przyspieszenie kolejnych buildów i lepsze wykorzystanie cache’a.


## Podsumowanie

Spełnione wymagania:
 - Obraz wspiera dwie architektury: linux/arm64 oraz linux/amd64.
 - Wykorzystywane są (wysyłanie i pobieranie) dane cache (eksporter: registry oraz backend-u registry w trybie max).
 - Te dane cache są przechowywane w dedykowanym, publicznym repozytorium na DockerHub.
 - Jest wykonany test CVE obrazu, który zapewnia, że obraz zostanie przesłany do publicznego repozytorium obrazów na GitHub tylko wtedy gdy nie zawiera zagrożeń sklasyfikowanych jako krytyczne lub wysokie.

### Zrzut ekranu z `ghcr.io/chumakbogdan/flask-app:latest`

![zrzut GHCR](GHCR.png)