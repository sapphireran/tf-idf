# Personal TF-IDF notes

These pages describe the pipeline in this repository, not a generic textbook chapter. Numbers that mention Alice, Hamlet, or Moby-Dick come from the checked-in `output/` directory.

## Start here

1. [algorithm.md](algorithm.md) — what is being computed and why `the` disappears.
2. [tiny-corpus walkthrough](../examples/tiny-corpus/walkthrough.md) — three six-word documents, every intermediate value.
3. [interpreting-results.md](interpreting-results.md) — ranked terms from the 18-book run.

## Implementation notes

- [tokenization.md](tokenization.md) — the exact cleaning steps in `tf-idf-values.pl`.
- [pipeline.md](pipeline.md) — script order, directories, and the `tf*idf-product.pl` filename.
- [output-formats.md](output-formats.md) — column layouts for `tf/`, `df.txt`, `idf.txt`, `tfidf/`.
- [known-quirks.md](known-quirks.md) — `N`, Folio speaker tags, vanished apostrophes.

## Corpus

- [corpus.md](corpus.md) — file list, approximate token counts, and what each book is distinctive for.

## Code examples

- [../examples/README.md](../examples/README.md) — tiny corpus plus Python helpers.

The Python files are teaching copies. They are meant to be read next to the Perl, not to replace a production indexer.
