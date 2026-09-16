# Tiny five-document corpus

Five original vignettes used by `examples/tfidf_toy.py` and
`examples/tiny_tfidf.pl`. They are short on purpose: every token list
fits in `docs/07-tiny-corpus-walkthrough.md`.

| File | About | Distinctive headword |
| --- | --- | --- |
| `kitchen.txt` | a cook and a pot of soup | `soup` |
| `garden.txt` | roses along a fence | `roses` |
| `harbor.txt` | a boat in fog | `boat` |
| `workshop.txt` | oak becoming a shelf | `oak` |
| `stars.txt` | a telescope on a hill | `hill` |

Shared glue words (`the`, and in this set `a` in some files) are
deliberate. After IDF, `the` scores 0 because it appears in all five
texts. Words that happen to occur in only one vignette still get the
maximum IDF even when they are not topical (`at` in the garden piece,
`and` in the kitchen piece). That is the whole point of keeping the
example small: the ranking is honest, including the awkward bits.

These files are not from Project Gutenberg. The Gutenberg texts stay
under `gutenberg/` at the repository root.
