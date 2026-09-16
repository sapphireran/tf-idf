# tf-idf

Personal toy project for **term frequency–inverse document frequency** (tf-idf).
The original 2012 Perl scripts score every token in a small [Project
Gutenberg](https://www.gutenberg.org/) corpus. This repo now also has a
walkthrough of the math, a tiny hand-calculated example, and implementations
you can run without touching the historical scripts.

The first commit pointed at a blog post,
[tfidf example and implementation details](http://nlp-stuff.blogspot.com/2012/09/tfidf-example-and-implementation-details.html)
(the URL is no longer available). The Perl files and the committed
`output/` trees are that original walkthrough.

## What tf-idf is measuring

A word is interesting in a document when it is **common in that document**
and **rare in the rest of the collection**.

```
tf(t, d)     = count(t in d) / tokens(d)
idf(t)       = ln( N / df(t) )
tfidf(t, d)  = tf(t, d) * idf(t)
```

`N` is the number of documents. `df(t)` is how many of those documents
contain term `t`. Words that appear in every document (`the`, `and`, `a` in
this Gutenberg slice) get `idf = ln(1) = 0`, so they disappear from the
ranking even if they are frequent.

Worked numbers for a three-sentence corpus live in
[`docs/worked-example.md`](docs/worked-example.md). The longer explanation,
including other common formulas, is in
[`docs/tfidf-explained.md`](docs/tfidf-explained.md).

## Repository layout

| Path | What it is |
| --- | --- |
| [`tf-idf-values.pl`](tf-idf-values.pl) | Historical script: tokenize Gutenberg files, write per-document `tf` plus collection `df` / `idf` |
| [`tf*idf-product.pl`](tf*idf-product.pl) | Historical script: multiply stored `tf` by stored `idf` |
| [`gutenberg/`](gutenberg/) | 18 public-domain texts used as the collection |
| [`output/`](output/) | Committed 2012 results (`tf/`, `idf.txt`, `df.txt`, `tfidf/`) |
| [`docs/`](docs/) | Math, pipeline notes, worked example, corpus notes |
| [`examples/tiny-corpus/`](examples/tiny-corpus/) | Three-line collection you can score by hand |
| [`examples/themes-corpus/`](examples/themes-corpus/) | Slightly longer bakery / observatory / concert texts |
| [`examples/python/tfidf.py`](examples/python/tfidf.py) | Stdlib Python implementation (correct `N`, parameterized paths) |
| [`examples/perl/compute_tf_idf.pl`](examples/perl/compute_tf_idf.pl) | Cleaned Perl rewrite that takes `--input` / `--output` |
| [`tests/`](tests/) | `unittest` checks against the hand-calculated tiny corpus |

## Quick start (Python, recommended)

Python 3.8+ is enough. There are no third-party dependencies.

```bash
# Score the three-line teaching corpus and print the ranking
python3 examples/python/tfidf.py --input examples/tiny-corpus --top 5

# Score the themed paragraphs
python3 examples/python/tfidf.py --input examples/themes-corpus --top 8

# Rank tokens from the committed Gutenberg tf-idf tables (no recompute)
python3 examples/python/top_terms.py --from-output output/tfidf --top 10

# Recompute Gutenberg from the texts (writes a new directory; does not overwrite output/)
python3 examples/python/tfidf.py --input gutenberg --output examples/_scratch/gutenberg --top 8
```

Run the checks:

```bash
python3 -m unittest discover -s tests -v
```

## Historical Perl scripts

The original pair is hardcoded to `gutenberg/` and `output/`. Quote the
product script name so the shell does not glob the `*`:

```bash
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

`tf*idf-product.pl` needs [Text::CSV_XS](https://metacpan.org/pod/Text::CSV_XS)
to parse the tab-separated `tf` / `idf` files. The cleaned example
[`examples/perl/compute_tf_idf.pl`](examples/perl/compute_tf_idf.pl) splits
on tabs itself and does not need that module:

```bash
perl examples/perl/compute_tf_idf.pl --input examples/tiny-corpus --output examples/_scratch/tiny-perl
```

A line-by-line reading of the 2012 scripts, including the `$#files`
document-count quirk, is in [`docs/perl-pipeline.md`](docs/perl-pipeline.md).

## Gutenberg snapshot

Eighteen files, public domain, used as one collection:

| File | Work |
| --- | --- |
| `austen-emma.txt` | Jane Austen, *Emma* |
| `austen-persuasion.txt` | Jane Austen, *Persuasion* |
| `austen-sense.txt` | Jane Austen, *Sense and Sensibility* |
| `bible-kjv.txt` | King James Bible |
| `blake-poems.txt` | William Blake, poems |
| `bryant-stories.txt` | Stories by J. C. Gorham / Bryant collection in this dump |
| `burgess-busterbrown.txt` | Thornton Burgess, *The Adventures of Buster Bear* (filename keeps the original dump name) |
| `carroll-alice.txt` | Lewis Carroll, *Alice's Adventures in Wonderland* |
| `chesterton-ball.txt` | G. K. Chesterton, *The Ball and the Cross* |
| `chesterton-brown.txt` | G. K. Chesterton, Father Brown stories |
| `chesterton-thursday.txt` | G. K. Chesterton, *The Man Who Was Thursday* |
| `edgeworth-parents.txt` | Maria Edgeworth, *The Parent's Assistant* |
| `melville-moby_dick.txt` | Herman Melville, *Moby-Dick* |
| `milton-paradise.txt` | John Milton, *Paradise Lost* |
| `shakespeare-caesar.txt` | *Julius Caesar* |
| `shakespeare-hamlet.txt` | *Hamlet* |
| `shakespeare-macbeth.txt` | *Macbeth* |
| `whitman-leaves.txt` | Walt Whitman, *Leaves of Grass* |

From the committed `output/tfidf/` tables, the highest-scoring tokens look
like character names and setting words — `alice` / `gryphon` / `hatter` in
Wonderland, `whale` / `ahab` / `queequeg` in *Moby-Dick*. Speech prefixes
and Early Modern spelling dominate the Shakespeare files (`ham`, `haue`,
`hor`). More of that ranking is in
[`docs/gutenberg-corpus.md`](docs/gutenberg-corpus.md) and
[`examples/gutenberg-top-terms.md`](examples/gutenberg-top-terms.md).

## Formula used here vs. the usual library defaults

This project uses **normalized term frequency** and **raw inverse document
frequency** with the natural logarithm, the same product the 2012 scripts
wrote to `output/`:

```
tfidf = (count / doc_length) * ln(N / df)
```

scikit-learn's `TfidfVectorizer` default is different: it uses `tf = count`
(or a sublinear variant), `idf = ln((N + 1) / (df + 1)) + 1`, and then
L2-normalizes each document vector. The ranking is usually similar; the
numbers are not interchangeable. See
[`docs/formula-notes.md`](docs/formula-notes.md).

## Docs index

- [What tf-idf means, with pictures of the ranking](docs/tfidf-explained.md)
- [How the original Perl pipeline writes `tf`, `df`, `idf`, `tfidf`](docs/perl-pipeline.md)
- [Hand calculation of the three-line corpus](docs/worked-example.md)
- [Gutenberg files, tokenization quirks, and sample rankings](docs/gutenberg-corpus.md)
- [N-counting, log base, smoothing, and sklearn](docs/formula-notes.md)
- [How to run every example](examples/README.md)
