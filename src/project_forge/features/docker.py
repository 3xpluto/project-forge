from __future__ import annotations

from pathlib import Path
from project_forge.engine.fs import ForgeError

def _write(path: Path, text: str, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise ForgeError(f"File exists: {path} (use --force)")
    path.write_text(text, encoding="utf-8")

def apply(dest: Path, force: bool) -> None:
    dockerfile = dest / "Dockerfile"
    _write(dockerfile, '''# Minimal Dockerfile (adjust to your template)
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN python -m pip install -U pip && pip install -e .

CMD ["python", "-m", "app"]
''', force)

feature = type("FeatureObj", (), {})()
feature.name = "docker"
feature.description = "Add a simple Dockerfile (you may need to tweak CMD)."
feature.apply = apply
