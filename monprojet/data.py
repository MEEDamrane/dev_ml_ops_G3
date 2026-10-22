
"""Chargement et découpage des données.

À vous d'écrire load_data() et split(). Les tests de tests/test_data.py disent ce qui est attendu.
"""
from math import ceil

import pandas as pd
from sklearn.model_selection import train_test_split

from monprojet import config


def load_data(path=None) -> pd.DataFrame:
    """Lit le fichier CSV et renvoie un DataFrame.

    Attendu :
    - lire config.DATA_PATH (ou `path` s'il est donné) ;
    - si la colonne config.TARGET n'existe pas, lever une ValueError avec un message clair ;
    - retirer les lignes où la cible est manquante.

    Pistes : pd.read_csv, df.columns, df.dropna(subset=[...]).
    """
    # Choisir le chemin du fichier CSV
    data_path = config.DATA_PATH if path is None else path

    # Lire le fichier CSV
    df = pd.read_csv(data_path)

    # Vérifier que la colonne cible existe
    if config.TARGET not in df.columns:
        raise ValueError(
            f"La colonne cible '{config.TARGET}' n'existe pas dans le fichier CSV."
        )

    # Supprimer les lignes où la cible est manquante
    df = df.dropna(subset=[config.TARGET]).copy()

    return df


def feature_columns(df: pd.DataFrame) -> list:
    """Les colonnes d'entrée : celles de config.FEATURES, ou toutes sauf la cible et la date. (Fournie.)"""
    if config.FEATURES is not None:
        return list(config.FEATURES)
    excluded = {config.TARGET, config.TIME_COLUMN}
    return [c for c in df.columns if c not in excluded]


def split(df: pd.DataFrame):
    """Renvoie X_train, X_test, y_train, y_test.

    Attendu :
    - X = les colonnes de feature_columns(df) ; y = la colonne cible ;
    - si config.SPLIT == "random" : un découpage aléatoire de taille config.TEST_SIZE,
      avec la graine config.SEED, et stratifié sur y pour une classification ;
    - si config.SPLIT == "chronologique" : trier selon config.TIME_COLUMN et garder
      les lignes les plus récentes pour le test (le modèle apprend le passé, il est testé sur le futur).

    Pistes : train_test_split(..., test_size=..., random_state=..., stratify=...) ;
    pd.to_datetime(...).argsort() ; X.iloc[...].
    """
    # Définir les variables d'entrée et la cible
    features = feature_columns(df)
    X = df[features]
    y = df[config.TARGET]

    # Découpage aléatoire
    if config.SPLIT == "random":

        # Stratifier les données pour une classification
        stratify = None

        if config.TASK == "classification" and y.nunique() > 1:
            counts = y.value_counts()

            n_test = (
                int(len(df) * config.TEST_SIZE)
                if isinstance(config.TEST_SIZE, float)
                else config.TEST_SIZE
            )
            n_train = len(df) - n_test

            # La stratification nécessite au moins deux exemples par classe
            # et suffisamment de lignes dans chaque ensemble
            if (
                counts.min() >= 2
                and n_test >= y.nunique()
                and n_train >= y.nunique()
            ):
                stratify = y

        return train_test_split(
            X,
            y,
            test_size=config.TEST_SIZE,
            random_state=config.SEED,
            stratify=stratify,
        )

    # Découpage chronologique
    elif config.SPLIT == "chronologique":

        # Vérifier la colonne de date
        if (
            config.TIME_COLUMN is None
            or config.TIME_COLUMN not in df.columns
        ):
            raise ValueError(
                "La colonne TIME_COLUMN doit être définie "
                "et exister dans le DataFrame."
            )

        # Trier les données de la plus ancienne à la plus récente
        order = pd.to_datetime(df[config.TIME_COLUMN], errors="raise").argsort(
            kind="stable"
        )

        # Calculer le nombre de lignes réservées au test
        n_test = (
            ceil(len(df) * config.TEST_SIZE)
            if isinstance(config.TEST_SIZE, float)
            else config.TEST_SIZE
        )

        if n_test <= 0 or n_test >= len(df):
            raise ValueError(
                "TEST_SIZE doit laisser au moins une ligne "
                "pour l'entraînement et une ligne pour le test."
            )

        # Les données récentes servent au test
        train_idx = order[:-n_test]
        test_idx = order[-n_test:]

        return (
            X.iloc[train_idx],
            X.iloc[test_idx],
            y.iloc[train_idx],
            y.iloc[test_idx],
        )

    else:
        raise ValueError(
            f"Valeur SPLIT invalide : '{config.SPLIT}'. "
            "Utilisez 'random' ou 'chronologique'."
        )
