# tf-idf

Personal toy for computing **TF-IDF** over a small Project Gutenberg shelf.

The original Perl scripts walk eighteen public-domain books, write per-document
term frequencies, a collection-wide inverse document frequency table, and a
TF-IDF weight for every surviving token. This checkout also has a worked
four-document example and a few Python readers so the numbers can be inspected
without re-running the full shelf.

This is a learning repo, not a library. The tokenizer is intentionally naive,
the IDF formula is the textbook `ln(N / df)` used by `tf-idf-values.pl`, and
the precomputed `output/` tables are the ones checked in with the original
scripts.

## Formula used here

For term `t` in document `d`:

```
TF(t, d)     = count(t, d) / |d|
IDF(t)       = ln(N / df(t))
TF-IDF(t, d) = TF(t, d) * IDF(t)
```

`N` is the number of processed documents. For the Gutenberg shelf that is 18,
which is why a term that appears in exactly one book has IDF `ln(18) ≈ 2.89037`
in `output/idf.txt`. A term that appears in every book (`the`, `and`) has
IDF 0, so its TF-IDF weight is 0 everywhere.

A longer derivation, plus the same arithmetic on a four-sentence corpus, lives
in the docs listed below.

## Layout

```
gutenberg/                 18 Project Gutenberg texts
output/df.txt              document frequency + source filenames
output/idf.txt             ln(N / df) for every term
output/tf/<book>.txt       normalized term frequency per book
output/tfidf/<book>.txt    TF * IDF per book
tf-idf-values.pl           tokenize, write TF / DF / IDF
tf*idf-product.pl          multiply TF by IDF
docs/                      primer, corpus notes, pipeline, quirks
examples/                  tiny corpus, ranker, query tool
```

## Quick start

The Python examples need only the standard library:

```bash
# Work the four-document toy all the way to tables
python3 examples/tiny_tfidf.py
python3 examples/tiny_tfidf.py --check

# Rank distinctive terms in a precomputed Gutenberg table
python3 examples/rank_terms.py carroll-alice
python3 examples/rank_terms.py --top 8 --all

# Which books on the shelf are most about these words?
python3 examples/query_documents.py alice gryphon hatter
python3 examples/query_documents.py whale ahab pequod

# One term, every document that uses it
python3 examples/explain_term.py alice
```

The tiny corpus is original teaching text. It is small enough that
[docs/03-worked-example.md](docs/03-worked-example.md) works every term in
`tea-garden.txt` by hand.

## Original Perl scripts

```bash
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

`tf*idf-product.pl` needs [Text::CSV_XS](https://metacpan.org/pod/Text::CSV_XS)
and quotes around the filename because of the `*` character. The scripts write
into `output/` and will overwrite the checked-in tables. See
[docs/04-perl-pipeline.md](docs/04-perl-pipeline.md) before regenerating
anything.

## Docs

| Note | What it covers |
| --- | --- |
| [01-tf-idf-primer.md](docs/01-tf-idf-primer.md) | TF, DF, IDF, and this repo's exact variant |
| [02-gutenberg-corpus.md](docs/02-gutenberg-corpus.md) | The 18 texts and their distinctive terms |
| [03-worked-example.md](docs/03-worked-example.md) | Hand calculation on `examples/tiny-corpus` |
| [04-perl-pipeline.md](docs/04-perl-pipeline.md) | What each Perl script writes |
| [05-reading-the-output.md](docs/05-reading-the-output.md) | How to read `df`, `idf`, `tf`, `tfidf` |
| [06-querying-and-ranking.md](docs/06-querying-and-ranking.md) | Rank terms and score a query |
| [07-tokenization-and-quirks.md](docs/07-tokenization-and-quirks.md) | Fused tokens, speaker tags, the `N` off-by-one |

## Corpus

The shelf is a mixed handful of Austen, Blake, the King James Bible, Bryant,
Burgess, Carroll, Chesterton, Edgeworth, Melville, Milton, Shakespeare, and
Whitman. File sizes and the actual top TF-IDF terms from `output/tfidf/` are
catalogued in [docs/02-gutenberg-corpus.md](docs/02-gutenberg-corpus.md).

Texts are public-domain Project Gutenberg transcriptions. Shakespeare files
keep early-modern spelling (`haue`, `selfe`) and speaker abbreviations
(`ham`, `macb`), which is why those strings outrank `hamlet` and `macbeth`.
