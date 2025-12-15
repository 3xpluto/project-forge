from __future__ import annotations

from pathlib import Path

from project_forge.engine.packs import list_packs
from project_forge.engine.plan import find_templates, generate
from project_forge.engine.render import load_manifest


def _builtin_root() -> Path:
    return Path(__file__).resolve().parents[1] / "src/project_forge/templates_builtin"


def _ctx_from_defaults(manifest: dict) -> dict:
    ctx: dict[str, str] = {}
    for k, spec in manifest.get("vars", {}).items():
        if isinstance(spec, dict) and "default" in spec:
            ctx[k] = str(spec["default"])
        else:
            # If no default, the CLI would require explicit --var in --yes mode.
            # In tests we fail loudly so templates don't regress.
            raise AssertionError(f"Template var '{k}' has no default")
    # Some templates have multiple vars that need to be distinct; override if needed.
    # Keep it minimal and deterministic.
    ctx.setdefault("project_name", "example")
    ctx.setdefault("package", "app")
    ctx.setdefault("package_name", "example")
    ctx.setdefault("module", "example.com/example")
    return ctx


def test_generate_each_builtin_template(tmp_path: Path) -> None:
    packs = list_packs(_builtin_root())
    templates = find_templates(packs)
    assert templates, "No templates found"

    for t in templates:
        manifest = load_manifest(t.root)
        ctx = _ctx_from_defaults(manifest)

        dest = tmp_path / t.name
        created = generate(
            template_name=t.name,
            dest=dest,
            packs=packs,
            ctx=ctx,
            force=True,
            dry_run=False,
            yes=True,
            init_git=False,
        )
        assert created, f"{t.name} produced no files"
        # Basic sanity: root exists and at least one created file exists
        assert dest.exists()
        assert any(Path(p).exists() for p in created)
