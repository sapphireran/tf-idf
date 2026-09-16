# tf-idf

Personal toy repo for **term frequency–inverse document frequency** on a
small Project Gutenberg mix, plus a documented Python companion that
reproduces the original formulas.

The 2012 Perl scripts and the committed `output/` tables are the original
artifact (companion to a now-vanished blog post). Everything under
`docs/`, `examples/`, `tfidf/`, and `tests/` is later explanation: same
math, smaller corpora, and a CLI you can run without `Text::CSV_XS`.

## Formula used here

```
tf(t, d)    = count(t, d) / tokens(d)
idf(t)      = log(N / df(t))          # natural log, raw mode
tfidf(t, d) = tf(t, d) * idf(t)
```

A term that appears in every document gets `idf = 0` and drops out.
That is why `a` / `about` are zero in `output/tfidf/carroll-alice.txt`
and why `emma` / `whale` / `alice` rise to the top of their files.

Walkthroughs:

- [docs/algorithm.md](docs/algorithm.md) — definitions and tokenization
- [examples/hand-calculation/](examples/hand-calculation/) — three lines, full arithmetic
- [examples/tiny-corpus/](examples/tiny-corpus/) — four original notes
- [docs/interpreting-gutenberg.md](docs/interpreting-gutenberg.md) — reading `output/`
- [docs/perl-pipeline.md](docs/perl-pipeline.md) — the 2012 scripts
- [docs/variants.md](docs/variants.md) — smooth IDF, sklearn, BM25
- [docs/cli-cookbook.md](docs/cli-cookbook.md) — copy-paste commands

## Quick start (Python, stdlib only)

```bash
python3 -m tfidf report examples/hand-calculation/corpus --n 5
python3 -m tfidf report examples/tiny-corpus --n 8
python3 -m tfidf query examples/tiny-corpus "ganymede telescope opposition"
python3 -m tfidf top-tsv output/tfidf --n 10
```

```bash
python3 -m unittest discover -s tests -v
# or
make test
```

## Quick start (original Perl)

```bash
perl tf-idf-values.pl      # writes output/tf, output/df.txt, output/idf.txt
perl tf*idf-product.pl     # needs Text::CSV_XS; writes output/tfidf
```

Re-running the Perl today will **not** bit-match the committed IDF table
unless you fix the document count. The scripts use `$#files` from
`readdir` (which includes `.` and `..`). The committed snapshot was
built with `N = 18`. Details are in [docs/perl-pipeline.md](docs/perl-pipeline.md).

## Layout

```
tf-idf-values.pl      # TF + DF + IDF from gutenberg/
tf*idf-product.pl     # TF * IDF
gutenberg/            # 18 public-domain texts
output/               # 2012 snapshot of the tables
tfidf/                # Python package (python3 -m tfidf)
examples/             # hand calculation + tiny original notes
docs/                 # algorithm, Perl notes, Gutenberg commentary
tests/                # unittest coverage of the math and examples
```

## CLI

| command | purpose |
| --- | --- |
| `python3 -m tfidf compute DIR -o OUT` | write `tf/`, `idf.txt`, `df.txt`, `tfidf/` |
| `python3 -m tfidf report DIR` | markdown top-terms + cosine matrix |
| `python3 -m tfidf top DIR` | keyword list per document |
| `python3 -m tfidf top-tsv output/tfidf` | rank the committed snapshot |
| `python3 -m tfidf query DIR "…"` | cosine rank against a query |
| `python3 -m tfidf similar DIR` | pairwise cosine |

`--idf raw|smooth` switches formulas. `--perl-compat` copies the Perl
TF denominator (leading empty split fields). See the cookbook.

## What this is not

It is not a search engine, a topic model, or a cleaned Gutenberg
distribution. Headers, speaker tags, and archaic pronouns are left in
on purpose so the rankings stay honest about the files on disk.
