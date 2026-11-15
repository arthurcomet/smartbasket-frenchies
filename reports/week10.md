# Team Frenchies — Week 10 Progress Report

**Project:** SmartBasket – A Solar-Powered Shopping Assistant Built on Frequent Itemset Mining
**Repository:** https://github.com/arthurcomet/smartbasket-frenchies

## 1. What we set out to do this week
- Load the full Instacart dataset in Colab and measure what it costs.
- Describe the data (basket sizes, product popularity).
- Run a first A-Priori (frequent pairs + association rules) on a sample of real orders.

## 2. What we have working
Evidence: `notebooks/01_data.ipynb`, `out/evidence_week10.json`, `out/rules_week10.csv`, `out/basket_size.png`, `out/long_tail.png`.

- **Dataset:** 3,214,874 orders, 32,434,489 basket lines, 49,677 distinct products bought. Mean basket size 10.09 (median 8, max 145).
- **Loading:** pandas default types (int64) use 1,037.9 MB. Forcing int32/int16/int8 brings it to 356.8 MB (−65.6%), at the cost of a slower load (12.8 s vs 10.2 s).
- **Long tail:** only 102 products appear in at least 1% of orders, 1,772 in at least 0.1%, 10,906 in at least 0.01%.
- **A-Priori on a 50,000-order sample, support 0.5% (250 baskets):** 29,207 distinct items, 257 frequent items after pass 1, 31,308 pair counters in pass 2 instead of 426,509,821 for brute force (about 13,600× fewer). 82 frequent pairs, 164 rules, 0.48 s.
- **Ranking the rules:** all 10 top rules by confidence recommend bananas (e.g. Organic Fuji Apple → Banana, confidence 0.392). Banana is in 14.7% of all orders, so these rules mostly say "bananas are popular". Ranked by lift, the top rules are real associations: Limes ↔ Organic Cilantro (lift 6.10), Organic Garlic ↔ Organic Yellow Onion (5.86), Organic Lemon ↔ Organic Hass Avocado (3.85). Only 5 of the top 10 by lift point to a top-10 popular product, against 10 of 10 by confidence. One frequent pair even has lift below 1 (Organic Yellow Onion → Banana, 0.97): frequent together, but not associated.

## 3. What broke or is blocking us
- Confidence alone gives useless recommendations (always bananas). We will rank by lift.
- Support 0.5% is too high: only 257 of 49,677 products can ever be recommended. Lowering it will multiply the number of pair counters, so we need to measure where memory and time break.
- We have not yet confirmed which agent framework from week 2 we must use with Upstage Solar.

## 4. What we will do next week
| Member | Task for week 11 |
|---|---|
| Victor DUMUR | Scale the data step: rerun loading on a larger sample and check the memory budget in Colab |
| Alexandre GRIMOND | Support sweep (0.5% down to 0.05%): pair counters, time and memory; switch to PCY if pass 2 no longer fits |
| Arthur COMET | Upstage API key and agent setup with a first tool, `get_recommendations(basket)` |
| Louis TURQUIN | Design the evaluation: hold out baskets and define the hit-rate metric against the popularity baseline |
| Merin SALLAMI | Find the week-2 agent material, keep the README and this report folder up to date |

## 5. Who did what this week
- **Arthur COMET:** repository setup, notebook 01 (data loading, description, first A-Priori), ran it in Colab and collected the results.
- The rest of the team joined the project this week; their individual tasks start in week 11 (table above).
