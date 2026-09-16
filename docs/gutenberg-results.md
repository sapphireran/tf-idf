# Reading the Gutenberg top-term lists

The tables below are the twelve highest tf-idf tokens from the
**committed Perl run** in `output/tfidf/`. They are a sketch of each
extract *relative to the other seventeen files*, not a summary of English
literature.

Recompute live with:

```bash
python3 -m tfidf_toy top --input gutenberg --k 12
python3 -m tfidf_toy compare --input gutenberg austen-emma.txt austen-sense.txt
```

Three patterns show up over and over. Once you see them, the lists stop
looking mysterious.

## 1. Proper names dominate novels

A protagonist’s name is frequent in one file and (usually) absent from
the others, so both tf and idf are large. That is why the first token is
so often a character:

| extract | top token | what it is |
| --- | --- | --- |
| `austen-emma.txt` | emma | heroine |
| `austen-sense.txt` | elinor | heroine |
| `austen-persuasion.txt` | elliot | family name |
| `carroll-alice.txt` | alice | heroine |
| `burgess-busterbrown.txt` | buster | title character |
| `chesterton-thursday.txt` | syme | protagonist |
| `melville-moby_dick.txt` | whale / ahab | subject and captain |

Supporting cast fills the next slots: Knightley, Harriet, Weston for
*Emma*; Gryphon, Duchess, Dormouse, Hatter for *Alice*; Stubb, Queequeg,
Starbuck for *Moby-Dick*.

This is the same effect as `rabbit` beating `the` in
[`worked-example.md`](worked-example.md), scaled up to a novel.

## 2. The tokenizer leaks through

tf-idf does not know about speech prefixes, spelling, or hyphenation. It
only knows tokens. On the Shakespeare extracts that becomes obvious:

| extract | tokens that look “wrong” | why they rank |
| --- | --- | --- |
| `shakespeare-hamlet.txt` | `ham`, `hor`, `qu`, `laer`, `ophe`, `pol` | abbreviated speaker tags (`Ham.`, `Hor.`, `Qu.`) after punctuation stripping |
| `shakespeare-macbeth.txt` | `macb`, `macd`, `rosse`, `banq` | the same convention |
| `shakespeare-caesar.txt` | `bru`, `cassi`, `caes`, `haue` | speaker tags plus Early Modern spelling (`have` → `haue`) |
| `carroll-alice.txt` | `alices` | `Alice's` lost its apostrophe |
| `milton-paradise.txt` | `th`, `thee`, `thou`, `thy` | elision and pronouns that are rare in the novels |
| `whitman-leaves.txt` | `o`, `passd`, `chant` | vocative *O* and 19th-century contractions |

If you wanted cleaner literary features you would strip speaker tags,
normalize long-s / u-v spelling, and keep apostrophes. This toy does none
of that on purpose: the “mistakes” are the tokenizer teaching you what
it actually counted.

## 3. Collection-relative function words

idf only zeros a word if it appears in **every** document. Archaic or
biblical glue that the novels barely use still gets a large idf:

| extract | high-ranking glue | why it is not zero |
| --- | --- | --- |
| `bible-kjv.txt` | `unto`, `saith`, `thee`, `hath`, `thou`, `thy` | dense in the KJV, sparse in Austen and Burgess |
| `milton-paradise.txt` | `thee`, `thou`, `thy`, `hath`, `spake` | same contrast against the novels |
| `blake-poems.txt` | `weep`, `thee`, `thou`, `lamb` | lyric pronouns plus Blake’s own names (`thel`, `lyca`) |

`the`, `and`, `of`, `a` *do* appear in all eighteen files, so they are
stored as `0` in every `output/tfidf/` table. You do not need a stoplist
for those. You *do* still see `mr` / `mrs` on the Austen lists because
the children’s books and the Bible do not use those titles as densely.

## Boilerplate can outrank plot

`chesterton-ball.txt` includes `ebook` and `gutenberg` in its top twelve.
Those tokens come from a Project Gutenberg header/footer, not from
Chesterton. They are rare across this particular dump (most extracts
here have a one-line `[title]` banner instead), so idf treats them as
distinctive.

That is a real corpus lesson: **tf-idf will happily surface license
banners** if you forget to strip them. The Python rewrite leaves the
files untouched so this remains visible.

## Full top-12 tables (Perl `output/tfidf/`)

Scores are `tf * ln(18/df)` with the original tokenizer.

### Austen

**Emma**

| score | token |
| ---: | --- |
| 0.01043 | emma |
| 0.00713 | harriet |
| 0.00698 | weston |
| 0.00614 | knightley |
| 0.00579 | elton |
| 0.00418 | mr |
| 0.00367 | fairfax |
| 0.00365 | woodhouse |
| 0.00352 | mrs |
| 0.00308 | jane |
| 0.00280 | hartfield |
| 0.00263 | churchill |

**Persuasion**

| score | token |
| ---: | --- |
| 0.00881 | elliot |
| 0.00663 | wentworth |
| 0.00587 | anne |
| 0.00385 | musgrove |
| 0.00311 | russell |
| 0.00283 | mrs |
| 0.00276 | charles |
| 0.00267 | uppercross |
| 0.00253 | kellynch |
| 0.00252 | captain |
| 0.00232 | lyme |
| 0.00229 | benwick |

**Sense and Sensibility**

| score | token |
| ---: | --- |
| 0.01503 | elinor |
| 0.00906 | marianne |
| 0.00545 | dashwood |
| 0.00494 | jennings |
| 0.00359 | mrs |
| 0.00325 | willoughby |
| 0.00290 | lucy |
| 0.00282 | brandon |
| 0.00265 | ferrars |
| 0.00216 | barton |
| 0.00194 | edward |
| 0.00161 | middleton |

`python3 -m tfidf_toy compare --input gutenberg austen-emma.txt austen-sense.txt`
is the interesting next step: Emma Woodhouse / Harriet / Knightley on one
side, Elinor / Marianne / Dashwood on the other, with `mrs` largely
cancelling out.

### Carroll, Melville, Milton, Whitman

**Alice’s Adventures in Wonderland** — character names, then `alices`
(possessive) and `herself` (style, not plot).

| score | token |
| ---: | --- |
| 0.02596 | alice |
| 0.00455 | gryphon |
| 0.00424 | dormouse |
| 0.00424 | duchess |
| 0.00371 | hatter |
| 0.00317 | turtle |
| 0.00182 | caterpillar |
| 0.00178 | rabbit |
| 0.00131 | alices |
| 0.00127 | herself |
| 0.00121 | soup |
| 0.00116 | mouse |

**Moby-Dick** — the subject matter actually wins over the captain, which
is unusual in this shelf.

| score | token |
| ---: | --- |
| 0.00494 | whale |
| 0.00432 | ahab |
| 0.00326 | sperm |
| 0.00309 | stubb |
| 0.00288 | queequeg |
| 0.00276 | whales |
| 0.00230 | starbuck |
| 0.00165 | pequod |
| 0.00130 | nantucket |
| 0.00127 | boats |
| 0.00117 | whaling |
| 0.00108 | moby |

**Paradise Lost** — pronouns and theology, not a single novelistic hero.

| score | token |
| ---: | --- |
| 0.00220 | thee |
| 0.00176 | thou |
| 0.00144 | heaven |
| 0.00130 | thy |
| 0.00116 | eve |
| 0.00114 | th |
| 0.00111 | adam |
| 0.00098 | hath |
| 0.00085 | spake |
| 0.00082 | satan |
| 0.00075 | bliss |
| 0.00072 | thus |

**Leaves of Grass** — scores are smaller (long book, diffuse vocabulary)
and the vocative `o` is the top token.

| score | token |
| ---: | --- |
| 0.00183 | o |
| 0.00099 | thee |
| 0.00085 | poems |
| 0.00077 | pioneers |
| 0.00077 | states |
| 0.00076 | passd |
| 0.00073 | chant |
| 0.00064 | cities |
| 0.00064 | forever |
| 0.00060 | soul |
| 0.00060 | chants |
| 0.00060 | manhattan |

### Shakespeare

Speaker tags first, then Early Modern spelling (`haue`, `vs`, `heere`,
`loue`, `vpon`). *Julius Caesar* still surfaces `antony` and `caesar`
underneath the prefixes.

**Hamlet**

`ham`, `haue`, `hor`, `qu`, `laer`, `ophe`, `pol`, `rosin`, `selfe`,
`loue`, `horatio`, `vs`

**Macbeth**

`macb`, `haue`, `macbeth`, `macd`, `rosse`, `vpon`, `vs`, `banquo`,
`lenox`, `mal`, `thane`, `banq`

**Julius Caesar**

`bru`, `brutus`, `cassi`, `haue`, `cassius`, `antony`, `caesar`, `caes`,
`vs`, `brut`, `heere`, `caska`

### Chesterton, Burgess, Bryant, Edgeworth, Blake, KJV

**The Man Who Was Thursday:** `syme` at 0.024 — a name as dominant as
`alice`. Then Gregory, the Professor, the Marquis, Gogol, anarchists.

**The Ball and the Cross:** `turnbull`, `macian`, `evan` — and then
`ebook` / `gutenberg` from the banner, a reminder to strip headers.

**Father Brown:** `flambeau` outranks `brown`; side characters are more
collection-specific than the priest’s surname, which is an ordinary
English word.

**Buster Brown:** `buster` at 0.040, the strongest single name score on
the shelf (short book + repeated name + unique to this file).

**Bryant stories / Edgeworth:** story-internal names (`margery`,
`jackal`, `cecilia`, `piedro`) because the files are anthologies, not
one plot.

**Blake:** `thel`, `lyca`, `weep`, `lamb` — short lyric collection, so
rare proper names and refrain words.

**King James Bible:** `unto` 0.012, then `israel`, `saith`, `david`,
`judah`, `jesus`. The distinctive signal is the translation’s dialect
as much as the people.

## What not to conclude

- A higher top score does not mean a “better” or “more distinctive”
  book. Short files with a repeated unique name (*Buster Brown*, *Alice*)
  inflate the maximum. Long, thematically broad files (*Leaves of Grass*)
  look “flat.”
- These scores are not comparable to sklearn, Lucene, or BM25.
- Adding a nineteenth book would change every idf and therefore every
  list.

For the arithmetic on a collection small enough to do by hand, stay with
[`worked-example.md`](worked-example.md).
