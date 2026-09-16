# Hand calculation for the tiny corpus

Collection size `N = 4`. Natural log. Tokenization: lowercase, drop
punctuation, split on spaces. Trailing newlines are whitespace and do not
become part of the last token.

```
tf(t, d)    = count(t, d) / tokens(d)
idf(t)      = ln(4 / df(t))
tfidf(t, d) = tf(t, d) * idf(t)
```

Useful constants:

```
ln(4/1) = ln(4)   = 1.38629436112
ln(4/2) = ln(2)   = 0.69314718056
ln(4/3)           = 0.28768207245
```

## Tokens

**cats.txt** (8): `cats chase mice cats sleep on warm mats`

| term | count | tf = count/8 |
| --- | ---: | ---: |
| cats | 2 | 0.250000 |
| chase | 1 | 0.125000 |
| mice | 1 | 0.125000 |
| sleep | 1 | 0.125000 |
| on | 1 | 0.125000 |
| warm | 1 | 0.125000 |
| mats | 1 | 0.125000 |

**dogs.txt** (8): `dogs chase cats dogs sleep on warm porches`

| term | count | tf = count/8 |
| --- | ---: | ---: |
| dogs | 2 | 0.250000 |
| chase | 1 | 0.125000 |
| cats | 1 | 0.125000 |
| sleep | 1 | 0.125000 |
| on | 1 | 0.125000 |
| warm | 1 | 0.125000 |
| porches | 1 | 0.125000 |

**space.txt** (9): `rockets fly past stars stars shine in deep space`

| term | count | tf = count/9 |
| --- | ---: | ---: |
| stars | 2 | 0.222222 |
| rockets | 1 | 0.111111 |
| fly | 1 | 0.111111 |
| past | 1 | 0.111111 |
| shine | 1 | 0.111111 |
| in | 1 | 0.111111 |
| deep | 1 | 0.111111 |
| space | 1 | 0.111111 |

**kitchen.txt** (9): `chefs chase warm bread bread smells in the kitchen`

| term | count | tf = count/9 |
| --- | ---: | ---: |
| bread | 2 | 0.222222 |
| chefs | 1 | 0.111111 |
| chase | 1 | 0.111111 |
| warm | 1 | 0.111111 |
| smells | 1 | 0.111111 |
| in | 1 | 0.111111 |
| the | 1 | 0.111111 |
| kitchen | 1 | 0.111111 |

## Document frequency

A term's DF is how many of the four files contain it at least once.

| term | docs | df | idf |
| --- | --- | ---: | ---: |
| bread, chefs, deep, dogs, fly, kitchen, mats, mice, past, porches, rockets, shine, smells, space, stars, the | one file each | 1 | 1.386294 |
| cats | cats, dogs | 2 | 0.693147 |
| in | space, kitchen | 2 | 0.693147 |
| on | cats, dogs | 2 | 0.693147 |
| sleep | cats, dogs | 2 | 0.693147 |
| chase | cats, dogs, kitchen | 3 | 0.287682 |
| warm | cats, dogs, kitchen | 3 | 0.287682 |

No term appears in all four documents, so nothing has IDF 0. That is the
opposite of `the` in the Gutenberg snapshot.

## TF-IDF, document by document

Rounded to six decimals, matching `compute_tfidf.py`.

### cats.txt

| term | tf | idf | tfidf |
| --- | ---: | ---: | ---: |
| cats | 0.250000 | 0.693147 | 0.173287 |
| mats | 0.125000 | 1.386294 | 0.173287 |
| mice | 0.125000 | 1.386294 | 0.173287 |
| on | 0.125000 | 0.693147 | 0.086643 |
| sleep | 0.125000 | 0.693147 | 0.086643 |
| chase | 0.125000 | 0.287682 | 0.035960 |
| warm | 0.125000 | 0.287682 | 0.035960 |

Check one product by hand:

```
cats:  (2/8) * ln(4/2) = 0.25 * 0.69314718056 = 0.17328679514
mice:  (1/8) * ln(4/1) = 0.125 * 1.38629436112 = 0.17328679514
```

Tied on purpose. Frequency and rarity cancel.

### dogs.txt

| term | tf | idf | tfidf |
| --- | ---: | ---: | ---: |
| dogs | 0.250000 | 1.386294 | 0.346574 |
| porches | 0.125000 | 1.386294 | 0.173287 |
| cats | 0.125000 | 0.693147 | 0.086643 |
| on | 0.125000 | 0.693147 | 0.086643 |
| sleep | 0.125000 | 0.693147 | 0.086643 |
| chase | 0.125000 | 0.287682 | 0.035960 |
| warm | 0.125000 | 0.287682 | 0.035960 |

```
dogs: (2/8) * ln(4/1) = 0.25 * 1.38629436112 = 0.34657359028
```

`dogs` is the largest score in the toy collection because the 0.25 TF is
paired with a unique-term IDF. `cats` in `cats.txt` cannot do that: the
dogs document also says "cats".

### space.txt

| term | tf | idf | tfidf |
| --- | ---: | ---: | ---: |
| stars | 0.222222 | 1.386294 | 0.308065 |
| deep, fly, past, rockets, shine, space | 0.111111 | 1.386294 | 0.154033 |
| in | 0.111111 | 0.693147 | 0.077016 |

```
stars: (2/9) * ln(4) = 0.222222... * 1.38629436112 = 0.30806541358
in:    (1/9) * ln(2) = 0.111111... * 0.69314718056 = 0.07701635340
```

`in` is the only term space shares with kitchen, so it is the only term
that is not at maximum IDF.

### kitchen.txt

| term | tf | idf | tfidf |
| --- | ---: | ---: | ---: |
| bread | 0.222222 | 1.386294 | 0.308065 |
| chefs, kitchen, smells, the | 0.111111 | 1.386294 | 0.154033 |
| in | 0.111111 | 0.693147 | 0.077016 |
| chase | 0.111111 | 0.287682 | 0.031965 |
| warm | 0.111111 | 0.287682 | 0.031965 |

`the` scores like `chefs` because in *this* collection it is equally rare.
Add a fifth document that also says "the" and both the kitchen row and the
Gutenberg intuition start to line up.

## Cosine sketch (optional)

Treat each document as its TF-IDF vector. `cats.txt` and `dogs.txt` share
`cats`, `sleep`, `on`, `chase`, and `warm`. `space.txt` shares only `in`
with `kitchen.txt` and nothing with the animals. The Gutenberg compare
script (`examples/compare_documents.py`) is the same cosine on much larger
vectors; this corpus is the version you can finish on paper.

Dot product of cats × dogs, using six-decimal scores:

```
cats    : 0.173287 * 0.086643 = 0.015014
sleep   : 0.086643 * 0.086643 = 0.007507
on      : 0.086643 * 0.086643 = 0.007507
chase   : 0.035960 * 0.035960 = 0.001293
warm    : 0.035960 * 0.035960 = 0.001293
sum                     ≈ 0.032614
```

`python3 examples/tiny-corpus/test_compute_tfidf.py` asserts the TF / IDF /
TF-IDF tables; it does not lock this approximate cosine.
