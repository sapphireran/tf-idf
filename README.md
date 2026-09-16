# tf-idf

Personal toy collection for **term frequency × inverse document frequency**
on a tiny Project Gutenberg shelf: 18 public-domain books, two original
Perl scripts, and a Python rewrite you can actually run.

The Perl side is the code that accompanied a blog post. This repo now
also has:

- the formulas written out, with the quirks of the original tokenizer
- a 3-document pencil-and-paper example whose numbers are pinned by tests
- a standard-library Python CLI that recomputes tf, idf, and tf-idf
- a reading of the distinctive terms in each Gutenberg extract

No company code. No extra services. `python3` 3.9+ is enough.

## Quick start

```bash
# Hand-sized corpus from docs/worked-example.md
python3 -m tfidf_toy demo

# Top distinctive terms in each Gutenberg extract (in-memory, no write)
python3 -m tfidf_toy top --input gutenberg --k 12

# Recompute the Perl-style TSV tables
python3 -m tfidf_toy compute --input gutenberg --output output_py

# Tests (stdlib unittest)
python3 -m unittest discover -s tests -v
```

The original Perl path still exists if you have `Text::CSV_XS`:

```bash
perl tf-idf-values.pl      # writes output/tf, output/df.txt, output/idf.txt
perl 'tf*idf-product.pl'   # writes output/tfidf
```

Committed `output/` is from that Perl run. Prefer `output_py/` for a fresh
Python recompute so the historical tables stay diffable.

## What is in the shelf

| file | work |
| --- | --- |
| `austen-emma.txt` | *Emma* (1816) |
| `austen-persuasion.txt` | *Persuasion* (1818) |
| `austen-sense.txt` | *Sense and Sensibility* (1811) |
| `bible-kjv.txt` | King James Bible |
| `blake-poems.txt` | Blake, *Songs of Innocence and of Experience* plus other poems |
| `bryant-stories.txt` | Bryant stories |
| `burgess-busterbrown.txt` | Burgess, Buster Brown |
| `carroll-alice.txt` | *Alice’s Adventures in Wonderland* (1865) |
| `chesterton-ball.txt` | Chesterton, *The Ball and the Cross* |
| `chesterton-brown.txt` | Chesterton, Father Brown |
| `chesterton-thursday.txt` | Chesterton, *The Man Who Was Thursday* |
| `edgeworth-parents.txt` | Edgeworth, *The Parent’s Assistant* |
| `melville-moby_dick.txt` | *Moby-Dick* |
| `milton-paradise.txt` | *Paradise Lost* |
| `shakespeare-caesar.txt` | *Julius Caesar* |
| `shakespeare-hamlet.txt` | *Hamlet* |
| `shakespeare-macbeth.txt` | *Macbeth* |
| `whitman-leaves.txt` | *Leaves of Grass* |

## Formula used here

\[
\mathrm{tf}(t,d)=\frac{\mathrm{count}(t,d)}{|d|},\quad
\mathrm{idf}(t)=\ln\frac{N}{\mathrm{df}(t)},\quad
\mathrm{tfidf}(t,d)=\mathrm{tf}(t,d)\times\mathrm{idf}(t)
\]

\(N = 18\) for the Gutenberg shelf. A token that appears in every book has
idf 0, so `the` never ranks. A token that appears in one book has idf
\(\ln 18 \approx 2.89037\).

Full write-up: [`docs/tf-idf.md`](docs/tf-idf.md).

## Alice, as a sanity check

Highest tf-idf tokens from the committed Perl output for
`carroll-alice.txt`:

```
alice       0.02596
gryphon     0.00455
duchess     0.00424
dormouse    0.00424
hatter      0.00371
turtle      0.00317
caterpillar 0.00182
rabbit      0.00178
```

Names and nonsense creatures surface; `the` is stored as `0`. That is the
behavior the worked example is designed to make obvious on three
sentences instead of 18 books.

## Documentation map

| doc | contents |
| --- | --- |
| [`docs/tf-idf.md`](docs/tf-idf.md) | tf, idf, product, variants this repo does *not* implement |
| [`docs/tokenization.md`](docs/tokenization.md) | lowercase, punctuation stripping, Perl length quirk |
| [`docs/pipeline.md`](docs/pipeline.md) | `gutenberg/` → `output/` file formats |
| [`docs/worked-example.md`](docs/worked-example.md) | every arithmetic step on 3 documents |
| [`docs/gutenberg-results.md`](docs/gutenberg-results.md) | how to read the 18-book top lists |
| [`examples/tiny_corpus/`](examples/tiny_corpus/) | the 3 source files plus a README |

## Python CLI sketch

```text
python3 -m tfidf_toy demo
python3 -m tfidf_toy top --input gutenberg --k 15
python3 -m tfidf_toy top --input gutenberg --only carroll-alice.txt --k 20
python3 -m tfidf_toy compare --input gutenberg austen-emma.txt austen-sense.txt
python3 -m tfidf_toy compute --input gutenberg --output output_py
python3 -m tfidf_toy diff-output --left output --right output_py
```

`--idf smooth` switches to \(\ln((N+1)/(\mathrm{df}+1))+1\) for comparison
with the raw formula above. Default is raw, matching the Perl scripts.

## Layout

```
gutenberg/                 source texts (public domain extracts)
output/                    original Perl tf / df / idf / tfidf tables
tf-idf-values.pl           original tf, df, idf writer
tf*idf-product.pl          original tf * idf writer
tfidf_toy/                 Python package (stdlib only)
tests/                     unittest
docs/                      long-form notes
examples/tiny_corpus/      3-document demo collection
```
