# TF-IDF, as this repository computes it

This note is the formula sheet for the personal Gutenberg toy collection.
It matches the checked-in files under `output/` and the teaching Python
under `examples/python/`. It is not a survey of every TF-IDF variant used
in search engines.

## The ranking question

A raw word count says "this document talks about `the` a lot." That is
true and useless. A collection-wide word count says "`the` is common
everywhere." Also true, also useless for telling documents apart.

TF-IDF multiplies a **local** signal by a **global** signal:

- **TF** (term frequency): how concentrated is this term *inside* one
  document?
- **IDF** (inverse document frequency): how rare is this term *across*
  the collection?

A good term for ranking a document is used often in that document and
used in few other documents.

## Definitions

Let the collection be `D = {d1, d2, ..., dN}`.

After tokenization (see below), each document is a bag of terms.

| Symbol | Meaning |
| --- | --- |
| `count(t, d)` | Number of times term `t` occurs in document `d` |
| `words(d)` | Number of tokens counted as the document length |
| `tf(t, d)` | `count(t, d) / words(d)` |
| `df(t)` | Number of documents in which `t` occurs at least once |
| `N` | Number of documents in the collection |
| `idf(t)` | `ln(N / df(t))` |
| `tfidf(t, d)` | `tf(t, d) * idf(t)` |

`ln` is the natural logarithm (`math.log` in Python, `log` in Perl).
Changing the base only rescales every IDF value by a constant; rankings
inside a single document stay the same.

## Why normalize TF by document length

`Moby-Dick` is much longer than `Blake's Poems`. If TF were a raw count,
every long book would dominate every short book. Dividing by `words(d)`
turns TF into a share of the document:

- `tf("alice", carroll-alice.txt)` is "what fraction of Alice's tokens
  are the word `alice`?"
- That fraction is comparable to `tf("emma", austen-emma.txt)` even
  though the books have different lengths.

The original Perl writes this normalized TF to `output/tf/<file>`.

## Why IDF uses documents, not raw collection counts

`df(t)` counts **documents**, not tokens. A word that appears 400 times
in one novel and nowhere else is still rare at the collection level
(`df = 1`). A word that appears once in every novel is common
(`df = N`) even if each book uses it sparingly.

That is the difference between "Ahab is a Moby-Dick word" and "the
narrator said `said` again."

## Boundary values

| Situation | IDF | TF-IDF |
| --- | --- | --- |
| `t` appears in every document (`df = N`) | `ln(1) = 0` | `0` |
| `t` appears in exactly one document | `ln(N / 1) = ln(N)` | `tf(t, d) * ln(N)` |
| `t` never appears in `d` | IDF is still defined | `0` because `tf = 0` |
| `t` never appears in the collection | `df = 0` | undefined; the scripts never emit the term |

For this Gutenberg collection, `N = 18`, so a one-document term has

```
idf = ln(18) ≈ 2.89037175789616
```

That constant is the ceiling of `output/idf.txt`. Catalog numbers and
typos that occur in a single header sit at that ceiling. They only
become high-ranking TF-IDF terms if they also have a non-trivial TF —
which is why a unique Project Gutenberg id is usually a curiosity in
`idf.txt` and not a top term, while a repeated unique header word
(`ebook` in one Chesterton file) can climb the ranking.

## What IDF is not

- It is not a probability.
- It is not "importance" in a literary sense.
- It is not robust to near-duplicates. If two files are the same book,
  every term's `df` goes up by one and the IDF of the book's own
  vocabulary drops.
- It does not know that `whale` and `whales` are related. This pipeline
  has no stemmer.

## Tokenizer (shared by Perl and the teaching Python)

For each input line:

1. Replace runs of horizontal or vertical whitespace with one space.
2. Lowercase ASCII letters. (The original Perl uses `tr/[A-Z]/[a-z]/`.
   The brackets in that `tr///` are literal no-op mappings; `A–Z` still
   fold to `a–z`.)
3. Delete characters outside `[A-Za-z0-9]` and whitespace. Apostrophes,
   hyphens, and Folio diacritics all disappear.
4. Split on one or more spaces.

Consequences that show up in the scores:

- `Alice's` → `alices` (a separate term from `alice`)
- `o'er` → `oer`
- `Moby-Dick` → `moby` and `dick` as two tokens if the hyphen is
  stripped in the middle of a join... actually `Moby-Dick` becomes
  `mobydick` because the hyphen is deleted, not replaced with a space.
- Speech prefixes like `Ham.` become `ham` after the period is removed.

The hyphen case is easy to miss: **deletion is not the same as splitting**.
`well-known` becomes `wellknown`, not `{well, known}`.

## Two-pass computation

The original project stores intermediate tables so you can inspect each
piece:

```
pass 1:  raw text  →  tf(t, d), df(t), idf(t)
pass 2:  tf(t, d) * idf(t)  →  tfidf(t, d)
```

That split is why `output/tf/carroll-alice.txt` still contains `a` with
a large TF, while `output/tfidf/carroll-alice.txt` lists `a` as `0`.
The local signal is real; the global signal is zero.

## Variants deliberately not used here

These come up in textbooks and search engines. They are **not** what
the checked-in `output/` files use.

| Variant | Typical formula | Why it is omitted here |
| --- | --- | --- |
| Raw TF | `count(t, d)` | Longer books would win automatically |
| Log TF | `1 + ln(count)` | Extra moving part for a toy collection |
| Smoothed IDF | `ln((N + 1) / (df + 1)) + 1` | Changes the Gutenberg numbers |
| BM25 | saturated TF + document-length prior | A different ranking function |
| Stopword lists | drop `the`, `and`, … | IDF already zeroes collection-wide terms |

If you want to experiment with a variant, change only
`examples/python/tfidf_lib.py` and leave the historical Perl +
`output/` tree as the blog-post snapshot.

## A three-term sketch

Suppose a collection of 18 documents and a 10,000-token novel.

| Term | count | df | tf | idf | tfidf |
| --- | ---: | ---: | ---: | ---: | ---: |
| `the` | 800 | 18 | 0.080 | `ln(18/18) = 0` | 0 |
| `whale` | 400 | 6 | 0.040 | `ln(18/6) ≈ 1.099` | ≈ 0.044 |
| `ahab` | 200 | 2 | 0.020 | `ln(18/2) ≈ 2.197` | ≈ 0.044 |

`whale` is more frequent in the book; `ahab` is rarer in the collection.
They can land at similar TF-IDF scores for different reasons. That
tradeoff is the whole method.

The actual Moby-Dick row in `output/tfidf/melville-moby_dick.txt` puts
`whale` slightly above `ahab`, which matches "more mentions, still
fairly rare in the other 17 files."

## Next

- How the Perl scripts implement this: [pipeline.md](pipeline.md)
- A fully worked 3-document collection: [worked-example.md](worked-example.md)
- How to read the TSV files: [output-formats.md](output-formats.md)
