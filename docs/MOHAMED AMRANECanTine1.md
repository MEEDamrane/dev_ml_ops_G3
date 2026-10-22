# TPO : MaintAI

**Nom :** Mohamed Amrane  
**Groupe :** G3  
**Module :** Développement et déploiement d’applications intelligentes — S4

## Le problème

L’objectif est de prédire le nombre de repas servis chaque jour dans une cantine scolaire. Cette prévision peut aider les responsables à mieux préparer les quantités, limiter le gaspillage alimentaire et éviter un manque de repas.

La variable cible est `repas_servis`. Il s’agit d’un problème de **régression**, car la valeur à prédire est un nombre.

Les variables explicatives comprennent notamment le jour, le nombre d’inscrits, le menu, la température, la pluie, les examens, les sorties scolaires, la veille des vacances et le nombre de repas servis la semaine précédente.

## Données et découpage

Le fichier utilisé est `data/cantine_repas.csv`. Il contient 340 observations.

Le découpage est chronologique :

- les 272 observations les plus anciennes sont utilisées pour l’entraînement ;
- les 68 observations les plus récentes sont utilisées pour le test ;
- les données ne sont pas mélangées aléatoirement afin de tester les modèles sur le futur.

La colonne `date` sert uniquement à ordonner les observations et n’est pas transmise aux modèles.

## Résultats sur le jeu de test

| Modèle | MAE | RMSE | R² |
|---|---:|---:|---:|
| Régression linéaire | **22,239** | **28,170** | **0,883** |
| Forêt aléatoire | 31,845 | 41,540 | 0,746 |
| Arbre de décision | 46,000 | 59,710 | 0,475 |
| Baseline | 70,271 | 88,416 | -0,151 |

La métrique principale est la **MAE** (*Mean Absolute Error*). Elle représente l’erreur absolue moyenne exprimée en nombre de repas. Une MAE plus faible indique un meilleur modèle.

## Modèle retenu

Le modèle retenu est la **régression linéaire**, car il obtient la MAE la plus faible : **22,239 repas**. Son erreur moyenne est inférieure de **48,032 repas** à celle de la baseline, soit une réduction d’environ **68,35 %**.

Son coefficient R² de **0,883** indique également que le modèle explique une grande partie de la variation du nombre de repas servis sur le jeu de test.

## Le critère d’acceptation est-il atteint ?

Aucun seuil métier précis n’a encore été défini dans le projet. Il n’est donc pas possible d’affirmer formellement que le critère d’acceptation est atteint.

Cependant, la régression linéaire améliore nettement la baseline. Elle constitue le meilleur modèle parmi ceux évalués. Pour valider définitivement son utilisation, il faudrait convenir avec le responsable de la cantine d’une erreur moyenne maximale acceptable, par exemple en fonction du coût d’un repas manquant ou gaspillé.

## Ce qui reste flou

- Le seuil métier maximal acceptable pour la MAE.
- Le coût réel d’un repas préparé en trop ou d’un repas manquant.
- La stabilité des performances pendant les périodes particulières comme les vacances, les examens ou les événements scolaires.
- La méthode de calcul et la disponibilité réelle de `repas_semaine_precedente` au moment de la prédiction.
- La fréquence prévue de réentraînement du modèle lorsque de nouvelles données seront disponibles.

## Conclusion

La régression linéaire donne les meilleurs résultats sur les données de test chronologiques. Avec une erreur moyenne d’environ **22 repas**, elle surpasse clairement la baseline et les modèles à base d’arbres testés. Elle est donc sélectionnée comme modèle final à ce stade du projet.
