# The archaic-pronoun corridor

Four files share a diction that the later novels mostly abandoned:
`thee`, `thou`, `thy`, and a vocative `o`. They form a corridor
across genre — scripture, epic, lyric, American chant — that cosine
picks up even though the plots have nothing in common.

## The corridor

| Pair | Cosine | Shared glue |
| --- | ---: | --- |
| Milton ↔ Whitman | **0.2654** | thee, thou, o, soul / heaven register |
| Blake ↔ Milton | **0.2244** | thee, thou, thy, lamb / heaven |
| Bible ↔ Milton | **0.2049** | thee, thou, thy, hath, heaven |
| Blake ↔ Whitman | 0.1583 | o, thee, thou |
| Bible ↔ Whitman | 0.1082 | thee, thou, o |
| Bible ↔ Blake | 0.0872 | thee, thou, thy |

Milton sits in the middle of the corridor. Every one of those four
files lists him as first or second neighbor. Whitman is the other
hub. The later novels (Austen, Carroll, Burgess, Chesterton) sit
outside: their nearest edge into the corridor is usually Whitman or
Milton at 0.02–0.04.

## Weights for the three pronouns

| File | thee | thou | thy |
| --- | ---: | ---: | ---: |
| Blake | 0.00266 | 0.00147 | 0.00100 |
| KJV | 0.00229 | 0.00217 | 0.00141 |
| Milton | 0.00220 | 0.00176 | 0.00130 |
| Macbeth | 0.00164 | 0.00154 | 0.00077 |
| Caesar | 0.00128 | 0.00176 | 0.00066 |
| Whitman | 0.00099 | 0.00053 | 0.00044 |
| Hamlet | 0.00093 | 0.00111 | 0.00074 |
| Moby-Dick | 0.00030 | 0.00041 | 0.00013 |

`idf(thee) ≈ 0.492` (`df = 11`). These are not rare words on this
shelf. They become distinctive only where they are *frequent*.
Blake's tiny file makes a moderate count look large. The KJV makes a
huge count look only moderately large. Both still outrun *Emma*,
which barely uses the pronouns.

Shakespeare participates in the pronouns but is pulled away from
the corridor by Folio consonants (`haue`, `vpon`) that Milton and
the KJV do not share. That is why Macbeth's nearest neighbors are
Hamlet and Caesar (0.31, 0.23), not Milton (0.056).

## Whitman is not "like Milton" in content

*Leaves of Grass* top terms: `o`, `thee`, `poems`, `pioneers`,
`states`, `passd`, `chant`, `cities`, `forever`, `soul`,
`manhattan`, `america`.

*Paradise Lost* top terms: `thee`, `thou`, `heaven`, `thy`, `eve`,
`adam`, `hath`, `spake`, `satan`, `bliss`.

The cosine is a register match (second-person address, elevated
nouns) plus a few biblical leftovers in Whitman. It is not a claim
that Whitman wrote an Eden epic. If you strip `thee`/`thou`/`thy`/`o`
from both vectors, the pair should fall toward the Melville–Whitman
band (0.13) — cataloguing, lists, American/nautical nouns — rather
than stay in the 0.26 spelling-and-address band.

A content query still separates them cleanly:

```
satan eve adam heaven        → Milton   0.3010
manhattan pioneers chant     → Whitman  0.1858
```

## Bible as style, not as plot

The KJV's heaviest terms are translation furniture: `unto`,
`israel`, `saith`, `thee`, `david`, `judah`, `thou`, `hath`,
`lord`. `jesus` appears, but below `david`. A query of
`unto israel moses david` returns the Bible at 0.6024. Second place
is Bryant (0.0951), which retells scripture-adjacent children's
stories (`david` is a Bryant top term too). That second place is a
real leak, not noise.

## How to read the corridor

- High cosine between Milton, Blake, Whitman, and the KJV means
  **shared address**, not shared plot.
- To talk about plot, use a name query (`satan eve`, `manhattan`,
  `israel moses`).
- To talk about style, the pronouns *are* the finding.

`query_shelf.py satan eve adam heaven` and
`query_shelf.py manhattan pioneers chant` are the two ends of the
corridor.
