# 06 — Ranking and cosine

A TF-IDF table is a document description. Ranking needs a second
description (the query) and a comparison rule.

## Query as a tiny document

I tokenize the query with the same tokenizer as the shelf. The query
has a TF (usually raw or length-normalized over a handful of tokens)
and it *reuses the shelf IDF*. That last part matters: the query does
not get its own collection statistics.

Default query weight in the lab:

\[
w(t, q) = \mathrm{tf}_{\mathrm{norm}}(t, q) \cdot \mathrm{idf}(t)
\]

with the same IDF flavor as the documents.

## Dot product

\[
\mathrm{score}(q, d) = \sum_{t \in q} w(t, q)\, w(t, d)
\]

Terms that are not in the query do not contribute. Terms that are in
the query but not in the document contribute nothing (the document
weight is zero). This is ordinary sparse multiplication.

Dot product still grows with the number of query terms that hit and
with the magnitude of the document vector. Long documents with many
distinct matching tokens tend to win.

## Cosine

\[
\cos(q, d) = \frac{q \cdot d}{\|q\|\,\|d\|}
\]

Division by the Euclidean norms removes pure magnitude. A short
children's story that is *about* rabbits can beat a long novel that
mentions a rabbit once.

Cosine is undefined if either vector is all zeros. The lab returns
score `0.0` and marks the document `empty_vector` rather than
dividing by zero. That happens when every query term has IDF 0 and
the flavor is `classic` — a stopword-only query against a shelf
where those stopwords are collection-wide.

## BM25 as a different comparison rule

BM25 is not "TF-IDF with cosine." It scores a query by summing, per
query term, an IDF times a saturated, length-normalized TF. There is
no query-side TF unless a term is repeated in the query, and there is
no cosine. I expose it as `--scheme bm25` on `rank` so I can see the
same query move.

## What I actually run

```bash
python3 -m tfidf rank "alice rabbit" --corpus gutenberg --scheme cosine
python3 -m tfidf rank "alice rabbit" --corpus gutenberg --scheme dot
python3 -m tfidf rank "alice rabbit" --corpus gutenberg --scheme bm25
```

Qualitative checks I care about are in
[08](08-gutenberg-lab-notes.md). Quantitative checks (hand-computed
cosines on the tiny corpus) are in `tests/test_rank.py`.
