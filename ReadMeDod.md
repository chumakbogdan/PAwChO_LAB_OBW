
# Zadanie dodatkowe №2

## **0. Sprawdzenie obrazu na zagrozenia**
```
docker scout cves --only-severity critical,high chumakbogdan/zadanie1
```

### Wynik

```
                    │         Analyzed Image          
────────────────────┼─────────────────────────────────
  Target            │  chumakbogdan/zadanie1:latest   
    digest          │  7fb0904e27cc                   
    platform        │ linux/arm64                     
    vulnerabilities │    0C     0H     0M     0L      
    size            │ 34 MB                           
    packages        │ 70                              
```

## 1. **Skrypt budujący obraz multiarch**

```bash
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

```

## 2. **Manifest zawiera deklaracje dla dwóch platform**

Po zbudowaniu obrazu uruchomiono:
```bash
docker buildx imagetools inspect chumakbogdan/zadanie1:latest
```

Wynik potwierdził obecność dwóch platform:
```
Name:      docker.io/chumakbogdan/zadanie1:latest
MediaType: application/vnd.oci.image.index.v1+json
Digest:    sha256:0b1b889639903cd2e72148ae7884d489b3f43909a72103b43f532bdcc8373a4b
           
Manifests: 
  Name:        docker.io/chumakbogdan/zadanie1:latest@sha256:a3aa73181f9ee951dac94438010feec2f853119c0cb9ab5ea1e98b2a73fab7f6
  MediaType:   application/vnd.oci.image.manifest.v1+json
  Platform:    linux/amd64
               
  Name:        docker.io/chumakbogdan/zadanie1:latest@sha256:7fb0904e27ccb446f2a5fdc5ca1051e08e9cc01faa47e2f6d5c986db8b6bd69a
  MediaType:   application/vnd.oci.image.manifest.v1+json
  Platform:    linux/arm64
```

## 3. **Wykorzystanie cache w procesie budowy obrazu**

W trakcie budowania obrazu zastosowano cache z rejestru:

```bash
--cache-from type=registry,ref=chumakbogdan/zadanie1:buildcache
--cache-to type=registry,ref=chumakbogdan/zadanie1:buildcache,mode=max
```

### Potwierdzenie działania cache

W logach kompilacji widoczne były wpisy:

```
#5 CACHED
#6 CACHED
#7 CACHED
```

co oznacza, że cache został skutecznie użyty i znacznie przyspieszył proces budowy.

## Podsumowanie

	•	Obraz zgodny z OCI
	•	Obsługuje linux/amd64 i linux/arm64
	•	Użyto cache (registry + inline)
	•	Manifest zawiera poprawne wpisy
	•	Skrypt automatyzuje cały proces
