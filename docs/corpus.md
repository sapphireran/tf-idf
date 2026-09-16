# Corpus

`gutenberg/` holds 18 plain-text files taken from Project Gutenberg. They are a convenience snapshot for this experiment, not a curated scholarly edition. Line counts below are `wc -l` on the committed files.

## Inventory

| File | Approx. lines | Author / work | Why it is in the mix |
| --- | ---: | --- | --- |
| `austen-emma.txt` | 16,823 | Jane Austen, *Emma* | Long novel; character names dominate TF-IDF |
| `austen-persuasion.txt` | 8,471 | Jane Austen, *Persuasion* | Same author, different names — useful contrast with *Emma* |
| `austen-sense.txt` | 14,796 | Jane Austen, *Sense and Sensibility* | Third Austen novel; shared period language, distinct cast |
| `bible-kjv.txt` | 99,805 | King James Bible | Largest file; archaic function words (`unto`, `saith`) stay distinctive |
| `blake-poems.txt` | 1,441 | William Blake, poems | Shortest literary file; high TF for rare names (`thel`, `lyca`) |
| `bryant-stories.txt` | 5,538 | Sara Cone Bryant, stories | Children's prose; different vocabulary from the novels |
| `burgess-busterbrown.txt` | 1,671 | Thornton Burgess, *Buster Brown* | Short animal story; another small-document extreme |
| `carroll-alice.txt` | 3,331 | Lewis Carroll, *Alice's Adventures in Wonderland* | Clear character-name signal (`alice`, `hatter`, `gryphon`) |
| `chesterton-ball.txt` | 9,548 | G. K. Chesterton, *The Ball and the Cross* | Early 20th-century novel |
| `chesterton-brown.txt` | 7,654 | G. K. Chesterton, Father Brown stories | Same author as `chesterton-ball.txt` |
| `chesterton-thursday.txt` | 6,793 | G. K. Chesterton, *The Man Who Was Thursday* | Third Chesterton file; author-style vs. title-specific words |
| `edgeworth-parents.txt` | 18,297 | Maria Edgeworth, *The Parent's Assistant* | Long didactic stories |
| `melville-moby_dick.txt` | 22,924 | Herman Melville, *Moby-Dick* | Setting vocabulary (`whale`, `pequod`, `nantucket`) |
| `milton-paradise.txt` | 10,635 | John Milton, *Paradise Lost* | Epic verse; different token length and diction |
| `shakespeare-caesar.txt` | 3,523 | Shakespeare, *Julius Caesar* | Play formatting (speaker tags) |
| `shakespeare-hamlet.txt` | 4,922 | Shakespeare, *Hamlet* | Speaker tags + original spelling dominate the ranking |
| `shakespeare-macbeth.txt` | 3,286 | Shakespeare, *Macbeth* | Third play; compare tag leakage across the three |
| `whitman-leaves.txt` | 17,435 | Walt Whitman, *Leaves of Grass* | Free verse; fewer plot-specific proper nouns |

Total: about 257,000 lines.

## Why this mix is useful for TF-IDF

The collection is small enough to recompute on a laptop and mixed enough that IDF is meaningful:

- **Multiple works by one author** (Austen ×3, Chesterton ×3, Shakespeare ×3). Words that belong to an author's period (`mr`, `mrs`, `haue`) have higher DF than words that belong to one title (`emma`, `hamlet`, `ahab`).
- **Extreme length range.** Blake and Burgess are a few thousand tokens; the King James Bible is nearly 100,000 lines. Raw counts would drown the poems. Normalized TF keeps a once-used word in Blake visible.
- **Genre mix.** Plays, novels, verse, scripture, and children's stories produce different "false distinctive" tokens (speaker prefixes vs. character names vs. archaic particles).
- **Shared English.** Function words really do appear in every file, so the zero-IDF effect is easy to demonstrate.

## What is *not* in the files

These are Gutenberg plain-text dumps as they were added to the repo. They may still contain:

- Header or footer remnants (`[Poems by William Blake 1789]`)
- Page numbers, act/scene markers, and speaker abbreviations
- OCR or transcription spellings
- Inconsistent newlines and spacing

The tokenizer does not try to strip Gutenberg boilerplate. A word that appears only in a header (`1789`, `blake`) can still receive a high TF-IDF score in a short file.

## Licensing

Project Gutenberg texts are public domain in the United States. If you add more files, prefer public-domain sources and keep this a personal study corpus. Do not add copyrighted books.

## Related

- Adding a file: [adding-texts.md](adding-texts.md)
- How length and formatting change scores: [interpreting-results.md](interpreting-results.md)
- A four-document original stand-in that avoids Gutenberg size: [../examples/toy-corpus](../examples/toy-corpus)
