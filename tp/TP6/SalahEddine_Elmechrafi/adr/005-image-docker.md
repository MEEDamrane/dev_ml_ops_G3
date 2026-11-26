# ADR 005 : une image Docker unique, sans modèle ni données ni secret

Date : 26/11/2026 · Auteurs : [Salah EDDINE ELMECHRAFI]

## Contexte
MaintAI doit tourner de la même façon sur n'importe quelle machine, sans installer Python ni ses bibliothèques. L'API et l'interface Streamlit sont deux services séparés. Le modèle `model.joblib` doit être lu par la version exacte de scikit-learn qui l'a écrit (1.8.0). Le modèle change à chaque réentraînement, et la clé API est un secret.

## Options étudiées
1. **Tout dans l'image** (code, modèle, données, clé) : un seul fichier à livrer, rien à monter au lancement. Mais il faut reconstruire l'image à chaque nouveau modèle. L'image grossit avec les données. Et la clé est lisible par toute personne qui récupère l'image, même si elle est supprimée dans une couche suivante.
2. **Une image par service** (une pour l'API, une pour l'interface) : chaque image ne contient que ce dont son service a besoin. Mais il y a deux Dockerfile à maintenir et deux builds. Le gain est faible, car les deux services partagent le code `maintai` et presque toutes les bibliothèques (pandas, scikit-learn, httpx).
3. **Une image unique avec seulement le code et les bibliothèques**, le reste fourni au lancement : un seul build, réutilisé par les deux services avec deux commandes. Le modèle et les données sont montés en volumes, la clé est passée par `.env`. En contrepartie, il faut penser à monter les volumes : sans `-v ...models...`, l'API démarre mais répond 503.

Pour l'image de départ : `python:3.11-slim`, la même version de Python que sur les PC, plutôt que `python:3.11`, qui pèse environ 1 Go de plus avec des outils inutiles ici. `alpine` est écartée : numpy, pandas et scikit-learn n'y ont pas toujours de roues précompilées, et le build serait long et fragile.

## Décision
On retient l'**option 3** : une seule image `maintai:0.4.0`, basée sur `python:3.11-slim`, avec les bibliothèques aux versions figées de `requirements-docker.txt` (dont `scikit-learn==1.8.0`) et sans mlflow, dvc ni pytest. Compose lance l'API avec la commande par défaut et l'interface avec `streamlit run`. Le modèle (`./models`) et les données (`./data`) sont montés en lecture seule, et la clé API arrive par `env_file: .env`. La raison principale : le modèle change plus souvent que le code et la clé ne doit jamais circuler avec l'image. Séparer ce qui est figé (l'image) de ce qui est fourni au lancement permet de changer de modèle ou de clé sans reconstruire l'image.

## Conséquences
- **Ce qui est plus facile** : un nouveau modèle ne demande qu'un `docker compose restart api`, sans rebuild. Les bibliothèques sont installées avant le code, donc une modification du code reconstruit l'image en environ 4 s au lieu de 85 s. La clé reste hors de l'image et hors de Git (`.dockerignore`, `.gitignore`).
- **Ce qui est plus difficile** : l'image ne fonctionne pas seule. Il faut fournir `models/`, `data/` et `.env` sur la machine qui la lance. L'image pèse quand même 1.13 GB, surtout à cause des bibliothèques scientifiques et de Streamlit, que l'API n'utilise pas.
- **À surveiller** : la version de scikit-learn de l'image doit rester celle qui a entraîné le modèle. Toute mise à jour de `requirements-docker.txt` impose de réentraîner le modèle. Si la taille de l'image devient gênante, on pourra revenir à l'option 2 et séparer l'API de l'interface.
