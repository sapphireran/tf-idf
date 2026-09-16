# 00 — Lab index

Personal information-retrieval notebook. The through-line is one
question: **how does a raw word count become a weight that can tell
books apart?**

I am using the eighteen Gutenberg files already in this repository as a
fixed shelf, plus a four-document toy corpus whose arithmetic I can do
on paper. Nothing here is trained. Everything is counted.

## Reading order

| Note | Title | Why it exists |
| --- | --- | --- |
| [01](01-tf-idf-from-scratch.md) | TF-IDF from scratch | Definitions, SMART-style variants, the product |
| [02](02-corpus-notes.md) | The Gutenberg shelf | What the eighteen files are, and what they are not |
| [03](03-original-perl-walkthrough.md) | The 2012 Perl specimen | How the original scripts tokenize, count, and slip |
| [04](04-worked-example-tiny-corpus.md) | Worked example | Every TF, DF, IDF, and product on four short texts |
| [05](05-idf-smoothing-variants.md) | IDF smoothings | `log(N/df)`, plus-one, probabilistic, BM25-style |
| [06](06-ranking-and-cosine.md) | Ranking and cosine | Turning weights into a query-vs-document score |
| [07](07-tokenization-and-stopwords.md) | Tokens and stopwords | Why `1murth` appears in Macbeth and `the` scores 0 |
| [08](08-gutenberg-lab-notes.md) | Shelf observations | Distinctive terms and query sanity checks |
| [09](09-limitations-and-next.md) | Limits and next steps | What this lab cannot claim |
| [10](10-glossary.md) | Glossary | Short definitions I kept mixing up |
| [11](11-further-reading.md) | Further reading | Public papers and books, not workplace docs |

## How I use the Python lab

The package under `tfidf/` is a notebook companion, not a library I
would ship. It has three jobs:

1. Reproduce the *spirit* of the Perl pipeline (normalized TF ×
   `log(N / df)`).
2. Show neighboring formulas on the same tokens so the differences are
   visible.
3. Rank a query against either `examples/tiny_corpus/` or `gutenberg/`.

See the repository [README](../README.md) for commands.

## Lab rules I am keeping

- Public-domain or self-written text only.
- Closed-form tests for every weight I claim to understand.
- When the Perl and the Python disagree, write down *why* before
  "fixing" either side.
- Do not quietly upgrade this into a search product.
