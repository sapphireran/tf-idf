# tf-idf

Personal notes and code for computing **term frequency–inverse document frequency** (TF-IDF) over a small Project Gutenberg collection.

The original two Perl scripts still do the heavy lift on the 18-book corpus in `gutenberg/`. This repo now also has:

- a written walkthrough of the formulas this pipeline actually uses
- a three-document toy corpus you can finish on paper
- a Python example that reproduces the same tokenization and scoring
- a reader for the checked-in `output/` tables, including top-term samples

Nothing here is a search-engine product. It is a personal lab notebook for the classic weighting scheme.

## What TF-IDF is doing here

Raw word counts are dominated by *the*, *and*, and *of*. TF-IDF keeps a word's rate inside one book and then down-weights words that appear in almost every book.

In this project:

1. **TF** is the word's count in a book divided by that book's token count (length-normalized term frequency).
2. **DF** is the number of books that contain the word at least once.
3. **IDF** is `ln(N / DF)` using the natural logarithm (`log` in Perl, `math.log` in Python).
4. **TF-IDF** is the product of those two numbers, written per word per book.

Words that appear in every book get `IDF = 0`, so their TF-IDF is zero even when TF is huge. That is why `the` tops `output/tf/carroll-alice.txt` and scores `0` in `output/tfidf/carroll-alice.txt`, while `alice` (DF 3), `gryphon` (DF 2), and `dormouse` (DF 1) rise to the top — high in-book TF still wins when IDF is only partly damped.

A full derivation, including a worked 3-document example, lives in [docs/algorithm.md](docs/algorithm.md).

## Repository layout

```
gutenberg/                 18 public-domain texts (one file = one document)
tf-idf-values.pl           tokenize, write per-doc TF, write corpus DF/IDF
tf*idf-product.pl          multiply TF × IDF into output/tfidf/
output/
  tf/<book>.txt            word<TAB>tf
  df.txt                   word, document frequency, book names
  idf.txt                  word<TAB>idf
  tfidf/<book>.txt         word<TAB>tf*idf
docs/                      formulas, corpus notes, pipeline, result reading
examples/
  tiny-corpus/             three short documents + hand-checked tables
  python/                  educational reimplementation and top-term reader
```

The Gutenberg files are listed, with token counts and distinctive terms, in [docs/corpus.md](docs/corpus.md).

## Run the original Perl pipeline

The scripts assume you are in the repository root. `tf-idf-values.pl` writes into `output/tf/`, `output/df.txt`, and `output/idf.txt`. `tf*idf-product.pl` reads those files and writes `output/tfidf/`.

```bash
# 1. term frequencies + document frequencies + inverse document frequencies
perl tf-idf-values.pl

# 2. per-document TF-IDF product
#    requires the Perl Text::CSV_XS module (tab-separated, despite the name)
perl 'tf*idf-product.pl'
```

The second script is named with a literal `*`. Quote the path so the shell does not glob it.

`tf*idf-product.pl` depends on [Text::CSV_XS](https://metacpan.org/pod/Text::CSV_XS). If it is missing:

```bash
cpanm Text::CSV_XS
# or: cpan Text::CSV_XS
```

Checked-in `output/` already contains a full run over the 18 books, so you can read results without rerunning anything. See [docs/pipeline.md](docs/pipeline.md) for what each script prints and which N the IDF formula used.

## Run the tiny worked example

The three files under `examples/tiny-corpus/docs/` are short enough to score by hand. Expected tables are in `examples/tiny-corpus/expected/`. The Python example regenerates them:

```bash
python3 examples/python/tfidf_example.py \
  --input-dir examples/tiny-corpus/docs \
  --output-dir /tmp/tiny-tfidf
```

Walkthrough: [examples/tiny-corpus/walkthrough.md](examples/tiny-corpus/walkthrough.md).

## Read the Gutenberg results

Highest TF-IDF terms from a checked-in output file:

```bash
python3 examples/python/extract_top_terms.py output/tfidf/carroll-alice.txt
python3 examples/python/extract_top_terms.py --tf output/tf/carroll-alice.txt
```

Sample ranked lists (Alice, Hamlet, Moby-Dick, Emma, and others) are in [docs/interpreting-results.md](docs/interpreting-results.md).

## Tokenization in one paragraph

Each line is squeezed to single spaces, lowercased, stripped of characters outside `[A-Za-z0-9]` plus whitespace, then split on runs of spaces. Empty tokens are dropped. There is no stemming, no stopword list, and no sentence splitter. Apostrophes disappear, so *Alice's* becomes `alices` and *I'm* becomes `im`. Details and edge cases: [docs/tokenization.md](docs/tokenization.md).

## Formula card

For term `t` in document `d` from a collection of `N` documents:

```
tf(t, d)  = count(t, d) / tokens(d)
df(t)     = |{ d : count(t, d) > 0 }|
idf(t)    = ln( N / df(t) )
tfidf(t,d)= tf(t, d) * idf(t)
```

This is **raw IDF**, not `ln(N / df) + 1` and not smoothed `ln((N + 1) / (df + 1)) + 1`. Collection-wide words therefore land at exactly zero.

The committed Gutenberg IDF table was produced with `N = 18` (one per `.txt` in `gutenberg/`). The Perl source uses `$#files` on a `readdir` listing, which is not the same number if `.` / `..` / `.DS_Store` are present. See [docs/known-quirks.md](docs/known-quirks.md).

## Docs index

| Document | Topic |
| --- | --- |
| [docs/README.md](docs/README.md) | Map of the notes |
| [docs/algorithm.md](docs/algorithm.md) | TF, DF, IDF, TF-IDF with arithmetic |
| [docs/tokenization.md](docs/tokenization.md) | Cleaning rules and side effects |
| [docs/pipeline.md](docs/pipeline.md) | How the two Perl scripts connect |
| [docs/corpus.md](docs/corpus.md) | The 18 Gutenberg files |
| [docs/output-formats.md](docs/output-formats.md) | TSV layouts |
| [docs/interpreting-results.md](docs/interpreting-results.md) | Ranked terms from the 18-book run |
| [docs/known-quirks.md](docs/known-quirks.md) | N, speaker tags, spelling, DF overlaps |
| [examples/README.md](examples/README.md) | Toy corpus, excerpts, and Python examples |
| [docs/further-experiments.md](docs/further-experiments.md) | Personal follow-up runs |

## License and sources

The scripts and notes in this repository are personal study material. The texts under `gutenberg/` are public-domain Project Gutenberg editions (or similarly redistributable plain-text literature). If you republish a derived table, keep the Gutenberg license headers that already sit at the top of several files.
