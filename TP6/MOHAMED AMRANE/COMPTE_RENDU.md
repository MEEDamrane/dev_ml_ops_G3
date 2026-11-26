# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :** à compléter  ·  **Membres :** à compléter  ·  **Date :** 26/11/2026

---

## 1. Mise en place (dans `TP/TP6`)

Sortie de `docker run hello-world` et de `docker version` :

```
Hello from Docker!
Client: Docker Engine - Community, version 29.6.2
Server: Docker Desktop 4.84.0 (Engine 29.6.2)
```

Dernière ligne de `python -m pytest` :

```
38 passed, 5 warnings in 72.23s (0:01:12)
```

## 2. Image et conteneur (pendant le premier build)

1. Une image est un modèle immuable contenant le code, les dépendances et la commande de démarrage. Un conteneur est une instance en cours d'exécution de cette image, avec son propre processus, son réseau et une couche d'écriture temporaire.
2. `COPY requirements-docker.txt` est placé avant `COPY maintai` pour que Docker réutilise la couche d'installation des dépendances tant que les exigences ne changent pas. Une modification du code invalide alors seulement les couches suivantes.
3. `scikit-learn==1.8.0` garantit la compatibilité avec le modèle sérialisé et rend le build reproductible. Avec `>=1.5`, une future version pourrait casser le chargement ou modifier les prédictions.
4. `mlflow`, `dvc` et `pytest` servent au suivi, à la gestion des données et aux tests, pas à l'inférence. Les exclure réduit la taille de l'image, le temps de téléchargement et la surface d'attaque.

## 3. Sprint 1 : le Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY maintai maintai
COPY ui ui

ENV MAINTAI_MODELS_DIR=/app/models \
    MAINTAI_DATA_PATH=/app/data/sensors.csv

EXPOSE 8000

CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

| Build | Durée | Taille de l'image (`docker images`) |
|---|---:|---:|
| premier build | non relevée | 1,13 Go sur disque (259 Mo de contenu) |
| après une modification de `maintai/predict.py` | non relevée | 1,13 Go sur disque (259 Mo de contenu) |

Les durées n'ont pas été enregistrées au moment des builds et ne peuvent pas être reconstruites fidèlement après coup.

`CACHED` signifie que Docker a trouvé une couche précédente dont l'instruction et les fichiers d'entrée n'ont pas changé. Il la réutilise sans réexécuter l'étape, notamment l'installation des dépendances.

## 4. Sprint 1 : lancer un conteneur

```powershell
docker run --rm --name test -p 8002:8000 --env-file .env -v "${PWD}/models:/app/models:ro" maintai:0.4.0
```

| Essai | Réponse |
|---|---|
| `GET /health` | `200 {"status":"ok","model_loaded":true}` |
| `POST /v1/predict` sans clé | `401 {"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict` avec la clé | `200 {"failure_probability":0.9553,"alert":true,"threshold":0.3,"model_version":"2026-11-26T09:47:26Z"}` |

**Piège 1.** Sans le volume du modèle, `/health` répond `200` avec `model_loaded: false`, car le modèle est exclu de l'image. `/v1/predict` répond `503 Service Unavailable`, car l'API démarre mais ne peut pas charger le modèle.

**Piège 2.** Avec `--host 127.0.0.1`, les logs indiquent qu'Uvicorn écoute sur `http://127.0.0.1:8000`, mais `http://localhost:8002/health` est inaccessible. Dans le conteneur, `127.0.0.1` désigne seulement sa boucle locale ; il faut `0.0.0.0` pour recevoir le trafic du port publié.

## 5. Sprint 2 : Docker Compose

```yaml
services:
  api:
    build: .
    image: maintai:0.4.0
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models:ro

  ui:
    image: maintai:0.4.0
    command: ["python", "-m", "streamlit", "run", "ui/app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
    environment:
      MAINTAI_API_URL: http://api:8000
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data:ro
    depends_on:
      - api
```

Sortie de `docker compose ps` :

```
NAME        IMAGE           SERVICE   STATUS         PORTS
tp6-api-1   maintai:0.4.0   api       Up 6 minutes   0.0.0.0:8000->8000/tcp
tp6-ui-1    maintai:0.4.0   ui        Up 6 minutes   0.0.0.0:8501->8501/tcp
```

La barre latérale affiche `http://api:8000`. Cette valeur vient de `MAINTAI_API_URL` dans `compose.yaml`, lue avec `os.getenv` dans `ui/app.py`. Le nom `api` est résolu par le réseau interne de Docker Compose.

```
$ docker compose exec ui python -c "import httpx; r=httpx.get('http://api:8000/health'); print(r.status_code, r.text)"
200 {"status":"ok","model_loaded":true}

$ docker compose exec ui python -c "import httpx; r=httpx.get('http://localhost:8000/health'); print(r.status_code, r.text)"
httpx.ConnectError: [Errno 111] Connection refused
```

La seconde commande échoue car, depuis `ui`, `localhost` désigne le conteneur `ui` lui-même. L'API tourne dans un autre conteneur et doit être jointe avec le nom de service `api`.

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
38 passed, 5 warnings in 72.23s (0:01:12)
```

## 6. Décision : l'ADR 005

Nous choisissons une image d'inférence légère et reproductible, avec des dépendances figées, contenant le code de l'API et de l'interface mais ni données, ni modèle, ni secret. Le modèle et les données sont montés en lecture seule au lancement, tandis que la clé API est injectée par variable d'environnement afin de changer ces éléments sans reconstruire l'image.

## 7. Questions de compréhension

1. L'image reçoit la base Python avec `FROM`, les bibliothèques avec `COPY requirements-docker.txt` puis `RUN pip install`, et le code avec `COPY maintai` et `COPY ui`. Au lancement, le modèle et les données arrivent par des volumes en lecture seule, la clé par `env_file: .env`, et l'URL de l'API par `MAINTAI_API_URL`.
2. Une image peut être partagée et inspectée couche par couche : une clé copiée dedans resterait récupérable. L'injection au lancement permet aussi de changer ou révoquer la clé sans reconstruire l'image.
3. Docker ajoute un environnement d'exécution reproductible : image de base, version de Python, dépendances figées, code du service, commande de démarrage, ports, configuration et montages des artefacts. Il faut aussi garantir la compatibilité entre la version de scikit-learn d'entraînement et celle de l'image.

## 8. Le rendu Git

- Lien de la pull request : à compléter
- Le tag `tp6` existe sur GitHub : non vérifiable dans cette copie (aucun dépôt `.git` à la racine)
- `git status` avant le commit : non vérifiable après coup ; selon `.gitignore`, `.env`, `models/` et `data/*.csv` ne doivent pas apparaître

## 9. Ce qui reste flou

Il reste à relever les durées lors d'un vrai premier build puis d'un second build après modification de `maintai/predict.py`. Il faut aussi compléter le groupe, les membres, le lien de la pull request et la présence du tag depuis le véritable dépôt Git.
