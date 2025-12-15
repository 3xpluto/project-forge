from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .fs import ForgeError

APP_DIR = Path(os.environ.get("PROJECT_FORGE_HOME", Path.home() / ".project-forge"))
PACKS_FILE = APP_DIR / "packs.json"
PACKS_LOCK = APP_DIR / "packs.lock.json"
CACHE_DIR = APP_DIR / "cache"

@dataclass(frozen=True)
class Pack:
    name: str
    kind: str  # "builtin" | "local" | "git"
    path: Path
    source: str | None = None
    commit: str | None = None

def _load_state() -> dict:
    if not PACKS_FILE.exists():
        return {"packs": []}
    return json.loads(PACKS_FILE.read_text(encoding="utf-8"))

def _save_state(state: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    PACKS_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    _write_lock(state)

def _write_lock(state: dict) -> None:
    # A reproducibility-friendly view of packs, including resolved git commit hashes.
    lock = {"packs": []}
    for p in state.get("packs", []):
        lock["packs"].append(
            {
                "name": p.get("name"),
                "kind": p.get("kind"),
                "source": p.get("source"),
                "path": p.get("path"),
                "commit": p.get("commit"),
            }
        )
    APP_DIR.mkdir(parents=True, exist_ok=True)
    PACKS_LOCK.write_text(json.dumps(lock, indent=2), encoding="utf-8")

def list_packs(builtin_root: Path) -> list[Pack]:
    state = _load_state()
    packs = [Pack(name="builtin", kind="builtin", path=builtin_root)]
    for p in state.get("packs", []):
        packs.append(
            Pack(
                name=p["name"],
                kind=p["kind"],
                path=Path(p["path"]),
                source=p.get("source"),
                commit=p.get("commit"),
            )
        )
    return packs

def add_pack(source: str, name: str | None = None) -> Pack:
    state = _load_state()
    APP_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Local folder?
    src_path = Path(source).expanduser()
    if src_path.exists() and src_path.is_dir():
        pack_name = name or src_path.name
        entry = {"name": pack_name, "kind": "local", "path": str(src_path.resolve())}
        _upsert(state, entry)
        _save_state(state)
        return Pack(pack_name, "local", Path(entry["path"]))

    # Otherwise treat as git url
    pack_name = name or _slug(source)
    dest = CACHE_DIR / f"gitpack-{pack_name}"
    if dest.exists():
        shutil.rmtree(dest)

    try:
        subprocess.run(["git", "clone", "--depth", "1", source, str(dest)], check=True)
    except FileNotFoundError:
        raise ForgeError("git not found on PATH (install git or only use local packs)")
    except subprocess.CalledProcessError as e:
        raise ForgeError(f"git clone failed: {e}")

    commit = None
    try:
        commit = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(dest))
            .decode("utf-8")
            .strip()
        )
    except Exception:
        commit = None

    entry = {
        "name": pack_name,
        "kind": "git",
        "path": str(dest.resolve()),
        "source": source,
        "commit": commit,
    }
    _upsert(state, entry)
    _save_state(state)
    return Pack(pack_name, "git", dest.resolve(), source=source, commit=commit)

def remove_pack(name: str) -> None:
    state = _load_state()
    packs = state.get("packs", [])
    new = [p for p in packs if p.get("name") != name]
    if len(new) == len(packs):
        raise ForgeError(f"No pack named '{name}'")
    state["packs"] = new
    _save_state(state)

def _upsert(state: dict, entry: dict) -> None:
    packs = state.setdefault("packs", [])
    for i, p in enumerate(packs):
        if p.get("name") == entry["name"]:
            packs[i] = entry
            return
    packs.append(entry)

def _slug(s: str) -> str:
    out = []
    for ch in s:
        out.append(ch.lower() if ch.isalnum() else "-")
    slug = "".join(out).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:40] or "pack"

def iter_template_dirs(packs: Iterable[Pack]) -> Iterable[Path]:
    for p in packs:
        # convention: templates live in <pack>/templates OR directly in <pack>
        t1 = p.path / "templates"
        if t1.exists() and t1.is_dir():
            yield t1
        yield p.path
