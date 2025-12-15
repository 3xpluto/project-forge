from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TEMPLATES = [
    ("python-cli", ["--var", "project_name=pythoncli", "--var", "package=pythoncli"]),
    ("python-fastapi", ["--var", "project_name=pythonfastapi", "--var", "package=app"]),
    ("go-api", ["--var", "project_name=goapi", "--var", "module=example.com/goapi"]),
    ("rust-cli", ["--var", "project_name=rustcli"]),
    ("rust-axum-api", ["--var", "project_name=rustaxum"]),
    ("node-ts-cli", ["--var", "project_name=nodetscli", "--var", "package_name=nodetscli"]),
    ("node-express-api", ["--var", "project_name=nodeexpress", "--var", "package_name=nodeexpress"]),
]

def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)

def main() -> int:
    forge = shutil.which("forge")
    if not forge:
        print("forge not found on PATH. Install project-forge (pip install -e .) first.", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        for name, vars_ in TEMPLATES:
            dest = base / name
            run([forge, "new", name, str(dest), "--yes", *vars_])

        # Python template tests
        run([sys.executable, "-m", "pip", "install", "-U", "pip"])
        # Add python-quality on python-cli and run tools if available
        run([forge, "add", "python-quality", str(base/"python-cli")])
        try:
            run([sys.executable, "-m", "pip", "install", "-e", str(base/"python-cli") + "[dev]"], cwd=base/"python-cli")
        except subprocess.CalledProcessError:
            run([sys.executable, "-m", "pip", "install", "-e", "."], cwd=base/"python-cli")
        for tool in ("ruff", "black", "mypy", "pytest"):
            if shutil.which(tool):
                run([tool, "--version"])
        print("Generated all templates into:", base)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
