# SmartBasket — Frenchies

Introduction to Big Data · Korea University Sejong · 2026-2 team project

**Frequent itemset mining (A-Priori) on the Instacart Market Basket dataset, exposed as tools to an LLM agent powered by Upstage Solar.**
The user describes a basket in natural language; the agent queries the mined association rules to recommend complementary products and explain why.

| Course condition | How it is met |
|---|---|
| Big-data method from the course | Frequent itemsets: A-Priori (MMDS §6.1–6.2), association rules with confidence and lift |
| LLM agent | Agent that calls our rule-lookup functions as tools |
| Model | Upstage Solar |

## Team

| Member | Role |
|---|---|
| Victor DUMUR (leader) | Data loading and description |
| Alexandre GRIMOND | A-Priori and association rules |
| Arthur COMET | Solar agent and tools |
| Louis TURQUIN | Evaluation against a popularity baseline |
| Merin SALLAMI | Report, slides, repository |

## Repository

```
notebooks/   one Colab notebook per stage, run in order
out/         results of each run (figures, CSV, evidence JSON)
reports/     weekly progress reports
```

| Notebook | Stage |
|---|---|
| `01_data.ipynb` | Load data, measure memory, describe, first A-Priori on a sample |

## Running

Open a notebook in Google Colab (File → Open notebook → GitHub → `arthurcomet/smartbasket-frenchies`).
Add your Kaggle token as a Colab secret named `KAGGLE_API_TOKEN`. Never commit a key: this repository is public.

Data: [Instacart Market Basket Analysis](https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis) (Kaggle).
