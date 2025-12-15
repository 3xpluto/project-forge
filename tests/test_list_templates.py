from pathlib import Path

from project_forge.engine.packs import list_packs
from project_forge.engine.plan import find_templates

def test_find_builtin_templates():
    builtin = Path(__file__).resolve().parents[1] / "src/project_forge/templates_builtin"
    packs = list_packs(builtin)
    items = find_templates(packs)
    names = [t.name for t in items]
    assert "python-cli" in names
    assert "python-fastapi" in names
    assert "python-fastapi-postgres" in names
    assert "go-api" in names
    assert "go-chi-api" in names
    assert "rust-cli" in names
    assert "rust-axum-api" in names
    assert "node-ts-cli" in names
    assert "node-express-api" in names
