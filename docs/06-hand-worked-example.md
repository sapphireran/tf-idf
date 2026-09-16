# Hand-worked three-document example

This is small enough to finish with a pen. The files live in
`examples/classic-three-docs/` and the numbers below are asserted in
`tests/test_tfidf_toy.py`.

## Documents

| id | file | text |
| --- | --- | --- |
| d1 | `cat_mat.txt` | `the cat sat on the mat` |
| d2 | `dog_log.txt` | `the dog sat on the log` |
| d3 | `friends.txt` | `cats and dogs are friends` |

Tokenize by lowercasing (already lower) and splitting on spaces.
Nothing to strip.

## Token lists

- d1: `the`, `cat`, `sat`, `on`, `the`, `mat` — **6** tokens
- d2: `the`, `dog`, `sat`, `on`, `the`, `log` — **6** tokens
- d3: `cats`, `and`, `dogs`, `are`, `friends` — **5** tokens

`N = 3`.

## Normalized TF

```
tf(t, d) = count(t, d) / |d|
```

### d1

| term | count | tf |
| --- | ---: | ---: |
| the | 2 | 2/6 = 0.333333 |
| cat | 1 | 1/6 = 0.166667 |
| sat | 1 | 1/6 |
| on | 1 | 1/6 |
| mat | 1 | 1/6 |

### d2

| term | count | tf |
| --- | ---: | ---: |
| the | 2 | 2/6 |
| dog | 1 | 1/6 |
| sat | 1 | 1/6 |
| on | 1 | 1/6 |
| log | 1 | 1/6 |

### d3

Each of the five terms has tf = 1/5 = 0.2.

## Document frequency and IDF

```
idf(t) = ln(N / df(t)) = ln(3 / df(t))
```

`ln(3) ≈ 1.09861228866811`
`ln(3/2) ≈ 0.40546510810816`

| term | appears in | df | idf |
| --- | --- | ---: | ---: |
| the | d1, d2 | 2 | ln(3/2) ≈ 0.405465 |
| sat | d1, d2 | 2 | ln(3/2) ≈ 0.405465 |
| on | d1, d2 | 2 | ln(3/2) ≈ 0.405465 |
| cat | d1 | 1 | ln(3) ≈ 1.098612 |
| mat | d1 | 1 | ln(3) ≈ 1.098612 |
| dog | d2 | 1 | ln(3) ≈ 1.098612 |
| log | d2 | 1 | ln(3) ≈ 1.098612 |
| cats | d3 | 1 | ln(3) ≈ 1.098612 |
| and | d3 | 1 | ln(3) ≈ 1.098612 |
| dogs | d3 | 1 | ln(3) ≈ 1.098612 |
| are | d3 | 1 | ln(3) ≈ 1.098612 |
| friends | d3 | 1 | ln(3) ≈ 1.098612 |

`the` is **not** zeroed out. It is missing from d3, so IDF still has
something to do. That is the contrast with the five-vignette corpus,
where `the` really is in every file.

## TF-IDF

```
tfidf(t, d) = tf(t, d) * idf(t)
```

### d1 (`cat_mat.txt`)

| term | tf | idf | tf*idf |
| --- | ---: | ---: | ---: |
| cat | 1/6 | ln(3) | **0.183102** |
| mat | 1/6 | ln(3) | **0.183102** |
| the | 2/6 | ln(3/2) | **0.135155** |
| sat | 1/6 | ln(3/2) | **0.067578** |
| on | 1/6 | ln(3/2) | **0.067578** |

`cat` outranks `the` even though `the` occurs twice. The extra count
does not make up for the lower IDF. `cat` and `mat` tie: same TF, same
IDF. The implementation breaks remaining ties alphabetically, so a
printed table may show `cat` then `mat`.

### d2 (`dog_log.txt`)

Symmetric with d1: `dog` and `log` at 0.183102, then `the` at
0.135155, then `sat` / `on`.

### d3 (`friends.txt`)

Every term is unique to d3, every tf is 1/5:

```
(1/5) * ln(3) ≈ 0.219722
```

All five terms tie at **0.219722**. Alphabetical order is the only
order left: `and`, `are`, `cats`, `dogs`, `friends`.

## What this example is trying to show

1. Length normalization is visible: d3's terms have larger TF because
   the document is shorter, so their tied score (0.220) is a bit above
   d1's unique terms (0.183).
2. IDF is a **collection** statistic. You cannot compute it from d1
   alone.
3. Ties are normal. A ranking that pretends otherwise is hiding them.
4. Stopwords are collection-dependent. `the` is a stopword in a corpus
   of English novels. Here it is only *mostly* common.

Run:

```bash
python3 examples/tfidf_toy.py --corpus examples/classic-three-docs
```

You should see the same six-decimal figures.
