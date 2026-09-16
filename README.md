# Personal Gutenberg TF-IDF shelf

This is a personal, public-domain playground. In 2012 the original
scripts scored a small Project Gutenberg shelf with the classical
product `tf * ln(N / df)`. The checked-in `output/` tables are a
fossil of that run. This checkout adds a **reading companion**: notes
and standard-library examples that treat those tables as a way to
*read* the eighteen books, not as a search-engine kit.

No workplace text. No product ranking stack. The Perl in the root
directory is left alone.

## What is already here

| Path | Role |
| --- | --- |
| `gutenberg/` | Eighteen public-domain texts (plus a stray `.DS_Store`) |
| `tf-idf-values.pl` | Tokenize, write per-document `tf`, then corpus `df` / `idf` |
| `tf*idf-product.pl` | Multiply those two tables into `output/tfidf/` |
| `output/` | The 2012 snapshot this companion reads |
| `docs/reading-companion/` | Essays, atlas, cookbook, exercises |
| `examples/reading-companion/` | Stdlib scripts over the snapshot |

The snapshot uses **N = 18** (one document per book file). Function
words that appear in every book (`the`, `a`, `and`) have `idf = 0`,
so their TF-IDF score is exactly zero. Distinctive names and Folio
spellings do not.

## Reading path

Start with the index, then follow whichever question you actually
have:

1. [Companion index](docs/reading-companion/00-index.md)
2. [How these weights read](docs/reading-companion/01-how-these-weights-read.md)
3. [Length and name bias](docs/reading-companion/02-length-and-name-bias.md)
4. [Shakespeare Folio spellings](docs/reading-companion/03-shakespeare-folio-spellings.md)
5. [Austen, Edgeworth, and manners](docs/reading-companion/04-austen-edgeworth-manners.md)
6. [Chesterton: names vs. license trailers](docs/reading-companion/05-chesterton-names-and-trailers.md)
7. [The archaic-pronoun corridor](docs/reading-companion/06-archaic-pronoun-corridor.md)
8. [Pairwise similarity map](docs/reading-companion/07-similarity-map.md)
9. [Term atlas](docs/reading-companion/08-term-atlas.md)
10. [Query cookbook](docs/reading-companion/09-query-cookbook.md)
11. [Exercises](docs/reading-companion/10-exercises.md) and [answers](docs/reading-companion/11-answers.md)

## Run the companion examples

Python 3, standard library only. From the repository root:

```bash
python3 examples/reading-companion/run_checks.py
python3 examples/reading-companion/term_atlas.py --top 8
python3 examples/reading-companion/cosine_map.py
python3 examples/reading-companion/query_shelf.py alice hatter gryphon
python3 examples/reading-companion/folio_spellings.py
python3 examples/reading-companion/length_study.py
python3 examples/reading-companion/boilerplate_scan.py
```

Each script accepts `--check` and will exit non-zero if a documented
measurement on this snapshot drifts.

## Re-running the 2012 Perl (optional)

The companion never rewrites `output/`. If you want to regenerate
those tables yourself:

```bash
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

`tf*idf-product.pl` needs `Text::CSV_XS`. The first script's
`$n = $#files` is the last `readdir` index, which can include `.`
and `..`. The checked-in IDF column matches **N = 18**, not that
index. See [how these weights read](docs/reading-companion/01-how-these-weights-read.md).

## Formula actually used

For term *t* in document *d*:

```
tf(t, d)  = count(t, d) / tokens(d)
idf(t)    = ln(N / df(t))          # natural log, N = 18 on the snapshot
tfidf     = tf(t, d) * idf(t)
```

No add-one smoothing. No sublinear TF. No cosine inside the Perl.
Cosine appears only in the companion scripts, as a way to compare
already-built book vectors.
