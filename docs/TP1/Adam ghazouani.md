
# TPO : MaintAI

**Nom :** Adam Ghzaouni  
**Groupe :** G3  
**Module :** Développement et déploiement d’applications intelligentes — S4

---

## 1. Le problème

L’objectif de ce projet est de prédire le nombre de repas servis chaque jour dans une cantine scolaire.

Cette prévision permet d’aider les responsables à mieux préparer les quantités nécessaires, à limiter le gaspillage alimentaire et à éviter les pénuries de repas.

La variable cible est `repas_servis`.

Il s’agit d’un problème de **régression**, car la valeur à prédire est un nombre.

Les variables explicatives comprennent notamment :

- Le jour
- Le nombre d’inscrits
- Le menu
- La température
- La pluie
- Les examens
- Les sorties scolaires
- La veille des vacances
- Le nombre de repas servis la semaine précédente

---

## 2. Données et découpage

Le fichier utilisé est `data/cantine_repas.csv`.

Il contient **340 observations**.

Le découpage des données est chronologique :

- **Entraînement :** les 272 observations les plus anciennes (80 %).
- **Test :** les 68 observations les plus récentes (20 %).

Les données ne sont pas mélangées aléatoirement afin d’évaluer les modèles sur des observations plus récentes que celles utilisées pour l’entraînement.

La colonne `date` sert uniquement à ordonner les observations et n’est pas transmise aux modèles.

---

## 3. Résultats sur le jeu de test

| Modèle | MAE | RMSE | R² |
|---|---:|---:|---:|
| Régression linéaire | **22,239** | **28,170** | **0,883** |
| Forêt aléatoire | 31,845 | 41,540 | 0,746 |
| Arbre de décision | 46,000 | 59,710 | 0,475 |
| Baseline | 70,271 | 88,416 | -0,151 |

La métrique principale est la **MAE (Mean Absolute Error)**.

Elle représente l’erreur absolue moyenne en nombre de repas. Plus elle est faible, plus les prédictions sont proches des valeurs réelles.

La **RMSE** pénalise davantage les erreurs élevées, tandis que le **R²** mesure la capacité du modèle à expliquer la variation du nombre de repas servis.

---

## 4. Modèle retenu

Le modèle retenu est la **régression linéaire**, car il obtient la MAE la plus faible parmi les modèles évalués, avec une erreur absolue moyenne de **22,239 repas**.

### 4.1. Réduction absolue de l’erreur

La réduction de la MAE par rapport à la baseline est :

```text
70,271 - 22,239 = 48,032 repas
```

### 4.2. Réduction relative de l’erreur

La réduction relative est calculée par :

```text
((70,271 - 22,239) / 70,271) × 100 ≈ 68,35 %
```

Le modèle réduit donc l’erreur absolue moyenne d’environ **68,35 %** par rapport à la baseline.

Son coefficient **R² de 0,883** indique une bonne capacité explicative sur le jeu de test, sans garantir des performances identiques sur toutes les périodes futures.

---

## 5. Le critère d’acceptation est-il atteint ?

Aucun seuil métier précis n’a encore été défini dans le projet.

Il n’est donc pas possible d’affirmer formellement que le critère d’acceptation est atteint.

Cependant, la régression linéaire améliore nettement les résultats par rapport à la baseline et constitue le meilleur modèle parmi ceux évalués.

Pour valider définitivement son utilisation, il faudrait définir avec le responsable de la cantine une erreur moyenne maximale acceptable, en tenant compte :

- Du coût d’un repas préparé en trop.
- Des conséquences d’un repas manquant.
- Des besoins réels de la cantine.

---

## 6. Points restant à clarifier

### 6.1. Seuil métier

Définir la MAE maximale acceptable.

### 6.2. Coûts opérationnels

Estimer le coût d’un repas préparé en trop et celui d’un repas manquant.

### 6.3. Périodes particulières

Vérifier la stabilité des performances pendant les vacances, les examens et les événements scolaires.

### 6.4. Disponibilité des variables

Vérifier que `repas_semaine_precedente` est disponible au moment de la prédiction, sans utiliser d’informations futures.

### 6.5. Réentraînement

Définir la fréquence de mise à jour du modèle lorsque de nouvelles observations sont disponibles.

### 6.6. Validation temporelle

Évaluer le modèle sur plusieurs découpages chronologiques afin de vérifier sa robustesse.

---

## 7. Conclusion

La **régression linéaire** obtient les meilleurs résultats sur le jeu de test chronologique.

Avec une **MAE de 22,239 repas**, elle surpasse nettement la baseline ainsi que les modèles de forêt aléatoire et d’arbre de décision.

Elle est donc sélectionnée comme **modèle final à ce stade du projet**.

Avant son utilisation opérationnelle, il reste nécessaire de :

- Définir un seuil d’acceptation métier.
- Vérifier la disponibilité des variables au moment de la prédiction.
- Confirmer la stabilité des performances sur différentes périodes.

---

**Réalisé par :** Adam Ghzaouni  
**Groupe :** G3  
**Module :** Développement et déploiement d’applications intelligentes — S4
