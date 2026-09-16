# Interpreting the Gutenberg rankings

`output/tfidf/*.txt` is alphabetical. Rank it by the second column and you get a crude "what is this book about" list. This page records those heads for the committed run and says when to distrust them.

Extract any list yourself:

```bash
python3 examples/python/extract_top_terms.py output/tfidf/carroll-alice.txt -n 20
python3 examples/python/extract_top_terms.py --tf output/tf/carroll-alice.txt -n 10
```

## The teaching contrast: Alice

Term frequency of *Alice's Adventures in Wonderland* is English:

| rank | term | tf |
| --- | --- | --- |
| 1 | the | 0.06130 |
| 2 | and | 0.03176 |
| 3 | to | 0.02713 |
| 4 | a | 0.02359 |
| 5 | she | 0.02021 |
| 6 | it | 0.01979 |
| 7 | of | 0.01912 |
| 8 | said | 0.01738 |
| 9 | i | 0.01505 |
| 10 | alice | 0.01449 |

TF-IDF of the same file is the cast:

| rank | term | tf-idf | df | note |
| --- | --- | --- | --- | --- |
| 1 | alice | 0.02596 | 3 | also in *Thursday* and Edgeworth |
| 2 | gryphon | 0.00455 | 2 | Milton uses the word once |
| 3 | duchess | 0.00424 | 1 | |
| 4 | dormouse | 0.00424 | 1 | |
| 5 | hatter | 0.00371 | 3 | Chesterton, Whitman |
| 6 | turtle | 0.00317 | 4 | Mock Turtle; also Bible, Whitman, Burgess |
| 7 | caterpillar | 0.00182 | 3 | Melville, Blake |
| 8 | rabbit | 0.00178 | 6 | several children's / Chesterton books |
| 9 | alices | 0.00131 | 1 | `Alice's` after apostrophe strip |
| 10 | herself | 0.00127 | 12 | high TF, low IDF; still sneaks in |

`said` is a dialogue marker with high TF and enough DF to fall out of the top ten TF-IDF. That is the algorithm working.

Identity check for the winner:

```
tf(alice, Alice)  = 0.0144867549668874
idf(alice)        = ln(18/3) = 1.79175946922805
product           = 0.025956780390307
```

That product is the committed `output/tfidf/carroll-alice.txt` row.

## Moby-Dick: rare names plus a common noun with huge TF

| rank | term | tf-idf | df |
| --- | --- | --- | --- |
| 1 | whale | 0.00494 | 6 |
| 2 | ahab | 0.00432 | 2 |
| 3 | sperm | 0.00326 | 1 |
| 4 | stubb | 0.00309 | 1 |
| 5 | queequeg | 0.00288 | 1 |
| 6 | whales | 0.00276 | 4 |
| 7 | starbuck | 0.00230 | 1 |
| 8 | pequod | 0.00165 | 1 |
| 9 | nantucket | 0.00130 | 1 |
| 10 | boats | 0.00127 | 4 |

`whale` is in six books (Bible Jonah, Hamlet's "very like a whale", Whitman, Bryant, Chesterton). It still wins because Melville says it so often that TF overcomes a middling IDF. `ahab` shares a DF slot with the biblical king. `queequeg`, `pequod`, and `sperm` (as in sperm whale) are effectively collection-unique and behave like the toy-corpus nouns.

`moby` itself is `df = 1` but lower TF than `whale`, so it sits further down (~0.00108).

## Emma: character graph

| rank | term | tf-idf | df |
| --- | --- | --- | --- |
| 1 | emma | 0.01043 | 2 |
| 2 | harriet | 0.00713 | 1 |
| 3 | weston | 0.00698 | 1 |
| 4 | knightley | 0.00614 | 1 |
| 5 | elton | 0.00579 | 1 |
| 6 | mr | 0.00418 | 10 | honorific; would die in an all-Austen shelf |
| 7 | fairfax | 0.00367 | 1 |
| 8 | woodhouse | 0.00365 | 2 | also a stray hit in Moby-Dick |
| 9 | mrs | 0.00352 | 8 |
| 10 | jane | 0.00308 | 3 | all three Austen novels |

`mr` / `mrs` survive because the other two Austen novels are only 2/18 of the collection. In an all-Austen corpus they would look like stopwords. `emma` is also mentioned in *Persuasion*; `harriet` and `knightley` are unique here.

## Thursday: one name dominates

| rank | term | tf-idf | df |
| --- | --- | --- | --- |
| 1 | syme | 0.02435 | 1 |
| 2 | gregory | 0.00391 | 2 |
| 3 | professor | 0.00323 | 5 |
| 4 | marquis | 0.00294 | 1 |
| 5 | secretary | 0.00201 | 3 |
| 6 | gogol | 0.00175 | 1 |
| 7 | anarchists | 0.00165 | 1 |
| 8 | symes | 0.00160 | 1 |
| 9 | anarchist | 0.00156 | 2 |
| 10 | president | 0.00148 | 5 |

`syme` is the same shape as `alice` or `buster`: a frequent, collection-unique proper name. `gregory` is shared with *The Ball and the Cross*.

## Hamlet: read past the speech prefix

| rank | term | tf-idf | what to do with it |
| --- | --- | --- | --- |
| 1 | ham | 0.01408 | skip; `HAM.` prefix, and `df = 5` |
| 2 | haue | 0.01022 | Early Modern *have*; shared by all three plays |
| 3 | hor | 0.00681 | prefix for Horatio |
| 4 | qu | 0.00584 | prefix for Queen |
| 5 | laer | 0.00565 | prefix for Laertes |
| 6 | ophe | 0.00528 | prefix for Ophelia |
| 7 | pol | 0.00462 | prefix for Polonius |
| 8 | rosin | 0.00405 | prefix for Rosencrantz |
| 9 | selfe | 0.00391 | spelling |
| 10 | loue | 0.00380 | spelling of *love* |
| 11 | horatio | 0.00377 | first "real" name that is not a tag |
| 13 | hamlet | 0.00358 | the word `hamlet` has `df = 6` |

A play file in this dump is a script, not a novel. TF-IDF will first recover the speaker list. If you want thematic vocabulary (`ghost`, `king`, `denmark`), strip prefixes before counting.

Macbeth and Julius Caesar behave the same way (`macb`, `rosse`, `banquo` / `bru`, `cassius`, `antony`).

## King James Bible: register, not a single plot

| rank | term | tf-idf | df |
| --- | --- | --- | --- |
| 1 | unto | 0.01204 | 6 |
| 2 | israel | 0.00400 | 5 |
| 3 | saith | 0.00338 | 2 |
| 4 | thee | 0.00229 | 11 |
| 5 | david | 0.00221 | 3 |
| 6 | judah | 0.00217 | 2 |
| 7 | thou | 0.00217 | 13 |
| 8 | hath | 0.00191 | 9 |
| 9 | lord | 0.00174 | 15 |
| 10 | jesus | 0.00153 | 5 |

`unto` is not rare in absolute English, but it is rare in this mixed modern/early-modern collection relative to how often the KJV uses it. Length normalization keeps the 821k-token file from simply winning every raw count. Because the whole Bible is **one** document, `david` and `jesus` share a DF of 1 book even though they barely co-occur in the narrative.

## Paradise Lost, Blake, Whitman, Burgess

**Milton** surfaces `thee` / `thou` / `heaven` / `eve` / `adam` / `satan`. `eve` and `satan` have `df = 7`; they rank because Milton's TF is high, same story as `whale`.

**Blake** is only 6.8k tokens, so `thel` and `lyca` jump to the top from a handful of repetitions. Short documents make TF-IDF twitchy; that is expected.

**Whitman** is baggier: `o`, `thee`, `pioneers`, `manhattan`, `eidolons`. The vocative `o` is a reminder that a "term" is not always a content word.

**Burgess** is a children's-animal cast list: `buster` (0.040 — the strongest single-book name score in the run), `blacky`, `chatterer`, `sammy`, `otter`. `buster` has `df = 1`.

## How to read a number

A TF-IDF value in these tables is **not** a probability and **not** comparable across books as "importance on a shared scale" without another normalization. It is:

```
(how concentrated the word is in this book)
    × (how few books in this 18-file shelf use it)
```

Useful comparisons:

- Two terms **in the same book** (alice vs gryphon).
- The same term **before and after** you add a file (copy Alice, rerun, watch `idf(alice)` drop).

Less useful:

- `syme = 0.024` vs `whale = 0.0049` as "Thursday is more about Syme than Moby-Dick is about whales." Different book lengths, different name repetition styles, different DF.

## A checklist before you trust a top term

1. Is it a speech prefix or a chapter number?
2. Is it an Early Modern spelling of a stopword (`haue`, `vpon`)?
3. Did an apostrophe vanish (`alices`, `im`, `dont`)?
4. What is `df`? Grep `output/df.txt`. High TF can beat middling DF (`whale`, `alice`, `unto`).
5. Is the document very short (Blake) or a bundle of many works (KJV, *Leaves of Grass*)?

If it survives that list, it is usually a character, a place, or a topical noun, which is what this experiment is for.
