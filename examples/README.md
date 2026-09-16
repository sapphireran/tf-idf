# Examples

Personal, stdlib-only companions to the 2012 Perl scripts. They do not
replace those scripts and they do not rewrite `output/`. They exist so
you can:

1. Reproduce the formula on a corpus small enough to check by hand.
2. Rank the alphabetical Gutenberg dumps.
3. Trace one token through DF → IDF → TF → product.
4. Compare documents with cosine similarity.

## Layout

| Path | What it is |
| --- | --- |
| `mini_corpus/three_docs/` | Three sentences. Every number is in the math notes and in the tests. |
| `mini_corpus/literary_snippets/` | Alice / Ishmael / Hamlet pastiches. Qualitative demo. |
| `tfidf_lib.py` | Tokenizer, TF, IDF variants, cosine, TSV helpers. |
| `mini_tfidf.py` | CLI that prints IDF and per-document rankings for a folder. |
| `rank_terms.py` | CLI that sorts `output/tf` or `output/tfidf`. |
| `follow_word.py` | CLI that traces one token through the committed tables. |
| `cosine_similarity.py` | CLI for pairwise cosine, from raw text or from scored TSV. |
| `walkthroughs/` | Prose that cites real rows from `output/`. |

## Commands

All commands assume the repository root.

```bash
# Hand-checkable toy (raw TF × ln(N/df), N = 3)
python3 examples/mini_tfidf.py examples/mini_corpus/three_docs

# Same math, slightly longer snippets
python3 examples/mini_tfidf.py examples/mini_corpus/literary_snippets --top 8

# Teaching variants (see docs/quirks-and-variants.md)
python3 examples/mini_tfidf.py examples/mini_corpus/three_docs --variant smooth
python3 examples/mini_tfidf.py examples/mini_corpus/three_docs --variant log_tf

# Rank the 2012 Gutenberg products
python3 examples/rank_terms.py --input-dir output/tfidf --top 12
python3 examples/rank_terms.py --only carroll-alice.txt --top 15

# Follow one token
python3 examples/follow_word.py alice
python3 examples/follow_word.py the
python3 examples/follow_word.py unto

# Similarities
python3 examples/cosine_similarity.py --corpus examples/mini_corpus/three_docs
python3 examples/cosine_similarity.py --from-output output/tfidf --top-pairs 15
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The tests lock the three-document products, the cosine order, the
Perl-like tokenizer on a few punctuation cases, and a couple of
Gutenberg sanity checks (`alice` IDF, `the` IDF = 0, Alice's top
term). They read `output/` but never write it.

## What this is not

- Not a production search engine.
- Not a port that bit-identical-replaces the Perl on the full corpus
  (whitespace classes and `$word_count` placement can still differ on
  odd files). The Gutenberg *tables* are treated as ground truth for
  the walkthroughs.
- Not company or client code. The corpus is public-domain NLTK
  Gutenberg extracts plus original toy sentences.

On the committed Gutenberg vectors, cosine ranks Shakespeare plays
together and ranks each Austen novel nearer Edgeworth than the other
Austens. Unique character names are strong labels and weak
same-author features. The walkthroughs call that out instead of
pretending authorship clustering falls out for free.
