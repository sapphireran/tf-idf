# Personal lab shortcuts. Run from the repository root.

PYTHON ?= python3

.PHONY: test demo rank-smoke help

help:
	@echo "make test        — unit tests"
	@echo "make demo        — tiny-corpus worked tables"
	@echo "make rank-smoke  — three Gutenberg sanity queries"

test:
	$(PYTHON) -m unittest discover -s tests -v

demo:
	$(PYTHON) -m tfidf demo

rank-smoke:
	$(PYTHON) -m tfidf rank "white whale ahab" --corpus gutenberg -k 5
	$(PYTHON) -m tfidf rank "alice rabbit queen" --corpus gutenberg -k 5
	$(PYTHON) -m tfidf rank "macbeth witches thane" --corpus gutenberg -k 5
