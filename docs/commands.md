# Commands

## Templates
- `forge list` — list templates from all packs
- `forge new <template> <dest>` — generate a project
  - `--var key=value` (repeat)
  - `--yes` non-interactive
  - `--dry-run` plan mode
  - `--force` overwrite existing files
  - `--git` initialize a git repo

## Packs
- `forge pack list`
- `forge pack add <path|git-url> [--name NAME]`
- `forge pack remove <name>`

## Features
- `forge features`
- `forge add <feature> <dest>`

## Doctor
- `forge doctor` — checks for git/python/go/rust/node and shows pack lockfile path.

## Output
- `forge new ... --output tree` — prints a tree of created files.


## Examples

```bash
forge new python-cli ./mytool --yes --var project_name=mytool --var package=mytool
forge add python-quality ./mytool
forge add release-python-pypi ./mytool
```
