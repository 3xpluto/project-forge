from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from project_forge.engine.fs import ForgeError
from project_forge.engine.packs import PACKS_LOCK, add_pack, list_packs, remove_pack
from project_forge.engine.plan import find_templates, generate
from project_forge.features import registry as feature_registry, get as get_feature

app = typer.Typer(help="Project Forge: generate production-ready projects from templates.")
pack_app = typer.Typer(help="Manage template packs.")
app.add_typer(pack_app, name="pack")

console = Console()

def _builtin_root() -> Path:
    return Path(__file__).parent / "templates_builtin"

def _parse_vars(kvs: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for kv in kvs:
        if "=" not in kv:
            raise ForgeError(f"Invalid --var {kv!r}. Use key=value.")
        k, v = kv.split("=", 1)
        k = k.strip()
        if not k:
            raise ForgeError("Empty var key")
        out[k] = v
    return out

def _prompt_vars(template_manifest: dict, provided: dict, yes: bool) -> dict:
    vars_spec = template_manifest.get("vars", {})
    ctx = dict(provided)
    for k, spec in vars_spec.items():
        if k in ctx:
            continue
        prompt = k
        default = ""
        regex = None
        if isinstance(spec, dict):
            prompt = str(spec.get("prompt", k))
            default = str(spec.get("default", "")) if "default" in spec else ""
            regex = spec.get("regex")
        if yes and default != "":
            val = default
        elif yes and default == "":
            raise ForgeError(f"Missing required var '{k}' (provide --var {k}=...)")
        else:
            val = typer.prompt(prompt, default=default if default != "" else None)
        if regex:
            import re
            if not re.fullmatch(regex, val):
                raise ForgeError(f"Var '{k}' did not match regex {regex!r}")
        ctx[k] = val
    return ctx

def _print_tree(dest: Path, created: list[str]) -> None:
    root_tree = Tree(str(dest))
    # Build a nested dict structure from created paths
    rels = []
    for p in created:
        try:
            rels.append(Path(p).resolve().relative_to(dest.resolve()))
        except Exception:
            # If outside (shouldn't happen), just show absolute
            rels.append(Path(p))
    rels = sorted(rels, key=lambda x: (len(x.parts), str(x)))
    nodes = {(): root_tree}

    for rel in rels:
        cur = ()
        for i, part in enumerate(rel.parts):
            nxt = cur + (part,)
            if nxt not in nodes:
                parent = nodes[cur]
                nodes[nxt] = parent.add(part)
            cur = nxt

    console.print(root_tree)

@app.command("list")
def list_templates() -> None:
    packs = list_packs(_builtin_root())
    templates = find_templates(packs)
    t = Table(title="Templates")
    t.add_column("Name", style="bold")
    t.add_column("Pack")
    t.add_column("Kind")
    for item in templates:
        t.add_row(item.name, item.pack.name, item.pack.kind)
    console.print(t)

@app.command("new")
def new(
    template: str = typer.Argument(..., help="Template name"),
    dest: Path = typer.Argument(..., help="Destination folder"),
    var: list[str] = typer.Option([], "--var", help="Template variables (key=value). Repeatable."),
    yes: bool = typer.Option(False, "--yes", help="Non-interactive. Use defaults and fail if required vars missing."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be written without writing."),
    git: bool = typer.Option(False, "--git", help="Run git init in destination."),
    output: str = typer.Option("list", "--output", help="Output style: list or tree"),
) -> None:
    packs = list_packs(_builtin_root())

    # Find template root + manifest for prompting
    from project_forge.engine.plan import get_template
    from project_forge.engine.render import load_manifest
    lt = get_template(template, packs)
    manifest = load_manifest(lt.root)

    provided = _parse_vars(var)
    ctx = _prompt_vars(manifest, provided, yes=yes)
    dest = dest.resolve()

    created = generate(template, dest, packs, ctx, force=force, dry_run=dry_run, yes=yes, init_git=git)

    if dry_run:
        console.print(f"[yellow]Dry run:[/] would create {len(created)} files")
    else:
        console.print(f"[green]Created {len(created)} files in[/] {dest}")

    if output == "tree":
        _print_tree(dest, created)
    else:
        for p in created:
            console.print(f"  - {p}")

@app.command("features")
def features() -> None:
    t = Table(title="Features")
    t.add_column("Name", style="bold")
    t.add_column("Description")
    for f in feature_registry():
        t.add_row(f.name, f.description)
    console.print(t)

@app.command("add")
def add_feature(
    feature: str = typer.Argument(..., help="Feature name"),
    dest: Path = typer.Argument(..., help="Project root"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files."),
) -> None:
    f = get_feature(feature)
    f.apply(dest.resolve(), force)
    console.print(f"[green]Applied feature:[/] {f.name}")

@app.command("doctor")
def doctor() -> None:
    """Check that common tooling exists for running templates."""
    tools = [
        ("git", ["git", "--version"]),
        ("python", [sys.executable, "--version"]),
        ("go", ["go", "version"]),
        ("cargo", ["cargo", "--version"]),
        ("rustc", ["rustc", "--version"]),
        ("node", ["node", "--version"]),
        ("npm", ["npm", "--version"]),
    ]
    t = Table(title="Forge Doctor")
    t.add_column("Tool", style="bold")
    t.add_column("Status")
    t.add_column("Details")
    for name, cmd in tools:
        if shutil.which(cmd[0]) is None and cmd[0] not in (sys.executable,):
            t.add_row(name, "[red]missing[/]", "")
            continue
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8").strip()
            t.add_row(name, "[green]ok[/]", out)
        except Exception as e:
            t.add_row(name, "[yellow]warn[/]", str(e))
    if PACKS_LOCK.exists():
        t.add_row("packs.lock", "[green]ok[/]", str(PACKS_LOCK))
    else:
        t.add_row("packs.lock", "[yellow]not created yet[/]", "Run: forge pack add ...")
    console.print(t)

@pack_app.command("list")
def pack_list() -> None:
    packs = list_packs(_builtin_root())
    t = Table(title="Packs")
    t.add_column("Name", style="bold")
    t.add_column("Kind")
    t.add_column("Path")
    t.add_column("Source")
    t.add_column("Commit")
    for p in packs:
        t.add_row(p.name, p.kind, str(p.path), str(p.source or ""), str(p.commit or ""))
    console.print(t)
    if PACKS_LOCK.exists():
        console.print(f"[dim]Lockfile:[/] {PACKS_LOCK}")

@pack_app.command("add")
def pack_add(
    source: str = typer.Argument(..., help="Local folder path or Git URL"),
    name: Optional[str] = typer.Option(None, "--name", help="Override pack name"),
) -> None:
    p = add_pack(source, name=name)
    msg = f"[green]Added pack:[/] {p.name} ({p.kind})"
    if p.commit:
        msg += f" @ {p.commit[:12]}"
    console.print(msg)

@pack_app.command("remove")
def pack_remove(name: str = typer.Argument(..., help="Pack name")) -> None:
    remove_pack(name)
    console.print(f"[green]Removed pack:[/] {name}")
