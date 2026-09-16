# Reproducing the numbers

There are three layers of results in this checkout. They are meant to
be reproduced independently.

## 1. Classroom example (fast, exact)

```bash
python3 examples/python/worked_example.py
python3 -m unittest discover -s tests -v
```

The worked example is computed from string literals inside
`tfidf_lab.py`. The tests check the `mats` row against `0.25 * ln(3)`
and check that the tiny corpus still prefers the obvious topical
words.

## 2. Tiny original corpus (fast, committed)

```bash
python3 examples/python/run_tiny_corpus.py
python3 examples/python/compare_docs.py examples/tiny_corpus/docs
python3 examples/python/make_report.py --include-worked
```

This writes TSV tables and `summary.txt` under
`examples/tiny_corpus/expected/` and an HTML report next to them.
Those files are part of the personal example, not a build artifact you
have to hide. If you edit a document, rerun the three commands and
commit the new tables.

## 3. Gutenberg tables (historical, optional)

The committed `output/` directory is the original 2012 toy result.
Reading it does not require Perl:

```bash
python3 examples/python/inspect_gutenberg.py -n 8
python3 examples/python/top_terms.py output/tfidf/carroll-alice.txt
```

Regenerating it does:

1. Install `Text::CSV_XS` for the product script.
2. Confirm `gutenberg/` contains the eighteen books and that you want
   `N` to be 18, not `$#files`.
3. Run `perl tf-idf-values.pl`.
4. Run `perl tf*idf-product.pl`.

Expect the TF files to be close and the IDF files to differ if `N` is
not 18. See [formulas](03-formulas.md) for the `$#files` pitfall.

## What "matching" means

Floating-point text dumps should be compared with a tolerance, not
string equality. The unit test that rereads
`examples/tiny_corpus/expected/idf.txt` uses `rel_tol=1e-9`. The
Gutenberg dumps use Perl's default numeric formatting; a Python
rewrite will not byte-match those files even when the math agrees.

## Files you should not treat as input

| path | role |
| --- | --- |
| `output/df-sorted.txt` | browse-only DF dump |
| `gutenberg/.DS_Store` | leftover; skipped by name |
| `output/.DS_Store` | leftover; skipped by name |

The only inputs the Python tiny-corpus path needs are the five files
in `examples/tiny_corpus/docs/`.
