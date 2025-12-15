from project_forge.features import registry

def test_registry_contains_new_features():
    names = [f.name for f in registry()]
    assert "python-quality" in names
    assert "release-python-pypi" in names
