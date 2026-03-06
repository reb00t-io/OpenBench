# AGENTS.md

## 1. Mission & Priorities
**Role:** Serve a benchmarking dashboard that displays and compares LLM benchmark scores for the latest models. Data is stored as a static JSON; the Flask app renders an interactive bar-chart UI.

**Decision priority order:** correctness > security > maintainability > performance > speed

**Global constraints/goals:** Must run on Python 3.13, Docker, and GitHub Actions without exposing secrets.

## 2. Executable Commands (Ground Truth)
All commands listed here must work.

- **Run dev server:** `python src/main.py` (or `uvicorn src.main:app --port $PORT`)
- **Docker build:** `./scripts/build.sh [linux/amd64]`
- **Run e2e tests:** `./test/e2e.sh`
- **Deploy:** `./scripts/deploy.sh`
- **Unit tests:** `pytest`
- **Lint / format / type-check:** (not defined; follow PEP 8)

## 3. Repository Map
**High-level structure:**
- `src/` — Flask app (`main.py`), Jinja2 templates (`templates/`), static benchmark data (`data/`)
- `src/data/benchmarks.json` — canonical source of truth for all model benchmark scores
- `scripts/` — helper scripts (build, deploy, venv, CI utilities)
- `test/` — pytest unit tests and e2e shell test
- `config/nginx/` — Nginx site configuration
- `.github/workflows/ci.yml` — CI pipeline
- `Dockerfile`, `docker-compose.yml` — container configuration
- `pyproject.toml` — package metadata and dependencies

- for new benchmarks, make sure to reuse the keys defined in src/data/benchmarks.json

**Entry points:**
- Backend: `src/main.py`
- Data: `src/data/benchmarks.json`

**Key configuration locations:**
- Environment variables: `.envrc`
- CI environment: `.github/workflows/ci.yml`

## 4. Definition of Done
For any change, the following must hold:
- [ ] `pytest` passes
- [ ] New benchmark data validated against `benchmarks.json` schema (list of models with `id`, `name`, `provider`, `url`, `color`, `benchmarks` dict)
- [ ] Documentation updated if routes or data shape changes
- [ ] PR description summarises the change

## 5. Code Style & Conventions (Repo-Specific)
- **Language(s) + version(s):** Python 3.13, Flask 3.1.2, Uvicorn 0.40.0
- **Formatter:** Not enforced; follow PEP 8
- **Naming conventions:** snake_case for functions/variables, PascalCase for classes
- **Error handling:** Raise exceptions for unexpected states; avoid bare `except:`
- **Logging:** Use `print` or standard logging only for important events; do not log secrets

## 6. Boundaries & Guardrails
The agent must **not**:
- Commit secret values (e.g., API keys, passwords)
- Modify files unrelated to the requested change
- Bypass or disable CI checks
- Add new runtime dependencies without updating `pyproject.toml`
- Mutate `benchmarks.json` at runtime; it is read-only static data

When unsure:
- Prefer the smallest possible change
- Add a TODO comment with context rather than guessing

## 7. Security & Privacy Constraints
- **Sensitive data locations:** `.envrc` may contain secrets; never commit actual secret values.
- **Redaction rules:** Ensure any secret placeholders are replaced with generic values before committing.
- **Approved patterns:** Use environment variables for credentials; do not hard-code them.

## 8. Common Pitfalls & Couplings
- Changing `PORT` in `.envrc` requires updating `Dockerfile` `EXPOSE`, `docker-compose.yml`, and Nginx config.
- Changing the Docker image name requires updating `scripts/build.sh`, `scripts/deploy.sh`, and `docker-compose.yml`.
- When adding new Python packages, update `pyproject.toml` and run `pip install -e .[dev]`.
- When adding a new model to `benchmarks.json`, use consistent benchmark key names so the intersection logic works correctly.
- The `/api/benchmarks` endpoint returns `benchmarks.json` verbatim — shape changes break the frontend.

## 9. Examples & Canonical Patterns

### Adding a new model
1. Add an entry to `src/data/benchmarks.json` following the existing schema.
2. Use the same benchmark key names as existing models where applicable.
3. Run `pytest` — the schema test will validate the new entry.

### Adding a new route
1. Create view function in `src/main.py`.
2. Add corresponding template under `src/templates/`.
3. Add tests in `test/` if applicable.
4. Run `pytest` and `./test/e2e.sh` locally.

## 10. Pull Requests & Branching
- **Default branch:** `main`
- **Branch naming:** `agent/<descriptive-name>`
- **PR creation:** Use `gh pr create` with a clear title and bullet-point summary.
