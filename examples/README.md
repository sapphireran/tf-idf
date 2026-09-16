# Examples

Teaching copies of the TF-IDF pipeline from this personal toy repo.
Nothing here talks to a network or depends on CPAN modules.

## What to run

From the repository root:

```bash
# five original vignettes (kitchen, garden, harbor, workshop, stars)
python3 examples/tfidf_toy.py --corpus examples/tiny-corpus --top 8

# the three-sentence example from the hand-worked doc
python3 examples/tfidf_toy.py --corpus examples/classic-three-docs

# same tiny corpus, Perl, no Text::CSV_XS
perl examples/tiny_tfidf.pl examples/tiny-corpus

# tests for the Python toy
python3 tests/test_tfidf_toy.py
```

Write TSV tables in the same shape as the root `output/` folder:

```bash
python3 examples/tfidf_toy.py \
  --corpus examples/tiny-corpus \
  --write-dir /tmp/tiny-tfidf
```

`examples/tiny-output/` is a committed snapshot of those tables.

## Files

| Path | Role |
| --- | --- |
| `tfidf_toy.py` | Python tokenizer, TF, IDF, tf*idf, CLI |
| `tiny_tfidf.pl` | Perl clone that uses a real document count for N |
| `tiny-corpus/` | five short original texts |
| `classic-three-docs/` | `the cat sat on the mat` style example |
| `tiny-output/` | expected TSV dump of the five-document run |

The Gutenberg ranking helper lives at
`scripts/rank_precomputed_tfidf.py` because it reads the large
precomputed `output/tfidf/` tables rather than these tiny files.

## Design choices that match the 2012 scripts

- lowercase everything
- drop characters outside `[a-z0-9]` and whitespace
- use **normalized** term frequency (`count / document length`)
- use **natural log** IDF: `ln(N / df)`
- do **not** add smoothing, stopword lists, or stemming

## Design choices that fix the original scripts

- `N` is `len(documents)`, not `$#files` after `readdir`
- rankings print in score order, not alphabetical term order
- Perl example splits TSV on tabs instead of requiring `Text::CSV_XS`
