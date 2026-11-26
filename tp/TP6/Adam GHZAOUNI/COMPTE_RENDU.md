# Compte rendu · TP6 : conteneuriser MaintAI (Docker, Docker Compose)

**Groupe :** À COMPLÉTER  ·  **Membres :** À COMPLÉTER  ·  **Date :** 26/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP6.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP6`)

Sortie de `docker run hello-world` (première ligne) et de `docker version` (lignes Client et Server) :

```
À COMPLÉTER : collez la sortie de « docker run hello-world » (« Hello from Docker! ») et de « docker version »
```

Dernière ligne de `python -m pytest` après la mise en place :

```
À COMPLÉTER : la dernière ligne attendue est « 5 failed, 33 passed »
(sous Windows, si le dossier temporaire est refusé : python -m pytest --basetemp=.pytest_tmp)
```

## 2. Image et conteneur (pendant le premier build)

1. Quelle différence entre une image et un conteneur ?
   Une image est le résultat figé et nommé du build (`maintai:0.4.0`) : un paquet en lecture seule qui contient le système, Python, les bibliothèques et le code. Un conteneur est une copie de cette image qui tourne, isolée (ses fichiers, son réseau). À partir d'une même image, on peut lancer autant de conteneurs qu'on veut.
2. Pourquoi `COPY requirements-docker.txt` est-il placé avant `COPY maintai` ?
   Chaque instruction crée une couche, et Docker réutilise les couches du build précédent jusqu'à la première qui change. Les bibliothèques sont lentes à installer et changent rarement ; le code est rapide à copier et change souvent. En copiant d'abord la liste des bibliothèques, la couche `pip install` reste en cache quand on ne modifie que le code.
3. Pourquoi `requirements-docker.txt` contient-il `scikit-learn==1.8.0` et pas `scikit-learn>=1.5` ?
   Le modèle a été entraîné et sauvegardé avec scikit-learn 1.8.0. Un modèle sauvegardé peut ne plus se charger, ou donner d'autres résultats, avec une autre version. Fixer la version exacte garantit que l'image reconstruit le même environnement que l'entraînement, à chaque build.
4. Pourquoi ni `mlflow`, ni `dvc`, ni `pytest` dans l'image ?
   L'image ne sert qu'à servir des prédictions (API et interface) : on n'y entraîne pas, on n'y suit pas d'expériences et on n'y teste pas. Ces bibliothèques alourdiraient l'image et augmenteraient ce qui peut tomber en panne ou être attaqué, sans rien apporter à l'exécution.

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
| premier build | 167 s (167,4 s) | 1,13 Go |
| après une modification de `maintai/predict.py` | À COMPLÉTER | À COMPLÉTER |

Que signifie `CACHED` dans le journal du second build ?

`CACHED` signifie que Docker a réutilisé la couche du build précédent sans la refaire, parce que ni l'instruction ni les fichiers qu'elle utilise n'ont changé. Au second build, les étapes jusqu'à `pip install` sont en `CACHED` : seule la copie du code modifié est refaite, d'où un build beaucoup plus court.

## 4. Sprint 1 : lancer un conteneur

Votre commande `docker run` :

```
docker run -d --name maintai-api -p 8000:8000 --env-file .env -v "${PWD}\models:/app/models:ro" maintai:0.4.0
```

| Essai | Réponse |
|---|---|
| `GET /health` | À COMPLÉTER : collez votre sortie (attendu : `{"status":"ok","model_loaded":true}`) |
| `POST /v1/predict` sans clé | `401 Unauthorized` : `{"detail":"Clé API absente ou invalide"}` |
| `POST /v1/predict` avec la clé | `{"failure_probability":0.9553,"alert":true,"threshold":0.3,"model_version":"2026-11-26T10:27:57Z"}` |

**Piège 1.** Sans l'option `-v ...models...`, que répondent `/health` et `/v1/predict` ? Pourquoi ?

`/health` répond `{"status":"ok","model_loaded":false}` et `/v1/predict` répond `503 Service Unavailable` (« Modèle non chargé : lancez python -m maintai.train puis redémarrez l'API »). Le modèle n'est volontairement pas dans l'image (`models/` est dans `.dockerignore`) : sans le volume, le dossier `/app/models` du conteneur est vide. L'API démarre quand même, car le code attrape l'erreur `FileNotFoundError`, mais elle n'a pas de modèle à utiliser.

**Piège 2.** Avec `--host 127.0.0.1`, que disent `docker logs test` et `http://localhost:8002/health` ? Pourquoi ?

`docker logs test` montre que l'API démarre normalement (« Uvicorn running on http://127.0.0.1:8000 »), mais `http://localhost:8002/health` ne répond pas (`curl: (52) Empty reply from server`). Dans un conteneur, `127.0.0.1` veut dire « ce conteneur seulement » : la redirection de port de Docker arrive par l'interface réseau du conteneur et non par son adresse locale. Pour être joignable depuis le PC, l'API doit écouter sur `0.0.0.0` (toutes les adresses), comme dans notre `CMD`.

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
À COMPLÉTER : collez la sortie de « docker compose ps » (api et ui à l'état Up, ports 8000 et 8501)
```

Quelle URL affiche la barre latérale de l'interface ? D'où vient-elle ?

La barre latérale affiche `http://api:8000` (à vérifier sur votre écran après `docker compose up -d --build`). Cette valeur vient de la variable d'environnement `MAINTAI_API_URL`, définie dans `compose.yaml` pour le service `ui` et lue dans `ui/app.py` par `os.getenv("MAINTAI_API_URL", "http://localhost:8000")`. `api` est le nom du service : sur le réseau créé par Compose, chaque service est joignable par son nom. Sans la variable (lancement hors Docker), l'interface garde `http://localhost:8000`.

Résultat des deux commandes `docker compose exec ui ...` (avec `api` puis avec `localhost`). Pourquoi la seconde échoue-t-elle ?

```
À COMPLÉTER : collez les deux sorties
docker compose exec ui python -c "import httpx; print(httpx.get('http://api:8000/health').text)"
docker compose exec ui python -c "import httpx; print(httpx.get('http://localhost:8000/health').text)"
```

La première, avec `api`, atteint l'API et affiche la réponse de `/health`. La seconde, avec `localhost`, échoue (connexion refusée) : dans le conteneur `ui`, `localhost` désigne le conteneur `ui` lui-même, où rien n'écoute sur le port 8000. L'API tourne dans un autre conteneur, qu'on joint par le nom de son service, `api`.

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
================== 38 passed, 6 warnings in 22.39s ==================
```

(lancé avec `python -m pytest --basetemp=.pytest_tmp`, car le dossier temporaire par défaut de Windows était refusé.)

## 6. Décision : l'ADR 005

Dans `docs/adr/005-image-docker.md`. Résumez ici votre décision en deux phrases :

Nous livrons MaintAI dans une image Docker qui contient seulement le code et les bibliothèques (versions figées), et nous fournissons le modèle, les données et la clé API au lancement (volumes et `--env-file`). Les deux conteneurs, l'API et l'interface, sont lancés ensemble avec Docker Compose, parce que le modèle et les données changent plus souvent que le code et que la clé ne doit jamais entrer dans une image qu'on peut partager.

## 7. Questions de compréhension

1. Qu'est-ce qui entre dans l'image, et qu'est-ce qui arrive au lancement ? Donnez le moyen pour chaque élément.
   Dans l'image (par le Dockerfile) : le système de base, Python 3.11, les bibliothèques aux versions figées (`requirements-docker.txt`) et le code (`maintai`, `ui`). Au lancement : le modèle, par un volume (`-v ./models:/app/models:ro`, ou `volumes:` dans Compose) ; les données, par un volume (`./data:/app/data:ro`) ; la clé API, par `--env-file .env` (ou `env_file: .env` dans Compose).
2. Pourquoi la clé API n'est-elle jamais dans l'image ?
   Une image se partage, se stocke et peut être publiée : tout ce qu'elle contient est lisible par quiconque la reçoit, même dans une couche ancienne. Un secret dans l'image serait donc exposé et impossible à changer sans reconstruire. En le fournissant au lancement, il reste sur la machine qui exécute le conteneur et peut être changé sans toucher à l'image.
3. Livrer un modèle (TP4, TP5) : qu'est-ce que Docker ajoute à la liste ?
   Le TP4 a livré le code sous forme de package (wheel), avec des versions figées ; le TP5 a ajouté le suivi des entraînements (MLflow) et des données (DVC). Docker ajoute l'environnement d'exécution complet : système, Python et bibliothèques emballés avec le code, qui tournent de la même façon sur n'importe quel PC ou serveur où Docker est installé, sans préparer de `.venv`.

## 8. Le rendu Git

- Lien de la pull request : À COMPLÉTER
- Le tag `tp6` existe sur GitHub : À COMPLÉTER (oui / non)
- `git status` avant le commit : `.env`, `models/` ou `data/*.csv` apparaissaient-ils ? À COMPLÉTER (oui / non)

## 9. Ce qui reste flou

À COMPLÉTER : écrivez ici, avec vos mots, ce qui n'est pas encore clair pour vous (par exemple : la différence entre `EXPOSE` et `-p`, ou le fonctionnement des volumes).
