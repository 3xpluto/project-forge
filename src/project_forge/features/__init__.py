from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from project_forge.engine.fs import ForgeError

@dataclass(frozen=True)
class Feature:
    name: str
    description: str
    apply: Callable[[Path, bool], None]

def registry() -> list[Feature]:
    from .ci_github_actions import feature as ci
    from .docker import feature as docker
    from .python_quality import feature as pyq
    from .release_python_pypi import feature as rel
    return [ci, docker, pyq, rel]

def get(name: str) -> Feature:
    for f in registry():
        if f.name == name:
            return f
    raise ForgeError(f"Unknown feature '{name}'. Try: forge features")
