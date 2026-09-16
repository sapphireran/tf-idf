# Formulas used in this repo

The committed tables use one specific triple. Write `count(t, d)` for
the number of times term `t` appears in document `d`, `|d|` for the
number of tokens in `d`, `df(t)` for the number of documents that
contain `t` at least once, and `N` for the number of documents in the
collection.

## Term frequency

```
tf(t, d) = count(t, d) / |d|
```

This is a proportion, not a raw count. A word that appears 10 times in
a 100-token essay scores `0.10`. The same 10 occurrences in a
100,000-token novel score `0.0001`. That is why the tiny-corpus tables
and the Gutenberg tables are not on the same numeric scale even when
the IDF values look familiar.

`tf-idf-values.pl` writes one `output/tf/<file>` row per term, sorted
by term, as `term<TAB>tf`.

## Inverse document frequency

```
idf(t) = ln(N / df(t))
```

The logarithm is the natural log, Perl's `log` and Python's
`math.log`. There is no `+1` smoother and no extra constant.

Properties that follow immediately:

- If `t` appears in every document, `df(t) = N` and `idf(t) = 0`.
- If `t` appears in one document, `idf(t) = ln(N)`.
- IDF never depends on how often the term occurs inside a document.
  Ten mentions and one mention produce the same IDF.

For the committed Gutenberg files, `N = 18`. You can verify that by
reading any singleton in `output/idf.txt`:

```
ln(18) = 2.89037175789616
```

That constant is the ceiling of the IDF column.

## The product

```
tfidf(t, d) = tf(t, d) * idf(t)
```

`tf*idf-product.pl` reads `output/idf.txt` and each `output/tf/<file>`,
multiplies matching keys, and writes `output/tfidf/<file>`. A missing
IDF key would produce an empty product for that term; the two scripts
are meant to be run as a pair on the same collection.

## Document frequency table

`output/df.txt` is a convenience dump, not an input to the product
script. Each row is:

```
term <TAB> df <TAB> comma-separated file names
```

`output/df-sorted.txt` is the same information ordered for browsing.

## A note about `N` in the Perl script

`tf-idf-values.pl` currently sets

```perl
my $n = $#files;
```

`$#files` is the last index of the `readdir` list, not the count of
processed `.txt` files. A directory that contains `.`, `..`,
`.DS_Store`, and 18 books has 21 entries, so `$#files` is 20. The
committed `output/idf.txt` was produced with `N = 18`, which is the
number of actual books and the number the Python reference uses.

When you regenerate Gutenberg scores, prefer an explicit document
count. The tiny-corpus tools already do that.

## Cosine similarity (examples only)

The original Perl path stops at per-document term weights. The Python
examples add a comparison step:

```
cos(u, v) = (u · v) / (|u| |v|)
```

Each vector is the sparse TF-IDF map of one document. Cosine is not
required to understand the tables; it is there so two essays can be
compared after they have been scored.
