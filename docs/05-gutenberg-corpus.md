# The Gutenberg sample

`gutenberg/` holds eighteen public-domain texts. They are the original
toy collection for this repository, not a balanced corpus and not a
library dump. Several files still include title pages, act headings,
and verse numbers, all of which become tokens.

## Inventory

| File | Work | Rough character |
| --- | --- | --- |
| `austen-emma.txt` | *Emma* | long novel, social vocabulary |
| `austen-persuasion.txt` | *Persuasion* | long novel, overlapping Austen lexicon |
| `austen-sense.txt` | *Sense and Sensibility* | long novel, same |
| `bible-kjv.txt` | King James Bible | largest file, archaic function words |
| `blake-poems.txt` | Blake poems | shortest literary file |
| `bryant-stories.txt` | Bryant stories | children's prose |
| `burgess-busterbrown.txt` | Buster Brown | children's prose |
| `carroll-alice.txt` | *Alice's Adventures in Wonderland* | invented names |
| `chesterton-ball.txt` | *The Ball and the Cross* | novel |
| `chesterton-brown.txt` | Father Brown stories | shared Chesterton lexicon |
| `chesterton-thursday.txt` | *The Man Who Was Thursday* | novel |
| `edgeworth-parents.txt` | *The Parent's Assistant* | didactic stories |
| `melville-moby_dick.txt` | *Moby-Dick* | whaling vocabulary |
| `milton-paradise.txt` | *Paradise Lost* | epic verse |
| `shakespeare-caesar.txt` | *Julius Caesar* | play, speech prefixes |
| `shakespeare-hamlet.txt` | *Hamlet* | play, speech prefixes |
| `shakespeare-macbeth.txt` | *Macbeth* | play, speech prefixes |
| `whitman-leaves.txt` | *Leaves of Grass* | long lined verse |

There is also a `.DS_Store` leftover from an older Mac checkout. Both
Perl and Python skip names that start with `.`.

## What the collection is good for

It is good for watching IDF do its job on real running text.

- Character names (`alice`, `ahab`, `thel`) behave like perfect
  keywords: high TF in one file, `df = 1`, IDF at the ceiling.
- Shared author signal is visible too. The three Austen novels share
  enough function and society words that their distinctive leftovers
  are proper names and a few favorite adjectives, not the word
  `the`.
- The three Shakespeare plays show the tokenizer's bias toward speech
  prefixes. That is a feature of the pipeline, not of the plays.

## What the collection is a poor fit for

- Training embeddings or any model that needs balanced genres.
- Claims about "English" in general. Half the tokens in the DF table
  come from verse, scripture, or dialogue tags.
- Cross-edition scholarship. These files are convenience copies.

If you want a collection whose terms you can reread in one sitting,
use `examples/tiny_corpus/docs/` instead. Those five files were
written for this lab and are not Gutenberg texts.

## Size snapshot

On the current checkout the eighteen `.txt` files together are about
257,000 lines. `output/idf.txt` has 57,368 terms. Most of those terms
appear in a single book; that is why the IDF histogram piles up at
`ln(18)`.
