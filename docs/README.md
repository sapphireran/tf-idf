# Docs

Companion notes for the personal TF-IDF toy in this repository. Read
the [root README](../README.md) first if you just want commands to run.

| Doc | What it covers |
| --- | --- |
| [01-tfidf-in-plain-language.md](01-tfidf-in-plain-language.md) | Why term frequency is not enough, and what IDF changes |
| [02-original-pipeline.md](02-original-pipeline.md) | How the 2012 Perl scripts walk `gutenberg/` into `output/` |
| [03-gutenberg-corpus.md](03-gutenberg-corpus.md) | The 18 public-domain files and why they are a good demo |
| [04-interpreting-output.md](04-interpreting-output.md) | TSV layout, zeros, and how to rank the precomputed tables |
| [05-quirks-and-limitations.md](05-quirks-and-limitations.md) | Tokenizer traps, `$n = $#files`, speaker tags, boilerplate |
| [06-hand-worked-example.md](06-hand-worked-example.md) | Every fraction for a 3-document corpus |
| [07-tiny-corpus-walkthrough.md](07-tiny-corpus-walkthrough.md) | The five original vignettes, with token lists |
| [gutenberg-top-terms.md](gutenberg-top-terms.md) | Top 8 tf*idf terms for each Gutenberg file |
| [formula-cheatsheet.md](formula-cheatsheet.md) | The equations in one place |
| [08-tf-versus-tfidf.md](08-tf-versus-tfidf.md) | Side-by-side TF and tf*idf rankings |

Runnable copies of the pipeline live under [`../examples/`](../examples/README.md).
