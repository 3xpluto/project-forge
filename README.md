# Project Forge

[![CI](https://github.com/3xpluto/project-forge/actions/workflows/ci.yml/badge.svg)](https://github.com/3xpluto/project-forge/actions/workflows/ci.yml)
[![Template CI](https://github.com/3xpluto/project-forge/actions/workflows/template-ci.yml/badge.svg)](https://github.com/3xpluto/project-forge/actions/workflows/template-ci.yml)
[![Docs](https://github.com/3xpluto/project-forge/actions/workflows/docs.yml/badge.svg)](https://github.com/3xpluto/project-forge/actions/workflows/docs.yml)


**Project Forge** is a fast, extensible scaffolding CLI that generates **production-ready** projects (Python/Go/Rust/Node/etc.)
from **versioned templates** and optional **feature plugins** (CI, Docker, linting, releases, docs).

- ✅ Built-in templates + local packs + Git packs  
- ✅ Variables + prompts + `--yes` non-interactive mode  
- ✅ Safe writes (path traversal protection, overwrite rules)  
- ✅ Dry-run planning mode  
- ✅ Feature system (`forge add ci`, `forge add docker`)  

## Install

Recommended (isolated):

```bash
pipx install project-forge
```

Or:

```bash
pip install project-forge
```

## 60-second quickstart

```bash
forge list
forge new python-cli ./mytool --var project_name=mytool --var package=mytool --git
cd mytool
python -m venv .venv && source .venv/bin/activate
pip install -e .
mytool --help
```

Dry-run (shows what would be created):

```bash
forge new python-fastapi ./api --dry-run --yes --output tree
```

## Template packs

Add a local folder as a pack:

```bash
forge pack add ./my-templates
forge pack list
```

Add a Git pack (cloned into your local cache):

```bash
forge pack add https://github.com/yourname/forge-packs.git
```

## Features

List features:

```bash
forge features
```

Apply a feature to an existing repo:

```bash
forge add ci-github-actions ./mytool
forge add docker ./mytool
```

## Documentation

- See `docs/` (MkDocs).  
- To run docs locally:

```bash
pip install -r docs/requirements.txt
mkdocs serve
```

## Contributing

- Add templates under `src/project_forge/templates_builtin/<template-name>/`
- Each template needs a `forge.json` manifest.
- Keep templates minimal and composable; push “extras” into **features**.

## License

MIT (see `LICENSE`).


### New in v0.1.x
- More built-in templates: Rust + Node
- `forge doctor` for toolchain checks
- `forge new --output tree` to print a file tree
- Template CI workflow that generates and tests each template


## More features (built-in)

```bash
forge add python-quality ./mytool
forge add release-python-pypi ./mytool
```

> The release workflow uses PyPI Trusted Publishing (OIDC). Enable it on PyPI for your project.
