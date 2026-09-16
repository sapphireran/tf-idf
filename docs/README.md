# Personal notes for this tf-idf lab

These pages explain the toy collection that already lives in this
repository: eighteen public-domain books, two Perl scripts, and the
precomputed tables under `output/`. Nothing here is product or company
code. It is a personal walkthrough of one classic ranking idea.

Start here:

1. [What tf-idf is measuring](01-what-is-tf-idf.md)
2. [Formulas used in this repo](03-formulas.md)
3. [Tokenization](02-tokenization.md)
4. [How the Perl pipeline is wired](04-this-repo-pipeline.md)
5. [The Gutenberg sample](05-gutenberg-corpus.md)
6. [How to read a score](06-interpreting-scores.md)
7. [Nearby variants](07-algorithm-variants.md)
8. [A three-sentence worked example](08-worked-example.md)
9. [Reproducing the numbers](09-reproducing-results.md)

There is also a [glossary](glossary.md) for the short names that show
up in the scripts.

Runnable companions live in [`examples/`](../examples/README.md):

- a five-document original corpus with committed TSV tables
- a Python reference that matches the intended scoring
- a classroom example that prints every cell
- a reader for the committed Gutenberg `output/tfidf/` files
