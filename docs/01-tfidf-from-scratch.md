# tf * idf from scratch

`tf * idf` is a weighting scheme for tokens in a corpus. It answers a narrow question:

> Which words are **characteristic of this document**, relative to the rest of the collection?

A word can be frequent in a document because it is frequent everywhere (`the`). A word can be rare in the corpus because it is a typo. The product is a compromise: frequent *here*, uncommon *elsewhere*.

## Term frequency

Raw count is a poor weight on its own. *Alice's Adventures in Wonderland* is much shorter than the King James Bible, so a raw count of `said` is not comparable across books.

This repo uses **length-normalized** term frequency:

```
tf(t, d) = count(t, d) / token_count(d)
```

`token_count(d)` is the number of whitespace-separated tokens in `d` after the normalizer runs. In the original Perl script that denominator also counts empty strings produced by `split` (see [05-quirks-and-design-choices.md](05-quirks-and-design-choices.md)). The Python rewrite can match that behavior or skip empties.

A token that appears 3 times in a 7-token document has `tf = 3/7 ≈ 0.4286`.

## Document frequency

```
df(t) = |{ d in corpus : count(t, d) > 0 }|
```

`df` ignores how often the token occurs inside a document. `alice` appearing 400 times in one book and once in another still has `df = 2`.

In the committed Gutenberg tables:

| Token | df | Reading |
| --- | ---: | --- |
| `the` | 18 | In every book |
| `alice` | 3 | Rare, but not unique |
| `gryphon` | 2 | Very rare |
| `dormouse` | 1 | Unique to one book |
| `ahab` | 2 | Almost unique |
| `whale` | 6 | Distinctive but shared |

36,887 of 57,368 vocabulary items have `df = 1`. Most of the vocabulary is a hapax-across-documents: a spelling, a proper name, or a word that only one author used in this sample.

## Inverse document frequency

```
idf(t) = ln(N / df(t))
```

`N` is the corpus size. For the Gutenberg sample, `N = 18`. The committed `output/idf.txt` matches `ln(18 / df(t))` for every well-formed row.

Useful checkpoints:

```
ln(18/1)  = 2.8903717578961645    unique token
ln(18/2)  = 2.1972245773362196
ln(18/3)  = 1.791759469228055
ln(18/6)  = 1.0986122886681098
ln(18/9)  = 0.6931471805599453
ln(18/18) = 0                     corpus-wide token
```

Properties that matter in this toy:

- `idf` is **not** a property of a document. It is a property of a token in a corpus.
- Adding a 19th book changes every `idf`, including tokens that do not appear in the new book.
- A token in every document is worthless as a discriminator, so its `idf` is exactly 0.

There are other common variants (`ln((N+1) / df)`, smoothed `ln(N / (df+1)) + 1`, log-base-2, plus-one TF). This repo does not use them. The 2012 scripts and the Python rewrite stay on `ln(N / df)`.

## The product

```
tfidf(t, d) = tf(t, d) * idf(t)
```

Worked numbers from the committed Alice table:

| Token | tf (Alice) | df | idf | tf * idf |
| --- | ---: | ---: | ---: | ---: |
| `alice` | 0.014485 | 3 | 1.7918 | 0.025957 |
| `dormouse` | 0.001468 | 1 | 2.8904 | 0.004242 |
| `the` | 0.0613 (approx.) | 18 | 0 | 0 |

`alice` is not unique to Carroll in this sample (it also appears in other books as a word or name), but it is frequent enough in Carroll and rare enough elsewhere to win. `dormouse` is unique, so it gets the maximum `idf`, but it is much rarer inside the book, so it ranks below `alice`. `the` vanishes.

That is the whole idea.

## What the product is not

- It is not a probability.
- It is not comparable across corpora with different `N` without care.
- It is not robust to tokenizer changes. `Alice's` and `alice` are different strings until punctuation is stripped; after stripping they become `alices` and `alice`.
- It does not know that `whale` and `whales` are the same lemma.

If you want a ranking of "what this book is about," `tf * idf` is a blunt but surprisingly readable first cut. The worked notes in `examples/worked/` read those rankings as literary labels, not as truth.

## A three-document sketch

The tiny corpus in `examples/tiny-corpus/` is the same formula on 21 tokens:

```
tf("cats", cats.txt) = 2/7
df("cats")           = 2
idf("cats")          = ln(3/2) ≈ 0.4055
tfidf                ≈ 0.1158
```

```
tf("chase", cats.txt) = 1/7
df("chase")           = 3
idf("chase")          = ln(3/3) = 0
tfidf                 = 0
```

`chase` appears in every short document, so it is this toy's `the`. `cats` is shared by two documents, so it is this toy's `alice`: distinctive, not unique. `mice` is unique, so it is this toy's `dormouse`.

The full arithmetic is in [../examples/tiny-corpus/walkthrough.md](../examples/tiny-corpus/walkthrough.md).
