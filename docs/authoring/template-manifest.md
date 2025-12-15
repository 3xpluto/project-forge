# Template manifest (forge.json)

Each template folder contains a `forge.json`.

## Schema

- `schema_version`: must be `1`
- `vars`: object of variable specs
  - `prompt`: displayed label
  - `default`: optional default value
  - `regex`: optional validation regex
- `files`: list of files
  - `src`: path inside the template
  - `dst`: destination path (Jinja supported)
  - `mode`: `text` | `binary` | `auto`

## Example

```json
{
  "schema_version": 1,
  "vars": {
    "project_name": {"prompt": "Project name", "default": "my-app"}
  },
  "files": [
    {"src": "README.md.j2", "dst": "README.md.j2", "mode": "text"}
  ]
}
```
