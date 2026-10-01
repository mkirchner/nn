.PHONY: all page-update

all:
	@echo "Read the Makefile; run page-update only when you intend to publish the site"

page-update:
	@test -n "$$NN_DB_URL" || (echo "Set NN_DB_URL to the production SQLite database URL before publishing" >&2; exit 1)
	nn import-readinglist
	nn render-site -t docs
	git add docs
	git commit -m "release"
	git push --set-upstream origin $$(git branch --show-current)
