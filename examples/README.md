# Examples

Runnable companions to the Gutenberg snapshot. Nothing here writes into `output/` unless you point a helper at those files on purpose.

## Tiny corpus

`toy-corpus/` is four short original documents (cat, harbor, bakery, observatory). They share `the` and `a`, share a couple of mid-frequency words (`wind`, `would`), and otherwise use disjoint vocabularies so the ranked lists are obvious.

```bash
perl examples/toy-tfidf.pl
perl examples/top-terms.pl --n 8 --dir examples/toy-output/tfidf
perl examples/lookup-term.pl --df examples/toy-output/df.txt \
    --idf examples/toy-output/idf.txt \
    --tfidf-dir examples/toy-output/tfidf \
    cat the wind schooner rye comet
```

`toy-tfidf.pl` rebuilds `examples/toy-output/` each run. The hand math is in [worked-example.md](worked-example.md).

| Script | Role |
| --- | --- |
| `toy-tfidf.pl` | Full TF → DF → IDF → TF-IDF on the toy corpus (core Perl only) |
| `top-terms.pl` | Sort any token/score table by score |
| `lookup-term.pl` | Print DF, IDF, and per-document TF-IDF for named tokens |

## Gutenberg snapshot (no recompute)

The committed `output/tfidf/` tables are already ranked raw by token. These commands only read them:

```bash
perl examples/top-terms.pl --n 15 output/tfidf/carroll-alice.txt
perl examples/top-terms.pl --n 10 --dir output/tfidf
perl examples/lookup-term.pl alice whale emma the ham hamlet
```

A reading of those lists is in [gutenberg-reading-notes.md](gutenberg-reading-notes.md).

## Add a fifth toy document

1. Write `examples/toy-corpus/your-topic.txt` (public-domain or original text only).
2. Run `perl examples/toy-tfidf.pl`.
3. `N` becomes 5, so every IDF changes. Unique words in the old files get `ln(5/1)` instead of `ln(4/1)`.

Use this path when you want to experiment. Leave `gutenberg/` alone until you intend to rebuild the large snapshot.

## Flags

```text
perl examples/toy-tfidf.pl --help
perl examples/top-terms.pl --help
perl examples/lookup-term.pl --help
```
