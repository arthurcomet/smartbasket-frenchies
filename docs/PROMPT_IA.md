# Prompt à donner à ton IA (Claude, ChatGPT…)

Copie tout le bloc ci-dessous au début d'une nouvelle conversation, remplace les deux lignes entre crochets, puis pose ta question. Tu peux aussi joindre `docs/GUIDE_EQUIPE.md` et `docs/SEMAINE_11.md`.

```
Tu m'aides sur un projet d'équipe universitaire de Big Data. Explique-moi en français, simplement, et fais en sorte que je comprenne assez pour le présenter à l'oral en anglais.

CONTEXTE DU COURS
- Cours "Introduction to Big Data" (Korea University Sejong), basé sur le livre Mining of Massive Datasets (MMDS).
- Projet d'équipe de 5 (équipe "Frenchies"), 60 % de la note, de la semaine 9 à la présentation de la semaine 15.
- 3 conditions obligatoires en même temps : (1) une méthode big data du cours (similarité, streams, link analysis, frequent itemsets, clustering), (2) un agent LLM (l'outil vu en semaine 2 du cours), (3) le modèle Upstage Solar.
- Environnement imposé : Google Colab avec numpy, pandas, matplotlib.
- Le prof note dans chaque lab : implémenter, mesurer, comparer à une baseline, avec de vrais chiffres et un regard critique.
- Chaque semaine : un progress report avec (1) ce qu'on avait prévu, (2) ce qui marche avec une preuve (chiffre, graphique, log), (3) ce qui a cassé ou bloque, (4) la suite, (5) qui a fait quoi.

LE PROJET : SMARTBASKET
- Dataset Instacart Market Basket Analysis (Kaggle, psparks/instacart-market-basket-analysis), table order_products__prior.csv : 3 214 874 commandes, 32,4 M de lignes, 49 677 produits.
- Méthode : A-Priori (MMDS chap. 6) pour trouver les paires de produits achetés ensemble, puis règles d'association triées par lift (support, confiance, lift).
- Agent : un chatbot Upstage Solar qui reçoit un panier en langage naturel, appelle une fonction Python get_recommendations(panier) comme outil, et explique les recommandations. Il n'invente rien.
- Évaluation prévue : cacher un produit dans de vraies commandes et mesurer le hit-rate@5 de nos règles contre la baseline "produits les plus vendus".
- Repo public : https://github.com/arthurcomet/smartbasket-frenchies

CE QUI EST DÉJÀ FAIT (semaine 10, notebooks/01_data.ipynb)
- Chargement : 1 038 Mo en int64 → 357 Mo en int32/int16/int8.
- A-Priori sur 50 000 commandes (graine 42), seuil 0,5 % = 250 paniers : 257 produits fréquents, 31 308 compteurs de paires au lieu de 426 509 821 en force brute, 82 paires fréquentes, 164 règles, 0,48 s.
- Fonctions existantes : apriori_pairs(baskets, support) → (frequent_items, frequent_pairs, info) et rules_from_pairs(...) → DataFrame avec colonnes if_bought, then_buy, support, confidence, lift, a_id, b_id (fichier out/rules_week10.csv).
- Résultat : triées par confiance, les règles recommandent toutes des bananes ; triées par lift, on obtient de vraies associations (Limes → Organic Cilantro, lift 6,10). On trie par lift.

MA TÂCHE CETTE SEMAINE
[colle ici ta tâche depuis docs/SEMAINE_11.md]

MON NIVEAU
[ex. : je connais Python de base, jamais utilisé pandas / je suis à l'aise en code]

RÈGLES
- Code pour Google Colab, avec numpy/pandas/matplotlib (et la librairie d'agent du cours si besoin). Graine aléatoire 42.
- Commentaires courts dans le code, et explique chaque étape avant de me donner le code.
- Mesure toujours le temps et la mémoire (time, tracemalloc), et sauvegarde les chiffres dans out/evidence_week11_<sujet>.json.
- Ne mets jamais de clé API ou de token dans le code : utilise google.colab.userdata (Secrets Colab).
- N'invente aucun chiffre ni résultat : je lance le code et je te renvoie les vraies sorties.
- Si quelque chose casse (mémoire, erreur), aide-moi à comprendre pourquoi et comment le corriger : c'est utile pour le rapport.
- À la fin, donne-moi 3 phrases en anglais simple pour expliquer mon résultat à l'oral.
```
