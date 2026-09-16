# tf-idf

Personal toy project for computing **term frequency–inverse document frequency**
(TF-IDF) over the classic NLTK / Project Gutenberg sample texts.

The original two Perl scripts produced the checked-in tables under `output/`.
This repo now also has a longer write-up of the math, the corpus, the pipeline
quirks, and a tiny hand-calculable example you can run without Perl modules.

This is a **personal learning repo**. It is not a library, not a product, and
not affiliated with Project Gutenberg or NLTK beyond using their public-domain
sample filenames and texts.

## What is in here

| Path | What it is |
| --- | --- |
| `gutenberg/` | 18 public-domain books (NLTK Gutenberg sample) |
| `tf-idf-values.pl` | Pass 1: per-document TF, plus corpus DF and IDF |
| `tf*idf-product.pl` | Pass 2: multiply TF × IDF into per-document scores |
| `output/tf/` | Normalized term frequencies, one file per book |
| `output/df.txt` | Document frequency and the books each term appears in |
| `output/idf.txt` | `ln(N / df)` for every term |
| `output/tfidf/` | Final TF-IDF tables, one file per book |
| `docs/` | Math, corpus notes, Perl pipeline, how to read the scores |
| `examples/` | Worked numbers from the real output, plus a tiny corpus |

Start with [docs/README.md](docs/README.md) if you want the explanation before
the scripts.

## Formula used here

For term `t` in document `d`:

```
tf(t, d)     = count(t, d) / tokens(d)
idf(t)       = ln( N / df(t) )
tfidf(t, d)  = tf(t, d) * idf(t)
```

- `N` is the number of documents in the collection.
- `df(t)` is the number of documents that contain `t` at least once.
- `ln` is the natural logarithm (Perl's `log`, Python's `math.log`).
- Tokens are lowercased and stripped of punctuation. See
  [docs/perl-pipeline.md](docs/perl-pipeline.md) for the exact rules and the
  off-by-one / empty-token quirks in the original scripts.

Checked-in `output/idf.txt` was generated with **N = 18** (one entry per
`.txt` book). Re-running `tf-idf-values.pl` as written will not necessarily
reproduce that: `readdir` also sees `.`, `..`, and any `.DS_Store`, and the
script uses `$#files` (last index) as `N`.

## Quick start

### Read the existing results

No extra dependencies. From the repo root:

```bash
python3 examples/top_terms.py --n 15
python3 examples/top_terms.py --doc carroll-alice --n 20
python3 examples/compare_documents.py --a carroll-alice --b austen-emma
python3 examples/compare_documents.py --matrix
```

`examples/top_terms.py` ranks the checked-in `output/tfidf/` tables.
`examples/compare_documents.py` treats each book as a sparse TF-IDF vector and
reports cosine similarity.

### Recreate TF / IDF / TF-IDF from the books (Perl)

You need a Perl that can `use strict` and, for the second script,
[Text::CSV_XS](https://metacpan.org/pod/Text::CSV_XS).

```bash
mkdir -p output/tf output/tfidf
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

The first script writes `output/tf/<book>.txt`, `output/df.txt`, and
`output/idf.txt`. The second multiplies those tables into
`output/tfidf/<book>.txt`.

### Hand-calculable tiny corpus (Python, stdlib only)

```bash
python3 examples/tiny-corpus/compute_tfidf.py
python3 examples/tiny-corpus/compute_tfidf.py --show-tokens
```

Walk through the arithmetic in
[examples/tiny-corpus/expected-hand-calc.md](examples/tiny-corpus/expected-hand-calc.md).

## A taste of the Gutenberg scores

Highest TF-IDF terms in a few books (from the checked-in tables):

| Book | Distinctive terms |
| --- | --- |
| *Alice's Adventures in Wonderland* | `alice`, `gryphon`, `dormouse`, `duchess`, `hatter` |
| *Moby Dick* | `whale`, `ahab`, `sperm`, `stubb`, `queequeg` |
| *Emma* | `emma`, `harriet`, `weston`, `knightley`, `elton` |
| *Macbeth* | `macb`, `haue`, `macbeth`, `macd`, `rosse` |
| Blake's poems | `thel`, `weep`, `lyca`, `thee`, `vales` |

Stopwords such as `the`, `and`, and `a` appear in every book, so their IDF is
`ln(18/18) = 0` and they vanish from the TF-IDF tables. Character names and
setting-specific nouns keep a high IDF and rise to the top.

Shakespeare looks odd because the texts keep speech prefixes (`HAM`, `MACB`)
and Early Modern spelling (`haue`, `vpon`). Those are features of the source
files, not a separate stemmer.

Full walkthroughs with the actual `tf`, `df`, `idf`, and `tfidf` numbers:
[examples/worked-examples.md](examples/worked-examples.md).

## Corpus snapshot

18 documents, about 2.1 million whitespace-separated words before the Perl
tokenizer runs:

| File | Work | Approx. words |
| --- | --- | ---: |
| `blake-poems.txt` | William Blake, poems | 6,845 |
| `burgess-busterbrown.txt` | Thornton Burgess, *Buster Brown* | 15,870 |
| `shakespeare-macbeth.txt` | *Macbeth* | 17,741 |
| `shakespeare-caesar.txt` | *Julius Caesar* | 20,459 |
| `carroll-alice.txt` | Lewis Carroll, *Alice* | 26,443 |
| `shakespeare-hamlet.txt` | *Hamlet* | 29,605 |
| `bryant-stories.txt` | Stories by Bryant | 45,988 |
| `chesterton-thursday.txt` | *The Man Who Was Thursday* | 57,955 |
| `chesterton-brown.txt` | Father Brown stories | 71,626 |
| `milton-paradise.txt` | *Paradise Lost* | 79,659 |
| `chesterton-ball.txt` | *The Ball and the Cross* | 81,598 |
| `austen-persuasion.txt` | *Persuasion* | 83,308 |
| `austen-sense.txt` | *Sense and Sensibility* | 118,675 |
| `whitman-leaves.txt` | *Leaves of Grass* | 122,070 |
| `austen-emma.txt` | *Emma* | 158,167 |
| `edgeworth-parents.txt` | Maria Edgeworth, *The Parent's Assistant* | 166,070 |
| `melville-moby_dick.txt` | *Moby-Dick* | 212,030 |
| `bible-kjv.txt` | King James Bible | 821,133 |

More context: [docs/corpus-notes.md](docs/corpus-notes.md).

## Output file format

All tables are tab-separated UTF-8 text.

**`output/tf/<book>.txt`** and **`output/tfidf/<book>.txt`**

```
term<TAB>score
```

Terms are sorted alphabetically, not by score. Use `examples/top_terms.py` to
rank them.

**`output/idf.txt`**

```
term<TAB>idf
```

**`output/df.txt`**

```
term<TAB>document_count<TAB>comma-separated filenames
```

The first line of `df.txt` is a header. `idf.txt` has no header.

## Documentation map

1. [docs/tf-idf-explained.md](docs/tf-idf-explained.md) — definition, IDF
   variants, why stopwords disappear, what TF-IDF is not.
2. [docs/corpus-notes.md](docs/corpus-notes.md) — where the 18 texts come
   from and what to watch for (stage directions, bible verse numbers).
3. [docs/perl-pipeline.md](docs/perl-pipeline.md) — line-by-line behavior of
   the two Perl scripts, including the `N` and empty-token bugs.
4. [docs/interpreting-scores.md](docs/interpreting-scores.md) — how to read a
   row, compare two books, and avoid ranking with `sort -n` on scientific
   notation.
5. [docs/tokenizer-examples.md](docs/tokenizer-examples.md) — before / after
   on real Alice, Shakespeare, and Bible strings.
6. [examples/worked-examples.md](examples/worked-examples.md) — Alice, Ahab,
   Emma, and `the` with numbers from `output/`.
7. [examples/tiny-corpus/](examples/tiny-corpus/) — four short documents and a
   Python script whose printed table matches the hand calculation.

## Personal scope

I keep this repository for blog-post leftovers, toy experiments, and notes.
Please do not treat the Perl as reference code for production search. If you
want a modern default, use a library that documents its tokenizer and IDF
smoothing (`sklearn.feature_extraction.text.TfidfVectorizer`,
`rank_bm25`, etc.). The point of this repo is to see every intermediate table.
