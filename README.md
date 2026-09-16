# tf-idf

A personal toy example for computing **term frequency × inverse document frequency** (`tf * idf`) over a tiny Project Gutenberg corpus.

The original 2012 scripts live at the repository root. They were written to accompany a blog walkthrough of the same calculation:

- [tfidf example and implementation details](http://nlp-stuff.blogspot.com/2012/09/tfidf-example-and-implementation-details.html) (the commit message for the first snapshot)
- Later rewrite: [Build your own search Engine](https://rutumulkar.com/ml-notes/information%20retrieval/lucene/2014/05/20/build-your-own-search-engine.html)

This checkout keeps those Perl scripts and their committed `output/` tables, and adds a longer personal study guide: the math, the pipeline, the quirks, a hand-worked three-document corpus, and small Python tools that reproduce the same formulas.

Nothing here is a search engine. It is a readable, fully inspectable `tf * idf` notebook in repository form.

## What is in this repo

| Path | Role |
| --- | --- |
| [`tf-idf-values.pl`](tf-idf-values.pl) | Original Perl pass: tokenize, write per-document `tf`, then corpus `df` / `idf` |
| [`tf*idf-product.pl`](tf*idf-product.pl) | Original Perl pass: multiply `tf * idf` into `output/tfidf/` |
| [`gutenberg/`](gutenberg/) | 18 public-domain books from the NLTK Gutenberg sample |
| [`output/`](output/) | Committed 2012 tables (`tf`, `df`, `idf`, `tfidf`) |
| [`docs/`](docs/) | Math, pipeline notes, corpus notes, output format, quirks, vectors |
| [`examples/tiny-corpus/`](examples/tiny-corpus/) | Three short documents you can score by hand |
| [`examples/python/`](examples/python/) | A small Python reimplementation and ranking / similarity tools |
| [`examples/worked/`](examples/worked/) | Distinctive-term readings of the Gutenberg tables |
| [`tests/`](tests/) | Checks for the tiny corpus, tokenizer, and committed-output readers |

## The formula this repo actually uses

For a token `t` in document `d`:

```
tf(t, d)  = count(t, d) / token_count(d)
idf(t)    = ln(N / df(t))
tfidf(t, d) = tf(t, d) * idf(t)
```

`N` is the number of documents in the corpus (18 books in `gutenberg/`). `df(t)` is the number of those documents that contain `t` at least once. The logarithm is the natural log.

A token that appears in every document has `idf = ln(1) = 0`, so its `tf * idf` is also 0. In this 18-book sample that list includes the usual function words (`the`, `and`, `of`) and a few content words that happen to be everywhere (`day`, `house`, `world`). That zero-IDF list is the closest thing this toy has to a stopword file.

See [docs/01-tfidf-from-scratch.md](docs/01-tfidf-from-scratch.md) for a derivation with numbers.

## Quick start

The original Perl path still works if you have `perl` and `Text::CSV_XS`:

```bash
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

The Python examples need only the standard library:

```bash
# Hand-worked three-document corpus
python3 examples/python/run_pipeline.py --input examples/tiny-corpus/docs --output /tmp/tiny-tfidf

# Rank distinctive terms from the committed Gutenberg tables
python3 examples/python/rank_terms.py --tfidf-dir output/tfidf --document carroll-alice.txt --top 15

# Pairwise cosine similarity over the committed Gutenberg tables
python3 examples/python/similarity.py --tfidf-dir output/tfidf --top 12
```

Run the checks with:

```bash
python3 -m unittest discover -s tests -v
```

## How to read the rest

1. [docs/00-overview.md](docs/00-overview.md) — map of the repository and the two-pass design
2. [docs/01-tfidf-from-scratch.md](docs/01-tfidf-from-scratch.md) — the math, including why `ln(N / df)` zeros out corpus-wide words
3. [docs/02-original-perl-pipeline.md](docs/02-original-perl-pipeline.md) — what the 2012 scripts do, line by line
4. [docs/03-gutenberg-corpus.md](docs/03-gutenberg-corpus.md) — the 18 books and why they are a useful toy
5. [docs/04-reading-the-output.md](docs/04-reading-the-output.md) — TSV layouts for `tf`, `df`, `idf`, `tfidf`
6. [docs/05-quirks-and-design-choices.md](docs/05-quirks-and-design-choices.md) — tokenization, `N`, empty tokens, Folio spellings
7. [docs/06-document-vectors-and-similarity.md](docs/06-document-vectors-and-similarity.md) — turning weights into cosine scores
8. [examples/tiny-corpus/walkthrough.md](examples/tiny-corpus/walkthrough.md) — every count and log computed on paper
9. [examples/worked/alice-in-wonderland.md](examples/worked/alice-in-wonderland.md) — reading Alice against the other 17 books

## Status

Personal study notes on top of a 2012 toy. The committed `output/` tables are treated as a frozen snapshot, including one known corrupted `idf` cell documented in the quirks note. The Python tools prefer the same formulas and the same tokenizer, but they count `N` from documents actually processed rather than from `$#files` after `readdir`.
