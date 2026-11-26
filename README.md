# Dépôt MLOps — Groupe 3

Le dépôt est organisé en deux parties principales :

| Dossier | Contenu |
|---|---|
| [`tp/`](tp/) | Travaux pratiques, comptes rendus et versions réalisées par les membres du groupe |
| [`projet/`](projet/) | Projet principal de comparaison et d'entraînement de modèles |

## Utiliser le projet principal

Depuis la racine du dépôt :

```powershell
cd projet
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest
```

Les instructions détaillées se trouvent dans [`projet/README.md`](projet/README.md).

## Consulter les TP

Les différents rendus ont été conservés séparément dans [`tp/`](tp/) afin d'éviter d'écraser les variantes portant le même numéro.
