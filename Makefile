.PHONY: all page-update

PAGE_BRANCH ?= gh-pages
PAGE_WORKTREE ?= ../nn-gh-pages

all:
	@echo "Read the Makefile; run page-update only when you intend to publish the site"

page-update:
	@test -n "$$NN_DB_URL" || (echo "Set NN_DB_URL to the production SQLite database URL before publishing" >&2; exit 1)
	@set -e; \
	new_count="$$(nn import-readinglist)"; \
	case "$$new_count" in \
		''|*[!0-9]*) echo "Unexpected import-readinglist output: $$new_count" >&2; exit 1 ;; \
	esac; \
	echo "Imported $$new_count new Reading List item(s)"; \
	if [ "$$new_count" -eq 0 ]; then \
		echo "No new Reading List items; skipping render/publish"; \
		exit 0; \
	fi; \
	git fetch origin $(PAGE_BRANCH); \
	git worktree add -B $(PAGE_BRANCH) "$(PAGE_WORKTREE)" origin/$(PAGE_BRANCH); \
	cleanup() { git worktree remove "$(PAGE_WORKTREE)" >/dev/null 2>&1 || true; }; \
	trap cleanup EXIT; \
	nn render-site -t "$(PAGE_WORKTREE)"; \
	(cd "$(PAGE_WORKTREE)" && git add . && (git diff --cached --quiet || git commit -m "release") && git push origin $(PAGE_BRANCH))
