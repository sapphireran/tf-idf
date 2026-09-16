# Python examples

Standard-library tools that reproduce this repository's `tf * idf` formulas. They are study code, not a replacement for the 2012 Perl snapshot.

## Layout

| File | Role |
| --- | --- |
| `tfidfkit/tokenize.py` | Line normalizer and bag-of-tokens |
| `tfidfkit/weights.py` | `tf`, `df`, `idf = ln(N / df)`, `tf * idf` |
| `tfidfkit/tables.py` | Readers / writers for the committed TSV layout |
| `tfidfkit/similarity.py` | Sparse dot product, cosine, query vectors |
| `run_pipeline.py` | Walk a directory and write `tf/`, `df.txt`, `idf.txt`, `tfidf/` |
| `rank_terms.py` | Sort one book (or every book) by weight |
| `similarity.py` | Pairwise cosine, or score a query |
| `inspect_committed.py` | Look up one token in the 2012 snapshot |

## Formulas

```
tf(t, d)      = count(t, d) / token_count(d)
idf(t)        = ln(N / df(t))
tfidf(t, d)   = tf(t, d) * idf(t)
cosine(a, b)  = dot(a, b) / (|a| |b|)
```

`N` is the number of documents the pipeline actually tokenized. That is the documented intent of the original tables, and it is not the same as Perl `$#files`. See `docs/05-quirks-and-design-choices.md`.

## Tiny corpus

```bash
python3 examples/python/run_pipeline.py \
  --input examples/tiny-corpus/docs \
  --output /tmp/tiny-tfidf

python3 examples/python/rank_terms.py \
  --tfidf-dir /tmp/tiny-tfidf/tfidf \
  --top 10
```

The expected tables are checked in under `examples/tiny-corpus/expected/` so you can diff a rerun.

## Gutenberg snapshot

Do not overwrite `output/`. Rank and compare the frozen tables in place:

```bash
python3 examples/python/rank_terms.py \
  --tfidf-dir output/tfidf \
  --output-root output \
  --document carroll-alice.txt \
  --top 15

python3 examples/python/similarity.py \
  --tfidf-dir output/tfidf \
  --top 12

python3 examples/python/similarity.py \
  --tfidf-dir output/tfidf \
  --idf output/idf.txt \
  --query "white whale ahab"

python3 examples/python/inspect_committed.py --token alice --summary
```

To recompute from `gutenberg/` into a scratch directory:

```bash
python3 examples/python/run_pipeline.py \
  --input gutenberg \
  --output /tmp/gutenberg-tfidf \
  --compat-empty-tokens
```

`--compat-empty-tokens` counts leading empty `split` fields in the TF denominator, matching `tf-idf-values.pl`. Omit it for the cleaner denominator used by the tiny-corpus walkthrough.

## Importing the library

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path("examples/python")))
from tfidfkit import run_pipeline, cosine

result = run_pipeline(Path("examples/tiny-corpus/docs"))
print(result.tfidf["cats.txt"]["mice"])
print(cosine(result.tfidf["cats.txt"], result.tfidf["dogs.txt"]))
```
