# 09 — Limits and next steps

## What this notebook is allowed to claim

- I can compute several classical term weights on a shelf I can read.
- I can show, with arithmetic, how \(N\), \(n_t\), and `|d|` move a
  score.
- I can rank a short query against eighteen books and say whether the
  winner is *plausible*.

## What it is not allowed to claim

- That TF-IDF (or BM25 with default \(k_1, b\)) is the right ranker
  for any application.
- That these tokenizers understand English.
- That a cosine on 18 documents predicts behavior on a web-scale
  index.
- That anything here is related to workplace search, logs, or
  customer data. It is not.

## Known holes I am leaving open

- No stemming, no lemmatization. `whale` and `whales` are neighbors
  only if I type both.
- No relevance judgments, so no MAP, nDCG, or residual collection
  evaluation. Sanity checks are qualitative.
- No phrase index. `white whale` is two terms, not a collocation.
- No handling of Gutenberg boilerplate beyond "it tokenizes like
  everything else."
- BM25 parameters are defaults from textbooks, not fits.
- The Perl scripts remain the 2012 text. Disagreements are documented
  rather than patched upstream.

## Next personal experiments (only if I come back)

1. Add a third tokenizer that keeps internal apostrophes and split
   out a true side-by-side table against `output/tf/`.
2. Hand-label twenty queries on this shelf and compute a toy nDCG so
   "plausible" becomes a number.
3. Read the BM25 survey chapter and re-derive the TF saturation curve
   with three values of \(k_1\) on *Moby-Dick* vs Blake.
4. Try character n-grams on the Shakespeare files to see whether
   speech prefixes stop polluting the term space.

None of those require a larger corpus. They require more patience
with this one.
