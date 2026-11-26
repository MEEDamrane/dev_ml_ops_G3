# TPO : MaintAI

*Nom :* SalahEddine Elmechrafi
*Groupe :* G3
*Date :* 22/10/2026
*Cours :* Développement et déploiement d'applications intelligentes — S4

---

## 1. Le problème

Prédire le **nombre de repas servis** chaque jour dans une cantine scolaire à partir de variables contextuelles (nombre d'inscrits, menu du jour, météo, périodes d'examens, sorties scolaires, veille de vacances).
Une mauvaise prédiction entraîne soit du **gaspillage alimentaire** (surestimation), soit des **repas insuffisants** (sous-estimation).

## 2. Données et découpage

| Élément | Valeur |
|---|---|
| Fichier | `data/cantine_repas.csv` |
| Lignes | 340 |
| Colonnes | `inscrits`, `jour`, `menu`, `temperature_c`, `pluie_mm`, `examens`, `sortie_scolaire`, `veille_vacances`, `repas_semaine_precedente` |
| Cible | `repas_servis` (variable continue) |
| Type de problème | Régression |
| Découpage | Chronologique (80 % entraînement, 20 % test) |
| Colonne de tri | `date` |
| Graine | 42 |

## 3. Résultats sur le jeu de test

| Modèle | MAE ↓ | RMSE ↓ | R² ↑ |
|---|---|---|---|
| **Linear Regression** | **22.239** | **28.170** | **0.883** |
| Random Forest | 31.845 | 41.540 | 0.746 |
| Decision Tree | 46.000 | 59.710 | 0.475 |
| Baseline (moyenne) | 70.271 | 88.416 | −0.151 |

*Métrique principale :* **MAE** (Mean Absolute Error) — elle donne directement l'erreur moyenne en nombre de repas, facilement interprétable pour le gestionnaire de la cantine.

## 4. Le critère d'acceptation est-il atteint ?

**Critère proposé :** MAE ≤ 30 repas (erreur acceptable pour la gestion quotidienne).

✅ **Oui.** La régression linéaire atteint une MAE de **22.24 repas**, bien en dessous du seuil de 30.
Elle bat la baseline de **48.03 repas** en valeur absolue, soit une amélioration de **68 %**.

## 5. Décision

**Modèle retenu : Régression linéaire** (`LinearRegression`)

- Meilleur score sur les trois métriques (MAE, RMSE, R²).
- Modèle simple, rapide, interprétable — les coefficients permettent de comprendre l'impact de chaque variable.
- R² de 0.883 : le modèle explique **88 %** de la variance du nombre de repas servis.

## 6. Ce qui reste flou / Limites

- **Taille du jeu de test** : seulement ~68 jours de test (20 % de 340) — les performances pourraient varier sur une plus longue période.
- **Saisonnalité non complète** : les données couvrent environ une année scolaire ; le modèle n'a pas vu plusieurs cycles annuels.
- **Valeurs manquantes** : la colonne `repas_semaine_precedente` a 60 valeurs manquantes (imputées par la médiane).
- **Événements exceptionnels** : grèves, jours fériés imprévus ou épidémies ne sont pas modélisés.
- **Decision Tree en surapprentissage** : la forte différence entre Decision Tree et Random Forest suggère un surapprentissage du premier.
