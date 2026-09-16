# Walkthrough of top terms in several Gutenberg books

Rankings below are from the **committed** `output/tfidf/` tables, \(N=18\), using:

```bash
python3 examples/python/rank_terms.py --from-table output/tfidf/<book>.txt --top 12
```

The point is not that tf-idf “understands” a novel. It is that a very small amount of counting, plus a collection-wide rarity weight, surfaces names, places, and a few topic nouns — and also surfaces tokenizer artifacts you should not ignore.

## Lewis Carroll — `carroll-alice.txt`

| rank | token | tf×idf | reading |
| ---: | --- | ---: | --- |
| 1 | `alice` | 0.02596 | title character; also in two other books, still dominates here |
| 2 | `gryphon` | 0.00455 | Mock Turtle sequence |
| 3 | `dormouse` | 0.00424 | tea-party |
| 4 | `duchess` | 0.00424 | pig-baby / pepper chapters |
| 5 | `hatter` | 0.00371 | “mad hatter” is two tokens; `hatter` carries the name |
| 6 | `turtle` | 0.00317 | Mock Turtle |
| 7 | `caterpillar` | 0.00182 | mushroom chapter |
| 8 | `rabbit` | 0.00178 | White Rabbit; `rabbit` is common English, so IDF is milder |
| 9 | `alices` | 0.00131 | leftover possessive `Alice's` |
| 10 | `herself` | 0.00127 | narration is close-third; `herself` is less common in the other 17 |
| 11 | `soup` | 0.00121 | “Turtle Soup” |
| 12 | `mouse` | 0.00116 | caucus-race / tale |

`im` and `ive` appear just below this window. They are `I'm` / `I've`, not characters. A real analyzer would keep them as contractions or drop them as stop-ish. This tokenizer cannot.

`alice` having `df = 3` is the best teaching row in the whole corpus: rarity is measured against **this** collection, not against English.

## Herman Melville — `melville-moby_dick.txt`

| rank | token | tf×idf | reading |
| ---: | --- | ---: | --- |
| 1 | `whale` | 0.00494 | the topic noun |
| 2 | `ahab` | 0.00432 | the captain |
| 3 | `sperm` | 0.00326 | sperm whale / sperm oil, not modern slang |
| 4 | `stubb` | 0.00309 | second mate |
| 5 | `queequeg` | 0.00288 | harpooneer |
| 6 | `whales` | 0.00276 | unstemmed plural of #1 |
| 7 | `starbuck` | 0.00230 | first mate |
| 8 | `pequod` | 0.00165 | the ship |
| 9 | `nantucket` | 0.00130 | the island |
| 10 | `boats` | 0.00127 | whaleboats |
| 11 | `whaling` | 0.00117 | the industry |
| 12 | `moby` | 0.00108 | only half of “Moby Dick”; `dick` is too common to win |

The winning *weight* is much smaller than Alice's `alice`. *Moby-Dick* is long and its mass is spread across a whole crew and a technical vocabulary (`harpooneer`, `fishery`, `leviathan`). tf-idf still reconstructs the cast list.

`whale` has `df = 6`. Milton, the Bible, and others mention whales. The term is still #1 in Melville because the **tf** is enormous there.

## Jane Austen — `austen-emma.txt`

| rank | token | tf×idf | reading |
| ---: | --- | ---: | --- |
| 1 | `emma` | 0.01043 | title character |
| 2 | `harriet` | 0.00713 | Harriet Smith |
| 3 | `weston` | 0.00698 | Mr / Mrs Weston |
| 4 | `knightley` | 0.00614 | Mr Knightley |
| 5 | `elton` | 0.00579 | Mr Elton |
| 6 | `mr` | 0.00418 | high tf; IDF is not zero because not every book uses `mr` |
| 7 | `fairfax` | 0.00367 | Jane Fairfax |
| 8 | `woodhouse` | 0.00365 | family name |
| 9 | `mrs` | 0.00352 | same pattern as `mr` |
| 10 | `jane` | 0.00308 | Jane Fairfax; also a common given name |
| 11 | `hartfield` | 0.00280 | the Woodhouse home |
| 12 | `churchill` | 0.00263 | Frank Churchill |

This is almost a dramatis personae plus two honorifics. `mr` / `mrs` ranking high is a reminder that IDF is estimated on **18 books**, several of which are biblical or early-modern verse and do not write `Mr. Knightley`. In a corpus of only 19th-century novels those honorifics would sink.

Compare the other Austen files if you want to see the same method name three different casts (`wentworth`, `elliot` in *Persuasion*; `elinor`, `marianne`, `dashwood` in *Sense and Sensibility*).

## Shakespeare — `shakespeare-macbeth.txt` and `shakespeare-hamlet.txt`

*Macbeth* (First Folio-ish spelling in the NLTK dump):

| rank | token | tf×idf | reading |
| ---: | --- | ---: | --- |
| 1 | `macb` | 0.02156 | speech prefix for Macbeth |
| 2 | `haue` | 0.01190 | Folio *have* |
| 3 | `macbeth` | 0.00976 | the name in dialogue / stage directions |
| 4 | `macd` | 0.00913 | Macduff's prefix |
| 5 | `rosse` | 0.00771 | Ross |
| 6 | `vpon` | 0.00566 | Folio *upon* |
| 7 | `vs` | 0.00536 | Folio *us* (also the two-letter English word) |
| 8 | `banquo` | 0.00535 | Banquo |
| 9 | `lenox` | 0.00441 | Lennox |
| 10 | `mal` | 0.00393 | Malcolm's prefix |
| 11 | `thane` | 0.00393 | “thane of Cawdor” |
| 12 | `banq` | 0.00378 | Banquo's prefix |

*Hamlet* is the same pattern: `ham`, `hor`, `laer`, `ophe`, `pol`, then `haue` / `selfe` / `loue`.

Two lessons:

1. **Speech prefixes are the strongest “names” in a play file.** They fire on every speech, so tf is huge, and they are play-specific, so idf is huge.
2. **Orthography is a feature.** `haue` ranks because the other 15 non-Shakespeare books write `have`. A modern-spelling edition would drop `haue` out of the top 12 and promote more names.

`exeunt` appearing in the Macbeth tail is the same phenomenon: a stage direction rare in novels.

## John Milton — `milton-paradise.txt`

| rank | token | tf×idf | reading |
| ---: | --- | ---: | --- |
| 1 | `thee` | 0.00220 | early-modern pronoun; also biblical |
| 2 | `thou` | 0.00176 | same |
| 3 | `heaven` | 0.00144 | the setting |
| 4 | `thy` | 0.00130 | same as thee/thou |
| 5 | `eve` | 0.00116 | Eve |
| 6 | `th` | 0.00114 | elided *the* (`th'`) after punctuation stripping |
| 7 | `adam` | 0.00111 | Adam |
| 8 | `hath` | 0.00098 | early-modern verb |
| 9 | `spake` | 0.00085 | “spake” |
| 10 | `satan` | 0.00082 | Satan |

The poem's *characters* (`eve`, `adam`, `satan`) do appear, but they lose a lot of mass to **pronouns and morphology that the Bible also uses**. Because the King James Bible is in the same 18-book collection, Milton's biblical diction is less unique than Ahab's Nantucket diction. Collection composition is part of the answer.

## King James Bible — `bible-kjv.txt`

| rank | token | tf×idf | reading |
| ---: | --- | ---: | --- |
| 1 | `unto` | 0.01204 | function word that the novels barely use |
| 2 | `israel` | 0.00400 | name |
| 3 | `saith` | 0.00338 | “saith the Lord” |
| 4 | `thee` | 0.00229 | shared with Milton / Shakespeare |
| 5 | `david` | 0.00221 | name |
| 6 | `judah` | 0.00217 | name |
| 7 | `thou` | 0.00217 | pronoun |
| 8 | `hath` | 0.00191 | verb |
| 9 | `lord` | 0.00174 | `lord` is not in every book with this density |
| 10 | `jesus` | 0.00153 | name |

`unto` beating `israel` is the same lesson as `haue` in Macbeth: **a stylistic function word that the rest of the collection does not share can outrank a content word.** IDF does not know about “content”. It only knows document frequency in these 18 files.

## G. K. Chesterton — `chesterton-thursday.txt`

| rank | token | tf×idf | reading |
| ---: | --- | ---: | --- |
| 1 | `syme` | 0.02435 | Gabriel Syme |
| 2 | `gregory` | 0.00391 | Lucian Gregory |
| 3 | `professor` | 0.00323 | Professor de Worms |
| 4 | `marquis` | 0.00294 | the Marquis |
| 5 | `secretary` | 0.00201 | the Secretary |
| 6 | `gogol` | 0.00175 | Gogol |
| 7 | `anarchists` | 0.00165 | the plot |
| 8 | `symes` | 0.00160 | possessive |
| 9 | `anarchist` | 0.00156 | unstemmed singular of #7 |
| 10 | `president` | 0.00148 | Sunday |

A clean cast-and-plot list. `syme` is the Alice / Ahab pattern again: a rare name used constantly.

Chesterton also contributes `chesterton-brown.txt` and `chesterton-ball.txt`. Similarity among those three should be higher than, say, Brown vs. Blake, because of shared vocabulary (`said`, but more usefully `anarchist`, `priest`, Chesterton's function-word mix). Check with `similar_docs.py`.

## William Blake — `blake-poems.txt`

| rank | token | tf×idf | reading |
| ---: | --- | ---: | --- |
| 1 | `thel` | 0.00558 | *The Book of Thel* |
| 2 | `weep` | 0.00396 | *Songs* refrain |
| 3 | `lyca` | 0.00298 | *The Little Girl Lost* |
| 4 | `thee` | 0.00266 | shared early-modern / lyric pronoun |
| 5 | `vales` | 0.00174 | “vales of Har” |
| 6 | `oer` | 0.00170 | `o'er` |
| 7 | `har` | 0.00149 | place in *Thel* |
| 8 | `thou` | 0.00147 | pronoun |
| 9 | `lamb` | 0.00146 | *The Lamb* |
| 10 | `weeping` | 0.00146 | same family as `weep` |

Blake is the shortest book. Short documents make every repeated rare word look larger (the tf denominator is small). `thel` and `lyca` are fair hits; `weep` / `weeping` would merge under stemming.

## Walt Whitman — `whitman-leaves.txt`

| rank | token | tf×idf | reading |
| ---: | --- | ---: | --- |
| 1 | `o` | 0.00183 | vocative “O” after punctuation stripping |
| 2 | `thee` | 0.00099 | lyric pronoun |
| 3 | `poems` | 0.00085 | the book talking about poems |
| 4 | `pioneers` | 0.00077 | “Pioneers! O Pioneers!” |
| 5 | `states` | 0.00077 | the Union |
| 6 | `passd` | 0.00076 | `pass'd` |
| 7 | `chant` | 0.00073 | Whitman's verb |
| 8 | `cities` | 0.00064 | cataloguing |
| 9 | `forever` | 0.00064 | — |
| 10 | `soul` | 0.00060 | — |

`o` as the top “term” is a tokenizer joke and a real fact about Whitman. A production pipeline would drop one-character tokens or keep `O` as punctuation. Leaving it in is useful in a toy: **you see what you counted.**

## What to take away

1. **Names and collection-rare nouns dominate** when the book is a novel with a stable cast (*Alice*, *Emma*, *Thursday*, *Moby-Dick*).
2. **Shared diction across the 18 files suppresses meaning** (Milton vs. the Bible; `whale` in six books).
3. **Edition and tokenizer choices leak into the ranking** (Folio spelling, speech prefixes, `alices`, `o`, `th`).
4. **Weights are not on a shared 0–1 “aboutness” scale.** Compare ranks inside a book, or cosine similarity across books, not raw `0.026` vs `0.005`.

For the same method on four nine-token notes you can recompute by hand, see [`../examples/tiny-corpus/worked-example.md`](../examples/tiny-corpus/worked-example.md).
