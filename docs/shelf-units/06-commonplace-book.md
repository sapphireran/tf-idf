# A personal commonplace book

The Gutenberg shelf is other people's writing. The notes in
`examples/commonplace/` are not. They are twelve short pieces written
for this kit, each seeded with a vocabulary that should not leak.

That is the control experiment. If classic TF-IDF cannot pick the
darkroom note out of a pile I designed for the purpose, the rest of the
literary claims are theater.

```bash
python3 -m shelf_units commonplace -k 5
python3 -m shelf_units commonplace "hypo fixer enlarger"
python3 -m shelf_units rank "zugzwang lucena opposition" --units commonplace
```

## The twelve notes

| id | title | seeded lexicon |
| --- | --- | --- |
| 01-darkroom | Darkroom nights | enlarger, hypo, fixer, Dektol, dodge, burn |
| 02-tide-pool | Tide pool, minus tide | anemones, limpets, holdfasts, urchins, kelp, chiton |
| 03-night-bus | Last night bus | terminus, transfer, fluorescent, validator |
| 04-endgame-study | Rook endgame on the kitchen table | Lucena, Philidor, zugzwang, opposition, rook |
| 05-fountain-pen | Tuning a stubborn nib | nib, tines, feed, converter, baby-bottom |
| 06-winter-swim | Winter swim off the jetty | afterdrop, neoprene, jetty, cold shock |
| 07-pottery-wheel | Centering, again | centering, grog, leather-hard, bat, cone |
| 08-espresso-dial | Dialing a stubborn puck | puck, channeling, WDT, blonding, portafilter |
| 09-star-chart | Averted vision on a school-night sky | averted, Messier, declination, collimation |
| 10-typewriter-ribbon | Replacing a typewriter ribbon | platen, escapement, pica, typebar |
| 11-beekeeping | A queenright check | queenright, varroa, brood, smoker, super |
| 12-orienteering | Attack point before the control | attack point, control flag, reentrant |

## Measured tops

These are not the seeded words in every case. Length-normalized TF-IDF
will happily promote a repeated ordinary word (`tide` in the tide-pool
note, `bus` in the night-bus note) when that word is rare on the rest of
*this* shelf. That is correct behavior for `N = 12`.

| note | observed top terms |
| --- | --- |
| 01-darkroom | darkroom, enlarger, stop, acetic |
| 02-tide-pool | tide, minus, anemones |
| 03-night-bus | bus, island, run |
| 04-endgame-study | pawn, bridge, lucena, philidor, rook |
| 05-fountain-pen | nib, pen, slit, tines |
| 08-espresso-dial | machine, puck, shot |
| 11-beekeeping | brood, queenright |
| 12-orienteering | control, attack, flag, map |

Queries with the seeded forms all elect the intended note. Two that I
keep on a scrap of paper:

| query | score | winner |
| --- | ---: | --- |
| `hypo fixer enlarger` | 0.235 | 01-darkroom |
| `zugzwang lucena opposition` | 0.244 | 04-endgame-study |

Stemming would have let `anemone` match `anemones`. This kit does not
stem, on purpose: the 2012 scripts did not, and the mismatch is a useful
scar. The tide-pool tests query `anemones limpets holdfasts urchins`.

## Why write new notes at all

Because a Gutenberg-only expansion is a reading of other people's books.
A commonplace book is a reading of a week. The same math that finds the
Hatter should also find the enlarger. If I later add a thirteenth note
about a color darkroom, `enlarger` will lose some idf and the ranking
will move. That is the whole method, happening at kitchen-table scale.
