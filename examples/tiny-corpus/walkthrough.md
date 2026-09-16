# Tiny corpus walkthrough

Three documents, six tokens each. Every number on this page is reproducible with:

```bash
python3 examples/python/tfidf_example.py \
  --input-dir examples/tiny-corpus/docs \
  --output-dir /tmp/tiny-tfidf
```

Expected tables live in `expected/` next to this file. `N = 3`. The logarithm is natural (`math.log`, same as Perl `log`).

## Documents

`docs/cats.txt`

```
the cat sat on the mat
```

`docs/dogs.txt`

```
the dog sat on the log
```

`docs/birds.txt`

```
a bird sat on the nest
```

After the same cleaning rules as `tf-idf-values.pl` there is nothing to strip: already lowercase, no punctuation.

| document | tokens | length |
| --- | --- | --- |
| cats.txt | the, cat, sat, on, the, mat | 6 |
| dogs.txt | the, dog, sat, on, the, log | 6 |
| birds.txt | a, bird, sat, on, the, nest | 6 |

## Term frequency

```
tf(t, d) = count(t, d) / 6
```

### cats.txt

| term | count | tf |
| --- | --- | --- |
| the | 2 | 2/6 = 0.3333333333333333 |
| cat | 1 | 1/6 = 0.16666666666666666 |
| sat | 1 | 1/6 |
| on | 1 | 1/6 |
| mat | 1 | 1/6 |

`the` is the most frequent word in the file. If we stopped here, we would report that cats.txt is about *the*.

### dogs.txt

Same shape: `the` at 2/6, `dog` / `sat` / `on` / `log` at 1/6.

### birds.txt

No repeated word. Every token is 1/6, including `the` (once) and `a`.

## Document frequency

A term's DF is the number of files it appears in, not how often it repeats inside a file. `the` occurs twice in cats.txt and still contributes only 1 to DF.

| term | df | documents |
| --- | --- | --- |
| the | 3 | cats, dogs, birds |
| sat | 3 | cats, dogs, birds |
| on | 3 | cats, dogs, birds |
| cat | 1 | cats |
| mat | 1 | cats |
| dog | 1 | dogs |
| log | 1 | dogs |
| a | 1 | birds |
| bird | 1 | birds |
| nest | 1 | birds |

Ten terms in the union. That is the whole vocabulary.

## Inverse document frequency

```
idf(t) = ln(3 / df(t))
```

| term | df | N/df | idf |
| --- | --- | --- | --- |
| the, sat, on | 3 | 1 | `ln(1) = 0.0` |
| every other term | 1 | 3 | `ln(3) = 1.0986122886681098` |

This is the same contrast as `the` vs `dormouse` on the Gutenberg shelf: collection-wide words are exactly zeroed.

## TF-IDF

```
tfidf(t, d) = tf(t, d) * idf(t)
```

### cats.txt

| term | tf | idf | tf-idf |
| --- | --- | --- | --- |
| cat | 0.16666666666666666 | 1.0986122886681098 | 0.1831020481113516 |
| mat | 0.16666666666666666 | 1.0986122886681098 | 0.1831020481113516 |
| the | 0.3333333333333333 | 0.0 | 0.0 |
| sat | 0.16666666666666666 | 0.0 | 0.0 |
| on | 0.16666666666666666 | 0.0 | 0.0 |

Ranking by TF-IDF: **cat**, **mat**. The document is no longer "about *the*".

### dogs.txt

**dog** and **log** at 0.1831020481113516; `the` / `sat` / `on` at 0.

### birds.txt

**a**, **bird**, **nest** at 0.1831020481113516; `sat` / `on` / `the` at 0.

`a` scores as high as `bird` because this toy collection has no other file that uses the word *a*. In the 18-book Gutenberg run, `a` appears in every file and its IDF is 0. The toy corpus is honest about that: IDF is rarity *in the shelf you actually built*, not an intrinsic property of English.

## One identity to check by hand

```
tf(cat, cats)    = 1 / 6
idf(cat)         = ln(3 / 1) = ln(3)
tfidf(cat, cats) = ln(3) / 6 ≈ 0.1831020481113516
```

`expected/tf/cats.txt`, `expected/idf.txt`, and `expected/tfidf/cats.txt` store those three numbers. If they ever disagree, the writer or the formula changed.

## What happens if you add a fourth file

Create `docs/pets.txt` containing `the cat and the dog` and rerun without changing the scripts.

- `N` becomes 4.
- `df(cat)` becomes 2, `idf(cat) = ln(4/2) = ln(2) ≈ 0.693147`.
- `tfidf(cat, cats)` falls from `ln(3)/6` to `ln(2)/6 ≈ 0.115525`.
- `the` still has `df = N`, so its IDF stays 0.

That is the same experiment as copying `carroll-alice.txt` on the big shelf, at a scale you can finish on paper.

## What happens if you use raw counts instead of TF

`count(cat, cats) = 1` looks the same as `count(whale, Moby-Dick) = 1`. Length-normalized TF is why a six-word file and a 212k-token novel can share a formula. Try ranking the tiny files by raw count: every distinctive noun is tied at 1, and you learn nothing about cats vs dogs vs birds that TF-IDF did not already tell you — because the documents are the same length. The Gutenberg collection is where the denominator matters.

## Files written

```
expected/
  df.txt
  idf.txt
  tf/cats.txt
  tf/dogs.txt
  tf/birds.txt
  tfidf/cats.txt
  tfidf/dogs.txt
  tfidf/birds.txt
```

Formats match [../../docs/output-formats.md](../../docs/output-formats.md), except DF filenames are sorted (the Python writer is deterministic; Perl's `keys` hash order is not).
