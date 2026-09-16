# Shakespeare Folio spellings

The three play files are not modern-spelling editions. They are
Folio-style texts (`haue`, `vpon`, `selfe`, `Macb.`). On an
eighteen-book shelf whose other sixteen files are mostly later
orthography, those spellings are a private alphabet. TF-IDF treats
them the way it treats a character name.

## The shared spine

Terms that appear in all three plays, ranked by the *smallest* of
the three weights:

| Term | Caesar | Hamlet | Macbeth | What it is |
| --- | ---: | ---: | ---: | --- |
| haue | 0.01240 | 0.01022 | 0.01190 | *have* |
| vs | 0.00523 | 0.00362 | 0.00536 | *us* |
| selfe | 0.00329 | 0.00391 | 0.00312 | *self* |
| vpon | 0.00397 | 0.00292 | 0.00566 | *upon* |
| giue | 0.00295 | 0.00345 | 0.00234 | *give* |
| heere | 0.00472 | 0.00263 | 0.00215 | *here* |
| speake | 0.00248 | 0.00270 | 0.00237 | *speak* |
| loue | 0.00287 | 0.00380 | 0.00185 | *love* |
| vp | 0.00270 | 0.00204 | 0.00254 | *up* |
| doe | 0.00118 | 0.00292 | 0.00371 | *do* |
| exeunt | 0.00156 | 0.00113 | 0.00246 | stage direction |
| feare | 0.00245 | 0.00117 | 0.00341 | *fear* — actually thematic in *Macbeth* |

`haue` is the heaviest shared token. It never appears in the other
fifteen files. `idf(haue) = ln(18/3) ≈ 1.792`, and the word is
ordinary English, so the TF is high in every play. The trio
`haue` / `vpon` / `selfe` is enough, by itself, to make the three
plays each other's nearest neighbors.

A query of those three tokens ranks:

```
0.3442  shakespeare-hamlet
0.3283  shakespeare-macbeth
0.2644  shakespeare-caesar
0.0000  everyone else
```

That is a spelling detector, not a tragedy detector.

## Speech prefixes occupy the top slot

| Play | Top terms | Reading |
| --- | --- | --- |
| Caesar | bru, brutus, cassi, haue, cassius, antony, caesar | Prefixes, then Folio *have*, then the plot |
| Hamlet | ham, haue, hor, qu, laer, ophe, pol, rosin | Prefixes for Hamlet, Horatio, Queen, Laertes, Ophelia, Polonius, Rosencrantz |
| Macbeth | macb, haue, macbeth, macd, rosse, vpon, vs, banquo | Prefixes, then the name in full, then Folio function words |

`bru` beating `brutus` is not a claim that the abbreviation is more
important. It is a claim that the compositor wrote the prefix more
often than the unabbreviated name in dialogue about him. Same for
`ham` vs `hamlet` and `macb` vs `macbeth`.

If you modernized the spelling and expanded the prefixes, the three
plays would still share vocabulary (`king`, `lord`, `blood`), but
their pairwise cosines would drop. The current 0.23–0.31 band is
mostly orthography plus stagecraft (`exeunt`, `enter` survivors
that made it through the tokenizer).

## What is *not* shared with Milton or the KJV

`thee` / `thou` / `thy` *do* leak into the archaic-pronoun corridor
(Bible, Milton, Blake, Whitman). Folio *have* does not. That is why
*Paradise Lost* is a weak neighbor of the plays (0.04–0.06) and a
strong neighbor of Whitman (0.265). Shared Early Modern pronouns
are a corridor; shared Folio consonants (`u` for `v`, silent `e`)
are a locked room.

## How to read a play file on this shelf

1. Ignore the top speech prefix. You already know which play it is.
2. Keep the next few full names (`banquo`, `ophelia` via `ophe`,
   `cassius`). They are the cast list.
3. Then look for the first content word that is not a name and not
   a Folio spelling. In *Macbeth* that is `thane` and `cawdor`. In
   *Caesar* it is later than you want — `caesar` is both name and
   theme. In *Hamlet* the snapshot is extremely prefix-heavy; the
   ghost does not crack the top fifteen.

`python3 examples/reading-companion/folio_spellings.py` reprints the
shared-spine table and the "only in the plays" test for `haue`.
