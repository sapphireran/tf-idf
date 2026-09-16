# TF-IDF primer (the variant this repo uses)

TF-IDF is a way to score how much a word characterizes a document *inside a
specific collection*. A word can be frequent in a book and still be a poor
label for that book if every other book uses it just as often.

This note matches the arithmetic in `tf-idf-values.pl` and
`tf*idf-product.pl`. Other toolkits (scikit-learn, Lucene, Indri) pick
different defaults. The differences are listed at the end so the Gutenberg
tables are not compared to those systems by accident.

## Term frequency

After tokenization (see [07-tokenization-and-quirks.md](07-tokenization-and-quirks.md)),
each document `d` is a bag of tokens. Raw count is divided by the document
length so a long book does not automatically outscore a short one:

```
TF(t, d) = count(t, d) / |d|
```

`|d|` is the number of tokens after cleaning, including stopwords. In
`output/tf/carroll-alice.txt` the line

```
alice	0.0144867549668874
```

means the token `alice` is about 1.45% of Alice's token stream. Common words
such as `the` have a much larger TF and a much smaller IDF.

This is **normalized term frequency**, not the raw count and not the BM25
saturation function. A word that appears twice in a 20-token note has
`TF = 0.10`. The same word appearing 200 times in a 2000-token chapter also
has `TF = 0.10`.

## Document frequency

```
df(t) = number of documents that contain t at least once
```

The scripts do not count extra occurrences inside a document. If `whale`
appears 1,000 times in *Moby-Dick* and once in *Hamlet*, `df(whale)` is still
only as large as the number of files that contain the token.

`output/df.txt` records that value and the filenames:

```
whale	6	melville-moby_dick.txt, bible-kjv.txt, whitman-leaves.txt, ...
alice	3	chesterton-thursday.txt, carroll-alice.txt, edgeworth-parents.txt
macbeth	1	shakespeare-macbeth.txt
the	18	(every book)
```

A 57,367-term vocabulary is large because the tokenizer keeps digits, fused
punctuation leftovers, and every proper name.

## Inverse document frequency

```
IDF(t) = ln(N / df(t))
```

`ln` is the natural logarithm, which is Perl's `log` without a base. `N` for
the checked-in Gutenberg tables is **18**, the number of `.txt` files that
were actually scored.

| df | IDF = ln(18 / df) | What that means on this shelf |
| --- | --- | --- |
| 1 | 2.890372 | appears in a single book (`macbeth`, `pequod`, `buster`) |
| 2 | 2.197225 | two books (`ahab`, `emma`, `woodhouse`) |
| 3 | 1.791759 | three books (`alice`) |
| 6 | 1.098612 | a third of the shelf (`whale`, `hamlet`) |
| 18 | 0 | every book (`the`, `and`) |

IDF is a property of the *collection*, not of a single file. That is why
`output/idf.txt` is one table shared by every document, and why adding a
nineteenth book would change every IDF value.

The zero at `df = N` is the most important special case. It is not a bug:
if a word cannot distinguish one document from another, TF-IDF assigns it
no weight. In the Alice table the term `all` has TF-IDF `0` for that reason.

There is no smoothing. A term must appear in at least one document to be in
the table at all, so `df(t)` is never 0 and `N / df(t)` is never undefined.

## The product

```
TF-IDF(t, d) = TF(t, d) * IDF(t)
```

`tf*idf-product.pl` does exactly that multiplication. High scores need both
halves:

* high TF — the document actually uses the word
* high IDF — the rest of the shelf mostly does not

That is why `alice` (TF ≈ 0.0145, IDF ≈ 1.792) dominates Carroll, while
`whale` (lower TF, IDF ≈ 1.099 because six books mention whales) still wins
*Moby-Dick* but by a smaller margin. Character names that are almost unique
to one novel (`gryphon`, `queequeg`, `hartfield`) rise even when they are
rarer than the title name.

A query such as `alice gryphon hatter` is just the sum of those per-document
weights. The ranking tool in `examples/query_documents.py` does that sum;
the walkthrough is in [06-querying-and-ranking.md](06-querying-and-ranking.md).

## What this variant is not

These are common alternatives this repo does **not** use:

| Variant | What changes |
| --- | --- |
| Raw TF | skip the `/ \|d\|` normalization |
| Log TF | `1 + ln(count)` so the 1,000th `whale` barely moves the score |
| Smoothed IDF | `ln((N + 1) / (df + 1)) + 1` or `ln(N / (df + 1))` |
| Base-10 IDF | same ranking inside one collection, different absolute numbers |
| sklearn `TfidfVectorizer` | L2-normalized rows, smoothed IDF, often `idf + 1` |
| BM25 | saturating TF, document-length prior, different IDF |

If you reimplement the shelf in another toolkit and the top terms shuffle,
check the tokenizer and the IDF definition before debugging the corpus.
`examples/compare_variants.py` runs three of those definitions on the
four-document toy so the difference is visible without leaving the repo.

## Worked numbers

The four-document toy in `examples/tiny-corpus/` uses the same three
formulas with `N = 4`. The next note,
[03-worked-example.md](03-worked-example.md), expands every token of
`tea-garden.txt`. The Gutenberg catalogue in
[02-gutenberg-corpus.md](02-gutenberg-corpus.md) shows what the same math
does to real books.
