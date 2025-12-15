from __future__ import annotations

from pathlib import Path
from project_forge.engine.fs import ForgeError

WORKFLOW = '''name: Release

on:
  push:
    tags:
      - "v*"

permissions:
  contents: read
  id-token: write

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Build
        run: |
          python -m pip install -U pip
          pip install build
          python -m build

      # Recommended: PyPI Trusted Publishing (OIDC)
      # Configure your project on PyPI to allow trusted publishing from this repo.
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
'''

def apply(dest: Path, force: bool) -> None:
    wf = dest / ".github/workflows/release.yml"
    wf.parent.mkdir(parents=True, exist_ok=True)
    if wf.exists() and not force:
        raise ForgeError(f"File exists: {wf} (use --force)")
    wf.write_text(WORKFLOW, encoding="utf-8")

feature = type("FeatureObj", (), {})()
feature.name = "release-python-pypi"
feature.description = "Add a tag-based release workflow that builds and publishes to PyPI (Trusted Publishing / OIDC)."
feature.apply = apply
