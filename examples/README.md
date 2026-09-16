# Examples

Personal, self-contained companions to the 2012 Gutenberg `tf * idf` toy. Nothing here is a library and nothing talks to a search service.

| Path | What you do with it |
| --- | --- |
| [`tiny-corpus/`](tiny-corpus/) | Four nine-token notes plus a pencil-and-paper walkthrough of every weight |
| [`gutenberg-similarity.md`](gutenberg-similarity.md) | Measured cosines and top-10 overlap vs the committed tables |
| [`python/tfidf_toy.py`](python/tfidf_toy.py) | Recompute `tf` / `df` / `idf` / `tf * idf` with \(N=\) number of files actually read |
| [`python/rank_terms.py`](python/rank_terms.py) | Sort a table (committed or freshly written) by weight |
| [`python/similar_docs.py`](python/similar_docs.py) | Cosine similarity on those weights |
| [`python/compare_rankings.py`](python/compare_rankings.py) | Top-N overlap vs the committed `output/tfidf/` tables |
| [`python/tests/`](python/tests/) | Exact checks of the tiny corpus and the tokenizer |

## Fast path

```bash
# 1. score the four notes
python3 examples/python/tfidf_toy.py examples/tiny-corpus/documents \
    --write-dir examples/tiny-corpus/output

# 2. rank one note
python3 examples/python/rank_terms.py \
    --from-table examples/tiny-corpus/output/tfidf/01-bakery-morning.txt

# 3. compare all four
python3 examples/python/similar_docs.py \
    --table-dir examples/tiny-corpus/output/tfidf

# 4. rank a committed Gutenberg table (no recompute)
python3 examples/python/rank_terms.py \
    --from-table output/tfidf/carroll-alice.txt --top 15
```

## Tests

```bash
python3 -m unittest discover -s examples/python/tests -v
```

Stdlib only. There is no `requirements.txt` on purpose.
