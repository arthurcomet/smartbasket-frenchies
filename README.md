# SmartBasket — Frenchies

Projet d'Introduction to Big Data · Korea University Sejong · semestre 2026-2.

On cherche des produits souvent achetés ensemble dans le jeu de données Instacart avec A-Priori. Ces règles doivent ensuite servir à un agent Upstage Solar pour proposer des produits complémentaires.

## Commencer ici

**Les 30 essais A-Priori sont terminés. Il n'y a rien à relancer pour consulter les résultats.**

| Tu cherches... | Va ici |
|---|---|
| Les conclusions et le seuil conseillé | [Compte rendu A-Priori](reports/apriori_20261118.md) |
| Le tableau des 10 configurations testées | [Résumé CSV](out/apriori_20261118/summary.csv) |
| Les règles calculées sur toutes les commandes à 0,05 % | [Règles CSV](out/apriori_20261118/rules_full_support_0p05.csv) |
| Les consignes pour l'équipe | [Guide d'équipe](docs/GUIDE_EQUIPE.md) et [semaine 11](docs/SEMAINE_11.md) |

## Où sont les fichiers ?

| Emplacement | Rôle |
|---|---|
| [`docs/`](docs/) | Consignes d'équipe et prompt pour l'agent IA |
| [`notebooks/01_data.ipynb`](notebooks/01_data.ipynb) | Chargement des données et premiers essais (semaine 10) |
| [`notebooks/02_apriori_experiments.ipynb`](notebooks/02_apriori_experiments.ipynb) | Notebook Colab pour reproduire la campagne A-Priori |
| [`scripts/apriori_experiments.py`](scripts/apriori_experiments.py) | Code de référence des expériences |
| [`scripts/build_experiment_notebook.py`](scripts/build_experiment_notebook.py) | Génère le notebook 02 depuis le code de référence |
| [`tests/`](tests/) | Tests sur de petits jeux de contrôle |
| [`reports/`](reports/) | Comptes rendus lisibles, semaines 10 et 11 |
| [`out/`](out/) | Fichiers produits : résultats, règles CSV et graphiques |

Le dossier [`out/apriori_20261118/`](out/apriori_20261118/) contient les résultats de la campagne :

- `summary.csv` : une ligne par configuration, avec les statistiques des trois répétitions ;
- `raw_runs.json` : les 30 mesures individuelles ;
- `report.md` : rapport détaillé généré pendant les essais ;
- `metadata.json` : paramètres, versions et empreinte SHA-256 des données ;
- `rules_*.csv` : règles pour chaque configuration, avec confiance et lift non arrondis.

Les autres fichiers directement dans `out/` viennent de la semaine 10. `data_DONOTPUSH/` contient les données locales Instacart : ce dossier est ignoré par Git.

## Résultat des expériences

Cinq seuils ont été testés sur 50 000 commandes, trois sur 250 000, puis deux sur les **3 214 874 commandes prior**. Chaque configuration a été répétée trois fois. Les 30 exécutions ont réussi.

Le seuil **0,05 %** est le candidat principal parmi ceux testés : 11 412 règles et 763 produits couverts sur le jeu complet. Le seuil **0,075 %** consomme moins de ressources, mais couvre 466 produits. Le [compte rendu](reports/apriori_20261118.md) explique les limites de cette comparaison : la qualité des recommandations doit encore être évaluée face à une référence basée sur la popularité.

## Reproduire plus tard (facultatif)

Le [notebook 02](notebooks/02_apriori_experiments.ipynb) fonctionne dans Google Colab. Il peut utiliser un dossier Instacart existant via `DATA_DIR` ou télécharger le jeu depuis [Kaggle](https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis). Dans Colab, la clé Kaggle doit être enregistrée comme secret `KAGGLE_API_TOKEN`.

En local, avec Python, NumPy et pandas :

```bash
python scripts/apriori_experiments.py --data-dir data_DONOTPUSH
```

La méthode cherche des paires de produits, sans utiliser le fichier `train`. Les réglages par défaut limitent chaque processus à 300 secondes, 2 048 Mo de mémoire résidente échantillonnée et 5 millions de compteurs de paires. Un essai interrompu est signalé comme tel. Les résultats sont enregistrés dans un nouveau dossier `out/apriori_<date UTC>/`. Les temps dépendent de la machine et ne se comparent pas directement à ceux du notebook 01.

Après une modification du script de référence, régénérer le notebook et lancer les tests :

```bash
python scripts/build_experiment_notebook.py
python -m unittest discover -s tests -v
```

## Équipe

| Membre | Rôle |
|---|---|
| Victor DUMUR | Chargement et description des données |
| Alexandre GRIMOND | A-Priori et règles d'association |
| Arthur COMET | Agent Solar et outils |
| Louis TURQUIN | Évaluation face à la popularité |
| Merin SALLAMI | Rapport, slides et dépôt |

Le projet répond aux consignes du cours avec A-Priori (MMDS §6.1–6.2), des règles d'association, un agent utilisant ces règles comme outils et le modèle Upstage Solar.
