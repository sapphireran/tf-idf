# Personal TF-IDF research notebook

Personal study notes for classical term weighting, built around a small
public-domain Gutenberg shelf and a 2012 Perl toy that computed
term frequency × inverse document frequency for those texts.

This repository is **personal research only**. It is not a product, not a
search engine, and not a workplace artifact. The original Perl scripts and
checked-in `output/` tables are a historical snapshot. The `notebook/`,
`examples/`, and `tfidf/` tree is a later personal lab layered on top of
that snapshot so the experiment can be re-run, explained, and compared
without depending on `Text::CSV_XS`.

## What is here

| Path | What it is |
| --- | --- |
| `notebook/` | Numbered lab notes: derivation, variants, ranking, tokenization, corpus observations |
| `examples/tiny_corpus/` | Four hand-written paragraphs used for fully worked arithmetic |
| `tfidf/` | Stdlib Python study library (`python3 -m tfidf`) |
| `tests/` | Unit tests against the tiny corpus and closed-form weights |
| `gutenberg/` | Eighteen Project Gutenberg texts (public domain) |
| `tf-idf-values.pl`, `tf*idf-product.pl` | Original 2012 Perl pipeline |
| `output/` | Historical TF / DF / IDF / TF-IDF tables from that pipeline |

Start at [`notebook/00-index.md`](notebook/00-index.md).

## Quick lab commands

From the repository root, no install required:

```bash
# Fully worked tiny-corpus arithmetic
python3 -m tfidf demo

# Distinctive terms in one Gutenberg text
python3 -m tfidf top --doc gutenberg/carroll-alice.txt --k 12

# Rank the Gutenberg shelf for a query
python3 -m tfidf rank "white whale" --corpus gutenberg --k 5

# Same query under several IDF smoothings
python3 -m tfidf compare "white whale" --corpus gutenberg

# Explain one term in one document
python3 -m tfidf explain whale --doc gutenberg/melville-moby_dick.txt
```

Run the personal test suite:

```bash
python3 -m unittest discover -s tests -v
```

## Provenance

The Perl toy and first README were committed in 2012–2015 as a companion
to a short public blog post on computing TF-IDF over Gutenberg files
(`nlp-stuff.blogspot.com`, 2012). This notebook keeps that history in
place and treats the scripts as a specimen: useful, slightly quirky, and
worth annotating. Gutenberg files remain public-domain transcriptions;
see each file's bracketed title line.

## Scope I am deliberately not adding

- No crawlers, no web index, no production retrieval stack
- No workplace datasets, tickets, or proprietary text
- No claim that these weights beat BM25, embeddings, or a real IR system

The point is to understand the arithmetic and the failure modes on a
shelf of books I can read.
