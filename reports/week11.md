# Team Frenchies — Week 11 Progress Report

**Project:** SmartBasket – A Solar-Powered Shopping Assistant Built on Frequent Itemset Mining
**Repository:** https://github.com/arthurcomet/smartbasket-frenchies
**Team (4):** Victor DUMUR (leader), Alexandre GRIMOND, Arthur COMET, Merin SALLAMI. Louis TURQUIN left the team this week.

## 1. What we set out to do this week

Following the professor's feedback ("making more deeper technology on the project"):
- Run frequent itemset mining on the **full dataset** (3.2 M orders) instead of a 50,000-order sample.
- Lower the support to cover more products, and measure where memory breaks; compare **A-Priori and PCY** (MMDS §6.3).
- Build a **first Upstage Solar agent** that calls our rules as tools.
- **Evaluate** our recommendations against a best-sellers baseline on unseen orders.

## 2. What we have working

**A-Priori on the full dataset** (notebook 02, `out/apriori_20261118/`). 10 configurations, each repeated 3 times, 30/30 runs successful:

| Orders | Support | Median time (s) | Peak process memory (MB) | Pair counters | Rules | Products covered |
|---:|---:|---:|---:|---:|---:|---:|
| 50,000 | 0.5 % | 0.91 | 52.7 | 31,308 | 164 | 34 |
| 50,000 | 0.05 % | 2.22 | 155.9 | 980,774 | 12,188 | 834 |
| 250,000 | 0.05 % | 12.85 | 318.5 | 2,303,378 | 11,612 | 768 |
| 3,214,874 | 0.075 % | 143.06 | 505.4 | 2,435,349 | 6,058 | 466 |
| 3,214,874 | 0.05 % | 175.77 | 775.2 | 4,538,892 | 11,412 | 763 |

The 0.5 % run reproduces exactly the 164 rules of week 10. Five unit tests compare our counts with an exhaustive count.

**PCY vs A-Priori at lower supports** (notebook 03, `out/pcy_week11/`), on all 3,214,874 orders (238,428,378 pairs inside baskets). Pass-2 memory with the MMDS model: 4 bytes per triangular counter, 12 bytes per counted pair, B/8 for the PCY bitmap; 16.8 M buckets.

| Support | Frequent items | A-Priori triangular counters (MB) | A-Priori counted pairs (MB) | PCY candidates (MB) | Frequent pairs | Rules | Products covered |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.05 % | 3,402 | 5,785,101 (23.1) | 4,538,892 (54.5) | 7,504 (2.2) | 5,706 | 11,412 | 763 (1.5 %) |
| 0.02 % | 6,985 | 24,391,620 (97.6) | 12,833,613 (154.0) | 40,429 (2.6) | 22,028 | 44,056 | 1,997 (4.0 %) |
| 0.01 % | 10,906 | 59,464,965 (237.9) | 20,568,480 (246.8) | 134,431 (3.7) | 56,809 | 113,618 | 3,679 (7.4 %) |
| 0.005 % | 15,990 | 127,832,055 (511.3) | 27,863,403 (334.4) | 410,935 (7.0) | 138,486 | 276,972 | 6,280 (12.6 %) |

- At 0.05 % we reproduce exactly the numbers of notebook 02 (3,402 frequent items, 4,538,892 counted pairs, 5,706 frequent pairs): the two implementations check each other.
- PCY finds **exactly the same frequent pairs** as A-Priori at every support (checked in the notebook), while counting 0.2 % to 1.5 % of the pairs A-Priori counts.
- Going from 0.05 % to 0.01 % multiplies the products we can recommend by 4.8 (763 → 3,679). A-Priori's pass 2 grows from 23 MB to 238 MB; PCY's stays under 4 MB.
- The price of PCY is pass 1: it hashes all 238 M pairs (7.4 s with 16.8 M buckets, against 0.16 s to count items only).

Number of buckets at 0.01 % (same frequent pairs in every case):

| Buckets | Bucket array (pass 1) | Frequent buckets | PCY candidates | vs A-Priori counted pairs | Pass-2 memory |
|---:|---:|---:|---:|---:|---:|
| 1,048,576 | 4.2 MB | 13.14 % | 2,922,124 | 14.2 % | 35.2 MB |
| 4,194,304 | 16.8 MB | 1.65 % | 417,157 | 2.0 % | 5.5 MB |
| 16,777,216 | 67.1 MB | 0.36 % | 134,431 | 0.7 % | 3.7 MB |

With too few buckets, frequent and infrequent pairs share buckets and the filter lets more pairs through: the trade-off between pass-1 and pass-2 memory from MMDS §6.3.

**Solar agent** (notebook 04, `out/agent_week11/`), model `solar-pro4`, rules at 0.05 % (notebook 02). Two tools: `search_products` (words → exact product names) and `recommend_for_basket` (rules ranked by lift, with confidence and lift as the reason). **5/5 test conversations answered, 14 tool calls, 0 errors.** In the 4 grocery conversations Solar called `search_products` for each product first, then `recommend_for_basket`, as instructed.

| User asks | Tools called | Agent answer |
|---|---|---|
| Guacamole with avocados and limes | search ×2 → recommend | Cilantro, jalapeño, poblano (lift 5.8 to 6.3), with the percentage of lime baskets for each |
| Spaghetti and marinara sauce | search ×2 → recommend | Whole milk, lemon, strawberries, avocado, banana (lift 1.8 to 2.4): generic |
| Tacos with ground beef and taco seasoning | search ×2 → recommend | Whole milk, lemon, avocado, spinach, banana (lift 1.8 to 3.2): generic |
| « J'ai des oeufs et du pain » (French) | search "oeufs", "pain" → nothing | Says honestly it found nothing |
| Phone charger and a laptop | search ×2 → nothing | Says these are not in the grocery data, invents nothing |

With the PCY 0.01 % rules (notebook 03), the same tools give a real taco answer: iceberg lettuce, mild salsa, sour cream, shredded Mexican cheese (lift 8 to 11), and penne and pasta sauces for spaghetti. The agent switches to these rules automatically once they are on GitHub.

**Evaluation** (notebook 05, `out/eval_week11/`): 124,364 unseen orders with at least 2 products (train file, never seen by A-Priori). In each order we hide one product at random (seed 42) and check whether it comes back in the top 5 / top 10 of each method.

| Rules | Method | hit@5 | hit@10 |
|---|---|---:|---:|
| — | Best-sellers (baseline) | 5.08 % | 7.38 % |
| A-Priori 0.05 % | Rules by lift | 3.09 % | 4.82 % |
| A-Priori 0.05 % | Rules by confidence | 6.12 % | 8.74 % |
| A-Priori 0.05 % | Rules + best-sellers | 3.49 % | 5.45 % |
| PCY 0.01 % | Rules by lift | 3.65 % | 5.41 % |
| PCY 0.01 % | **Rules by confidence** | **7.44 %** | **10.89 %** |
| PCY 0.01 % | Rules + best-sellers | 3.74 % | 5.57 % |

| Rules | Baskets that get a rule recommendation | Hidden product can be recommended at all |
|---|---:|---:|
| A-Priori 0.05 % | 87.5 % | 46.0 % |
| PCY 0.01 % | 96.3 % | 72.9 % |

- **Rules ranked by confidence beat the best-sellers baseline:** 10.89 % against 7.38 % at hit@10 (+48 %) with the PCY 0.01 % rules.
- **Lowering the support helps every rule-based method** (lift 4.82 → 5.41 %, confidence 8.74 → 10.89 %), because 72.9 % of the hidden products can now be recommended instead of 46.0 %.
- **Rules ranked by lift lose to best-sellers** (5.41 % against 7.38 %). Lift favours rare, very specific products, while the products people actually add are often popular ones. This contradicts our week-10 choice of lift and is discussed below.

## 3. What broke or is blocking us

- **Coverage:** at 0.05 % on the full data, only 763 products (1.5 % of the catalogue) could be recommended, and pasta or taco baskets got generic answers (bananas, milk). Fixed by lowering the support to 0.01 % with PCY (3,679 products).
- **Product search by words:** "beer" matches "Root Beer" and "dog food" matches "Hot Dogs". Simple word matching is not enough; to be improved with MinHash/LSH on product names.
- **Substitutes instead of complements:** the highest-lift rules are other flavours of the same product (Almond Milk Blueberry Yogurt → Almond Milk Peach Yogurt, lift 327). A shopping assistant should not propose a second yogurt flavour. Fix for now: a simple name filter in the agent tool. Proper fix next week with MinHash/LSH.
- **Upstage API:** our key first returned `403 – API key suspended due to insufficient credit`. The connection and the model name were correct; we had to register a payment method on the Upstage console. Then `solar-pro2` and `solar-pro3` returned `400 – model deprecated`; we listed the available models through the API and switched to `solar-pro4`. The two tools were tested without the LLM in the meantime.
- **Translation:** the system prompt asks Solar to translate the user's words to English before searching, but for the French request it searched "oeufs" and "pain" and found nothing. The agent stayed honest, but a French user gets no help. Next fix: translate in the tool itself, or add a few examples to the prompt.
- **Generic answers at 0.05 %:** for pasta and tacos the agent recommends milk, lemon and bananas, because the specific products are not frequent enough at that support. This is the coverage problem that PCY at 0.01 % fixes.
- **Lift vs confidence:** in week 10 we chose lift because confidence always recommended bananas. The hit-rate shows the opposite trade-off: confidence predicts the missing product better (10.9 % vs 5.4 %), lift gives more interesting but less likely suggestions. Hit-rate rewards predicting popular items, so it is not the whole story. Next week we will test a mixed score (for example confidence among rules with lift > 1.5) and keep the substitute filter.

## 4. What we will do next week

- **MinHash/LSH** (MMDS ch. 3) on product baskets to detect similar products: separate substitutes from complements, and give the agent a third tool ("similar products").
- Switch the agent to the PCY 0.01 % rules and handle product names typed by users.
- Re-run the evaluation with the substitute filter and a mixed confidence/lift score; switch the agent to the best ranking.

## 5. Who did what

| Member | This week |
|---|---|
| Alexandre GRIMOND | A-Priori experiments on the full dataset: 10 configurations × 3 repeats, unit tests (notebook 02) |
| Victor DUMUR | PCY vs A-Priori at lower supports, bucket-size experiment (notebook 03) |
| Arthur COMET | Upstage Solar agent with two tools, test conversations (notebook 04) |
| Merin SALLAMI | Evaluation against best-sellers on 124,364 unseen orders (notebook 05), this report |
