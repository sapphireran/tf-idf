# tf-idf toy (Project Gutenberg)

Personal teaching repo for a 2012 blog toy: compute **tf\*idf** on a
pocket corpus of 18 public-domain books, then inspect which words
actually distinguish each file.

The original Perl scripts and their precomputed `output/` tables are
still here. This revision adds a walk-through of the math, a five-document
corpus you can read in one sitting, a Python implementation with tests,
and a ranking helper so the Gutenberg scores are not stuck in
alphabetical TSV dumps.

## Quick start

No third-party Python packages. From the repository root:

```bash
python3 examples/tfidf_toy.py --corpus examples/tiny-corpus --top 8
python3 -m unittest discover -s tests -v
python3 scripts/rank_precomputed_tfidf.py --only carroll-alice.txt --top 8
```

The tiny corpus should print `soup`, `roses`, `boat`, `oak`, and `hill`
as the top term of each vignette.

Perl, matching the original tokenizer more closely and still avoiding
`Text::CSV_XS`:

```bash
perl examples/tiny_tfidf.pl examples/tiny-corpus
```

The 2012 Gutenberg pipeline is two scripts. They expect to be launched
from the repository root and they rewrite `output/tf`, `output/df.txt`,
`output/idf.txt`, and `output/tfidf`:

```bash
perl tf-idf-values.pl
perl 'tf*idf-product.pl'    # quote the star or the shell will glob
```

`tf*idf-product.pl` needs the CPAN module `Text::CSV_XS` only because it
parses tab-separated lines. The teaching Perl example does not.

## Formula used here

For a term \(t\) in document \(d\):

\[
\mathrm{tf}(t,d) = \frac{\mathrm{count}(t,d)}{|d|}
\qquad
\mathrm{idf}(t) = \ln \frac{N}{\mathrm{df}(t)}
\qquad
\mathrm{tfidf}(t,d) = \mathrm{tf}(t,d)\cdot\mathrm{idf}(t)
\]

- \(|d|\) is the token count of that document after cleaning.
- \(N\) should be the number of documents. The checked-in Gutenberg
  tables use \(N = 18\). The original Perl assigns `$n = $#files` after
  `readdir`, which is easy to get wrong; see
  [docs/05-quirks-and-limitations.md](docs/05-quirks-and-limitations.md).
- \(\ln\) is the natural logarithm (Perl `log`, Python `math.log`).
- No add-one smoothing. A word that appears in every document gets
  \(\mathrm{idf} = 0\) and drops out of the ranking.

## Layout

```
gutenberg/                 18 public-domain texts (the original corpus)
output/                    precomputed df, idf, tf, and tf*idf tables
tf-idf-values.pl           pass 1: tf per file, plus df and idf
tf*idf-product.pl          pass 2: tf * idf per file
examples/                  tiny corpora + Python/Perl teaching clones
scripts/rank_precomputed_tfidf.py
tests/test_tfidf_toy.py
tests/test_rank_precomputed.py
docs/                      math, pipeline notes, worked examples
```

## Why the Gutenberg rankings look the way they do

The pipeline is a bag of words. It does not know about characters,
stage directions, or license headers. That is useful:

- **Austen and Chesterton** surface character names (`emma`, `syme`,
  `elinor`).
- **Alice** surfaces `alice`, then Wonderland creatures.
- **Moby-Dick** surfaces `whale` / `ahab` / `pequod`, with `whale` and
  `whales` counted separately because there is no stemmer.
- **Shakespeare** surfaces speaker tags (`macb`, `ham`, `bru`) and
  First Folio spellings (`haue`, `vs`).
- **The King James Bible** surfaces `unto` / `saith` / `thou` because
  those function words are common in that file and rarer elsewhere.
- One Chesterton file ranks `ebook`, which is leftover Gutenberg
  boilerplate, not a plot point.

Full tables: [docs/gutenberg-top-terms.md](docs/gutenberg-top-terms.md).

## Docs

1. [What TF-IDF is doing](docs/01-tfidf-in-plain-language.md)
2. [The original Perl pipeline](docs/02-original-pipeline.md)
3. [The 18-book corpus](docs/03-gutenberg-corpus.md)
4. [How to read `output/`](docs/04-interpreting-output.md)
5. [Quirks and limitations](docs/05-quirks-and-limitations.md)
6. [Hand-worked three-document example](docs/06-hand-worked-example.md)
7. [Five-vignette walk-through](docs/07-tiny-corpus-walkthrough.md)
8. [Gutenberg top-term tables](docs/gutenberg-top-terms.md)
9. [Formula cheat sheet](docs/formula-cheatsheet.md)
10. [TF versus TF-IDF](docs/08-tf-versus-tfidf.md)

## History

The first commit in this repository shipped the Gutenberg files, the
two Perl scripts, and the `output/` tables as a companion to a 2012
note on TF-IDF. A follow-up commit fixed how the number of files was
counted when computing IDF. The README was a single sentence pointing
at that write-up.

This tree keeps that toy intact and adds examples that can be checked
in a unit test.
