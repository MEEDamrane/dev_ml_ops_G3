# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :*G1-3* …  ·  **Membres :*RIZQY NABILA* …  ·  **Date :*19/11/2026* …

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP4.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
(.venv) macbookair@MacBookAir maintai-starter-tp4 % python -m pytest 
============================================================================= test session starts ==============================================================================
platform darwin -- Python 3.14.5, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/macbookair/Desktop/maintai-starter-tp4
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.16.0
collected 27 items                                                                                                                                                             

tests/test_api.py .......                                                                                                                                                [ 25%]
tests/test_cli.py ..                                                                                                                                                     [ 33%]
tests/test_client.py ...                                                                                                                                                 [ 44%]
tests/test_data.py ...                                                                                                                                                   [ 55%]
tests/test_package.py FF                                                                                                                                                 [ 62%]
tests/test_security.py .....                                                                                                                                             [ 81%]
tests/test_train.py ...                                                                                                                                                  [ 92%]
tests/test_ui.py ..                                                                                                                                                      [100%]

=================================================================================== FAILURES ===================================================================================
___________________________________________________________________ test_installed_version_matches_the_code ____________________________________________________________________

cls = <class 'importlib.metadata.Distribution'>, name = 'maintai'

    @classmethod
    def from_name(cls, name: str) -> Distribution:
        """Return the Distribution for the given package name.
    
        :param name: The name of the distribution package to search for.
        :return: The Distribution instance (or subclass thereof) for the named
            package, if found.
        :raises PackageNotFoundError: When the named package's distribution
            metadata cannot be found.
        :raises ValueError: When an invalid value is supplied for name.
        """
        if not name:
            raise ValueError("A distribution name is required.")
        try:
>           return next(iter(cls.discover(name=name)))
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           StopIteration

/opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/lib/python3.14/importlib/metadata/__init__.py:407: StopIteration

During handling of the above exception, another exception occurred:

    def test_installed_version_matches_the_code():
        # Échoue tant que le package n'est pas installé (pip install -e .)
>       assert version("maintai") == maintai.__version__
               ^^^^^^^^^^^^^^^^^^

tests/test_package.py:8: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/lib/python3.14/importlib/metadata/__init__.py:987: in version
    return distribution(distribution_name).version
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/lib/python3.14/importlib/metadata/__init__.py:960: in distribution
    return Distribution.from_name(distribution_name)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

cls = <class 'importlib.metadata.Distribution'>, name = 'maintai'

    @classmethod
    def from_name(cls, name: str) -> Distribution:
        """Return the Distribution for the given package name.
    
        :param name: The name of the distribution package to search for.
        :return: The Distribution instance (or subclass thereof) for the named
            package, if found.
        :raises PackageNotFoundError: When the named package's distribution
            metadata cannot be found.
        :raises ValueError: When an invalid value is supplied for name.
        """
        if not name:
            raise ValueError("A distribution name is required.")
        try:
            return next(iter(cls.discover(name=name)))
        except StopIteration:
>           raise PackageNotFoundError(name)
E           importlib.metadata.PackageNotFoundError: No package metadata was found for maintai

/opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/lib/python3.14/importlib/metadata/__init__.py:409: PackageNotFoundError
___________________________________________________________________________ test_command_is_declared ___________________________________________________________________________

    def test_command_is_declared():
        noms = [e.name for e in entry_points(group="console_scripts")]
>       assert "maintai-predict" in noms
E       AssertionError: assert 'maintai-predict' in ['pip', 'pip3', 'uvicorn', 'watchfiles', 'fastapi', 'websockets', ...]

tests/test_package.py:13: AssertionError
=============================================================================== warnings summary ===============================================================================
.venv/lib/python3.14/site-packages/fastapi/testclient.py:1
  /Users/macbookair/Desktop/maintai-starter-tp4/.venv/lib/python3.14/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================================================================== short test summary info ============================================================================
FAILED tests/test_package.py::test_installed_version_matches_the_code - importlib.metadata.PackageNotFoundError: No package metadata was found for maintai
FAILED tests/test_package.py::test_command_is_declared - AssertionError: assert 'maintai-predict' in ['pip', 'pip3', 'uvicorn', 'watchfiles', 'fastapi', 'websockets', ...]
=================================================================== 2 failed, 25 passed, 1 warning in 30.29s ===================================================================
(.venv) macbookair@MacBookAir maintai-starter-tp4 % 


```

Quels sont les deux tests qui échouent, et pourquoi ?

…
Les deux tests qui échouent sont dans tests/test_package.py :

test_installed_version_matches_the_code : maintai n'est pas installé comme package, donc importlib.metadata ne trouve aucune métadonnée (PackageNotFoundError).
test_command_is_declared : la commande maintai-predict n'est pas déclarée dans [project.scripts] et n'a pas été installée, donc elle est absente de la liste des commandes.


## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Vos sections `dependencies` et `[project.scripts]` :

```toml
Vos sections dependencies et [project.scripts] :

dependencies = [
    "pandas>=2.2",
    "numpy>=1.26",
    "scikit-learn>=1.5",
    "joblib>=1.4",
    "httpx>=0.27",
]

[project.scripts]
maintai-predict = "maintai.cli:main"


```

Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

… 

Parce que dependencies ne contient que ce qu'il faut pour que le package fonctionne chez tout le monde (par exemple pour lancer maintai-predict). pytest ne sert qu'aux développeurs (groupe dev) et fastapi qu'à ceux qui lancent l'API (groupe api). Ils s'installent à la demande avec pip install -e ".[api,dev]".



Sortie de `pip show maintai` (les quatre premières lignes) :

```
platform darwin -- Python 3.14.5, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/macbookair/Desktop/maintai-starter-tp4
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.16.0
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
collected 27 items                                                                                                                                                             

tests/test_api.py .......                                                                                                                                                [ 25%]
tests/test_cli.py ..                                                                                                                                                     [ 33%]
tests/test_client.py ...                                                                                                                                                 [ 44%]
tests/test_data.py ...                                                                                                                                                   [ 55%]
tests/test_package.py ..                                                                                                                                                 [ 62%]
tests/test_security.py .....                                                                                                                                             [ 81%]
tests/test_train.py ...                                                                                                                                                  [ 92%]
tests/test_ui.py ..                                                                                                                                                      [100%]

=============================================================================== warnings summary ===============================================================================
.venv/lib/python3.14/site-packages/fastapi/testclient.py:1
  /Users/macbookair/Desktop/maintai-starter-tp4/.venv/lib/python3.14/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================================================================== 27 passed, 1 warning in 3.42s =========================================================================
(.venv) macbookair@MacBookAir maintai-starter-tp4 % 

```

Placez-vous dans un autre dossier (`cd %TEMP%`) et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de `maintai` ?

… (.venv) macbookair@MacBookAir maintai-starter-tp4 % cd /tmp
maintai-predict 72 6 85 15000
python -c "import maintai; print(maintai.__file__)"

Probabilité de panne : 95 % (ALERTE)
/Users/macbookair/Desktop/maintai-starter-tp4/maintai/__init__.py
(.venv) macbookair@MacBookAir /tmp % 
(.venv) macbookair@MacBookAir /tmp % 



Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?
 
… J'ai remplacé « Probabilité de panne » par « Risque de panne » dans le print de maintai/cli.py. Après relance de maintai-predict sans réinstaller, le changement est visible immédiatement : « Risque de panne : 95 % (ALERTE) ». C'est parce que pip install -e . ne copie pas le code : il pose un lien vers mon dossier TP\TP4\maintai\. La commande exécute donc toujours le fichier que je modifie.



## 3. Sprint 2 : construire et installer le wheel

Sortie de `dir dist` après `python -m build` :

```
Successfully built maintai-0.2.0.tar.gz and maintai-0.2.0-py3-none-any.whl
total 56
drwxr-xr-x   4 macbookair  staff    128 19 nov 10:57 .
drwxr-xr-x@ 21 macbookair  staff    672 19 nov 10:57 ..
-rw-r--r--   1 macbookair  staff  11607 19 nov 10:57 maintai-0.2.0-py3-none-any.whl
-rw-r--r--   1 macbookair  staff  12403 19 nov 10:57 maintai-0.2.0.tar.gz
Archive:  dist/maintai-0.2.0-py3-none-any.whl
  Length      Date    Time    Name
---------  ---------- -----   ----
       95  11-02-2026 17:56   maintai/__init__.py
     1338  11-02-2026 17:56   maintai/cli.py
     1498  11-02-2026 17:50   maintai/client.py
     1505  10-20-2026 14:55   maintai/config.py
      787  10-20-2026 14:55   maintai/data.py
     1327  10-20-2026 14:55   maintai/dataset.py
     1188  10-20-2026 14:55   maintai/predict.py
     3058  10-20-2026 14:55   maintai/train.py
        0  10-20-2026 14:55   maintai/api/__init__.py
     1915  10-20-2026 14:55   maintai/api/main.py
     1186  10-20-2026 14:55   maintai/api/schemas.py
      747  10-20-2026 14:55   maintai/api/security.py
     3412  11-19-2026 10:57   maintai-0.2.0.dist-info/METADATA
       91  11-19-2026 10:57   maintai-0.2.0.dist-info/WHEEL
       53  11-19-2026 10:57   maintai-0.2.0.dist-info/entry_points.txt
        8  11-19-2026 10:57   maintai-0.2.0.dist-info/top_level.txt
     1290  11-19-2026 10:57   maintai-0.2.0.dist-info/RECORD
---------                     -------
    19498                     17 files
(.venv) macbookair@MacBookAir maintai-starter-tp4 % 

```

Contenu du wheel (`tar -tf dist\maintai-0.2.0-py3-none-any.whl`). Le modèle, les tests et `ui/` y sont-ils ? Pourquoi ?

```
Non : le modèle, les tests et ui/ ne sont pas dans le wheel. Dans pyproject.toml, [tool.setuptools.packages.find] a include = ["maintai*"], donc seul le dossier maintai/ entre dans le package. models/ contient des fichiers générés (model.joblib, model_info.json), pas du code, et tests/ et ui/ ne servent pas à utiliser la commande. Le wheel contient donc le code, mais pas le modèle : il faut le livrer à part et indiquer son dossier avec MAINTAI_MODELS_DIR.

Dans un environnement neuf (%TEMP%\essai), installez le wheel et lancez maintai-predict :

Étape	Ce qui s'affiche
sans MAINTAI_MODELS_DIR	Modèle introuvable : /Users/macbookair/Desktop/maintai-starter-tp4>/models\model.joblib, puis « Entraînez-le (python -m maintai.train) ou indiquez son dossier dans MAINTAI_MODELS_DIR. »
avec MAINTAI_MODELS_DIR vers vos models	3 InconsistentVersionWarning (StandardScaler, LogisticRegression, Pipeline : « Trying to unpickle estimator ... from version 1.8.0 when using version 1.9.1 »), puis Probabilité de panne : 95 % (ALERTE)
après pip install scikit-learn==1.8.0	Plus aucun avertissement : seulement Probabilité de panne : 95 % (ALERTE)
D'où vient l'avertissement InconsistentVersionWarning ? Quelle ligne de models/model_info.json permet de le comprendre ?

L'avertissement vient d'un décalage de version : le modèle (model.joblib) a été entraîné et écrit avec scikit-learn 1.8.0, mais pip a installé la version 1.9.1 avec le wheel, parce que pyproject.toml demande seulement scikit-learn>=1.5 (« au moins »). Au chargement, scikit-learn voit que le modèle a été écrit par une autre version et prévient que les résultats peuvent être faux. La ligne "sklearn_version": "1.8.0" de models/model_info.json donne la version qui a écrit le modèle. Avec pip install scikit-learn==1.8.0, comme dans requirements.txt (« exactement »), l'avertissement disparaît.


```


Dans un environnement neuf (`%TEMP%\essai`), installez le wheel et lancez `maintai-predict` :

| Étape | Ce qui s'affiche |
|---|---|
| sans `MAINTAI_MODELS_DIR` | |
| avec `MAINTAI_MODELS_DIR` vers vos `models` | |
| après `pip install scikit-learn==1.8.0` | |

D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

…

## 4. Questions de compréhension

Quelle différence entre requirements.txt et la liste dependencies de pyproject.toml ? dependencies dit « au moins » (>=) : elle liste ce dont le package a besoin pour fonctionner et reste souple, pour pouvoir s'installer à côté d'autres packages. requirements.txt dit « exactement » (==) : il fixe les versions de tout l'environnement, pour retrouver les mêmes conditions. C'est nécessaire pour un modèle, qui se relit avec la version qui l'a écrit : avec scikit-learn>=1.5, pip a installé la 1.9.1 et on a eu l'InconsistentVersionWarning, alors que le modèle avait été écrit avec la 1.8.0 (==1.8.0).
Quelle différence entre pip install -e . et pip install dist\maintai-0.2.0-py3-none-any.whl ? pip install -e . (éditable) pose dans site-packages un lien vers mon dossier TP\TP4\maintai\ : mes modifications sont visibles tout de suite (le message de cli.py a changé sans réinstaller). Il sert à développer. Le wheel est une copie du code, figée au moment du python -m build : modifier TP\TP4 ne change plus rien dans l'environnement où il est installé, il faut reconstruire et réinstaller. Il sert à livrer à quelqu'un d'autre.
Qu'est-ce qu'un « point d'entrée » ([project.scripts]) ? Où pip crée-t-il le fichier maintai-predict.exe ? Un point d'entrée associe un nom de commande à une fonction Python, au format nom = "module:fonction" (ici maintai-predict = "maintai.cli:main"). À l'installation, pip crée un petit fichier .exe qui appelle cette fonction. Il le place dans le dossier Scripts de l'environnement, donc .venv\Scripts\maintai-predict.exe, ce qui rend la commande disponible quand le .venv est activé. Il ne marche donc pas si le .venv n'est pas activé. …

## 5. Le rendu Git

- Lien de la pull request : …
- Le tag `tp4` existe sur GitHub : oui / non
- `git status` avant le commit : `dist/`, `build/` ou `maintai.egg-info/` apparaissaient-ils ? oui / non

## 6. Ce qui reste flou

…







