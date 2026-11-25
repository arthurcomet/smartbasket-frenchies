# Guide de l'équipe Frenchies

À lire une fois en entier (10 min). Tout ce qu'il faut pour travailler sur le projet.

## 1. Le projet en 30 secondes

**SmartBasket** : on prend 3,2 millions de vraies commandes d'un supermarché en ligne (Instacart). Avec **A-Priori** (lab 6), on trouve les produits souvent achetés ensemble. Ensuite un **chatbot Upstage Solar** utilise ces résultats : tu lui décris ton panier, il te propose d'autres produits et explique pourquoi.

Le prof impose **3 conditions, toutes en même temps** :

| Condition | Chez nous |
|---|---|
| Une méthode big data du cours | Frequent itemsets : A-Priori (+ PCY si besoin) |
| Un agent LLM (outil de la semaine 2) | Le chatbot appelle nos fonctions Python comme outils |
| Le modèle Upstage Solar | Le chatbot tourne sur Solar |

Le projet vaut **60 % de la note**. Chaque semaine on rend un **progress report** ; en semaine 15, présentation + évaluation par les pairs.

## 2. Ce qui est déjà fait (semaine 10)

Tout est dans `notebooks/01_data.ipynb` et `out/`. Les chiffres à connaître :

- **Données** : 3 214 874 commandes, 32,4 M de lignes, 49 677 produits, ~10 produits par commande.
- **Mémoire** : 1 038 Mo avec les types par défaut → 357 Mo en forçant `int32/int16/int8` (−66 %).
- **A-Priori** sur 50 000 commandes, seuil 0,5 % (250 paniers) : 257 produits fréquents, 31 308 compteurs de paires au lieu de 426 millions, 82 paires fréquentes, 164 règles, 0,48 s.
- **Résultat clé** : triées par *confiance*, les règles recommandent toutes des bananes (dans 15 % des commandes). Triées par *lift*, on a de vraies associations : citron vert → coriandre (×6,1), ail → oignon (×5,9). **On trie par lift.**

Les 3 mots à maîtriser :
- **Support** : dans combien de paniers la paire apparaît.
- **Confiance A→B** : parmi les paniers avec A, la part qui a aussi B.
- **Lift** : confiance ÷ popularité de B. Au-dessus de 1 = vrai lien.

## 3. Ce que le prof attend (à garder en tête)

Dans tous les labs, il note la même chose : **implémenter, mesurer, comparer à une baseline**, avec de vrais chiffres et un regard critique.

Chaque progress report contient :
1. Ce qu'on avait prévu cette semaine
2. Ce qui marche, **avec une preuve** (chiffre, graphique ou log)
3. Ce qui a cassé ou bloque
4. Ce qu'on fait la semaine suivante
5. Qui a fait quoi

Donc pour ta tâche : **garde toujours les vraies sorties** (temps, mémoire, erreurs). Une erreur bien expliquée vaut autant qu'un succès dans le rapport. On n'invente jamais un problème ni un chiffre.

## 4. Installation (une seule fois, 10 min)

1. **GitHub** : envoie ton pseudo à Arthur pour qu'il t'ajoute au repo (accepte l'invitation reçue par mail).
2. **Données (Google Drive)** : Arthur partage avec toi un dossier Drive nommé `instacart`. Ouvre-le, clic droit sur le dossier → **Organiser → Ajouter un raccourci** → **Mon Drive**. Garde le nom `instacart`.
3. **Colab** : va sur colab.research.google.com → **Fichier → Ouvrir un notebook → GitHub** → tape `arthurcomet/smartbasket-frenchies` → ouvre `notebooks/01_data.ipynb`.
4. **Exécution → Tout exécuter**. Colab demande l'accès à ton Drive : accepte. Ça prend 3 à 5 min. Si tu obtiens les mêmes chiffres que ci-dessus, tout est bon.

Plan B, si le Drive ne marche pas : crée un compte sur kaggle.com → **Settings** → **API** → **Create New Token**, puis dans Colab icône 🔑 → secret `KAGGLE_API_TOKEN` avec ce token → active **Accès au notebook**. Le notebook télécharge alors les données tout seul.

## 5. Comment travailler

- **Un notebook par tâche**, numéroté (ex. `notebooks/03_support_sweep.ipynb`). Ne modifie pas le notebook de quelqu'un d'autre.
- Pour démarrer : ouvre `01_data.ipynb`, puis **Fichier → Enregistrer une copie dans Drive**, renomme-la, et garde les cellules 0 à 3 (chargement des données). Ajoute ton travail en dessous.
- **Graine aléatoire fixe** : `SEED = 42` partout, pour que les chiffres soient reproductibles.
- Tes résultats vont dans `out/` avec un nom clair : `evidence_week11_<sujet>.json`, `<sujet>.png`.

**Mettre ton travail sur GitHub** (deux façons) :
- depuis Colab : **Fichier → Enregistrer une copie dans GitHub** → repo `arthurcomet/smartbasket-frenchies`, chemin `notebooks/0X_nom.ipynb`, coche « Include a link to Colab » ;
- ou sur github.com : **Add file → Upload files**, en tapant `notebooks/` ou `out/` devant le nom du fichier.

Message de commit : court et clair, ex. `Week 11: support sweep 0.5% to 0.05%`.

## 6. Règles de sécurité (le repo est public)

- **Jamais de token, mot de passe ou clé API** dans un notebook, un fichier ou un message de commit. Toujours via les **Secrets Colab** (`userdata.get("NOM")`).
- Si tu as collé un token par erreur : préviens Arthur et **régénère-le** tout de suite sur le site concerné.
- Les données Kaggle ne vont pas dans le repo (trop lourdes) : le notebook les télécharge à chaque fois.

## 7. Calendrier

| Semaine | Objectif | Rendu |
|---|---|---|
| 10 | Données + premier A-Priori | ✅ rendu |
| 11 | A-Priori sur tout le dataset, PCY, premier agent Solar, évaluation | Report avant le **1er déc. 23:59** |
| 12 | MinHash/LSH (produits similaires), agent avec 3 outils | Report + présentation (à confirmer) |
| 13 | Agent en conversation (noms de produits) | Report |
| 14 | Évaluation contre la baseline popularité | Report |
| 15 | Présentation finale + démo | Présentation + peer evaluation |

**Deadline interne : chaque samedi soir**, chacun envoie à Merin ses chiffres (copie de son `evidence_*.json`) + 2-3 phrases « ce qui a marché / ce qui a cassé ». Merin assemble le rapport.

Tâches détaillées de la semaine : `docs/SEMAINE_11.md`. Prompt à donner à ton IA : `docs/PROMPT_IA.md`.
