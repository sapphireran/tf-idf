# Documentation

Personal notes for the TF-IDF toy in this repository. Read them in this
order if you are new to the checkout:

1. [`../README.md`](../README.md) — layout, formulas, how to run things
2. [`tf-idf-explained.md`](tf-idf-explained.md) — TF, DF, IDF, TF-IDF, and
   the variants this project does not use
3. [`pipeline.md`](pipeline.md) — the two Perl scripts and their outputs
4. [`tokenizer-and-quirks.md`](tokenizer-and-quirks.md) — preprocessing, `N`,
   and the dirty `thatyou` row
5. [`corpus.md`](corpus.md) — the 18 Gutenberg files
6. [`interpreting-output.md`](interpreting-output.md) — how to read the TSV
   files without a bogus string sort
7. [`idf-selected-terms.md`](idf-selected-terms.md) — lookup table of
   interesting `df` / `idf` values

Worked numbers live under [`../examples/`](../examples/), including a
four-document corpus you can finish with a pencil.
