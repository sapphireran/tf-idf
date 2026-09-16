# Personal TF-IDF on a Gutenberg toy corpus

This is a **personal study repo**, not a product and not company code.

In 2012 I wrote two small Perl scripts that compute term frequency (TF),
document frequency (DF), inverse document frequency (IDF), and the
product TF\*IDF over a handful of public-domain [Project Gutenberg](https://www.gutenberg.org/)
texts. The original write-up lived at
`http://nlp-stuff.blogspot.com/2012/09/tfidf-example-and-implementation-details.html`
(the post is gone; this checkout is the surviving companion).

The scripts are still here, along with the tables they produced. This
checkout also has a from-scratch Python benchmark I use to time the same
arithmetic, explain the tokenizer, and check that a reimplementation
still matches the checked-in numbers.

If you want the short version: each book is treated as one document,
each token's score in that book is

```
tf(term, doc)  = count(term, doc) / tokens_in_doc
idf(term)      = ln(N / df(term))
tfidf          = tf * idf
```

where `N` is the number of books and `df(term)` is how many books
contain the term at least once. Words that appear in every book get
`idf = ln(1) = 0`, which is why `the` / `and` / `a` drop out of the
interesting end of the ranking.

## What is in this checkout

| Path | Role |
| --- | --- |
| `gutenberg/` | 18 public-domain texts (plus a leftover `.DS_Store`) |
| `tf-idf-values.pl` | Walk the corpus, write per-doc TF and global DF / IDF |
| `tf*idf-product.pl` | Multiply each TF by the matching IDF |
| `output/tf/` | Checked-in TF tables from the Perl pass |
| `output/df.txt`, `output/df-sorted.txt` | Term → document-frequency |
| `output/idf.txt` | Term → `ln(N / df)` |
| `output/tfidf/` | Checked-in TF\*IDF tables |
| `scripts/tfidf_benchmark.py` | Personal Python benchmark + commentary |
| `docs/` | Longer notes on the math, the Perl, and the benchmark |

Nothing here is a library. There is no installer, no package, and no
shared utility pulled in from anywhere else. The Python script uses
the standard library only.

## Corpus at a glance

Eighteen books, roughly 11 MB of raw text, about 57k distinct tokens
after the 2012 tokenizer (lowercase, strip punctuation, split on
spaces). The largest file is the King James Bible; the smallest is
Blake's poems. A file-by-file listing lives in
[`docs/corpus.md`](docs/corpus.md).

The tokenizer is deliberately crude. Apostrophes are deleted, so
`don't` becomes `dont`. There is no stemmer and no stop-word list.
Stop words are handled implicitly: they appear in every document, so
their IDF is zero.

## Formulas this repo actually uses

There are many textbook variants of TF-IDF. **This checkout uses the
plain one from the 2012 scripts**, not sklearn's default, not BM25,
and not a smoothed IDF.

1. **Term frequency** is a length-normalized count:
   `tf = raw_count / word_count`.
2. **Document frequency** is binary per file: a term counts once in a
   book even if it appears a thousand times there.
3. **IDF** is `ln(N / df)`. Perl's `log` is the natural log; Python's
   `math.log` is the same. Base 10 would only rescale the numbers.
4. **TF-IDF** is the product of those two scalars. There is no cosine
   normalization of the document vector afterward.

Two implementation details change the numbers if you are trying to
reproduce `output/` exactly. Both are documented in
[`docs/algorithm.md`](docs/algorithm.md) and
[`docs/original-perl.md`](docs/original-perl.md):

- `word_count` in `tf-idf-values.pl` is incremented **before** empty
  tokens are skipped, so leftover empty fields from `split` still
  inflate the TF denominator.
- The Perl script sets `my $n = $#files` (last index of `readdir`,
  including `.` and `..`). The tables already in `output/idf.txt`
  match `N = 18` (the real document count), which is
  `ln(18) ≈ 2.89037175789616` for terms that appear in one book.
  Rerunning the Perl as-is on this directory listing will **not**
  reproduce those IDF values.

The personal benchmark defaults to `N = number of documents` so it
can compare against the checked-in `output/` files. Pass
`--n-mode perl-last-index` if you want the live Perl quirk instead.

## Running the original Perl

From the repository root, with the `gutenberg/` and `output/`
directories already present:

```bash
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

The second script needs [Text::CSV_XS](https://metacpan.org/pod/Text::CSV_XS)
because it parses the TF tables as tab-separated rows. The first
script is core Perl only.

Both scripts write under `output/` and will overwrite the checked-in
tables. That is useful if you want a fresh Perl run; it is noisy if
you only wanted to read the old results.

## Running the personal benchmark

```bash
python3 scripts/tfidf_benchmark.py
python3 scripts/tfidf_benchmark.py --self-test
python3 scripts/tfidf_benchmark.py --repeats 3 --top 10 --compare-output
```

`--self-test` runs a three-document toy corpus whose TF-IDF values
are written out by hand in [`docs/algorithm.md`](docs/algorithm.md).
`--compare-output` diffs the recomputed IDF / TF / TF-IDF numbers
against the files in `output/`.

A full flag list and a guide to reading the report are in
[`docs/benchmark.md`](docs/benchmark.md).

## Suggested reading order

1. This README, so the layout and the formula are in your head.
2. [`docs/algorithm.md`](docs/algorithm.md) — worked example and
   tokenizer pipeline.
3. [`docs/original-perl.md`](docs/original-perl.md) — what each
   script writes, and the two quirks above.
4. [`docs/benchmark.md`](docs/benchmark.md) — how to time a pass and
   how to tell that the Python matches the checked-in tables.
5. `scripts/tfidf_benchmark.py` — the same story in code, with
   comments next to each step.

## What this is not

- Not a search engine.
- Not a sklearn / gensim wrapper.
- Not a stemmer, lemmatizer, or language-id tool.
- Not company code, and not a place to drop company code.

The interesting part of TF-IDF on this corpus is qualitative: after
the common words zero out, *Alice* surfaces `alice`, *Moby-Dick*
surfaces `whale` / `ahab`, and the Bible surfaces names and
theological vocabulary. The benchmark's top-term table is there so
you can see that without opening the raw TSV files.
