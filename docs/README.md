# Documentation

Personal notes for the `tf-idf` toy: the 2012 Perl scripts, the committed Gutenberg tables, and the later examples.

Read these in order if you are new to the repo:

| # | Note | Use it when |
| --- | --- | --- |
| 1 | [tf-idf-explained.md](tf-idf-explained.md) | You want the formula and a reason the common words score 0 |
| 2 | [pipeline-and-scripts.md](pipeline-and-scripts.md) | You want to know what each Perl script writes |
| 3 | [reading-the-outputs.md](reading-the-outputs.md) | You are opening files under `output/` |
| 4 | [gutenberg-term-walkthrough.md](gutenberg-term-walkthrough.md) | You want a reading of Alice, Ahab, Emma, Macbeth, … |
| 5 | [document-vectors-and-similarity.md](document-vectors-and-similarity.md) | You want cosine similarity on the same weights |
| 6 | [formula-and-implementation-notes.md](formula-and-implementation-notes.md) | You want the `$#files` / empty-token / corrupt-line caveats |

Runnable counterparts live under [`../examples/`](../examples/README.md). Measured Gutenberg cosines are in [`../examples/gutenberg-similarity.md`](../examples/gutenberg-similarity.md).
