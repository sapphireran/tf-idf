# tf-idf

Personal toy project that walks a small [Project Gutenberg](https://www.gutenberg.org/) corpus through term frequency, inverse document frequency, and their product. The original two Perl scripts accompany a blog-post writeup of the same experiment.

This repository is **personal study code**, not a library. The scripts write tab-separated text files so you can inspect every intermediate number. The `docs/` and `examples/` trees expand that experiment into a readable pipeline, a worked calculation, and helpers that rank the precomputed scores.

## What the experiment measures

TF-IDF scores a word higher when it is common *inside one document* and rare *across the rest of the collection*. In this corpus that surfaces character names and setting words (`alice`, `ahab`, `emma`, `pequod`) instead of function words (`the`, `and`, `of`), which appear in every file and therefore get an IDF of zero.

The implementation is deliberately small:

1. `tf-idf-values.pl` tokenizes every file in `gutenberg/`, writes a per-document term-frequency table, then writes collection-wide document frequency and IDF tables.
2. `tf*idf-product.pl` multiplies each document's TF by the matching IDF and writes a TF-IDF table per file.

See [docs/algorithm.md](docs/algorithm.md) for the exact formulas, including the quirks that come from matching the original scripts.

## Repository layout

```text
.
├── tf-idf-values.pl      # TF, DF, and IDF over gutenberg/
├── tf*idf-product.pl     # TF × IDF per document
├── gutenberg/            # 18 public-domain texts
├── output/
│   ├── tf/               # normalized term frequency per document
│   ├── tfidf/            # TF-IDF per document
│   ├── df.txt            # word → document count + source file names
│   ├── df-sorted.txt     # same DF table, easier to scan
│   └── idf.txt           # word → ln(N / df)
├── docs/                 # algorithm, corpus, output formats
└── examples/             # tiny corpus, worked math, ranking helpers
```

## Requirements

- Perl 5 (the scripts use `strict` only; no CPAN modules in `tf-idf-values.pl`)
- `Text::CSV_XS` for `tf*idf-product.pl` (tab-separated parse of the TF and IDF tables)

The ranking helpers under `examples/` stay on core Perl so they run without extra modules.

## Run the Gutenberg pipeline

From the repository root:

```bash
mkdir -p output/tf output/tfidf
perl tf-idf-values.pl
perl 'tf*idf-product.pl'
```

The product script is named `tf*idf-product.pl`. Quote or escape the `*` so the shell does not glob it.

Re-running both scripts overwrites `output/`. The committed tables are the snapshot from the original experiment; keep a copy if you want to compare a new run against that snapshot.

To inspect the existing snapshot without recomputing:

```bash
perl examples/top-terms.pl --n 15 output/tfidf/carroll-alice.txt
perl examples/lookup-term.pl alice whale emma the
```

## Run the tiny worked example

The Gutenberg texts are large. `examples/toy-corpus/` is four short original documents so you can finish a run in about a second and check the arithmetic by hand:

```bash
perl examples/toy-tfidf.pl
perl examples/top-terms.pl --n 8 --dir examples/toy-output/tfidf
```

The hand calculation that matches those numbers is in [examples/worked-example.md](examples/worked-example.md).

## Reading the precomputed scores

Highest TF-IDF terms from the committed Gutenberg snapshot:

| Document | Distinctive terms |
| --- | --- |
| `carroll-alice.txt` | alice, gryphon, duchess, dormouse, hatter |
| `melville-moby_dick.txt` | whale, ahab, sperm, stubb, queequeg |
| `austen-emma.txt` | emma, harriet, weston, knightley, elton |
| `blake-poems.txt` | thel, weep, lyca, thee, vales |
| `shakespeare-hamlet.txt` | ham, haue, hor, qu, laer (speaker prefixes + original spelling) |
| `bible-kjv.txt` | unto, israel, saith, thee, david |

`the`, `and`, `of`, and `a` have IDF `0` because they occur in every document, so their TF-IDF is also `0` everywhere. Play texts promote abbreviated speaker tags (`ham`, `hor`) because those tokens are frequent in one file and rare elsewhere. [docs/interpreting-results.md](docs/interpreting-results.md) covers those cases.

## Documentation

| Document | Contents |
| --- | --- |
| [docs/algorithm.md](docs/algorithm.md) | Tokenization, TF, DF, IDF, TF-IDF, and implementation notes |
| [docs/corpus.md](docs/corpus.md) | The 18 Gutenberg files and why they are a useful mix |
| [docs/outputs.md](docs/outputs.md) | Table formats and directory contract |
| [docs/interpreting-results.md](docs/interpreting-results.md) | How to read high, low, and zero scores |
| [docs/adding-texts.md](docs/adding-texts.md) | Drop in a new `.txt` file and rebuild |
| [examples/README.md](examples/README.md) | Toy corpus, helpers, and sample commands |

## License notes

The texts under `gutenberg/` come from Project Gutenberg and are in the public domain in the United States. The scripts and documentation in this repository are personal study material.
