# 02 — The Gutenberg shelf

Eighteen public-domain texts, already sitting in `gutenberg/`. I am
not adding books in this pass. A fixed shelf keeps IDF tables
comparable to the historical `output/` snapshot.

## The eighteen

| File | Bracketed title line | Rough kind |
| --- | --- | --- |
| `austen-emma.txt` | Emma, Jane Austen, 1816 | Novel |
| `austen-persuasion.txt` | Persuasion, Jane Austen, 1818 | Novel |
| `austen-sense.txt` | Sense and Sensibility, Jane Austen, 1811 | Novel |
| `bible-kjv.txt` | King James Bible | Scripture, very long |
| `blake-poems.txt` | Poems, William Blake, 1789 | Short verse |
| `bryant-stories.txt` | Stories to Tell to Children, Sara Cone Bryant, 1918 | Children's stories |
| `burgess-busterbrown.txt` | The Adventures of Buster Bear, Thornton W. Burgess, 1920 | Children's animal story |
| `carroll-alice.txt` | Alice's Adventures in Wonderland, Lewis Carroll, 1865 | Children's novel |
| `chesterton-ball.txt` | The Ball and the Cross, G. K. Chesterton, 1909 | Novel |
| `chesterton-brown.txt` | The Wisdom of Father Brown, G. K. Chesterton, 1914 | Detective stories |
| `chesterton-thursday.txt` | The Man Who Was Thursday, G. K. Chesterton, 1908 | Novel |
| `edgeworth-parents.txt` | The Parent's Assistant, Maria Edgeworth | Moral tales |
| `melville-moby_dick.txt` | Moby Dick, Herman Melville, 1851 | Novel |
| `milton-paradise.txt` | Paradise Lost, John Milton, 1667 | Epic verse |
| `shakespeare-caesar.txt` | Julius Caesar, 1599 | Play |
| `shakespeare-hamlet.txt` | Hamlet, 1599 | Play |
| `shakespeare-macbeth.txt` | Macbeth, 1603 | Play |
| `whitman-leaves.txt` | Leaves of Grass, Walt Whitman, 1855 | Verse |

Dates in the title lines are the ones printed in these files, not a
scholarly census.

## Why this shelf is a good toy and a bad universe

Good toy:

- Every file is readable English (or Early Modern English, or verse).
- Lengths span a useful range: Blake and Burgess are short; the KJV
  and *Moby-Dick* are not.
- Several natural clusters exist (three Austens, three Chestertons,
  three Shakespeare plays). IDF inside a cluster is harsher on words
  those books share (`emma` is distinctive; `said` is not).

Bad universe:

- Eighteen documents is a tiny \(N\). A word that appears in two
  novels already looks common. In a million-document web index the
  same word might still be rare.
- The shelf is almost entirely narrative literary English. Technical
  prose, dialogue-only transcripts, and non-English text are absent.
- Project Gutenberg header-ish title lines (`[Emma by Jane Austen
  1816]`) survive tokenization as `1816`, `1818`, and so on. Those
  tokens can rise in TF-IDF because they are document-specific
  metadata, not because Jane Austen used the number thematically.
- Plays arrive with speech prefixes (`Ham.`, `Macb.`) which the Perl
  stripper turns into odd leftovers. See [07](07-tokenization-and-stopwords.md).

## Length, intuitively

I am not checking in a new full-shelf statistic dump next to the 2012
`output/` tree. When I need sizes I ask the lab:

```bash
python3 -m tfidf corpus-stats --corpus gutenberg
```

Expect the KJV to dwarf Blake. Any ranking rule that uses *raw* TF
without a length story will let the Bible hoard common query terms.
That is the practical reason the Perl divided by `word_count`.

## Clusters I use as sanity checks

When I rank queries I expect, qualitatively:

| Query | Documents I would be suspicious not to see near the top |
| --- | --- |
| `white whale ahab` | `melville-moby_dick.txt` |
| `alice rabbit queen` | `carroll-alice.txt` |
| `macbeth witches thane` | `shakespeare-macbeth.txt` |
| `hamlet ghost horatio` | `shakespeare-hamlet.txt` |
| `emma woodhouse hartfield` | `austen-emma.txt` |
| `father brown flambeau` | `chesterton-brown.txt` |
| `paradise satan eden` | `milton-paradise.txt` |

If a query of that shape loses to a random children's story, the bug
is almost always tokenization, IDF = 0 on a term I thought was rare,
or cosine on near-empty vectors — not "IR is dead."

## Texts I wrote myself

The four paragraphs in `examples/tiny_corpus/` are mine. They exist so
[04](04-worked-example-tiny-corpus.md) can show every intermediate
number without opening *Moby-Dick*.
