# Measured walk (this checkout)

Captured with `python3 -m shelf_units …` after the tests in `tests/`
passed (41 tests, OK). These numbers are the study kit, not the 2012
`output/` fossil.

## Commonplace control

```
query: hypo fixer enlarger
  0.2347  01-darkroom

query: zugzwang lucena opposition
  0.2435  04-endgame-study
```

Top terms, selected notes:

```
01-darkroom      darkroom, enlarger, stop, acetic
04-endgame-study pawn, bridge, lucena, philidor, rook
11-beekeeping    brood, queenright
12-orienteering  control, attack, flag, map
```

## Alice chapters

```
query: hatter hare tea
  0.5031  alice-vii   A Mad Tea-Party
  0.3148  alice-xi    Who Stole the Tarts?
  0.0547  alice-vi    Pig and Pepper
```

Chapter VII tops: `dormouse`, `hatter`, `hare`, `march`, `twinkle`.

## File grain (the 2012 filing)

```
query: alice rabbit queen
  0.8084  carroll-alice
  0.0128  bryant-stories
```

## Bible books (`N = 55`)

Genesis tops: `laban`, `abram`, `jacob`, `joseph`, `esau`, `rachel`.

Exodus tops: `moses`, `sockets`, `aaron`, `pharaoh`, `egypt`.

```
query: pharaoh egypt passover     -> exodus
query: nineveh great fish jonah   -> hosea-malachi
query: laban rachel rebekah esau  -> genesis
```

## Passage windows in Alice (`window=80`, `stride=40`)

```
query: hatter march hare twinkle
  0.7054  pass-0360  [14400:14480]  twinkle twinkle little bat
  0.6648  pass-0361  [14440:14520]  teatray / dormouse
  0.4387  pass-0359  [14360:14440]  quarrelled last march
```

## Macbeth voices

Witches rise on `bubble`, `cauldron`, `double`, `haile`, `hayle`.
Lady Macbeth's document contains Folio `vnsex`. Sixteen voices have
at least twenty words.
