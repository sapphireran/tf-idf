# tf-idf

A small, personal toy for computing **term frequency–inverse document frequency** (tf-idf) over a pocket corpus of [Project Gutenberg](https://www.gutenberg.org/) texts.

This repository is the code and data that originally accompanied a 2012 write-up on discovering distinctive words in a document. The blog URL recorded in git history (`nlp-stuff.blogspot.com`, September 2012) is no longer reachable; the notes under [`docs/`](docs/) reconstruct the method from the scripts that are actually here.

The pipeline is intentionally simple. It is meant to be read, rerun, and compared against a hand-worked example — not used as a production search engine.

## What this repo contains

| Path | Role |
| --- | --- |
| [`gutenberg/`](gutenberg/) | 18 public-domain texts (Austen, Shakespeare, Melville, the KJV, …) |
| [`tf-idf-values.pl`](tf-idf-values.pl) | Walk the corpus, write per-document **tf** and corpus-wide **df / idf** |
| [`tf*idf-product.pl`](tf*idf-product.pl) | Multiply each term’s tf by its idf |
| [`output/`](output/) | Precomputed tables from a run of those two scripts |
| [`docs/`](docs/) | Algorithm, pipeline, corpus catalog, quirks, script walkthrough |
| [`examples/`](examples/) | A four-document toy corpus, a hand calculation, and helper scripts |

## The formula used here

For a term \(t\) in document \(d\):

\[
\mathrm{tf}(t, d) = \frac{\mathrm{count}(t, d)}{\mathrm{tokens}(d)}
\qquad
\mathrm{idf}(t) = \ln\frac{N}{\mathrm{df}(t)}
\qquad
\mathrm{tfidf}(t, d) = \mathrm{tf}(t, d) \times \mathrm{idf}(t)
\]

- \(N\) is the number of documents in the collection.
- \(\mathrm{df}(t)\) is how many documents contain \(t\) at least once.
- Tokenization is lowercase alphanumeric words only (see [docs/known-quirks.md](docs/known-quirks.md)).

A term that appears in **every** document gets \(\mathrm{idf} = \ln 1 = 0\), so its tf-idf is zero. That is why `the`, `a`, and `and` vanish in `output/tfidf/` even though they dominate raw counts.

This is **raw (normalized) tf** times **smooth-less idf**. Libraries such as scikit-learn often use log-scaled tf, add-one smoothing, and an extra `+ 1` on idf. Rankings will not match those libraries exactly, and that is expected.

## Quick start

You need Perl 5. The second script also wants [`Text::CSV_XS`](https://metacpan.org/pod/Text::CSV_XS) because it treats the tab-separated `output/` files as CSV.

```bash
# 1. term frequencies + document frequencies + idf
perl tf-idf-values.pl

# 2. per-document tf * idf tables
perl 'tf*idf-product.pl'
```

The committed `output/` tree is already filled in, so you can study results without rerunning anything.

To list the most distinctive words in a precomputed file (no extra Perl modules):

```bash
python3 examples/top_terms.py output/tfidf/carroll-alice.txt --n 15
```

On this corpus that surfaces `alice`, `turtle`, `hatter`, `gryphon`, `dormouse` — the words that actually belong to Wonderland rather than to English in general.

A four-document teaching corpus, with a hand calculation you can check on paper, lives in [`examples/`](examples/):

```bash
python3 examples/run_toy_example.py
python3 examples/test_toy_example.py
```

## A taste of the Gutenberg results

Highest tf-idf terms from the committed tables (stopwords already sit at 0):

| Document | Distinctive terms |
| --- | --- |
| `carroll-alice.txt` | alice, gryphon, dormouse, duchess, hatter |
| `shakespeare-macbeth.txt` | macb, haue, macbeth, macd, rosse |
| `melville-moby_dick.txt` | whale, ahab, sperm, stubb, queequeg |
| `austen-emma.txt` | emma, harriet, weston, knightley, elton |
| `milton-paradise.txt` | thee, thou, heaven, thy, eve |

Shakespeare ranks **speech prefixes** (`macb`, `ham`, `bru`) and **old spelling** (`haue`, `vpon`) above most plot words. That is the tokenizer being literal, not a failure of idf. Details are in [docs/interpreting-results.md](docs/interpreting-results.md).

## Documentation map

1. [What tf-idf is doing](docs/tf-idf-explained.md)
2. [How the two Perl scripts fit together](docs/pipeline.md)
3. [The 18 Gutenberg texts](docs/corpus.md)
4. [How to read `output/`](docs/interpreting-results.md)
5. [Quirks worth knowing before you trust a ranking](docs/known-quirks.md)
6. [Line-by-line script notes](docs/script-reference.md)
7. [Formula variants (sklearn, BM25, cosine)](docs/formula-variants.md)
8. [Examples and the toy corpus](examples/README.md)

## License notes

The texts under `gutenberg/` are Project Gutenberg editions of public-domain works. Keep the source headers if you copy them elsewhere. The original Perl toy has no SPDX header; treat new example scripts in this tree as personal study code.
