# ADR 005 : Séparer l'image Docker des données, du modèle et des secrets

Date : 26/11/2026 · Auteurs : à compléter

## Contexte

MaintAI doit fournir une API et une interface reproductibles sans intégrer dans l'image Docker des fichiers locaux, volumineux ou sensibles. Le modèle, les données et la clé API doivent pouvoir être remplacés sans reconstruire ni republier l'image.

## Options étudiées

1. Tout intégrer dans l'image : le déploiement est simple et autonome, mais l'image devient plus lourde, les secrets peuvent être exposés et toute modification du modèle, des données ou de la clé impose un nouveau build.
2. Construire une image d'inférence minimale et injecter les éléments variables au lancement : l'image reste légère, réutilisable et plus sûre, mais le démarrage nécessite de configurer correctement les volumes et les variables d'environnement.

## Décision

Nous retenons une image d'inférence minimale contenant Python, les dépendances figées, le code de l'API et l'interface. Le modèle et les données sont montés en lecture seule avec des volumes Docker, tandis que la clé API et l'URL interne de l'API sont fournies par des variables d'environnement, car ces éléments changent indépendamment du code.

## Conséquences

Cette décision facilite la reproductibilité, réduit les reconstructions inutiles et évite de publier la clé API dans une couche Docker. En contrepartie, le déploiement dépend de la présence des fichiers montés et d'une configuration correcte de `.env` et de `compose.yaml` ; il faudra aussi surveiller la compatibilité entre la version de scikit-learn de l'image et celle utilisée pour produire le modèle.
