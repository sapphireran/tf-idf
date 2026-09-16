# Examples

Small, personal walkthroughs that sit next to the original Perl
scripts. Nothing here is a rewrite of the Gutenberg run; the checked-in
`output/` directory is still the result of `tf-idf-values.pl` followed
by `tf*idf-product.pl`.

| Path | What it is |
| --- | --- |
| [tiny-corpus/](tiny-corpus/) | Four original micro-documents, a Python runner that mirrors the Perl math, and a fully worked calculation |
| [rank_terms.py](rank_terms.py) | Rank a `term<TAB>score` file with real floating-point order |

## Tiny corpus

Four short texts I wrote for this repo: a cat named Miso, a loaf of
bread, a night with a telescope, and a tomato-and-basil garden. Shared
function words (`the`, `a`, `on`) appear in every document and get
IDF 0. Distinctive words (`moth`, `baker`, `saturn`, `tomato`) appear
in one document and get IDF `ln(4) ≈ 1.386`.

```bash
python3 examples/tiny-corpus/run_tfidf.py --check
```

The runner prints a ranked table per document. `--check` asserts the
identities used in [tiny-corpus/README.md](tiny-corpus/README.md).
`--write-expected` refreshes the TSV snapshots under
`tiny-corpus/expected/`.

## Ranking the Gutenberg output

The Perl scripts write scientific notation for small scores. `sort -n`
on those files is wrong; `9.89e-05` is read as `9.89`.

```bash
# real top terms for Alice
python3 examples/rank_terms.py output/tfidf/carroll-alice.txt -n 12

# terms that characterize Moby-Dick against Alice
python3 examples/rank_terms.py output/tfidf/melville-moby_dick.txt \
    --versus output/tfidf/carroll-alice.txt -n 12

# equivalent shell, if you prefer
sort -t$'\t' -k2,2g output/tfidf/carroll-alice.txt | tail
```

On this corpus the true peaks are character names and setting words
(`alice`, `gryphon`, `whale`, `ahab`, `macbeth`, `emma`), not the
mid-list tokens that a naive `sort -n` surfaces. The interpretation
write-up is in [docs/03-interpreting-gutenberg.md](../docs/03-interpreting-gutenberg.md).

From the repo root, `python3 examples/test_examples.py` checks the
tiny-corpus identity, Alice's top term, and the Moby-Dick contrast.

## What these examples are not

- Not a second copy of the Project Gutenberg texts.
- Not a drop-in replacement for the Perl scripts on the full corpus.
- Not a production search engine. There is no stopword list, no
  stemming, and no add-one smoothing. That is the point of the toy:
  you can see every term and every score.
