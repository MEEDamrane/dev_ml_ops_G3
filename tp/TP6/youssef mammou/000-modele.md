# ADR 000 : Conteneurisation et déploiement de MaintAI avec Docker Compose

**Date :** 26/11/2026 · **Auteurs :** Youssef Mammou

## Contexte

Le projet MaintAI comprend deux composants principaux : une API FastAPI pour effectuer les prédictions de panne et une interface Streamlit pour permettre aux utilisateurs d'interagir avec l'application.

Il est nécessaire de disposer d'un environnement d'exécution reproductible, de faciliter le déploiement et d'assurer la communication entre ces deux composants.

## Options étudiées

1. **Exécution locale sans Docker :**
   - Avantages : installation simple pour le développement et débogage direct.
   - Inconvénients : dépendance à l'environnement de chaque machine, risques de conflits entre les versions des bibliothèques et configuration manuelle des services.

2. **Conteneurisation avec Docker et Docker Compose :**
   - Avantages : environnement reproductible, isolation des services, gestion centralisée de l'API et de l'interface, facilité de déploiement.
   - Inconvénients : configuration initiale plus complexe, consommation de ressources et nécessité de maîtriser les volumes, réseaux et variables d'environnement.

## Décision

Nous avons choisi **Docker et Docker Compose** pour déployer MaintAI dans deux conteneurs distincts : un conteneur pour l'API FastAPI et un autre pour l'interface Streamlit.

Les deux services utilisent la même image Docker `maintai:0.4.0`. La communication entre les conteneurs se fait à travers le réseau interne Docker, en utilisant le nom du service `api` et le port `8000`.

Le modèle et les données sont fournis à l'exécution avec des volumes, tandis que la clé API est configurée à travers un fichier `.env`.

Ce choix permet de garantir un environnement cohérent et de séparer le code applicatif des ressources et configurations nécessaires à son exécution.

## Conséquences

- Le déploiement des deux services est facilité grâce à une seule commande : `docker compose up -d`.
- L'API et l'interface Streamlit sont isolées dans deux conteneurs distincts.
- La même image Docker peut être réutilisée pour les deux services.
- Le modèle et les données peuvent être remplacés sans reconstruire l'image.
- Les informations sensibles, notamment la clé API, doivent rester dans le fichier `.env` et ne doivent pas être publiées dans Git.
- Il faudra surveiller la disponibilité de l'API avant l'envoi des requêtes depuis l'interface, ainsi que la compatibilité des dépendances et la taille de l'image Docker.