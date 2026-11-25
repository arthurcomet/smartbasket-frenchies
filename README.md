# SmartBasket — Team Frenchies

Introduction to Big Data · Korea University Sejong · 2026-2 team project

**Frequent itemset mining on 3.2 million real grocery orders (Instacart), served by an LLM agent powered by Upstage Solar.**
The user describes a basket in plain language; the agent calls our tools, which read the association rules mined with A-Priori and PCY, and recommends complementary products with the reason (confidence and lift).

| Course condition | How it is met |
|---|---|
| Big-data method from the course | Frequent itemsets: A-Priori and PCY (MMDS §6.1–6.3) on all 3.2 M orders, association rules with confidence and lift |
| LLM agent | Solar calls our Python functions as tools (`search_products`, `recommend_for_basket`) |
| Model | Upstage Solar |

## Start here

| You are looking for… | Go to |
|---|---|
| What we did each week | [`reports/`](reports/) — [week 10](reports/week10.md), [week 11](reports/week11.md) |
| A-Priori on the full dataset, 5 supports, 3 repeats | [Notebook 02 report](reports/apriori_20261118.md) and [`out/apriori_20261118/`](out/apriori_20261118/) |
| Team guide, weekly tasks, AI prompt (French) | [`docs/`](docs/) |

## Notebooks

Run them in order in Google Colab: *File → Open notebook → GitHub* → `arthurcomet/smartbasket-frenchies`.

| Notebook | Stage | Week |
|---|---|---|
| [`01_data.ipynb`](notebooks/01_data.ipynb) | Load and describe the data, first A-Priori on 50,000 orders | 10 |
| [`02_apriori_experiments.ipynb`](notebooks/02_apriori_experiments.ipynb) | A-Priori on all 3.2 M orders: 10 configurations × 3 repeats, time and memory | 11 |
| [`03_pcy.ipynb`](notebooks/03_pcy.ipynb) | PCY vs A-Priori at lower supports: pass-2 counters and memory, same frequent pairs | 11 |
| [`04_agent.ipynb`](notebooks/04_agent.ipynb) | First Upstage Solar agent with two tools on the rules | 11 |
| [`05_evaluation.ipynb`](notebooks/05_evaluation.ipynb) | Hit-rate of our rules vs a best-sellers baseline on 131k unseen orders | 11 |

## Repository

```
notebooks/   one Colab notebook per stage
scripts/     reference code of the notebook 02 experiments
tests/       unit tests of the A-Priori experiments (python -m unittest discover -s tests)
out/         results of each run: evidence JSON, summaries, rules CSV, figures
reports/     weekly progress reports
docs/        team guide (French): setup, weekly tasks, AI prompt
```

## Data and keys

Data: [Instacart Market Basket Analysis](https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis) (Kaggle). It is never committed. The notebooks read it from a Google Drive folder `instacart`, or download it from Kaggle with a Colab secret `KAGGLE_API_TOKEN`.

The agent needs a Colab secret `UPSTAGE_API_KEY`. **Never commit a key: this repository is public.**

## Team

| Member | Role |
|---|---|
| Victor DUMUR (leader) | Data loading, PCY |
| Alexandre GRIMOND | A-Priori experiments on the full dataset |
| Arthur COMET | Solar agent and tools |
| Merin SALLAMI | Evaluation, reports |
