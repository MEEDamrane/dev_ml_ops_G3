# Compte rendu Â· TP4 : MaintAI devient un package Python

**Groupe :** Ã  complÃ©ter  Â·  **Membres :** Ã  complÃ©ter  Â·  **Date :** 12 novembre 2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP4.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

DerniÃ¨re ligne de `python -m pytest` juste aprÃ¨s `pip install -r requirements.txt` :

```
2 failed, 25 passed (durÃ©e non relevÃ©e)
```

Quels sont les deux tests qui Ã©chouent, et pourquoi ?

Les deux tests de `tests/test_package.py` :

- `test_installed_version_matches_the_code` Ã©choue car `maintai` n'a pas encore
  Ã©tÃ© installÃ© dans l'environnement et ses mÃ©tadonnÃ©es de distribution ne sont
  pas disponibles.
- `test_command_is_declared` Ã©choue car le point d'entrÃ©e
  `maintai-predict` n'est pas encore enregistrÃ© par pip.

Ces deux tests vÃ©rifient l'installation du package et la crÃ©ation de sa
commande ; ils passent aprÃ¨s `pip install -e .`.

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Vos sections `dependencies` et `[project.scripts]` :

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

Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

`pytest` est un outil de dÃ©veloppement/test, pas une dÃ©pendance nÃ©cessaire Ã 
l'utilisation du package. `fastapi` est optionnelle : elle sert Ã  l'API, et est
dÃ©clarÃ©e dans l'extra `api` plutÃ´t que dans les dÃ©pendances de base.

Sortie de `pip show maintai` (les quatre premiÃ¨res lignes) :

```
Name: maintai
Version: 0.2.0
Summary: Application de prediction de panne a partir de releves de capteurs
Home-page:
```

DerniÃ¨re ligne de `python -m pytest` Ã  la fin du sprint 1 :

```
27 passed, 1 warning in 3.17s
```

Placez-vous dans un autre dossier (`cd %TEMP%`) et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? OÃ¹ Python trouve-t-il le code de `maintai` ?

Depuis `%TEMP%`, `maintai-predict 72 6 85 15000` a affichÃ© :

```
ProbabilitÃ© de panne : 95 % (ALERTE)
```

La commande `python -c "import maintai; print(maintai.__file__)"` a affichÃ© le
chemin :

```
C:\Users\youssef\Documents\Applications intelligentes\TP4\maintai-starter-tp4\maintai\__init__.py
```

Avec l'installation Ã©ditable, Python charge donc le code directement depuis
le projet, et non depuis une copie installÃ©e dans `site-packages`.

Modifiez le message affichÃ© par `maintai/cli.py`, puis relancez `maintai-predict` sans rÃ©installer. Le changement est-il visible ? Pourquoi ?

Oui. Avec `pip install -e .`, le lanceur importe le module depuis le dossier
source du projet. Une modification de `maintai/cli.py` est donc visible Ã  la
prochaine exÃ©cution, sans rÃ©installation.

## 3. Sprint 2 : construire et installer le wheel

Sortie de `dir dist` aprÃ¨s `python -m build` :

```
maintai-0.2.0-py3-none-any.whl  11624 octets
maintai-0.2.0.tar.gz            12176 octets
```

Contenu du wheel (`tar -tf dist\maintai-0.2.0-py3-none-any.whl`). Le modÃ¨le, les tests et `ui/` y sont-ils ? Pourquoi ?

```
maintai/__init__.py
maintai/cli.py
maintai/client.py
maintai/config.py
maintai/data.py
maintai/dataset.py
maintai/predict.py
maintai/train.py
maintai/api/__init__.py
maintai/api/main.py
maintai/api/schemas.py
maintai/api/security.py
maintai-0.2.0.dist-info/METADATA
maintai-0.2.0.dist-info/WHEEL
maintai-0.2.0.dist-info/entry_points.txt
maintai-0.2.0.dist-info/top_level.txt
maintai-0.2.0.dist-info/RECORD
```

Le modÃ¨le (`models/`), les tests (`tests/`) et l'interface (`ui/`) ne sont pas
dans le wheel. La configuration setuptools ne sÃ©lectionne que les packages
`maintai*` (`[tool.setuptools.packages.find]`) ; ces dossiers sont Ã  cÃ´tÃ© du
package et ne sont donc pas inclus.

Dans un environnement neuf (`%TEMP%\essai`), installez le wheel et lancez `maintai-predict` :

| Ã‰tape | Ce qui s'affiche |
|---|---|
| sans `MAINTAI_MODELS_DIR` | Erreur `ModÃ¨le introuvable` : le wheel ne contient pas `model.joblib`; le message indique le chemin recherchÃ© et suggÃ¨re `MAINTAI_MODELS_DIR`. |
| avec `MAINTAI_MODELS_DIR` vers vos `models` | `ProbabilitÃ© de panne : 95 % (ALERTE)` avec le modÃ¨le fourni et scikit-learn 1.8.0. |
| aprÃ¨s `pip install scikit-learn==1.8.0` | MÃªme prÃ©diction ; l'avertissement de version disparaÃ®t si le modÃ¨le Ã©tait chargÃ© avec une autre version de scikit-learn. |

D'oÃ¹ vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

`InconsistentVersionWarning` est Ã©mis par scikit-learn lors du chargement d'un
modÃ¨le sÃ©rialisÃ© avec une version diffÃ©rente de celle installÃ©e dans
l'environnement. Dans `models/model_info.json`, la ligne
`"sklearn_version": "1.8.0"` indique la version utilisÃ©e pour entraÃ®ner le
modÃ¨le.

## 4. Questions de comprÃ©hension

1. Quelle diffÃ©rence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?
   `requirements.txt` est une liste d'installation pour l'environnement du TP,
   ici avec des versions exactes pour reproduire l'environnement. Les
   `dependencies` de `pyproject.toml` sont les dÃ©pendances d'exÃ©cution du
   package publiÃ© et indiquent des contraintes de versions minimales.
2. Quelle diffÃ©rence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?
   `pip install -e .` installe le projet en mode Ã©ditable : Python utilise les
   fichiers source du dossier de travail, donc les modifications sont visibles
   sans rÃ©installation. L'installation du wheel installe une distribution
   construite et indÃ©pendante de l'arborescence source ; pour prendre en compte
   un changement, il faut reconstruire puis rÃ©installer le wheel.
3. Qu'est-ce qu'un Â« point d'entrÃ©e Â» (`[project.scripts]`) ? OÃ¹ pip crÃ©e-t-il le fichier `maintai-predict.exe` ?
   C'est une association entre un nom de commande et une fonction Python, ici
   `maintai-predict` vers `maintai.cli:main`. Sous Windows, pip crÃ©e le lanceur
   dans le dossier `Scripts` de l'environnement Python actif (par exemple
   `.venv\Scripts\maintai-predict.exe`).

## 5. Le rendu Git

- Lien de la pull request : Ã  complÃ©ter par le groupe aprÃ¨s crÃ©ation de la PR.
- Le tag `tp4` existe sur GitHub : Ã  vÃ©rifier sur le dÃ©pÃ´t distant du groupe.
- `git status` : impossible Ã  relever ici, car le dossier de travail fourni
  n'est pas un dÃ©pÃ´t Git (`fatal: not a git repository`).

## 6. Ce qui reste flou

Rien pour le moment concernant le contenu technique du TP. Les informations
sur la PR et le tag `tp4` restent Ã  complÃ©ter par le groupe depuis son dÃ©pÃ´t
GitHub.

**VÃ©rification finale dans l'environnement de travail :** `python -m pytest -q`
a donnÃ© `27 passed, 1 warning in 3.17s`. Une exÃ©cution antÃ©rieure avait Ã©chouÃ©
au chargement de DLL natives (`pydantic_core` et `pyarrow`) bloquÃ©es par la
politique Application Control de Windows ; cette erreur n'a pas Ã©tÃ© reproduite
lors de la vÃ©rification finale.

