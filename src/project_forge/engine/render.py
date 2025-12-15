from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from jinja2 import Environment, StrictUndefined

from .fs import ForgeError, WriteOp, safe_join

@dataclass(frozen=True)
class Template:
    name: str
    root: Path
    manifest: dict[str, Any]

def load_manifest(template_root: Path) -> dict[str, Any]:
    mpath = template_root / "forge.json"
    if not mpath.exists():
        raise ForgeError(f"Missing forge.json in template: {template_root}")
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ForgeError("Unsupported schema_version (expected 1)")
    if "files" not in manifest or not isinstance(manifest["files"], list):
        raise ForgeError("Manifest must include a 'files' list")
    if "vars" in manifest and not isinstance(manifest["vars"], dict):
        raise ForgeError("'vars' must be an object")
    return manifest

def env() -> Environment:
    # StrictUndefined catches missing vars (professional UX)
    return Environment(undefined=StrictUndefined, autoescape=False, keep_trailing_newline=True)

def render_plan(tpl: Template, dest: Path, ctx: Mapping[str, Any]) -> list[WriteOp]:
    e = env()
    ops: list[WriteOp] = []

    for item in tpl.manifest["files"]:
        src = str(item["src"])
        dst_tmpl = str(item.get("dst", src))
        mode = str(item.get("mode", "text"))  # text | binary | auto

        # destination path can use jinja
        dst_rel = e.from_string(dst_tmpl).render(**ctx)
        if dst_rel.endswith(".j2"):
            dst_rel = dst_rel[:-3]

        dst_path = safe_join(dest, dst_rel)
        src_path = tpl.root / src
        if not src_path.exists():
            raise ForgeError(f"Missing template file: {src_path}")

        raw = src_path.read_bytes()

        if mode == "binary":
            ops.append(WriteOp(dst=dst_path, bytes_data=raw, is_binary=True))
            continue

        if mode == "auto":
            # simple heuristic: if it decodes, treat as text, else binary
            try:
                raw.decode("utf-8")
                mode = "text"
            except UnicodeDecodeError:
                mode = "binary"

        if mode == "binary":
            ops.append(WriteOp(dst=dst_path, bytes_data=raw, is_binary=True))
            continue

        text = raw.decode("utf-8")
        out = e.from_string(text).render(**ctx)
        ops.append(WriteOp(dst=dst_path, text_data=out, is_binary=False))

    return ops

def apply_plan(ops: list[WriteOp], force: bool) -> None:
    for op in ops:
        op.dst.parent.mkdir(parents=True, exist_ok=True)
        if op.dst.exists() and not force:
            raise ForgeError(f"File exists: {op.dst} (use --force)")
        if op.is_binary:
            assert op.bytes_data is not None
            op.dst.write_bytes(op.bytes_data)
        else:
            assert op.text_data is not None
            op.dst.write_text(op.text_data, encoding="utf-8")
