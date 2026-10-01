.PHONY: all page-update

PAGE_BRANCH ?= gh-pages
PAGE_WORKTREE ?= ../nn-gh-pages

all:
	@echo "Read the Makefile; run page-update only when you intend to publish the site"

page-update:
	@test -n "$$NN_DB_URL" || (echo "Set NN_DB_URL to the production SQLite database URL before publishing" >&2; exit 1)
	git fetch origin $(PAGE_BRANCH)
	git worktree add -B $(PAGE_BRANCH) $(PAGE_WORKTREE) origin/$(PAGE_BRANCH)
	nn import-readinglist
	nn render-site -t $(PAGE_WORKTREE)
	cd $(PAGE_WORKTREE) && git add . && (git diff --cached --quiet || git commit -m "release")
	cd $(PAGE_WORKTREE) && git push origin $(PAGE_BRANCH)
	git worktree remove $(PAGE_WORKTREE)
