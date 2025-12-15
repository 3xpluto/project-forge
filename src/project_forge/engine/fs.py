from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

class ForgeError(RuntimeError):
    pass

def safe_join(root: Path, rel: str) -> Path:
    rel_path = Path(rel)
    if rel_path.is_absolute():
        raise ForgeError(f"Refusing absolute path: {rel}")
    combined = (root / rel_path).resolve()
    if combined != root and root not in combined.parents:
        raise ForgeError(f"Refusing path traversal: {rel}")
    return combined

@dataclass(frozen=True)
class WriteOp:
    dst: Path
    bytes_data: bytes | None = None
    text_data: str | None = None
    is_binary: bool = False

    def describe(self) -> str:
        return str(self.dst)
