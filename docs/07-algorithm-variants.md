# Nearby variants

The product `tf * ln(N / df)` is one point in a small family. The
Python reference implements two neighbors so you can see what changes
when only one factor moves.

## `repo` — the default, matching this repository

```
tf = count / |d|
idf = ln(N / df)
tfidf = tf * idf
```

This is the variant committed under `output/` and under
`examples/tiny_corpus/expected/`.

## `log_tf` — dampen raw repetition

```
tf = 1 + ln(count)   for count > 0
idf = ln(N / df)
```

A term that appears 100 times no longer scores 100 times a term that
appears once. Document length drops out of TF, so short and long
files become more comparable. Distinctive rare words lose some of
their advantage if a common topical word is repeated.

Run it on the tiny corpus:

```bash
python3 examples/python/run_tiny_corpus.py --variant log_tf --out /tmp/tfidf-log-tf
```

## `smooth_idf` — keep query terms from exploding

```
tf = count / |d|
idf = ln((N + 1) / (df + 1)) + 1
```

This is a common "plus-one" form. It never hits `ln(N / 0)` if you
later score a query term that the collection has never seen, and it
never hits exact zero for a term that appears in every document.
The extra `+ 1` also shifts the whole IDF column upward, so the
absolute numbers are not comparable to the `repo` tables.

```bash
python3 examples/python/run_tiny_corpus.py --variant smooth_idf --out /tmp/tfidf-smooth
```

## Variants this repo does not implement

| Idea | What it would change |
| --- | --- |
| Raw-count TF | Long books would dominate every ranking |
| Sublinear TF `1 + log10(count)` | Similar to `log_tf`, different base |
| IDF as `log10(N / df)` | Same ranking inside a document, different scale |
| Okapi BM25 | Adds document-length normalization and saturation; not a product |
| Stop-word lists | Would drop `the` before IDF has to |
| Stemming / lemmatization | `whale` and `whales` would share mass |
| n-grams | `white rabbit` could be one term |

BM25 is the usual next reading if you want a ranking function that
search engines actually ship. It is intentionally out of scope here.
The point of this lab is to keep the product small enough that every
cell can be checked.

## A practical rule

When you change a variant, regenerate the whole collection. Mixing a
`repo` IDF file with a `log_tf` TF file produces a number that is not
in any of the writeups.
