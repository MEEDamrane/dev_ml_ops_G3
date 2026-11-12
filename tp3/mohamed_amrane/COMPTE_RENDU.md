# Compte rendu du TP3 – Interface Streamlit de MaintAI

**Réalisé par : Mohamed Amrane**  
**Date : 12 novembre 2026**

## 1. Objectif du TP

L'objectif de ce TP est de créer une interface Streamlit pour l'application MaintAI. Cette interface permet d'explorer les relevés des capteurs, de visualiser le taux de panne et d'envoyer un relevé à l'API afin d'obtenir une prédiction.

Le travail a été divisé en deux sprints :

- Sprint 1 : affichage des indicateurs et des graphiques ;
- Sprint 2 : communication avec l'API et affichage de la prédiction.

## 2. Installation et lancement

J'ai créé et activé un environnement virtuel, puis installé les dépendances :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

J'ai ensuite généré les données et entraîné le modèle :

```powershell
python -m maintai.dataset
python -m maintai.train
```

L'API et l'interface ont été lancées dans deux terminaux différents :

```powershell
uvicorn maintai.api.main:app --reload --env-file .env
```

```powershell
python -m streamlit run ui/app.py
```

L'API est disponible sur <http://localhost:8000> et l'interface Streamlit sur <http://localhost:8501>.

La commande `python -m streamlit` fonctionne même lorsque la commande `streamlit` n'est pas directement reconnue par PowerShell, car elle lance le module Streamlit avec l'interpréteur Python de l'environnement actif.

## 3. Sprint 1 – Exploration des données

Dans l'onglet « Données », j'ai ajouté trois indicateurs :

| Indicateur | Valeur obtenue |
|---|---:|
| Nombre de relevés | 5 000 |
| Taux de panne | 13,6 % |
| Température moyenne | 59,8 °C |

Le code utilisé est le suivant :

```python
col_releves, col_pannes, col_temperature = st.columns(3)
col_releves.metric("Nombre de relevés", len(df))
col_pannes.metric("Taux de panne", f"{df.failure.mean():.1%}")
col_temperature.metric(
    "Température moyenne",
    f"{df.temperature_c.mean():.1f} °C",
)
```

J'ai ensuite ajouté une liste permettant de choisir une variable parmi les caractéristiques du modèle. Les valeurs sont regroupées en dix tranches avec `pd.cut`, puis le taux de panne moyen de chaque tranche est affiché sous forme d'histogramme.

```python
variable = st.selectbox("Variable", FEATURES)
tranches = pd.cut(df[variable], bins=10, duplicates="drop")
taux_par_tranche = (
    df.groupby(tranches, observed=True)
    .failure.mean()
    .rename_axis("Tranche")
    .reset_index(name="Taux de panne")
)
taux_par_tranche["Tranche"] = taux_par_tranche["Tranche"].astype(str)
st.bar_chart(taux_par_tranche, x="Tranche", y="Taux de panne")
```

La conversion des tranches en texte est nécessaire, car Altair 6 ne peut pas utiliser directement les objets `Interval` créés par pandas.

Lorsque je sélectionne `vibration_mm_s`, je constate que le risque augmente avec les vibrations. Le taux est proche de 2 % dans la tranche la plus basse, dépasse 66 % entre environ 6,7 et 8,9 mm/s, puis atteint presque 100 % pour les vibrations les plus importantes.

Enfin, le nuage de points permet de comparer la température et les vibrations, avec une couleur qui indique la présence ou non d'une panne :

```python
st.scatter_chart(
    df,
    x="temperature_c",
    y="vibration_mm_s",
    color="failure",
)
```

Streamlit réexécute le script du haut vers le bas à chaque interaction. Le décorateur `@st.cache_data` évite donc de relire inutilement le fichier CSV à chaque exécution.

## 4. Sprint 2 – Communication avec l'API

J'ai implémenté la méthode `predict` du client Python :

```python
def predict(self, reading: dict) -> dict:
    """Envoie un relevé et renvoie la réponse JSON de l'API."""
    headers = {"X-API-Key": self.api_key} if self.api_key else {}
    r = self.http.post("/v1/predict", json=reading, headers=headers)
    if r.status_code != 200:
        raise APIError(r.status_code, r.json().get("detail"))
    return r.json()
```

La méthode ajoute la clé dans l'en-tête `X-API-Key`, envoie le relevé au point d'accès `/v1/predict`, puis renvoie la réponse JSON. Si l'API refuse la requête, une exception `APIError` est levée.

Dans Streamlit, trois situations sont gérées :

| Situation | Résultat affiché |
|---|---|
| Bonne clé et API disponible | Probabilité de panne, puis alerte ou situation normale |
| Clé incorrecte ou absente | `Erreur API 401 : Clé API absente ou invalide` |
| API arrêtée ou mauvaise URL | Message indiquant que l'API est injoignable |

Pendant le test, j'ai rencontré l'erreur 401. Elle signifie que la clé saisie dans Streamlit ne correspond pas à celle chargée par l'API. La configuration attendue est :

```env
MAINTAI_API_KEY=<cle-configuree-localement>
```

Après une modification du fichier `.env`, il est nécessaire d'arrêter puis de redémarrer Uvicorn avec `--env-file .env`. La même clé doit ensuite être saisie dans la barre latérale de Streamlit.

Le port 8501 n'a pas besoin d'être ajouté à `MAINTAI_CORS_ORIGINS`. En effet, la requête est envoyée par le serveur Python Streamlit avec `httpx`, et non directement par le navigateur. La protection CORS s'applique principalement aux requêtes effectuées par le navigateur entre deux origines différentes.

## 5. Tests

Les tests du client donnent le résultat suivant :

```text
3 passed, 22 warnings
```

Le résultat final de tous les tests est :

```text
23 passed, 99 warnings
```

Les avertissements sont liés à des dépréciations dans Starlette et Joblib. Ils n'empêchent pas le bon fonctionnement de l'application.

Les tests de `test_client.py` n'ont pas besoin d'un serveur Uvicorn. Ils injectent le `TestClient` de FastAPI dans `MaintaiClient`, ce qui permet d'appeler l'API directement en mémoire.

## 6. Comparaison avec le client web du TP2

Dans le client HTML/JavaScript du TP2, le navigateur envoie directement la requête à l'API avec `fetch`. Dans l'application Streamlit du TP3, le navigateur communique avec Streamlit, puis le code Python envoie la requête à l'API avec `httpx`.

Pour une démonstration rapide d'un modèle d'intelligence artificielle, Streamlit est un bon choix, car il permet de construire rapidement une interface fonctionnelle. Pour une application finale utilisée quotidiennement par des techniciens, une interface web personnalisée peut être plus adaptée afin de mieux contrôler l'ergonomie, l'affichage mobile et l'intégration aux autres outils.

## 7. Gestion des fichiers avec Git

Les éléments suivants sont ignorés par Git :

- `.env`, car il contient la clé API ;
- `data/*.csv`, car les données sont générées ;
- `models/`, car les fichiers du modèle sont des artefacts d'entraînement ;
- `.venv/` et les fichiers de cache Python.

Lien de la pull request : **à renseigner**  
Tag `tp3` sur GitHub : **à vérifier**

## 8. Conclusion

Ce TP m'a permis de développer une interface Streamlit connectée à une API FastAPI. J'ai affiché les statistiques du jeu de données, construit deux visualisations, implémenté un client HTTP avec authentification et géré les principales erreurs. L'application fonctionne et les 23 tests automatisés passent.
