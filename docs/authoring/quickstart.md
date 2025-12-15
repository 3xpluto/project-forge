# Template authoring quickstart

This guide walks you through creating a **new Project Forge template** in ~5 minutes.

## 1) Create a template folder

Templates live inside a pack. For built-in templates, add a folder under:

```
src/project_forge/templates_builtin/<template-name>/
```

Example:

```
src/project_forge/templates_builtin/python-fastapi-postgres/
```

## 2) Add a `forge.json` manifest

Every template needs a `forge.json` file.

Minimal example:

```json
{
  "schema_version": 1,
  "vars": {
    "project_name": {"prompt": "Project name", "default": "my-app", "regex": "[a-zA-Z0-9_-]{2,64}"}
  },
  "files": [
    {"src": "README.md.j2", "dst": "README.md.j2", "mode": "text"}
  ]
}
```

### Manifest fields

- `schema_version`: must be `1`
- `vars`: variables that can be used in file bodies and destination paths
  - `prompt`: label shown to the user
  - `default`: value used for `--yes` mode
  - `regex`: optional validation regex
- `files`: list of files to render
  - `src`: path relative to the template folder
  - `dst`: destination path (Jinja supported)
  - `mode`: `text` | `binary` | `auto`

## 3) Add template files (`.j2`)

Use **Jinja** in file bodies, and also in `dst` paths.

Example destination path:

```json
{"src":"src/app/__init__.py.j2", "dst":"src/{{ package }}/__init__.py.j2"}
```

Inside file content:

```python
print("project:", "{{ project_name }}")
```

## 4) Test your template locally

List templates:

```bash
forge list
```

Generate your template:

```bash
forge new <template-name> ./tmp --yes
```

Use `--output tree` to see what was created:

```bash
forge new <template-name> ./tmp --yes --output tree
```

## 5) Add a template to a custom pack

Any folder can be a pack if it contains templates:

```
my-pack/
  templates/
    my-template/
      forge.json
      ...
```

Then install the pack:

```bash
forge pack add ./my-pack
forge list
```

## Best practices

- Keep templates **small** and **composable**.
- Put optional tooling into **features** instead of duplicating across templates.
- Ensure every variable has a **default** so `--yes` works.
- Add a smoke test to the generated project when possible.
