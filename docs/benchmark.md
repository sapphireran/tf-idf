# Personal TF-IDF benchmark

`scripts/tfidf_benchmark.py` is a from-scratch, standard-library-only
Python script. It is personal study code. It does not wrap sklearn,
NLTK, or any company library.

The script exists to answer three questions I keep asking of this
toy:

1. Do I still understand the 2012 formula well enough to recompute
   every cell in `output/`?
2. Where does a naive in-memory pass spend its time on 18 Gutenberg
   files (~12 MB, ~2.1 million tokens)?
3. After the common words zero out, which terms actually rank as
   "this book, not the other seventeen"?

## Commands

From the repository root. Python 3.9+ is enough (`list[str]` hints,
`argparse.BooleanOptionalAction`). 3.12 is what I run here.

```bash
# Default: classic IDF, N = 18, compare against output/, print top 8.
python3 scripts/tfidf_benchmark.py

# Postcard corpus from docs/algorithm.md. No Gutenberg I/O.
python3 scripts/tfidf_benchmark.py --self-test

# More stable timings, more keywords, write a copy of the report.
python3 scripts/tfidf_benchmark.py --repeats 5 --top 10 \
    --write-report reports/benchmark.txt \
    --write-json reports/benchmark.json

# Shadow a live Perl run (N = $#files) instead of the checked-in tables.
python3 scripts/tfidf_benchmark.py --n-mode perl-last-index --no-compare-output

# See what a non-zeroing IDF does to the ranking (spoiler: "the").
python3 scripts/tfidf_benchmark.py --variant sklearnish --no-compare-output --top 5
```

`reports/` is gitignored. `--self-test` exits `1` if any postcard
cell drifts. The default Gutenberg run exits `1` only when
`--variant classic` and `--n-mode documents` disagree with `output/`
beyond `1e-12`.

## What each stage is timing

| Stage | Work |
| --- | --- |
| `read_files` | `os.listdir` + `read_bytes` + latin-1 decode |
| `tokenize_and_count` | Per-line Perl-compatible cleanup, `%tf`, `%df` |
| `compute_idf` | One `ln(N / df)` (or other variant) per vocab term |
| `compute_tfidf` | `tf * idf` for each term that occurs in each book |
| `rank_top_terms` | Sort each book's scores descending |

On this machine, a typical best-of-3 classic pass looks like:

| Stage | Ballpark |
| --- | --- |
| `read_files` | ~4 ms |
| `tokenize_and_count` | ~1.08 s |
| `compute_idf` | ~6 ms |
| `compute_tfidf` | ~17 ms |
| `rank_top_terms` | ~60 ms |
| **TOTAL** | **~1.16 s** |

Almost all of the time is the tokenizer. That is the expected shape
for a 2-million-token bag-of-words with a ~57k vocabulary: the
arithmetic is a thin loop over types, not over tokens. If you change
the tokenizer (Unicode splits, stemming, stop lists) this is the
stage that will move. If you only change the IDF formula, it will
not.

`--repeats` runs the whole pipeline independently and prints the
fastest total plus the mean. It is a coarse laptop timer, not a
microbenchmark. Close the browser, do not treat the third decimal
as science.

## Corpus numbers the script should print

These are properties of the checked-in `gutenberg/` bytes plus the
2012 tokenizer, so they should stay still unless you edit either:

| Stat | Value |
| --- | --- |
| Documents | 18 |
| Raw bytes | 11,793,318 |
| Perl `word_count` (split fields) | 2,143,747 |
| Kept tokens | 2,134,514 |
| Empty split fields | 9,233 |
| Vocabulary | 57,368 |
| Terms with `df = 1` | 36,887 |
| Terms with `df = 18` (classic IDF 0) | 221 |

The 9,233 empty fields are leading-whitespace lines. They only
affect the TF denominator. They are why a "just split on words"
reimplementation misses `output/tf/` even when the IDF table
matches.

221 terms appear in every book. Classic IDF sends them to zero.
That is the stop-word list this toy never wrote down.

## Gold comparison

Default `--compare-output` diffs three tables:

- `output/idf.txt` versus recomputed IDF
- every `output/tf/<file>` versus `count / word_count`
- every `output/tfidf/<file>` versus the product

A passing run on this tree prints something like:

```
Gold comparison against output/  (abs tol 1e-12)
  idf     ok   shared=57368   missing=0  extra=0  mismatches=0  max|Δ|=4.9e-15
  tf      ok   shared=137344  missing=0  extra=0  mismatches=0  max|Δ|=5.0e-17
  tfidf   ok   shared=137344  missing=0  extra=0  mismatches=0  max|Δ|=8.8e-17
```

`137344` is the sum of per-document vocabularies, not the global
57k: the same term is compared once per book it occurs in.

One gold IDF cell is corrupt (`thatyou` ends with a stray `y`).
The loader strips that letter. See
[`original-perl.md`](original-perl.md).

`--variant` values other than `classic`, and `--n-mode perl-last-index`,
will disagree with `output/` on purpose. The script then refuses to
call the diff a failure. Use `--no-compare-output` if you do not
want the extra I/O.

## How to read the top-term lists

Sort is `(score descending, term ascending)`. A high score still
means "common in this book, rare in the other seventeen."

Things that work as a demo:

- *Emma* → `emma`, `harriet`, `weston`, `knightley`
- *Alice* → `alice`, `gryphon`, `dormouse`, `duchess`, `hatter`
- *Moby-Dick* → `whale`, `ahab`, `sperm`, `stubb`, `queequeg`
- *Thursday* → `syme`, `gregory`, `marquis`
- Burgess → `buster` (very high TF in a short file)

Things that look like bugs and are not:

- Shakespeare speaker codes (`ham`, `macb`, `bru`, `cassi`). The
  texts print abbreviated speech prefixes. Those strings are almost
  unique to one play, so IDF is huge and they beat `hamlet` /
  `macbeth` themselves.
- Early-modern spellings (`haue`, `vpon`, `vs`, `passd`, `oer`).
  The tokenizer does not normalize them to modern English, so
  `have` in Chesterton and `haue` in Shakespeare are different
  terms. `have` can therefore pick up a non-zero IDF and leak into
  a modern book's top ten.
- `ebook` in *The Ball and the Cross*. A Gutenberg header token
  that happens not to appear in the other 17 files.
- *Paradise Lost* ranking `thee` / `thou` / `thy`. Those pronouns
  are common in Milton and the Bible but not in Austen, so they
  are not collection-wide stop words here.
- *Leaves of Grass* ranking `o`. Vocative `O` survives as a single
  letter and is characteristic of Whitman in this mix.

sklearn-style IDF (`--variant sklearnish`) does **not** zero the
221 shared terms. The top of *Emma* becomes `to` / `the`. That is
the most compact argument I know for why the 2012 script used
`ln(N / df)` without a plus-one.

## `--self-test`

Recomputes the three-document postcard:

```
doc_a: the cat sat
doc_b: the dog sat
doc_c: the cat
```

and checks four IDF values plus `tfidf(cat, A)` and `tfidf(dog, B)`
against the hand numbers in [`algorithm.md`](algorithm.md). It also
asserts that `the` is exactly `0.0` in every document, not a
tiny leftover float.

Run this first when you touch the tokenizer or the IDF function.
It is fast enough to be a habit.

## What this script will not do

- It will not overwrite `output/`. The Perl scripts do that.
- It will not stem, lemmatize, or drop stop words.
- It will not compute cosine similarity between books.
- It will not download new Gutenberg texts.
- It will not import anything outside the Python standard library.

If you want a new experiment, add a flag and a comment next to it.
Keep the default path equal to the 2012 tables so `--compare-output`
stays a regression test for the toy, not a moving target.
