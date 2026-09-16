# tf-idf

Personal toy project that computes **term frequency–inverse document frequency**
(TF-IDF) over a small Project Gutenberg corpus. The original Perl scripts
here accompanied a blog post; this repository now also has a worked
teaching path so the same numbers can be recomputed, inspected, and
explained without touching any company code.

TF-IDF is a ranking, not a language model. It answers a narrow question:

> In this document, which words are common *here* and uncommon *across
> the rest of the collection*?

That is enough to surface character names in Austen, the white whale in
Melville, and speech prefixes in the First Folio texts — and it is also
enough to leak Project Gutenberg boilerplate when a header is unique to
one file.

## Repository layout

| Path | What it is |
| --- | --- |
| `tf-idf-values.pl` | Original Perl pass: tokenize, write per-document TF, write collection DF/IDF |
| `tf*idf-product.pl` | Original Perl pass: multiply stored TF by stored IDF |
| `gutenberg/` | 18 public-domain texts used as the collection |
| `output/` | Checked-in results from the original Perl run (`N = 18`) |
| `docs/` | Math, pipeline, corpus notes, and how to read the numbers |
| `examples/` | Tiny/micro corpora plus a stdlib Python teaching implementation |
| `tests/` | Unit tests for the teaching implementation |

## Formula used in this repo

For term `t` in document `d`:

```
tf(t, d)  = count(t, d) / words(d)
idf(t)    = ln(N / df(t))
tfidf(t, d) = tf(t, d) * idf(t)
```

- `count(t, d)` is the raw number of times `t` occurs in `d` after
  the tokenizer below.
- `words(d)` is the number of whitespace-separated tokens in `d`
  (see [docs/limitations.md](docs/limitations.md) for empty-token
  quirks in the original Perl).
- `N` is the number of documents in the collection. The checked-in
  Gutenberg outputs are consistent with **`N = 18`**.
- `df(t)` is the number of documents that contain `t` at least once.
- `ln` is the natural logarithm.

A term that appears in every document gets `idf = ln(1) = 0`, so its
TF-IDF score is zero everywhere. That is why `a`, `the`, and `and` drop
out of `output/tfidf/` even though this pipeline has **no stopword list**.

Worked arithmetic: [docs/tf-idf-explained.md](docs/tf-idf-explained.md)
and [docs/worked-example.md](docs/worked-example.md).

## Tokenizer

Both the original Perl and the teaching Python apply the same cleaning
rules, in order:

1. Collapse horizontal/vertical whitespace to a single space.
2. Lowercase ASCII letters.
3. Delete every character that is not `A–Z`, `a–z`, a digit, or
   whitespace.
4. Split on one or more spaces.

Apostrophes disappear (`o'er` → `oer`, `Alice's` → `alices`). That is
visible in the Shakespeare and Carroll rankings.

## Quick start (teaching Python)

The teaching implementation is stdlib-only and scores `*.txt` files
only (so example READMEs are not documents). From the repository root:

```bash
python3 examples/python/compute_tfidf.py \
  --input-dir examples/tiny-corpus \
  --output-dir /tmp/tiny-tfidf

python3 examples/python/top_terms.py /tmp/tiny-tfidf/tfidf --top 8
```

Expected distinctive terms for the three-document toy collection:

- `cats.txt` → `cats`, `cat`, `purr`, `yarn`
- `dogs.txt` → `dogs`, `dog`, `bark`, `ball`
- `baking.txt` → `bread`, `dough`, `ovens`, `flour`

Run the same ranker on the checked-in Gutenberg scores:

```bash
python3 examples/python/top_terms.py output/tfidf --top 10
```

## Original Perl pipeline

These scripts are historical. They still describe the blog-post
calculation; they are not a general-purpose library.

```bash
# 1) TF per file + collection DF/IDF  →  output/tf, output/df.txt, output/idf.txt
perl tf-idf-values.pl

# 2) TF * IDF per file  →  output/tfidf
perl 'tf*idf-product.pl'
```

The product script needs `Text::CSV_XS` to parse the tab-separated
intermediate files. The teaching Python path does not.

Pipeline details and the `$#files` document-count quirk:
[docs/pipeline.md](docs/pipeline.md).

## What the Gutenberg rankings show

Checked-in `output/tfidf/` already behaves like a character-and-setting
index:

| File | Highest-scoring terms |
| --- | --- |
| `austen-emma.txt` | emma, harriet, weston, knightley |
| `carroll-alice.txt` | alice, gryphon, dormouse, duchess |
| `melville-moby_dick.txt` | whale, ahab, sperm, stubb |
| `shakespeare-hamlet.txt` | ham, haue, hor, qu |
| `chesterton-ball.txt` | turnbull, macian — and also `ebook`, `gutenberg` |

The Hamlet row is a reminder that TF-IDF ranks **tokens**, not literary
themes. Folio speech prefixes (`ham`, `hor`) outrank `hamlet` itself.
The Chesterton row is a reminder that unique boilerplate is as
"distinctive" as a protagonist.

Fuller notes: [docs/interpreting-results.md](docs/interpreting-results.md)
and [docs/gutenberg-corpus.md](docs/gutenberg-corpus.md).

## Documentation map

1. [docs/tf-idf-explained.md](docs/tf-idf-explained.md) — definitions and the exact formula
2. [docs/pipeline.md](docs/pipeline.md) — how the two Perl scripts fit together
3. [docs/output-formats.md](docs/output-formats.md) — TSV layouts under `output/`
4. [docs/worked-example.md](docs/worked-example.md) — hand-computed micro collection
5. [docs/gutenberg-corpus.md](docs/gutenberg-corpus.md) — the 18 texts
6. [docs/interpreting-results.md](docs/interpreting-results.md) — reading the rankings
7. [docs/limitations.md](docs/limitations.md) — tokenizer, `N`, boilerplate, Folio prefixes
8. [examples/README.md](examples/README.md) — toy corpora and the Python CLI

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Corpus and license notes

The files under `gutenberg/` are public-domain texts distributed by
[Project Gutenberg](https://www.gutenberg.org/). Headers and license
paragraphs are part of some files and therefore part of the scores.
The Perl scripts, Python teaching code, and writeups in this repository
are personal study material, not a product.
