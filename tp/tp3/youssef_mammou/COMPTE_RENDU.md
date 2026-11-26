# Compte rendu – TP3 : Une interface Streamlit pour MaintAI

**Nom :** Youssef Mammou  
**Classe :** 5IIR – G1  
**TP :** TP3 – MaintAI  
**Date :** 12 novembre 2026

## Introduction

L’objectif de ce TP est de développer une interface utilisateur pour l’application MaintAI, qui permet de suivre l’état des équipements industriels à partir de données de capteurs.

L’application utilise :
- **Streamlit** pour créer une interface interactive.
- **FastAPI** pour exposer une API de prédiction.
- **Python et Pandas** pour manipuler les données.
- **Scikit-learn** pour exploiter le modèle de Machine Learning.
- **Pytest** pour effectuer les tests.

L’interface permet de consulter les relevés des capteurs, de visualiser les indicateurs et de demander une prédiction du risque de panne.

---

## 1. Mise en place et vérification

### 1.1 Installation du projet

Après avoir récupéré le projet, j’ai installé les dépendances dans l’environnement virtuel Python.

Commandes utilisées :

```powershell
python -m pip install -r requirements.txt
```

Pour vérifier les dépendances :

```powershell
python -m pip check
```

Résultat obtenu :

```text
No broken requirements found.
```

Cela signifie que les dépendances installées ne présentent pas de conflit détecté par pip.

### 1.2 Génération des données

J’ai exécuté la commande suivante depuis le dossier du projet :

```powershell
python -m maintai.dataset
```

Cette commande a permis de générer un jeu de données contenant **5 000 relevés de capteurs**, avec un taux de panne de **13,6 %**.

### 1.3 Exécution des tests

Commande :

```powershell
pytest
```

Dans mon environnement, certains tests ne peuvent pas être exécutés correctement à cause d'un blocage de DLL natives par la politique de sécurité Windows (Code Integrity).

Les bibliothèques concernées sont notamment :
- `pyarrow`
- `pydantic_core`

Les erreurs apparaissent pendant le chargement des modules, avant même l'exécution complète des tests.

**Conclusion :** le problème ne vient pas nécessairement du code du projet ni des dépendances Python, mais d'une restriction de sécurité Windows qui bloque certains fichiers DLL.

---

## 2. Lancement de l'application Streamlit

### 2.1 Démarrage de l'API

Dans un premier terminal, depuis le dossier du projet :

```powershell
uvicorn maintai.api.main:app --reload --env-file .env
```

L'API est accessible à l'adresse :

```text
http://localhost:8000
```

La documentation interactive est disponible ici :

```text
http://localhost:8000/docs
```

### 2.2 Démarrage de Streamlit

Dans un deuxième terminal :

```powershell
python -m streamlit run ui/app.py
```

L'interface est accessible à l'adresse :

```text
http://localhost:8501
```

### 2.3 Pourquoi utiliser `python -m streamlit` ?

La commande :

```powershell
python -m streamlit run ui/app.py
```

permet de lancer Streamlit avec le Python de l'environnement virtuel actuellement utilisé.

Elle évite certains problèmes de reconnaissance de la commande `streamlit` dans le terminal, notamment lorsque son exécutable n'est pas présent dans le PATH.

---

## 3. Sprint 1 – Développement de l'onglet Data

### 3.1 Objectif

L'objectif de ce sprint est de créer un tableau de bord permettant d'explorer les données des capteurs et de visualiser les principaux indicateurs.

### 3.2 Affichage des indicateurs

Le code suivant permet d'afficher trois indicateurs :

```python
col_releves, col_pannes, col_temperature = st.columns(3)

col_releves.metric("Nombre de relevés", len(df))

col_pannes.metric(
    "Taux de panne",
    f"{df.failure.mean():.1%}"
)

col_temperature.metric(
    "Température moyenne",
    f"{df.temperature_c.mean():.1f} °C"
)
```

Les trois indicateurs sont :
- Nombre total de relevés.
- Taux de panne.
- Température moyenne.

Selon le rapport précédent, les valeurs obtenues étaient :
- 5 000 relevés.
- 13,6 % de pannes.
- 59,8 °C de température moyenne.

### 3.3 Analyse du taux de panne par variable

Le code suivant permet de sélectionner une variable et de calculer le taux de panne par tranche :

```python
variable = st.selectbox("Variable", FEATURES)

tranches = pd.cut(
    df[variable],
    bins=10,
    duplicates="drop"
)

taux_par_tranche = (
    df.groupby(tranches, observed=True)
    .failure.mean()
    .rename_axis("Tranche")
    .reset_index(name="Taux de panne")
)

taux_par_tranche["Tranche"] = (
    taux_par_tranche["Tranche"].astype(str)
)

st.bar_chart(
    taux_par_tranche,
    x="Tranche",
    y="Taux de panne"
)
```

La fonction `pd.cut()` divise les valeurs en dix intervalles.

La fonction `groupby()` regroupe les relevés par intervalle et calcule la moyenne de la variable `failure`.

Le résultat permet de visualiser les tranches dans lesquelles le risque de panne est le plus élevé.

### 3.4 Visualisation des capteurs

Le graphique suivant représente la relation entre la température et les vibrations :

```python
st.scatter_chart(
    df,
    x="temperature_c",
    y="vibration_mm_s",
    color="failure"
)
```

Ce graphique permet d'observer la distribution des relevés et de comparer les mesures associées aux pannes et aux situations normales.

### 3.5 Interprétation des résultats

D'après les résultats présentés dans le rapport précédent, le taux de panne augmente fortement dans les tranches élevées de vibration.

On observe notamment :
- Un risque faible dans les premières tranches.
- Une augmentation importante du risque lorsque les vibrations atteignent environ 6,7 à 8,9 mm/s.
- Un risque très élevé dans les dernières tranches.

Cela montre que les vibrations peuvent constituer un indicateur important pour anticiper les défaillances des équipements.

### 3.6 Pourquoi Streamlit relance-t-il le script ?

Lorsqu'on interagit avec un élément de l'interface, Streamlit réexécute le script de haut en bas.

Par exemple, si le code contient :

```python
print("relance")
```

Le message apparaît à nouveau dans le terminal à chaque interaction qui provoque une réexécution.

### 3.7 Utilisation de `@st.cache_data`

Le décorateur `@st.cache_data` permet de mettre en cache le résultat d'une fonction qui charge ou prépare des données.

Exemple :

```python
@st.cache_data
def charger_donnees():
    return pd.read_csv("data/sensor_readings.csv")
```

Son intérêt est d'éviter de relire le fichier CSV à chaque réexécution du script lorsque les paramètres et les données en cache restent valides.

---

## 4. Sprint 2 – Intégration de la prédiction

### 4.1 Objectif

Ce sprint consiste à connecter l'interface Streamlit à l'API FastAPI pour envoyer un relevé de capteurs et obtenir une prédiction du risque de panne.

### 4.2 Méthode `predict`

La méthode suivante permet d'envoyer les données à l'API :

```python
def predict(self, reading: dict) -> dict:
    """Envoie un relevé à l'API et récupère la prédiction."""

    headers = (
        {"X-API-Key": self.api_key}
        if self.api_key else {}
    )

    r = self.http.post(
        "/v1/predict",
        json=reading,
        headers=headers
    )

    if r.status_code != 200:
        raise APIError(
            r.status_code,
            r.json().get("detail")
        )

    return r.json()
```

**Explication :**
- `reading` contient les mesures des capteurs.
- `headers` transmet la clé API.
- `post()` envoie les données à l'API.
- `status_code` vérifie le résultat de la requête.
- `return r.json()` retourne la prédiction sous forme de dictionnaire Python.

### 4.3 Gestion de la clé API

La clé API est définie dans le fichier `.env` :

```env
MAINTAI_API_KEY=demo123
```

La même clé doit être renseignée dans l'interface Streamlit.

Elle permet de sécuriser l'accès à l'endpoint de prédiction.

### 4.4 Scénarios de test

| Scénario | Résultat attendu |
|---|---|
| Clé correcte et API démarrée | La prédiction est retournée. |
| Clé incorrecte | L'API retourne une erreur HTTP 401. |
| API arrêtée | L'application signale que l'API est inaccessible. |

Ces scénarios permettent de vérifier le fonctionnement de la communication entre l'interface et l'API.

### 4.5 Pourquoi CORS n'est-il pas nécessaire ici ?

CORS est un mécanisme de sécurité appliqué par les navigateurs lorsqu'une page Web effectue des requêtes vers un autre domaine ou une autre origine.

Dans ce TP, Streamlit utilise Python et la bibliothèque `httpx` pour communiquer directement avec FastAPI.

La requête n'est donc pas effectuée par le navigateur avec JavaScript `fetch()`.

C'est pourquoi le problème CORS rencontré dans une architecture Web classique ne se pose pas de la même manière ici.

---

## 5. Compréhension de l'architecture et des tests

### 5.1 Différence entre TP2 et TP3

Dans le TP2, l'interface Web communique avec l'API à l'aide de JavaScript et de `fetch()`.

Dans le TP3, Streamlit utilise Python et `httpx` pour envoyer les requêtes à FastAPI.

La principale différence concerne donc la technologie utilisée pour construire l'interface et communiquer avec l'API.

### 5.2 Pourquoi utiliser `TestClient` sans démarrer Uvicorn ?

FastAPI fournit `TestClient`, qui permet de tester directement les endpoints de l'application.

Il n'est pas nécessaire de lancer un serveur Uvicorn pour chaque test.

Cela rend les tests plus rapides et facilite la vérification des réponses HTTP.

### 5.3 Pourquoi choisir Streamlit plutôt que HTML/JavaScript ?

Streamlit permet de développer rapidement une interface interactive en Python.

Ses avantages :
- Peu de code HTML et JavaScript.
- Intégration simple avec Pandas et les bibliothèques de Data Science.
- Création rapide de tableaux de bord.
- Visualisation facile des données.
- Adapté aux prototypes et aux applications de Machine Learning.

---

## 6. Git et gestion du projet

Git permet de suivre les modifications du code et de travailler avec différentes versions du projet.

Commandes utiles :

```powershell
git status
git add .
git commit -m "Finalisation TP3 MaintAI"
git push
```

La commande `git status` permet de vérifier les fichiers modifiés ou non suivis.

Les fichiers suivants ne doivent généralement pas être envoyés dans le dépôt :

- `.env` : contient les clés et les variables sensibles.
- `.venv/` : contient l'environnement virtuel.
- `__pycache__/` : fichiers temporaires Python.
- `data/*.csv` : données générées localement, selon les consignes du projet.
- `models/` : modèles générés localement, selon les consignes du projet.

Pour vérifier les éléments suivis par Git :

```powershell
git status
```

**Lien de Pull Request :** à compléter avec le lien réel.

**Tag `tp3` :** à vérifier dans le dépôt Git.

---

## 7. Difficultés rencontrées

Pendant la réalisation du TP, plusieurs difficultés ont été rencontrées :

1. Le lancement des commandes Python depuis le bon dossier du projet.
2. La configuration de l'environnement virtuel.
3. La communication entre Streamlit et FastAPI.
4. La gestion de la clé API et des erreurs HTTP.
5. Le blocage de certaines DLL natives par la politique de sécurité Windows.

Pour résoudre les problèmes de lancement, j'ai utilisé `python -m` afin d'exécuter les modules avec l'interpréteur Python de l'environnement virtuel.

Concernant les DLL bloquées, les événements Code Integrity de Windows ont confirmé une restriction de sécurité sur certains fichiers natifs de PyArrow et Pydantic.

---

## 8. Points qui restent à approfondir

Les points que je souhaite approfondir sont :

- Le fonctionnement interne de Streamlit et de ses mécanismes de réexécution.
- La mise en cache avec `@st.cache_data`.
- La communication entre une interface et une API REST.
- La sécurisation des endpoints avec une clé API.
- Les tests automatisés avec Pytest et FastAPI TestClient.
- Le fonctionnement du modèle de Machine Learning et l'interprétation des probabilités de panne.

---

## Conclusion

Ce TP m'a permis de comprendre comment construire une interface interactive avec Streamlit et la connecter à une API FastAPI.

J'ai également appris à manipuler des données de capteurs avec Pandas, à créer des visualisations, à transmettre des relevés à une API et à récupérer des prédictions.

Enfin, ce travail m'a permis de mieux comprendre l'organisation d'une application intelligente composée d'une interface utilisateur, d'une API et d'un modèle de Machine Learning.

**Le TP3 constitue ainsi une étape importante dans la réalisation d'une application de maintenance prédictive avec Python et l'intelligence artificielle.**