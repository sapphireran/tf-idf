# Docs

Companion notes for the personal `tf-idf` toy that scores a folder of
Project Gutenberg texts. Read them in order if you are coming back to
the repo after a long time.

1. [What TF-IDF is](01-what-is-tf-idf.md) — the two factors, the log,
   and why `the` scores 0 on this corpus.
2. [Pipeline](02-pipeline.md) — how `tf-idf-values.pl` and
   `tf*idf-product.pl` write `output/`.
3. [Interpreting the Gutenberg results](03-interpreting-gutenberg.md) —
   real top terms for Alice, Moby-Dick, Macbeth, Emma, and Blake.
4. [Design notes](04-design-notes.md) — tokenization, `N`, glued
   words, speech prefixes, and `sort -n` vs `sort -g`.

A four-document worked example with original text (not Gutenberg) lives
in [examples/tiny-corpus/](../examples/tiny-corpus/).
