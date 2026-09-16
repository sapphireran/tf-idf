# Interpreting the Gutenberg `output/tfidf` tables

The files in `output/tfidf/` are sorted **by term**, not by score. A useful first command is:

```bash
python3 examples/top_terms.py --n 15
python3 examples/top_terms.py --n 12 --files carroll-alice.txt melville-moby_dick.txt shakespeare-hamlet.txt austen-emma.txt blake-poems.txt
```

Scores below come from the checked-in snapshot. Re-running the Perl scripts can move the last digits; the names in these lists should not.

Each list is labeled with the three buckets from [corpus.md](corpus.md):

- **content** — character, place, or invented-thing names that match the plot.
- **morphology** — extra ranks you would merge if you stemmed.
- **artifact** — speaker tags, old spelling, honorifics, header tokens.

## Alice (`carroll-alice.txt`)

| term | score | bucket | note |
| --- | ---: | --- | --- |
| alice | 0.02596 | content | Title character; almost private to this file. |
| gryphon | 0.00455 | content | Invented creature, \(\mathrm{df}\) near 1. |
| duchess, dormouse | 0.00424 | content | Same story. |
| hatter | 0.00371 | content | “Mad Hatter” reduced to one token. |
| turtle | 0.00317 | content | Mock Turtle; `mock` also ranks. |
| caterpillar, rabbit | ~0.0018 | content | |
| alices | 0.00131 | morphology | `Alice's` after apostrophe stripping. |
| herself | 0.00127 | artifact-ish | Frequent in this narration, rarer in plays/Bible. |
| im | 0.00106 | artifact | `I'm`. |
| dinah | 0.00091 | content | The cat. |
| 1865 | (header) | artifact | Title-line year; tokenize keeps digits. |

Zeros in this file (`a`, `about`, `after`, …) are collection-wide words: \(\mathrm{idf} = 0\) in the snapshot. They are not missing from Alice.

Alice is the cleanest “tf-idf found the plot” demo in the snapshot. Read it first.

## Moby-Dick (`melville-moby_dick.txt`)

| term | score | bucket | note |
| --- | ---: | --- | --- |
| whale | 0.00494 | content | Topic word with \(\mathrm{df}\) well below 18. |
| ahab | 0.00432 | content | Captain’s name. |
| sperm | 0.00326 | content | Sperm whale, not the modern default sense. |
| stubb, queequeg, starbuck | 0.0031–0.0023 | content | Crew. |
| whales | 0.00276 | morphology | Sibling of `whale`. |
| pequod | 0.00165 | content | Ship. |
| nantucket | 0.00130 | content | Place. |
| boats, whaling, moby | ~0.0012 | content | |
| captain, deck, ship | ~0.0009 | content / common | Lower because other books also sail. |

Notice the scores are **smaller** than Alice’s `alice`. *Moby-Dick* is much longer, so even a very common-in-this-book word has a smaller tf share. The ranking is still right; do not compare raw magnitudes across files without looking at length.

## Hamlet (`shakespeare-hamlet.txt`)

| term | score | bucket | note |
| --- | ---: | --- | --- |
| ham | 0.01408 | artifact | Speaker tag for Hamlet. |
| haue | 0.01022 | artifact | First Folio `have`. |
| hor | 0.00681 | artifact | Horatio’s tag. |
| qu, laer, ophe, pol | 0.0058–0.0046 | artifact | Queen, Laertes, Ophelia, Polonius. |
| rosin | 0.00405 | artifact | Rosencrantz, clipped. |
| selfe, loue, vs, giue | 0.0039–0.0034 | artifact | `self`, `love`, `us`, `give`. |
| horatio | 0.00377 | content | Full name, finally. |
| hamlet | 0.00358 | content | Below the speaker tag `ham`. |

The method is not “wrong” on Hamlet. The **document** is a play dump with speech prefixes and 1623 spelling, so the rarest, densest tokens are prefixes and old spellings. If you want a character ranking, strip speaker tags first or modernize the text. tf-idf will not do that for you.

Compare *Julius Caesar* in the same snapshot: you should see `brutus` / `cassius` mixed with a different tag set, not `ham`.

## Emma (`austen-emma.txt`)

| term | score | bucket | note |
| --- | ---: | --- | --- |
| emma | 0.01043 | content | |
| harriet | 0.00713 | content | |
| weston | 0.00698 | content | |
| knightley | 0.00614 | content | |
| elton | 0.00579 | content | |
| mr | 0.00418 | artifact | Honorific used constantly; rarer in Blake/Bible/Melville at this rate. |
| fairfax, woodhouse | ~0.0037 | content | |
| mrs | 0.00352 | artifact | Same as `mr`. |
| hartfield, highbury | ~0.0025 | content | House and village. |
| harriets, eltons | 0.00157 | morphology | Possessives after stripping `'`. |
| have | 0.00152 | artifact-ish | Austen’s prose leans on it; not quite \(\mathrm{df}=N\). |

Emma is what Hamlet would look like if the input were modern narrative prose: a character-and-place list. `mr` / `mrs` are the reminder that “rare in this collection” is not the same as “interesting.”

*Persuasion* and *Sense and Sensibility* should not share this top list. If `wentworth` ever ranks inside Emma, something mixed the files up.

## Blake (`blake-poems.txt`)

| term | score | bucket | note |
| --- | ---: | --- | --- |
| thel | 0.00558 | content | *The Book of Thel*. |
| weep | 0.00396 | content | Songs repeat it. |
| lyca | 0.00298 | content | “Little Girl Lost/Found.” |
| thee, thou, thy | 0.0027–0.0010 | artifact-ish | Archaic pronouns; other files use them less densely (except the KJV). |
| vales, oer, lamb, infant | ~0.0015 | content | Lyric diction. |
| blake | 0.00112 | artifact | Header / byline token. |

Blake is short, so a handful of repetitions produce ranks that look like Alice’s mid-list. That is tf doing its job: the denominator is small.

The KJV also uses `thee` / `thou`. If those pronouns rank *lower* in Blake than you expect, check `output/df.txt`: a high df from the Bible and Milton will shrink idf.

## How to chase a surprising term

1. **Is the score zero?** Collection-wide word. Confirm in `output/idf.txt`.
2. **Is the term a fragment?** Apostrophe stripping (`alices`, `im`) or a speaker tag (`ham`). Open the source file and search the raw spelling.
3. **Is df 1?** Almost any nonce token wins. Typos and page numbers live here.
4. **Is the file huge?** Small magnitudes, still a valid ranking (*Moby-Dick*, KJV).
5. **Did you compare two files’ scores as if they shared a scale?** They share idf, not tf. Compare **ranks**, or compare tf shares first.

A top-10 table for **every** file, including the three Austens side by side and the `ebook` / `gutenberg` banner tokens in Chesterton’s *The Ball and the Cross*, is in [gutenberg-top-terms.md](gutenberg-top-terms.md).

## What this snapshot is good for

- Showing a newcomer why `alice` beats `the`.
- Showing why the same code emits `ham` on a play.
- Diffing a reimplementation (`examples/tiny-corpus/compute_tfidf.py` is the small version; do not expect its floats to match these files).

## What this snapshot is not good for

- Search relevance. There is no query.
- Cross-collection research. \(N = 18\) and the mix is opportunistic.
- Authorship or genre claims. Three Chestertons and three Austens will share diction that idf only partly cancels.

For a collection you can explain term-by-term, switch to [examples/tiny-corpus/](../examples/tiny-corpus/).
