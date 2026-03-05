import json
import os
from pathlib import Path

from flask import Flask, jsonify, render_template

app = Flask(__name__)

VERSION = Path("VERSION").read_text().strip()
DEPLOY_DATE = os.environ.get("DEPLOY_DATE", "unknown")

_DATA_DIR = Path(__file__).parent / "data"


def load_benchmarks():
    bench_defs = json.loads((_DATA_DIR / "benchmarks.json").read_text())
    models = [
        json.loads(p.read_text())
        for p in sorted((_DATA_DIR / "models").glob("*.json"))
    ]
    return {"benchmark_defs": bench_defs, "models": models}


@app.route("/")
def index():
    return render_template("index.html", version=VERSION, deploy_date=DEPLOY_DATE)


@app.route("/api/benchmarks")
def benchmarks():
    return jsonify(load_benchmarks())


if __name__ == "__main__":
    import uvicorn
    from asgiref.wsgi import WsgiToAsgi

    print(f"OpenBench v{VERSION} (deployed {DEPLOY_DATE})", flush=True)
    port = int(os.environ["PORT"])
    uvicorn.run(WsgiToAsgi(app), host="0.0.0.0", port=port, log_level="info", lifespan="off")
