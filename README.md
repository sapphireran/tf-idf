# tf-idf

Personal toy lab for term frequency–inverse document frequency.

The original checkout is the 2012 example: eighteen public-domain
books under `gutenberg/`, two Perl scripts, and precomputed tables
under `output/`. This revision adds a written walkthrough of those
choices and a second, tiny corpus you can rerun in a few seconds.

This is personal study material. It is not product code.

## Quick start

```bash
# every arithmetic cell of a 3-sentence collection
python3 examples/python/worked_example.py

# five original essays, committed tables refreshed
python3 examples/python/run_tiny_corpus.py

# distinctive terms already sitting in output/tfidf/
python3 examples/python/inspect_gutenberg.py --only carroll-alice.txt melville-moby_dick.txt

# tests for the reference implementation
python3 -m unittest discover -s tests -v
```

## Repository map

| Path | Role |
| --- | --- |
| `gutenberg/` | Eighteen public-domain books (the historical sample) |
| `tf-idf-values.pl` | Perl: TF, DF, and IDF |
| `tf*idf-product.pl` | Perl: multiply TF by IDF |
| `output/` | Committed Gutenberg tables |
| `docs/` | Written explanation of the formulas and the pipeline |
| `examples/tiny_corpus/` | Five original essays plus expected TSV/HTML |
| `examples/python/` | Standard-library reference implementation |
| `tests/` | Unit tests for the reference and the tiny corpus |

Start reading at [docs/README.md](docs/README.md).

## Scoring in one line

```
tf(t, d)     = count(t, d) / |d|
idf(t)       = ln(N / df(t))
tfidf(t, d)  = tf(t, d) * idf(t)
```

`N` is 18 in the committed Gutenberg `output/idf.txt` and 5 in the
tiny corpus. Tokens are lowercase letters and digits after punctuation
is deleted. There is no stop-word list; words that appear in every
document get `idf = 0`.

## Historical Perl path

```bash
perl tf-idf-values.pl      # writes output/tf, output/df.txt, output/idf.txt
perl tf*idf-product.pl     # writes output/tfidf  (needs Text::CSV_XS)
```

The committed `output/` files are the original toy result, including
the 2012 IDF collection-size fix. You can study them without rerunning
Perl. If you do regenerate them, set `N` to the number of books, not
to `$#files`. Details are in `docs/03-formulas.md` and
`docs/09-reproducing-results.md`.
