# How to read the published `output/` tables

The files under `output/` are the 2012 result set. They are large (`df.txt` is about 3.5 MB; `idf.txt` has ~57k rows) and they are **not** ranked. This note is a field guide for opening them without getting lost.

## What each directory is for

| File | Rows | Columns | Question it answers |
| --- | --- | --- | --- |
| `output/tf/<book>.txt` | vocabulary of that book | token, tf | How often does this token appear *in this book*, as a fraction of the book's tokens? |
| `output/df.txt` | union vocabulary | token, df, file list | How many books contain this token, and which ones? |
| `output/idf.txt` | same union | token, idf | How surprising is this token in an 18-book collection? |
| `output/tfidf/<book>.txt` | vocabulary of that book | token, tf×idf | How characteristic is this token *of this book*? |
| `output/df-sorted.txt` | same as `df.txt` | same | `df.txt` ordered for eyeballing (not produced by the Perl scripts) |

`output/.DS_Store` is leftover Finder metadata. Ignore it.

## Open a table as TSV

Every data file is tab-separated. `df.txt` is the only one with a header.

```bash
# 15 highest tf*idf weights in Alice (committed table)
python3 examples/python/rank_terms.py --from-table output/tfidf/carroll-alice.txt --top 15

# same idea with standard Unix tools
sort -t$'\t' -k2,2nr output/tfidf/carroll-alice.txt | head
```

Do not assume the on-disk order is a ranking. Both Perl writers iterate `sort keys %hash`, i.e. alphabetical by token.

## A single token across the four tables

Take `alice`:

| Table | Value | Meaning |
| --- | --- | --- |
| `output/tf/carroll-alice.txt` | `0.01448675` | about 1.45% of Alice's tokens |
| `output/df.txt` | `3` books: Thursday, Alice, Edgeworth | not unique to Carroll |
| `output/idf.txt` | `1.79175947` = \(\ln(18/3)\) | moderately rare |
| `output/tfidf/carroll-alice.txt` | `0.02595678` | still the top weight *in Alice* because the tf is huge there |

In *The Man Who Was Thursday* the same token has a tiny tf (a passing mention) times the same idf, so it does not appear near the top of that book's ranking. IDF is a property of the **collection**; TF and TF-IDF are properties of a **(token, document)** pair.

## Zeros are information

A `0` in a `tfidf` file almost always means “this token's IDF is 0”, i.e. it occurred in all 18 books. It does **not** mean the token is absent — absent tokens are omitted entirely.

Useful check:

```bash
# tokens that cannot discriminate among these 18 books
awk -F'\t' '$2 == 0 { print $1 }' output/idf.txt | head
```

You should see function words (`a`, `and`, `if`, `of`, `the`, `when`, …). That list is the implicit stoplist of this collection.

## Scientific notation

Perl prints small floats as `8.26770235301107e-05`. That is ordinary scientific notation, not a second column. `rank_terms.py` and `float()` both accept it.

## The `df` file list is not a ranking either

```
whale	6	melville-moby_dick.txt, milton-paradise.txt, ...
```

Order of filenames is Perl hash-key order. Do not read “first named book” as “book that uses the word most”. To see *that*, compare the `tf` or `tfidf` value of `whale` across the six files.

## Scale differences between books

TF-IDF values are not comparable as “importance out of 1.0” across books of very different length and vocabulary.

| Book | Top token | Top weight (committed) | Why the scale differs |
| --- | --- | --- | --- |
| `chesterton-thursday.txt` | `syme` | ~0.0244 | one name, used constantly, almost collection-unique |
| `carroll-alice.txt` | `alice` | ~0.0260 | same pattern |
| `melville-moby_dick.txt` | `whale` | ~0.0049 | long book; mass is spread over `whale`, `ahab`, `sperm`, `stubb`, … |
| `whitman-leaves.txt` | `o` | ~0.0018 | huge, diffuse vocabulary; even the winner is small |

A 0.004 weight in *Moby-Dick* can still be the most characteristic term in that book.

## When to recompute vs when to read

| Goal | Use |
| --- | --- |
| Understand the 2012 blog numbers | committed `output/` |
| Rank or compare those numbers | `examples/python/rank_terms.py --from-table …` |
| Reproduce the *intended* formula \(N=18\) from `gutenberg/` | `examples/python/tfidf_toy.py gutenberg` |
| Reproduce the *Perl source* exactly | `perl tf-idf-values.pl` (will not match `output/` — see the notes file) |
| Hand-check the arithmetic | `examples/tiny-corpus/` |
