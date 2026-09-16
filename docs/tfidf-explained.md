# What tf-idf is doing

tf-idf is a bag-of-words score from information retrieval. It is not a
language model and it does not care about word order. For each pair
`(term, document)` it answers:

> How concentrated is this term in this document, relative to the rest
> of the collection?

That is enough to surface *Alice*, *Ahab*, or *violinist* without a
stopword list. Common function words drop out because they appear
everywhere.

## The two halves

### Term frequency

```
tf(t, d) = count(t, d) / tokens(d)
```

This repo uses **length-normalized** tf, matching `tf-idf-values.pl`.
A 200-count of `whale` in a 200,000-token novel is a smaller tf than a
20-count of `alice` in a 27,000-token children's book.

Raw count (`tf = count`) is the other common choice. It favors long
documents. Sublinear tf (`1 + ln(count)` when count > 0) is a third
option used by some search indexes.

### Inverse document frequency

```
idf(t) = ln( N / df(t) )
```

`N` is the number of documents in the collection. `df(t)` is the number
of those documents that contain `t` at least once. Extra occurrences
inside one document do not raise `df`.

| Situation | `df` | `idf` |
| --- | --- | --- |
| Term in every document | `N` | `ln(1) = 0` |
| Term in half the documents | `N/2` | `ln(2) ≈ 0.693` |
| Term in exactly one document | `1` | `ln(N)` |

On the committed Gutenberg run, `the`, `and`, and `a` have `idf = 0`.
`alice` appears in 3 of 18 files, so `idf = ln(18/3) = ln(6) ≈ 1.792`.
`whale` appears in 6 files: `idf = ln(3) ≈ 1.099`.

The logarithm compresses the range. Going from `df = 1` to `df = 2`
hurts more than going from `df = 9` to `df = 10`.

## The product

```
tfidf(t, d) = tf(t, d) * idf(t)
```

High score: the term is a large fraction of `d`, and few other documents
use it. Low or zero score: the term is rare in `d`, or it is so common
in the collection that `idf` is ~0.

For *Alice's Adventures in Wonderland* the committed table ranks:

| rank | term | tf-idf |
| --- | --- | --- |
| 1 | alice | 0.02596 |
| 2 | gryphon | 0.00455 |
| 3 | duchess | 0.00424 |
| 4 | dormouse | 0.00424 |
| 5 | hatter | 0.00371 |

`alice` wins on tf (the name is everywhere in that file) times a
mid-sized idf (a few other files mention the name). `gryphon` has a
higher idf but a much smaller tf.

## What the score is not

- It does not stem. `whale` and `whales` are different terms.
- It does not use a stoplist. Universal terms vanish because `idf = 0`,
  not because someone deleted them.
- It does not know that `ham` in the Hamlet file is a speech prefix.
- It is not comparable across collections. Change `N` or swap in a
  different set of books and every idf changes.
- The numbers in `output/tfidf/` are **not** L2-normalized document
  vectors. You can still cosine-similarity them, but that is a second
  step this repo does not take.

## A picture of one collection

Imagine three documents:

```
cats:   the cat sat on the mat
dogs:   the dog sat on the log
birds:  a bird flew over the lake
```

`the` is in all three → idf 0 → it never ranks. `sat` and `on` are in
two of three → small idf. `cat` / `mat` / `dog` / `log` / `bird` / …
are in one document → they take the top slots of that document.

The arithmetic for this collection is written out in
[worked-example.md](worked-example.md). Run it with:

```bash
python3 examples/python/tfidf.py --input examples/tiny-corpus --top 5
```

## Why people still use it

tf-idf is cheap, inspectable, and surprisingly good at “what is this
document about?” for a fixed corpus. It is a baseline for keyword
highlights, related-document search, and feature vectors before you
reach for embeddings. The Gutenberg toy here is the first of those:
print the words that make each book look like itself.
