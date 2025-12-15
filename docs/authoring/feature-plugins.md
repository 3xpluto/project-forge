# Feature plugins

Features are small code modules that can be applied after generation.

## Example

- `ci-github-actions`: adds a `.github/workflows/ci.yml`
- `docker`: adds a minimal `Dockerfile`

## Add a feature

Create `src/project_forge/features/<name>.py` and register it in `features/__init__.py`.
