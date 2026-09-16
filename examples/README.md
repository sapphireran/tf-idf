# Examples

Small collections and scripts that sit next to the 2012 Gutenberg dump
without replacing it.

## Corpora

| Directory | Size | Purpose |
| --- | --- | --- |
| [`tiny-corpus/`](tiny-corpus/) | 3 × 6 tokens | Hand-calculated fixture (`expected.json`) |
| [`themes-corpus/`](themes-corpus/) | 3 short paragraphs | Obvious winners: baker / stars / violin |

## Python (stdlib)

```bash
# Rank the teaching corpus
python3 examples/python/tfidf.py --input examples/tiny-corpus --top 6

# Rank the themed paragraphs and show cosine vs bakery.txt
python3 examples/python/tfidf.py --input examples/themes-corpus --top 8
python3 examples/python/tfidf.py --input examples/themes-corpus --similar bakery.txt

# sklearn-style idf (still no L2) on the same tiny files
python3 examples/python/tfidf.py --input examples/tiny-corpus --idf sklearn --top 6

# Rank the committed Gutenberg products; do not recompute
python3 examples/python/top_terms.py --from-output output/tfidf --top 10

# Rebuild a markdown report
python3 examples/python/top_terms.py \
  --from-output output/tfidf \
  --top 12 \
  --markdown examples/gutenberg-top-terms.md
```

`--output DIR` writes `tf/`, `df.txt`, `idf.txt`, and `tfidf/` in the
same tab-separated shape as the historical `output/` tree.

## Perl (cleaned)

```bash
perl examples/perl/compute_tf_idf.pl \
  --input examples/tiny-corpus \
  --output examples/_scratch/tiny-perl \
  --top 6
```

No `Text::CSV_XS`. `N` is the number of `.txt` files read.

## Historical pair

```bash
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

Those two overwrite `output/`. Prefer the example scripts unless you
are reproducing the 2012 run on purpose.
