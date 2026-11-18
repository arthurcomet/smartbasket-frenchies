# A-Priori experiment report

Run: 2026-11-18T05:08:31.834375+00:00 (UTC)

## Scope and method

Pairs only, using the two-pass A-Priori algorithm from notebook 01. No PCY.
Only prior orders are used; the train file is left untouched for future evaluation.
Samples are drawn uniformly without replacement with a fixed seed. Every support within a stage uses exactly the same baskets.
The 50k and 250k samples use separate fixed-seed draws; they are not necessarily nested.
Threshold counts use ceil(N * support_pct / 100). Products are deduplicated within each basket.

Selection between stages maximizes the number of distinct consequents in rules with lift > 1, then prefers faster mining and fewer counters.
This is a coverage/resource heuristic, not a recommendation-quality evaluation or proof of an optimal threshold.
Full-data validation uses every prior order, with no sampling.

## Measurements

Mining time covers both A-Priori passes, including basket iteration, but excludes data preparation and rule export.
Wall time also includes worker startup, loading and rule export.
Worker RSS is sampled every 20 ms, in decimal MB: it includes the interpreter, mapped input pages, counters and rules. Brief peaks may be missed.
RSS increase is relative to the worker after opening inputs, not an exact allocation measurement. OS file caching can affect repetitions.
Parent memory is recorded separately in metadata; the worker limit is not a system-wide memory limit.
Memory/time/pair stops are incomplete attempts, never treated as successful full runs.

| Stage | Baskets | Support % | Status | Repeats OK | Mining median s | Peak worker MB | Pair counters | Rules | Products with lift > 1 |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| sample_1 | 50000 | 0.500 | ok | 3 | 0.914 | 52.732 | 31308 | 164 | 34 |
| sample_1 | 50000 | 0.250 | ok | 3 | 1.080 | 58.249 | 150137 | 766 | 98 |
| sample_1 | 50000 | 0.100 | ok | 3 | 1.668 | 103.694 | 545903 | 3946 | 344 |
| sample_1 | 50000 | 0.075 | ok | 3 | 1.895 | 156.283 | 713906 | 6304 | 490 |
| sample_1 | 50000 | 0.050 | ok | 3 | 2.218 | 155.943 | 980774 | 12188 | 834 |
| sample_2 | 250000 | 0.050 | ok | 3 | 12.851 | 318.489 | 2303378 | 11612 | 768 |
| sample_2 | 250000 | 0.075 | ok | 3 | 10.994 | 290.234 | 1501214 | 6102 | 461 |
| sample_2 | 250000 | 0.100 | ok | 3 | 9.487 | 178.856 | 1019315 | 3834 | 318 |
| full | 3214874 | 0.050 | ok | 3 | 175.772 | 775.197 | 4538892 | 11412 | 763 |
| full | 3214874 | 0.075 | ok | 3 | 143.062 | 505.373 | 2435349 | 6058 | 466 |

## sample_1: support 0.5%

Baskets: 50,000. Minimum pair count: 250.
Status: ok. Successful repetitions: 3/3.

Frequent individual products: 257; products in positive-lift rules: 34 (0.07% of the catalogue).

Top rules by lift (descriptive associations, not causal effects):

| If bought | Then buy | Pair count | Confidence | Lift |
|---|---|---:|---:|---:|
| Limes | Organic Cilantro | 268 | 0.123 | 6.10 |
| Organic Cilantro | Limes | 268 | 0.266 | 6.10 |
| Organic Yellow Onion | Organic Garlic | 356 | 0.197 | 5.86 |
| Organic Garlic | Organic Yellow Onion | 356 | 0.211 | 5.86 |
| Limes | Large Lemon | 431 | 0.197 | 4.16 |
| Large Lemon | Limes | 431 | 0.182 | 4.16 |
| Organic Hass Avocado | Organic Lemon | 369 | 0.111 | 3.85 |
| Organic Lemon | Organic Hass Avocado | 369 | 0.256 | 3.85 |
| Organic Cucumber | Organic Hass Avocado | 279 | 0.220 | 3.31 |
| Organic Hass Avocado | Organic Cucumber | 279 | 0.084 | 3.31 |

## sample_1: support 0.25%

Baskets: 50,000. Minimum pair count: 125.
Status: ok. Successful repetitions: 3/3.

Frequent individual products: 649; products in positive-lift rules: 98 (0.20% of the catalogue).

Top rules by lift (descriptive associations, not causal effects):

| If bought | Then buy | Pair count | Confidence | Lift |
|---|---|---:|---:|---:|
| Total 2% with Strawberry Lowfat Greek Strained Yogurt | Total 2% Lowfat Greek Strained Yogurt With Blueberry | 130 | 0.278 | 44.37 |
| Total 2% Lowfat Greek Strained Yogurt With Blueberry | Total 2% with Strawberry Lowfat Greek Strained Yogurt | 130 | 0.415 | 44.37 |
| Sparkling Lemon Water | Lime Sparkling Water | 132 | 0.245 | 16.34 |
| Lime Sparkling Water | Sparkling Lemon Water | 132 | 0.176 | 16.34 |
| Sparkling Lemon Water | Sparkling Water Grapefruit | 156 | 0.290 | 11.66 |
| Sparkling Water Grapefruit | Sparkling Lemon Water | 156 | 0.126 | 11.66 |
| Lime Sparkling Water | Sparkling Water Grapefruit | 217 | 0.289 | 11.62 |
| Sparkling Water Grapefruit | Lime Sparkling Water | 217 | 0.175 | 11.62 |
| Bunched Cilantro | Limes | 194 | 0.282 | 6.47 |
| Limes | Bunched Cilantro | 194 | 0.089 | 6.47 |

## sample_1: support 0.1%

Baskets: 50,000. Minimum pair count: 50.
Status: ok. Successful repetitions: 3/3.

Frequent individual products: 1,829; products in positive-lift rules: 344 (0.69% of the catalogue).

Top rules by lift (descriptive associations, not causal effects):

| If bought | Then buy | Pair count | Confidence | Lift |
|---|---|---:|---:|---:|
| Yotoddler Organic Pear Spinach Mango Yogurt | Organic Whole Milk Strawberry Beet Berry Yogurt Pouch | 57 | 0.491 | 225.40 |
| Organic Whole Milk Strawberry Beet Berry Yogurt Pouch | Yotoddler Organic Pear Spinach Mango Yogurt | 57 | 0.523 | 225.40 |
| Kiwi Sandia Sparkling Water | Blackberry Cucumber Sparkling Water | 50 | 0.338 | 101.15 |
| Blackberry Cucumber Sparkling Water | Kiwi Sandia Sparkling Water | 50 | 0.299 | 101.15 |
| Non Fat Acai & Mixed Berries Yogurt | Non Fat Raspberry Yogurt | 59 | 0.413 | 75.57 |
| Non Fat Raspberry Yogurt | Non Fat Acai & Mixed Berries Yogurt | 59 | 0.216 | 75.57 |
| Nonfat Icelandic Style Strawberry Yogurt | Icelandic Style Skyr Blueberry Non-fat Yogurt | 77 | 0.478 | 74.50 |
| Icelandic Style Skyr Blueberry Non-fat Yogurt | Nonfat Icelandic Style Strawberry Yogurt | 77 | 0.240 | 74.50 |
| Nonfat Icelandic Style Strawberry Yogurt | Non Fat Raspberry Yogurt | 62 | 0.385 | 70.53 |
| Non Fat Raspberry Yogurt | Nonfat Icelandic Style Strawberry Yogurt | 62 | 0.227 | 70.53 |

## sample_1: support 0.075%

Baskets: 50,000. Minimum pair count: 38.
Status: ok. Successful repetitions: 3/3.

Frequent individual products: 2,404; products in positive-lift rules: 490 (0.99% of the catalogue).

Top rules by lift (descriptive associations, not causal effects):

| If bought | Then buy | Pair count | Confidence | Lift |
|---|---|---:|---:|---:|
| Almond Milk Blueberry Yogurt | Almond Milk Peach Yogurt | 46 | 0.484 | 331.65 |
| Almond Milk Peach Yogurt | Almond Milk Blueberry Yogurt | 46 | 0.630 | 331.65 |
| Almond Milk Strawberry Yogurt | Almond Milk Peach Yogurt | 42 | 0.412 | 282.03 |
| Almond Milk Peach Yogurt | Almond Milk Strawberry Yogurt | 42 | 0.575 | 282.03 |
| Almond Milk Blueberry Yogurt | Almond Milk Strawberry Yogurt | 47 | 0.495 | 242.52 |
| Almond Milk Strawberry Yogurt | Almond Milk Blueberry Yogurt | 47 | 0.461 | 242.52 |
| Yotoddler Organic Pear Spinach Mango Yogurt | Organic Whole Milk Strawberry Beet Berry Yogurt Pouch | 57 | 0.491 | 225.40 |
| Organic Whole Milk Strawberry Beet Berry Yogurt Pouch | Yotoddler Organic Pear Spinach Mango Yogurt | 57 | 0.523 | 225.40 |
| Vanilla Almond Milk Yogurt | Almond Milk Strawberry Yogurt | 40 | 0.396 | 194.14 |
| Almond Milk Strawberry Yogurt | Vanilla Almond Milk Yogurt | 40 | 0.392 | 194.14 |

## sample_1: support 0.05%

Baskets: 50,000. Minimum pair count: 25.
Status: ok. Successful repetitions: 3/3.

Frequent individual products: 3,505; products in positive-lift rules: 834 (1.68% of the catalogue).

Top rules by lift (descriptive associations, not causal effects):

| If bought | Then buy | Pair count | Confidence | Lift |
|---|---|---:|---:|---:|
| Raspberry Essence Water | Unsweetened Blackberry Water | 28 | 0.683 | 494.87 |
| Unsweetened Blackberry Water | Raspberry Essence Water | 28 | 0.406 | 494.87 |
| Coconut Chia Bar | Acai Berry Chia Bar | 29 | 0.367 | 346.31 |
| Acai Berry Chia Bar | Coconut Chia Bar | 29 | 0.547 | 346.31 |
| Almond Milk Blueberry Yogurt | Almond Milk Peach Yogurt | 46 | 0.484 | 331.65 |
| Almond Milk Peach Yogurt | Almond Milk Blueberry Yogurt | 46 | 0.630 | 331.65 |
| Chocolate Peanut Butter | Coconut Chia Bar | 36 | 0.462 | 292.11 |
| Coconut Chia Bar | Chocolate Peanut Butter | 36 | 0.456 | 292.11 |
| Almond Milk Strawberry Yogurt | Almond Milk Peach Yogurt | 42 | 0.412 | 282.03 |
| Almond Milk Peach Yogurt | Almond Milk Strawberry Yogurt | 42 | 0.575 | 282.03 |

## sample_2: support 0.05%

Baskets: 250,000. Minimum pair count: 125.
Status: ok. Successful repetitions: 3/3.

Frequent individual products: 3,411; products in positive-lift rules: 768 (1.55% of the catalogue).

Top rules by lift (descriptive associations, not causal effects):

| If bought | Then buy | Pair count | Confidence | Lift |
|---|---|---:|---:|---:|
| Almond Milk Blueberry Yogurt | Almond Milk Peach Yogurt | 172 | 0.482 | 330.00 |
| Almond Milk Peach Yogurt | Almond Milk Blueberry Yogurt | 172 | 0.471 | 330.00 |
| Almond Milk Blueberry Yogurt | Almond Milk Strawberry Yogurt | 204 | 0.571 | 306.56 |
| Almond Milk Strawberry Yogurt | Almond Milk Blueberry Yogurt | 204 | 0.438 | 306.56 |
| Coconut Chia Bar | Chocolate Peanut Butter | 150 | 0.402 | 298.33 |
| Chocolate Peanut Butter | Coconut Chia Bar | 150 | 0.445 | 298.33 |
| Almond Milk Strawberry Yogurt | Almond Milk Peach Yogurt | 181 | 0.388 | 266.04 |
| Almond Milk Peach Yogurt | Almond Milk Strawberry Yogurt | 181 | 0.496 | 266.04 |
| Yotoddler Organic Pear Spinach Mango Yogurt | Organic Whole Milk Strawberry Beet Berry Yogurt Pouch | 218 | 0.472 | 234.52 |
| Organic Whole Milk Strawberry Beet Berry Yogurt Pouch | Yotoddler Organic Pear Spinach Mango Yogurt | 218 | 0.433 | 234.52 |

## sample_2: support 0.075%

Baskets: 250,000. Minimum pair count: 188.
Status: ok. Successful repetitions: 3/3.

Frequent individual products: 2,360; products in positive-lift rules: 461 (0.93% of the catalogue).

Top rules by lift (descriptive associations, not causal effects):

| If bought | Then buy | Pair count | Confidence | Lift |
|---|---|---:|---:|---:|
| Almond Milk Blueberry Yogurt | Almond Milk Strawberry Yogurt | 204 | 0.571 | 306.56 |
| Almond Milk Strawberry Yogurt | Almond Milk Blueberry Yogurt | 204 | 0.438 | 306.56 |
| Yotoddler Organic Pear Spinach Mango Yogurt | Organic Whole Milk Strawberry Beet Berry Yogurt Pouch | 218 | 0.472 | 234.52 |
| Organic Whole Milk Strawberry Beet Berry Yogurt Pouch | Yotoddler Organic Pear Spinach Mango Yogurt | 218 | 0.433 | 234.52 |
| Blueberry on the Bottom Nonfat Greek Yogurt | Strawberry on the Bottom Nonfat Greek Yogurt | 202 | 0.422 | 178.39 |
| Strawberry on the Bottom Nonfat Greek Yogurt | Blueberry on the Bottom Nonfat Greek Yogurt | 202 | 0.342 | 178.39 |
| Strawberry on the Bottom Nonfat Greek Yogurt | Peach on the Bottom Nonfat Greek Yogurt | 199 | 0.337 | 136.21 |
| Peach on the Bottom Nonfat Greek Yogurt | Strawberry on the Bottom Nonfat Greek Yogurt | 199 | 0.322 | 136.21 |
| Raspberry Yoghurt | Blueberry Yoghurt | 249 | 0.371 | 115.82 |
| Blueberry Yoghurt | Raspberry Yoghurt | 249 | 0.311 | 115.82 |

## sample_2: support 0.1%

Baskets: 250,000. Minimum pair count: 250.
Status: ok. Successful repetitions: 3/3.

Frequent individual products: 1,774; products in positive-lift rules: 318 (0.64% of the catalogue).

Top rules by lift (descriptive associations, not causal effects):

| If bought | Then buy | Pair count | Confidence | Lift |
|---|---|---:|---:|---:|
| Icelandic Style Skyr Blueberry Non-fat Yogurt | Non Fat Raspberry Yogurt | 580 | 0.383 | 75.77 |
| Non Fat Raspberry Yogurt | Icelandic Style Skyr Blueberry Non-fat Yogurt | 580 | 0.459 | 75.77 |
| Icelandic Style Skyr Blueberry Non-fat Yogurt | Non Fat Acai & Mixed Berries Yogurt | 280 | 0.185 | 73.74 |
| Non Fat Acai & Mixed Berries Yogurt | Icelandic Style Skyr Blueberry Non-fat Yogurt | 280 | 0.447 | 73.74 |
| Nonfat Icelandic Style Strawberry Yogurt | Icelandic Style Skyr Blueberry Non-fat Yogurt | 345 | 0.421 | 69.56 |
| Icelandic Style Skyr Blueberry Non-fat Yogurt | Nonfat Icelandic Style Strawberry Yogurt | 345 | 0.228 | 69.56 |
| Nonfat Icelandic Style Strawberry Yogurt | Non Fat Raspberry Yogurt | 281 | 0.343 | 67.86 |
| Non Fat Raspberry Yogurt | Nonfat Icelandic Style Strawberry Yogurt | 281 | 0.222 | 67.86 |
| Nonfat Icelandic Style Strawberry Yogurt | Vanilla Skyr Nonfat Yogurt | 296 | 0.361 | 64.45 |
| Vanilla Skyr Nonfat Yogurt | Nonfat Icelandic Style Strawberry Yogurt | 296 | 0.211 | 64.45 |

## full: support 0.05%

Baskets: 3,214,874. Minimum pair count: 1,608.
Status: ok. Successful repetitions: 3/3.

Frequent individual products: 3,402; products in positive-lift rules: 763 (1.54% of the catalogue).

Top rules by lift (descriptive associations, not causal effects):

| If bought | Then buy | Pair count | Confidence | Lift |
|---|---|---:|---:|---:|
| Almond Milk Blueberry Yogurt | Almond Milk Peach Yogurt | 2260 | 0.479 | 327.31 |
| Almond Milk Peach Yogurt | Almond Milk Blueberry Yogurt | 2260 | 0.480 | 327.31 |
| Almond Milk Blueberry Yogurt | Almond Milk Strawberry Yogurt | 2702 | 0.573 | 322.07 |
| Almond Milk Strawberry Yogurt | Almond Milk Blueberry Yogurt | 2702 | 0.472 | 322.07 |
| Almond Milk Strawberry Yogurt | Almond Milk Peach Yogurt | 2477 | 0.433 | 295.82 |
| Almond Milk Peach Yogurt | Almond Milk Strawberry Yogurt | 2477 | 0.526 | 295.82 |
| Coconut Chia Bar | Chocolate Peanut Butter | 1870 | 0.402 | 277.20 |
| Chocolate Peanut Butter | Coconut Chia Bar | 1870 | 0.402 | 277.20 |
| Yotoddler Organic Pear Spinach Mango Yogurt | Organic Whole Milk Strawberry Beet Berry Yogurt Pouch | 2823 | 0.461 | 235.91 |
| Organic Whole Milk Strawberry Beet Berry Yogurt Pouch | Yotoddler Organic Pear Spinach Mango Yogurt | 2823 | 0.449 | 235.91 |

## full: support 0.075%

Baskets: 3,214,874. Minimum pair count: 2,412.
Status: ok. Successful repetitions: 3/3.

Frequent individual products: 2,375; products in positive-lift rules: 466 (0.94% of the catalogue).

Top rules by lift (descriptive associations, not causal effects):

| If bought | Then buy | Pair count | Confidence | Lift |
|---|---|---:|---:|---:|
| Almond Milk Blueberry Yogurt | Almond Milk Strawberry Yogurt | 2702 | 0.573 | 322.07 |
| Almond Milk Strawberry Yogurt | Almond Milk Blueberry Yogurt | 2702 | 0.472 | 322.07 |
| Almond Milk Strawberry Yogurt | Almond Milk Peach Yogurt | 2477 | 0.433 | 295.82 |
| Almond Milk Peach Yogurt | Almond Milk Strawberry Yogurt | 2477 | 0.526 | 295.82 |
| Yotoddler Organic Pear Spinach Mango Yogurt | Organic Whole Milk Strawberry Beet Berry Yogurt Pouch | 2823 | 0.461 | 235.91 |
| Organic Whole Milk Strawberry Beet Berry Yogurt Pouch | Yotoddler Organic Pear Spinach Mango Yogurt | 2823 | 0.449 | 235.91 |
| Blueberry on the Bottom Nonfat Greek Yogurt | Strawberry on the Bottom Nonfat Greek Yogurt | 2767 | 0.434 | 182.69 |
| Strawberry on the Bottom Nonfat Greek Yogurt | Blueberry on the Bottom Nonfat Greek Yogurt | 2767 | 0.362 | 182.69 |
| Strawberry on the Bottom Nonfat Greek Yogurt | Peach on the Bottom Nonfat Greek Yogurt | 2665 | 0.349 | 144.10 |
| Peach on the Bottom Nonfat Greek Yogurt | Strawberry on the Bottom Nonfat Greek Yogurt | 2665 | 0.342 | 144.10 |

## Interpretation and next step

Compare the increase in coverage with the number of counters, mining time and RSS as support falls.
A low-support run reaching a limit is evidence to investigate PCY or another implementation; this notebook never switches algorithms automatically.
The number of rules and lift alone do not demonstrate improved recommendation accuracy. Held-out evaluation against popularity is still required.

Raw repetitions: raw_runs.json. Configuration, data SHA-256 and versions: metadata.json.
CSV exports retain unrounded confidence and lift. Rules include both directions, which share the same lift.
