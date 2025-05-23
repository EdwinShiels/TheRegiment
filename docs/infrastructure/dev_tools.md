✅ Dev Tooling

Use `.pre-commit-config.yaml` to enforce:

- black (code formatting)
- isort (import sorting)
- flake8 (optional)

Cursor should generate this file.

Run `pre-commit install` locally after setting up the repo.

Local dev:
- Use Docker Compose to spin up bot + API together
- Run tests via `poetry run pytest`

Deployment to Railway once all modules are scaffolded and tested
