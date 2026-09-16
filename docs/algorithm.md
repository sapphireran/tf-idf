# TF-IDF as implemented in this repo

Term frequency–inverse document frequency is a weighting scheme, not a
model. It answers a narrow question: **which words are characteristic of
this document relative to the rest of the collection?**

This repository's original Perl scripts (`tf-idf-values.pl` and
`tf*idf-product.pl`) implement the textbook product with almost no extras:
no stopword list, no stemming, no sublinear TF, no L2 normalization. The
Python package under `tfidf/` uses the same default formulas so the
examples stay comparable.

## Pieces

For a term `t` and a document `d` in a collection of `N` documents:

```
count(t, d)  = how many times t occurs in d
tf(t, d)     = count(t, d) / tokens(d)
df(t)        = how many documents contain t at least once
idf(t)       = log(N / df(t))          # natural log
tfidf(t, d)  = tf(t, d) * idf(t)
```

`tokens(d)` is the number of kept tokens after cleanup, not the number of
unique terms.

### Why divide by document length?

A 4,000-word novel will mention `the` more often than a 400-word poem.
Raw counts therefore reward length. Dividing by `tokens(d)` turns the
count into a share of the document. `whale` in *Moby-Dick* still wins
because it is both common in that file and rare in the others.

### Why the log?

Document frequency already says "this word is common across the
collection." The log compresses the range: a term in 1 of 18 documents
scores `log(18) ≈ 2.89`, a term in 9 of 18 scores `log(2) ≈ 0.69`, and a
term in all 18 scores `log(1) = 0`. Without the log, IDF would be linear
in `N/df` and a hapax would dominate even more violently.

### Why do some committed scores equal zero?

Look at `output/tfidf/carroll-alice.txt`. The terms `a`, `about`, `after`,
and `against` are `0`. Their IDF is zero because they appear in every
Gutenberg file that was processed. Raw IDF treats a collection-wide word
as useless for distinguishing documents. That is a feature of this
formula, not a bug in the TSV writer.

Smoothed IDF (`docs/variants.md`) keeps a residual weight for those
terms. The Perl scripts do not.

## Tokenization

Both the Perl and Python paths apply the same cleanup to each line:

1. Drop the newline.
2. Collapse horizontal and vertical whitespace runs to a single space.
3. Lowercase ASCII letters.
4. Delete every character that is not `[a-z0-9]` or whitespace.
5. Split on one or more spaces.

Consequences you will see in the Gutenberg tables:

| input | tokens |
| --- | --- |
| `It's` | `its` |
| `sperm-whale` | `spermwhale` |
| `221B` | `221b` |
| `o'er` | `oer` |
| speech prefixes like `Macb.` | `macb` |

Shakespeare files therefore rank `macb`, `ham`, and `bru` near the top.
Those are abbreviated speaker tags, not vocabulary about Scotland or
Denmark. The weighting is doing its job on the file it was given.

## What IDF is not

- It is not a measure of literary quality.
- It is not a topic model. There is no hidden theme variable.
- It is not robust to near-duplicate documents. If two files are the
  same text, every term's `df` rises together and the contrast collapses.
- It is not comparable across collections. `idf("whale")` on this 18-book
  mix is not the same number you would get on a marine-biology crawl.

## Worked numbers

The three-line corpus in `examples/hand-calculation/` is small enough to
recompute on paper. The four-note corpus in `examples/tiny-corpus/` is
large enough that distinctive nouns beat function words, which is the
behavior people mean when they say "TF-IDF finds keywords."

## Implementation map

| step | Perl | Python |
| --- | --- | --- |
| tokenize + TF + DF + IDF | `tf-idf-values.pl` | `tfidf.compute.build_index` |
| multiply TF by IDF | `tf*idf-product.pl` | same function, in one pass |
| write TSV | `output/tf`, `idf.txt`, `df.txt`, `output/tfidf` | `tfidf.io_tsv.write_pipeline_output` |
| rank a query | not implemented | `tfidf.compute.score_query` |

Read `docs/perl-pipeline.md` next if you want a line-by-line tour of the
2012 scripts, including the `$n = $#files` document-count quirk.
