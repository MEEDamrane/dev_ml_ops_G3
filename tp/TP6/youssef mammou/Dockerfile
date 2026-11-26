
# Image de départ
FROM python:3.11-slim

# Dossier de travail
WORKDIR /app

# Copier les dépendances
COPY requirements-docker.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copier le code de l'application
COPY maintai ./maintai
COPY ui ./ui

# Variables d'environnement
ENV MAINTAI_MODELS_DIR=/app/models
ENV MAINTAI_DATA_PATH=/app/data/sensors.csv

# Port de l'API
EXPOSE 8000

# Lancer l'API
CMD ["uvicorn", "maintai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
