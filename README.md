# tf-idf

Personal toy project for computing **term frequency–inverse document frequency** (TF-IDF) on a small Project Gutenberg sample.

The original Perl scripts and precomputed `output/` tables come from a 2012 walkthrough
([commit `a170430`](https://github.com/sapphireran/tf-idf/commit/a170430210315606251173e6823cff3689460e3b)).
This checkout keeps those scripts as-is and adds documentation plus smaller examples you can
finish by hand.

## What this repo contains

| Path | Role |
| --- | --- |
| `tf-idf-values.pl` | Walk `gutenberg/`, write per-document TF and corpus DF / IDF |
| `tf*idf-product.pl` | Multiply each document's TF by the shared IDF table |
| `gutenberg/` | 18 public-domain texts (plus a leftover `.DS_Store`) |
| `output/tf/` | Normalized term frequency, one TSV per document |
| `output/df.txt` | Document frequency and the filenames that contain each term |
| `output/idf.txt` | `ln(N / df)` for each term, with `N = 18` in the checked-in tables |
| `output/tfidf/` | Per-document TF × IDF |
| `docs/` | Formulas, pipeline notes, corpus catalog, tokenizer quirks |
| `examples/` | A 4-document hand example plus readings of the Gutenberg scores |

## Formulas used here

This project uses **raw relative TF** and **natural-log IDF** with no smoothing:

```
tf(t, d)  = count(t, d) / tokens(d)
idf(t)    = ln( N / df(t) )
tfidf(t,d)= tf(t, d) * idf(t)
```

- `count(t, d)` is the number of times term `t` occurs in document `d` after the
  tokenizer in `docs/tokenizer-and-quirks.md`.
- `tokens(d)` is the document length in those same tokens.
- `df(t)` is the number of documents that contain `t` at least once.
- `N` is the number of documents in the corpus. The checked-in Gutenberg tables
  were generated with `N = 18` (`ln(18) ≈ 2.89037` for a term that appears in
  exactly one file).

A term that appears in every document gets `idf = ln(1) = 0`, so its TF-IDF is
always `0`. That is why `the`, `and`, and `a` vanish in `output/tfidf/` even
though they dominate the raw counts.

There is **no** add-one / `log(N / (df+1))` smoothing, no `log(1 + tf)` sublinear
TF, and no L2 document-length normalization beyond dividing by `tokens(d)`.

Walk through the algebra with numbers in [`docs/tf-idf-explained.md`](docs/tf-idf-explained.md).
A four-document corpus you can compute on paper is in
[`examples/tiny-corpus/`](examples/tiny-corpus/).

## How to read the Gutenberg results

Distinctive proper names and setting words rise to the top. Function words that
occur in all 18 files drop to zero. A few Folio speech prefixes (`macb`, `ham`,
`bru`) outrank the character names they stand for.

| Document | Highest TF-IDF terms (checked-in `output/tfidf/`) |
| --- | --- |
| `austen-emma.txt` | `emma`, `harriet`, `weston`, `knightley` |
| `austen-persuasion.txt` | `elliot`, `wentworth`, `anne`, `musgrove` |
| `austen-sense.txt` | `elinor`, `marianne`, `dashwood`, `jennings` |
| `melville-moby_dick.txt` | `whale`, `ahab`, `sperm`, `stubb` |
| `carroll-alice.txt` | `alice`, `gryphon`, `dormouse`, `duchess` |
| `shakespeare-macbeth.txt` | `macb`, `haue`, `macbeth`, `macd` |
| `burgess-busterbrown.txt` | `buster`, `browns`, `joe`, `blacky` |

Longer rankings and why speaker tags win are in
[`examples/gutenberg-top-terms.md`](examples/gutenberg-top-terms.md) and
[`examples/shakespeare-speaker-tags.md`](examples/shakespeare-speaker-tags.md).

## Running the original Perl scripts

The checked-in `output/` already contains a full run. Recomputing the Gutenberg
collection is optional and slow: `bible-kjv.txt` alone is about 821k words, and
the whole sample is about 2.1 million tokens.

```bash
# 1) per-document TF + corpus DF/IDF
perl tf-idf-values.pl

# 2) TF * IDF  (needs the Text::CSV_XS module)
perl 'tf*idf-product.pl'
```

`tf-idf-values.pl` uses only core Perl. `tf*idf-product.pl` parses the TSV files
with [`Text::CSV_XS`](https://metacpan.org/pod/Text::CSV_XS):

```bash
cpanm Text::CSV_XS
# or: sudo apt-get install libtext-csv-xs-perl
```

Both scripts write under `output/` and print `Processing file: ...` as they go.
They do not take command-line arguments; paths are hard-coded.

`tf-idf-values.pl` sets `N` from `$#files` on the raw `readdir` list, which
includes `.` and `..`. The tables in this repo match `N = 18` (the `.txt`
count). See [`docs/pipeline.md`](docs/pipeline.md) before treating a fresh run
as bit-identical to `output/`.

## Running the tiny example (no Perl modules)

```bash
python3 examples/tiny-corpus/compute_tfidf.py \
  --corpus examples/tiny-corpus/docs \
  --output examples/tiny-corpus/output

python3 examples/tiny-corpus/compute_tfidf.py --verify
```

The verifier checks rankings and a handful of exact values from
[`examples/hand-calculation.md`](examples/hand-calculation.md).

To reprint the Gutenberg top terms from the checked-in tables:

```bash
python3 examples/rank_top_terms.py --dir output/tfidf --k 8
```

## Documentation map

- [`docs/tf-idf-explained.md`](docs/tf-idf-explained.md) — TF, DF, IDF, TF-IDF, and common variants this repo does **not** use
- [`docs/pipeline.md`](docs/pipeline.md) — what each Perl script reads and writes
- [`docs/corpus.md`](docs/corpus.md) — the 18 Gutenberg files and sizes
- [`docs/interpreting-output.md`](docs/interpreting-output.md) — TSV layout and how to sort scores
- [`docs/tokenizer-and-quirks.md`](docs/tokenizer-and-quirks.md) — preprocessing, `N`, and data nits
- [`docs/idf-selected-terms.md`](docs/idf-selected-terms.md) — selected `df` / `idf` values from `output/`
- [`examples/README.md`](examples/README.md) — index of worked examples
- [`examples/reproducing-a-gutenberg-score.md`](examples/reproducing-a-gutenberg-score.md) — `tf * idf` identity checks on the checked-in tables

## Corpus credit

The texts under `gutenberg/` are Project Gutenberg transcriptions of public-domain
works. Filenames follow `author-title.txt`. One Chesterton file still carries
Project Gutenberg boilerplate, which is why `ebook` and `gutenberg` appear as
high-IDF terms in `chesterton-ball.txt`.
