from __future__ import annotations

from pathlib import Path

from project_forge.engine.packs import list_packs
from project_forge.engine.plan import generate
from project_forge.engine.render import load_manifest
from project_forge.features import get as get_feature


def _builtin_root() -> Path:
    return Path(__file__).resolve().parents[1] / "src/project_forge/templates_builtin"


def test_apply_ci_and_release_features(tmp_path: Path) -> None:
    packs = list_packs(_builtin_root())

    # Generate a python-cli project
    troot = _builtin_root() / "python-cli"
    manifest = load_manifest(troot)
    ctx = {k: str(v.get("default", "")) for k, v in manifest["vars"].items()}
    ctx["project_name"] = "mytool"
    ctx["package"] = "mytool"

    dest = tmp_path / "mytool"
    generate("python-cli", dest, packs, ctx, force=True, dry_run=False, yes=True, init_git=False)

    # Apply CI feature
    get_feature("ci-github-actions").apply(dest, force=True)
    assert (dest / ".github/workflows/ci.yml").exists()

    # Apply Release feature
    get_feature("release-python-pypi").apply(dest, force=True)
    assert (dest / ".github/workflows/release.yml").exists()


def test_apply_python_quality_feature(tmp_path: Path) -> None:
    packs = list_packs(_builtin_root())

    troot = _builtin_root() / "python-cli"
    manifest = load_manifest(troot)
    ctx = {k: str(v.get("default", "")) for k, v in manifest["vars"].items()}
    ctx["project_name"] = "mytool"
    ctx["package"] = "mytool"

    dest = tmp_path / "mytool"
    generate("python-cli", dest, packs, ctx, force=True, dry_run=False, yes=True, init_git=False)

    get_feature("python-quality").apply(dest, force=True)

    pyproject = (dest / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.ruff]" in pyproject
    assert "[tool.black]" in pyproject
    assert "[tool.mypy]" in pyproject
    assert (dest / ".pre-commit-config.yaml").exists()


def test_apply_docker_feature(tmp_path: Path) -> None:
    packs = list_packs(_builtin_root())

    troot = _builtin_root() / "python-fastapi"
    manifest = load_manifest(troot)
    ctx = {k: str(v.get("default", "")) for k, v in manifest["vars"].items()}
    ctx["project_name"] = "api"
    ctx["package"] = "app"

    dest = tmp_path / "api"
    generate("python-fastapi", dest, packs, ctx, force=True, dry_run=False, yes=True, init_git=False)

    get_feature("docker").apply(dest, force=True)
    assert (dest / "Dockerfile").exists()
