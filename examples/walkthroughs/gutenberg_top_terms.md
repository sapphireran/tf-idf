# Top TF-IDF terms in the committed Gutenberg run

Ranked from `output/tfidf/` with \(N = 18\), raw TF × unsmoothed IDF.
Regenerate the tables (without rewriting `output/`) with:

```bash
python3 examples/rank_terms.py --input-dir output/tfidf --top 12
```

Commentary is qualitative. There is no labeled gold list.

## Jane Austen

### `austen-emma.txt`

| Rank | Term | Score | Note |
| ---: | --- | ---: | --- |
| 1 | emma | 0.010432 | Title character |
| 2 | harriet | 0.007127 | Harriet Smith |
| 3 | weston | 0.006980 | Mr / Mrs Weston |
| 4 | knightley | 0.006140 | Mr Knightley |
| 5 | elton | 0.005793 | Mr Elton |
| 6 | mr | 0.004177 | Period address; also high in Edgeworth |
| 7 | fairfax | 0.003673 | Jane Fairfax |
| 8 | woodhouse | 0.003653 | Family name |
| 9 | mrs | 0.003522 | Shared Austen/Edgeworth diction |
| 10 | jane | 0.003081 | Jane Fairfax (and the author, once) |
| 11 | hartfield | 0.002796 | Estate |
| 12 | churchill | 0.002625 | Frank Churchill |

### `austen-persuasion.txt`

`elliot`, `wentworth`, `anne`, `musgrove`, `russell`, `uppercross`,
`kellynch`, `benwick`. Same pattern: surnames and places, then `mrs` /
`captain`.

### `austen-sense.txt`

`elinor`, `marianne`, `dashwood`, `jennings`, `willoughby`, `lucy`,
`brandon`, `ferrars`, `barton`. *Sense and Sensibility* has the
largest lead for its heroine (`elinor` at 0.015) of the three Austen
files — Elinor is on the page constantly, and the name is collection-rare.

## Lewis Carroll — `carroll-alice.txt`

| Rank | Term | Score |
| ---: | --- | ---: |
| 1 | alice | 0.025957 |
| 2 | gryphon | 0.004547 |
| 3 | duchess | 0.004242 |
| 4 | dormouse | 0.004242 |
| 5 | hatter | 0.003708 |
| 6 | turtle | 0.003169 |
| 7 | caterpillar | 0.001820 |
| 8 | rabbit | 0.001778 |
| 9 | alices | 0.001305 |
| 10 | herself | 0.001266 |
| 11 | soup | 0.001214 |
| 12 | mouse | 0.001160 |

`herself` is a reminder that mildly rare pronouns can sneak in.
`alices` is the possessive after apostrophe deletion. See
[alice_through_the_pipeline.md](alice_through_the_pipeline.md).

## Herman Melville — `melville-moby_dick.txt`

| Rank | Term | Score |
| ---: | --- | ---: |
| 1 | whale | 0.004943 |
| 2 | ahab | 0.004322 |
| 3 | sperm | 0.003258 |
| 4 | stubb | 0.003095 |
| 5 | queequeg | 0.002877 |
| 6 | whales | 0.002760 |
| 7 | starbuck | 0.002304 |
| 8 | pequod | 0.001650 |
| 9 | nantucket | 0.001295 |
| 10 | boats | 0.001270 |
| 11 | whaling | 0.001171 |
| 12 | moby | 0.001077 |

`moby` is unique to this file (\(\mathrm{df} = 1\)) and still ranks
12th: the common noun `whale` (\(\mathrm{df} = 6\)) is used far more.
`sperm` is *sperm whale*, not a tokenizer accident. `boats` is the
first generic noun that is only "sort of" about this book.

## King James Bible — `bible-kjv.txt`

`unto`, `israel`, `saith`, `thee`, `david`, `judah`, `thou`, `hath`,
`lord`, `jesus`, `thereof`, `thy`.

Aboutness (`israel`, `david`, `jesus`) is mixed with Early Modern
glue (`unto`, `saith`, `thee`). Those glue words are frequent in this
file and rare in Austen/Chesterton, so IDF treats them as content.
A stopword list for scripture needs a different dialect than a
stopword list for novels.

## John Milton — `milton-paradise.txt`

`thee`, `thou`, `heaven`, `thy`, `eve`, `th`, `adam`, `hath`, `spake`,
`satan`, `bliss`, `thus`.

Same archaic-pronoun effect as the Bible. `eve`, `adam`, and `satan`
are the topical core; `th` is a broken remnant of `th'` / `the`.

## William Blake — `blake-poems.txt`

`thel`, `weep`, `lyca`, `thee`, `vales`, `oer`, `har`, `thou`,
`weeping`, `lamb`, `infant`, `morn`.

The file is short, so magnitudes look larger than Milton's even when
the terms are softer. `oer` is `o'er`. `thel` / `lyca` / `har` are
Blake names.

## Children's books

### `burgess-busterbrown.txt`

`buster` at 0.040 is the largest single score in the whole run. The
book is short and the name is everywhere. Then `browns`, `joe`,
`blacky`, `billy`, `otter`, `sammy`, `chatterer`. Animal-story
proper names, textbook TF-IDF.

### `bryant-stories.txt`

`margery`, `jackal`, `brahmin`, `epaminondas`, `nightingale`,
`halfchick`, `gingerbread`. A story anthology, so top terms are
per-tale protagonists rather than one hero.

### `edgeworth-parents.txt`

`cecilia`, `susan`, `piedro`, `jem`, `leonora`, `archer` — another
anthology of moral tales, same shape as Bryant at a larger size.

## G. K. Chesterton

### `chesterton-thursday.txt`

`syme` (0.024), then `gregory`, `professor`, `marquis`, `gogol`,
`anarchists`. Clean thriller-name ranking.

### `chesterton-brown.txt`

`flambeau`, then a long tail of single-story surnames (`boulnois`,
`muscari`, `fanshaw`). Father Brown himself is `brown` at rank 5 —
the name is ordinary English, so IDF hurts it.

### `chesterton-ball.txt`

`turnbull`, `macian`, `evan` — then `ebook` and `gutenberg`. This
file's boilerplate is heavier than its neighbors. License language is
rare in the *collection* and repeated in *this* file, so it ranks
like a character. Strip headers before trusting the tail of this list.

## Shakespeare (Folio-flavored texts)

### `shakespeare-hamlet.txt`

`ham`, `haue`, `hor`, `qu`, `laer`, `ophe`, `pol`, `rosin`, `selfe`,
`loue`, `horatio`, `vs`.

Speech prefixes (`Ham.`, `Hor.`, `Qu.`, `Laer.`, `Ophe.`, `Pol.`,
`Rosin.`) plus period spelling. `horatio` does appear, below `hor`.
The play is "about" Hamlet; the *file* is about the token `ham`.

### `shakespeare-macbeth.txt`

`macb`, `haue`, `macbeth`, `macd`, `rosse`, `vpon`, `vs`, `banquo`,
`lenox`, `thane`. Same structure. `macbeth` as a spelled-out name
still makes the top five because it is \(\mathrm{df} = 1\).

### `shakespeare-caesar.txt`

`bru`, `brutus`, `cassi`, `haue`, `cassius`, `antony`, `caesar`,
`caes`. `caesar` has \(\mathrm{df} = 8\) (Bible, Melville, other
plays mention him) and still ranks high on TF.

If you want topical Shakespeare terms, normalize speech prefixes and
modernize spelling first. The example library does not, so it stays
comparable to the Perl.

## Walt Whitman — `whitman-leaves.txt`

`o`, `thee`, `poems`, `pioneers`, `states`, `passd`, `chant`,
`cities`, `forever`, `soul`, `manhattan`. Vocative `o` and `thee` are
stylistic fingerprints. `manhattan` / `pioneers` / `chant` are the
content. Whitman's top magnitude (`o` at 0.0018) is small because the
book is long and the distinctive words are spread out.

## How to use these lists

- Teaching "TF-IDF finds names": start with Emma, Alice, Buster, Syme.
- Teaching "IDF is collection-relative": Brown vs `brown`, Alice vs
  `rabbit`, Melville `whale` vs `moby`.
- Teaching "garbage in": Hamlet prefixes, Ball `gutenberg`, Bible
  `unto`.
- Teaching "do not compare raw magnitudes across books": Buster 0.040
  vs whale 0.005.

Pairwise cosine on these same vectors is
`python3 examples/cosine_similarity.py --from-output output/tfidf --top-pairs 15`.

What actually sits at the top is shared *register*, not shared
authorship:

| Pair | Cosine | Why |
| --- | ---: | --- |
| hamlet – macbeth | 0.308 | Folio tags and spellings |
| paradise – leaves | 0.265 | `thee` / `thou` / vocatives |
| caesar – hamlet | 0.253 | same as the other plays |
| persuasion – edgeworth | 0.119 | `mrs` / `mr` period address |
| emma – sense | 0.067 | same author, different names |
| buster – caesar | 0.0002 | almost no shared rare tokens |

Character-name TF-IDF is excellent for labeling a *single* book and
mediocre for clustering authors. The walkthroughs keep both lessons.
