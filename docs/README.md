# Documentation index

Personal notes that go with the Gutenberg TF-IDF toy project. Read these in
order if you are coming back to the repo after a long time.

| Doc | Purpose |
| --- | --- |
| [tf-idf-explained.md](tf-idf-explained.md) | The formula this repo actually uses, plus the common variants it does not use |
| [corpus-notes.md](corpus-notes.md) | The 18 NLTK Gutenberg files: sizes, genres, tokenizer traps |
| [perl-pipeline.md](perl-pipeline.md) | What `tf-idf-values.pl` and `tf*idf-product.pl` write, and where they disagree with the checked-in `output/` |
| [interpreting-scores.md](interpreting-scores.md) | How to read a row and how to rank terms without getting fooled by `1e-05` |
| [tokenizer-examples.md](tokenizer-examples.md) | Before / after on real Alice, Shakespeare, and Bible strings |

Runnable extras live under [`../examples/`](../examples/README.md), not here.
The examples consume the checked-in `output/` tables or the tiny teaching
corpus. They do not replace the Perl scripts.
