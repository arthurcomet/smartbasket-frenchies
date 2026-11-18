# Semaine 11 — tâches de chacun

Rapport à rendre avant le **1er décembre 23:59**. Deadline interne : **samedi 29 novembre au soir**, chiffres envoyés à Merin.

Chaque tâche part des cellules 0 à 3 de `notebooks/01_data.ipynb` (chargement des données). Les bouts de code ci-dessous sont des **points de départ** : à adapter, lancer et mesurer.

| Qui | Tâche | Notebook | Résultat attendu |
|---|---|---|---|
| Victor | Passer à plus de commandes | `02_scale.ipynb` | Temps et mémoire selon la taille de l'échantillon |
| Alexandre | Baisser le seuil de support | `03_support_sweep.ipynb` | Courbe « seuil → nombre de compteurs », PCY si ça explose |
| Arthur | Premier agent Solar | `04_agent.ipynb` | Le chatbot répond à un panier avec nos règles |
| Louis | Évaluation | `05_evaluation.ipynb` | Hit-rate de nos règles contre la baseline popularité |
| Merin | Cours semaine 2 + rapport | `reports/week11.md` | Outil de l'agent confirmé, rapport assemblé |

---

## Victor — Passer à plus de commandes

**Pourquoi** : en semaine 10, on n'a utilisé que 50 000 commandes sur 3,2 millions. Il faut savoir jusqu'où on peut monter dans Colab.

**Quoi faire** :
1. Pour N = 50 000, 200 000, 500 000, 1 000 000 et toutes les commandes : construire les paniers (`groupby(...).apply(frozenset)`) et mesurer le **temps** et la **mémoire**.
2. Lancer A-Priori (fonction `apriori_pairs` du notebook 01) au même seuil 0,5 % sur chaque taille.
3. Noter où Colab ralentit trop ou plante (RAM pleine = redémarrage de session : c'est un résultat, note-le).

**Code de départ** :
```python
import tracemalloc, time
results = []
for n in [50_000, 200_000, 500_000, 1_000_000]:
    ids = rng.choice(all_orders, size=n, replace=False)
    tracemalloc.start(); t0 = time.time()
    b = prior[prior["order_id"].isin(ids)].groupby("order_id")["product_id"].apply(frozenset).tolist()
    _, pairs, info = apriori_pairs(b, max(1, int(len(b) * 0.005)))
    _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
    results.append({"orders": n, "seconds": round(time.time() - t0, 1),
                    "peak_MB": round(peak / 1e6, 1), **info})
    print(results[-1])
```

**À rendre** : `out/evidence_week11_scale.json` + un graphique `out/scale.png` (commandes → secondes et Mo).

---

## Alexandre — Baisser le seuil de support

**Pourquoi** : à 0,5 %, seuls 257 produits sur 49 677 peuvent être recommandés. Si on baisse le seuil, on couvre plus de produits, mais le nombre de paires à compter explose. C'est exactement le lab 6 task 2, sur de vraies données.

**Quoi faire** :
1. Sur les 50 000 commandes du notebook 01, lancer `apriori_pairs` avec un seuil de 0,5 %, 0,25 %, 0,1 % et 0,05 %.
2. Pour chaque seuil, noter : produits fréquents, compteurs de paires, paires fréquentes, secondes, mémoire max.
3. Tracer la courbe « seuil → compteurs » (échelle log).
4. Si la passe 2 devient trop lourde : reprendre **PCY** (`w06-apriori/task3_pcy.py` du lab 6) et comparer le nombre de compteurs.
5. Bonus utile pour la suite : regarder si le top 10 par lift change quand on baisse le seuil.

**Code de départ** :
```python
import tracemalloc, time
sweep = []
for pct in [0.5, 0.25, 0.1, 0.05]:
    s = max(1, int(N * pct / 100))
    tracemalloc.start(); t0 = time.time()
    _, pairs, info = apriori_pairs(baskets, s)
    _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
    sweep.append({"support_pct": pct, "support_baskets": s, **info,
                  "seconds": round(time.time() - t0, 2), "peak_MB": round(peak / 1e6, 1)})
    print(sweep[-1])
```

**À rendre** : `out/evidence_week11_sweep.json`, `out/support_sweep.png`, et le fichier de règles au seuil retenu `out/rules_week11.csv` (même format que `rules_week10.csv`). Arthur et Louis en ont besoin.

---

## Arthur — Premier agent Solar

**Pourquoi** : c'est la condition 2 + 3 du prof. Le chatbot ne doit rien inventer : il appelle notre fonction, qui lit les règles d'A-Priori.

**Quoi faire** :
1. Créer une clé sur console.upstage.ai, la mettre dans les Secrets Colab sous `UPSTAGE_API_KEY`.
2. Écrire `get_recommendations(products, k=5)` : à partir de `out/rules_week10.csv`, garder les règles dont `if_bought` est dans le panier, exclure ce qui est déjà dans le panier, trier par **lift**, renvoyer les k meilleurs avec leur lift.
3. Brancher cette fonction comme outil (tool calling) sur Solar et tester 5 paniers.
4. Garder les conversations : ce sont les preuves du rapport.

**Point bloquant** : utiliser **le même outil d'agent que la semaine 2** du cours (Merin le confirme). En attendant, l'API Upstage s'utilise comme celle d'OpenAI ; vérifier le nom exact du modèle dans la console Upstage :
```python
from openai import OpenAI
from google.colab import userdata
client = OpenAI(api_key=userdata.get("UPSTAGE_API_KEY"), base_url="https://api.upstage.ai/v1")
```

**À rendre** : `notebooks/04_agent.ipynb` avec 5 conversations, et la liste de ce qui a raté (ex. produit tapé « eggs » introuvable).

---

## Louis — Évaluation

**Pourquoi** : le prof veut toujours une comparaison avec une baseline. La nôtre : « recommander simplement les produits les plus vendus ». Si nos règles ne font pas mieux, il faut le savoir et l'expliquer.

**Quoi faire** :
1. Prendre 10 000 commandes **qui ne sont pas** dans les 50 000 du notebook 01 (pour ne pas tricher).
2. Pour chaque commande d'au moins 2 produits : cacher un produit au hasard (graine 42).
3. **Nos règles** : avec les produits restants, recommander les 5 meilleurs selon le lift (`out/rules_week10.csv`).
4. **Baseline** : recommander les 5 produits les plus vendus qui ne sont pas déjà dans le panier.
5. **Hit-rate@5** = part des commandes où le produit caché est dans les 5 recommandés. Comparer les deux.
6. Noter aussi la **couverture** : dans combien de commandes nos règles proposent au moins un produit (avec 257 produits seulement, ce sera faible : c'est un vrai résultat à expliquer).

**Code de départ** :
```python
import random
random.seed(42)
rules = pd.read_csv("out/rules_week10.csv")   # à uploader dans Colab, ou lire depuis GitHub
def recommend_rules(basket, k=5):
    r = rules[rules["a_id"].isin(basket) & ~rules["b_id"].isin(basket)]
    return r.groupby("b_id")["lift"].max().sort_values(ascending=False).head(k).index.tolist()
def recommend_popular(basket, k=5):
    return [p for p in item_count.index if p not in basket][:k]
```

**À rendre** : `out/evidence_week11_eval.json` (hit-rate des deux méthodes, couverture, nombre de commandes testées) et `notebooks/05_evaluation.ipynb`.

---

## Merin — Cours semaine 2 + rapport

**Pourquoi** : le prof a dit que l'agent doit utiliser **l'outil vu en semaine 2**. Sans ça, Arthur risque de construire avec le mauvais outil.

**Quoi faire** :
1. Retrouver les slides ou le code de la semaine 2 (« coding agent ») sur le LMS ou le site du cours, et noter : quelle librairie / quel outil, et un exemple de code. Envoyer à Arthur **dès que possible**.
2. Récupérer les chiffres de chacun le samedi 29 novembre.
3. Écrire `reports/week11.md` sur le modèle de `reports/week10.md` (les 5 parties), avec « qui a fait quoi ».
4. Mettre à jour le tableau des notebooks dans `README.md`.
5. Le rapport est soumis sur le LMS avant le 1er déc. (une soumission par équipe).

**À rendre** : `reports/week11.md` et le README à jour.
