PYTHON ?= python3

.PHONY: test report-hand report-tiny gutenberg-top help

help:
	@echo "make test            run unit tests"
	@echo "make report-hand     markdown report for the 3-line corpus"
	@echo "make report-tiny     markdown report for the 4-note corpus"
	@echo "make gutenberg-top   rank the committed output/tfidf tables"

test:
	$(PYTHON) -m unittest discover -s tests -v

report-hand:
	$(PYTHON) -m tfidf report examples/hand-calculation/corpus --n 5

report-tiny:
	$(PYTHON) -m tfidf report examples/tiny-corpus --n 8 --query "ganymede telescope opposition"

gutenberg-top:
	$(PYTHON) -m tfidf top-tsv output/tfidf --n 12
