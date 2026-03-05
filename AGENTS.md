# AGENTS.md

## 1. Mission & Priorities
- **Role:** Provide a ready‑to‑use scaffold for Python Flask + Uvicorn web applications, including CI/CD, Docker, and deployment scripts.
- **Decision priority order:** correctness > security > maintainability > performance > speed
- **Global constraints/goals:** Must run on Python 3.13, Docker, and GitHub Actions without exposing secrets.

## 2. Executable Commands (Ground Truth)
All commands listed here must work.

- **Install / setup:** `direnv allow` (creates a virtualenv, installs dev dependencies)
- **Run dev server:** `python src/main.py` (or `uvicorn src.main:app --port $PORT`)
- **Docker build:** `./scripts/build.sh [linux/amd64]`
- **Run e2e tests:** `./test/e2e.sh`
- **Deploy:** `./scripts/deploy.sh`
- **Lint / format / type‑check:** (not defined; add as needed)
- **Unit tests:** `pytest`

## 3. Repository Map
**High‑level structure:**
- `src/` — application source code (Flask app, templates)
- `scripts/` — helper scripts (build, deploy, venv, CI utilities)
- `test/` — end‑to‑end test script
- `config/nginx/` — Nginx site configuration
- `.github/workflows/ci.yml` — CI pipeline
- `Dockerfile`, `docker-compose.yml` — container configuration
- `pyproject.toml` — package metadata and dependencies
- `README.md` — project overview
- `.envrc` — direnv environment loader

**Entry points:**
- Backend: `src/main.py`
- CLI / worker: various helper scripts in `scripts/`

**Key configuration locations:**
- Environment variables: `.envrc`
- CI environment: `.github/workflows/ci.yml`
- Docker image name / port: `scripts/build.sh`, `scripts/deploy.sh`

## 4. Definition of Done
For any change, the following must hold:
- [ ] Required tests added or updated
- [ ] All checks (CI, lint, type‑check) pass
- [ ] Documentation updated if behavior changes
- [ ] A concise PR description summarises the change

## 5. Code Style & Conventions (Repo‑Specific)
- **Language(s) + version(s):** Python 3.13, Flask 3.1.2, Uvicorn 0.40.0
- **Formatter:** Not enforced; follow PEP 8
- **Naming conventions:** snake_case for functions/variables, PascalCase for classes
- **Error handling:** Raise exceptions for unexpected states; avoid bare `except:`
- **Logging:** Use `print` or standard logging only for important events; do not log secrets

## 6. Boundaries & Guardrails
The agent must **not**:
- Commit secret values (e.g., API keys, passwords)
- Modify files unrelated to the requested change
- Bypass or disable CI checks
- Add new runtime dependencies without updating `pyproject.toml`

When unsure:
- Prefer the smallest possible change
- Add a TODO comment with context rather than guessing

## 7. Security & Privacy Constraints
- **Sensitive data locations:** `.envrc` may contain secrets; never commit actual secret values.
- **Redaction rules:** Ensure any secret placeholders are replaced with generic values before committing.
- **Approved patterns:** Use environment variables for credentials; do not hard‑code them.

## 8. Common Pitfalls & Couplings
- Changing `PORT` in `.envrc` requires updating `Dockerfile` `EXPOSE`, `docker-compose.yml`, and Nginx config.
- Changing the Docker image name requires updating `scripts/build.sh`, `scripts/deploy.sh`, and `docker-compose.yml`.
- When adding new Python packages, update `pyproject.toml` and run `pip install -e .[dev]`.

## 9. Examples & Canonical Patterns (Optional)
- **Adding a new route:**
  1. Create view function in `src/main.py`.
  2. Add corresponding template under `src/templates/`.
  3. Add tests in `test/` if applicable.
  4. Run `pytest` and `./test/e2e.sh` locally.

## 10. Pull Requests & Branching
- **Default branch:** `main`
- **Branch naming:** `agent/<descriptive-name>`
- **PR creation:** Use `gh pr create` with a clear title and bullet‑point summary.
