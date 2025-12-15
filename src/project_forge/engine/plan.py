from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .fs import ForgeError
from .packs import Pack, iter_template_dirs
from .render import Template, load_manifest, render_plan, apply_plan
from .hooks import run_post_hooks

@dataclass(frozen=True)
class LocatedTemplate:
    name: str
    root: Path
    pack: Pack

def find_templates(packs: list[Pack]) -> list[LocatedTemplate]:
    found: list[LocatedTemplate] = []
    for pack in packs:
        for tdir in iter_template_dirs([pack]):
            if not tdir.exists():
                continue
            for child in tdir.iterdir():
                if child.is_dir() and (child / "forge.json").exists():
                    found.append(LocatedTemplate(name=child.name, root=child, pack=pack))
    # keep last win (later packs override earlier)
    dedup: dict[str, LocatedTemplate] = {}
    for t in found:
        dedup[t.name] = t
    return sorted(dedup.values(), key=lambda x: x.name)

def get_template(name: str, packs: list[Pack]) -> LocatedTemplate:
    for t in find_templates(packs):
        if t.name == name:
            return t
    raise ForgeError(f"Template '{name}' not found. Try: forge list")

def generate(
    template_name: str,
    dest: Path,
    packs: list[Pack],
    ctx: Mapping[str, Any],
    force: bool,
    dry_run: bool,
    yes: bool,
    init_git: bool,
) -> list[str]:
    lt = get_template(template_name, packs)
    manifest = load_manifest(lt.root)
    tpl = Template(name=lt.name, root=lt.root, manifest=manifest)
    ops = render_plan(tpl, dest, ctx)

    created: list[str] = [str(op.dst) for op in ops]

    if dry_run:
        return created

    dest.mkdir(parents=True, exist_ok=True)
    apply_plan(ops, force=force)

    if init_git:
        _git_init(dest)

    run_post_hooks(manifest, dest, ctx, yes=yes)
    return created

def _git_init(dest: Path) -> None:
    import subprocess
    try:
        subprocess.run(["git", "init"], cwd=str(dest), check=True)
    except FileNotFoundError:
        raise ForgeError("git not found (install git or omit --git)")
