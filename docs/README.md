# Docs

Teaching notes for this personal tf-idf toy. Read in this order if you are new to the repo:

1. [../README.md](../README.md) — map of the tree and the formulas the scripts actually use.
2. [tf-idf-explained.md](tf-idf-explained.md) — what the score measures, and what it does not.
3. [../examples/hand-calculation.md](../examples/hand-calculation.md) — three sentences, every float. Source files live in [../examples/hand-calculation/](../examples/hand-calculation/).
4. [../examples/tiny-corpus/README.md](../examples/tiny-corpus/README.md) — five original short documents and the Python helper.
5. [pipeline.md](pipeline.md) — the two Perl scripts, including the \(N\) quirk.
6. [corpus.md](corpus.md) — the 18 Gutenberg files.
7. [interpreting-results.md](interpreting-results.md) — how to read Alice / *Moby-Dick* / *Hamlet* / *Emma* / Blake.
8. [gutenberg-top-terms.md](gutenberg-top-terms.md) — top 10 for every file in the snapshot.
9. [idf-variants.md](idf-variants.md) — raw `ln(N/df)` vs smoothed / probabilistic / BM25-style idf.

Nothing here is a product spec. If a sentence disagrees with `tf-idf-values.pl`, the script wins until someone changes both.
