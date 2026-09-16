# Convenience targets. Run from this directory or via `make -C examples …`.

ROOT := $(abspath ..)
PY := python3

.PHONY: toy test alice macbeth compare term cosine extra help

help:
	@echo "make toy       - print the four-document worked example"
	@echo "make test      - toy arithmetic + helper smoke tests"
	@echo "make alice     - top 15 tf-idf terms in Alice"
	@echo "make macbeth   - top 15 tf-idf terms in Macbeth"
	@echo "make compare   - Alice vs Macbeth windows"
	@echo "make term T=whale - collection-wide report for T"
	@echo "make cosine    - pairwise cosine on output/tfidf"
	@echo "make extra     - add more-cats.txt and show the ranking shift"

toy:
	$(PY) run_toy_example.py

test:
	$(PY) test_toy_example.py
	$(PY) test_helpers.py

alice:
	$(PY) top_terms.py $(ROOT)/output/tfidf/carroll-alice.txt --n 15

macbeth:
	$(PY) top_terms.py $(ROOT)/output/tfidf/shakespeare-macbeth.txt --n 15

compare:
	$(PY) compare_documents.py \
		$(ROOT)/output/tfidf/carroll-alice.txt \
		$(ROOT)/output/tfidf/shakespeare-macbeth.txt --n 12

term:
	$(PY) term_report.py $(T)

cosine:
	$(PY) cosine_similarity.py --matrix --n 12

extra:
	$(PY) add_a_document.py
