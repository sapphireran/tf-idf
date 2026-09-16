# Gutenberg shelf

Eighteen public-domain files. Token counts below use the same Perl-compatible
tokenizer as `tf-idf-values.pl` (denominator `word_count`, not a Unicode
word-breaker).

| File | Work (short) | Tokens | Types |
| --- | --- | ---: | ---: |
| `austen-emma.txt` | Austen, *Emma* | 158,176 | 9,312 |
| `austen-persuasion.txt` | Austen, *Persuasion* | 83,307 | 5,990 |
| `austen-sense.txt` | Austen, *Sense and Sensibility* | 118,826 | 7,335 |
| `bible-kjv.txt` | King James Bible | 821,131 | 16,567 |
| `blake-poems.txt` | Blake, *Songs* and *Thel* | 7,769 | 1,542 |
| `bryant-stories.txt` | Bryant, children’s stories | 46,296 | 4,011 |
| `burgess-busterbrown.txt` | Burgess, *Buster Brown* | 15,901 | 1,568 |
| `carroll-alice.txt` | Carroll, *Alice’s Adventures in Wonderland* | 26,576 | 2,753 |
| `chesterton-ball.txt` | Chesterton, *The Ball and the Cross* | 81,636 | 8,646 |
| `chesterton-brown.txt` | Chesterton, Father Brown | 72,764 | 8,235 |
| `chesterton-thursday.txt` | Chesterton, *The Man Who Was Thursday* | 57,916 | 6,524 |
| `edgeworth-parents.txt` | Edgeworth, *The Parent’s Assistant* | 166,197 | 9,561 |
| `melville-moby_dick.txt` | Melville, *Moby-Dick* | 212,014 | 19,961 |
| `milton-paradise.txt` | Milton, *Paradise Lost* | 79,768 | 9,321 |
| `shakespeare-caesar.txt` | Shakespeare, *Julius Caesar* | 21,239 | 3,091 |
| `shakespeare-hamlet.txt` | Shakespeare, *Hamlet* | 30,669 | 4,799 |
| `shakespeare-macbeth.txt` | Shakespeare, *Macbeth* | 18,370 | 3,560 |
| `whitman-leaves.txt` | Whitman, *Leaves of Grass* | 125,192 | 14,568 |
| **shelf** | | **2,143,747** | **137,344 type-in-doc cells** |

The Bible is about **38%** of every token on the shelf. A term that is merely
common in the KJV can still pick up a modest IDF if it is rare in the novels.
The opposite is more visible: a hapax in Blake (`thel`) outranks most of
Blake’s English because `df = 1` and the file is short.

## What actually ranks high

Top gold TF-IDF terms (classic weights) are mostly **names and tags**, not
themes:

| Book | High weights |
| --- | --- |
| Alice | `alice`, `gryphon`, `dormouse`, `duchess`, `hatter` |
| Macbeth | `macb`, `haue`, `macbeth`, `macd`, `rosse` |
| Moby-Dick | `whale`, `ahab`, `sperm`, `stubb`, `queequeg` |
| Emma | `emma`, `harriet`, `weston`, `knightley`, `elton` |
| Blake | `thel`, `weep`, `lyca`, `thee`, `vales` |

Macbeth’s leader is the speaker prefix `macb`, not the word *macbeth*.
Folio spellings (`haue`, `vpon`, `vs`) share a three-play IDF and still
outrank modern synonyms because the First Folio texts were not normalized.
See [06-quirks.md](06-quirks.md).

## How to read a gold file

```bash
# Highest TF-IDF in Alice (gold table, no recompute)
python3 -m querydesk top --doc carroll-alice.txt --n 15

# Same idea for any other stem in output/tfidf/
python3 -m querydesk top --doc milton-paradise.txt --n 10
```

`top` reads `output/tfidf/` directly, so it stays faithful to the 2012
product even if you later experiment with `--variant smooth` on queries.
