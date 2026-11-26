# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :** G  ·  **Membres :** …  ·  **Date :** 26/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP6.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP6`)

Sortie de `docker run hello-world` (première ligne) et de `docker version` (lignes Client et Server) :

```
Hello from Docker!

Client: 29.8.2
Server: Docker Desktop 4.95.0 (242831) — Engine 29.8.2
```

Dernière ligne de `python -m pytest` après la mise en place :

```
7 failed, 31 passed, 2 warnings in 90.20s (0:01:30)
```

(Les 7 échecs : les 5 tests Docker, normal avant le TP, et les 2 tests du package, corrigés par `pip install -e .`.)

## 2. Image et conteneur (pendant le premier build)

1. Quelle différence entre une image et un conteneur ?
   L'image est un modèle figé en lecture seule : le système, Python, les bibliothèques et le code. Le conteneur est une instance de cette image en cours d'exécution, avec son propre processus, son réseau et une couche modifiable. Une même image peut lancer plusieurs conteneurs : ici `api` et `ui` viennent tous les deux de `maintai:0.4.0`.
2. Pourquoi `COPY requirements-docker.txt` est-il placé avant `COPY maintai` ?
   Docker met chaque étape en cache et ne refait que les étapes qui suivent un changement. Le code change souvent, la liste des bibliothèques rarement. En installant les bibliothèques avant de copier le code, l'étape lente `pip install` reste en cache quand on modifie seulement le code : le build passe de 85 s à 4 s (voir partie 3).
3. Pourquoi `requirements-docker.txt` contient-il `scikit-learn==1.8.0` et pas `scikit-learn>=1.5` ?
   Le modèle `model.joblib` a été écrit par scikit-learn 1.8.0. Un fichier joblib n'est garanti lisible que par la même version. Avec `>=1.5`, un build plus tard pourrait installer une autre version, et l'image ne pourrait plus charger le modèle ou donnerait d'autres prédictions. Figer la version rend le build reproductible.
4. Pourquoi ni `mlflow`, ni `dvc`, ni `pytest` dans l'image ?
   L'image sert seulement à faire tourner l'API et l'interface. On n'y entraîne pas de modèle (MLflow), on n'y versionne pas les données (DVC) et on n'y lance pas les tests (pytest). Les ajouter alourdirait l'image et ajouterait des dépendances, donc des failles possibles, pour rien.

## 3. Sprint 1 : le Dockerfile

Votre `Dockerfile` :

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY maintai ./maintai
COPY ui ./ui

ENV MAINTAI_MODELS_DIR=/app/models \
    MAINTAI_DATA_PATH=/app/data/sensors.csv

EXPOSE 8000
CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

| Build | Durée | Taille de l'image (`docker images`) |
|---|---|---|
| premier build | 85 s (`--no-cache`, image `python:3.11-slim` déjà téléchargée ; l'étape `pip install` seule prend environ 1 min 30 au tout premier build) | 1.13 GB |
| après une modification de `maintai/predict.py` | 4 s | 1.13 GB |

Que signifie `CACHED` dans le journal du second build ?

Docker n'a pas refait l'étape : il a réutilisé la couche calculée au build précédent, parce que rien n'a changé avant ni dans cette étape. Au second build, `WORKDIR`, `COPY requirements-docker.txt` et `RUN pip install` sont `CACHED`. Seuls `COPY maintai` (le fichier a changé) et `COPY ui` (qui vient après) sont refaits :

```
#8 [4/6] RUN pip install --no-cache-dir -r requirements-docker.txt
#8 CACHED
#9 [5/6] COPY maintai ./maintai
#9 DONE 0.1s
```

## 4. Sprint 1 : lancer un conteneur

Votre commande `docker run` :

```
docker run -d --name test -p 8002:8000 --env-file .env -v "C:/Users/hp/Desktop/TP6/models:/app/models:ro" maintai:0.4.0
```

| Essai | Réponse |
|---|---|
| `GET /health` | 200 `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict` sans clé | 401 `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict` avec la clé | 200 `{"failure_probability":0.9908,"alert":true,"threshold":0.3,"model_version":"2026-11-26T09:38:03Z"}` |

**Piège 1.** Sans l'option `-v ...models...`, que répondent `/health` et `/v1/predict` ? Pourquoi ?

`/health` répond 200 `{"status":"ok","model_loaded":false}` et `/v1/predict` répond 503 `{"detail":"Modèle non chargé : lancez python -m maintai.train puis redémarrez l'API"}`. Le dossier `models/` est exclu de l'image par `.dockerignore` : le modèle doit être monté depuis le PC au lancement. Sans le volume, `/app/models` est vide. L'API démarre quand même, car elle intercepte le `FileNotFoundError`, mais elle n'a aucun modèle pour prédire.

**Piège 2.** Avec `--host 127.0.0.1`, que disent `docker logs test` et `http://localhost:8002/health` ? Pourquoi ?

`docker logs test` affiche un démarrage normal : `Uvicorn running on http://127.0.0.1:8000`. Mais `http://localhost:8002/health` ne répond pas : curl échoue avec l'erreur 52 (réponse vide). `127.0.0.1` est l'adresse locale du conteneur lui-même. Les requêtes du PC arrivent par l'interface réseau du conteneur, pas par cette adresse, donc l'API ne les reçoit jamais. Avec `0.0.0.0`, elle écoute sur toutes les interfaces, dont celle où Docker redirige le port.

## 5. Sprint 2 : Docker Compose

Votre `compose.yaml` :

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
    command: ["python", "-m", "streamlit", "run", "ui/app.py",
              "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
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
NAME        IMAGE           COMMAND                  SERVICE   CREATED          STATUS          PORTS
tp6-api-1   maintai:0.4.0   "uvicorn maintai.api…"   api       13 minutes ago   Up 13 minutes   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
tp6-ui-1    maintai:0.4.0   "python -m streamlit…"   ui        13 minutes ago   Up 13 minutes   0.0.0.0:8501->8501/tcp, [::]:8501->8501/tcp
```

Quelle URL affiche la barre latérale de l'interface ? D'où vient-elle ?

`http://api:8000`. Elle vient de la variable d'environnement `MAINTAI_API_URL`, définie dans `compose.yaml` pour le service `ui` et lue par `ui/app.py` avec `os.getenv("MAINTAI_API_URL", "http://localhost:8000")`. Hors Docker, la variable n'existe pas et l'interface garde `http://localhost:8000`.

Résultat des deux commandes `docker compose exec ui ...` (avec `api` puis avec `localhost`). Pourquoi la seconde échoue-t-elle ?

```
$ docker compose exec ui python -c "import httpx; print(httpx.get('http://api:8000/health').text)"
{"status":"ok","model_loaded":true}

$ docker compose exec ui python -c "import httpx; print(httpx.get('http://localhost:8000/health').text)"
httpx.ConnectError: [Errno 111] Connection refused
```

Dans le conteneur `ui`, `localhost` désigne le conteneur `ui` lui-même, et rien n'y écoute sur le port 8000 : l'API tourne dans un autre conteneur. Compose relie les services par un réseau commun où chacun est joignable par son nom de service. Il faut donc appeler `api:8000`.

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
38 passed, 2 warnings in 103.93s (0:01:43)
```

## 6. Décision : l'ADR 005

Dans `docs/adr/005-image-docker.md`. Résumez ici votre décision en deux phrases :

On construit une seule image `maintai:0.4.0`, basée sur `python:3.11-slim` avec des bibliothèques aux versions figées. Elle sert à la fois l'API et l'interface, avec deux commandes différentes dans Compose. Le modèle, les données et la clé API ne sont jamais dans l'image : ils arrivent au lancement par des volumes en lecture seule et par `env_file`, ce qui permet de changer de modèle ou de clé sans reconstruire l'image.

## 7. Questions de compréhension

1. Qu'est-ce qui entre dans l'image, et qu'est-ce qui arrive au lancement ? Donnez le moyen pour chaque élément.
   - **Dans l'image, au build** : Python 3.11 (`FROM`), les bibliothèques (`COPY requirements-docker.txt` puis `RUN pip install`), le code `maintai/` et `ui/` (`COPY`), les chemins par défaut (`ENV`) et la commande de démarrage (`CMD`).
   - **Au lancement** : le modèle (volume `./models:/app/models:ro`), les données (volume `./data:/app/data:ro`), la clé API (`--env-file .env` ou `env_file: .env`), l'adresse de l'API pour l'interface (`environment: MAINTAI_API_URL`) et les ports (`-p` ou `ports`).
2. Pourquoi la clé API n'est-elle jamais dans l'image ?
   Une image se partage : on la pousse sur un registre, on la donne à d'autres. N'importe qui l'ayant récupérée pourrait lire la clé dans ses couches, même si on la supprime dans une étape suivante. Changer la clé obligerait aussi à reconstruire l'image. La clé reste donc dans `.env`, exclu de l'image par `.dockerignore` et de Git par `.gitignore`, et elle est injectée au lancement.
3. Livrer un modèle (TP4, TP5) : qu'est-ce que Docker ajoute à la liste ?
   Le TP4 livrait le code en package avec ses versions, le TP5 suivait les entraînements (MLflow) et les données (DVC). Docker ajoute l'environnement d'exécution complet : le système et la version de Python, figés dans l'image. Le modèle tourne de la même façon sur n'importe quelle machine qui a Docker, en une commande (`docker compose up`), sans installer Python ni les bibliothèques. Il ajoute aussi une séparation nette entre ce qui est figé (l'image) et ce qui est fourni au lancement (modèle, données, secrets).

## 8. Le rendu Git

- Lien de la pull request : …
- Le tag `tp6` existe sur GitHub : oui / non
- `git status` avant le commit : `.env`, `models/` ou `data/*.csv` apparaissaient-ils ? oui / non

## 9. Ce qui reste flou

…
