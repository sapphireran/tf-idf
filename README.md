# tf-idf

Personal toy for **term frequency × inverse document frequency** on a
folder of public-domain Project Gutenberg texts. The original two Perl
scripts (2012) still produce the checked-in tables in `output/`. This
checkout adds worked notes, a three-document corpus you can score by
hand, and small Python CLIs that read those tables without rerunning
Perl.

The texts are public-domain NLTK Gutenberg extracts. There is no
company, client, or private data in this repository.

## What is in the box

```
gutenberg/                 18 public-domain books (NLTK-style names)
tf-idf-values.pl           tokenize → TF, DF, IDF
tf*idf-product.pl          TF × IDF
output/tf/                 per-document term frequencies
output/idf.txt             collection IDF, N = 18
output/tfidf/              the products the blog post ranked
docs/                      math, pipeline, corpus, quirks
examples/                  mini corpora + ranking / tracing CLIs
tests/                     unittest checks for the toy math
```

## The formula

\[
\mathrm{tf}(t, d) = \frac{\text{count}(t, d)}{|d|}
\qquad
\mathrm{idf}(t) = \ln\frac{N}{\mathrm{df}(t)}
\qquad
\mathrm{tfidf}(t, d) = \mathrm{tf}(t, d) \times \mathrm{idf}(t)
\]

`the` appears in all 18 books, so its IDF is 0. `alice` appears in 3,
so its IDF is \(\ln(18/3)\). In `carroll-alice.txt` that product is
the top score. The full derivation, including a three-sentence
walkthrough, is [docs/tf-idf-math.md](docs/tf-idf-math.md).

## Quick start (no Perl)

From the repository root, Python 3 stdlib only:

```bash
# Every number in the math notes, printed as tables
python3 examples/mini_tfidf.py examples/mini_corpus/three_docs

# Rank the committed Gutenberg products
python3 examples/rank_terms.py --input-dir output/tfidf --top 12

# Trace one token through DF / IDF / each book
python3 examples/follow_word.py alice

# Pairwise cosine on the 18 scored books
python3 examples/cosine_similarity.py --from-output output/tfidf --top-pairs 10

python3 -m unittest discover -s tests -v
```

## Quick start (original Perl)

```bash
perl tf-idf-values.pl          # writes output/tf, output/df.txt, output/idf.txt
perl 'tf*idf-product.pl'       # writes output/tfidf  (needs Text::CSV_XS)
```

A fresh run of `tf-idf-values.pl` does **not** automatically reproduce
the committed IDF table. The script uses `$#files` after `readdir`,
which counts `.` / `..` / `.DS_Store`; the tables in `output/` were
corrected to \(N = 18\) in 2012. Details:
[docs/quirks-and-variants.md](docs/quirks-and-variants.md). Prefer the
Python examples if you want the math without regenerating megabytes of
TSV.

## Documentation

- [docs/tf-idf-math.md](docs/tf-idf-math.md) — formula and hand calculation
- [docs/perl-pipeline.md](docs/perl-pipeline.md) — how the two scripts work
- [docs/corpus.md](docs/corpus.md) — the 18 files
- [docs/reading-results.md](docs/reading-results.md) — how to read a ranking
- [docs/quirks-and-variants.md](docs/quirks-and-variants.md) — \(N\), tokenization, variants
- [examples/README.md](examples/README.md) — CLIs and mini corpora
- [examples/walkthroughs/alice_through_the_pipeline.md](examples/walkthroughs/alice_through_the_pipeline.md)
- [examples/walkthroughs/gutenberg_top_terms.md](examples/walkthroughs/gutenberg_top_terms.md)
- [examples/walkthroughs/three_docs_by_hand.md](examples/walkthroughs/three_docs_by_hand.md)

## What the Gutenberg rankings look like

Characteristic top terms from the committed run (not a gold label):

| Book | Distinctive tokens |
| --- | --- |
| *Emma* | emma, harriet, weston, knightley |
| *Alice* | alice, gryphon, duchess, dormouse, hatter |
| *Moby-Dick* | whale, ahab, sperm, stubb, queequeg |
| *Thursday* | syme, gregory, professor |
| *Buster Bear* | buster, browns, joe, blacky |
| *Hamlet* (this file) | ham, haue, hor — speech prefixes, not plot words |
| KJV | unto, israel, saith — archaic glue mixed with names |

That last pair is the point of the reading notes: TF-IDF describes
this collection, not English, and it believes whatever tokens the
tokenizer emitted.

## License and scope

Hobby / blog-post code plus personal documentation. Gutenberg extracts
are public domain. Do not drop private or employer corpora into
`gutenberg/` on this branch.
