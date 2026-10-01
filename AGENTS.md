# Agent Guide

This repository contains `nn`, a small Python link collector and static-site renderer.

## What the project does

`nn` collects links from personal export/import sources, stores them in SQLite, and renders a static HTML website from the database.

Current sources and outputs:

- Safari Reading List import: `nn/srl.py`
- Pocket export import: `nn/pocket.py`
- Optional webpage title crawling/autocomplete: `nn/crawl.py`
- SQLite storage: `nn/db.py`
- Click CLI: `nn/cli.py`
- Jinja templates: `templates/`
- Rendered static site: published from the separate `gh-pages` branch.
- Local/production SQLite databases: usually under `db/` or pointed to by `NN_DB_URL`; these should not be source-controlled.

## Repository map

- `nn/` — Python package source.
- `nn/cli.py` — CLI command definitions and rendering flow.
- `nn/db.py` — database abstraction and SQLite implementation.
- `nn/srl.py` — reads Safari's `Bookmarks.plist` and extracts Reading List entries.
- `nn/pocket.py` — parses a Pocket HTML export.
- `nn/crawl.py` — fetches pages and extracts titles.
- `nn/events.py` — experimental event scraping support.
- `templates/` — Jinja templates used by `render-site`.
- `db/` — local SQLite databases. These are runtime/content artifacts, not source files.
- `pyproject.toml` — Poetry package metadata and dependencies.
- `Makefile` — page publishing helper; read it before running any target.

The `main` branch is for source and tooling. Generated website files do not belong on `main`; they are committed to `gh-pages` by `make page-update`.

## Setup

This project is configured for Poetry:

```sh
poetry install
poetry run nn --help
```

If Poetry is not available, use an isolated virtual environment and install the package with an equivalent PEP 517/pip workflow.

The CLI entry point is:

```sh
nn --help
```

or, when using Poetry:

```sh
poetry run nn --help
```

## Database safety

Most commands accept `--db-url` or read `NN_DB_URL` from the environment. Use this to choose a scratch, local, or production database explicitly:

```sh
export NN_DB_URL=sqlite:////tmp/nn-dev.sqlite
poetry run nn import-pocket --source /path/to/pocket-export.html
poetry run nn render-site -t /tmp/nn-site
```

Important safety rules for agents:

- Do **not** commit SQLite databases. Use `NN_DB_URL` to point at the intended local, scratch, or production database.
- Prefer a scratch database such as `sqlite:////tmp/nn-dev.sqlite` for experiments.
- Do **not** commit generated site output to `main`.
- Do **not** run `make page-update` unless explicitly requested. It requires `NN_DB_URL`, imports the local Safari Reading List into that database, renders into a `gh-pages` worktree, commits the rendered site there, and pushes `gh-pages`.
- Do **not** assume Safari data exists or is accessible in non-interactive environments.

## Common tasks

List available CLI commands:

```sh
poetry run nn --help
```

Import Safari Reading List into the selected database:

```sh
NN_DB_URL=sqlite:////tmp/nn-dev.sqlite poetry run nn import-readinglist
```

Import Pocket export:

```sh
NN_DB_URL=sqlite:////tmp/nn-dev.sqlite poetry run nn import-pocket --source /path/to/export.html
```

Render the site to a target directory:

```sh
NN_DB_URL=sqlite:////tmp/nn-dev.sqlite poetry run nn render-site -t /tmp/nn-site
```

Publish the site to GitHub Pages when explicitly requested:

```sh
NN_DB_URL=sqlite:////absolute/path/to/bookmarks.sqlite make page-update
```

List recent entries:

```sh
NN_DB_URL=sqlite:////tmp/nn-dev.sqlite poetry run nn list-recent --limit 20
```

## Verification

There is no formal test suite yet. Useful lightweight checks:

```sh
python -m compileall -q nn
poetry run nn --help
```

For changes to rendering, use a scratch database and render to a temporary directory, then inspect the generated HTML.

For changes to importers, prefer small fixture files or scratch copies of real exports. Do not depend on the user's live Safari profile unless the task specifically asks for it.

## Extension guidance

When adding functionality:

- Add new CLI commands in `nn/cli.py` using Click.
- Keep storage changes in `nn/db.py` and preserve the existing `create_store(url)` factory pattern unless intentionally redesigning storage.
- Prefer adding importer-specific code to a separate module, similar to `srl.py` and `pocket.py`.
- Keep rendering data preparation in `nn/cli.py` unless it grows enough to justify extraction.
- Update this file when setup, commands, or safety assumptions change.

Known rough edges agents should be aware of:

- The project currently has minimal documentation and no automated tests.
- Some code paths are personal-workflow-specific, especially Safari Reading List import and `make page-update`.
- `events.py` appears experimental and requires external credentials for Eventbrite-related behavior.
- Generated site years are currently hard-coded in `nn/cli.py`.
