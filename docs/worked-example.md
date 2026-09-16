# Worked example: three six-word documents

This is the entire collection in [`examples/tiny-corpus/`](../examples/tiny-corpus/):

```
cats.txt:   the cat sat on the mat
dogs.txt:   the dog sat on the log
birds.txt:  a bird flew over the lake
```

Tokenization is lowercase, punctuation stripped, split on spaces. There
is no punctuation here, so each file is exactly six tokens. `N = 3`.

## Document frequency and idf

A term's `df` is the number of files that contain it at least once.

| term | files | `df` | `idf = ln(3 / df)` |
| --- | --- | --- | --- |
| the | cats, dogs, birds | 3 | `ln(1) = 0` |
| sat | cats, dogs | 2 | `ln(1.5) ≈ 0.405465108108` |
| on | cats, dogs | 2 | `ln(1.5) ≈ 0.405465108108` |
| cat, mat | cats | 1 | `ln(3) ≈ 1.098612288668` |
| dog, log | dogs | 1 | `ln(3) ≈ 1.098612288668` |
| a, bird, flew, over, lake | birds | 1 | `ln(3) ≈ 1.098612288668` |

`the` is useless as a keyword in this collection. Everything else is
some kind of content word.

## Term frequency

`tf = count / 6`.

### cats.txt

| term | count | tf |
| --- | --- | --- |
| the | 2 | 2/6 = 0.333333… |
| cat | 1 | 1/6 = 0.166666… |
| sat | 1 | 1/6 |
| on | 1 | 1/6 |
| mat | 1 | 1/6 |

### dogs.txt

Same shape: `the` twice, then `dog`, `sat`, `on`, `log` once each.

### birds.txt

Every term once, including a single `the`. `a` is a hapax in this
collection, so it gets the large idf — a reminder that tf-idf is not a
linguistic stoplist. In the 18-book Gutenberg slice, `a` appears
everywhere and its idf falls to 0.

## tf-idf

`tfidf = tf * idf`. Values below use `ln` and full double precision,
matching [`examples/tiny-corpus/expected.json`](../examples/tiny-corpus/expected.json)
and `tests/test_tfidf.py`.

### cats.txt

| term | tf | idf | tf-idf |
| --- | --- | --- | --- |
| cat | 1/6 | ln(3) | **0.183102048111** |
| mat | 1/6 | ln(3) | **0.183102048111** |
| sat | 1/6 | ln(3/2) | 0.067577518018 |
| on | 1/6 | ln(3/2) | 0.067577518018 |
| the | 2/6 | 0 | 0 |

`cat` and `mat` tie. That is correct: same count, same df.

### dogs.txt

| term | tf-idf |
| --- | --- |
| dog, log | 0.183102048111 |
| sat, on | 0.067577518018 |
| the | 0 |

### birds.txt

| term | tf-idf |
| --- | --- |
| a, bird, flew, over, lake | 0.183102048111 |
| the | 0 |

`birds.txt` shares only `the` with the other files, so five of its six
tokens land in the top bucket.

## What this example is for

- Check a new implementation against numbers you can redo on paper.
- See `idf = 0` kill a high-tf function word.
- See a two-document overlap (`sat`, `on`) lose to a one-document
  content word.

Recompute:

```bash
python3 examples/python/tfidf.py --input examples/tiny-corpus --top 6
perl examples/perl/compute_tf_idf.pl --input examples/tiny-corpus --output examples/_scratch/tiny-perl
python3 -m unittest discover -s tests -v
```

The themed paragraphs in [`examples/themes-corpus/`](../examples/themes-corpus/)
use the same formulas on slightly longer text, so `baker` / `telescope` /
`violin` separate cleanly without a three-way tie on every content word.
