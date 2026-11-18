"""Reproducible, bounded A-Priori experiments; no PCY or LLM calls.

Run from the repository root:
python scripts/apriori_experiments.py --data-dir path/to/instacart
"""

import argparse
import csv
import ctypes
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations

import numpy as np


SUPPORTS = [0.5, 0.25, 0.1, 0.075, 0.05]
RULE_COLUMNS = ["if_bought", "then_buy", "support", "confidence", "lift", "a_id", "b_id"]


class PairBudgetExceeded(RuntimeError):
    pass


def support_count(n, percent):
    if n <= 0 or not 0 < percent <= 100:
        raise ValueError("Need nonempty baskets and a support in (0, 100].")
    # arrondi superieur : le seuil relatif doit vraiment etre atteint
    return max(1, math.ceil(n * percent / 100))


def apriori_pairs(baskets, support, max_pairs=5_000_000):
    # meme algorithme en deux passes que le notebook 01
    item_counts = Counter()
    for basket in baskets():
        item_counts.update(set(basket))
    frequent_items = {i: c for i, c in item_counts.items() if c >= support}
    pair_counts = Counter()
    for basket in baskets():
        kept = sorted(i for i in set(basket) if i in frequent_items)
        pair_counts.update(combinations(kept, 2))
        if len(pair_counts) > max_pairs:
            raise PairBudgetExceeded(f"More than {max_pairs:,} distinct pair counters")
    frequent_pairs = {p: c for p, c in pair_counts.items() if c >= support}
    info = dict(distinct_items=len(item_counts), frequent_items=len(frequent_items),
                pair_counters=len(pair_counts), frequent_pairs=len(frequent_pairs),
                possible_all_pairs=len(item_counts) * (len(item_counts) - 1) // 2)
    return frequent_items, frequent_pairs, info


def rules_from_pairs(pairs, counts, n, names):
    rows = []
    for (a, b), count in sorted(pairs.items()):
        for x, y in ((a, b), (b, a)):
            confidence = count / counts[x]
            rows.append(dict(if_bought=names.get(x, str(x)), then_buy=names.get(y, str(y)),
                             support=count, confidence=confidence,
                             lift=confidence / (counts[y] / n), a_id=x, b_id=y))
    return rows


def write_csv(path, rows, columns):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def rss_mb(pid):
    """Current resident process memory, including inputs; decimal MB."""
    if os.name == "nt":
        from ctypes import wintypes

        class MemoryCounters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
                (name, ctypes.c_size_t) for name in (
                    "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                    "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage",
                    "PagefileUsage", "PeakPagefileUsage")]

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE,
                                              ctypes.POINTER(MemoryCounters), wintypes.DWORD]
        handle = kernel.OpenProcess(0x1000 | 0x0010, False, pid)
        if not handle:
            return None
        try:
            counters = MemoryCounters()
            counters.cb = ctypes.sizeof(counters)
            if psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
                return counters.WorkingSetSize / 1e6
        finally:
            kernel.CloseHandle(handle)
        return None
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) * 1024 / 1e6
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return None
    return None


def worker(job_path):
    job = json.loads(Path(job_path).read_text(encoding="utf-8"))
    items = np.load(job["items"], mmap_mode="r")
    offsets = np.load(job["offsets"], mmap_mode="r")
    n = len(offsets) - 1
    baseline = rss_mb(os.getpid())

    def baskets():
        for left, right in zip(offsets[:-1], offsets[1:]):
            yield items[int(left):int(right)].tolist()

    started = time.perf_counter()
    try:
        counts, pairs, info = apriori_pairs(baskets, support_count(n, job["support_pct"]),
                                           job["max_pairs"])
        mining_s = time.perf_counter() - started
        names = {int(k): v for k, v in json.loads(Path(job["names"]).read_text(encoding="utf-8")).items()}
        rules = rules_from_pairs(pairs, counts, n, names)
        positive = [r for r in rules if r["lift"] > 1]
        covered = len({r["b_id"] for r in positive})
        # les dix meilleurs exemples gardent aussi support et confiance
        ranked = sorted(positive, key=lambda r: (-r["lift"], -r["support"], r["a_id"], r["b_id"]))
        write_csv(job["rules_file"], rules, RULE_COLUMNS)
        result = dict(status="ok", mining_s=mining_s, worker_baseline_mb=baseline,
                      worker_final_mb=rss_mb(os.getpid()), **info, rules=len(rules),
                      positive_rules=len(positive), covered_products=covered,
                      coverage_pct=100 * covered / job["catalogue_size"], top_rules=ranked[:10])
    except (PairBudgetExceeded, MemoryError) as error:
        result = dict(status="pair_limit" if isinstance(error, PairBudgetExceeded) else "memory_error",
                      error=str(error), elapsed_to_stop_s=time.perf_counter() - started,
                      worker_baseline_mb=baseline)
    write_json(job["result"], result)


def bounded_run(job, script, scratch, timeout_s, max_worker_mb):
    job_path = scratch / "job.json"
    result_path = scratch / "result.json"
    result_path.unlink(missing_ok=True)
    job["result"] = str(result_path)
    write_json(job_path, job)
    started = time.perf_counter()
    peak = 0.0
    memory_seen = False
    stop = None
    with (scratch / "worker.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen([sys.executable, str(script), "--worker", str(job_path)],
                                   stdout=log, stderr=log)
        try:
            while process.poll() is None:
                memory = rss_mb(process.pid)
                if memory is not None:
                    memory_seen = True
                    peak = max(peak, memory)
                if memory is not None and memory > max_worker_mb:
                    stop = "memory_limit"
                elif time.perf_counter() - started > timeout_s:
                    stop = "timeout"
                if stop:
                    process.kill()
                    break
                time.sleep(0.02)
            process.wait()
        except BaseException:
            process.kill()
            process.wait()
            raise
    wall = time.perf_counter() - started
    if stop:
        result = dict(status=stop, error=f"Worker stopped at {wall:.2f} s / {peak:.1f} MB")
    elif process.returncode != 0 or not result_path.exists():
        result = dict(status="error", error=(scratch / "worker.log").read_text(encoding="utf-8")[-4000:])
    else:
        result = json.loads(result_path.read_text(encoding="utf-8"))
    if result.get("worker_final_mb") is not None:
        peak = max(peak, result["worker_final_mb"])
    result.update(wall_s=wall, peak_worker_rss_mb=peak if memory_seen else None)
    baseline = result.get("worker_baseline_mb")
    result["rss_increase_mb"] = max(0, peak - baseline) if memory_seen and baseline is not None else None
    return result


def prepare_data(data_dir, cache):
    import pandas as pd

    data_dir = Path(data_dir)
    for name in ("order_products__prior.csv", "products.csv"):
        if not (data_dir / name).is_file():
            raise FileNotFoundError(f"Missing {data_dir / name}")
    started = time.perf_counter()
    source = data_dir / "order_products__prior.csv"
    # seules les deux colonnes utiles sont chargees
    prior = pd.read_csv(source, usecols=["order_id", "product_id"],
                        dtype={"order_id": "int32", "product_id": "int32"})
    orders = prior["order_id"].to_numpy()
    items = prior["product_id"].to_numpy()
    if len(orders) == 0:
        raise ValueError("The source contains no basket lines.")
    if np.any(orders[1:] < orders[:-1]):
        raise ValueError("Expected prior.csv sorted by order_id; sort it before running.")
    offsets = np.r_[0, np.flatnonzero(orders[1:] != orders[:-1]) + 1, len(orders)].astype(np.int64)
    products = pd.read_csv(data_dir / "products.csv", usecols=["product_id", "product_name"])
    names = dict(zip(products["product_id"].astype(int), products["product_name"]))
    write_json(cache / "names.json", names)
    np.save(cache / "full_items.npy", items)
    np.save(cache / "full_offsets.npy", offsets)
    digest = hashlib.sha256()
    with source.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    info = dict(source=source.name, source_bytes=source.stat().st_size,
                source_sha256=digest.hexdigest(), basket_lines=len(items),
                orders=len(offsets) - 1, catalogue_products=len(names),
                preparation_s=time.perf_counter() - started)
    del prior, orders, items, products
    gc.collect()
    return info


def sample_store(cache, n, seed):
    full_items = np.load(cache / "full_items.npy", mmap_mode="r")
    full_offsets = np.load(cache / "full_offsets.npy", mmap_mode="r")
    total = len(full_offsets) - 1
    if n >= total:
        return cache / "full_items.npy", cache / "full_offsets.npy", total
    # meme tirage que notebook 01 pour 50 000 commandes, sans remise
    chosen = np.sort(np.random.default_rng(seed).choice(total, size=n, replace=False))
    lengths = full_offsets[chosen + 1] - full_offsets[chosen]
    offsets = np.r_[0, np.cumsum(lengths)].astype(np.int64)
    items_path = cache / f"sample_{n}_items.npy"
    offsets_path = cache / f"sample_{n}_offsets.npy"
    sampled = np.lib.format.open_memmap(items_path, mode="w+", dtype="int32", shape=(int(offsets[-1]),))
    for position, index in enumerate(chosen):
        sampled[offsets[position]:offsets[position + 1]] = full_items[full_offsets[index]:full_offsets[index + 1]]
    sampled.flush()
    del sampled
    np.save(offsets_path, offsets)
    return items_path, offsets_path, n


def summaries(raw):
    groups = {}
    for row in raw:
        groups.setdefault((row["stage"], row["baskets"], row["support_pct"]), []).append(row)
    results = []
    for (stage, n, pct), rows in groups.items():
        ok = [r for r in rows if r["status"] == "ok"]
        row = dict(stage=stage, baskets=n, support_pct=pct,
                   support_baskets=support_count(n, pct), successful_repeats=len(ok),
                   attempted_repeats=len(rows), status="ok" if len(ok) == len(rows) else ",".join(sorted({r["status"] for r in rows})))
        if ok:
            for key in ("mining_s", "wall_s"):
                row[key + "_median"] = statistics.median(r[key] for r in ok)
                row[key + "_min"] = min(r[key] for r in ok)
                row[key + "_max"] = max(r[key] for r in ok)
            for key in ("peak_worker_rss_mb", "rss_increase_mb"):
                values = [r[key] for r in ok if r[key] is not None]
                row[key] = max(values) if values else None
            for key in ("distinct_items", "frequent_items", "pair_counters", "frequent_pairs", "rules",
                        "positive_rules", "covered_products", "coverage_pct", "possible_all_pairs"):
                values = {r[key] for r in ok}
                if len(values) != 1:
                    raise AssertionError(f"Nonreproducible counts for {stage}/{pct}/{key}")
                row[key] = ok[0][key]
        results.append(row)
    return results


def shortlist(rows, limit):
    # couverture d'abord, puis temps et nombre de compteurs
    feasible = [r for r in rows if r["status"] == "ok" and r.get("positive_rules", 0) > 0]
    ranked = sorted(feasible, key=lambda r: (-r["covered_products"], r["mining_s_median"], r["pair_counters"]))
    return [r["support_pct"] for r in ranked[:limit]]


def render_report(out, raw, metadata):
    summary = summaries(raw)
    if summary:
        columns = list(dict.fromkeys(key for row in summary for key in row))
        write_csv(out / "summary.csv", summary, columns)
    lines = ["# A-Priori experiment report", "", f"Run: {metadata['started_utc']} (UTC)", "",
             "## Scope and method", "",
             "Pairs only, using the two-pass A-Priori algorithm from notebook 01. No PCY.",
             "Only prior orders are used; the train file is left untouched for future evaluation.",
             "Samples are drawn uniformly without replacement with a fixed seed. Every support within a stage uses exactly the same baskets.",
             "The 50k and 250k samples use separate fixed-seed draws; they are not necessarily nested.",
             "Threshold counts use ceil(N * support_pct / 100). Products are deduplicated within each basket.",
             "", "Selection between stages maximizes the number of distinct consequents in rules with lift > 1, then prefers faster mining and fewer counters.",
             "This is a coverage/resource heuristic, not a recommendation-quality evaluation or proof of an optimal threshold.",
             "Full-data validation uses every prior order, with no sampling.", "",
             "## Measurements", "",
             "Mining time covers both A-Priori passes, including basket iteration, but excludes data preparation and rule export.",
             "Wall time also includes worker startup, loading and rule export.",
             "Worker RSS is sampled every 20 ms, in decimal MB: it includes the interpreter, mapped input pages, counters and rules. Brief peaks may be missed.",
             "RSS increase is relative to the worker after opening inputs, not an exact allocation measurement. OS file caching can affect repetitions.",
             "Parent memory is recorded separately in metadata; the worker limit is not a system-wide memory limit.",
             "Memory/time/pair stops are incomplete attempts, never treated as successful full runs.", "",
             "| Stage | Baskets | Support % | Status | Repeats OK | Mining median s | Peak worker MB | Pair counters | Rules | Products with lift > 1 |",
             "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|"]
    def fmt(value):
        return f"{value:.3f}" if isinstance(value, float) else str(value) if value is not None else "—"
    for row in summary:
        keys = ("stage", "baskets", "support_pct", "status", "successful_repeats", "mining_s_median",
                "peak_worker_rss_mb", "pair_counters", "rules", "covered_products")
        lines.append("| " + " | ".join(fmt(row.get(k)) for k in keys) + " |")
    for row in summary:
        runs = [r for r in raw if (r["stage"], r["support_pct"]) == (row["stage"], row["support_pct"])]
        lines += ["", f"## {row['stage']}: support {row['support_pct']}%", "",
                  f"Baskets: {row['baskets']:,}. Minimum pair count: {row['support_baskets']:,}.",
                  f"Status: {row['status']}. Successful repetitions: {row['successful_repeats']}/{row['attempted_repeats']}."]
        good = next((r for r in runs if r["status"] == "ok"), None)
        if good:
            lines += ["", f"Frequent individual products: {good['frequent_items']:,}; products in positive-lift rules: {good['covered_products']:,} ({good['coverage_pct']:.2f}% of the catalogue).",
                      "", "Top rules by lift (descriptive associations, not causal effects):", "",
                      "| If bought | Then buy | Pair count | Confidence | Lift |", "|---|---|---:|---:|---:|"]
            for rule in good["top_rules"]:
                lines.append(f"| {rule['if_bought'].replace('|', '/')} | {rule['then_buy'].replace('|', '/')} | {rule['support']} | {rule['confidence']:.3f} | {rule['lift']:.2f} |")
        for run in runs:
            if run["status"] != "ok":
                lines += ["", f"Repetition {run['repeat']}: {run['status']}. {run.get('error', '')}"]
    lines += ["", "## Interpretation and next step", "",
              "Compare the increase in coverage with the number of counters, mining time and RSS as support falls.",
              "A low-support run reaching a limit is evidence to investigate PCY or another implementation; this notebook never switches algorithms automatically.",
              "The number of rules and lift alone do not demonstrate improved recommendation accuracy. Held-out evaluation against popularity is still required.",
              "", "Raw repetitions: raw_runs.json. Configuration, data SHA-256 and versions: metadata.json.",
              "CSV exports retain unrounded confidence and lift. Rules include both directions, which share the same lift."]
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(out / "raw_runs.json", raw)
    write_json(out / "metadata.json", metadata)
    return summary


def run_experiments(data_dir, output_dir, repeats=3, timeout_s=300,
                    max_worker_mb=2048, max_pairs=5_000_000, seed=42,
                    sample_sizes=(50_000, 250_000), supports=SUPPORTS, script_path=None):
    import pandas as pd

    if repeats < 1 or timeout_s <= 0 or max_worker_mb <= 0 or max_pairs < 1:
        raise ValueError("Repetitions and resource budgets must be positive.")
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=False)
    script = Path(script_path or __file__).resolve()
    raw = []
    metadata = dict(started_utc=datetime.now(timezone.utc).isoformat(), seed=seed,
                    repeats=repeats, sample_sizes=list(sample_sizes), supports_pct=list(supports),
                    timeout_s=timeout_s, max_worker_mb=max_worker_mb, max_pair_counters=max_pairs,
                    python=sys.version, numpy=np.__version__, pandas=pd.__version__,
                    platform=platform.platform(), protocol="5 supports at 50k; up to 3 at 250k; up to 2 on every prior order")
    try:
        with tempfile.TemporaryDirectory(prefix="smartbasket_apriori_") as temp:
            cache = Path(temp)
            metadata["dataset"] = prepare_data(data_dir, cache)
            total = metadata["dataset"]["orders"]
            print(f"Loaded {total:,} orders / {metadata['dataset']['basket_lines']:,} lines", flush=True)
            selected = list(supports)
            for stage_index, requested in enumerate((*sample_sizes, total)):
                stage = f"sample_{stage_index + 1}" if stage_index < len(sample_sizes) else "full"
                items, offsets, n = sample_store(cache, requested, seed)
                if stage != "full" and n == total:
                    raise ValueError("Sample size must be smaller than the full dataset.")
                print(f"{stage}: {n:,} baskets; supports {selected}", flush=True)
                for pct in selected:
                    label = f"{stage}_support_{pct:g}".replace(".", "p")
                    for repeat in range(1, repeats + 1):
                        job = dict(items=str(items), offsets=str(offsets), support_pct=pct,
                                   names=str(cache / "names.json"), catalogue_size=metadata["dataset"]["catalogue_products"],
                                   max_pairs=max_pairs, rules_file=str(out / f"rules_{label}.csv"))
                        result = bounded_run(job, script, cache, timeout_s, max_worker_mb)
                        result.update(stage=stage, baskets=n, support_pct=pct, repeat=repeat)
                        raw.append(result)
                        metadata["parent_rss_mb"] = rss_mb(os.getpid())
                        summary = render_report(out, raw, metadata)
                        print(f"  {pct:g}% repeat {repeat}: {result['status']}; mining {result.get('mining_s', 0):.2f}s; wall {result['wall_s']:.2f}s; RSS {result.get('peak_worker_rss_mb')} MB", flush=True)
                        if result["status"] != "ok":
                            break
                    # ne retenir que des combinaisons ayant fini toutes les repetitions
                stage_rows = [r for r in summary if r["stage"] == stage and r["successful_repeats"] == repeats]
                selected = shortlist(stage_rows, 3 if stage_index == 0 else 2)
                metadata[f"selected_after_{stage}"] = selected
                if not selected:
                    metadata["stopped_reason"] = f"No complete feasible positive-lift configuration after {stage}"
                    break
        metadata["finished_utc"] = datetime.now(timezone.utc).isoformat()
    except BaseException as error:
        metadata["interrupted_or_error"] = f"{type(error).__name__}: {error}"
        render_report(out, raw, metadata)
        raise
    return render_report(out, raw, metadata)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", help=argparse.SUPPRESS)
    parser.add_argument("--data-dir")
    parser.add_argument("--out", default="out/apriori_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"))
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout-s", type=float, default=300)
    parser.add_argument("--max-worker-mb", type=float, default=2048)
    parser.add_argument("--max-pairs", type=int, default=5_000_000)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
    else:
        if not args.data_dir:
            parser.error("--data-dir is required")
        run_experiments(args.data_dir, args.out, repeats=args.repeats, timeout_s=args.timeout_s,
                        max_worker_mb=args.max_worker_mb, max_pairs=args.max_pairs)


if __name__ == "__main__":
    main()
