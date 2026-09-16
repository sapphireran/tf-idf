# Austen vs Shakespeare: names versus dialect

Both clusters look like "same author" problems. Cosine disagrees.

## Austen: three novels, three casts

Top-8 `tf * idf` for the Austen files:

| *Emma* | *Persuasion* | *Sense and Sensibility* |
| --- | --- | --- |
| `emma` 0.01043 (df=2) | `elliot` 0.00881 (df=1) | `elinor` 0.01503 (df=1) |
| `harriet` 0.00713 | `wentworth` 0.00663 | `marianne` 0.00906 (df=2) |
| `weston` 0.00698 | `anne` 0.00587 (df=6) | `dashwood` 0.00545 |
| `knightley` 0.00614 | `musgrove` 0.00385 | `jennings` 0.00494 |
| `elton` 0.00579 | `russell` 0.00311 | `mrs` 0.00359 (df=8) |
| `mr` 0.00418 (df=10) | `mrs` 0.00283 | `willoughby` 0.00325 |
| `fairfax` 0.00367 | `charles` 0.00276 | `lucy` 0.00290 |
| `woodhouse` 0.00365 (df=2) | `uppercross` 0.00267 | `brandon` 0.00282 |

The novels share a period social vocabulary (`mr`, `mrs`, `miss`) but those tokens have middling `idf`. The weights that actually set the direction of each vector are character names, and the names do not overlap.

Cosine for `austen-emma.txt`:

| Other book | Cosine |
| --- | ---: |
| `edgeworth-parents.txt` | 0.1009 |
| `austen-persuasion.txt` | 0.0879 |
| `austen-sense.txt` | 0.0675 |

*Emma*'s nearest neighbor is Edgeworth's *Parent's Assistant*, not another Austen novel. Edgeworth is also late-18th / early-19th-century moral prose with `mr` / `mrs` and a rotating cast of first names. Those medium-`idf` social tokens add up. Austen's own titles cannot match each other on `emma` / `elinor` / `elliot` because those strings are nearly disjoint.

A name query still works, because a query vector made of *Emma* names has almost no mass on `mr`:

```
--query "emma harriet knightley highbury"
```

| Rank | Book | Cosine |
| ---: | --- | ---: |
| 1 | `austen-emma.txt` | 0.6142 |
| 2 | `austen-persuasion.txt` | 0.0006 |
| 3 | `austen-sense.txt` | 0.0000 |

Retrieval and clustering are different questions on this weighting.

## Shakespeare: three plays, one spelling system

Top-8 for the plays:

| *Macbeth* | *Hamlet* | *Julius Caesar* |
| --- | --- | --- |
| `macb` 0.02156 | `ham` 0.01408 (df=5) | `bru` 0.02082 |
| `haue` 0.01190 (df=3) | `haue` 0.01022 (df=3) | `brutus` 0.01666 |
| `macbeth` 0.00976 | `hor` 0.00681 | `cassi` 0.01456 |
| `macd` 0.00913 | `qu` 0.00584 | `haue` 0.01240 (df=3) |
| `rosse` 0.00771 | `laer` 0.00565 | `cassius` 0.01157 |
| `vpon` 0.00566 (df=3) | `ophe` 0.00528 | `antony` 0.00776 |
| `vs` 0.00536 (df=3) | `pol` 0.00462 | `caesar` 0.00725 (df=8) |
| `banquo` 0.00535 | `rosin` 0.00405 | `caes` 0.00531 |

Two kinds of string dominate:

1. **Speech prefixes.** `macb`, `macd`, `ham`, `hor`, `bru`, `cassi`. Unique or nearly unique, and they appear every time a character speaks. They are the `alice` of drama.
2. **Folio spelling.** `haue`, `vpon`, `vs` occur in all three plays and almost nowhere else (`df = 3`). That is a shared dialect vector. It is also why the three plays are each other's nearest neighbors even though their casts do not overlap.

Global top pairs:

| Pair | Cosine |
| --- | ---: |
| Hamlet — Macbeth | 0.3084 |
| Caesar — Hamlet | 0.2529 |
| Caesar — Macbeth | 0.2261 |

Those three pairs are ranks 1, 3, and 4 in the whole 18-book collection (Milton–Whitman sneaks into rank 2 on `thee` / `thou`).

A name query is still play-specific:

```
--query "macbeth banquo thane cawdor"
```

| Rank | Book | Cosine |
| ---: | --- | ---: |
| 1 | `shakespeare-macbeth.txt` | 0.3073 |
| 2 | everything else | 0.0000 |

`haue` does not appear in the query, so the Folio dialect does not leak Macbeth's query into Hamlet.

## The lesson

`tf * idf` cosine clusters documents that share **the same rare strings**, not documents that share an author or a genre.

- Shakespeare shares rare strings that are not names (`haue`).
- Austen shares only common social strings (`mrs`) and keeps her rare strings to herself.
- Alice shares almost nothing at high weight, so she sits alone.

If you wanted "same author" you would need a different representation: character 3-grams, a stemmer, a stop list that includes speech prefixes, or an embedding trained on something other than 18 books.
