# Semaine 11 — tâches de chacun (équipe de 4)

Rapport à rendre avant le **1er décembre 23:59**. Le prof a demandé « more deeper technology » : cette semaine on passe aux **3,2 millions de commandes**, on compare **A-Priori et PCY**, on construit le **premier agent Solar** et on **évalue** contre une baseline.

| Qui | Notebook | Statut | Résultat |
|---|---|---|---|
| Alexandre | `02_apriori_experiments.ipynb` | ✅ fait | A-Priori sur tout le dataset, 10 réglages × 3 répétitions |
| Victor | `03_pcy.ipynb` | à lancer **en premier** | PCY contre A-Priori à des seuils plus bas, règles à 0,01 % |
| Arthur | `04_agent.ipynb` | à lancer | Agent Solar avec 2 outils, 5 conversations de test |
| Merin | `05_evaluation.ipynb` + `reports/week11.md` | à lancer **après Victor** | Hit-rate contre la baseline best-sellers, rapport |

**Ordre important** : Victor pousse `out/pcy_week11/` sur GitHub avant que Merin lance le notebook 05, sinon l'évaluation ne trouve que les règles à 0,05 %.

Pour chaque notebook : ouvrir dans Colab depuis GitHub → **Exécution → Tout exécuter** → accepter l'accès au Drive. Les données viennent du dossier `instacart` partagé sur le Drive (voir `GUIDE_EQUIPE.md`).

---

## Victor — PCY contre A-Priori (`03_pcy.ipynb`)

**L'idée en une phrase** : pour recommander plus de produits, il faut baisser le seuil ; A-Priori doit alors compter beaucoup plus de paires au passage 2. PCY profite du passage 1 pour ranger toutes les paires dans des « seaux », et au passage 2 ne compte que les paires dont le seau est fréquent.

**Ce que fait le notebook** (environ 10 à 15 min dans Colab) :
1. Charge les 32 M de lignes en deux tableaux NumPy.
2. Passage 1 : compte les produits, et range toutes les paires dans 1 M, 4 M et 16,8 M de seaux.
3. Passage 2 à 0,05 / 0,02 / 0,01 / 0,005 % : compte A-Priori et PCY, et **vérifie qu'ils trouvent exactement les mêmes paires fréquentes**.
4. Contrôle : à 0,05 % on doit retrouver les chiffres d'Alexandre (3 402 produits, 4 538 892 paires, 5 706 paires fréquentes).
5. Sauvegarde les règles à 0,01 % pour l'agent et l'évaluation.

**À pousser** : `notebooks/03_pcy.ipynb` (avec les sorties) et le dossier `out/pcy_week11/`.

**À savoir dire** : la dernière cellule du notebook contient le texte de présentation à compléter.

---

## Arthur — Agent Solar (`04_agent.ipynb`)

**L'idée** : l'utilisateur décrit son panier, Solar appelle `search_products` pour trouver les noms exacts, puis `recommend_for_basket`, qui lit les règles d'A-Priori et classe par lift. Solar n'invente rien.

**Avant de lancer** : clé sur console.upstage.ai → Secrets Colab, nom `UPSTAGE_API_KEY`. Si la cellule de connexion échoue, changer `MODEL` (solar-pro3, solar-pro4) ou `BASE_URL` (`https://api.upstage.ai/v1/solar`) dans la 1re cellule.

**À pousser** : `notebooks/04_agent.ipynb` (avec les conversations) et `out/agent_week11/`.

---

## Merin — Évaluation + rapport (`05_evaluation.ipynb`, `reports/week11.md`)

**L'idée** : 131 209 commandes que A-Priori n'a jamais vues (fichier *train*). Dans chacune, on cache un produit au hasard et on regarde s'il revient dans le top 5 / top 10 de chaque méthode : best-sellers, règles par lift, règles par confiance, règles + best-sellers.

**À lancer après** que Victor a poussé `out/pcy_week11/`. Durée : 5 à 10 min.

**À pousser** : `notebooks/05_evaluation.ipynb`, `out/eval_week11/`, puis `reports/week11.md` complété avec les chiffres des notebooks 03, 04 et 05 (les crochets `[ ]`).

**Soumission LMS** : le contenu de `reports/week11.md` + le lien du repo, avant le 1er déc. 23:59.
