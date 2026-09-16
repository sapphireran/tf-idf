# CLI cookbook

All commands assume the repository root and Python 3. The package is
pure stdlib; there is nothing to `pip install`.

```bash
python3 -m tfidf --help
```

## Tiny examples (fast, tested)

```bash
# full markdown report
python3 -m tfidf report examples/hand-calculation/corpus --n 5
python3 -m tfidf report examples/tiny-corpus --n 8

# keyword list only
python3 -m tfidf top examples/tiny-corpus --n 8

# search-style ranking
python3 -m tfidf query examples/tiny-corpus "ganymede telescope"
python3 -m tfidf query examples/tiny-corpus "jib barnacles mooring"

# pairwise cosine
python3 -m tfidf similar examples/tiny-corpus

# write TSV like the 2012 layout
python3 -m tfidf compute examples/tiny-corpus -o /tmp/tiny-tfidf
```

Add a query to the report:

```bash
python3 -m tfidf report examples/tiny-corpus --n 5 \
  --query "levain dutch oven"
```

## Compare raw vs smoothed IDF

```bash
python3 -m tfidf top examples/hand-calculation/corpus --idf raw --n 5
python3 -m tfidf top examples/hand-calculation/corpus --idf smooth --n 5
```

## Read the committed Gutenberg snapshot

```bash
python3 -m tfidf top-tsv output/tfidf --n 10
```

This does **not** re-tokenize the novels. It only sorts the existing
numbers.

## Recompute on Gutenberg (slow)

```bash
python3 -m tfidf compute gutenberg -o /tmp/gutenberg-tfidf
python3 -m tfidf query gutenberg "whale boat nantucket"
python3 -m tfidf similar gutenberg
```

`similar` on 18 long files builds 18-choose-2 = 153 cosines. That is
fine. The expensive part is the first tokenization of `bible-kjv.txt`.

## Only ``*.txt`` by default

`examples/tiny-corpus/` and `examples/hand-calculation/` keep a README
beside the documents. The CLI only reads `*.txt` unless you pass
another glob:

```bash
python3 -m tfidf report examples/tiny-corpus --glob '*'
```

## Perl-compat denominator

```bash
python3 -m tfidf report examples/hand-calculation/corpus --perl-compat
```

The three-line corpus has no leading spaces, so the flag changes
nothing there. It matters on indented verse.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Or `make test`.
