# OpenBench

LLM benchmark dashboard. Displays and compares scores for the latest models via an interactive bar chart.

## Quick Start

```bash
direnv allow      # create venv, install deps, set PORT
python src/main.py
# → http://localhost:$PORT
```

Or with Docker:

```bash
./scripts/build.sh
docker compose up
```

## Features

- Model selector — toggle models on/off
- Benchmark filter — limited to the common set for selected models
- Grouped bar chart with per-benchmark averages
- Data table with best scores highlighted

## Structure

```
src/
  main.py               # Flask app + /api/benchmarks endpoint
  data/benchmarks.json  # Ordered benchmark key definitions
  data/models/*.json    # Per-model benchmark data and source URLs
  templates/index.html  # Single-page dashboard (Chart.js)
test/
  test_benchmarks.py    # Schema, data, and API tests
scripts/                # build, deploy, venv helpers
.github/workflows/ci.yml
```

## Adding a Model

1. Add a JSON file under `src/data/models/` following the existing schema (`id`, `name`, `provider`, `release_date`, `urls`, `color`, `benchmarks`).
2. Use consistent benchmark key names for intersection logic to work.
3. Add any brand-new benchmark names to `src/data/benchmarks.json` so they appear in the desired order.
3. Run `pytest`.
