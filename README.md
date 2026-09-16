# tf-idf

Personal toy example for computing **term frequency × inverse document frequency** (`tf * idf`) over the 18-book [NLTK Project Gutenberg](https://www.nltk.org/nltk_data/) selection.

The original Perl scripts and precomputed `output/` tables date from 2012. This repository now also has a walkthrough of the math, a hand-sized corpus you can score with a pencil, a small Python reimplementation, and notes on how to read the published Gutenberg results.

This is personal / educational material only. It is not a search-engine library and it is not production ranking code.

## Why this exists

Documents represented as `tf * idf` vectors are a classic starting point for:

- keyword-style search
- document similarity (cosine of the vectors)
- a first look at why stopwords drop out of a ranking without an explicit stoplist

The original write-up is [Build your own search Engine](https://rutumulkar.com/ml-notes/information%20retrieval/lucene/2014/05/20/build-your-own-search-engine.html) (2014), which grew out of the 2012 notes linked from the first commit:

`http://nlp-stuff.blogspot.com/2012/09/tfidf-example-and-implementation-details.html`

## Formula used here

For term \(t\) in document \(d\):

\[
\mathrm{tf}(t, d) = \frac{\mathrm{count}(t, d)}{|d|}
\qquad
\mathrm{idf}(t) = \ln\frac{N}{\mathrm{df}(t)}
\qquad
\mathrm{tfidf}(t, d) = \mathrm{tf}(t, d) \times \mathrm{idf}(t)
\]

- \(|d|\) is the token count of document \(d\) after the regex cleanup described below.
- \(N\) in the **published** `output/` tables is **18** (one per book).
- \(\mathrm{df}(t)\) is the number of books that contain \(t\) at least once.
- \(\ln\) is the natural log (Perl's `log`, Python's `math.log`).

A term that appears in every book has \(\mathrm{idf} = \ln(18/18) = 0\), so its `tf * idf` is also 0. That is how `the`, `and`, `of`, `if`, and `when` disappear from the Gutenberg rankings without a hand-written stoplist.

Worked arithmetic for a four-document kitchen / trail / music corpus is in [`examples/tiny-corpus/worked-example.md`](examples/tiny-corpus/worked-example.md). Implementation caveats (directory counting, empty tokens, one corrupt IDF line) are in [`docs/formula-and-implementation-notes.md`](docs/formula-and-implementation-notes.md).

## Repository map

| Path | What it is |
| --- | --- |
| [`gutenberg/`](gutenberg/) | 18 public-domain books (plus a leftover `.DS_Store`) |
| [`tf-idf-values.pl`](tf-idf-values.pl) | Tokenize, write per-book `tf`, then corpus `df` / `idf` |
| [`tf*idf-product.pl`](tf*idf-product.pl) | Multiply each book's `tf` by the global `idf` |
| [`output/tf/`](output/tf/) | Precomputed term frequencies |
| [`output/df.txt`](output/df.txt) | Document frequency plus the book list for each term |
| [`output/idf.txt`](output/idf.txt) | Inverse document frequency |
| [`output/tfidf/`](output/tfidf/) | Precomputed `tf * idf` |
| [`docs/`](docs/) | Math, pipeline, and how to read the tables |
| [`examples/`](examples/) | Tiny corpus, Python toy, ranking and similarity scripts |

## The 18 books

| File | Work |
| --- | --- |
| `austen-emma.txt` | Jane Austen, *Emma* |
| `austen-persuasion.txt` | Jane Austen, *Persuasion* |
| `austen-sense.txt` | Jane Austen, *Sense and Sensibility* |
| `bible-kjv.txt` | King James Bible |
| `blake-poems.txt` | William Blake, poems |
| `bryant-stories.txt` | Sara Cone Bryant, stories |
| `burgess-busterbrown.txt` | Thornton Burgess, *The Adventures of Buster Bear* (NLTK filename) |
| `carroll-alice.txt` | Lewis Carroll, *Alice's Adventures in Wonderland* |
| `chesterton-ball.txt` | G. K. Chesterton, *The Ball and the Cross* |
| `chesterton-brown.txt` | G. K. Chesterton, Father Brown stories |
| `chesterton-thursday.txt` | G. K. Chesterton, *The Man Who Was Thursday* |
| `edgeworth-parents.txt` | Maria Edgeworth, *The Parent's Assistant* |
| `melville-moby_dick.txt` | Herman Melville, *Moby-Dick* |
| `milton-paradise.txt` | John Milton, *Paradise Lost* |
| `shakespeare-caesar.txt` | Shakespeare, *Julius Caesar* |
| `shakespeare-hamlet.txt` | Shakespeare, *Hamlet* |
| `shakespeare-macbeth.txt` | Shakespeare, *Macbeth* |
| `whitman-leaves.txt` | Walt Whitman, *Leaves of Grass* |

Together they are about 257k lines. The King James Bible is by far the largest file; Blake is the smallest.

## Tokenization (shared by the Perl scripts)

Each line is cleaned with the same four steps the 2014 post highlights:

```perl
chomp($txt);                      # drop the newline
$txt =~ s/[\h\v]+/ /g;            # collapse whitespace
$txt =~ tr/[A-Z]/[a-z]/;          # lowercase
$txt =~ s/[^a-zA-Z\d\s]//g;       # drop punctuation and other symbols
```

Tokens are then `split` on spaces. Contractions become new spellings (`I'm` → `im`, `Alice's` → `alices`). Early-modern spellings stay as printed (`haue`, `vpon`, `selfe`), which is why those forms rank highly in the Shakespeare files.

The Python toy in `examples/python/` applies the same cleanup so its Gutenberg rankings can be compared with `output/tfidf/`.

## Quick start

### Read the published tables

You do not have to rerun anything to study the original experiment. The `output/` directory already has `tf`, `df`, `idf`, and `tf * idf` for every book.

```bash
# highest-weighted terms in Alice, using the committed table
python3 examples/python/rank_terms.py --from-table output/tfidf/carroll-alice.txt --top 15
```

### Score the tiny corpus (no Gutenberg required)

```bash
python3 examples/python/tfidf_toy.py examples/tiny-corpus/documents --write-dir examples/tiny-corpus/output
python3 examples/python/rank_terms.py --from-table examples/tiny-corpus/output/tfidf/01-bakery-morning.txt
python3 examples/python/similar_docs.py --table-dir examples/tiny-corpus/output/tfidf
```

Expected numbers are written out in [`examples/tiny-corpus/expected-results.md`](examples/tiny-corpus/expected-results.md).

### Rank a Gutenberg book from the source text

```bash
python3 examples/python/tfidf_toy.py gutenberg --write-dir /tmp/gutenberg-tfidf
python3 examples/python/rank_terms.py --from-table /tmp/gutenberg-tfidf/tfidf/melville-moby_dick.txt --top 20
python3 examples/python/similar_docs.py --table-dir /tmp/gutenberg-tfidf/tfidf --top-pairs 12
```

### Original Perl pipeline

```bash
perl tf-idf-values.pl          # writes output/tf/*, output/df.txt, output/idf.txt
perl 'tf*idf-product.pl'       # writes output/tfidf/*
```

`tf*idf-product.pl` needs [Text::CSV_XS](https://metacpan.org/pod/Text::CSV_XS) (`cpanm Text::CSV_XS`). `tf-idf-values.pl` is stdlib-only. See [`docs/formula-and-implementation-notes.md`](docs/formula-and-implementation-notes.md) before expecting a rerun to match `output/` bit-for-bit: the Perl `N` is `$#files` from `readdir`, which is not the same as “18 books”.

## Documentation index

1. [What tf * idf is doing in this repo](docs/tf-idf-explained.md)
2. [Perl pipeline and file formats](docs/pipeline-and-scripts.md)
3. [How to read the published `output/` tables](docs/reading-the-outputs.md)
4. [Walkthrough of top terms in several Gutenberg books](docs/gutenberg-term-walkthrough.md)
5. [Document vectors and cosine similarity](docs/document-vectors-and-similarity.md)
6. [Formula and implementation notes](docs/formula-and-implementation-notes.md)
7. [Examples index](examples/README.md)

## License and data

The 18 texts are public-domain Project Gutenberg works as redistributed in NLTK's Gutenberg corpus. The scripts are a personal toy from 2012 with later notes added here.
