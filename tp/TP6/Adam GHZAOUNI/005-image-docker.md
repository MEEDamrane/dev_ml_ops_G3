# ADR 005 : Livrer MaintAI dans une image Docker (code et bibliothèques), avec le modèle, les données et la clé au lancement

Date : 26/11/2026 · Auteurs : À COMPLÉTER (vos noms)

## Contexte
MaintAI ne tournait que sur un PC préparé à la main (bon Python, .venv, six minutes d'installation, scikit-learn en version 1.8.0 exacte). Il doit pouvoir tourner sur un serveur où personne ne prépare d'environnement, de la même façon que sur nos PC.

## Options étudiées
1. Livrer le package (wheel) et une liste de versions : léger, mais chaque machine doit réinstaller Python et les bibliothèques, et une version différente de scikit-learn peut casser le modèle sans bruit.
2. Une image Docker qui contient aussi le modèle, les données et la clé : démarrage immédiat, mais l'image devient lourde, doit être reconstruite à chaque réentraînement, et la clé API serait lisible par quiconque reçoit l'image.
3. Une image Docker avec le code et les bibliothèques seulement ; le modèle et les données arrivent par des volumes, la clé par --env-file : même environnement partout, image stable, secret hors de l'image. Il faut penser à fournir le modèle et la clé au lancement.

## Décision
Option 3 : image `maintai:0.4.0` (python:3.11-slim, bibliothèques figées dans requirements-docker.txt, sans mlflow, dvc ni pytest), lancée avec le dossier models monté en lecture seule et la clé via .env, et orchestrée avec Docker Compose (API et interface dans deux conteneurs qui se joignent par le nom du service). La raison principale : le modèle et les données changent plus souvent que le code, et la clé ne doit jamais entrer dans une image qu'on peut partager.

## Conséquences
Facilite : un environnement identique sur tout PC ou serveur ; réentraîner sans reconstruire l'image ; un rebuild rapide grâce au cache des couches. Rend plus difficile : Docker doit être installé, et un conteneur lancé sans le volume models démarre mais sans modèle (/health indique model_loaded false, /v1/predict répond 503). À surveiller : la taille de l'image (1,13 Go), la cohérence entre la version de scikit-learn de l'image et celle qui a entraîné le modèle, et la rotation de la clé.
