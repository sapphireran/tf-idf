# tf-idf

Personal study checkout for the 2012 Gutenberg TF-IDF toy
([original note](http://nlp-stuff.blogspot.com/2012/09/tfidf-example-and-implementation-details.html)).
The two Perl scripts and the checked-in `output/` tables are unchanged in
spirit: **normalized term frequency × `ln(N / df)`**, with **`N = 18`** in the
gold files.

This branch adds a **query desk** — personal docs, a four-note field corpus,
and a standard-library Python companion that can rank a question against the
shelf and show *which terms* earned the score.

No company code. Public-domain texts only.

## Layout

| Path | What it is |
| --- | --- |
| `tf-idf-values.pl` | 2012 tokenizer, per-document TF, collection DF / IDF |
| `tf*idf-product.pl` | Multiplies each TF table by the IDF table |
| `gutenberg/` | Eighteen public-domain texts (plus a `.DS_Store`) |
| `output/` | Gold `df.txt`, `idf.txt`, `tf/`, `tfidf/` |
| `docs/` | Reading path for the weights, the Perl pipeline, and the desk |
| `examples/field-notes/` | Tiny four-document corpus with expected tables |
| `examples/query-desk/` | Sample questions to ask the shelf |
| `querydesk/` | Stdlib Python: tokenize, weight, rank, explain |
| `tests/` | `unittest` checks against the gold tables and the field notes |

## Formula this checkout actually uses

For term *t* in document *d*:

\[
\mathrm{tf}(t,d) = \frac{\mathrm{count}(t,d)}{\mathrm{word\_count}(d)}, \quad
\mathrm{idf}(t) = \ln\frac{N}{\mathrm{df}(t)}, \quad
\mathrm{tfidf}(t,d) = \mathrm{tf}(t,d)\cdot\mathrm{idf}(t)
\]

- `word_count` follows the 2012 Perl loop: every `split(/ +/)` field increments
  the denominator, including the empty field you get from a leading space.
- Gold IDF uses **`N = 18`** (the eighteen `.txt` files). The live Perl line
  `my $n = $#files` is the last `readdir` index and does **not** reproduce
  those tables if you rerun it today. See [docs/06-quirks.md](docs/06-quirks.md).

A term that appears in every text has `idf = ln(18/18) = 0`, so its TF-IDF is
exactly zero. That is why `the`, `and`, and `about` vanish from rankings even
though no stoplist is applied.

## Query desk in one minute

```bash
# Rank the Gutenberg shelf for a question (cosine of query TF-IDF vs each book)
python3 -m querydesk rank "white whale pequod ahab"

# Show which terms paid for the top hit
python3 -m querydesk explain "white whale pequod ahab"

# Top weighted terms in one gold file
python3 -m querydesk top --doc carroll-alice.txt --n 12

# Worked four-note corpus (glacier / letterpress / tide / herbarium)
python3 -m querydesk field-notes
python3 -m querydesk field-notes --query "cairn moraine icefall"

# Teaching variants next to the classic weights
python3 -m querydesk compare "thane heath witches" --variants classic,smooth,bm25

# Reproduce a slice of the 2012 gold tables
python3 -m querydesk self-test
```

```bash
make test          # python3 -m unittest discover -s tests -v
make field-notes   # rebuild and print the tiny corpus
make alice         # top terms for Alice
```

## Original Perl

Needs a `perl` with `Text::CSV_XS` for the second script.

```bash
mkdir -p output/tf output/tfidf
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

Rerunning the first script on this tree will also try to read
`gutenberg/.DS_Store` and will set `N` from `$#files`. Prefer `querydesk` or
the checked-in `output/` tables when you want the 2012 numbers.

## Reading path

1. [docs/README.md](docs/README.md) — map of the notes
2. [docs/01-weights-this-repo-uses.md](docs/01-weights-this-repo-uses.md) — TF, IDF, product
3. [docs/02-perl-pipeline.md](docs/02-perl-pipeline.md) — what each 2012 script writes
4. [docs/03-gutenberg-shelf.md](docs/03-gutenberg-shelf.md) — the eighteen files
5. [docs/04-query-desk.md](docs/04-query-desk.md) — ranking and attribution
6. [docs/05-field-notes-walkthrough.md](docs/05-field-notes-walkthrough.md) — hand-sized corpus
7. [docs/06-quirks.md](docs/06-quirks.md) — `$#files`, speaker tags, apostrophes
8. [docs/07-exercises.md](docs/07-exercises.md) / [docs/08-answers.md](docs/08-answers.md)
