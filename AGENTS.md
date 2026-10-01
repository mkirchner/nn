# Agent Guide

This repository contains `nn`, a small Python link collector and static-site renderer for **The Deep End**.

## Current repository model

The project is intentionally split into three parts:

1. **`main` branch: source and tooling only**
   - Python package source
   - Jinja templates
   - package metadata and lock file
   - publishing helper in `Makefile`
   - no generated website output
   - no tracked SQLite database

2. **`gh-pages` branch: generated website only**
   - rendered HTML and static assets at the branch root
   - published by GitHub Pages from `gh-pages` `/`
   - no Python package source
   - no SQLite database

3. **SQLite database: local/external runtime artifact**
   - selected with `NN_DB_URL`
   - commonly kept locally as `db/bookmarks.sqlite`
   - ignored by Git
   - used as input to rendering, not deployed with the site

There is no longer a `rel` branch in the normal workflow.

## What the project does

`nn` collects links from personal import sources, stores them in SQLite, and renders a static HTML website from the database.

Current sources and outputs:

- Safari Reading List import: `nn/srl.py`
- Pocket export import: `nn/pocket.py`
- Optional webpage title crawling/autocomplete: `nn/crawl.py`
- SQLite storage: `nn/db.py`
- Click CLI: `nn/cli.py`
- Jinja templates: `templates/`
- Rendered static site: `gh-pages` branch
- Local/production database: `NN_DB_URL`, often `sqlite:////absolute/path/to/db/bookmarks.sqlite`

## Repository map on `main`

- `nn/` — Python package source.
- `nn/cli.py` — CLI commands and the site rendering flow.
- `nn/db.py` — storage abstraction and SQLite implementation.
- `nn/srl.py` — reads Safari's `Bookmarks.plist` and extracts Reading List entries.
- `nn/pocket.py` — parses a Pocket HTML export.
- `nn/crawl.py` — fetches pages and extracts titles.
- `nn/events.py` — experimental event scraping support.
- `templates/` — Jinja templates.
- `templates/hnlike.html` — current index page template.
- `templates/hnlike_archive.html` — current archive page template.
- `templates/nn.html`, `templates/archive.html`, `templates/events.html` — older/alternate templates.
- `pyproject.toml` — Poetry package metadata and dependency constraints.
- `poetry.lock` — locked dependency versions.
- `Makefile` — publishing helper.
- `README.md` — minimal human-facing project description.
- `AGENTS.md` — this file.

Directories/files intentionally absent or ignored on `main`:

- `docs/` — generated website output; belongs on `gh-pages`, not `main`.
- `db/*.sqlite` — local SQLite databases; runtime/content artifacts, not source files.
- Python caches and virtualenvs.

## Setup

This project is configured for Poetry. If Poetry is installed directly:

```sh
poetry install
poetry run nn --help
```

If Poetry is not installed, `uvx` can run the pinned Poetry workflow without a global Poetry install:

```sh
uvx --from poetry==1.8.3 poetry install
uvx --from poetry==1.8.3 poetry run nn --help
```

This checkout may also have a local `.venv`; in that case the CLI can be invoked as:

```sh
.venv/bin/nn --help
```

## Database usage and safety

Most commands accept `--db-url` or read `NN_DB_URL` from the environment. Always choose the intended database explicitly.

Scratch/development example:

```sh
export NN_DB_URL=sqlite:////tmp/nn-dev.sqlite
.venv/bin/nn import-pocket --source /path/to/pocket-export.html
.venv/bin/nn render-site -t /tmp/nn-site
```

Production/local example:

```sh
export NN_DB_URL=sqlite:////absolute/path/to/db/bookmarks.sqlite
```

Important safety rules for agents:

- Do **not** commit SQLite databases.
- Do **not** commit generated website output to `main`.
- Do **not** create or restore a `rel` publishing workflow.
- Do **not** run `make page-update` unless explicitly requested by the user.
- Do **not** assume Safari data exists or is accessible in non-interactive environments.
- Prefer scratch databases and temporary render directories for experiments.

## Common commands

List CLI commands:

```sh
.venv/bin/nn --help
```

or:

```sh
uvx --from poetry==1.8.3 poetry run nn --help
```

Import Safari Reading List into the selected database:

```sh
NN_DB_URL=sqlite:////tmp/nn-dev.sqlite .venv/bin/nn import-readinglist
```

Import a Pocket export:

```sh
NN_DB_URL=sqlite:////tmp/nn-dev.sqlite .venv/bin/nn import-pocket --source /path/to/export.html
```

Render the site to a temporary directory:

```sh
NN_DB_URL=sqlite:////tmp/nn-dev.sqlite .venv/bin/nn render-site -t /tmp/nn-site
```

List recent entries:

```sh
NN_DB_URL=sqlite:////tmp/nn-dev.sqlite .venv/bin/nn list-recent --limit 20
```

## Publishing to GitHub Pages

Publishing is done from `main` with:

```sh
export NN_DB_URL=sqlite:////absolute/path/to/db/bookmarks.sqlite
make page-update
```

`make page-update` does the following:

1. Requires `NN_DB_URL` to be set.
2. Fetches `origin/gh-pages`.
3. Creates or resets a sibling worktree at `../nn-gh-pages` for the `gh-pages` branch.
4. Runs `nn import-readinglist` against `NN_DB_URL`.
5. Runs `nn render-site -t ../nn-gh-pages`.
6. Commits changed generated files on `gh-pages` with message `release` if there are changes.
7. Pushes `gh-pages`.
8. Removes the temporary worktree.

The target is configurable:

```sh
PAGE_BRANCH=gh-pages PAGE_WORKTREE=/tmp/nn-gh-pages make page-update
```

GitHub Pages is configured to publish from:

```text
gh-pages /
```

## Rendering notes

- The current renderer is `render_site()` in `nn/cli.py`.
- Index output uses `templates/hnlike.html`.
- Archive output uses `templates/hnlike_archive.html`.
- The index template receives `rendered_at`, a UTC timestamp formatted as `YYYY-MM-DD HH:MM:SS UTC`, and displays it below the pink footer bar.
- Archive years are currently hard-coded in `nn/cli.py`.
- Rendering currently writes `index.html` plus one archive file per configured year.

## Verification

There is no formal test suite yet. Useful lightweight checks:

```sh
python -m compileall -q nn
.venv/bin/nn --help
uvx --from poetry==1.8.3 poetry check --lock
```

For rendering changes, if the user has not asked for production publishing, render to a temporary directory with a scratch database and inspect the generated HTML.

For importer changes, prefer small fixture files or scratch copies of real exports. Do not depend on the user's live Safari profile unless the task specifically asks for it.

## Dependency maintenance

Dependencies are managed with Poetry:

- constraints: `pyproject.toml`
- lock file: `poetry.lock`

Use Poetry 1.8.3 for lock-file updates to preserve the existing lock format:

```sh
uvx --from poetry==1.8.3 poetry update <package> --lock
uvx --from poetry==1.8.3 poetry check --lock
```

## Extension guidance

When adding functionality:

- Add new CLI commands in `nn/cli.py` using Click.
- Keep storage changes in `nn/db.py` and preserve the existing `create_store(url)` factory pattern unless intentionally redesigning storage.
- Prefer adding importer-specific code to a separate module, similar to `srl.py` and `pocket.py`.
- Keep rendering data preparation in `nn/cli.py` unless it grows enough to justify extraction.
- Update this file when setup, commands, branch structure, deployment, or safety assumptions change.

Known rough edges agents should be aware of:

- The project currently has minimal human-facing documentation and no automated tests.
- Some code paths are personal-workflow-specific, especially Safari Reading List import and `make page-update`.
- `events.py` appears experimental and requires external credentials for Eventbrite-related behavior.
- Generated site years are currently hard-coded in `nn/cli.py`.
