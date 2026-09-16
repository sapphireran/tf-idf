# Hand calculation: three six-token documents

This folder is the smallest corpus in the repo. Every weight can be computed
with a pencil. The Python tests in `tests/test_hand_corpus_files.py` check
that `python3 -m tfidf` reproduces the arithmetic below.

## Documents

| file | text | tokens |
| --- | --- | --- |
| `doc-a.txt` | the cat sat on the mat | 6 |
| `doc-b.txt` | the dog sat on the log | 6 |
| `doc-c.txt` | a cat and a dog played | 6 |

`N = 3`. Term frequency is raw count divided by 6.

## Document frequency

| term | documents | df |
| --- | --- | ---: |
| the | A, B | 2 |
| sat | A, B | 2 |
| on | A, B | 2 |
| cat | A, C | 2 |
| dog | B, C | 2 |
| mat | A | 1 |
| log | B | 1 |
| a | C | 1 |
| and | C | 1 |
| played | C | 1 |

## Inverse document frequency

Raw IDF uses the natural log, matching Perl's `log`:

```
idf(t) = ln(N / df(t))
```

| term | df | idf |
| --- | ---: | ---: |
| the, sat, on, cat, dog | 2 | ln(3/2) ≈ 0.405465 |
| mat, log, a, and, played | 1 | ln(3/1) ≈ 1.098612 |

## TF-IDF for document A

| term | tf | idf | tf-idf |
| --- | ---: | ---: | ---: |
| the | 2/6 | 0.405465 | **0.135155** |
| cat | 1/6 | 0.405465 | 0.067577 |
| sat | 1/6 | 0.405465 | 0.067577 |
| on | 1/6 | 0.405465 | 0.067577 |
| mat | 1/6 | 1.098612 | **0.183102** |

`mat` wins because it is unique to A. `the` is more frequent inside A but
appears in two documents, so IDF cuts it down.

The same pattern makes `log` the top term of B and `played` (tied with `a`
and `and` on frequency, unique to C) a top term of C.

## Run it

From the repository root:

```bash
python3 -m tfidf report examples/hand-calculation/corpus --n 5
python3 -m tfidf query examples/hand-calculation/corpus "the mat"
```

The query `the mat` should rank `doc-a.txt` first: `mat` has a high IDF and
only A contains it.

## Compare with smoothed IDF

```bash
python3 -m tfidf top examples/hand-calculation/corpus --idf smooth --n 5
```

Smoothed IDF is `ln((N+1)/(df+1)) + 1`. Terms that appear everywhere no
longer go to zero; see `docs/variants.md`.
