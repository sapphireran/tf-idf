# Documentation

These notes describe the **personal** tf-idf toy in this repository: two Perl scripts, an 18-document Gutenberg pocket corpus, and the precomputed `output/` tables.

They are written so you can reconstruct the 2012 experiment from the code that is actually in the tree. The original blog post is gone; nothing here depends on it.

| Note | What it covers |
| --- | --- |
| [tf-idf-explained.md](tf-idf-explained.md) | Intuition, the exact formulas this repo uses, and how they differ from library defaults |
| [pipeline.md](pipeline.md) | Directory layout, the two-script run, and what each output file is |
| [corpus.md](corpus.md) | Title, author, and size of every file under `gutenberg/` |
| [interpreting-results.md](interpreting-results.md) | How to read tf, df, idf, and tf-idf; real numbers from Alice, Macbeth, and Moby-Dick |
| [known-quirks.md](known-quirks.md) | Tokenization, empty tokens, `$#files` vs \(N\), scientific-notation `sort`, stopwords |
| [formula-variants.md](formula-variants.md) | This repo vs log-tf, smooth idf, sklearn, and cosine |
| [script-reference.md](script-reference.md) | Walkthrough of `tf-idf-values.pl` and `tf*idf-product.pl` |

Worked numbers on a four-document corpus, plus helper scripts, are under [`../examples/`](../examples/README.md).
