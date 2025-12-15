# Features

Features can be applied after generation:

```bash
forge features
forge add python-quality ./mytool
forge add release-python-pypi ./mytool
```

## python-quality

Adds:
- `ruff` config (`[tool.ruff]`)
- `black` config (`[tool.black]`)
- `mypy` config (`[tool.mypy]`)
- `.pre-commit-config.yaml`
- a `dev` extra in `pyproject.toml` with common tooling deps

## release-python-pypi

Adds `.github/workflows/release.yml` that:
- triggers on tags like `v0.1.0`
- builds via `python -m build`
- publishes via `pypa/gh-action-pypi-publish` (Trusted Publishing / OIDC)
