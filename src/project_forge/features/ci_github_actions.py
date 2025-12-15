from __future__ import annotations

from pathlib import Path
from project_forge.engine.fs import ForgeError

def _write(path: Path, text: str, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise ForgeError(f"File exists: {path} (use --force)")
    path.write_text(text, encoding="utf-8")

def apply(dest: Path, force: bool) -> None:
    yml = dest / ".github/workflows/ci.yml"
    _write(yml, '''name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install
        run: |
          python -m pip install -U pip
          pip install -e ".[dev]" || pip install -e .
          pip install pytest ruff
      - name: Lint
        run: ruff check .
      - name: Tests
        run: pytest
''', force)

feature = type("FeatureObj", (), {})()
feature.name = "ci-github-actions"
feature.description = "Add a GitHub Actions CI workflow (pytest + ruff)."
feature.apply = apply
