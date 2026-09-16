# Tiny corpus: four short original notes

These four documents are original prose written for this repository. They
are not Project Gutenberg texts. Each note leans on a tight vocabulary so
TF-IDF has something obvious to reward.

| file | topic | words you should see near the top |
| --- | --- | --- |
| `cats.txt` | a windowsill calico | `miso`, `whiskers`, `moths`, `calico`, `purr` |
| `sourdough.txt` | feeding a jar and baking | `levain`, `gluten`, `crumb`, `dutch`, `oven` |
| `harbor.txt` | a skiff at low tide | `jib`, `barnacles`, `mooring`, `keel`, `tide` |
| `jupiter.txt` | a fire-escape observing night | `ganymede`, `telescope`, `belts`, `opposition`, `jupiter` |

Shared English (`the`, `and`, `i`, `a`) appears in every note. With raw IDF
those terms get `log(4/4) = 0` and disappear from the ranking. That is the
whole demonstration.

## Commands

```bash
# markdown report with top terms and pairwise cosine
python3 -m tfidf report examples/tiny-corpus --n 8

# rank notes against a query
python3 -m tfidf query examples/tiny-corpus "ganymede telescope opposition"
python3 -m tfidf query examples/tiny-corpus "levain gluten crumb"

# write TSV tables in the same layout as output/
python3 -m tfidf compute examples/tiny-corpus -o examples/tiny-corpus/output
```

`examples/tiny-corpus/output/` is gitignored. Re-run `compute` whenever you
want a fresh dump.

## What "good" looks like

1. Each note's top term is a topical noun, not a function word.
2. The Jupiter query ranks `jupiter.txt` first.
3. Pairwise cosine stays modest. The notes do not share plot, only grammar.

`tests/test_compute.py` encodes (1) and (2). If you edit the prose, keep
those distinctive nouns or update the tests.

## Why not use the Gutenberg files here?

The Gutenberg texts are huge and already have committed `output/tfidf/`
tables. This folder exists so a new reader can finish the arithmetic, and
the tests, in a few seconds. For the large corpus see
`docs/interpreting-gutenberg.md` and:

```bash
python3 -m tfidf top-tsv output/tfidf --n 10
```
