# Examples

Worked readings of this repo's TF-IDF definition. Nothing here talks to a
network or a company codebase; the only inputs are the tiny documents in
`tiny-corpus/docs/` and the checked-in Gutenberg `output/` tables.

## Start here

1. [`hand-calculation.md`](hand-calculation.md) — every TF / DF / IDF / TF-IDF
   number for a 4-document, ~80-token corpus, done on paper-friendly arithmetic.
2. [`tiny-corpus/`](tiny-corpus/) — the four source texts, a Python scorer that
   matches the Perl formulas, and a `--verify` check against those numbers.
3. [`reproducing-a-gutenberg-score.md`](reproducing-a-gutenberg-score.md) —
   multiply `output/tf` × `output/idf` and match `output/tfidf` for `emma`,
   `harriet`, `the`, and `whale`.
4. [`gutenberg-top-terms.md`](gutenberg-top-terms.md) — top-12 lists from
   `output/tfidf/` with a short note on each book.
5. [`compare-austen-novels.md`](compare-austen-novels.md) — same author, three
   novels: names dominate, shared honorifics linger, `anne` is diluted.
6. [`shakespeare-speaker-tags.md`](shakespeare-speaker-tags.md) — why `macb`,
   `ham`, and `bru` beat the character names.

## Commands

```bash
# rebuild the tiny tables and check the hand-calculation anchors
python3 examples/tiny-corpus/compute_tfidf.py --verify

# reprint Gutenberg rankings from the committed TSV files
python3 examples/rank_top_terms.py --dir output/tfidf --k 12

# one file only
python3 examples/rank_top_terms.py --dir output/tfidf --file carroll-alice.txt --k 8
```

## What these examples are for

- Confirming that `idf = ln(N / df)` really zeros corpus-wide words.
- Seeing IDF split two terms that have the same in-document TF (`apple` vs
  `orchard` in the tiny corpus; `whale` vs `ahab` in Melville).
- Noticing tokenizer artifacts (Folio prefixes, Gutenberg headers) instead of
  pretending the input is clean.

They are not a search-engine tutorial and not a claim that this weighting is
the “modern” default (BM25, sublinear TF, and smoothed IDF are all more common
now). The point is to make **this** toy implementation inspectable.
