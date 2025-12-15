from pathlib import Path

from project_forge.engine.fs import safe_join, ForgeError

def test_safe_join_blocks_traversal(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    try:
        safe_join(root, "../../etc/passwd")
        assert False, "expected ForgeError"
    except ForgeError:
        assert True

def test_safe_join_allows_normal_paths(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    p = safe_join(root, "a/b/c.txt")
    assert str(p).endswith("a/b/c.txt")
