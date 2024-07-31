all:
	@echo "Read the Makefile; run only in the rel branch"

update:
	nn import-readinglist
	nn render-site -t docs
	git add -u
	git commit -m "release"
	git push --set-upstream origin $(git_current_branch)
