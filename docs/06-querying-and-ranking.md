# Querying and ranking

Two small readers sit on top of the tab-separated tables. They do not
retokenize Gutenberg; they only look up weights that already exist.

## Rank the terms inside one book

```bash
python3 examples/rank_terms.py carroll-alice
python3 examples/rank_terms.py melville-moby_dick --top 10
python3 examples/rank_terms.py --top 5 --all
python3 examples/rank_terms.py --dir examples/tiny-output/tfidf
```

The first argument is a stem (`carroll-alice`) or a filename
(`carroll-alice.txt`). `--all` walks every table in the directory.

Expected Gutenberg heads (checked-in `output/tfidf/`):

```
== carroll-alice.txt ==
  1        0.025957  alice
  2        0.004547  gryphon
  3        0.004242  dormouse

== melville-moby_dick.txt ==
  1        0.004943  whale
  2        0.004322  ahab
  3        0.003258  sperm

== shakespeare-hamlet.txt ==
  1        0.014075  ham
  2        0.010224  haue
  3        0.006806  hor
```

If `ham` looking like a winner is surprising, read
[07-tokenization-and-quirks.md](07-tokenization-and-quirks.md). The ranker
is showing the tokenizer's vocabulary, not a modern-spelling index.

## Score a query against the shelf

```
score(d, q) = sum_{t in q} TF-IDF(t, d)
```

Missing terms contribute 0. Query words are lowercased but not otherwise
rewritten, so they must already be tokens (`gryphon`, not `Gryphon's`).

```bash
python3 examples/query_documents.py alice gryphon hatter
python3 examples/query_documents.py whale ahab pequod
python3 examples/query_documents.py emma knightley harriet
python3 examples/query_documents.py unto israel saith
python3 examples/query_documents.py hamlet horatio
python3 examples/query_documents.py macbeth banquo
```

On the checked-in tables those queries rank as:

| Query | First hit | Why |
| --- | --- | --- |
| `alice gryphon hatter` | `carroll-alice.txt` | all three weights live there; `gryphon`/`hatter` barely appear elsewhere |
| `whale ahab pequod` | `melville-moby_dick.txt` | `pequod` is unique; `ahab` is almost unique |
| `emma knightley harriet` | `austen-emma.txt` | Highbury names |
| `unto israel saith` | `bible-kjv.txt` | KJV function/content mix |
| `hamlet horatio` | `shakespeare-hamlet.txt` | even though `ham` (the speaker tag) is not in the query |
| `macbeth banquo` | `shakespeare-macbeth.txt` | `macbeth` has df = 1 |

A query of stopwords (`the and of`) scores 0 for every book because those
IDFs are 0. That is a useful sanity check: if a query of `the` suddenly
ranks something, the tables were rebuilt with a different `N` or a
smoothed IDF.

## Tiny-corpus queries

```bash
python3 examples/tiny_tfidf.py
python3 examples/query_documents.py --dir examples/tiny-output/tfidf tea rabbit
python3 examples/query_documents.py --dir examples/tiny-output/tfidf whale
python3 examples/query_documents.py --dir examples/tiny-output/tfidf bread tea
```

`whale` is unique, so that one-word query is a single-document answer.
`bread tea` still prefers `market-day.txt` because `bread` is heavier than
the shared `tea` weight in `tea-garden.txt`. The arithmetic is in
[03-worked-example.md](03-worked-example.md).

## What this ranking is not

It is not cosine similarity over a vector space, not BM25, and not a
phrase search. Order in the query does not matter; `whale ahab` and
`ahab whale` are the same sum. Repeated query terms are not weighted
extra — `query_documents.py` uses each string once in the order given,
and a duplicate would add the same document weight again.

For teaching, the dumb sum is enough: it makes the TF-IDF tables do
something you can see without introducing another formula.
