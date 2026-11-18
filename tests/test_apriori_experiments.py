"""Small exact checks, independent of the Instacart download."""

import csv
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import random
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "apriori_experiments.py"
spec = importlib.util.spec_from_file_location("experiments", SCRIPT)
exp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exp)


class AprioriTests(unittest.TestCase):
    def test_matches_unpruned_reference_with_duplicates(self):
        rng = random.Random(42)
        baskets = [[rng.randrange(12) for _ in range(rng.randrange(1, 10))] for _ in range(100)]
        reference = exp.Counter(pair for b in baskets for pair in combinations(sorted(set(b)), 2))
        for threshold in (1, 5, 20, 100):
            counts, pairs, _ = exp.apriori_pairs(lambda: iter(baskets), threshold)
            expected = {p: c for p, c in reference.items() if c >= threshold}
            self.assertEqual(pairs, expected)
            rules = exp.rules_from_pairs(pairs, counts, len(baskets), {})
            for rule in rules:
                a, b = rule["a_id"], rule["b_id"]
                self.assertAlmostEqual(rule["confidence"], reference[tuple(sorted((a, b)))] / counts[a])
                self.assertAlmostEqual(rule["lift"], rule["confidence"] / (counts[b] / len(baskets)))

    def test_threshold_rounding_and_pair_budget(self):
        self.assertEqual(exp.support_count(50_000, 0.075), 38)
        self.assertEqual(exp.support_count(50_000, 0.5), 250)
        with self.assertRaises(ValueError):
            exp.support_count(0, 0.5)
        with self.assertRaises(exp.PairBudgetExceeded):
            exp.apriori_pairs(lambda: iter([[1, 2, 3, 4]]), 1, max_pairs=2)

    def test_empty_rules_and_memory_monitor(self):
        counts, pairs, info = exp.apriori_pairs(lambda: iter([[1], [2]]), 1)
        self.assertEqual(exp.rules_from_pairs(pairs, counts, 2, {}), [])
        self.assertEqual(info["frequent_pairs"], 0)
        self.assertGreater(exp.rss_mb(exp.os.getpid()), 0)

    def test_pipeline_uses_every_order_for_full_stage(self):
        # ce jeu sert seulement a verifier le code, pas a produire des resultats Instacart
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with (root / "products.csv").open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["product_id", "product_name"])
                writer.writerows([(1, "one"), (2, "two"), (3, "three"), (4, "four")])
            with (root / "order_products__prior.csv").open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["order_id", "product_id"])
                for order in range(60):
                    for item in ([1, 2] if order % 2 == 0 else [3, 4]):
                        writer.writerow([order, item])
            summary = exp.run_experiments(root, root / "results", repeats=1,
                                          sample_sizes=(10, 30), supports=[10, 20],
                                          timeout_s=30, script_path=SCRIPT)
            full = [r for r in summary if r["stage"] == "full"]
            self.assertTrue(full)
            self.assertTrue(all(r["baskets"] == 60 for r in full))
            self.assertTrue(all(r["status"] == "ok" for r in summary))
            metadata = json.loads((root / "results" / "metadata.json").read_text())
            self.assertEqual(metadata["dataset"]["basket_lines"], 120)
            # meme ordre de produits et memes repetitions sur les memes paniers
            cache = root / "cache"
            cache.mkdir()
            exp.prepare_data(root, cache)
            items1, offsets1, _ = exp.sample_store(cache, 10, 42)
            first = exp.np.load(items1).copy()
            offsets = exp.np.load(offsets1).copy()
            items2, offsets2, _ = exp.sample_store(cache, 10, 42)
            exp.np.testing.assert_array_equal(first, exp.np.load(items2))
            exp.np.testing.assert_array_equal(offsets, exp.np.load(offsets2))

    def test_interrupted_worker_is_not_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slow_script = root / "slow.py"
            slow_script.write_text("import time\ntime.sleep(5)\n")
            result = exp.bounded_run({}, slow_script, root, timeout_s=0.1, max_worker_mb=2048)
            self.assertEqual(result["status"], "timeout")
            self.assertNotIn("mining_s", result)


if __name__ == "__main__":
    unittest.main()
