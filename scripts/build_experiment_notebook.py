"""Generate the portable Colab notebook from the canonical experiment script."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
engine = (ROOT / "scripts" / "apriori_experiments.py").read_text(encoding="utf-8")


def cell(kind, source):
    result = dict(cell_type=kind, metadata={}, source=source.strip("\n").splitlines(keepends=True))
    if kind == "code":
        result.update(execution_count=None, outputs=[])
    return result


cells = [
    cell("markdown", """
# SmartBasket — A-Priori experiments

This notebook is self-contained: the worker code is bundled below, so a GitHub clone is not required in Colab.
It uses the same two-pass **pair** mining method as notebook 01. **No PCY** is run.

Protocol:
1. Five support thresholds (0.5%, 0.25%, 0.1%, 0.075%, 0.05%) on 50,000 random prior orders.
2. Up to three completed configurations on 250,000 random prior orders.
3. Up to two completed configurations on **every prior order**, without sampling.

Each configuration is repeated three times. Selection maximizes product coverage in rules with lift > 1,
then prefers shorter mining time and fewer pair counters. It does not establish recommendation accuracy.
Raw runs, timing ranges, sampled worker RSS, rules, source SHA-256 and a per-configuration report are exported.
Limits stop individual workers; they never silently replace a full-data run with a sample.

Run cells in order. A local data directory must contain `order_products__prior.csv` and `products.csv`.
If no directory is supplied, the notebook downloads the same Kaggle dataset as notebook 01.
If Kaggle authentication is needed, add `KAGGLE_API_TOKEN` as a Colab secret. Never put a token in a cell.
"""),
    cell("code", '''
# parametres des experiences et emplacement des fichiers
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR = os.environ.get("SB_DATA_DIR", "")  # sinon telechargement Kaggle
OUTPUT_DIR = "out/apriori_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
REPEATS = 3
TIMEOUT_S = 300           # limite par repetition, demarrage et export inclus
MAX_WORKER_MB = 2048      # memoire du processus de calcul, pas celle de tout Colab
MAX_PAIRS = 5_000_000
SEED = 42
'''),
    cell("code", '''
# chargement des donnees locales ou du dataset complet depuis Kaggle
if not DATA_DIR:
    import importlib.util
    import subprocess
    if importlib.util.find_spec("kagglehub") is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "kagglehub"])
    try:
        from google.colab import userdata
        token = userdata.get("KAGGLE_API_TOKEN")
        if token:
            os.environ["KAGGLE_API_TOKEN"] = token
        del token
    except Exception:
        pass  # un dataset public peut aussi etre disponible sans secret
    import kagglehub
    DATA_DIR = kagglehub.dataset_download("psparks/instacart-market-basket-analysis")

DATA_DIR = Path(DATA_DIR).expanduser().resolve()
for filename in ("order_products__prior.csv", "products.csv"):
    path = DATA_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(path)
    print(filename, f"{path.stat().st_size / 1e6:.1f} MB")
'''),
    cell("markdown", """
## Experiment engine

The next cell installs no software. It writes our bundled Python worker to a temporary directory and imports it.
The canonical source is `scripts/apriori_experiments.py`; regenerate this notebook with
`python scripts/build_experiment_notebook.py` after changing that script.
"""),
    cell("code", "# code du projet embarque pour que le notebook fonctionne seul dans Colab\n"
         + "ENGINE_SOURCE = r'''\n" + engine + "\n'''\n\n"
         + '''import tempfile
import importlib.util

_worker_directory = tempfile.TemporaryDirectory(prefix="smartbasket_notebook_")
ENGINE_SCRIPT = Path(_worker_directory.name) / "apriori_experiments.py"
ENGINE_SCRIPT.write_text(ENGINE_SOURCE, encoding="utf-8")
_spec = importlib.util.spec_from_file_location("smartbasket_experiments", ENGINE_SCRIPT)
experiments = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(experiments)
print("A-Priori experiment engine ready")
'''),
    cell("code", '''
# essais progressifs puis validation sur toutes les commandes prior
summary = experiments.run_experiments(
    DATA_DIR, OUTPUT_DIR,
    repeats=REPEATS, timeout_s=TIMEOUT_S,
    max_worker_mb=MAX_WORKER_MB, max_pairs=MAX_PAIRS, seed=SEED,
    script_path=ENGINE_SCRIPT,
)
'''),
    cell("code", '''
# tableau de comparaison des mesures, sans confondre couverture et precision
import pandas as pd
display(pd.DataFrame(summary))
from IPython.display import Markdown
display(Markdown((Path(OUTPUT_DIR) / "report.md").read_text(encoding="utf-8")))
'''),
    cell("markdown", """
## Keep the evidence

The report and raw JSON are updated after every repetition. Failed or capped attempts are kept with their status.
If interrupted, inspect the files already saved in `OUTPUT_DIR`.
The archive below contains results only: no dataset and no credentials.
In Colab, run the final cell to download it and preserve it before the runtime closes.
"""),
    cell("code", '''
# archive des resultats et du compte rendu
import shutil
archive = shutil.make_archive(str(Path(OUTPUT_DIR).resolve()), "zip", root_dir=OUTPUT_DIR)
print(archive)
'''),
    cell("code", '''
# telechargement des resultats depuis Colab, facultatif en local
try:
    from google.colab import files
except ImportError:
    print("Local run: results are in", Path(OUTPUT_DIR).resolve())
else:
    files.download(archive)
'''),
]

for index, entry in enumerate(cells):
    entry["id"] = f"apriori-{index:02d}"
notebook = dict(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                      "language_info": {"name": "python", "version": "3"}},
                nbformat=4, nbformat_minor=5)
path = ROOT / "notebooks" / "02_apriori_experiments.ipynb"
path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(path)
