# Examples

Three layers, from arithmetic to the original dump.

## 1. Hand calculation

`hand-calculation/` has three one-line documents. Open
`hand-calculation/README.md` and recompute `mat` vs `the` before you
trust any larger run.

```bash
python3 -m tfidf report examples/hand-calculation/corpus --n 5
python3 -m tfidf query examples/hand-calculation/corpus "the mat"
```

## 2. Tiny corpus

`tiny-corpus/` has four short original notes (cat, bread, boat, planet).
This is the corpus the unit tests use for query ranking.

```bash
python3 -m tfidf report examples/tiny-corpus --n 8
python3 -m tfidf query examples/tiny-corpus "ganymede telescope opposition"
```

## 3. Gutenberg snapshot

`gutenberg-top-terms.md` is a frozen ranking of `output/tfidf/`. Rebuild
it after you change the renderer:

```bash
python3 -m tfidf top-tsv output/tfidf --n 12 > examples/gutenberg-top-terms.md
```

The novels themselves stay in `gutenberg/`. They are not duplicated here.
