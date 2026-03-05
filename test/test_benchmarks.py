"""Tests for benchmark data integrity and the /api/benchmarks endpoint."""
import json
from pathlib import Path

import pytest

_DATA_DIR = Path(__file__).parent.parent / "src" / "data"
BENCH_DEFS_PATH = _DATA_DIR / "benchmarks.json"
MODELS_DIR = _DATA_DIR / "models"


@pytest.fixture(scope="module")
def benchmark_data():
    from src.main import load_benchmarks
    return load_benchmarks()


@pytest.fixture(scope="module")
def client():
    import os
    os.environ.setdefault("PORT", "8000")
    from src.main import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── Data schema tests ──────────────────────────────────────────────────────────

class TestBenchmarkSchema:
    def test_files_exist(self):
        assert BENCH_DEFS_PATH.exists(), "src/data/benchmarks.json not found"
        assert MODELS_DIR.is_dir() and any(MODELS_DIR.glob("*.json")), \
            "src/data/models/ has no JSON files"

    def test_top_level_keys(self, benchmark_data):
        assert "models" in benchmark_data
        assert "benchmark_defs" in benchmark_data
        assert isinstance(benchmark_data["benchmark_defs"], list)
        assert all("key" in d and "name" in d for d in benchmark_data["benchmark_defs"])

    def test_models_is_list(self, benchmark_data):
        assert isinstance(benchmark_data["models"], list)

    def test_at_least_one_model(self, benchmark_data):
        assert len(benchmark_data["models"]) >= 1

    def test_required_model_fields(self, benchmark_data):
        required = {"id", "name", "provider", "url", "color", "benchmarks"}
        for model in benchmark_data["models"]:
            missing = required - model.keys()
            assert not missing, f"{model.get('id')} missing fields: {missing}"

    def test_benchmarks_are_floats_or_ints(self, benchmark_data):
        for model in benchmark_data["models"]:
            for key, val in model["benchmarks"].items():
                assert isinstance(val, (int, float)), (
                    f"{model['id']} → {key}: expected number, got {type(val)}"
                )

    def test_scores_in_valid_range(self, benchmark_data):
        for model in benchmark_data["models"]:
            for key, val in model["benchmarks"].items():
                assert 0 <= val <= 100, (
                    f"{model['id']} → {key}: score {val} out of [0, 100]"
                )

    def test_unique_model_ids(self, benchmark_data):
        ids = [m["id"] for m in benchmark_data["models"]]
        assert len(ids) == len(set(ids)), "Duplicate model IDs found"

    def test_color_format(self, benchmark_data):
        import re
        hex_re = re.compile(r"^#[0-9a-fA-F]{6}$")
        for model in benchmark_data["models"]:
            assert hex_re.match(model["color"]), (
                f"{model['id']} has invalid color: {model['color']}"
            )


# ── Known data spot-checks ─────────────────────────────────────────────────────

class TestKnownValues:
    def _get_model(self, data, model_id):
        for m in data["models"]:
            if m["id"] == model_id:
                return m
        pytest.fail(f"Model {model_id!r} not found in data")

    def test_qwen_gpqa(self, benchmark_data):
        m = self._get_model(benchmark_data, "qwen3.5-397b")
        assert m["benchmarks"]["GPQA-Diamond"] == pytest.approx(88.4)

    def test_kimi_swebench(self, benchmark_data):
        m = self._get_model(benchmark_data, "kimi-k2.5")
        assert m["benchmarks"]["SWE-bench Verified"] == pytest.approx(76.8)

    def test_glm5_imo(self, benchmark_data):
        m = self._get_model(benchmark_data, "glm-5")
        assert m["benchmarks"]["IMOAnswerBench"] == pytest.approx(82.5)


# ── Common-benchmark intersection logic ───────────────────────────────────────

class TestCommonBenchmarks:
    def _common(self, data, model_ids):
        models = [m for m in data["models"] if m["id"] in model_ids]
        if not models:
            return set()
        sets = [set(m["benchmarks"].keys()) for m in models]
        result = sets[0]
        for s in sets[1:]:
            result = result & s
        return result

    def test_all_models_share_gpqa(self, benchmark_data):
        ids = [m["id"] for m in benchmark_data["models"]]
        common = self._common(benchmark_data, ids)
        assert "GPQA-Diamond" in common

    def test_models_with_hle_share_it(self, benchmark_data):
        # GPT-OSS-120B only reports "HLE w/ CoT", so HLE is not universal
        ids_with_hle = [
            m["id"] for m in benchmark_data["models"] if "HLE" in m["benchmarks"]
        ]
        assert len(ids_with_hle) >= 4, "Expected most models to have HLE"

    def test_all_models_share_swebench_verified(self, benchmark_data):
        ids = [m["id"] for m in benchmark_data["models"]]
        common = self._common(benchmark_data, ids)
        assert "SWE-bench Verified" in common

    def test_qwen_kimi_share_mmlu_pro(self, benchmark_data):
        common = self._common(benchmark_data, {"qwen3.5-397b", "kimi-k2.5"})
        assert "MMLU-Pro" in common


# ── API tests ─────────────────────────────────────────────────────────────────

class TestAPI:
    def test_index_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_benchmarks_endpoint_returns_200(self, client):
        r = client.get("/api/benchmarks")
        assert r.status_code == 200

    def test_benchmarks_endpoint_content_type(self, client):
        r = client.get("/api/benchmarks")
        assert "application/json" in r.content_type

    def test_benchmarks_endpoint_has_models(self, client):
        r = client.get("/api/benchmarks")
        body = r.get_json()
        assert "models" in body
        assert len(body["models"]) >= 1

    def test_unknown_route_404(self, client):
        r = client.get("/does-not-exist")
        assert r.status_code == 404
