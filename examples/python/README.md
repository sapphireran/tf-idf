# Python reference

`tfidf_lab.py` is the library. The other files are thin command-line
front ends. There are no third-party dependencies.

## Library

```python
from tfidf_lab import build_index, load_documents

index = build_index(load_documents("../tiny_corpus/docs"))
print(index.scored["harbor-cats.txt"].top_terms(5))
print(index.cosine("sourdough-baking.txt", "kitchen-garden.txt"))
```

`build_index(..., variant="repo")` is the default and matches the
writeups in `docs/`. The other variants are documented in
`docs/07-algorithm-variants.md`.

## Commands

```bash
# every cell of cats / dogs / mats
python3 examples/python/worked_example.py

# score the tiny corpus and refresh expected/
python3 examples/python/run_tiny_corpus.py

# compare essays
python3 examples/python/compare_docs.py examples/tiny_corpus/docs

# rank a committed Gutenberg table
python3 examples/python/top_terms.py output/tfidf/melville-moby_dick.txt

# browse several Gutenberg tables
python3 examples/python/inspect_gutenberg.py --only blake-poems.txt shakespeare-hamlet.txt

# HTML report
python3 examples/python/make_report.py --include-worked
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The tests cover tokenization, the hand-calculated `mats` row, topical
rankings on the tiny corpus, and a reread of `expected/idf.txt`.
