from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Mapping

from .fs import ForgeError

def run_post_hooks(manifest: dict[str, Any], dest: Path, ctx: Mapping[str, Any], yes: bool) -> None:
    hooks = manifest.get("hooks", {})
    if not hooks:
        return
    post = hooks.get("post", [])
    if not post:
        return

    # Hooks are intentionally limited to explicit commands.
    # If not --yes, we require user confirmation per hook.
    for cmd in post:
        if not isinstance(cmd, list) or not cmd:
            raise ForgeError("Invalid hook command (expected list[str])")
        if not yes:
            ans = input(f"Run post-hook in {dest}: {' '.join(cmd)} ? [y/N]: ").strip().lower()
            if ans not in ("y", "yes"):
                continue
        try:
            subprocess.run(cmd, cwd=str(dest), check=True)
        except FileNotFoundError:
            raise ForgeError(f"Command not found: {cmd[0]}")
        except subprocess.CalledProcessError as e:
            raise ForgeError(f"Hook failed: {e}")
