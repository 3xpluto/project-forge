from __future__ import annotations

import re
from pathlib import Path

from project_forge.engine.fs import ForgeError


RUFF_SECTION = '''
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
ignore = []
'''


BLACK_SECTION = '''
[tool.black]
line-length = 100
target-version = ["py311"]
'''

MYPY_SECTION = '''
[tool.mypy]
python_version = "3.11"
strict = true
warn_unused_configs = true
'''

PRECOMMIT_CONFIG = '''repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.12.1
    hooks:
      - id: mypy
'''


def _append_block_if_missing(pyproject: Path, marker: str, block: str) -> None:
    txt = pyproject.read_text(encoding="utf-8")
    if marker in txt:
        return
    if not txt.endswith("\n"):
        txt += "\n"
    pyproject.write_text(txt + "\n" + block.lstrip("\n"), encoding="utf-8")


def _ensure_dev_extra(pyproject: Path) -> None:
    txt = pyproject.read_text(encoding="utf-8")

    # If a dev extra already exists, don't touch it.
    if "[project.optional-dependencies]" in txt and re.search(r"^dev\s*=", txt, flags=re.M):
        return

    dev_line = 'dev = ["pytest", "ruff", "black", "mypy", "pre-commit"]\n'

    if "[project.optional-dependencies]" in txt:
        # Insert dev line inside existing optional deps section.
        lines = txt.splitlines(True)
        out = []
        in_section = False
        inserted = False
        for line in lines:
            if line.strip() == "[project.optional-dependencies]":
                in_section = True
                out.append(line)
                continue

            if in_section and line.strip().startswith("[") and line.strip().endswith("]"):
                if not inserted:
                    out.append(dev_line)
                    inserted = True
                in_section = False

            out.append(line)

        if in_section and not inserted:
            out.append(dev_line)

        pyproject.write_text("".join(out), encoding="utf-8")
        return

    # Otherwise append a new section
    block = "\n[project.optional-dependencies]\n" + dev_line
    if not txt.endswith("\n"):
        txt += "\n"
    pyproject.write_text(txt + block, encoding="utf-8")


def apply(dest: Path, force: bool) -> None:
    pyproject = dest / "pyproject.toml"
    if not pyproject.exists():
        raise ForgeError("python-quality expects pyproject.toml in the project root")

    _ensure_dev_extra(pyproject)

    _append_block_if_missing(pyproject, "[tool.ruff]", RUFF_SECTION)
    _append_block_if_missing(pyproject, "[tool.black]", BLACK_SECTION)
    _append_block_if_missing(pyproject, "[tool.mypy]", MYPY_SECTION)

    pc = dest / ".pre-commit-config.yaml"
    if pc.exists() and not force:
        raise ForgeError(f"File exists: {pc} (use --force)")
    pc.write_text(PRECOMMIT_CONFIG, encoding="utf-8")


feature = type("FeatureObj", (), {})()
feature.name = "python-quality"
feature.description = "Add ruff + black + mypy + pre-commit config (and a dev extra in pyproject.toml)."
feature.apply = apply
