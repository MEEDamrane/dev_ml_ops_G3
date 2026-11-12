# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** G3  ·  **Membre :** Mohamed Amrane  ·  **Date :** 12 novembre 2026

## 1. Mise en place

Avant l'installation du package :

```text
2 failed, 25 passed
```

Les tests `test_installed_version_matches_the_code` et `test_command_is_declared` échouent parce que `maintai` n'est pas encore installé. Sa version n'est pas disponible dans les métadonnées et le point d'entrée `maintai-predict` n'existe pas encore.

## 2. Sprint 1 : package et installation éditable

```toml
dependencies = [
    "numpy>=2.0",
    "pandas>=2.2",
    "scikit-learn>=1.5",
    "joblib>=1.4",
    "httpx>=0.27",
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

`pytest` reste dans le groupe `dev`, `fastapi` dans `api` et `streamlit` dans `ui`, car ces bibliothèques ne sont pas nécessaires à la commande terminal principale.

```text
Name: maintai
Version: 0.2.0
Summary: Application de prediction de panne a partir de releves de capteurs
Location: C:\Users\moham\Desktop\mlops\maintai-starter-tp4\.venv\Lib\site-packages
Editable project location: C:\Users\moham\Desktop\mlops\maintai-starter-tp4
```

Résultat final des tests :

```text
27 passed, 1 warning in 9.13s
```

Essai depuis un autre dossier :

```text
> maintai-predict 72 6 85 15000
Probabilité de panne : 95 % (ALERTE)

> python -c "import maintai; print(maintai.__file__)"
C:\Users\moham\Desktop\mlops\maintai-starter-tp4\maintai\__init__.py
```

Python trouve le code dans le dossier source. Avec `pip install -e .`, les modifications de `maintai/cli.py` sont visibles immédiatement sans réinstallation.

## 3. Sprint 2 : construire et installer le wheel

```text
maintai-0.2.0-py3-none-any.whl    11623 octets
maintai-0.2.0.tar.gz              12219 octets
```

Le wheel contient les modules de `maintai/` et les métadonnées `maintai-0.2.0.dist-info/`. Il ne contient ni le modèle, ni les tests, ni `ui/`, car seuls les packages `maintai*` sont inclus. Le modèle doit être livré séparément.

| Étape | Résultat |
|---|---|
| sans `MAINTAI_MODELS_DIR` | `Modèle introuvable : ...\site-packages\models\model.joblib` |
| avec `MAINTAI_MODELS_DIR` | avertissement possible `InconsistentVersionWarning` si la version de scikit-learn diffère |
| après `pip install scikit-learn==1.8.0` | `Probabilité de panne : 95 % (ALERTE)` |

La ligne suivante de `models/model_info.json` explique l'avertissement :

```json
"sklearn_version": "1.8.0"
```

## 4. Questions de compréhension

1. `requirements.txt` fixe les versions avec `==` pour reproduire l'environnement d'entraînement. `pyproject.toml` utilise des minimums avec `>=` pour permettre l'installation à côté d'autres applications compatibles.

2. `pip install -e .` pointe vers le dossier source et rend les changements immédiatement visibles. L'installation du wheel copie une version construite dans `site-packages` ; il faut reconstruire et réinstaller pour appliquer des changements.

3. `[project.scripts]` associe un nom de commande à une fonction Python. `maintai-predict = "maintai.cli:main"` crée le lanceur `.venv\Scripts\maintai-predict.exe`.

## 5. Rendu Git

`dist/`, `build/`, `maintai.egg-info/`, `.venv/` et `models/` sont exclus par `.gitignore`. Un livrable de machine learning complet comprend le wheel, le modèle entraîné et les versions exactes utilisées pour l'entraînement.
