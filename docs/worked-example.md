# Worked example: a three-document micro collection

This page computes every TF, DF, IDF, and TF-IDF value for the files
in `examples/micro-corpus/`. The documents are short enough to do by
hand. The teaching Python should reproduce the same fractions.

## The collection

**`d1-cat.txt`**

```
the cat sat on the mat
```

**`d2-dog.txt`**

```
the dog sat on the log
```

**`d3-bread.txt`**

```
bakers bake bread
```

After the shared tokenizer (already lowercase, no punctuation):

| Doc | Tokens | `words(d)` |
| --- | --- | ---: |
| d1 | the, cat, sat, on, the, mat | 6 |
| d2 | the, dog, sat, on, the, log | 6 |
| d3 | bakers, bake, bread | 3 |

`N = 3`.

## Raw counts

| Term | d1 | d2 | d3 | `df` |
| --- | ---: | ---: | ---: | ---: |
| bake | 0 | 0 | 1 | 1 |
| bakers | 0 | 0 | 1 | 1 |
| bread | 0 | 0 | 1 | 1 |
| cat | 1 | 0 | 0 | 1 |
| dog | 0 | 1 | 0 | 1 |
| log | 0 | 1 | 0 | 1 |
| mat | 1 | 0 | 0 | 1 |
| on | 1 | 1 | 0 | 2 |
| sat | 1 | 1 | 0 | 2 |
| the | 2 | 2 | 0 | 2 |

`the` is the only term with count 2. It still misses d3, so it is
**not** a collection-wide term and will not get IDF 0.

## Term frequency

`tf = count / words(d)`

| Term | tf d1 | tf d2 | tf d3 |
| --- | ---: | ---: | ---: |
| bake | 0 | 0 | 1/3 |
| bakers | 0 | 0 | 1/3 |
| bread | 0 | 0 | 1/3 |
| cat | 1/6 | 0 | 0 |
| dog | 0 | 1/6 | 0 |
| log | 0 | 1/6 | 0 |
| mat | 1/6 | 0 | 0 |
| on | 1/6 | 1/6 | 0 |
| sat | 1/6 | 1/6 | 0 |
| the | 2/6 | 2/6 | 0 |

## Inverse document frequency

`idf(t) = ln(3 / df(t))`

| `df` | `idf` | Exact |
| ---: | ---: | --- |
| 1 | `ln(3)` | 1.0986122886681098 |
| 2 | `ln(3/2)` | 0.4054651081081644 |
| 3 | `ln(1)` | 0 |

| Term | df | idf |
| --- | ---: | ---: |
| bake, bakers, bread, cat, dog, log, mat | 1 | ln(3) |
| on, sat, the | 2 | ln(3/2) |

## TF-IDF

`tfidf = tf * idf`

### d1 (cat / mat)

| Term | tf | idf | tfidf |
| --- | ---: | ---: | ---: |
| cat | 1/6 | ln(3) | 0.18310204811135163 |
| mat | 1/6 | ln(3) | 0.18310204811135163 |
| on | 1/6 | ln(3/2) | 0.0675775180180274 |
| sat | 1/6 | ln(3/2) | 0.0675775180180274 |
| the | 2/6 | ln(3/2) | 0.1351550360360548 |

Ranking: `cat` = `mat` > `the` > `on` = `sat`.

`the` outranks `on` and `sat` because it occurs twice, even though all
three shared terms have the same IDF. Distinctive nouns still win.

### d2 (dog / log)

Symmetric with d1: `dog` = `log` at the top, then `the`, then `on`/`sat`.

### d3 (bread)

Every term has `tf = 1/3` and `idf = ln(3)`:

| Term | tfidf |
| --- | ---: |
| bake | 0.36620409622270326 |
| bakers | 0.36620409622270326 |
| bread | 0.36620409622270326 |

d3 is only three tokens long, so each word's TF is large. Combined with
`df = 1`, every baking term outscores every term in d1 and d2. That is
correct for this formula and a warning: **short documents get larger
TF shares.** The Gutenberg collection is closer in scale book-to-book
than this micro set, but Blake's poems are still much shorter than the
King James Bible, which is one reason Blake's top scores can look
"spikier" on a per-term basis.

## What this example is meant to show

1. Shared function words (`the`, `on`, `sat`) get a smaller IDF, not
   a special stopword rule.
2. A word that is missing from even one document (`the` misses d3)
   keeps a positive IDF.
3. Two equally rare nouns in the same short document (`cat`, `mat`)
   tie. TF-IDF has no notion of "more interesting noun."
4. Document length is in the denominator of TF. A 3-word document is
   a loud document.

## Reproduce

```bash
python3 examples/python/compute_tfidf.py \
  --input-dir examples/micro-corpus \
  --output-dir /tmp/micro-tfidf

python3 examples/python/top_terms.py /tmp/micro-tfidf/tfidf --top 5
```

`tests/test_micro_corpus.py` asserts the table above.

## Next example

`examples/tiny-corpus/` is the same idea with paragraph-length
original texts (cats, dogs, baking). The arithmetic is too large to
do entirely by hand; the distinctive-term ranking is still obvious.
See [../examples/README.md](../examples/README.md).
