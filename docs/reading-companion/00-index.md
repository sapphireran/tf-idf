# Reading companion — index

These notes use the checked-in TF-IDF snapshot as a personal reading
aid for the eighteen Gutenberg files. They are not a second copy of
an information-retrieval textbook. The questions are literary and
empirical:

- Why does a short children's book outrank *Paradise Lost* on its
  own top term?
- Why do the three Shakespeare plays look more like each other than
  the three Austens do?
- Why does Maria Edgeworth sit closer to Austen than Austen sits to
  Austen?
- Why do `ebook` and `gutenberg` crack the top ten of *The Ball and
  the Cross*?
- Why does a query of `the and of` retrieve nothing?

Every number below was measured on `output/tfidf/` in this checkout.
If a script and a paragraph disagree, believe the script and file a
note — the snapshot is the source of truth.

## Map

| Note | What it is for |
| --- | --- |
| [01 How these weights read](01-how-these-weights-read.md) | The exact product, zero-IDF stopwords, and the one corrupt IDF line |
| [02 Length and name bias](02-length-and-name-bias.md) | Why `buster` (0.040) dwarfs `whale` (0.005) |
| [03 Shakespeare Folio spellings](03-shakespeare-folio-spellings.md) | `haue`, `vpon`, speaker tags |
| [04 Austen and Edgeworth](04-austen-edgeworth-manners.md) | Domestic-fiction cluster, and why Austen does not self-cluster |
| [05 Chesterton](05-chesterton-names-and-trailers.md) | One-off names plus a Gutenberg trailer |
| [06 Archaic-pronoun corridor](06-archaic-pronoun-corridor.md) | Bible → Milton → Blake → Whitman |
| [07 Similarity map](07-similarity-map.md) | All 153 pairwise cosines |
| [08 Term atlas](08-term-atlas.md) | Top terms for every book, annotated |
| [09 Query cookbook](09-query-cookbook.md) | Worked queries against the snapshot |
| [10 Exercises](10-exercises.md) | Problems that stay inside this shelf |
| [11 Answers](11-answers.md) | Worked solutions |

Scripts live in [`examples/reading-companion/`](../../examples/reading-companion/README.md).

## Shelf at a glance

| File | Work | Approx. words | Top term | Score |
| --- | --- | ---: | --- | ---: |
| `austen-emma.txt` | *Emma* | 158,167 | emma | 0.01043 |
| `austen-persuasion.txt` | *Persuasion* | 83,308 | elliot | 0.00881 |
| `austen-sense.txt` | *Sense and Sensibility* | 118,675 | elinor | 0.01503 |
| `bible-kjv.txt` | King James Bible | 821,133 | unto | 0.01204 |
| `blake-poems.txt` | Blake poems | 6,845 | thel | 0.00558 |
| `bryant-stories.txt` | Bryant stories | 45,988 | margery | 0.00375 |
| `burgess-busterbrown.txt` | *The Adventures of Buster Bear* | 15,870 | buster | 0.04035 |
| `carroll-alice.txt` | *Alice's Adventures in Wonderland* | 26,443 | alice | 0.02596 |
| `chesterton-ball.txt` | *The Ball and the Cross* | 81,598 | turnbull | 0.01795 |
| `chesterton-brown.txt` | Father Brown | 71,626 | flambeau | 0.00489 |
| `chesterton-thursday.txt` | *The Man Who Was Thursday* | 57,955 | syme | 0.02435 |
| `edgeworth-parents.txt` | *The Parent's Assistant* | 166,070 | cecilia | 0.00268 |
| `melville-moby_dick.txt` | *Moby-Dick* | 212,030 | whale | 0.00494 |
| `milton-paradise.txt` | *Paradise Lost* | 79,659 | thee | 0.00220 |
| `shakespeare-caesar.txt` | *Julius Caesar* (Folio) | 20,459 | bru | 0.02082 |
| `shakespeare-hamlet.txt` | *Hamlet* (Folio) | 29,605 | ham | 0.01408 |
| `shakespeare-macbeth.txt` | *Macbeth* (Folio) | 17,741 | macb | 0.02156 |
| `whitman-leaves.txt` | *Leaves of Grass* | 122,070 | o | 0.00183 |

Word counts are whitespace splits of the raw files, including any
Project Gutenberg header or trailer. Scores are the snapshot's
already-normalized TF times natural-log IDF.
