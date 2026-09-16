# Overview

This repository is a personal, fully checked-in `tf * idf` lab. The original snapshot is two Perl scripts plus the 18-book NLTK Gutenberg sample and the tables those scripts wrote in 2012. The `docs/` and `examples/` trees are a later expansion so the same calculation can be read without reconstructing it from a blog post and a pair of scripts.

## Two passes, four artifacts

The original pipeline is deliberately split:

```
gutenberg/*.txt
        │
        ▼
 tf-idf-values.pl
        │
        ├── output/tf/<book>.txt     raw normalized term frequencies
        ├── output/df.txt            document frequency + posting list
        └── output/idf.txt           ln(N / df(t))
                │
                ▼
     tf*idf-product.pl
                │
                └── output/tfidf/<book>.txt
```

Pass 1 walks every book, builds a per-document term-frequency map, and a corpus-wide document-frequency map. Pass 2 is a join: for each token in each `tf` file, multiply by the matching `idf`.

That split is useful for study. You can open `output/tf/carroll-alice.txt` and see that `alice` is common *inside* Alice. You can open `output/idf.txt` and see that `alice` is rare *across* the 18 books (`df = 3`). The product in `output/tfidf/carroll-alice.txt` is the interesting number.

## What this is for

- Walking through `tf`, `df`, `idf`, and `tf * idf` with real files
- Seeing why stopwords vanish without a stopword list
- Seeing why character names dominate a book's ranking
- Comparing a Perl 5 implementation to a short Python rewrite
- Computing cosine similarity on the same weights the blog post used for document vectors

## What this is not

- Not a production indexer
- Not a stemmer, lemmatizer, or phrase detector
- Not a search engine (there is no query parser, no inverted-index runtime, no BM25)
- Not a cleaned literary corpus (Gutenberg headers, Bible verse numbers, and Folio spellings are left in)

The value of the toy is that every choice is visible. If a token looks strange (`haue`, `alices`, `1865`, `macb`), the quirks note explains how it got there.

## Suggested path

If you want the shortest path from zero to a number you computed yourself, start with [../examples/tiny-corpus/walkthrough.md](../examples/tiny-corpus/walkthrough.md). Those three documents have seven tokens each. You can finish the arithmetic before you open the Gutenberg tables.

If you want to understand the 2012 snapshot, read the pipeline note, then the output-format note, then one of the worked Gutenberg readings.

If you want to reuse the weights, use the Python tools in `examples/python/`. They read either a directory of `.txt` files or the committed `output/tfidf/` tables.
